//
//  PortfolioView.swift
//  EnlikoTrading
//
//  Portfolio overview with balance and stats
//

import SwiftUI

struct PortfolioView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    @State private var isRefreshing = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Account Selector
                        accountSelector
                        
                        // Balance Card
                        balanceCard
                        
                        // Quick Stats
                        quickStatsGrid
                        
                        // PnL Chart Placeholder
                        pnlChartCard
                        
                        // Recent Trades
                        recentTradesSection
                    }
                    .padding()
                }
                .refreshable {
                    await tradingService.refreshAll()
                }
            }
            .navigationTitle("portfolio_title".localized)
            .withRTLSupport()
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { Task { await tradingService.refreshAll() } }) {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(.enlikoPrimary)
                    }
                }
            }
            // Refresh data when exchange or account type changes
            .onChange(of: appState.selectedExchange) { _, _ in
                Task { await tradingService.refreshAll() }
            }
            .onChange(of: appState.selectedAccountType) { _, _ in
                Task { await tradingService.refreshAll() }
            }
            .task {
                // Initial load
                await tradingService.refreshAll()
            }
        }
    }
    
    // MARK: - Account Selector
    private var accountSelector: some View {
        HStack(spacing: 12) {
            // Exchange Picker
            Menu {
                ForEach(Exchange.allCases, id: \.self) { exchange in
                    Button(action: { appState.switchExchange(to: exchange) }) {
                        HStack {
                            Text(exchange.displayName)
                            if appState.selectedExchange == exchange {
                                Image(systemName: "checkmark")
                            }
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
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color.enlikoCard)
                .cornerRadius(10)
            }
            
            // Account Type Picker - use Binding with onChange to properly sync
            Picker("Account", selection: Binding(
                get: { appState.selectedAccountType },
                set: { appState.switchAccountType(to: $0) }
            )) {
                ForEach(appState.selectedExchange.accountTypes, id: \.self) { type in
                    Text(type.displayName).tag(type)
                }
            }
            .pickerStyle(.segmented)
            
            // Account indicator
            Text(appState.selectedAccountType.icon)
                .font(.title2)
        }
    }
    
    // MARK: - Balance Card
    private var balanceCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("portfolio_balance".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
                Spacer()
                if tradingService.isLoadingBalance {
                    ProgressView()
                        .scaleEffect(0.8)
                }
            }
            
            if let balance = tradingService.balance {
                Text("$\(balance.totalEquity.formattedPrice)")
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                
                HStack(spacing: 24) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("portfolio_available".localized)
                            .font(.caption)
                            .foregroundColor(.enlikoTextSecondary)
                        Text("$\(balance.available.formattedPrice)")
                            .font(.headline)
                            .foregroundColor(.enlikoGreen)
                    }
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("portfolio_in_positions".localized)
                            .font(.caption)
                            .foregroundColor(.enlikoTextSecondary)
                        Text("$\(balance.positionMargin.formattedPrice)")
                            .font(.headline)
                            .foregroundColor(.enlikoYellow)
                    }
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("portfolio_unrealized_pnl".localized)
                            .font(.caption)
                            .foregroundColor(.enlikoTextSecondary)
                        Text(balance.unrealizedPnl.formattedCurrency)
                            .font(.headline)
                            .foregroundColor(balance.unrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
                    }
                }
            } else {
                Text("--")
                    .font(.system(size: 36, weight: .bold))
                    .foregroundColor(.enlikoTextMuted)
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color.enlikoCard, Color.enlikoCard.opacity(0.8)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.enlikoPrimary.opacity(0.3), lineWidth: 1)
        )
    }
    
    // MARK: - Quick Stats Grid
    private var quickStatsGrid: some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible())
        ], spacing: 12) {
            if let stats = tradingService.tradingStats {
                PortfolioStatCard(
                    title: "stats_total_trades".localized,
                    value: "\(stats.totalTradesCount)",
                    icon: "chart.bar.fill",
                    color: .enlikoBlue
                )
                
                PortfolioStatCard(
                    title: "stats_win_rate".localized,
                    value: String(format: "%.1f%%", stats.winRateValue),
                    icon: "target",
                    color: stats.winRateValue >= 50 ? .enlikoGreen : .enlikoRed
                )
                
                PortfolioStatCard(
                    title: "stats_total_pnl".localized,
                    value: (stats.totalPnl ?? 0).formattedCurrency,
                    icon: "dollarsign.circle.fill",
                    color: (stats.totalPnl ?? 0) >= 0 ? .enlikoGreen : .enlikoRed
                )
                
                PortfolioStatCard(
                    title: "stats_avg_trade".localized,
                    value: (stats.avgPnl ?? 0).formattedCurrency,
                    icon: "chart.line.uptrend.xyaxis",
                    color: (stats.avgPnl ?? 0) >= 0 ? .enlikoGreen : .enlikoRed
                )
            } else {
                ForEach(0..<4) { _ in
                    PortfolioStatCard(
                        title: "--",
                        value: "--",
                        icon: "chart.bar.fill",
                        color: .enlikoTextMuted
                    )
                }
            }
        }
    }
    
    // MARK: - PnL Chart Card
    private var pnlChartCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("portfolio_pnl_chart".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Text("portfolio_pnl_week".localized)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            // Simple bar chart placeholder
            if tradingService.tradingStats != nil {
                HStack(alignment: .bottom, spacing: 8) {
                    ForEach(0..<7, id: \.self) { index in
                        RoundedRectangle(cornerRadius: 4)
                            .fill(index % 2 == 0 ? Color.enlikoGreen : Color.enlikoRed)
                            .frame(height: CGFloat.random(in: 30...100))
                    }
                }
                .frame(height: 120)
            } else {
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.enlikoSurface)
                    .frame(height: 120)
                    .overlay(
                        Text("portfolio_no_chart_data".localized)
                            .foregroundColor(.enlikoTextMuted)
                    )
            }
        }
        .padding(16)
        .enlikoCard()
    }
    
    // MARK: - Recent Trades Section
    private var recentTradesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("portfolio_recent_trades".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                NavigationLink("common_all".localized) {
                    TradeHistoryView()
                }
                .font(.subheadline)
                .foregroundColor(.enlikoPrimary)
            }
            
            if tradingService.trades.isEmpty {
                HStack {
                    Spacer()
                    VStack(spacing: 8) {
                        Image(systemName: "doc.text.magnifyingglass")
                            .font(.largeTitle)
                            .foregroundColor(.enlikoTextMuted)
                        Text("portfolio_no_recent_trades".localized)
                            .foregroundColor(.enlikoTextSecondary)
                    }
                    .padding(.vertical, 24)
                    Spacer()
                }
            } else {
                ForEach(tradingService.trades.prefix(5)) { trade in
                    TradeRow(trade: trade)
                }
            }
        }
        .padding(16)
        .enlikoCard()
    }
}

// MARK: - Stat Card
struct PortfolioStatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                Text(value)
                    .font(.headline.bold())
                    .foregroundColor(.white)
            }
            Spacer()
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
        }
        .padding(16)
        .enlikoCard()
    }
}

// MARK: - Trade Row
struct TradeRow: View {
    let trade: Trade
    
    var body: some View {
        HStack {
            // Side indicator
            Circle()
                .fill(trade.side.lowercased() == "buy" ? Color.enlikoGreen : Color.enlikoRed)
                .frame(width: 8, height: 8)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(trade.symbol)
                    .font(.subheadline.weight(.medium))
                    .foregroundColor(.white)
                Text(trade.exitReason ?? trade.side)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text(trade.pnl?.formattedCurrency ?? "--")
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor((trade.pnl ?? 0) >= 0 ? .enlikoGreen : .enlikoRed)
                if let pnlPct = trade.pnlPct {
                    Text(pnlPct.formattedPercent)
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                }
            }
        }
        .padding(.vertical, 8)
    }
}

#Preview {
    PortfolioView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
