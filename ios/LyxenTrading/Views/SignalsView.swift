//
//  SignalsView.swift
//  LyxenTrading
//
//  Trading signals view
//

import SwiftUI

struct SignalsView: View {
    @StateObject private var signalsService = SignalsService.shared
    @State private var selectedTab = 0
    @State private var selectedStrategy: String?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Tab Picker
                Picker("", selection: $selectedTab) {
                    Text("Active").tag(0)
                    Text("All").tag(1)
                    Text("Stats").tag(2)
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding()
                
                // Content
                switch selectedTab {
                case 0:
                    ActiveSignalsView(signals: signalsService.activeSignals)
                case 1:
                    AllSignalsView(
                        signals: signalsService.signals,
                        selectedStrategy: $selectedStrategy
                    )
                case 2:
                    SignalStatsView(stats: signalsService.stats)
                default:
                    EmptyView()
                }
            }
            .navigationTitle("Signals")
            .refreshable {
                await signalsService.refreshAll()
            }
            .overlay {
                if signalsService.isLoading && signalsService.signals.isEmpty {
                    ProgressView()
                }
            }
            .task {
                await signalsService.refreshAll()
            }
            .onChange(of: selectedStrategy) { strategy in
                Task {
                    signalsService.selectedStrategy = strategy
                    await signalsService.fetchSignals(strategy: strategy)
                    await signalsService.fetchStats(strategy: strategy)
                }
            }
        }
    }
}

// MARK: - Active Signals View
struct ActiveSignalsView: View {
    let signals: [TradingSignal]
    
    var body: some View {
        if signals.isEmpty {
            VStack(spacing: 12) {
                Image(systemName: "bell.slash")
                    .font(.system(size: 48))
                    .foregroundColor(.secondary)
                Text("No Active Signals")
                    .font(.headline)
                Text("Active trading signals will appear here")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .frame(maxHeight: .infinity)
        } else {
            List(signals) { signal in
                SignalRow(signal: signal)
            }
            .listStyle(PlainListStyle())
        }
    }
}

// MARK: - All Signals View
struct AllSignalsView: View {
    let signals: [TradingSignal]
    @Binding var selectedStrategy: String?
    
    private var strategies: [String] {
        Array(Set(signals.map { $0.strategy })).sorted()
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Strategy Filter
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    FilterButton(
                        title: "All",
                        isSelected: selectedStrategy == nil
                    ) {
                        selectedStrategy = nil
                    }
                    
                    ForEach(strategies, id: \.self) { strategy in
                        FilterButton(
                            title: strategy.capitalized,
                            isSelected: selectedStrategy == strategy
                        ) {
                            selectedStrategy = strategy
                        }
                    }
                }
                .padding(.horizontal)
            }
            .padding(.vertical, 8)
            
            // Signals List
            if signals.isEmpty {
                VStack(spacing: 12) {
                    Image(systemName: "doc.text.magnifyingglass")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("No Signals")
                        .font(.headline)
                }
                .frame(maxHeight: .infinity)
            } else {
                List(signals) { signal in
                    SignalRow(signal: signal)
                }
                .listStyle(PlainListStyle())
            }
        }
    }
}

struct FilterButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.accentColor : Color(.systemGray5))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(16)
        }
    }
}

// MARK: - Signal Row
struct SignalRow: View {
    let signal: TradingSignal
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(signal.sideIcon)
                Text(signal.symbol)
                    .font(.headline)
                
                Text(signal.side)
                    .font(.caption)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(signal.side.lowercased() == "buy" ? Color.green.opacity(0.2) : Color.red.opacity(0.2))
                    .foregroundColor(signal.side.lowercased() == "buy" ? .green : .red)
                    .cornerRadius(4)
                
                Spacer()
                
                Text(signal.statusIcon)
                Text(signal.status.capitalized)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            HStack {
                VStack(alignment: .leading) {
                    Text("Strategy")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text(signal.strategy.capitalized)
                        .font(.caption)
                }
                
                Spacer()
                
                if let entry = signal.entryPrice {
                    VStack(alignment: .center) {
                        Text("Entry")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text(formatPrice(entry))
                            .font(.caption)
                    }
                }
                
                Spacer()
                
                if let tp = signal.takeProfit {
                    VStack(alignment: .center) {
                        Text("TP")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text(formatPrice(tp))
                            .font(.caption)
                            .foregroundColor(.green)
                    }
                }
                
                Spacer()
                
                if let sl = signal.stopLoss {
                    VStack(alignment: .trailing) {
                        Text("SL")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text(formatPrice(sl))
                            .font(.caption)
                            .foregroundColor(.red)
                    }
                }
            }
            
            if let pnl = signal.pnl {
                HStack {
                    Text("PnL:")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "$%.2f", pnl))
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(pnl >= 0 ? .green : .red)
                }
            }
        }
        .padding(.vertical, 4)
    }
    
    private func formatPrice(_ price: Double) -> String {
        if price >= 1000 {
            return String(format: "$%.0f", price)
        } else if price >= 1 {
            return String(format: "$%.2f", price)
        } else {
            return String(format: "$%.4f", price)
        }
    }
}

// MARK: - Signal Stats View
struct SignalStatsView: View {
    let stats: SignalStats?
    
    var body: some View {
        if let stats = stats {
            ScrollView {
                VStack(spacing: 16) {
                    // Overview Cards
                    HStack(spacing: 12) {
                        StatsCard(title: "Total", value: "\(stats.totalSignals)", icon: "chart.bar.fill")
                        StatsCard(title: "Active", value: "\(stats.activeSignals)", icon: "bell.fill", color: .blue)
                    }
                    
                    HStack(spacing: 12) {
                        StatsCard(title: "Executed", value: "\(stats.executedSignals)", icon: "checkmark.circle.fill", color: .green)
                        StatsCard(
                            title: "Win Rate",
                            value: String(format: "%.1f%%", stats.winRate),
                            icon: "percent",
                            color: stats.winRate >= 50 ? .green : .red
                        )
                    }
                    
                    HStack(spacing: 12) {
                        StatsCard(
                            title: "Total PnL",
                            value: String(format: "$%.2f", stats.totalPnl),
                            icon: "dollarsign.circle.fill",
                            color: stats.totalPnl >= 0 ? .green : .red
                        )
                        StatsCard(
                            title: "Avg PnL",
                            value: String(format: "$%.2f", stats.avgPnlPerSignal),
                            icon: "chart.line.uptrend.xyaxis",
                            color: stats.avgPnlPerSignal >= 0 ? .green : .red
                        )
                    }
                }
                .padding()
            }
        } else {
            VStack(spacing: 12) {
                ProgressView()
                Text("Loading stats...")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .frame(maxHeight: .infinity)
        }
    }
}

struct StatsCard: View {
    let title: String
    let value: String
    let icon: String
    var color: Color = .accentColor
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

#Preview {
    SignalsView()
}
