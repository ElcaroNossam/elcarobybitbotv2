//
//  StatsView.swift
//  EnlikoTrading
//
//  Trading statistics dashboard view with localization
//

import SwiftUI

struct StatsView: View {
    @ObservedObject private var stats = StatsService.shared
    @EnvironmentObject private var appState: AppState
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 16) {
                    // Period Picker
                    PeriodPicker(selectedPeriod: $stats.selectedPeriod) {
                        Task {
                            await stats.fetchPnlHistory(
                                period: stats.selectedPeriod,
                                accountType: appState.currentAccountType.rawValue,
                                exchange: appState.currentExchange.rawValue
                            )
                        }
                    }
                    
                    // Dashboard Cards
                    if let dashboard = stats.dashboard {
                        DashboardCards(dashboard: dashboard)
                    }
                    
                    // PnL Chart
                    if !stats.pnlHistory.isEmpty {
                        PnLChartCard(history: stats.pnlHistory)
                    }
                    
                    // Strategy Performance
                    if !stats.strategyReports.isEmpty {
                        StrategyPerformanceCard(reports: stats.strategyReports)
                    }
                    
                    // Positions Summary
                    if let summary = stats.positionsSummary {
                        PositionsSummaryCard(summary: summary)
                    }
                }
                .padding()
            }
            .navigationTitle("stats_title".localized)
            .withRTLSupport()
            .refreshable {
                await stats.refreshAll(accountType: appState.currentAccountType.rawValue, exchange: appState.currentExchange.rawValue)
            }
            .overlay {
                if stats.isLoading && stats.dashboard == nil {
                    ProgressView()
                }
            }
            .task {
                await stats.refreshAll(accountType: appState.currentAccountType.rawValue, exchange: appState.currentExchange.rawValue)
            }
            .onChange(of: appState.currentExchange) { _, newValue in
                Task {
                    await stats.refreshAll(accountType: appState.currentAccountType.rawValue, exchange: newValue.rawValue)
                }
            }
            .onChange(of: appState.currentAccountType) { _, newValue in
                Task {
                    await stats.refreshAll(accountType: newValue.rawValue, exchange: appState.currentExchange.rawValue)
                }
            }
        }
    }
}

// MARK: - Period Picker
struct PeriodPicker: View {
    @Binding var selectedPeriod: StatsService.StatsPeriod
    let onChange: () -> Void
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(StatsService.StatsPeriod.allCases, id: \.self) { period in
                    Button {
                        selectedPeriod = period
                        onChange()
                    } label: {
                        Text(period.displayName)
                            .font(.caption)
                            .fontWeight(selectedPeriod == period ? .semibold : .regular)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(selectedPeriod == period ? Color.accentColor : Color(.systemGray5))
                            .foregroundColor(selectedPeriod == period ? .white : .primary)
                            .cornerRadius(16)
                    }
                }
            }
        }
    }
}

// MARK: - Dashboard Cards
struct DashboardCards: View {
    let dashboard: DashboardStats
    
    var body: some View {
        VStack(spacing: 12) {
            // PnL Summary
            HStack(spacing: 12) {
                StatCard(
                    title: "Total PnL",
                    value: formatCurrency(dashboard.totalPnl),
                    color: dashboard.totalPnl >= 0 ? .green : .red
                )
                StatCard(
                    title: "Today",
                    value: formatCurrency(dashboard.todayPnl),
                    color: dashboard.todayPnl >= 0 ? .green : .red
                )
            }
            
            HStack(spacing: 12) {
                StatCard(
                    title: "Week",
                    value: formatCurrency(dashboard.weekPnl),
                    color: dashboard.weekPnl >= 0 ? .green : .red
                )
                StatCard(
                    title: "Month",
                    value: formatCurrency(dashboard.monthPnl),
                    color: dashboard.monthPnl >= 0 ? .green : .red
                )
            }
            
            // Trading Stats
            HStack(spacing: 12) {
                StatCard(
                    title: "Total Trades",
                    value: "\(dashboard.totalTrades)"
                )
                StatCard(
                    title: "Win Rate",
                    value: String(format: "%.1f%%", dashboard.winRate),
                    color: dashboard.winRate >= 50 ? .green : .red
                )
            }
            
            HStack(spacing: 12) {
                StatCard(
                    title: "Avg Profit",
                    value: formatCurrency(dashboard.avgProfit),
                    color: .green
                )
                StatCard(
                    title: "Avg Loss",
                    value: formatCurrency(dashboard.avgLoss),
                    color: .red
                )
            }
            
            // Best/Worst Trade
            HStack(spacing: 12) {
                StatCard(
                    title: "Best Trade",
                    value: formatCurrency(dashboard.bestTrade),
                    color: .green
                )
                StatCard(
                    title: "Worst Trade",
                    value: formatCurrency(dashboard.worstTrade),
                    color: .red
                )
            }
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

struct StatCard: View {
    let title: String
    let value: String
    var color: Color = .primary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.headline)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

// MARK: - PnL Chart Card
struct PnLChartCard: View {
    let history: [PnlHistoryPoint]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("PnL History")
                .font(.headline)
            
            // Simple bar chart
            GeometryReader { geometry in
                let maxPnl = history.map { abs($0.pnl) }.max() ?? 1
                let barWidth = geometry.size.width / CGFloat(history.count) - 2
                
                HStack(alignment: .bottom, spacing: 2) {
                    ForEach(history) { point in
                        VStack {
                            Rectangle()
                                .fill(point.pnl >= 0 ? Color.green : Color.red)
                                .frame(
                                    width: barWidth,
                                    height: max(4, CGFloat(abs(point.pnl) / maxPnl) * (geometry.size.height - 20))
                                )
                        }
                    }
                }
            }
            .frame(height: 100)
            
            // Legend
            HStack {
                ForEach(history.prefix(3)) { point in
                    VStack(alignment: .leading) {
                        Text(point.date)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text(String(format: "$%.0f", point.pnl))
                            .font(.caption)
                            .foregroundColor(point.pnl >= 0 ? .green : .red)
                    }
                    if point.id != history.prefix(3).last?.id {
                        Spacer()
                    }
                }
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
}

// MARK: - Strategy Performance Card
struct StrategyPerformanceCard: View {
    let reports: [StrategyReport]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Strategy Performance")
                .font(.headline)
            
            ForEach(reports) { report in
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(report.strategy.capitalized)
                            .font(.subheadline)
                            .fontWeight(.medium)
                        Text("\(report.totalTrades) trades")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 4) {
                        Text(String(format: "$%.2f", report.totalPnl))
                            .font(.subheadline)
                            .foregroundColor(report.totalPnl >= 0 ? .green : .red)
                        Text(String(format: "%.1f%% WR", report.winRate ?? 0))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.vertical, 4)
                
                if report.id != reports.last?.id {
                    Divider()
                }
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
}

// MARK: - Positions Summary Card
struct PositionsSummaryCard: View {
    let summary: PositionsSummary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Active Positions")
                .font(.headline)
            
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("common_total".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(summary.totalPositions)")
                        .font(.title2)
                        .fontWeight(.bold)
                }
                
                Spacer()
                
                VStack(alignment: .center, spacing: 4) {
                    Text("Long")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(summary.longPositions)")
                        .font(.title3)
                        .foregroundColor(.green)
                }
                
                Spacer()
                
                VStack(alignment: .center, spacing: 4) {
                    Text("Short")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(summary.shortPositions)")
                        .font(.title3)
                        .foregroundColor(.red)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text("Unrealized")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "$%.2f", summary.totalUnrealizedPnl))
                        .font(.title3)
                        .foregroundColor(summary.totalUnrealizedPnl >= 0 ? .green : .red)
                }
            }
            
            Divider()
            
            HStack {
                Text("Avg Leverage: \(String(format: "%.1fx", summary.avgLeverage))")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Text("Total Margin: $\(String(format: "%.2f", summary.totalMargin))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
}

#Preview {
    StatsView()
        .environmentObject(AppState.shared)
}
