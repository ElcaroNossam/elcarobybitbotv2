//
//  StrategyStatsView.swift
//  EnlikoTrading
//
//  Strategy-based trading statistics with period filter
//  Like Telegram bot stats but with beautiful iOS design
//

import SwiftUI
import Charts

// MARK: - Strategy Stats View
struct StrategyStatsView: View {
    @StateObject private var viewModel = StrategyStatsViewModel()
    @EnvironmentObject var appState: AppState
    @ObservedObject var localization = LocalizationManager.shared
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            ZStack {
                // Background
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Period Selector
                        periodSelector
                        
                        // Strategy Filter Pills
                        strategyFilterPills
                        
                        // Summary Card
                        if let stats = viewModel.currentStats {
                            summaryCard(stats: stats)
                        }
                        
                        // Strategy Breakdown
                        if !viewModel.strategyBreakdown.isEmpty {
                            strategyBreakdownSection
                        }
                        
                        // Trade History
                        if !viewModel.recentTrades.isEmpty {
                            recentTradesSection
                        }
                    }
                    .padding()
                    .padding(.bottom, 80)
                }
                .refreshable {
                    await viewModel.refresh(accountType: appState.currentAccountType.rawValue)
                }
                
                // Loading overlay
                if viewModel.isLoading && viewModel.currentStats == nil {
                    LoadingOverlay()
                }
            }
            .navigationTitle("stats_by_strategy".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button {
                        dismiss()
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                            .font(.title2)
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    accountTypePicker
                }
            }
        }
        .task {
            await viewModel.refresh(accountType: appState.currentAccountType.rawValue)
        }
        .onChange(of: appState.currentAccountType) { _, newValue in
            Task {
                await viewModel.refresh(accountType: newValue.rawValue)
            }
        }
    }
    
    // MARK: - Period Selector
    private var periodSelector: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(StatsPeriod.allCases, id: \.self) { period in
                    PeriodPill(
                        title: period.displayName,
                        isSelected: viewModel.selectedPeriod == period
                    ) {
                        withAnimation(.spring(response: 0.3)) {
                            viewModel.selectedPeriod = period
                        }
                        Task {
                            await viewModel.refresh(accountType: appState.currentAccountType.rawValue)
                        }
                        HapticManager.shared.perform(.selection)
                    }
                }
            }
        }
    }
    
    // MARK: - Strategy Filter Pills
    private var strategyFilterPills: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                StrategyPill(
                    name: "all_strategies".localized,
                    icon: "chart.bar.fill",
                    color: .enlikoPrimary,
                    isSelected: viewModel.selectedStrategy == nil
                ) {
                    viewModel.selectedStrategy = nil
                    Task {
                        await viewModel.refresh(accountType: appState.currentAccountType.rawValue)
                    }
                }
                
                ForEach(TradingStrategy.allCases, id: \.self) { strategy in
                    StrategyPill(
                        name: strategy.displayName,
                        icon: strategy.icon,
                        color: strategy.color,
                        isSelected: viewModel.selectedStrategy == strategy
                    ) {
                        viewModel.selectedStrategy = strategy
                        Task {
                            await viewModel.refresh(accountType: appState.currentAccountType.rawValue)
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Summary Card
    private func summaryCard(stats: StrategyStats) -> some View {
        VStack(spacing: 16) {
            // Main PnL
            VStack(spacing: 4) {
                Text("total_pnl".localized)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text(formatCurrency(stats.totalPnl))
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    .foregroundColor(stats.totalPnl >= 0 ? .enlikoGreen : .enlikoRed)
            }
            
            Divider()
                .background(Color.enlikoBorder)
            
            // Stats Grid
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 16) {
                StatItem(
                    title: "trades".localized,
                    value: "\(stats.totalTrades)",
                    icon: "number"
                )
                
                StatItem(
                    title: "win_rate".localized,
                    value: String(format: "%.1f%%", stats.winRate),
                    icon: "percent",
                    color: stats.winRate >= 50 ? .enlikoGreen : .enlikoRed
                )
                
                StatItem(
                    title: "profit_factor".localized,
                    value: String(format: "%.2f", stats.profitFactor),
                    icon: "chart.line.uptrend.xyaxis"
                )
                
                StatItem(
                    title: "avg_win".localized,
                    value: formatCurrency(stats.avgWin),
                    icon: "arrow.up.right",
                    color: .enlikoGreen
                )
                
                StatItem(
                    title: "avg_loss".localized,
                    value: formatCurrency(abs(stats.avgLoss)),
                    icon: "arrow.down.right",
                    color: .enlikoRed
                )
                
                StatItem(
                    title: "best_trade".localized,
                    value: formatCurrency(stats.bestTrade),
                    icon: "trophy.fill",
                    color: .enlikoGold
                )
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    // MARK: - Strategy Breakdown
    private var strategyBreakdownSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("strategy_breakdown".localized)
                .font(.headline)
                .foregroundColor(.primary)
            
            ForEach(viewModel.strategyBreakdown) { item in
                StrategyBreakdownRow(item: item)
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    // MARK: - Recent Trades
    private var recentTradesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("recent_trades".localized)
                    .font(.headline)
                
                Spacer()
                
                NavigationLink(destination: TradeHistoryView()) {
                    Text("view_all".localized)
                        .font(.caption)
                        .foregroundColor(.enlikoPrimary)
                }
            }
            
            ForEach(viewModel.recentTrades.prefix(5)) { trade in
                TradeRow(trade: trade)
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    // MARK: - Account Type Picker
    private var accountTypePicker: some View {
        Menu {
            Button {
                appState.currentAccountType = .demo
            } label: {
                Label("Demo", systemImage: appState.currentAccountType == .demo ? "checkmark" : "")
            }
            
            Button {
                appState.currentAccountType = .real
            } label: {
                Label("Real", systemImage: appState.currentAccountType == .real ? "checkmark" : "")
            }
        } label: {
            HStack(spacing: 4) {
                Circle()
                    .fill(appState.currentAccountType == .demo ? .orange : .green)
                    .frame(width: 8, height: 8)
                Text(appState.currentAccountType == .demo ? "Demo" : "Real")
                    .font(.caption.bold())
                Image(systemName: "chevron.down")
                    .font(.caption2)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(Color.enlikoCard)
            .cornerRadius(20)
        }
    }
    
    private func formatCurrency(_ value: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = "USD"
        formatter.maximumFractionDigits = 2
        return formatter.string(from: NSNumber(value: value)) ?? "$0.00"
    }
}

// MARK: - Supporting Views
struct PeriodPill: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption.bold())
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(isSelected ? Color.enlikoPrimary : Color.enlikoCard)
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(20)
        }
    }
}

struct StrategyPill: View {
    let name: String
    let icon: String
    let color: Color
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.caption2)
                Text(name)
                    .font(.caption.bold())
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(isSelected ? color : Color.enlikoCard)
            .foregroundColor(isSelected ? .white : .primary)
            .cornerRadius(20)
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(isSelected ? Color.clear : color.opacity(0.3), lineWidth: 1)
            )
        }
    }
}

struct StatItem: View {
    let title: String
    let value: String
    let icon: String
    var color: Color = .primary
    
    var body: some View {
        VStack(spacing: 6) {
            Image(systemName: icon)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(value)
                .font(.headline)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }
}

struct StrategyBreakdownRow: View {
    let item: StrategyBreakdownItem
    
    var body: some View {
        HStack {
            // Strategy icon + name
            HStack(spacing: 8) {
                Image(systemName: item.strategy.icon)
                    .foregroundColor(item.strategy.color)
                    .frame(width: 24)
                
                Text(item.strategy.displayName)
                    .font(.subheadline)
            }
            
            Spacer()
            
            // Stats
            VStack(alignment: .trailing, spacing: 2) {
                Text(formatCurrency(item.pnl))
                    .font(.subheadline.bold())
                    .foregroundColor(item.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                
                Text("\(item.trades) trades • \(String(format: "%.0f%%", item.winRate)) WR")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
    
    private func formatCurrency(_ value: Double) -> String {
        let sign = value >= 0 ? "+" : ""
        return "\(sign)$\(String(format: "%.2f", abs(value)))"
    }
}

struct TradeRow: View {
    let trade: RecentTrade
    
    var body: some View {
        HStack {
            // Symbol + Side
            VStack(alignment: .leading, spacing: 2) {
                Text(trade.symbol)
                    .font(.subheadline.bold())
                
                HStack(spacing: 4) {
                    Text(trade.side)
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(trade.side == "Long" ? Color.enlikoGreen.opacity(0.2) : Color.enlikoRed.opacity(0.2))
                        .foregroundColor(trade.side == "Long" ? .enlikoGreen : .enlikoRed)
                        .cornerRadius(4)
                    
                    if let strategy = trade.strategy {
                        Text(strategy.capitalized)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
            
            // PnL + Time
            VStack(alignment: .trailing, spacing: 2) {
                Text(formatCurrency(trade.pnl))
                    .font(.subheadline.bold())
                    .foregroundColor(trade.pnl >= 0 ? .enlikoGreen : .enlikoRed)
                
                Text(trade.closedAt)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
    
    private func formatCurrency(_ value: Double) -> String {
        let sign = value >= 0 ? "+" : ""
        return "\(sign)$\(String(format: "%.2f", abs(value)))"
    }
}

struct LoadingOverlay: View {
    var body: some View {
        ZStack {
            Color.black.opacity(0.3)
            
            VStack(spacing: 16) {
                ProgressView()
                    .scaleEffect(1.2)
                
                Text("loading".localized)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(24)
            .background(.ultraThinMaterial)
            .cornerRadius(16)
        }
        .ignoresSafeArea()
    }
}

// MARK: - View Model
class StrategyStatsViewModel: ObservableObject {
    @Published var selectedPeriod: StatsPeriod = .week
    @Published var selectedStrategy: TradingStrategy? = nil
    @Published var currentStats: StrategyStats?
    @Published var strategyBreakdown: [StrategyBreakdownItem] = []
    @Published var recentTrades: [RecentTrade] = []
    @Published var isLoading = false
    
    private let network = NetworkService.shared
    
    @MainActor
    func refresh(accountType: String) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let strategyParam = selectedStrategy?.rawValue ?? "all"
            let periodParam = selectedPeriod.apiValue
            
            // Fetch stats
            let stats: StrategyStatsResponse = try await network.get(
                "/stats/by-strategy",
                query: [
                    "strategy": strategyParam,
                    "period": periodParam,
                    "account_type": accountType
                ]
            )
            
            currentStats = stats.summary
            strategyBreakdown = stats.breakdown
            recentTrades = stats.recentTrades
        } catch {
            print("Failed to fetch strategy stats: \(error)")
        }
    }
}

// MARK: - Models
enum StatsPeriod: String, CaseIterable {
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
    
    var apiValue: String {
        rawValue
    }
}

enum TradingStrategy: String, CaseIterable {
    case rsi_bb
    case fibonacci
    case scryptomera
    case scalper
    case elcaro
    case oi
    case manual
    
    var displayName: String {
        switch self {
        case .rsi_bb: return "RSI+BB"
        case .fibonacci: return "Fibonacci"
        case .scryptomera: return "Scryptomera"
        case .scalper: return "Scalper"
        case .elcaro: return "Elcaro"
        case .oi: return "OI Signal"
        case .manual: return "Manual"
        }
    }
    
    var icon: String {
        switch self {
        case .rsi_bb: return "waveform.path.ecg"
        case .fibonacci: return "spiral"
        case .scryptomera: return "chart.xyaxis.line"
        case .scalper: return "bolt.fill"
        case .elcaro: return "flame.fill"
        case .oi: return "chart.bar.fill"
        case .manual: return "hand.raised.fill"
        }
    }
    
    var color: Color {
        switch self {
        case .rsi_bb: return .pink
        case .fibonacci: return .purple
        case .scryptomera: return .blue
        case .scalper: return .orange
        case .elcaro: return .red
        case .oi: return .cyan
        case .manual: return .gray
        }
    }
}

struct StrategyStats: Codable {
    let totalPnl: Double
    let totalTrades: Int
    let winRate: Double
    let profitFactor: Double
    let avgWin: Double
    let avgLoss: Double
    let bestTrade: Double
    let worstTrade: Double
    
    enum CodingKeys: String, CodingKey {
        case totalPnl = "total_pnl"
        case totalTrades = "total_trades"
        case winRate = "win_rate"
        case profitFactor = "profit_factor"
        case avgWin = "avg_win"
        case avgLoss = "avg_loss"
        case bestTrade = "best_trade"
        case worstTrade = "worst_trade"
    }
}

struct StrategyBreakdownItem: Codable, Identifiable {
    var id: String { strategyName }
    let strategyName: String
    let pnl: Double
    let trades: Int
    let winRate: Double
    
    var strategy: TradingStrategy {
        TradingStrategy(rawValue: strategyName) ?? .manual
    }
    
    enum CodingKeys: String, CodingKey {
        case strategyName = "strategy"
        case pnl
        case trades
        case winRate = "win_rate"
    }
}

struct RecentTrade: Codable, Identifiable {
    let id: Int
    let symbol: String
    let side: String
    let pnl: Double
    let strategy: String?
    let closedAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, symbol, side, pnl, strategy
        case closedAt = "closed_at"
    }
}

struct StrategyStatsResponse: Codable {
    let summary: StrategyStats
    let breakdown: [StrategyBreakdownItem]
    let recentTrades: [RecentTrade]
    
    enum CodingKeys: String, CodingKey {
        case summary, breakdown
        case recentTrades = "recent_trades"
    }
}

#Preview {
    StrategyStatsView()
        .environmentObject(AppState.shared)
        .preferredColorScheme(.dark)
}
