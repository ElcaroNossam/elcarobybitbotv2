//
//  EnlikoWidgets.swift
//  EnlikoTrading
//
//  📱 Home Screen Widgets for Enliko
//  ==========================================
//
//  Widgets:
//  1. Balance Widget - Quick view of account balance
//  2. PnL Widget - Today's profit/loss
//  3. Price Widget - Live crypto prices
//  4. Position Widget - Active positions summary
//

import WidgetKit
import SwiftUI
import Intents

// MARK: - Widget Data Models

struct WidgetBalance: Codable {
    let totalEquity: Double
    let unrealizedPnL: Double
    let todayPnL: Double
    let todayPnLPercent: Double
    let lastUpdated: Date
}

struct WidgetPrice: Codable {
    let symbol: String
    let price: Double
    let change24h: Double
    let lastUpdated: Date
}

struct WidgetPosition: Codable {
    let symbol: String
    let side: String
    let pnl: Double
    let pnlPercent: Double
}

// MARK: - Widget Data Manager

class WidgetDataManager {
    static let shared = WidgetDataManager()
    
    private let userDefaults = UserDefaults(suiteName: "group.io.enliko.trading")
    
    private init() {}
    
    // Balance
    func saveBalance(_ balance: WidgetBalance) {
        if let encoded = try? JSONEncoder().encode(balance) {
            userDefaults?.set(encoded, forKey: "widget_balance")
        }
        WidgetCenter.shared.reloadTimelines(ofKind: "BalanceWidget")
    }
    
    func getBalance() -> WidgetBalance? {
        guard let data = userDefaults?.data(forKey: "widget_balance"),
              let balance = try? JSONDecoder().decode(WidgetBalance.self, from: data) else {
            return nil
        }
        return balance
    }
    
    // Prices
    func savePrices(_ prices: [WidgetPrice]) {
        if let encoded = try? JSONEncoder().encode(prices) {
            userDefaults?.set(encoded, forKey: "widget_prices")
        }
        WidgetCenter.shared.reloadTimelines(ofKind: "PriceWidget")
    }
    
    func getPrices() -> [WidgetPrice] {
        guard let data = userDefaults?.data(forKey: "widget_prices"),
              let prices = try? JSONDecoder().decode([WidgetPrice].self, from: data) else {
            return []
        }
        return prices
    }
    
    // Positions
    func savePositions(_ positions: [WidgetPosition]) {
        if let encoded = try? JSONEncoder().encode(positions) {
            userDefaults?.set(encoded, forKey: "widget_positions")
        }
        WidgetCenter.shared.reloadTimelines(ofKind: "PositionWidget")
    }
    
    func getPositions() -> [WidgetPosition] {
        guard let data = userDefaults?.data(forKey: "widget_positions"),
              let positions = try? JSONDecoder().decode([WidgetPosition].self, from: data) else {
            return []
        }
        return positions
    }
}

// MARK: - Balance Widget Timeline Provider

struct BalanceProvider: TimelineProvider {
    func placeholder(in context: Context) -> BalanceEntry {
        BalanceEntry(date: Date(), balance: sampleBalance)
    }
    
    func getSnapshot(in context: Context, completion: @escaping (BalanceEntry) -> Void) {
        let entry = BalanceEntry(
            date: Date(),
            balance: WidgetDataManager.shared.getBalance() ?? sampleBalance
        )
        completion(entry)
    }
    
    func getTimeline(in context: Context, completion: @escaping (Timeline<BalanceEntry>) -> Void) {
        let currentDate = Date()
        let refreshDate = Calendar.current.date(byAdding: .minute, value: 15, to: currentDate)!
        
        let entry = BalanceEntry(
            date: currentDate,
            balance: WidgetDataManager.shared.getBalance() ?? sampleBalance
        )
        
        let timeline = Timeline(entries: [entry], policy: .after(refreshDate))
        completion(timeline)
    }
    
    private var sampleBalance: WidgetBalance {
        WidgetBalance(
            totalEquity: 10234.56,
            unrealizedPnL: 123.45,
            todayPnL: 234.56,
            todayPnLPercent: 2.34,
            lastUpdated: Date()
        )
    }
}

struct BalanceEntry: TimelineEntry {
    let date: Date
    let balance: WidgetBalance
}

// MARK: - Balance Widget View

struct BalanceWidgetView: View {
    @Environment(\.widgetFamily) var family
    let entry: BalanceEntry
    
    var body: some View {
        switch family {
        case .systemSmall:
            smallBalanceView
        case .systemMedium:
            mediumBalanceView
        default:
            smallBalanceView
        }
    }
    
    private var smallBalanceView: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Image(systemName: "chart.pie.fill")
                    .foregroundColor(.enlikoPrimary)
                Text("Portfolio")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // Balance
            Text("$\(entry.balance.totalEquity.formattedWidget)")
                .font(.system(size: 24, weight: .bold, design: .rounded))
                .foregroundColor(.primary)
            
            // Today's PnL
            HStack(spacing: 4) {
                Image(systemName: entry.balance.todayPnL >= 0 ? "arrow.up.right" : "arrow.down.right")
                    .font(.caption2.bold())
                Text(String(format: "%+.2f%%", entry.balance.todayPnLPercent))
                    .font(.caption.bold())
            }
            .foregroundColor(entry.balance.todayPnL >= 0 ? .green : .red)
        }
        .padding()
        .containerBackground(for: .widget) {
            Color(.systemBackground)
        }
    }
    
    private var mediumBalanceView: some View {
        HStack(spacing: 16) {
            // Left side - Balance
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: "chart.pie.fill")
                        .foregroundColor(.enlikoPrimary)
                    Text("Portfolio")
                        .font(.caption.bold())
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Text("$\(entry.balance.totalEquity.formattedWidget)")
                    .font(.system(size: 28, weight: .bold, design: .rounded))
                
                HStack(spacing: 4) {
                    Image(systemName: entry.balance.todayPnL >= 0 ? "arrow.up.right" : "arrow.down.right")
                    Text(String(format: "%+.2f%%", entry.balance.todayPnLPercent))
                }
                .font(.subheadline.bold())
                .foregroundColor(entry.balance.todayPnL >= 0 ? .green : .red)
            }
            
            Divider()
            
            // Right side - Stats
            VStack(alignment: .leading, spacing: 12) {
                statRow(title: "Today", value: String(format: "%+.2f", entry.balance.todayPnL), isPositive: entry.balance.todayPnL >= 0)
                statRow(title: "Unrealized", value: String(format: "%+.2f", entry.balance.unrealizedPnL), isPositive: entry.balance.unrealizedPnL >= 0)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding()
        .containerBackground(for: .widget) {
            Color(.systemBackground)
        }
    }
    
    private func statRow(title: String, value: String, isPositive: Bool) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
            Text(value)
                .font(.subheadline.bold())
                .foregroundColor(isPositive ? .green : .red)
        }
    }
}

// MARK: - Price Widget Timeline Provider

struct PriceProvider: TimelineProvider {
    func placeholder(in context: Context) -> PriceEntry {
        PriceEntry(date: Date(), prices: samplePrices)
    }
    
    func getSnapshot(in context: Context, completion: @escaping (PriceEntry) -> Void) {
        let prices = WidgetDataManager.shared.getPrices()
        let entry = PriceEntry(date: Date(), prices: prices.isEmpty ? samplePrices : prices)
        completion(entry)
    }
    
    func getTimeline(in context: Context, completion: @escaping (Timeline<PriceEntry>) -> Void) {
        let currentDate = Date()
        let refreshDate = Calendar.current.date(byAdding: .minute, value: 5, to: currentDate)!
        
        let prices = WidgetDataManager.shared.getPrices()
        let entry = PriceEntry(date: currentDate, prices: prices.isEmpty ? samplePrices : prices)
        
        let timeline = Timeline(entries: [entry], policy: .after(refreshDate))
        completion(timeline)
    }
    
    private var samplePrices: [WidgetPrice] {
        [
            WidgetPrice(symbol: "BTC", price: 45234.50, change24h: 2.34, lastUpdated: Date()),
            WidgetPrice(symbol: "ETH", price: 2456.78, change24h: -1.23, lastUpdated: Date()),
            WidgetPrice(symbol: "SOL", price: 98.76, change24h: 5.67, lastUpdated: Date())
        ]
    }
}

struct PriceEntry: TimelineEntry {
    let date: Date
    let prices: [WidgetPrice]
}

// MARK: - Price Widget View

struct PriceWidgetView: View {
    @Environment(\.widgetFamily) var family
    let entry: PriceEntry
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Image(systemName: "bitcoinsign.circle.fill")
                    .foregroundColor(.orange)
                Text("Crypto Prices")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                Spacer()
            }
            
            Spacer()
            
            // Prices
            ForEach(entry.prices.prefix(3), id: \.symbol) { price in
                priceRow(price)
            }
        }
        .padding()
        .containerBackground(for: .widget) {
            Color(.systemBackground)
        }
    }
    
    private func priceRow(_ price: WidgetPrice) -> some View {
        HStack {
            Text(price.symbol)
                .font(.caption.bold())
                .frame(width: 35, alignment: .leading)
            
            Text("$\(price.price.formattedWidget)")
                .font(.caption)
                .foregroundColor(.primary)
            
            Spacer()
            
            HStack(spacing: 2) {
                Image(systemName: price.change24h >= 0 ? "arrow.up.right" : "arrow.down.right")
                    .font(.caption2)
                Text(String(format: "%+.1f%%", price.change24h))
                    .font(.caption2.bold())
            }
            .foregroundColor(price.change24h >= 0 ? .green : .red)
        }
    }
}

// MARK: - Position Widget Timeline Provider

struct PositionProvider: TimelineProvider {
    func placeholder(in context: Context) -> PositionEntry {
        PositionEntry(date: Date(), positions: samplePositions)
    }
    
    func getSnapshot(in context: Context, completion: @escaping (PositionEntry) -> Void) {
        let positions = WidgetDataManager.shared.getPositions()
        let entry = PositionEntry(date: Date(), positions: positions.isEmpty ? samplePositions : positions)
        completion(entry)
    }
    
    func getTimeline(in context: Context, completion: @escaping (Timeline<PositionEntry>) -> Void) {
        let currentDate = Date()
        let refreshDate = Calendar.current.date(byAdding: .minute, value: 5, to: currentDate)!
        
        let positions = WidgetDataManager.shared.getPositions()
        let entry = PositionEntry(date: currentDate, positions: positions.isEmpty ? samplePositions : positions)
        
        let timeline = Timeline(entries: [entry], policy: .after(refreshDate))
        completion(timeline)
    }
    
    private var samplePositions: [WidgetPosition] {
        [
            WidgetPosition(symbol: "BTCUSDT", side: "Long", pnl: 123.45, pnlPercent: 2.34),
            WidgetPosition(symbol: "ETHUSDT", side: "Short", pnl: -45.67, pnlPercent: -1.23)
        ]
    }
}

struct PositionEntry: TimelineEntry {
    let date: Date
    let positions: [WidgetPosition]
}

// MARK: - Position Widget View

struct PositionWidgetView: View {
    let entry: PositionEntry
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Image(systemName: "list.bullet.rectangle.fill")
                    .foregroundColor(.enlikoPrimary)
                Text("Positions")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                Spacer()
                Text("\(entry.positions.count)")
                    .font(.caption.bold())
                    .foregroundColor(.enlikoPrimary)
            }
            
            Spacer()
            
            if entry.positions.isEmpty {
                Text("No open positions")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
            } else {
                ForEach(entry.positions.prefix(3), id: \.symbol) { position in
                    positionRow(position)
                }
            }
        }
        .padding()
        .containerBackground(for: .widget) {
            Color(.systemBackground)
        }
    }
    
    private func positionRow(_ position: WidgetPosition) -> some View {
        HStack {
            Circle()
                .fill(position.side == "Long" ? Color.green : Color.red)
                .frame(width: 6, height: 6)
            
            Text(position.symbol.replacingOccurrences(of: "USDT", with: ""))
                .font(.caption.bold())
            
            Spacer()
            
            Text(String(format: "%+.2f", position.pnl))
                .font(.caption.bold())
                .foregroundColor(position.pnl >= 0 ? .green : .red)
        }
    }
}

// MARK: - Double Extension for Widget Formatting

extension Double {
    var formattedWidget: String {
        if abs(self) >= 1000 {
            return String(format: "%.0f", self)
        } else if abs(self) >= 1 {
            return String(format: "%.2f", self)
        } else {
            return String(format: "%.4f", self)
        }
    }
}

// MARK: - Widget Color Extension
// Note: When building a separate Widget Extension target, you'll need to duplicate
// the color definitions from Color+Extensions.swift into the widget target,
// as app extensions cannot access main app code.
// For the main app, we use the colors from Color+Extensions.swift

// MARK: - Widget Definitions

// Note: These would go in a WidgetExtension target
// Just showing the structure here for reference

/*
@main
struct EnlikoWidgets: WidgetBundle {
    var body: some Widget {
        BalanceWidget()
        PriceWidget()
        PositionWidget()
    }
}

struct BalanceWidget: Widget {
    let kind: String = "BalanceWidget"
    
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: BalanceProvider()) { entry in
            BalanceWidgetView(entry: entry)
        }
        .configurationDisplayName("Portfolio Balance")
        .description("View your account balance at a glance.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

struct PriceWidget: Widget {
    let kind: String = "PriceWidget"
    
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: PriceProvider()) { entry in
            PriceWidgetView(entry: entry)
        }
        .configurationDisplayName("Crypto Prices")
        .description("Track live cryptocurrency prices.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

struct PositionWidget: Widget {
    let kind: String = "PositionWidget"
    
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: PositionProvider()) { entry in
            PositionWidgetView(entry: entry)
        }
        .configurationDisplayName("Open Positions")
        .description("Monitor your active trades.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
*/

// MARK: - Preview
// Note: Widget previews require actual Widget implementation in extension target
/*
#Preview("Balance Small", as: .systemSmall) {
    // BalanceWidget()
} timeline: {
    BalanceEntry(date: Date(), balance: WidgetBalance(
        totalEquity: 10234.56,
        unrealizedPnL: 123.45,
        todayPnL: 234.56,
        todayPnLPercent: 2.34,
        lastUpdated: Date()
    ))
}
*/
