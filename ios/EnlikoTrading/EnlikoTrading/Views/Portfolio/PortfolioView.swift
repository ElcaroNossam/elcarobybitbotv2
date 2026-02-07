//
//  PortfolioView.swift
//  EnlikoTrading
//
//  Portfolio overview with Spot/Futures balance, period filters,
//  interactive PnL charts with cluster analysis
//

import SwiftUI
import Charts

// MARK: - Period Filter Enum
enum PeriodFilter: String, CaseIterable {
    case day = "1d"
    case week = "1w"
    case month = "1m"
    case quarter = "3m"
    case year = "1y"
    case custom = "custom"
    
    var displayName: String {
        switch self {
        case .day: return "1D"
        case .week: return "1W"
        case .month: return "1M"
        case .quarter: return "3M"
        case .year: return "1Y"
        case .custom: return "📅"
        }
    }
}

// MARK: - Portfolio Tab
enum PortfolioTab: String, CaseIterable {
    case overview
    case spot
    case futures
    
    var displayName: String {
        switch self {
        case .overview: return "portfolio_overview".localized
        case .spot: return "portfolio_spot".localized
        case .futures: return "portfolio_futures".localized
        }
    }
    
    var icon: String {
        switch self {
        case .overview: return "chart.pie.fill"
        case .spot: return "bitcoinsign.circle.fill"
        case .futures: return "chart.line.uptrend.xyaxis"
        }
    }
}

// MARK: - Portfolio Data Models
struct PortfolioSummary: Codable {
    let spot: PortfolioSpotData?
    let futures: PortfolioFuturesData?
    let totalUsd: Double
    let pnlPeriod: Double
    let pnlPeriodPct: Double
    let period: String
    let chartData: [PnLDataPoint]
    let candles: [CandleCluster]
    
    enum CodingKeys: String, CodingKey {
        case spot, futures, period
        case totalUsd = "total_usd"
        case pnlPeriod = "pnl_period"
        case pnlPeriodPct = "pnl_period_pct"
        case chartData = "chart_data"
        case candles
    }
}

struct PortfolioSpotData: Codable {
    let totalUsd: Double
    let pnl: Double
    let pnlPct: Double
    let assets: [AssetBalance]
    
    enum CodingKeys: String, CodingKey {
        case pnl, assets
        case totalUsd = "total_usd"
        case pnlPct = "pnl_pct"
    }
}

struct PortfolioFuturesData: Codable {
    let totalEquity: Double
    let available: Double
    let positionMargin: Double
    let unrealizedPnl: Double
    let realizedPnl: Double
    let positionCount: Int
    
    enum CodingKeys: String, CodingKey {
        case available
        case totalEquity = "total_equity"
        case positionMargin = "position_margin"
        case unrealizedPnl = "unrealized_pnl"
        case realizedPnl = "realized_pnl"
        case positionCount = "position_count"
    }
}

struct AssetBalance: Codable, Identifiable {
    var id: String { asset }
    let asset: String
    let free: Double
    let locked: Double
    let total: Double
    let usdValue: Double
    let pnl24h: Double
    let pnl24hPct: Double
    
    enum CodingKeys: String, CodingKey {
        case asset, free, locked, total
        case usdValue = "usd_value"
        case pnl24h = "pnl_24h"
        case pnl24hPct = "pnl_24h_pct"
    }
}

struct PnLDataPoint: Codable, Identifiable {
    var id: String { timestamp }
    let timestamp: String
    let pnl: Double
    let cumulativePnl: Double
    let tradeCount: Int
    
    enum CodingKeys: String, CodingKey {
        case timestamp, pnl
        case cumulativePnl = "cumulative_pnl"
        case tradeCount = "trade_count"
    }
}

struct CandleCluster: Codable, Identifiable {
    var id: String { timestamp }
    let timestamp: String
    let openPnl: Double
    let highPnl: Double
    let lowPnl: Double
    let closePnl: Double
    let volume: Double
    let tradeCount: Int
    let longCount: Int
    let shortCount: Int
    let longPnl: Double
    let shortPnl: Double
    let winCount: Int
    let lossCount: Int
    let avgWin: Double
    let avgLoss: Double
    let strategies: [String: StrategyCluster]
    let symbols: [String: SymbolCluster]
    let trades: [ClusterTrade]
    
    enum CodingKeys: String, CodingKey {
        case timestamp, volume, strategies, symbols, trades
        case openPnl = "open_pnl"
        case highPnl = "high_pnl"
        case lowPnl = "low_pnl"
        case closePnl = "close_pnl"
        case tradeCount = "trade_count"
        case longCount = "long_count"
        case shortCount = "short_count"
        case longPnl = "long_pnl"
        case shortPnl = "short_pnl"
        case winCount = "win_count"
        case lossCount = "loss_count"
        case avgWin = "avg_win"
        case avgLoss = "avg_loss"
    }
}

struct StrategyCluster: Codable {
    let count: Int
    let pnl: Double
    let winRate: Double?
    
    enum CodingKeys: String, CodingKey {
        case count, pnl
        case winRate = "win_rate"
    }
}

struct SymbolCluster: Codable {
    let count: Int
    let pnl: Double
}

struct ClusterTrade: Codable, Identifiable {
    let id: Int?
    let symbol: String
    let side: String
    let pnl: Double
    let pnlPct: Double
    let strategy: String?
    let exitReason: String?
    let ts: String
    
    enum CodingKeys: String, CodingKey {
        case id, symbol, side, pnl, strategy, ts
        case pnlPct = "pnl_pct"
        case exitReason = "exit_reason"
    }
}

// MARK: - Portfolio View
struct PortfolioView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var selectedTab: PortfolioTab = .overview
    @State private var selectedPeriod: PeriodFilter = .week
    @State private var portfolioData: PortfolioSummary?
    @State private var isLoading = false
    @State private var selectedCandle: CandleCluster?
    @State private var showCandleDetail = false
    @State private var showCustomDatePicker = false
    @State private var customStartDate = Date().addingTimeInterval(-7 * 24 * 3600)
    @State private var customEndDate = Date()
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        accountSelector
                        portfolioTabsView
                        periodFilterView
                        
                        switch selectedTab {
                        case .overview:
                            overviewContent
                        case .spot:
                            spotContent
                        case .futures:
                            futuresContent
                        }
                        
                        pnlChartWithClusters
                        recentTradesSection
                    }
                    .padding()
                    .padding(.bottom, 100)
                }
                .refreshable {
                    await loadPortfolioData()
                }
            }
            .navigationTitle("portfolio_title".localized)
            .withRTLSupport()
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { Task { await loadPortfolioData() } }) {
                        if isLoading {
                            ProgressView().scaleEffect(0.8)
                        } else {
                            Image(systemName: "arrow.clockwise").foregroundColor(.enlikoPrimary)
                        }
                    }
                }
            }
            .onChange(of: appState.currentExchange) { _, _ in Task { await loadPortfolioData() } }
            .onChange(of: appState.currentAccountType) { _, _ in Task { await loadPortfolioData() } }
            .onChange(of: selectedPeriod) { _, newValue in
                if newValue == .custom { showCustomDatePicker = true }
                else { Task { await loadPortfolioData() } }
            }
            .task { await loadPortfolioData() }
            .sheet(isPresented: $showCandleDetail) {
                if let candle = selectedCandle { CandleClusterDetailView(candle: candle) }
            }
            .sheet(isPresented: $showCustomDatePicker) {
                CustomDatePickerSheet(startDate: $customStartDate, endDate: $customEndDate, onConfirm: {
                    showCustomDatePicker = false
                    Task { await loadPortfolioData() }
                })
            }
        }
    }
    
    private func loadPortfolioData() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            var params = ["period": selectedPeriod.rawValue, "account_type": appState.currentAccountType.rawValue, "exchange": appState.currentExchange.rawValue]
            if selectedPeriod == .custom {
                let formatter = ISO8601DateFormatter()
                params["custom_start"] = formatter.string(from: customStartDate)
                params["custom_end"] = formatter.string(from: customEndDate)
            }
            let queryString = params.map { "\($0.key)=\($0.value)" }.joined(separator: "&")
            portfolioData = try await NetworkService.shared.get("/portfolio/summary?\(queryString)")
            await tradingService.refreshAll()
        } catch {
            AppLogger.shared.error("Failed to load portfolio: \(error)", category: .network)
        }
    }
    
    private var accountSelector: some View {
        HStack(spacing: 12) {
            Menu {
                ForEach(Exchange.allCases, id: \.self) { exchange in
                    Button(action: { appState.switchExchange(to: exchange) }) {
                        HStack {
                            Text(exchange.displayName)
                            if appState.selectedExchange == exchange { Image(systemName: "checkmark") }
                        }
                    }
                }
            } label: {
                HStack {
                    Image(systemName: appState.selectedExchange == .bybit ? "b.circle.fill" : "h.circle.fill")
                    Text(appState.selectedExchange.displayName)
                    Image(systemName: "chevron.down")
                }
                .font(.subheadline.weight(.medium))
                .padding(.horizontal, 16).padding(.vertical, 10)
                .background(Color.enlikoCard).cornerRadius(10)
            }
            
            Picker("Account", selection: Binding(get: { appState.selectedAccountType }, set: { appState.switchAccountType(to: $0) })) {
                ForEach(appState.selectedExchange.accountTypes, id: \.self) { type in Text(type.displayName).tag(type) }
            }.pickerStyle(.segmented)
            
            Text(appState.selectedAccountType.icon).font(.title2)
        }
    }
    
    private var portfolioTabsView: some View {
        HStack(spacing: 0) {
            ForEach(PortfolioTab.allCases, id: \.self) { tab in
                Button(action: { withAnimation(.spring(response: 0.3)) { selectedTab = tab } }) {
                    VStack(spacing: 6) {
                        Image(systemName: tab.icon).font(.title3)
                        Text(tab.displayName).font(.caption.weight(.medium))
                    }
                    .foregroundColor(selectedTab == tab ? .enlikoPrimary : .enlikoTextSecondary)
                    .frame(maxWidth: .infinity).padding(.vertical, 12)
                    .background(selectedTab == tab ? Color.enlikoPrimary.opacity(0.15) : Color.clear)
                }
            }
        }.background(Color.enlikoCard).cornerRadius(12)
    }
    
    private var periodFilterView: some View {
        HStack(spacing: 8) {
            ForEach(PeriodFilter.allCases, id: \.self) { period in
                Button(action: { selectedPeriod = period }) {
                    Text(period.displayName)
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(selectedPeriod == period ? .white : .enlikoTextSecondary)
                        .padding(.horizontal, 16).padding(.vertical, 8)
                        .background(selectedPeriod == period ? Color.enlikoPrimary : Color.enlikoCard)
                        .cornerRadius(8)
                }
            }
        }.frame(maxWidth: .infinity, alignment: .leading)
    }
    
    private var overviewContent: some View {
        VStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text("portfolio_total_balance".localized).font(.subheadline).foregroundColor(.enlikoTextSecondary)
                    Spacer()
                    if isLoading { ProgressView().scaleEffect(0.8) }
                }
                Text("$\(portfolioData?.totalUsd.formattedPrice ?? "0.00")")
                    .font(.system(size: 36, weight: .bold, design: .rounded)).foregroundColor(.white)
                
                HStack(spacing: 8) {
                    let pnl = portfolioData?.pnlPeriod ?? 0
                    let pnlPct = portfolioData?.pnlPeriodPct ?? 0
                    Text("\(selectedPeriod.displayName) PnL:").font(.subheadline).foregroundColor(.enlikoTextSecondary)
                    Text(pnl.formattedCurrency).font(.headline.weight(.semibold)).foregroundColor(pnl >= 0 ? .enlikoGreen : .enlikoRed)
                    Text("(\(pnlPct >= 0 ? "+" : "")\(String(format: "%.2f", pnlPct))%)")
                        .font(.subheadline).foregroundColor(pnlPct >= 0 ? .enlikoGreen : .enlikoRed)
                }
            }
            .padding(20).frame(maxWidth: .infinity, alignment: .leading)
            .background(LinearGradient(colors: [Color.enlikoCard, Color.enlikoCard.opacity(0.8)], startPoint: .topLeading, endPoint: .bottomTrailing))
            .cornerRadius(16).overlay(RoundedRectangle(cornerRadius: 16).stroke(Color.enlikoPrimary.opacity(0.3), lineWidth: 1))
            
            // HyperLiquid Spot Balance section
            if appState.currentExchange == .hyperliquid, let spotBalance = tradingService.hlSpotBalance, spotBalance.hasBalance {
                hlSpotBalanceCard(spotBalance)
            }
            
            quickStatsGrid
        }
    }
    
    private var spotContent: some View {
        VStack(spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("portfolio_spot_balance".localized).font(.subheadline).foregroundColor(.enlikoTextSecondary)
                    Text("$\(portfolioData?.spot?.totalUsd.formattedPrice ?? "0.00")").font(.title.bold()).foregroundColor(.white)
                }
                Spacer()
                Image(systemName: "bitcoinsign.circle.fill").font(.largeTitle).foregroundColor(.enlikoYellow)
            }.padding().enlikoCard()
            
            if let assets = portfolioData?.spot?.assets, !assets.isEmpty {
                VStack(spacing: 0) {
                    ForEach(assets) { asset in
                        AssetRowView(asset: asset)
                        if asset.id != assets.last?.id { Divider().background(Color.enlikoBorder) }
                    }
                }.enlikoCard()
            } else { emptyStateView(message: "portfolio_no_spot_assets".localized) }
        }
    }
    
    private var futuresContent: some View {
        VStack(spacing: 16) {
            if let futures = portfolioData?.futures {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Text("portfolio_futures_equity".localized).font(.subheadline).foregroundColor(.enlikoTextSecondary)
                        Spacer()
                        Text("\(futures.positionCount) " + "portfolio_positions".localized).font(.caption).foregroundColor(.enlikoPrimary)
                    }
                    Text("$\(futures.totalEquity.formattedPrice)").font(.system(size: 32, weight: .bold, design: .rounded)).foregroundColor(.white)
                    HStack(spacing: 24) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("portfolio_available".localized).font(.caption).foregroundColor(.enlikoTextSecondary)
                            Text("$\(futures.available.formattedPrice)").font(.headline).foregroundColor(.enlikoGreen)
                        }
                        VStack(alignment: .leading, spacing: 4) {
                            Text("portfolio_margin".localized).font(.caption).foregroundColor(.enlikoTextSecondary)
                            Text("$\(futures.positionMargin.formattedPrice)").font(.headline).foregroundColor(.enlikoYellow)
                        }
                        VStack(alignment: .leading, spacing: 4) {
                            Text("portfolio_unrealized".localized).font(.caption).foregroundColor(.enlikoTextSecondary)
                            Text(futures.unrealizedPnl.formattedCurrency).font(.headline).foregroundColor(futures.unrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
                        }
                    }
                }.padding(20).frame(maxWidth: .infinity, alignment: .leading).background(Color.enlikoCard).cornerRadius(16)
            }
            
            if !tradingService.positions.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    Text("portfolio_open_positions".localized).font(.headline).foregroundColor(.white)
                    ForEach(tradingService.positions.prefix(5)) { position in PositionRowView(position: position) }
                    if tradingService.positions.count > 5 {
                        NavigationLink("common_view_all".localized) { PositionsView() }.font(.subheadline).foregroundColor(.enlikoPrimary)
                    }
                }.padding().enlikoCard()
            }
        }
    }
    
    private var pnlChartWithClusters: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("portfolio_pnl_chart".localized).font(.headline).foregroundColor(.white)
                Spacer()
                if let data = portfolioData { Text("\(data.candles.count) " + "portfolio_candles".localized).font(.caption).foregroundColor(.enlikoTextSecondary) }
            }
            
            if let candles = portfolioData?.candles, !candles.isEmpty {
                Chart {
                    ForEach(candles) { candle in
                        RectangleMark(x: .value("Time", candle.timestamp), yStart: .value("Open", candle.openPnl), yEnd: .value("Close", candle.closePnl), width: 12)
                            .foregroundStyle(candle.closePnl >= candle.openPnl ? Color.enlikoGreen : Color.enlikoRed)
                            .opacity(selectedCandle?.id == candle.id ? 1 : 0.8)
                        RuleMark(x: .value("Time", candle.timestamp), yStart: .value("Low", candle.lowPnl), yEnd: .value("High", candle.highPnl))
                            .foregroundStyle(candle.closePnl >= candle.openPnl ? Color.enlikoGreen : Color.enlikoRed)
                    }
                }
                .frame(height: 200)
                .chartYAxis { AxisMarks(position: .leading) { value in
                    AxisGridLine().foregroundStyle(Color.enlikoBorder)
                    AxisValueLabel { if let pnl = value.as(Double.self) { Text("$\(Int(pnl))").font(.caption2).foregroundColor(.enlikoTextSecondary) } }
                }}
                .chartXAxis { AxisMarks { _ in AxisGridLine().foregroundStyle(Color.enlikoBorder.opacity(0.5)) }}
                .chartOverlay { proxy in
                    GeometryReader { geometry in
                        Rectangle().fill(Color.clear).contentShape(Rectangle())
                            .gesture(SpatialTapGesture().onEnded { value in handleChartTap(at: value.location, proxy: proxy, geometry: geometry, candles: candles) })
                    }
                }
                Text("💡 " + "portfolio_tap_candle_hint".localized).font(.caption).foregroundColor(.enlikoTextMuted)
            } else {
                RoundedRectangle(cornerRadius: 8).fill(Color.enlikoSurface).frame(height: 200)
                    .overlay(VStack(spacing: 8) { Image(systemName: "chart.bar.xaxis").font(.largeTitle).foregroundColor(.enlikoTextMuted); Text("portfolio_no_chart_data".localized).foregroundColor(.enlikoTextMuted) })
            }
        }.padding(16).enlikoCard()
    }
    
    private func handleChartTap(at location: CGPoint, proxy: ChartProxy, geometry: GeometryProxy, candles: [CandleCluster]) {
        guard !candles.isEmpty else { return }
        let plotFrame = geometry.frame(in: .local)
        let xPosition = location.x - plotFrame.minX
        let candleWidth = plotFrame.width / CGFloat(candles.count)
        let index = Int(xPosition / candleWidth)
        if index >= 0 && index < candles.count {
            selectedCandle = candles[index]
            showCandleDetail = true
            HapticFeedback.selection()
        }
    }
    
    // MARK: - HyperLiquid Spot Balance Card
    private func hlSpotBalanceCard(_ spotBalance: HLSpotBalance) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "cart.fill").foregroundColor(.enlikoYellow)
                Text("🛒 Spot Balance").font(.headline).foregroundColor(.white)
                Spacer()
                Text("$\(String(format: "%.2f", spotBalance.totalUsdValue))").font(.title2.bold()).foregroundColor(.enlikoYellow)
            }
            
            Divider().background(Color.enlikoBorder)
            
            ForEach(spotBalance.tokens.prefix(5)) { token in
                HStack {
                    Text(token.token).font(.subheadline.weight(.medium)).foregroundColor(.white)
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {
                        Text(String(format: "%.4f", token.total)).font(.subheadline).foregroundColor(.enlikoTextSecondary)
                        Text("$\(String(format: "%.2f", token.usdValue))").font(.caption).foregroundColor(.enlikoTextMuted)
                    }
                }
            }
            
            // Warning if Perp balance is 0 but Spot has money
            if tradingService.balance?.equity ?? 0 == 0 && spotBalance.totalUsdValue > 0 {
                HStack(spacing: 8) {
                    Image(systemName: "exclamationmark.triangle.fill").foregroundColor(.enlikoOrange)
                    Text("Funds on Spot! Transfer to Perp to trade.").font(.caption).foregroundColor(.enlikoOrange)
                }.padding(.top, 4)
            }
        }
        .padding(16)
        .background(
            LinearGradient(colors: [Color.enlikoCard, Color.enlikoCard.opacity(0.8)], startPoint: .topLeading, endPoint: .bottomTrailing)
        )
        .cornerRadius(16)
        .overlay(RoundedRectangle(cornerRadius: 16).stroke(Color.enlikoYellow.opacity(0.3), lineWidth: 1))
    }
    
    private var quickStatsGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            if let stats = tradingService.tradingStats {
                PortfolioStatCard(title: "stats_total_trades".localized, value: "\(stats.totalTradesCount)", icon: "chart.bar.fill", color: .enlikoBlue)
                PortfolioStatCard(title: "stats_win_rate".localized, value: String(format: "%.1f%%", stats.winRateValue), icon: "target", color: stats.winRateValue >= 50 ? .enlikoGreen : .enlikoRed)
                PortfolioStatCard(title: "stats_total_pnl".localized, value: (stats.totalPnl ?? 0).formattedCurrency, icon: "dollarsign.circle.fill", color: (stats.totalPnl ?? 0) >= 0 ? .enlikoGreen : .enlikoRed)
                PortfolioStatCard(title: "stats_avg_trade".localized, value: (stats.avgPnl ?? 0).formattedCurrency, icon: "chart.line.uptrend.xyaxis", color: (stats.avgPnl ?? 0) >= 0 ? .enlikoGreen : .enlikoRed)
            } else { ForEach(0..<4, id: \.self) { _ in PortfolioStatCard(title: "--", value: "--", icon: "chart.bar.fill", color: .enlikoTextMuted) }}
        }
    }
    
    private var recentTradesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("portfolio_recent_trades".localized).font(.headline).foregroundColor(.white)
                Spacer()
                NavigationLink("common_all".localized) { TradeHistoryView() }.font(.subheadline).foregroundColor(.enlikoPrimary)
            }
            if tradingService.trades.isEmpty { emptyStateView(message: "portfolio_no_recent_trades".localized) }
            else { ForEach(tradingService.trades.prefix(5)) { trade in TradeRow(trade: trade) } }
        }.padding(16).enlikoCard()
    }
    
    private func emptyStateView(message: String) -> some View {
        HStack { Spacer(); VStack(spacing: 8) { Image(systemName: "doc.text.magnifyingglass").font(.largeTitle).foregroundColor(.enlikoTextMuted); Text(message).foregroundColor(.enlikoTextSecondary) }.padding(.vertical, 24); Spacer() }
    }
}

struct AssetRowView: View {
    let asset: AssetBalance
    var body: some View {
        HStack {
            Circle().fill(Color.enlikoPrimary.opacity(0.2)).frame(width: 40, height: 40)
                .overlay(Text(String(asset.asset.prefix(1))).font(.headline.bold()).foregroundColor(.enlikoPrimary))
            VStack(alignment: .leading, spacing: 2) {
                Text(asset.asset).font(.headline).foregroundColor(.white)
                Text("\(asset.total.formattedPrice) \(asset.asset)").font(.caption).foregroundColor(.enlikoTextSecondary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 2) {
                Text("$\(asset.usdValue.formattedPrice)").font(.headline).foregroundColor(.white)
                if asset.pnl24h != 0 { Text(asset.pnl24h.formattedCurrency).font(.caption).foregroundColor(asset.pnl24h >= 0 ? .enlikoGreen : .enlikoRed) }
            }
        }.padding()
    }
}

struct PositionRowView: View {
    let position: Position
    var body: some View {
        HStack {
            Circle().fill(position.side.lowercased() == "buy" ? Color.enlikoGreen : Color.enlikoRed).frame(width: 8, height: 8)
            VStack(alignment: .leading, spacing: 2) {
                Text(position.symbol).font(.subheadline.weight(.medium)).foregroundColor(.white)
                Text("\(position.leverage ?? 1)x • \(position.side)").font(.caption).foregroundColor(.enlikoTextSecondary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 2) {
                Text("$\(position.positionValue.formattedPrice)").font(.subheadline).foregroundColor(.white)
                Text(position.unrealizedPnl.formattedCurrency).font(.caption).foregroundColor(position.unrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
            }
        }.padding(.vertical, 8)
    }
}

struct CandleClusterDetailView: View {
    let candle: CandleCluster
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) { summaryCard; directionBreakdown; strategyBreakdown; symbolBreakdown; tradesListSection }.padding()
            }
            .background(Color.enlikoBackground)
            .navigationTitle("cluster_analysis".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .topBarTrailing) { Button("common_close".localized) { dismiss() } } }
        }
    }
    
    private var summaryCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("cluster_summary".localized).font(.headline).foregroundColor(.white)
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                ClusterStatItem(title: "cluster_trades".localized, value: "\(candle.tradeCount)")
                ClusterStatItem(title: "cluster_pnl".localized, value: (candle.closePnl - candle.openPnl).formattedCurrency, color: candle.closePnl >= candle.openPnl ? .enlikoGreen : .enlikoRed)
                ClusterStatItem(title: "cluster_win_rate".localized, value: candle.tradeCount > 0 ? String(format: "%.1f%%", Double(candle.winCount) / Double(candle.tradeCount) * 100) : "--")
                ClusterStatItem(title: "cluster_volume".localized, value: "$\(candle.volume.formattedPrice)")
            }
        }.padding().enlikoCard()
    }
    
    private var directionBreakdown: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("cluster_direction".localized).font(.headline).foregroundColor(.white)
            HStack(spacing: 16) {
                VStack(spacing: 8) {
                    HStack { Circle().fill(Color.enlikoGreen).frame(width: 8, height: 8); Text("LONG").font(.subheadline.weight(.medium)).foregroundColor(.enlikoGreen) }
                    Text("\(candle.longCount) trades").font(.caption).foregroundColor(.enlikoTextSecondary)
                    Text(candle.longPnl.formattedCurrency).font(.headline).foregroundColor(candle.longPnl >= 0 ? .enlikoGreen : .enlikoRed)
                }.frame(maxWidth: .infinity).padding().background(Color.enlikoGreen.opacity(0.1)).cornerRadius(12)
                VStack(spacing: 8) {
                    HStack { Circle().fill(Color.enlikoRed).frame(width: 8, height: 8); Text("SHORT").font(.subheadline.weight(.medium)).foregroundColor(.enlikoRed) }
                    Text("\(candle.shortCount) trades").font(.caption).foregroundColor(.enlikoTextSecondary)
                    Text(candle.shortPnl.formattedCurrency).font(.headline).foregroundColor(candle.shortPnl >= 0 ? .enlikoGreen : .enlikoRed)
                }.frame(maxWidth: .infinity).padding().background(Color.enlikoRed.opacity(0.1)).cornerRadius(12)
            }
        }.padding().enlikoCard()
    }
    
    private var strategyBreakdown: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("cluster_strategies".localized).font(.headline).foregroundColor(.white)
            ForEach(Array(candle.strategies.keys.sorted()), id: \.self) { strategy in
                if let data = candle.strategies[strategy] {
                    HStack {
                        Text(strategy.capitalized).font(.subheadline).foregroundColor(.white)
                        Spacer()
                        Text("\(data.count) trades").font(.caption).foregroundColor(.enlikoTextSecondary)
                        Text(data.pnl.formattedCurrency).font(.subheadline.weight(.medium)).foregroundColor(data.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                    }.padding(.vertical, 4)
                }
            }
        }.padding().enlikoCard()
    }
    
    private var symbolBreakdown: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("cluster_symbols".localized).font(.headline).foregroundColor(.white)
            ForEach(Array(candle.symbols.keys.sorted()), id: \.self) { symbol in
                if let data = candle.symbols[symbol] {
                    HStack {
                        Text(symbol).font(.subheadline.weight(.medium)).foregroundColor(.white)
                        Spacer()
                        Text("\(data.count)").font(.caption).foregroundColor(.enlikoTextSecondary)
                        Text(data.pnl.formattedCurrency).font(.subheadline.weight(.medium)).foregroundColor(data.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                    }.padding(.vertical, 4)
                }
            }
        }.padding().enlikoCard()
    }
    
    private var tradesListSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("cluster_all_trades".localized).font(.headline).foregroundColor(.white)
            ForEach(candle.trades) { trade in
                HStack {
                    Circle().fill(trade.side.lowercased() == "buy" ? Color.enlikoGreen : Color.enlikoRed).frame(width: 8, height: 8)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(trade.symbol).font(.subheadline.weight(.medium)).foregroundColor(.white)
                        Text(trade.strategy ?? "manual").font(.caption).foregroundColor(.enlikoTextSecondary)
                    }
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {
                        Text(trade.pnl.formattedCurrency).font(.subheadline.weight(.semibold)).foregroundColor(trade.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                        Text(trade.pnlPct.formattedPercent).font(.caption).foregroundColor(.enlikoTextSecondary)
                    }
                }.padding(.vertical, 4)
            }
        }.padding().enlikoCard()
    }
}

struct ClusterStatItem: View {
    let title: String; let value: String; var color: Color = .white
    var body: some View { VStack(spacing: 4) { Text(title).font(.caption).foregroundColor(.enlikoTextSecondary); Text(value).font(.headline).foregroundColor(color) } }
}

struct CustomDatePickerSheet: View {
    @Binding var startDate: Date; @Binding var endDate: Date; let onConfirm: () -> Void
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("custom_start_date".localized).font(.subheadline).foregroundColor(.enlikoTextSecondary)
                    DatePicker("", selection: $startDate, displayedComponents: .date).datePickerStyle(.graphical).tint(.enlikoPrimary)
                }
                VStack(alignment: .leading, spacing: 8) {
                    Text("custom_end_date".localized).font(.subheadline).foregroundColor(.enlikoTextSecondary)
                    DatePicker("", selection: $endDate, displayedComponents: .date).datePickerStyle(.graphical).tint(.enlikoPrimary)
                }
                Button("common_apply".localized) { onConfirm() }.buttonStyle(.borderedProminent).tint(.enlikoPrimary)
            }.padding().background(Color.enlikoBackground).navigationTitle("custom_period".localized).navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .topBarLeading) { Button("common_cancel".localized) { dismiss() } } }
        }
    }
}

struct PortfolioStatCard: View {
    let title: String; let value: String; let icon: String; let color: Color
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) { Text(title).font(.caption).foregroundColor(.enlikoTextSecondary); Text(value).font(.headline.bold()).foregroundColor(.white) }
            Spacer()
            Image(systemName: icon).font(.title2).foregroundColor(color)
        }.padding(16).enlikoCard()
    }
}

struct TradeRow: View {
    let trade: Trade
    var body: some View {
        HStack {
            Circle().fill(trade.side.lowercased() == "buy" ? Color.enlikoGreen : Color.enlikoRed).frame(width: 8, height: 8)
            VStack(alignment: .leading, spacing: 2) {
                Text(trade.symbol).font(.subheadline.weight(.medium)).foregroundColor(.white)
                Text(trade.exitReason ?? trade.side).font(.caption).foregroundColor(.enlikoTextSecondary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 2) {
                Text(trade.pnl?.formattedCurrency ?? "--").font(.subheadline.weight(.semibold)).foregroundColor((trade.pnl ?? 0) >= 0 ? .enlikoGreen : .enlikoRed)
                if let pnlPct = trade.pnlPct { Text(pnlPct.formattedPercent).font(.caption).foregroundColor(.enlikoTextSecondary) }
            }
        }.padding(.vertical, 8)
    }
}

#Preview {
    PortfolioView().environmentObject(AppState.shared).environmentObject(TradingService.shared).preferredColorScheme(.dark)
}
