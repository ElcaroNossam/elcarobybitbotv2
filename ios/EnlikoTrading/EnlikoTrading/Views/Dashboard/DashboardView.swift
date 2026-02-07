//
//  DashboardView.swift
//  EnlikoTrading
//
//  Main Dashboard - like Portfolio/Profile in Telegram bot
//  Shows: Balance, Stats with period filters, Strategy breakdown
//  Exchange/Account switcher at top
//

import SwiftUI
import Combine

// MARK: - Dashboard View (Main Profile Screen)
struct DashboardView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = DashboardViewModel()
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Exchange & Account Switcher
                exchangeAccountSwitcher
                
                // Balance Card
                balanceCard
                
                // Period Filter Pills
                periodFilterSection
                
                // Stats Overview
                statsOverviewSection
                
                // Strategy Breakdown (Cluster Analysis)
                strategyBreakdownSection
                
                // Quick Actions
                quickActionsSection
                
                // Recent Trades
                recentTradesSection
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 100)
        }
        .background(Color.enlikoBackground)
        .navigationTitle("dashboard".localized)
        .navigationBarTitleDisplayMode(.large)
        .refreshable {
            await viewModel.refresh(
                accountType: appState.currentAccountType.rawValue,
                exchange: appState.currentExchange.rawValue
            )
        }
        .onAppear {
            Task {
                await viewModel.refresh(
                    accountType: appState.currentAccountType.rawValue,
                    exchange: appState.currentExchange.rawValue
                )
            }
        }
        .onChange(of: appState.currentExchange) { _, _ in
            Task { await viewModel.refresh(accountType: appState.currentAccountType.rawValue, exchange: appState.currentExchange.rawValue) }
        }
        .onChange(of: appState.currentAccountType) { _, _ in
            Task { await viewModel.refresh(accountType: appState.currentAccountType.rawValue, exchange: appState.currentExchange.rawValue) }
        }
    }
    
    // MARK: - Exchange & Account Switcher
    private var exchangeAccountSwitcher: some View {
        HStack(spacing: 12) {
            // Exchange Picker
            Menu {
                Button {
                    appState.switchExchange(to: .bybit)
                } label: {
                    HStack {
                        Text("🟠 Bybit")
                        if appState.currentExchange == .bybit {
                            Image(systemName: "checkmark")
                        }
                    }
                }
                Button {
                    appState.switchExchange(to: .hyperliquid)
                } label: {
                    HStack {
                        Text("🔷 HyperLiquid")
                        if appState.currentExchange == .hyperliquid {
                            Image(systemName: "checkmark")
                        }
                    }
                }
            } label: {
                HStack(spacing: 6) {
                    Circle()
                        .fill(appState.currentExchange == .bybit ? Color.orange : Color.cyan)
                        .frame(width: 10, height: 10)
                    Text(appState.currentExchange.displayName)
                        .font(.subheadline.bold())
                    Image(systemName: "chevron.down")
                        .font(.caption)
                }
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color.enlikoSurface)
                .cornerRadius(20)
            }
            
            // Account Type Picker
            Menu {
                if appState.currentExchange == .bybit {
                    Button {
                        appState.switchAccountType(to: .demo)
                    } label: {
                        HStack {
                            Text("🎮 Demo")
                            if appState.currentAccountType == .demo {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                    Button {
                        appState.switchAccountType(to: .real)
                    } label: {
                        HStack {
                            Text("💎 Real")
                            if appState.currentAccountType == .real {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                } else {
                    Button {
                        appState.switchAccountType(to: .testnet)
                    } label: {
                        HStack {
                            Text("🧪 Testnet")
                            if appState.currentAccountType == .testnet {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                    Button {
                        appState.switchAccountType(to: .mainnet)
                    } label: {
                        HStack {
                            Text("🌐 Mainnet")
                            if appState.currentAccountType == .mainnet {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                }
            } label: {
                HStack(spacing: 6) {
                    Circle()
                        .fill(accountTypeColor)
                        .frame(width: 10, height: 10)
                    Text(accountTypeLabel)
                        .font(.subheadline.bold())
                    Image(systemName: "chevron.down")
                        .font(.caption)
                }
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color.enlikoSurface)
                .cornerRadius(20)
            }
            
            Spacer()
        }
    }
    
    private var accountTypeLabel: String {
        switch appState.currentAccountType {
        case .demo: return "Demo"
        case .real: return "Real"
        case .testnet: return "Testnet"
        case .mainnet: return "Mainnet"
        }
    }
    
    private var accountTypeColor: Color {
        switch appState.currentAccountType {
        case .demo, .testnet: return .orange
        case .real, .mainnet: return .green
        }
    }
    
    // MARK: - Balance Card (Modern Glassmorphism)
    private var balanceCard: some View {
        VStack(spacing: 16) {
            VStack(spacing: 8) {
                Text("total_balance".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
                
                if viewModel.isLoading {
                    ProgressView()
                        .frame(height: 40)
                } else {
                    Text(viewModel.totalBalance.formattedCurrency)
                        .font(.system(size: 42, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                }
                
                // Unrealized PnL
                if viewModel.unrealizedPnl != 0 {
                    HStack(spacing: 4) {
                        Text("unrealized".localized + ":")
                            .font(.caption)
                            .foregroundColor(.enlikoTextSecondary)
                        Text(viewModel.unrealizedPnl.formattedSignedAmount)
                            .font(.caption.bold())
                            .foregroundColor(viewModel.unrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
                    }
                }
            }
            
            // PnL Summary Row
            HStack(spacing: 0) {
                pnlCell(title: "today".localized, value: viewModel.todayPnl)
                Divider().frame(height: 40).background(Color.enlikoBorder)
                pnlCell(title: "7d".localized, value: viewModel.weekPnl)
                Divider().frame(height: 40).background(Color.enlikoBorder)
                pnlCell(title: "30d".localized, value: viewModel.monthPnl)
            }
        }
        .padding(24)
        .frame(maxWidth: .infinity)
        .background(
            ZStack {
                // Gradient base
                LinearGradient(
                    colors: [Color.enlikoPrimary.opacity(0.2), Color.enlikoCard],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                // Glass overlay
                RoundedRectangle(cornerRadius: 24)
                    .fill(.ultraThinMaterial.opacity(0.3))
            }
        )
        .cornerRadius(24)
        .overlay(
            RoundedRectangle(cornerRadius: 24)
                .stroke(Color.enlikoPrimary.opacity(0.3), lineWidth: 1)
        )
        .shadow(color: Color.enlikoPrimary.opacity(0.2), radius: 20, y: 10)
    }
    
    private func pnlCell(title: String, value: Double) -> some View {
        VStack(spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value.formattedSignedAmount)
                .font(.subheadline.bold())
                .foregroundColor(value >= 0 ? .enlikoGreen : .enlikoRed)
        }
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - Period Filter
    private var periodFilterSection: some View {
        HStack(spacing: 8) {
            ForEach(DashboardPeriod.allCases, id: \.self) { period in
                Button {
                    viewModel.selectedPeriod = period
                    Task {
                        await viewModel.fetchStats(
                            accountType: appState.currentAccountType.rawValue,
                            exchange: appState.currentExchange.rawValue
                        )
                    }
                } label: {
                    Text(period.displayName)
                        .font(.subheadline.bold())
                        .foregroundColor(viewModel.selectedPeriod == period ? .white : .secondary)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(viewModel.selectedPeriod == period ? Color.enlikoPrimary : Color.enlikoSurface)
                        .cornerRadius(20)
                }
            }
            Spacer()
        }
    }
    
    // MARK: - Stats Overview (Cluster Analysis)
    private var statsOverviewSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("stats_overview".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            // Main Stats Grid
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                DashboardStatCard(
                    title: "total_trades".localized,
                    value: "\(viewModel.totalTrades)",
                    icon: "number",
                    iconColor: .enlikoPrimary
                )
                DashboardStatCard(
                    title: "win_rate".localized,
                    value: String(format: "%.1f%%", viewModel.winRate),
                    icon: "chart.pie.fill",
                    iconColor: viewModel.winRate >= 50 ? .enlikoGreen : .enlikoRed
                )
                DashboardStatCard(
                    title: "profit_factor".localized,
                    value: String(format: "%.2f", viewModel.profitFactor),
                    icon: "arrow.up.arrow.down",
                    iconColor: viewModel.profitFactor >= 1 ? .enlikoGreen : .enlikoRed
                )
                DashboardStatCard(
                    title: "total_pnl".localized,
                    value: viewModel.totalPnl.formattedCurrency,
                    icon: "dollarsign.circle.fill",
                    iconColor: viewModel.totalPnl >= 0 ? .enlikoGreen : .enlikoRed,
                    valueColor: viewModel.totalPnl >= 0 ? .enlikoGreen : .enlikoRed
                )
            }
            
            // Avg Win / Loss Row
            HStack(spacing: 12) {
                HStack {
                    Image(systemName: "arrow.up.circle.fill")
                        .foregroundColor(.enlikoGreen)
                    VStack(alignment: .leading) {
                        Text("avg_win".localized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(viewModel.avgWin.formattedCurrency)
                            .font(.subheadline.bold())
                            .foregroundColor(.enlikoGreen)
                    }
                    Spacer()
                }
                .padding(12)
                .background(Color.enlikoGreen.opacity(0.1))
                .cornerRadius(12)
                
                HStack {
                    Image(systemName: "arrow.down.circle.fill")
                        .foregroundColor(.enlikoRed)
                    VStack(alignment: .leading) {
                        Text("avg_loss".localized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(viewModel.avgLoss.formattedCurrency)
                            .font(.subheadline.bold())
                            .foregroundColor(.enlikoRed)
                    }
                    Spacer()
                }
                .padding(12)
                .background(Color.enlikoRed.opacity(0.1))
                .cornerRadius(12)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Strategy Breakdown (Cluster Analysis)
    private var strategyBreakdownSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("by_strategy".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                NavigationLink {
                    StrategyStatsView()
                } label: {
                    Text("details".localized)
                        .font(.caption)
                        .foregroundColor(.enlikoPrimary)
                }
            }
            
            if viewModel.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity)
                    .padding()
            } else if viewModel.strategyBreakdown.isEmpty {
                VStack(spacing: 8) {
                    Image(systemName: "chart.bar.doc.horizontal")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text("no_trades_yet".localized)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 24)
            } else {
                // Strategy Performance Rows
                ForEach(viewModel.strategyBreakdown) { item in
                    StrategyClusterRow(item: item)
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Quick Actions (Enhanced with new features)
    private var quickActionsSection: some View {
        VStack(spacing: 12) {
            Text("quick_actions".localized)
                .font(.headline)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            // Row 1: Positions & Orders
            HStack(spacing: 12) {
                NavigationLink {
                    PositionsView()
                } label: {
                    QuickActionCard(
                        icon: "chart.line.uptrend.xyaxis",
                        title: "positions".localized,
                        count: viewModel.openPositionsCount,
                        color: .enlikoPrimary
                    )
                }
                
                NavigationLink {
                    PositionsView()
                } label: {
                    QuickActionCard(
                        icon: "clock.fill",
                        title: "orders".localized,
                        count: viewModel.pendingOrdersCount,
                        color: .orange
                    )
                }
            }
            
            // Row 2: Market & Wallet
            HStack(spacing: 12) {
                NavigationLink {
                    MarketHubView()
                } label: {
                    QuickActionCard(
                        icon: "chart.bar.fill",
                        title: "Market",
                        count: 0,
                        color: .blue
                    )
                }
                
                NavigationLink {
                    WalletView()
                } label: {
                    QuickActionCard(
                        icon: "wallet.pass.fill",
                        title: "Wallet",
                        count: 0,
                        color: .green
                    )
                }
            }
            
            // Row 3: Alerts & History
            HStack(spacing: 12) {
                NavigationLink {
                    AlertsView()
                } label: {
                    QuickActionCard(
                        icon: "bell.badge.fill",
                        title: "Alerts",
                        count: 0,
                        color: .yellow
                    )
                }
                
                NavigationLink {
                    TradeHistoryFullView()
                } label: {
                    QuickActionCard(
                        icon: "clock.arrow.circlepath",
                        title: "History",
                        count: 0,
                        color: .purple
                    )
                }
            }
            
            // HyperLiquid Section (if HL selected)
            if appState.currentExchange == .hyperliquid {
                NavigationLink {
                    HyperLiquidView()
                } label: {
                    HStack {
                        Image(systemName: "cube.transparent.fill")
                            .font(.title2)
                            .foregroundColor(.cyan)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text("HyperLiquid")
                                .font(.subheadline.bold())
                                .foregroundColor(.white)
                            Text("Vaults, Transfers, Points")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(
                        LinearGradient(
                            colors: [Color.cyan.opacity(0.2), Color.enlikoSurface],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(12)
                }
            }
        }
    }
    
    // MARK: - Recent Trades
    private var recentTradesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("recent_trades".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                NavigationLink {
                    TradeHistoryView()
                } label: {
                    Text("view_all".localized)
                        .font(.caption)
                        .foregroundColor(.enlikoPrimary)
                }
            }
            
            if viewModel.recentTrades.isEmpty {
                VStack(spacing: 8) {
                    Image(systemName: "clock.arrow.circlepath")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text("no_trades_yet".localized)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 24)
            } else {
                ForEach(viewModel.recentTrades.prefix(5)) { trade in
                    DashboardRecentTradeRow(trade: trade)
                    if trade.id != viewModel.recentTrades.prefix(5).last?.id {
                        Divider().background(Color.enlikoBorder)
                    }
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
}

// MARK: - Strategy Cluster Row (Enhanced)
struct StrategyClusterRow: View {
    let item: StrategyBreakdownItem
    
    var body: some View {
        HStack(spacing: 12) {
            // Strategy Icon
            ZStack {
                Circle()
                    .fill(item.color.opacity(0.2))
                    .frame(width: 44, height: 44)
                Text(strategyEmoji)
                    .font(.title2)
            }
            
            // Strategy Info
            VStack(alignment: .leading, spacing: 2) {
                Text(item.strategy.uppercased())
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                let tradesText = "\(item.trades) " + "trades".localized
                let winRateText = String(format: "%.0f%%", item.winRate) + " WR"
                Text(tradesText + " • " + winRateText)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // PnL with progress bar
            VStack(alignment: .trailing, spacing: 4) {
                Text(item.pnl.formattedSignedAmount)
                    .font(.subheadline.bold())
                    .foregroundColor(item.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                
                // Progress bar showing relative PnL
                GeometryReader { geo in
                    ZStack(alignment: item.pnl >= 0 ? .leading : .trailing) {
                        Rectangle()
                            .fill(Color.enlikoBorder)
                        Rectangle()
                            .fill(item.pnl >= 0 ? Color.enlikoGreen : Color.enlikoRed)
                            .frame(width: min(geo.size.width, geo.size.width * min(abs(item.pnl) / 500, 1)))
                    }
                }
                .frame(width: 60, height: 4)
                .cornerRadius(2)
            }
        }
        .padding(12)
        .background(Color.enlikoBackground)
        .cornerRadius(12)
    }
    
    private var strategyEmoji: String {
        switch item.strategy.lowercased() {
        case "oi": return "📊"
        case "rsi_bb", "rsi-bb": return "📈"
        case "scryptomera": return "🔮"
        case "scalper": return "⚡"
        case "fibonacci": return "🌀"
        case "elcaro": return "🎯"
        case "manual": return "✋"
        default: return "📊"
        }
    }
}

// MARK: - Quick Action Card (Glass Style)
struct QuickActionCard: View {
    let icon: String
    let title: String
    let count: Int
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                ZStack {
                    Circle()
                        .fill(color.opacity(0.15))
                        .frame(width: 44, height: 44)
                    Image(systemName: icon)
                        .font(.title3)
                        .foregroundColor(color)
                }
                Spacer()
                if count > 0 {
                    Text("\(count)")
                        .font(.caption.bold())
                        .foregroundColor(.white)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(
                            Capsule()
                                .fill(color)
                        )
                }
            }
            
            Text(title)
                .font(.subheadline.weight(.medium))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(16)
        .background(
            ZStack {
                Color.enlikoSurface
                RoundedRectangle(cornerRadius: 16)
                    .fill(color.opacity(0.05))
            }
        )
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(color.opacity(0.2), lineWidth: 1)
        )
    }
}

// MARK: - Dashboard Stat Card (Modern Glass)
struct DashboardStatCard: View {
    let title: String
    let value: String
    let icon: String
    var iconColor: Color = .enlikoPrimary
    var valueColor: Color = .white
    
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                ZStack {
                    Circle()
                        .fill(iconColor.opacity(0.15))
                        .frame(width: 36, height: 36)
                    Image(systemName: icon)
                        .font(.subheadline)
                        .foregroundColor(iconColor)
                }
                Spacer()
            }
            Text(value)
                .font(.title3.bold())
                .foregroundColor(valueColor)
            Text(title)
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.enlikoCard)
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color.enlikoBorder, lineWidth: 0.5)
        )
    }
}

// MARK: - Dashboard Recent Trade Row (Simple version)
struct DashboardRecentTradeRow: View {
    let trade: DashboardRecentTrade
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text(trade.symbol)
                        .font(.subheadline.bold())
                        .foregroundColor(.white)
                    Text(trade.side)
                        .font(.caption.bold())
                        .foregroundColor(trade.side == "Long" ? .enlikoGreen : .enlikoRed)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background((trade.side == "Long" ? Color.enlikoGreen : Color.enlikoRed).opacity(0.2))
                        .cornerRadius(4)
                }
                Text(trade.strategy.uppercased())
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text(trade.pnl.formattedSignedAmount)
                    .font(.subheadline.bold())
                    .foregroundColor(trade.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                Text(trade.closedAt)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Period Enum
enum DashboardPeriod: String, CaseIterable {
    case today = "today"
    case week = "week"
    case month = "month"
    case all = "all"
    
    var displayName: String {
        switch self {
        case .today: return "24h"
        case .week: return "7d"
        case .month: return "30d"
        case .all: return "All"
        }
    }
    
    var apiValue: String { rawValue }
}

// MARK: - Dashboard Recent Trade (Simple model for API response)
struct DashboardRecentTrade: Codable, Identifiable {
    var id: String { "\(symbol)-\(closedAt)-\(pnl)" }
    let symbol: String
    let side: String
    let pnl: Double
    let strategy: String
    let closedAt: String
    
    enum CodingKeys: String, CodingKey {
        case symbol, side, pnl, strategy
        case closedAt = "closed_at"
    }
}

// MARK: - ViewModel
@MainActor
class DashboardViewModel: ObservableObject {
    @Published var selectedPeriod: DashboardPeriod = .week
    @Published var isLoading = false
    
    @Published var totalBalance: Double = 0
    @Published var unrealizedPnl: Double = 0
    @Published var todayPnl: Double = 0
    @Published var weekPnl: Double = 0
    @Published var monthPnl: Double = 0
    
    @Published var totalTrades: Int = 0
    @Published var winRate: Double = 0
    @Published var profitFactor: Double = 0
    @Published var totalPnl: Double = 0
    @Published var avgWin: Double = 0
    @Published var avgLoss: Double = 0
    
    @Published var strategyBreakdown: [StrategyBreakdownItem] = []
    @Published var recentTrades: [DashboardRecentTrade] = []
    
    @Published var openPositionsCount: Int = 0
    @Published var pendingOrdersCount: Int = 0
    
    private let network = NetworkService.shared
    
    func refresh(accountType: String, exchange: String) async {
        isLoading = true
        defer { isLoading = false }
        
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.fetchBalance(accountType: accountType, exchange: exchange) }
            group.addTask { await self.fetchStats(accountType: accountType, exchange: exchange) }
            group.addTask { await self.fetchPnlPeriods(accountType: accountType, exchange: exchange) }
            group.addTask { await self.fetchPositionsCount(accountType: accountType, exchange: exchange) }
            group.addTask { await self.fetchOrdersCount(accountType: accountType, exchange: exchange) }
        }
    }
    
    private func fetchBalance(accountType: String, exchange: String) async {
        do {
            // Try direct Balance decode first (API returns balance directly, not wrapped)
            let balance: Balance = try await network.get("/trading/balance", params: ["account_type": accountType, "exchange": exchange])
            totalBalance = balance.equity
            unrealizedPnl = balance.unrealizedPnl
        } catch {
            // Fallback to wrapped BalanceResponse
            do {
                let response: BalanceResponse = try await network.get("/trading/balance", params: ["account_type": accountType, "exchange": exchange])
                if let balance = response.balanceData {
                    totalBalance = balance.equity
                    unrealizedPnl = balance.unrealizedPnl
                }
            } catch {
                print("Dashboard: Failed to fetch balance: \(error)")
            }
        }
    }
    
    private func fetchPnlPeriods(accountType: String, exchange: String) async {
        // Fetch PnL for different periods from /trading/stats endpoint
        do {
            // Today
            let todayResponse: DashboardStatsResponse = try await network.get(
                "/trading/stats/by-strategy",
                params: ["period": "today", "account_type": accountType, "exchange": exchange, "strategy": "all"]
            )
            todayPnl = todayResponse.summary?.totalPnl ?? 0
            
            // Week
            let weekResponse: DashboardStatsResponse = try await network.get(
                "/trading/stats/by-strategy",
                params: ["period": "week", "account_type": accountType, "exchange": exchange, "strategy": "all"]
            )
            weekPnl = weekResponse.summary?.totalPnl ?? 0
            
            // Month
            let monthResponse: DashboardStatsResponse = try await network.get(
                "/trading/stats/by-strategy",
                params: ["period": "month", "account_type": accountType, "exchange": exchange, "strategy": "all"]
            )
            monthPnl = monthResponse.summary?.totalPnl ?? 0
        } catch {
            print("Dashboard: Failed to fetch PnL periods: \(error)")
        }
    }
    
    func fetchStats(accountType: String, exchange: String) async {
        do {
            let response: DashboardStatsResponse = try await network.get(
                "/trading/stats/by-strategy",
                params: ["period": selectedPeriod.apiValue, "account_type": accountType, "exchange": exchange, "strategy": "all"]
            )
            if let summary = response.summary {
                totalTrades = summary.totalTrades
                winRate = summary.winRate
                profitFactor = summary.profitFactor
                totalPnl = summary.totalPnl
                avgWin = summary.avgWin
                avgLoss = summary.avgLoss
            }
            strategyBreakdown = response.breakdown ?? []
            recentTrades = response.recentTrades ?? []
        } catch {
            print("Dashboard: Failed to fetch stats: \(error)")
        }
    }
    
    private func fetchPositionsCount(accountType: String, exchange: String) async {
        do {
            let response: PositionsResponse = try await network.get("/trading/positions", params: ["account_type": accountType, "exchange": exchange])
            openPositionsCount = response.positionsData.count
        } catch {
            print("Dashboard: Failed to fetch positions: \(error)")
        }
    }
    
    private func fetchOrdersCount(accountType: String, exchange: String) async {
        do {
            let response: OrdersResponse = try await network.get("/trading/orders", params: ["account_type": accountType, "exchange": exchange])
            pendingOrdersCount = response.ordersData.count
        } catch {
            print("Dashboard: Failed to fetch orders: \(error)")
        }
    }
}

// MARK: - Response Models (Dashboard specific)
struct DashboardStatsResponse: Codable {
    let summary: DashboardStatsSummary?
    let breakdown: [StrategyBreakdownItem]?
    let recentTrades: [DashboardRecentTrade]?
    
    enum CodingKeys: String, CodingKey {
        case summary, breakdown
        case recentTrades = "recent_trades"
    }
}

struct DashboardStatsSummary: Codable {
    let totalTrades: Int
    let winRate: Double
    let profitFactor: Double
    let avgWin: Double
    let avgLoss: Double
    let bestTrade: Double
    let totalPnl: Double
    
    enum CodingKeys: String, CodingKey {
        case totalTrades = "total_trades"
        case winRate = "win_rate"
        case profitFactor = "profit_factor"
        case avgWin = "avg_win"
        case avgLoss = "avg_loss"
        case bestTrade = "best_trade"
        case totalPnl = "total_pnl"
    }
}

// MARK: - Extensions
extension Double {
    var formattedSignedAmount: String {
        let sign = self >= 0 ? "+" : ""
        return "\(sign)$\(String(format: "%.2f", abs(self)))"
    }
}

#Preview {
    NavigationStack {
        DashboardView()
            .environmentObject(AppState.shared)
            .preferredColorScheme(.dark)
    }
}
