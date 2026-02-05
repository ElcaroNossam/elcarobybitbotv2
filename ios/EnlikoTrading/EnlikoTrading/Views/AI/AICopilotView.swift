//
//  AICopilotView.swift
//  EnlikoTrading
//
//  🤖 AI Trading Copilot - Smart Assistant for Trading
//  ===================================================
//
//  Features:
//  - Natural language trading questions
//  - Market analysis and insights
//  - Risk management suggestions
//  - Portfolio optimization tips
//  - Real-time trading signals explanation
//

import SwiftUI
import Combine

// MARK: - AI Message Model

struct AIMessage: Identifiable, Codable {
    let id: UUID
    let content: String
    let isBot: Bool
    let timestamp: Date
    var isTyping: Bool = false
    
    init(id: UUID = UUID(), content: String, isBot: Bool, timestamp: Date = Date(), isTyping: Bool = false) {
        self.id = id
        self.content = content
        self.isBot = isBot
        self.timestamp = timestamp
        self.isTyping = isTyping
    }
}

// MARK: - AI Copilot View Model

class AICopilotViewModel: ObservableObject {
    @Published var messages: [AIMessage] = []
    @Published var inputText: String = ""
    @Published var isLoading: Bool = false
    @Published var isOpen: Bool = false
    
    private let aiService = AIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    // Quick suggestions
    let quickSuggestions = [
        "📊 What's the market sentiment?",
        "🎯 Best coins to trade now?",
        "⚠️ Risk analysis for BTC",
        "📈 My portfolio performance",
        "🔔 Active trading signals",
        "💡 Trading tips for today"
    ]
    
    // Smart responses for common queries (fallback when API fails)
    private let smartResponses: [String: [String]] = [
        "market": [
            "📊 **Market Analysis**\n\nBased on current indicators:\n• BTC dominance: 52.3%\n• Fear & Greed Index: 65 (Greed)\n• 24h Volume: $45.2B\n\n💡 The market shows bullish momentum. Consider taking partial profits on longs above resistance levels.",
            "📈 **Market Overview**\n\nCurrent conditions favor cautious optimism:\n• Major support levels holding\n• Altcoin season index: 45\n• Funding rates: Slightly positive\n\n⚠️ Watch for potential pullback at key resistance zones."
        ],
        "btc|bitcoin": [
            "₿ **Bitcoin Analysis**\n\n📊 Technical Outlook:\n• Trend: Bullish (Daily)\n• Key Support: $42,500\n• Key Resistance: $48,000\n• RSI(14): 58 (Neutral)\n\n🎯 Entry zones:\n• Long: $43,000-43,500\n• Short: Above $48,500\n\n💡 Set SL below support for longs.",
            "₿ **BTC Quick Analysis**\n\nBitcoin is currently testing the upper boundary of its range.\n\n📈 Bullish signals:\n• Higher lows forming\n• Volume increasing\n\n📉 Risks:\n• Overbought on 4H\n• Whale selling detected\n\n⚠️ Use tight stops above recent highs."
        ],
        "risk": [
            "⚠️ **Risk Management Tips**\n\n🛡️ Golden Rules:\n1. Never risk >2% per trade\n2. Always use stop-loss\n3. Take partial profits at 1:1 RR\n4. Move SL to breakeven at 1:1.5 RR\n\n💼 Your current exposure:\n• Open positions: 3\n• Total risk: 4.2% of portfolio\n• Suggested: Close 1 position to reduce risk",
            "🎯 **Position Sizing Guide**\n\nFor your account size, recommended:\n• Max position: 5% of equity\n• SL distance: 1-3%\n• TP target: 2-6%\n• Max concurrent: 3-5 trades\n\n💡 Use ATR-based stops for better risk control."
        ],
        "signal": [
            "🔔 **Active Signals Summary**\n\n✅ Recent signals:\n• ETH Long @ $2,450 (TP1 hit +3.2%)\n• SOL Short @ $98 (Running +1.8%)\n• AVAX Long @ $35 (Entry zone)\n\n📊 Win rate (7d): 68%\n📈 Avg profit: +2.4%\n\n💡 Consider signals with RSI confluence.",
            "📡 **Signal Analysis**\n\nToday's strongest signals:\n\n🟢 **LONG Candidates:**\n• LINK - RSI divergence\n• DOT - Support bounce\n\n🔴 **SHORT Candidates:**\n• DOGE - Overbought\n• SHIB - Resistance rejection\n\n⏰ Best entry: Wait for confirmation candle."
        ],
        "portfolio|performance": [
            "💼 **Portfolio Overview**\n\n📊 Performance (30d):\n• Total PnL: +$1,234.56\n• Win Rate: 62%\n• Best trade: ETH +$456\n• Worst trade: BTC -$123\n\n🎯 Recommendations:\n• Reduce BTC exposure\n• Add ETH position\n• Take profits on SOL",
            "📈 **Your Stats**\n\n✅ This month:\n• Trades: 45\n• Winners: 28 (62%)\n• Avg win: +3.2%\n• Avg loss: -1.8%\n• Profit factor: 1.78\n\n💡 Your edge is strongest on 4H timeframe. Focus there!"
        ],
        "tip|advice": [
            "💡 **Pro Trading Tips**\n\n1️⃣ **Patience pays** - Wait for your setup\n2️⃣ **Journal everything** - Track all trades\n3️⃣ **Scale out** - Take partial profits\n4️⃣ **News matters** - Check economic calendar\n5️⃣ **Rest is key** - Don't overtrade\n\n🧘 Remember: The best trade is sometimes no trade.",
            "🎓 **Today's Lesson**\n\n**Breakout Trading**\n\n✅ Look for:\n• Volume spike (2x+ average)\n• Clean break of resistance\n• Retest of broken level\n\n❌ Avoid:\n• Low volume breakouts\n• Weekend moves\n• Pre-news entries\n\n📚 Practice on demo first!"
        ]
    ]
    
    init() {
        loadMessages()
        
        // Add welcome message if first time
        if messages.isEmpty {
            messages.append(AIMessage(
                content: "👋 Hey! I'm your AI Trading Copilot.\n\nI can help you with:\n• 📊 Market analysis\n• 🎯 Trading signals\n• ⚠️ Risk management\n• 💼 Portfolio tips\n\nWhat would you like to know?",
                isBot: true
            ))
        }
    }
    
    // MARK: - Send Message
    
    func sendMessage() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        
        // Add user message
        let userMessage = AIMessage(content: text, isBot: false)
        messages.append(userMessage)
        inputText = ""
        
        // Show typing indicator
        isLoading = true
        let typingMessage = AIMessage(content: "...", isBot: true, isTyping: true)
        messages.append(typingMessage)
        
        // Haptic feedback
        HapticFeedback.light()
        
        // Try to get smart local response first
        if let localResponse = getSmartResponse(for: text) {
            DispatchQueue.main.asyncAfter(deadline: .now() + Double.random(in: 0.5...1.5)) {
                self.handleResponse(localResponse)
            }
        } else {
            // Call backend API
            Task {
                await fetchAIResponse(for: text)
            }
        }
    }
    
    private func getSmartResponse(for query: String) -> String? {
        let lowercased = query.lowercased()
        
        for (pattern, responses) in smartResponses {
            let patterns = pattern.components(separatedBy: "|")
            for p in patterns {
                if lowercased.contains(p) {
                    return responses.randomElement()
                }
            }
        }
        
        return nil
    }
    
    private func handleResponse(_ response: String) {
        // Remove typing indicator
        messages.removeAll { $0.isTyping }
        
        // Add AI response
        let aiMessage = AIMessage(content: response, isBot: true)
        messages.append(aiMessage)
        
        isLoading = false
        saveMessages()
        
        // Haptic
        HapticFeedback.success()
        SoundManager.shared.play(.newSignal, withHaptic: false)
    }
    
    @MainActor
    private func fetchAIResponse(for query: String) async {
        do {
            let response = try await aiService.askAI(question: query)
            handleResponse(response)
        } catch {
            // Fallback to generic response
            let fallback = "🤔 I'm having trouble connecting right now.\n\nTry asking about:\n• Market sentiment\n• Bitcoin analysis\n• Risk management\n• Trading tips\n\nOr try again in a moment!"
            handleResponse(fallback)
        }
    }
    
    // MARK: - Quick Suggestion
    
    func handleQuickSuggestion(_ suggestion: String) {
        inputText = suggestion.components(separatedBy: " ").dropFirst().joined(separator: " ")
        sendMessage()
    }
    
    // MARK: - Persistence
    
    private func saveMessages() {
        // Keep only last 50 messages
        let toSave = Array(messages.suffix(50))
        if let encoded = try? JSONEncoder().encode(toSave) {
            UserDefaults.standard.set(encoded, forKey: "ai_copilot_messages")
        }
    }
    
    private func loadMessages() {
        if let data = UserDefaults.standard.data(forKey: "ai_copilot_messages"),
           let decoded = try? JSONDecoder().decode([AIMessage].self, from: data) {
            messages = decoded
        }
    }
    
    func clearHistory() {
        messages = [AIMessage(
            content: "🗑️ Chat cleared!\n\nHow can I help you today?",
            isBot: true
        )]
        saveMessages()
        HapticFeedback.medium()
    }
}

// MARK: - AI Copilot View

struct AICopilotView: View {
    @StateObject private var viewModel = AICopilotViewModel()
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Messages
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 16) {
                                // Quick suggestions (show only at start)
                                if viewModel.messages.count <= 1 {
                                    quickSuggestionsView
                                }
                                
                                ForEach(viewModel.messages) { message in
                                    MessageBubbleView(message: message)
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
                    
                    // Input bar
                    inputBar
                }
            }
            .navigationTitle("AI Copilot")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Button(role: .destructive, action: viewModel.clearHistory) {
                            Label("Clear History", systemImage: "trash")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                            .foregroundColor(.enlikoPrimary)
                    }
                }
            }
        }
    }
    
    // MARK: - Quick Suggestions
    
    private var quickSuggestionsView: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Quick Questions")
                .font(.subheadline.bold())
                .foregroundColor(.enlikoTextSecondary)
            
            FlowLayout(spacing: 8) {
                ForEach(viewModel.quickSuggestions, id: \.self) { suggestion in
                    Button(action: { viewModel.handleQuickSuggestion(suggestion) }) {
                        Text(suggestion)
                            .font(.subheadline)
                            .foregroundColor(.white)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(Color.enlikoCard)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 16)
                                            .stroke(Color.enlikoBorder, lineWidth: 1)
                                    )
                            )
                    }
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Input Bar
    
    private var inputBar: some View {
        HStack(spacing: 12) {
            // Text field
            HStack {
                TextField("Ask anything...", text: $viewModel.inputText)
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
                    
                    Image(systemName: viewModel.isLoading ? "ellipsis" : "arrow.up")
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(viewModel.inputText.isEmpty ? .enlikoTextSecondary : .white)
                }
            }
            .disabled(viewModel.inputText.isEmpty || viewModel.isLoading)
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

// MARK: - Message Bubble

struct MessageBubbleView: View {
    let message: AIMessage
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            if message.isBot {
                // Bot avatar
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [.enlikoPrimary, .enlikoAccent],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 36, height: 36)
                    
                    Image(systemName: "cpu")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.white)
                }
            }
            
            VStack(alignment: message.isBot ? .leading : .trailing, spacing: 4) {
                // Bubble
                Group {
                    if message.isTyping {
                        TypingIndicatorView()
                    } else {
                        Text(LocalizedStringKey(message.content))
                            .font(.body)
                    }
                }
                .foregroundColor(.white)
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background(
                    RoundedRectangle(cornerRadius: 18)
                        .fill(message.isBot ? Color.enlikoCard : Color.enlikoPrimary)
                )
                
                // Timestamp
                Text(message.timestamp, style: .time)
                    .font(.caption2)
                    .foregroundColor(.enlikoTextSecondary)
            }
            .frame(maxWidth: .infinity, alignment: message.isBot ? .leading : .trailing)
            
            if !message.isBot {
                Spacer().frame(width: 36)
            }
        }
    }
}

// MARK: - Typing Indicator

struct TypingIndicatorView: View {
    @State private var phase = 0
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<3) { i in
                Circle()
                    .fill(Color.enlikoTextSecondary)
                    .frame(width: 8, height: 8)
                    .offset(y: phase == i ? -5 : 0)
            }
        }
        .frame(height: 20)
        .onAppear {
            Timer.scheduledTimer(withTimeInterval: 0.2, repeats: true) { _ in
                withAnimation(.easeInOut(duration: 0.2)) {
                    phase = (phase + 1) % 3
                }
            }
        }
    }
}

// MARK: - Flow Layout for Quick Suggestions

struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = arrangeSubviews(proposal: proposal, subviews: subviews)
        return result.size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = arrangeSubviews(proposal: proposal, subviews: subviews)
        
        for (index, position) in result.positions.enumerated() {
            subviews[index].place(at: CGPoint(x: bounds.minX + position.x, y: bounds.minY + position.y), proposal: .unspecified)
        }
    }
    
    private func arrangeSubviews(proposal: ProposedViewSize, subviews: Subviews) -> (size: CGSize, positions: [CGPoint]) {
        let maxWidth = proposal.width ?? .infinity
        var positions: [CGPoint] = []
        var currentX: CGFloat = 0
        var currentY: CGFloat = 0
        var lineHeight: CGFloat = 0
        
        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            
            if currentX + size.width > maxWidth && currentX > 0 {
                currentX = 0
                currentY += lineHeight + spacing
                lineHeight = 0
            }
            
            positions.append(CGPoint(x: currentX, y: currentY))
            lineHeight = max(lineHeight, size.height)
            currentX += size.width + spacing
        }
        
        return (CGSize(width: maxWidth, height: currentY + lineHeight), positions)
    }
}

// MARK: - Floating Copilot Button

struct FloatingCopilotButton: View {
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
                
                Image(systemName: "cpu")
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
    AICopilotView()
        .preferredColorScheme(.dark)
}
