//
//  SupportChatView.swift
//  EnlikoTrading
//
//  💬 Support Chat - Direct communication with admin
//  =================================================
//
//  Features:
//  - Real-time chat with admin support
//  - FAQ quick answers as buttons
//  - Multilingual (uses app language)  
//  - Chat history
//  - Rating system after resolution
//

import SwiftUI
import Combine

// MARK: - Models

struct SupportChat: Codable {
    let id: Int
    let status: String
    let subject: String?
    let language: String
    let createdAt: String
    let updatedAt: String
    let rating: Int?
    
    enum CodingKeys: String, CodingKey {
        case id, status, subject, language, rating
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
    
    var statusEmoji: String {
        switch status {
        case "open": return "🟢"
        case "waiting": return "🟡"
        case "resolved": return "✅"
        case "closed": return "⚫"
        default: return "⚪"
        }
    }
}

struct SupportMessage: Identifiable, Codable {
    let id: Int
    let senderType: String
    let message: String
    let messageType: String
    let isRead: Bool
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, message
        case senderType = "sender_type"
        case messageType = "message_type"
        case isRead = "is_read"
        case createdAt = "created_at"
    }
    
    var isAdmin: Bool { senderType == "admin" }
    var isSystem: Bool { messageType == "system" }
}

struct FAQItem: Identifiable, Codable {
    let id: Int
    let category: String
    let question: String
    let answer: String
}

// API Response wrappers
struct ChatResponse: Codable {
    let chat: SupportChat?
    let messages: [SupportMessage]?
    let isNew: Bool?
    
    enum CodingKeys: String, CodingKey {
        case chat, messages
        case isNew = "is_new"
    }
}

struct FAQResponse: Codable {
    let faq: [FAQItem]
}

struct SendMessageResponse: Codable {
    let message: SupportMessage
}


// MARK: - View Model

@MainActor
class SupportChatViewModel: ObservableObject {
    @Published var chat: SupportChat?
    @Published var messages: [SupportMessage] = []
    @Published var faqItems: [FAQItem] = []
    @Published var inputText = ""
    @Published var isLoading = false
    @Published var showFAQ = true
    @Published var errorMessage: String?
    @Published var showRating = false
    @Published var selectedRating = 0
    
    private var refreshTimer: Timer?
    
    init() {
        loadChat()
        loadFAQ()
    }
    
    deinit {
        refreshTimer?.invalidate()
    }
    
    // MARK: - Load Chat
    
    func loadChat() {
        Task {
            isLoading = true
            defer { isLoading = false }
            
            do {
                let response: ChatResponse = try await NetworkService.shared.get("/support/chat")
                self.chat = response.chat
                self.messages = response.messages ?? []
                if chat != nil {
                    showFAQ = false
                    startAutoRefresh()
                }
            } catch {
                // No active chat = show FAQ
                showFAQ = true
            }
        }
    }
    
    // MARK: - Create Chat
    
    func createChat() {
        Task {
            isLoading = true
            defer { isLoading = false }
            
            let lang = LocalizationManager.shared.currentLanguage.rawValue
            let body: [String: String] = ["language": lang]
            
            do {
                let response: ChatResponse = try await NetworkService.shared.post("/support/chat", body: body)
                self.chat = response.chat
                self.messages = response.messages ?? []
                self.showFAQ = false
                startAutoRefresh()
                HapticFeedback.success()
            } catch {
                self.errorMessage = "Failed to create chat"
            }
        }
    }
    
    // MARK: - Send Message
    
    func sendMessage() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        
        // Instantly show user message (optimistic)
        let optimistic = SupportMessage(
            id: Int.random(in: 100000...999999),
            senderType: "user",
            message: text,
            messageType: "text",
            isRead: false,
            createdAt: ISO8601DateFormatter().string(from: Date())
        )
        messages.append(optimistic)
        inputText = ""
        HapticFeedback.light()
        
        Task {
            do {
                let body = ["message": text]
                let _: SendMessageResponse = try await NetworkService.shared.post("/support/chat/message", body: body)
                // Refresh to get server-confirmed message
                await refreshMessages()
            } catch {
                // Remove optimistic message on failure
                messages.removeAll { $0.id == optimistic.id }
                errorMessage = "Failed to send message"
            }
        }
    }
    
    // MARK: - Send FAQ as message
    
    func sendFAQAnswer(_ faq: FAQItem) {
        if chat == nil {
            createChat()
        }
        
        // Wait a bit for chat creation then send
        Task {
            try? await Task.sleep(nanoseconds: 500_000_000)
            inputText = faq.question
            sendMessage()
        }
    }
    
    // MARK: - Load FAQ
    
    func loadFAQ() {
        Task {
            let lang = LocalizationManager.shared.currentLanguage.rawValue
            do {
                let response: FAQResponse = try await NetworkService.shared.get("/support/faq?language=\(lang)")
                self.faqItems = response.faq
            } catch {
                // Silent fail - FAQ is optional
            }
        }
    }
    
    // MARK: - Close Chat
    
    func closeChat() {
        Task {
            do {
                try await NetworkService.shared.postIgnoreResponse("/support/chat/close")
                self.chat = nil
                self.messages = []
                self.showFAQ = true
                refreshTimer?.invalidate()
                HapticFeedback.medium()
            } catch {
                errorMessage = "Failed to close chat"
            }
        }
    }
    
    // MARK: - Rate Chat
    
    func rateChat() {
        guard selectedRating > 0 else { return }
        Task {
            do {
                let body = ["rating": selectedRating]
                try await NetworkService.shared.postIgnoreResponse("/support/chat/rate", body: body)
                showRating = false
                HapticFeedback.success()
            } catch {
                // Silent
            }
        }
    }
    
    // MARK: - Auto Refresh
    
    private func startAutoRefresh() {
        refreshTimer?.invalidate()
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                await self?.refreshMessages()
            }
        }
    }
    
    func refreshMessages() async {
        guard chat != nil else { return }
        do {
            let response: ChatResponse = try await NetworkService.shared.get("/support/chat")
            if let newChat = response.chat {
                self.chat = newChat
                self.messages = response.messages ?? []
                
                // Check if resolved → show rating
                if newChat.status == "resolved" && newChat.rating == nil {
                    showRating = true
                    refreshTimer?.invalidate()
                }
            }
        } catch {
            // Silent refresh failure
        }
    }
}


// MARK: - Support Chat View

struct SupportChatView: View {
    @StateObject private var viewModel = SupportChatViewModel()
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    if viewModel.chat != nil {
                        // Active chat
                        chatContent
                        inputBar
                    } else {
                        // No chat - show welcome + FAQ
                        welcomeContent
                    }
                }
            }
            .navigationTitle("support_title".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if viewModel.chat != nil {
                    ToolbarItem(placement: .topBarTrailing) {
                        Menu {
                            Button(role: .destructive, action: viewModel.closeChat) {
                                Label("close_chat".localized, systemImage: "xmark.circle")
                            }
                        } label: {
                            Image(systemName: "ellipsis.circle")
                                .foregroundColor(.enlikoPrimary)
                        }
                    }
                }
            }
            .alert("rate_support".localized, isPresented: $viewModel.showRating) {
                ForEach(1...5, id: \.self) { star in
                    Button("\(String(repeating: "⭐", count: star))") {
                        viewModel.selectedRating = star
                        viewModel.rateChat()
                    }
                }
                Button("common_cancel".localized, role: .cancel) {}
            } message: {
                Text("rate_support_message".localized)
            }
        }
    }
    
    // MARK: - Welcome Content (No Active Chat)
    
    private var welcomeContent: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 16) {
                    ZStack {
                        Circle()
                            .fill(
                                LinearGradient(
                                    colors: [.enlikoPrimary, .enlikoAccent],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                            .frame(width: 80, height: 80)
                        
                        Image(systemName: "headphones.circle.fill")
                            .font(.system(size: 40))
                            .foregroundColor(.white)
                    }
                    
                    Text("support_welcome_title".localized)
                        .font(.title2.bold())
                        .foregroundColor(.white)
                    
                    Text("support_welcome_subtitle".localized)
                        .font(.subheadline)
                        .foregroundColor(.enlikoTextSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 32)
                }
                .padding(.top, 40)
                
                // Start Chat Button
                Button(action: viewModel.createChat) {
                    HStack {
                        Image(systemName: "bubble.left.and.bubble.right.fill")
                        Text("start_chat".localized)
                            .fontWeight(.semibold)
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        LinearGradient(
                            colors: [.enlikoPrimary, .enlikoAccent],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(16)
                }
                .padding(.horizontal, 32)
                
                // FAQ Section
                if !viewModel.faqItems.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("faq_title".localized)
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding(.horizontal)
                        
                        // Group by category
                        let categories = Dictionary(grouping: viewModel.faqItems, by: { $0.category })
                        
                        ForEach(Array(categories.keys.sorted()), id: \.self) { category in
                            VStack(alignment: .leading, spacing: 8) {
                                Text(category.capitalized)
                                    .font(.subheadline.bold())
                                    .foregroundColor(.enlikoPrimary)
                                    .padding(.horizontal)
                                
                                ForEach(categories[category] ?? []) { faq in
                                    FAQButton(faq: faq) {
                                        viewModel.sendFAQAnswer(faq)
                                    }
                                }
                            }
                        }
                    }
                    .padding(.top, 8)
                }
            }
            .padding()
        }
    }
    
    // MARK: - Chat Content
    
    private var chatContent: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 12) {
                    // Chat status header
                    if let chat = viewModel.chat {
                        HStack {
                            Text(chat.statusEmoji)
                            Text("chat_status_\(chat.status)".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                        .padding(.vertical, 8)
                    }
                    
                    ForEach(viewModel.messages) { message in
                        SupportMessageBubble(message: message)
                            .id(message.id)
                    }
                }
                .padding()
            }
            .onChange(of: viewModel.messages.count) { _, _ in
                if let lastId = viewModel.messages.last?.id {
                    withAnimation {
                        proxy.scrollTo(lastId, anchor: .bottom)
                    }
                }
            }
        }
    }
    
    // MARK: - Input Bar
    
    private var inputBar: some View {
        HStack(spacing: 12) {
            // FAQ button
            Button(action: { viewModel.showFAQ.toggle() }) {
                Image(systemName: "questionmark.circle.fill")
                    .font(.title2)
                    .foregroundColor(viewModel.showFAQ ? .enlikoPrimary : .enlikoTextSecondary)
            }
            
            // Text field
            HStack {
                TextField("type_message".localized, text: $viewModel.inputText)
                    .textFieldStyle(.plain)
                    .focused($isInputFocused)
                    .submitLabel(.send)
                    .onSubmit(viewModel.sendMessage)
                
                if !viewModel.inputText.isEmpty {
                    Button(action: { viewModel.inputText = "" }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.enlikoTextSecondary)
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.enlikoCard)
            .cornerRadius(25)
            
            // Send button
            Button(action: viewModel.sendMessage) {
                ZStack {
                    Circle()
                        .fill(
                            viewModel.inputText.isEmpty
                            ? AnyShapeStyle(Color.enlikoCard)
                            : AnyShapeStyle(LinearGradient(colors: [.enlikoPrimary, .enlikoAccent], startPoint: .topLeading, endPoint: .bottomTrailing))
                        )
                        .frame(width: 44, height: 44)
                    
                    Image(systemName: "arrow.up")
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(viewModel.inputText.isEmpty ? .enlikoTextSecondary : .white)
                }
            }
            .disabled(viewModel.inputText.isEmpty)
        }
        .padding(.horizontal)
        .padding(.vertical, 12)
        .background(
            Rectangle()
                .fill(.ultraThinMaterial)
                .ignoresSafeArea()
        )
    }
}


// MARK: - Support Message Bubble

struct SupportMessageBubble: View {
    let message: SupportMessage
    
    var body: some View {
        if message.isSystem {
            // System message (centered)
            Text(message.message)
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                .frame(maxWidth: .infinity)
        } else {
            HStack(alignment: .top, spacing: 10) {
                if message.isAdmin {
                    // Admin avatar
                    ZStack {
                        Circle()
                            .fill(
                                LinearGradient(
                                    colors: [.enlikoPrimary, .enlikoAccent],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                            .frame(width: 32, height: 32)
                        
                        Image(systemName: "headphones")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.white)
                    }
                }
                
                VStack(alignment: message.isAdmin ? .leading : .trailing, spacing: 4) {
                    Text(message.message)
                        .font(.body)
                        .foregroundColor(.white)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 10)
                        .background(
                            RoundedRectangle(cornerRadius: 18)
                                .fill(message.isAdmin ? Color.enlikoCard : Color.enlikoPrimary)
                        )
                    
                    HStack(spacing: 4) {
                        Text(message.createdAt.formattedDate)
                            .font(.caption2)
                            .foregroundColor(.enlikoTextMuted)
                        
                        if !message.isAdmin && message.isRead {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.system(size: 10))
                                .foregroundColor(.enlikoPrimary)
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: message.isAdmin ? .leading : .trailing)
                
                if !message.isAdmin {
                    Spacer().frame(width: 32)
                }
            }
        }
    }
}


// MARK: - FAQ Button

struct FAQButton: View {
    let faq: FAQItem
    let onTap: () -> Void
    
    @State private var isExpanded = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button(action: { withAnimation { isExpanded.toggle() } }) {
                HStack {
                    Image(systemName: categoryIcon)
                        .foregroundColor(.enlikoPrimary)
                        .frame(width: 24)
                    
                    Text(faq.question)
                        .font(.subheadline)
                        .foregroundColor(.white)
                        .multilineTextAlignment(.leading)
                    
                    Spacer()
                    
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.enlikoTextSecondary)
                        .font(.caption)
                }
            }
            
            if isExpanded {
                Text(faq.answer)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                    .padding(.leading, 32)
                
                Button(action: onTap) {
                    Text("ask_about_this".localized)
                        .font(.caption.bold())
                        .foregroundColor(.enlikoPrimary)
                        .padding(.leading, 32)
                }
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.enlikoSurface)
        .cornerRadius(12)
        .padding(.horizontal)
    }
    
    private var categoryIcon: String {
        switch faq.category {
        case "api": return "key.fill"
        case "trading": return "chart.line.uptrend.xyaxis"
        case "billing": return "creditcard.fill"
        default: return "questionmark.circle.fill"
        }
    }
}


// MARK: - Floating Support Button (replaces Copilot button)

struct FloatingSupportButton: View {
    @Binding var isOpen: Bool
    @State private var isPulsing = false
    
    var body: some View {
        Button(action: {
            withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                isOpen = true
            }
            HapticFeedback.medium()
        }) {
            ZStack {
                // Glow
                Circle()
                    .fill(Color.enlikoPrimary.opacity(0.3))
                    .frame(width: 70, height: 70)
                    .scaleEffect(isPulsing ? 1.2 : 1.0)
                
                // Main button
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.enlikoPrimary, .enlikoAccent],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 56, height: 56)
                    .shadow(color: .enlikoPrimary.opacity(0.5), radius: 15, y: 5)
                
                Image(systemName: "headphones.circle.fill")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
            }
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 1.5).repeatForever(autoreverses: true)) {
                isPulsing = true
            }
        }
    }
}


// MARK: - Preview

#Preview {
    SupportChatView()
        .preferredColorScheme(.dark)
}
