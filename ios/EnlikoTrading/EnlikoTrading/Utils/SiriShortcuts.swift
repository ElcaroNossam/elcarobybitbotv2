//
//  SiriShortcuts.swift
//  EnlikoTrading
//
//  🎙️ Siri Shortcuts & App Intents
//  ================================
//
//  Features:
//  1. "Hey Siri, what's my crypto balance?"
//  2. "Hey Siri, show my positions"
//  3. "Hey Siri, close all positions"
//  4. Quick shortcuts for common actions
//

import AppIntents
import SwiftUI

// MARK: - Balance Intent

@available(iOS 16.0, *)
struct GetBalanceIntent: AppIntent {
    static var title: LocalizedStringResource = "Get Crypto Balance"
    static var description = IntentDescription("Check your trading balance and PnL")
    
    static var openAppWhenRun: Bool = false
    
    @MainActor
    func perform() async throws -> some IntentResult & ReturnsValue<String> & ProvidesDialog {
        // Fetch balance from cache/API
        let balance = await fetchBalance()
        
        let response = """
        Your total equity is $\(String(format: "%.2f", balance.totalEquity)).
        Today's PnL is \(balance.todayPnL >= 0 ? "plus" : "minus") $\(String(format: "%.2f", abs(balance.todayPnL))).
        Unrealized PnL is \(balance.unrealizedPnL >= 0 ? "plus" : "minus") $\(String(format: "%.2f", abs(balance.unrealizedPnL))).
        """
        
        return .result(
            value: response,
            dialog: IntentDialog(stringLiteral: response)
        )
    }
    
    private func fetchBalance() async -> (totalEquity: Double, todayPnL: Double, unrealizedPnL: Double) {
        // Try to get from cache first
        // In real implementation, fetch from API or cached data
        return (totalEquity: 10000.0, todayPnL: 150.0, unrealizedPnL: 75.0)
    }
}

// MARK: - Positions Intent

@available(iOS 16.0, *)
struct GetPositionsIntent: AppIntent {
    static var title: LocalizedStringResource = "Get Open Positions"
    static var description = IntentDescription("Check your open trading positions")
    
    static var openAppWhenRun: Bool = false
    
    @MainActor
    func perform() async throws -> some IntentResult & ReturnsValue<String> & ProvidesDialog {
        let positions = await fetchPositions()
        
        if positions.isEmpty {
            return .result(
                value: "No open positions",
                dialog: IntentDialog(stringLiteral: "You have no open positions right now.")
            )
        }
        
        var response = "You have \(positions.count) open positions. "
        
        for (index, pos) in positions.prefix(3).enumerated() {
            let pnlWord = pos.pnl >= 0 ? "up" : "down"
            response += "\(index + 1): \(pos.symbol) \(pos.side) is \(pnlWord) \(String(format: "%.1f", abs(pos.pnlPercent))) percent. "
        }
        
        if positions.count > 3 {
            response += "And \(positions.count - 3) more."
        }
        
        return .result(
            value: response,
            dialog: IntentDialog(stringLiteral: response)
        )
    }
    
    private func fetchPositions() async -> [(symbol: String, side: String, pnl: Double, pnlPercent: Double)] {
        // Mock data - in real app, fetch from API
        return [
            (symbol: "BTC", side: "Long", pnl: 50.0, pnlPercent: 2.5),
            (symbol: "ETH", side: "Short", pnl: -20.0, pnlPercent: -1.2)
        ]
    }
}

// MARK: - Price Check Intent

@available(iOS 16.0, *)
struct GetPriceIntent: AppIntent {
    static var title: LocalizedStringResource = "Get Crypto Price"
    static var description = IntentDescription("Check the current price of a cryptocurrency")
    
    @Parameter(title: "Cryptocurrency")
    var crypto: CryptoEntity
    
    static var openAppWhenRun: Bool = false
    
    @MainActor
    func perform() async throws -> some IntentResult & ReturnsValue<String> & ProvidesDialog {
        let price = await fetchPrice(for: crypto.symbol)
        let change = await fetchPriceChange(for: crypto.symbol)
        
        let changeWord = change >= 0 ? "up" : "down"
        let response = "\(crypto.displayName) is currently trading at $\(String(format: "%.2f", price)), \(changeWord) \(String(format: "%.1f", abs(change))) percent in the last 24 hours."
        
        return .result(
            value: response,
            dialog: IntentDialog(stringLiteral: response)
        )
    }
    
    private func fetchPrice(for symbol: String) async -> Double {
        // Mock - in real app, fetch from API
        switch symbol.uppercased() {
        case "BTC": return 43250.0
        case "ETH": return 2250.0
        case "SOL": return 95.0
        default: return 0
        }
    }
    
    private func fetchPriceChange(for symbol: String) async -> Double {
        switch symbol.uppercased() {
        case "BTC": return 2.5
        case "ETH": return -1.2
        case "SOL": return 5.8
        default: return 0
        }
    }
}

// MARK: - Crypto Entity

@available(iOS 16.0, *)
struct CryptoEntity: AppEntity {
    let id: String
    let symbol: String
    let displayName: String
    
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Cryptocurrency"
    static var defaultQuery = CryptoQuery()
    
    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(displayName)")
    }
    
    static let allCryptos = [
        CryptoEntity(id: "btc", symbol: "BTC", displayName: "Bitcoin"),
        CryptoEntity(id: "eth", symbol: "ETH", displayName: "Ethereum"),
        CryptoEntity(id: "sol", symbol: "SOL", displayName: "Solana"),
        CryptoEntity(id: "bnb", symbol: "BNB", displayName: "Binance Coin"),
        CryptoEntity(id: "xrp", symbol: "XRP", displayName: "Ripple"),
        CryptoEntity(id: "doge", symbol: "DOGE", displayName: "Dogecoin"),
        CryptoEntity(id: "ada", symbol: "ADA", displayName: "Cardano"),
        CryptoEntity(id: "avax", symbol: "AVAX", displayName: "Avalanche"),
        CryptoEntity(id: "link", symbol: "LINK", displayName: "Chainlink"),
        CryptoEntity(id: "dot", symbol: "DOT", displayName: "Polkadot")
    ]
}

@available(iOS 16.0, *)
struct CryptoQuery: EntityQuery {
    func entities(for identifiers: [String]) async throws -> [CryptoEntity] {
        CryptoEntity.allCryptos.filter { identifiers.contains($0.id) }
    }
    
    func suggestedEntities() async throws -> [CryptoEntity] {
        Array(CryptoEntity.allCryptos.prefix(5))
    }
}

// MARK: - Quick Trade Intent

@available(iOS 16.0, *)
struct QuickTradeIntent: AppIntent {
    static var title: LocalizedStringResource = "Quick Trade"
    static var description = IntentDescription("Open a quick market order")
    
    @Parameter(title: "Direction")
    var direction: TradeDirection
    
    @Parameter(title: "Cryptocurrency")
    var crypto: CryptoEntity
    
    @Parameter(title: "Amount in USDT")
    var amount: Double
    
    static var openAppWhenRun: Bool = true // Open app for confirmation
    
    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        // This will open the app with pre-filled trade parameters
        // In real implementation, pass data to app via URL or shared storage
        
        return .result(
            dialog: IntentDialog("Opening Enliko to confirm your \(direction.rawValue.lowercased()) order for \(crypto.displayName) worth $\(String(format: "%.0f", amount)).")
        )
    }
}

@available(iOS 16.0, *)
enum TradeDirection: String, AppEnum {
    case long = "Long"
    case short = "Short"
    
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Trade Direction"
    
    static var caseDisplayRepresentations: [TradeDirection: DisplayRepresentation] = [
        .long: "Long (Buy)",
        .short: "Short (Sell)"
    ]
}

// MARK: - Close All Positions Intent

@available(iOS 16.0, *)
struct CloseAllPositionsIntent: AppIntent {
    static var title: LocalizedStringResource = "Close All Positions"
    static var description = IntentDescription("Close all open trading positions")
    
    static var openAppWhenRun: Bool = true // Require confirmation in app
    
    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let positionCount = await fetchPositionCount()
        
        if positionCount == 0 {
            return .result(
                dialog: IntentDialog("You have no open positions to close.")
            )
        }
        
        // This is a destructive action - always open app for confirmation
        return .result(
            dialog: IntentDialog("Opening Enliko to confirm closing \(positionCount) positions.")
        )
    }
    
    private func fetchPositionCount() async -> Int {
        // Mock - in real app, fetch from API
        return 2
    }
}

// MARK: - Market Summary Intent

@available(iOS 16.0, *)
struct MarketSummaryIntent: AppIntent {
    static var title: LocalizedStringResource = "Market Summary"
    static var description = IntentDescription("Get a quick overview of the crypto market")
    
    static var openAppWhenRun: Bool = false
    
    @MainActor
    func perform() async throws -> some IntentResult & ReturnsValue<String> & ProvidesDialog {
        let btcPrice = 43250.0
        let btcChange = 2.5
        let ethPrice = 2250.0
        let ethChange = -1.2
        let fearGreed = 65
        
        var response = "Here's the market summary. "
        response += "Bitcoin is at $\(String(format: "%.0f", btcPrice)), \(btcChange >= 0 ? "up" : "down") \(String(format: "%.1f", abs(btcChange))) percent. "
        response += "Ethereum is at $\(String(format: "%.0f", ethPrice)), \(ethChange >= 0 ? "up" : "down") \(String(format: "%.1f", abs(ethChange))) percent. "
        response += "The fear and greed index is at \(fearGreed), indicating \(fearGreedLabel(fearGreed))."
        
        return .result(
            value: response,
            dialog: IntentDialog(stringLiteral: response)
        )
    }
    
    private func fearGreedLabel(_ value: Int) -> String {
        switch value {
        case 0..<25: return "extreme fear"
        case 25..<45: return "fear"
        case 45..<55: return "neutral sentiment"
        case 55..<75: return "greed"
        default: return "extreme greed"
        }
    }
}

// MARK: - Shortcuts Provider

@available(iOS 16.0, *)
struct EnlikoShortcutsProvider: AppShortcutsProvider {
    @AppShortcutsBuilder
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: GetBalanceIntent(),
            phrases: [
                "Check my \(.applicationName) balance",
                "What's my crypto balance in \(.applicationName)",
                "Show my \(.applicationName) portfolio",
                "How much do I have in \(.applicationName)"
            ],
            shortTitle: "Check Balance",
            systemImageName: "dollarsign.circle.fill"
        )
        
        AppShortcut(
            intent: GetPositionsIntent(),
            phrases: [
                "Show my \(.applicationName) positions",
                "What positions do I have in \(.applicationName)",
                "Check my trades in \(.applicationName)",
                "List my \(.applicationName) open positions"
            ],
            shortTitle: "View Positions",
            systemImageName: "list.bullet.rectangle.fill"
        )
        
        AppShortcut(
            intent: GetPriceIntent(),
            phrases: [
                "What's the price of \(\.$crypto) in \(.applicationName)",
                "How much is \(\.$crypto) in \(.applicationName)",
                "Check \(\.$crypto) price in \(.applicationName)"
            ],
            shortTitle: "Check Price",
            systemImageName: "chart.line.uptrend.xyaxis"
        )
        
        AppShortcut(
            intent: MarketSummaryIntent(),
            phrases: [
                "Give me a \(.applicationName) market summary",
                "What's happening in crypto markets with \(.applicationName)",
                "Crypto market overview in \(.applicationName)"
            ],
            shortTitle: "Market Summary",
            systemImageName: "globe"
        )
    }
}

// MARK: - Spotlight Integration

import CoreSpotlight
import MobileCoreServices

@available(iOS 16.0, *)
class SpotlightManager {
    static let shared = SpotlightManager()
    
    func indexPositions(_ positions: [WatchPositionData]) {
        var searchableItems: [CSSearchableItem] = []
        
        for position in positions {
            let attributeSet = CSSearchableItemAttributeSet(contentType: .content)
            attributeSet.title = "\(position.symbol) \(position.side)"
            attributeSet.contentDescription = "PnL: \(String(format: "%+.2f%%", position.pnlPercent))"
            attributeSet.keywords = ["trade", "position", position.symbol, position.side]
            
            let item = CSSearchableItem(
                uniqueIdentifier: "position-\(position.id)",
                domainIdentifier: "io.enliko.trading.positions",
                attributeSet: attributeSet
            )
            item.expirationDate = Date().addingTimeInterval(3600) // 1 hour
            
            searchableItems.append(item)
        }
        
        CSSearchableIndex.default().indexSearchableItems(searchableItems) { error in
            if let error = error {
                print("Error indexing positions: \(error)")
            }
        }
    }
    
    func indexSymbols(_ symbols: [String]) {
        var searchableItems: [CSSearchableItem] = []
        
        for symbol in symbols {
            let attributeSet = CSSearchableItemAttributeSet(contentType: .content)
            attributeSet.title = symbol.replacingOccurrences(of: "USDT", with: "")
            attributeSet.contentDescription = "Trade \(symbol) on Enliko"
            attributeSet.keywords = ["crypto", "trade", symbol]
            
            let item = CSSearchableItem(
                uniqueIdentifier: "symbol-\(symbol)",
                domainIdentifier: "io.enliko.trading.symbols",
                attributeSet: attributeSet
            )
            
            searchableItems.append(item)
        }
        
        CSSearchableIndex.default().indexSearchableItems(searchableItems)
    }
    
    func removeAllItems() {
        CSSearchableIndex.default().deleteAllSearchableItems()
    }
}

// MARK: - Preview & Testing View

@available(iOS 16.0, *)
struct ShortcutsTestView: View {
    var body: some View {
        List {
            Section("Available Shortcuts") {
                ShortcutRow(
                    title: "Check Balance",
                    phrase: "What's my crypto balance?",
                    icon: "dollarsign.circle.fill",
                    color: .green
                )
                
                ShortcutRow(
                    title: "View Positions",
                    phrase: "Show my positions",
                    icon: "list.bullet.rectangle.fill",
                    color: .blue
                )
                
                ShortcutRow(
                    title: "Check Price",
                    phrase: "What's the Bitcoin price?",
                    icon: "chart.line.uptrend.xyaxis",
                    color: .orange
                )
                
                ShortcutRow(
                    title: "Market Summary",
                    phrase: "Give me a market summary",
                    icon: "globe",
                    color: .purple
                )
            }
            
            Section("Quick Actions") {
                ShortcutRow(
                    title: "Quick Long",
                    phrase: "Long Bitcoin $100",
                    icon: "arrow.up.right.circle.fill",
                    color: .green
                )
                
                ShortcutRow(
                    title: "Close All",
                    phrase: "Close all positions",
                    icon: "xmark.circle.fill",
                    color: .red
                )
            }
        }
        .navigationTitle("Siri Shortcuts")
    }
}

@available(iOS 16.0, *)
struct ShortcutRow: View {
    let title: String
    let phrase: String
    let icon: String
    let color: Color
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.white)
                .frame(width: 44, height: 44)
                .background(color)
                .cornerRadius(10)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.headline)
                Text("\"\(phrase)\"")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .italic()
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview("Shortcuts Test") {
    if #available(iOS 16.0, *) {
        NavigationStack {
            ShortcutsTestView()
        }
    } else {
        Text("iOS 16+ required")
    }
}
