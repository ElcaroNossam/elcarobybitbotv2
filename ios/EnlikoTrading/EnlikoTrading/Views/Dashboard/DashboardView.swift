//
//  DashboardView.swift
//  EnlikoTrading
//
//  Main Dashboard - like Portfolio/Profile in Telegram bot
//  Shows: Balance, Stats with period filters, Strategy breakdown
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
                // Balance Card
                balanceCard
                
                // Period Filter Pills
                periodFilterSection
                
                // Stats Overview
                statsOverviewSection
                
                // Strategy Breakdown
                strategyBreakdownSection
                
                // Recent Trades
                recentTradesSection
                
                // Quick Actions
                quickActionsSection
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
    
    // MARK: - Balance Card
    private var balanceCard: some View {
        VStack(spacing: 16) {
            HStack {
                HStack(spacing: 6) {
                    Circle()
                        .fill(appState.currentExchange == .bybit ? Color.orange : Color.cyan)
                        .frame(width: 8, height: 8)
                    Text(appState.currentExchange.displayName)
                        .font(.caption.bold())
                        .foregroundColor(.secondary)
                }
                Spacer()
                HStack(spacing: 6) {
                    Circle()
                        .fill(appState.currentAccountType == .demo ? Color.orange : Color.green)
                        .frame(width: 8, height: 8)
                    Text(appState.currentAccountType == .demo ? "Demo" : "Real")
                        .font(.caption.bold())
                        .foregroundColor(.secondary)
                }
            }
            
            VStack(spacing: 8) {
                Text("total_balance".localized)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                if viewModel.isLoading {
                    ProgressView()
                        .frame(height: 40)
                } else {
                    Text(viewModel.totalBalance.formattedCurrency)
                        .font(.system(size: 36, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                }
            }
            
            HStack(spacing: 24) {
                VStack(spacing: 4) {
                    Text("today".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(viewModel.todayPnl.formattedSignedAmount)
                        .font(.subheadline.bold())
                        .foregroundColor(viewModel.todayPnl >= 0 ? .enlikoGreen : .enlikoRed)
                }
                
                VStack(spacing: 4) {
                    Text("7d".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(viewModel.weekPnl.formattedSignedAmount)
                        .font(.subheadline.bold())
                        .foregroundColor(viewModel.weekPnl >= 0 ? .enlikoGreen : .enlikoRed)
                }
                
                VStack(spacing: 4) {
                    Text("30d".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(viewModel.monthPnl.formattedSignedAmount)
                        .font(.subheadline.bold())
                        .foregroundColor(viewModel.monthPnl >= 0 ? .enlikoGreen : .enlikoRed)
                }
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity)
        .background(
            LinearGradient(
                colors: [Color.enlikoPrimary.opacity(0.3), Color.enlikoSurface],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(20)
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
        }
    }
    
    // MARK: - Stats Overview
    private var statsOverviewSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("stats_overview".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                DashboardStatCard(title: "total_trades".localized, value: "\(viewModel.totalTrades)", icon: "number")
                DashboardStatCard(title: "win_rate".localized, value: String(format: "%.1f%%", viewModel.winRate), icon: "chart.pie.fill")
                DashboardStatCard(title: "avg_win".localized, value: viewModel.avgWin.formattedCurrency, icon: "arrow.up.circle.fill", valueColor: .enlikoGreen)
                DashboardStatCard(title: "avg_loss".localized, value: viewModel.avgLoss.formattedCurrency, icon: "arrow.down.circle.fill", valueColor: .enlikoRed)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Strategy Breakdown
    private var strategyBreakdownSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("by_strategy".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            if viewModel.strategyBreakdown.isEmpty {
                Text("no_trades_yet".localized)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            } else {
                ForEach(viewModel.strategyBreakdown) { item in
                    StrategyRowCard(item: item)
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
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
                Text("no_trades_yet".localized)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            } else {
                ForEach(viewModel.recentTrades.prefix(5)) { trade in
                    RecentTradeRow(trade: trade)
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
    
    // MARK: - Quick Actions
    private var quickActionsSection: some View {
        VStack(spacing: 12) {
            NavigationLink {
                PositionsView()
            } label: {
                DashboardQuickAction(
                    icon: "chart.line.uptrend.xyaxis",
                    title: "positions".localized,
                    count: viewModel.openPositionsCount,
                    color: .enlikoPrimary
                )
            }
            
            NavigationLink {
                // Orders are in PositionsView tabs
                PositionsView()
            } label: {
                DashboardQuickAction(
                    icon: "clock.fill",
                    title: "pending_orders".localized,
                    count: viewModel.pendingOrdersCount,
                    color: .orange
                )
            }
        }
    }
}

// MARK: - Supporting Views
struct DashboardStatCard: View {
    let title: String
    let value: String
    let icon: String
    var valueColor: Color = .white
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(.enlikoPrimary)
                Spacer()
            }
            Text(value)
                .font(.title3.bold())
                .foregroundColor(valueColor)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(12)
        .background(Color.enlikoBackground)
        .cornerRadius(12)
    }
}

struct StrategyRowCard: View {
    let item: StrategyBreakdownItem
    
    var body: some View {
        HStack {
            Circle()
                .fill(item.color)
                .frame(width: 10, height: 10)
            
            Text(item.strategy.capitalized)
                .font(.subheadline.bold())
                .foregroundColor(.white)
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text(item.pnl.formattedSignedAmount)
                    .font(.subheadline.bold())
                    .foregroundColor(item.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                Text("\(item.trades) trades • \(Int(item.winRate))% WR")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 8)
    }
}

struct RecentTradeRow: View {
    let trade: RecentTrade
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(trade.symbol)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                HStack(spacing: 4) {
                    Text(trade.side.uppercased())
                        .font(.caption2.bold())
                        .foregroundColor(trade.side.lowercased() == "buy" ? .enlikoGreen : .enlikoRed)
                    if let strategy = trade.strategy {
                        Text("• \(strategy)")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text(trade.pnl.formattedSignedAmount)
                    .font(.subheadline.bold())
                    .foregroundColor(trade.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                Text(trade.closedAt.timeAgo)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

struct DashboardQuickAction: View {
    let icon: String
    let title: String
    let count: Int
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(color)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                if count > 0 {
                    Text("\(count) open")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            if count > 0 {
                Text("\(count)")
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(color)
                    .cornerRadius(10)
            }
            
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(12)
        .frame(maxWidth: .infinity)
        .background(Color.enlikoSurface)
        .cornerRadius(12)
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

// MARK: - ViewModel
class DashboardViewModel: ObservableObject {
    @Published var selectedPeriod: DashboardPeriod = .week
    @Published var isLoading = false
    
    @Published var totalBalance: Double = 0
    @Published var todayPnl: Double = 0
    @Published var weekPnl: Double = 0
    @Published var monthPnl: Double = 0
    
    @Published var totalTrades: Int = 0
    @Published var winRate: Double = 0
    @Published var profitFactor: Double = 0
    @Published var avgWin: Double = 0
    @Published var avgLoss: Double = 0
    
    @Published var strategyBreakdown: [StrategyBreakdownItem] = []
    @Published var recentTrades: [RecentTrade] = []
    
    @Published var openPositionsCount: Int = 0
    @Published var pendingOrdersCount: Int = 0
    
    private let network = NetworkService.shared
    
    @MainActor
    func refresh(accountType: String, exchange: String) async {
        isLoading = true
        defer { isLoading = false }
        
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.fetchBalance(accountType: accountType, exchange: exchange) }
            group.addTask { await self.fetchStats(accountType: accountType, exchange: exchange) }
            group.addTask { await self.fetchPositionsCount(accountType: accountType, exchange: exchange) }
            group.addTask { await self.fetchOrdersCount(accountType: accountType, exchange: exchange) }
        }
    }
    
    @MainActor
    private func fetchBalance(accountType: String, exchange: String) async {
        do {
            let response: BalanceResponse = try await network.get("/balance", params: ["account_type": accountType, "exchange": exchange])
            if let balance = response.balanceData {
                totalBalance = balance.equity
                todayPnl = balance.unrealizedPnl
                // weekPnl comes from stats, not balance
            }
        } catch {
            print("Dashboard: Failed to fetch balance: \(error)")
        }
    }
    
    @MainActor
    func fetchStats(accountType: String, exchange: String) async {
        do {
            let response: DashboardStatsResponse = try await network.get(
                "/stats/by-strategy",
                params: ["period": selectedPeriod.apiValue, "account_type": accountType, "exchange": exchange, "strategy": "all"]
            )
            if let summary = response.summary {
                totalTrades = summary.totalTrades
                winRate = summary.winRate
                profitFactor = summary.profitFactor
                avgWin = summary.avgWin
                avgLoss = summary.avgLoss
            }
            strategyBreakdown = response.breakdown ?? []
            recentTrades = response.recentTrades ?? []
        } catch {
            print("Dashboard: Failed to fetch stats: \(error)")
        }
    }
    
    @MainActor
    private func fetchPositionsCount(accountType: String, exchange: String) async {
        do {
            let response: PositionsResponse = try await network.get("/positions", params: ["account_type": accountType, "exchange": exchange])
            openPositionsCount = response.positionsData.count
        } catch {
            print("Dashboard: Failed to fetch positions: \(error)")
        }
    }
    
    @MainActor
    private func fetchOrdersCount(accountType: String, exchange: String) async {
        do {
            let response: OrdersResponse = try await network.get("/orders", params: ["account_type": accountType, "exchange": exchange])
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
    let recentTrades: [RecentTrade]?
    
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

extension Date {
    var timeAgo: String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: self, relativeTo: Date())
    }
}

#Preview {
    NavigationStack {
        DashboardView()
            .environmentObject(AppState.shared)
            .preferredColorScheme(.dark)
    }
}
