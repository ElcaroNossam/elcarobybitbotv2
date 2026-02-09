//
//  TradeHistoryView.swift
//  EnlikoTrading
//
//  Complete Trade History View like Binance/Bybit
//  Features: Orders History, Trades History, Funding History, PnL Analysis
//

import SwiftUI

// MARK: - History Models
struct OrderHistoryItem: Identifiable {
    let id = UUID()
    let symbol: String
    let side: String
    let orderType: String
    let price: Double
    let quantity: Double
    let filledQty: Double
    let status: String
    let createdAt: Date
    let updatedAt: Date
    
    var statusColor: Color {
        switch status.lowercased() {
        case "filled": return .green
        case "cancelled": return .red
        case "partially_filled": return .orange
        case "pending": return .yellow
        default: return .secondary
        }
    }
    
    var formattedStatus: String {
        switch status.lowercased() {
        case "filled": return "Filled"
        case "cancelled": return "Cancelled"
        case "partially_filled": return "Partial"
        case "pending": return "Pending"
        default: return status
        }
    }
}

struct TradeHistoryItem: Identifiable {
    let id = UUID()
    let symbol: String
    let side: String
    let price: Double
    let quantity: Double
    let fee: Double
    let pnl: Double?
    let executedAt: Date
    
    var sideColor: Color {
        side.lowercased() == "buy" ? .green : .red
    }
}

struct FundingHistoryItem: Identifiable {
    let id = UUID()
    let symbol: String
    let fundingRate: Double
    let payment: Double
    let position: Double
    let timestamp: Date
}

struct TradeHistoryFullView: View {
    @ObservedObject var localization = LocalizationManager.shared
    @EnvironmentObject var tradingService: TradingService
    
    @State private var selectedTab: HistoryTab = .orders
    @State private var selectedFilter: HistoryFilter = .all
    @State private var selectedTimeframe: TimeframeFilter = .week
    @State private var showFilters = false
    @State private var searchText = ""
    @State private var isLoading = false
    
    @State private var orders: [OrderHistoryItem] = []
    @State private var trades: [TradeHistoryItem] = []
    @State private var funding: [FundingHistoryItem] = []
    
    enum HistoryTab: String, CaseIterable {
        case orders = "Orders"
        case trades = "Trades"
        case funding = "Funding"
        case pnl = "PnL"
    }
    
    enum HistoryFilter: String, CaseIterable {
        case all = "All"
        case buy = "Buy"
        case sell = "Sell"
        case filled = "Filled"
        case cancelled = "Cancelled"
    }
    
    enum TimeframeFilter: String, CaseIterable {
        case day = "24h"
        case week = "7d"
        case month = "30d"
        case quarter = "3m"
        case all = "All"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab Selector
            tabSelector
            
            // Filters
            filtersBar
            
            // Content
            if isLoading {
                Spacer()
                ProgressView()
                Spacer()
            } else {
                contentView
            }
        }
        .background(Color.enlikoBackground)
        .navigationTitle("History")
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task { await refreshData() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(.enlikoPrimary)
                }
            }
        }
        .task {
            await refreshData()
        }
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 0) {
                ForEach(HistoryTab.allCases, id: \.self) { tab in
                    Button {
                        withAnimation { selectedTab = tab }
                    } label: {
                        VStack(spacing: 6) {
                            Text(tab.rawValue)
                                .font(.subheadline.bold())
                                .foregroundColor(selectedTab == tab ? .white : .secondary)
                                .padding(.horizontal, 16)
                            
                            Rectangle()
                                .fill(selectedTab == tab ? Color.enlikoPrimary : Color.clear)
                                .frame(height: 2)
                        }
                    }
                }
            }
        }
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Filters Bar
    private var filtersBar: some View {
        VStack(spacing: 8) {
            // Search
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)
                
                TextField("Search symbol", text: $searchText)
                    .textFieldStyle(.plain)
                
                if !searchText.isEmpty {
                    Button {
                        searchText = ""
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding(10)
            .background(Color.enlikoSurface)
            .cornerRadius(10)
            
            // Time & Filter
            HStack {
                // Timeframe
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(TimeframeFilter.allCases, id: \.self) { tf in
                            Button {
                                selectedTimeframe = tf
                            } label: {
                                Text(tf.rawValue)
                                    .font(.caption.bold())
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(selectedTimeframe == tf ? Color.enlikoPrimary : Color.enlikoSurface)
                                    .foregroundColor(selectedTimeframe == tf ? .white : .secondary)
                                    .cornerRadius(6)
                            }
                        }
                    }
                }
                
                Spacer()
                
                // Filter menu
                Menu {
                    ForEach(HistoryFilter.allCases, id: \.self) { filter in
                        Button {
                            selectedFilter = filter
                        } label: {
                            HStack {
                                Text(filter.rawValue)
                                if selectedFilter == filter {
                                    Image(systemName: "checkmark")
                                }
                            }
                        }
                    }
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                        Text(selectedFilter.rawValue)
                            .font(.caption)
                    }
                    .foregroundColor(.secondary)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.enlikoSurface)
                    .cornerRadius(6)
                }
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
    
    // MARK: - Content View
    @ViewBuilder
    private var contentView: some View {
        switch selectedTab {
        case .orders:
            ordersListView
        case .trades:
            tradesListView
        case .funding:
            fundingListView
        case .pnl:
            pnlAnalysisView
        }
    }
    
    // MARK: - Orders List
    private var ordersListView: some View {
        Group {
            if filteredOrders.isEmpty {
                emptyStateView(text: "No orders found")
            } else {
                ScrollView {
                    LazyVStack(spacing: 1) {
                        ForEach(filteredOrders) { order in
                            OrderHistoryRow(order: order)
                        }
                    }
                }
            }
        }
    }
    
    private var filteredOrders: [OrderHistoryItem] {
        var result = orders
        
        if !searchText.isEmpty {
            result = result.filter { $0.symbol.lowercased().contains(searchText.lowercased()) }
        }
        
        switch selectedFilter {
        case .buy:
            result = result.filter { $0.side.lowercased() == "buy" }
        case .sell:
            result = result.filter { $0.side.lowercased() == "sell" }
        case .filled:
            result = result.filter { $0.status.lowercased() == "filled" }
        case .cancelled:
            result = result.filter { $0.status.lowercased() == "cancelled" }
        default:
            break
        }
        
        return result
    }
    
    // MARK: - Trades List
    private var tradesListView: some View {
        Group {
            if filteredTrades.isEmpty {
                emptyStateView(text: "No trades found")
            } else {
                ScrollView {
                    LazyVStack(spacing: 1) {
                        ForEach(filteredTrades) { trade in
                            TradeHistoryRow(trade: trade)
                        }
                    }
                }
            }
        }
    }
    
    private var filteredTrades: [TradeHistoryItem] {
        var result = trades
        
        if !searchText.isEmpty {
            result = result.filter { $0.symbol.lowercased().contains(searchText.lowercased()) }
        }
        
        switch selectedFilter {
        case .buy:
            result = result.filter { $0.side.lowercased() == "buy" }
        case .sell:
            result = result.filter { $0.side.lowercased() == "sell" }
        default:
            break
        }
        
        return result
    }
    
    // MARK: - Funding List
    private var fundingListView: some View {
        Group {
            if funding.isEmpty {
                emptyStateView(text: "No funding history")
            } else {
                ScrollView {
                    LazyVStack(spacing: 1) {
                        ForEach(funding) { item in
                            FundingHistoryRow(item: item)
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - PnL Analysis
    private var pnlAnalysisView: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Summary Card (from real stats)
                VStack(spacing: 16) {
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Total PnL")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            let totalPnl = tradingService.tradingStats?.totalPnl ?? 0
                            Text(totalPnl >= 0 ? "+$\(totalPnl, specifier: "%.2f")" : "-$\(abs(totalPnl), specifier: "%.2f")")
                                .font(.title.bold())
                                .foregroundColor(totalPnl >= 0 ? .green : .red)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing) {
                            Text("Win Rate")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            let wr = tradingService.tradingStats?.winRateValue ?? 0
                            Text("\(wr, specifier: "%.1f")%")
                                .font(.title2.bold())
                                .foregroundColor(wr >= 50 ? .green : .red)
                        }
                    }
                    
                    Divider()
                    
                    HStack {
                        let stats = tradingService.tradingStats
                        pnlStatItem(title: "Winning", value: "\(stats?.winningCount ?? 0)", color: .green)
                        Spacer()
                        pnlStatItem(title: "Losing", value: "\(stats?.losingCount ?? 0)", color: .red)
                        Spacer()
                        pnlStatItem(title: "Total", value: "\(stats?.totalTradesCount ?? 0)", color: .enlikoPrimary)
                    }
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                
                // Recent Trades PnL
                VStack(alignment: .leading, spacing: 12) {
                    Text("Recent Trades")
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    if tradingService.trades.isEmpty {
                        Text("No trades to display")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .padding(.vertical, 8)
                    } else {
                        ForEach(tradingService.trades.prefix(10)) { trade in
                            HStack {
                                Text(trade.symbol ?? "???")
                                    .font(.caption.bold())
                                    .foregroundColor(.white)
                                    .frame(width: 80, alignment: .leading)
                                
                                Text(trade.side ?? "—")
                                    .font(.caption2.bold())
                                    .foregroundColor((trade.side ?? "").lowercased() == "buy" ? .green : .red)
                                    .frame(width: 30)
                                
                                Spacer()
                                
                                let pnl = trade.pnl ?? 0
                                Text(pnl >= 0 ? "+$\(pnl, specifier: "%.2f")" : "-$\(abs(pnl), specifier: "%.2f")")
                                    .font(.caption.bold())
                                    .foregroundColor(pnl >= 0 ? .green : .red)
                            }
                            .padding(.vertical, 2)
                        }
                    }
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                
                // Top Performers (from trades)
                VStack(alignment: .leading, spacing: 12) {
                    Text("Top Performers")
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    let bySymbol = Dictionary(grouping: tradingService.trades, by: { $0.symbol ?? "???" })
                    let symbolPnl = bySymbol.map { (symbol: $0.key, pnl: $0.value.reduce(0) { $0 + ($1.pnl ?? 0) }) }
                        .sorted { $0.pnl > $1.pnl }
                    
                    if symbolPnl.isEmpty {
                        Text("No data available")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    } else {
                        ForEach(symbolPnl.prefix(5), id: \.symbol) { item in
                            HStack {
                                Text(item.symbol)
                                    .font(.subheadline.bold())
                                    .foregroundColor(.white)
                                
                                Spacer()
                                
                                Text(item.pnl >= 0 ? "+$\(item.pnl, specifier: "%.2f")" : "-$\(abs(item.pnl), specifier: "%.2f")")
                                    .font(.subheadline.bold())
                                    .foregroundColor(item.pnl >= 0 ? .green : .red)
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
            }
            .padding()
        }
    }
    
    private func pnlStatItem(title: String, value: String, color: Color) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3.bold())
                .foregroundColor(color)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
    
    // MARK: - Empty State
    private func emptyStateView(text: String) -> some View {
        VStack(spacing: 16) {
            Spacer()
            
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 50))
                .foregroundColor(.secondary.opacity(0.5))
            
            Text(text)
                .font(.headline)
                .foregroundColor(.secondary)
            
            Spacer()
        }
    }
    
    // MARK: - Date Parser
    private func parseDate(_ str: String?) -> Date {
        guard let str = str, !str.isEmpty else { return Date() }
        let formatters: [DateFormatter] = {
            let iso = DateFormatter()
            iso.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
            iso.locale = Locale(identifier: "en_US_POSIX")
            let iso2 = DateFormatter()
            iso2.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
            iso2.locale = Locale(identifier: "en_US_POSIX")
            let simple = DateFormatter()
            simple.dateFormat = "yyyy-MM-dd HH:mm:ss"
            simple.locale = Locale(identifier: "en_US_POSIX")
            return [iso, iso2, simple]
        }()
        for fmt in formatters {
            if let d = fmt.date(from: str) { return d }
        }
        // Try epoch seconds
        if let epoch = Double(str) {
            return Date(timeIntervalSince1970: epoch > 1e12 ? epoch / 1000 : epoch)
        }
        return Date()
    }
    
    // MARK: - Refresh
    private func refreshData() async {
        isLoading = true
        
        // Fetch real data from API via TradingService
        await tradingService.fetchOrders()
        await tradingService.fetchTrades()
        await tradingService.fetchStats()
        
        await MainActor.run {
            // Map Order model → OrderHistoryItem
            orders = tradingService.orders.map { order in
                OrderHistoryItem(
                    symbol: order.symbol,
                    side: order.side,
                    orderType: order.orderType,
                    price: order.price ?? 0,
                    quantity: order.qty,
                    filledQty: order.status?.lowercased() == "filled" ? order.qty : 0,
                    status: order.status ?? "Unknown",
                    createdAt: parseDate(order.createdAt),
                    updatedAt: parseDate(order.createdAt)
                )
            }
            
            // Map Trade model → TradeHistoryItem
            trades = tradingService.trades.map { trade in
                TradeHistoryItem(
                    symbol: trade.symbol,
                    side: trade.side,
                    price: trade.entryPrice,
                    quantity: 0,
                    fee: 0,
                    pnl: trade.pnl,
                    executedAt: parseDate(trade.timestamp)
                )
            }
            
            // Funding: not available via current API — show empty
            funding = []
            
            isLoading = false
        }
    }
}

// MARK: - Order History Row
struct OrderHistoryRow: View {
    let order: OrderHistoryItem
    
    private let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "MMM d, HH:mm"
        return f
    }()
    
    var body: some View {
        HStack(spacing: 12) {
            // Status indicator
            Circle()
                .fill(order.statusColor)
                .frame(width: 8, height: 8)
            
            VStack(alignment: .leading, spacing: 4) {
                // Symbol & Side
                HStack {
                    Text(order.symbol)
                        .font(.subheadline.bold())
                        .foregroundColor(.white)
                    
                    Text(order.side)
                        .font(.caption.bold())
                        .foregroundColor(order.side.lowercased() == "buy" ? .green : .red)
                    
                    Text("• \(order.orderType)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                // Details
                HStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Price")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text("$\(order.price, specifier: "%.2f")")
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Qty")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text("\(order.filledQty, specifier: "%.4f")/\(order.quantity, specifier: "%.4f")")
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text(order.formattedStatus)
                    .font(.caption.bold())
                    .foregroundColor(order.statusColor)
                
                Text(dateFormatter.string(from: order.createdAt))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
    }
}

// MARK: - Trade History Row
struct TradeHistoryRow: View {
    let trade: TradeHistoryItem
    
    private let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "MMM d, HH:mm:ss"
        return f
    }()
    
    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                // Symbol & Side
                HStack {
                    Text(trade.symbol)
                        .font(.subheadline.bold())
                        .foregroundColor(.white)
                    
                    Text(trade.side.uppercased())
                        .font(.caption.bold())
                        .foregroundColor(trade.sideColor)
                }
                
                // Details
                HStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Price")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text("$\(trade.price, specifier: "%.2f")")
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Qty")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text("\(trade.quantity, specifier: "%.4f")")
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Fee")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text("$\(trade.fee, specifier: "%.4f")")
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                if let pnl = trade.pnl {
                    Text(pnl >= 0 ? "+$\(pnl, specifier: "%.2f")" : "-$\(abs(pnl), specifier: "%.2f")")
                        .font(.subheadline.bold())
                        .foregroundColor(pnl >= 0 ? .green : .red)
                }
                
                Text(dateFormatter.string(from: trade.executedAt))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
    }
}

// MARK: - Funding History Row
struct FundingHistoryRow: View {
    let item: FundingHistoryItem
    
    private let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "MMM d, HH:mm"
        return f
    }()
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(item.symbol)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                
                Text("Rate: \(item.fundingRate * 100, specifier: "%.4f")%")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text(item.payment >= 0 ? "+$\(item.payment, specifier: "%.4f")" : "-$\(abs(item.payment), specifier: "%.4f")")
                    .font(.subheadline.bold())
                    .foregroundColor(item.payment >= 0 ? .green : .red)
                
                Text(dateFormatter.string(from: item.timestamp))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
    }
}

#Preview {
    NavigationStack {
        TradeHistoryFullView()
            .environmentObject(TradingService.shared)
            .preferredColorScheme(.dark)
    }
}
