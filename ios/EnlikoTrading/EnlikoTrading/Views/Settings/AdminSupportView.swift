//
//  AdminSupportView.swift
//  EnlikoTrading
//
//  Admin interface for managing support chats
//

import SwiftUI
import Combine

// MARK: - Admin Support List View

struct AdminSupportView: View {
    @StateObject private var viewModel = AdminSupportViewModel()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Stats bar
                if let stats = viewModel.stats {
                    HStack(spacing: 12) {
                        StatPill(label: "Open", value: "\(stats.open)", color: .green)
                        StatPill(label: "Waiting", value: "\(stats.waiting)", color: .yellow)
                        StatPill(label: "Today", value: "\(stats.resolvedToday)", color: .blue)
                    }
                    .padding(.horizontal)
                }
                
                if viewModel.isLoading {
                    ProgressView()
                        .padding(.top, 60)
                } else if viewModel.chats.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "bubble.left.and.bubble.right")
                            .font(.system(size: 50))
                            .foregroundColor(.gray)
                        Text("No support chats")
                            .foregroundColor(.gray)
                    }
                    .padding(.top, 60)
                } else {
                    ForEach(viewModel.chats, id: \.chatId) { chat in
                        NavigationLink(destination: AdminChatDetailView(chatId: chat.chatId)) {
                            AdminChatRow(chat: chat)
                        }
                    }
                    .padding(.horizontal)
                }
            }
            .padding(.top)
        }
        .background(Color.enlikoBackground)
        .navigationTitle("Support Chats")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button(action: { viewModel.loadChats() }) {
                    Image(systemName: "arrow.clockwise")
                }
            }
        }
    }
}


// MARK: - Admin Chat Row

struct AdminChatRow: View {
    let chat: AdminSupportChat
    
    var body: some View {
        HStack(spacing: 12) {
            // Status indicator
            Circle()
                .fill(chat.statusColor)
                .frame(width: 10, height: 10)
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(chat.userName)
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    if chat.unreadCount > 0 {
                        Text("\(chat.unreadCount)")
                            .font(.caption2.bold())
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Color.enlikoPrimary)
                            .clipShape(Capsule())
                    }
                }
                
                if let lastMsg = chat.lastMessage {
                    Text(lastMsg)
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                        .lineLimit(1)
                }
                
                HStack {
                    Text(chat.status.uppercased())
                        .font(.system(size: 10, weight: .bold))
                        .foregroundColor(chat.statusColor)
                    
                    Text("•")
                        .foregroundColor(.gray)
                    
                    Text(chat.language.uppercased())
                        .font(.system(size: 10))
                        .foregroundColor(.gray)
                    
                    Spacer()
                    
                    Text(chat.updatedAt)
                        .font(.caption2)
                        .foregroundColor(.gray)
                }
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(12)
    }
}


// MARK: - Admin Chat Detail View

struct AdminChatDetailView: View {
    let chatId: Int
    @StateObject private var viewModel = AdminChatDetailViewModel()
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // Messages
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(viewModel.messages) { message in
                            AdminMessageBubble(message: message)
                                .id(message.id)
                        }
                    }
                    .padding()
                }
                .onChange(of: viewModel.messages.count) { _, _ in
                    if let lastId = viewModel.messages.last?.id {
                        withAnimation { proxy.scrollTo(lastId, anchor: .bottom) }
                    }
                }
            }
            
            // Input bar
            HStack(spacing: 12) {
                TextField("Reply...", text: $viewModel.replyText)
                    .textFieldStyle(.plain)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(Color.enlikoCard)
                    .cornerRadius(25)
                    .focused($isInputFocused)
                    .submitLabel(.send)
                    .onSubmit { viewModel.sendReply(chatId: chatId) }
                
                Button(action: { viewModel.sendReply(chatId: chatId) }) {
                    ZStack {
                        Circle()
                            .fill(
                                viewModel.replyText.isEmpty
                                ? AnyShapeStyle(Color.enlikoCard)
                                : AnyShapeStyle(LinearGradient(colors: [.enlikoPrimary, .enlikoAccent], startPoint: .topLeading, endPoint: .bottomTrailing))
                            )
                            .frame(width: 44, height: 44)
                        
                        Image(systemName: "arrow.up")
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(viewModel.replyText.isEmpty ? .gray : .white)
                    }
                }
                .disabled(viewModel.replyText.isEmpty)
            }
            .padding(.horizontal)
            .padding(.vertical, 12)
            .background(.ultraThinMaterial)
        }
        .background(Color.enlikoBackground)
        .navigationTitle("Chat #\(chatId)")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Button(action: { viewModel.resolveChat(chatId: chatId) }) {
                        Label("Resolve", systemImage: "checkmark.circle")
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .task {
            await viewModel.loadChat(chatId: chatId)
        }
    }
}


struct AdminMessageBubble: View {
    let message: SupportMessage
    
    var body: some View {
        if message.isSystem {
            Text(message.message)
                .font(.caption)
                .foregroundColor(.gray)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                .frame(maxWidth: .infinity)
        } else {
            HStack(alignment: .top, spacing: 10) {
                if !message.isAdmin {
                    // User avatar
                    ZStack {
                        Circle()
                            .fill(Color.enlikoCard)
                            .frame(width: 32, height: 32)
                        Image(systemName: "person.fill")
                            .font(.system(size: 14))
                            .foregroundColor(.gray)
                    }
                }
                
                VStack(alignment: message.isAdmin ? .trailing : .leading, spacing: 4) {
                    Text(message.message)
                        .font(.body)
                        .foregroundColor(.white)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 10)
                        .background(
                            RoundedRectangle(cornerRadius: 18)
                                .fill(message.isAdmin ? Color.enlikoPrimary : Color.enlikoCard)
                        )
                    
                    Text(message.createdAt.formattedDate)
                        .font(.caption2)
                        .foregroundColor(.enlikoTextMuted)
                }
                .frame(maxWidth: .infinity, alignment: message.isAdmin ? .trailing : .leading)
                
                if message.isAdmin {
                    Spacer().frame(width: 32)
                }
            }
        }
    }
}


// MARK: - Stat Pill

struct StatPill: View {
    let label: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3.bold())
                .foregroundColor(color)
            Text(label)
                .font(.caption2)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}


// MARK: - Models

struct AdminSupportChat: Codable {
    let chatId: Int
    let userId: Int
    let userName: String
    let status: String
    let language: String
    let unreadCount: Int
    let lastMessage: String?
    let updatedAt: String
    
    enum CodingKeys: String, CodingKey {
        case status, language
        case chatId = "chat_id"
        case userId = "user_id"
        case userName = "user_name"
        case unreadCount = "unread_count"
        case lastMessage = "last_message"
        case updatedAt = "updated_at"
    }
    
    var statusColor: Color {
        switch status {
        case "open": return .green
        case "waiting": return .yellow
        case "resolved": return .blue
        default: return .gray
        }
    }
}

struct AdminSupportStats: Codable {
    let total: Int
    let open: Int
    let waiting: Int
    let resolved: Int
    let closed: Int
    let resolvedToday: Int
    let avgRating: Double?
    
    enum CodingKeys: String, CodingKey {
        case total, open, waiting, resolved, closed
        case resolvedToday = "resolved_today"
        case avgRating = "avg_rating"
    }
}

struct AdminChatsResponse: Codable {
    let chats: [AdminSupportChat]
}

struct AdminChatDetailResponse: Codable {
    let chat: SupportChat
    let messages: [SupportMessage]
}


// MARK: - View Models

@MainActor
class AdminSupportViewModel: ObservableObject {
    @Published var chats: [AdminSupportChat] = []
    @Published var stats: AdminSupportStats?
    @Published var isLoading = false
    
    init() { loadChats() }
    
    func loadChats() {
        Task {
            isLoading = true
            defer { isLoading = false }
            
            do {
                let response: AdminChatsResponse = try await NetworkService.shared.get("/support/admin/chats")
                self.chats = response.chats
                
                let statsResp: AdminSupportStats = try await NetworkService.shared.get("/support/admin/stats")
                self.stats = statsResp
            } catch {
                // silent
            }
        }
    }
}

@MainActor
class AdminChatDetailViewModel: ObservableObject {
    @Published var messages: [SupportMessage] = []
    @Published var replyText = ""
    @Published var chat: SupportChat?
    
    private var refreshTimer: Timer?
    
    func loadChat(chatId: Int) async {
        do {
            let response: AdminChatDetailResponse = try await NetworkService.shared.get("/support/admin/chat/\(chatId)")
            self.chat = response.chat
            self.messages = response.messages
            startAutoRefresh(chatId: chatId)
        } catch {
            // silent
        }
    }
    
    func sendReply(chatId: Int) {
        let text = replyText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        
        // Optimistic
        let optimistic = SupportMessage(
            id: Int.random(in: 100000...999999),
            senderType: "admin",
            message: text,
            messageType: "text",
            isRead: true,
            createdAt: ISO8601DateFormatter().string(from: Date())
        )
        messages.append(optimistic)
        replyText = ""
        
        Task {
            do {
                let body = ["message": text]
                let _: SendMessageResponse = try await NetworkService.shared.post("/support/admin/chat/\(chatId)/reply", body: body)
                await loadChat(chatId: chatId)
            } catch {
                messages.removeAll { $0.id == optimistic.id }
            }
        }
    }
    
    func resolveChat(chatId: Int) {
        Task {
            do {
                try await NetworkService.shared.postIgnoreResponse("/support/admin/chat/\(chatId)/resolve")
                await loadChat(chatId: chatId)
            } catch { }
        }
    }
    
    private func startAutoRefresh(chatId: Int) {
        refreshTimer?.invalidate()
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                await self?.loadChat(chatId: chatId)
            }
        }
    }
    
    deinit {
        refreshTimer?.invalidate()
    }
}

#Preview {
    NavigationStack {
        AdminSupportView()
    }
    .preferredColorScheme(.dark)
}
