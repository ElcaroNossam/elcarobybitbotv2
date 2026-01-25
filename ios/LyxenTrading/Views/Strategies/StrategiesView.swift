//
//  StrategiesView.swift
//  LyxenTrading
//
//  Strategy management and marketplace
//

import SwiftUI

struct StrategiesView: View {
    @EnvironmentObject var tradingService: TradingService
    @StateObject private var strategyService = StrategyService.shared
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.lyxenBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Tab Selector
                    tabSelector
                    
                    TabView(selection: $selectedTab) {
                        myStrategiesTab
                            .tag(0)
                        
                        marketplaceTab
                            .tag(1)
                        
                        backtestTab
                            .tag(2)
                    }
                    .tabViewStyle(.page(indexDisplayMode: .never))
                }
            }
            .navigationTitle("Strategies")
            .navigationBarTitleDisplayMode(.large)
        }
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach(["My Strategies", "Marketplace", "Backtest"].indices, id: \.self) { index in
                let title = ["My Strategies", "Marketplace", "Backtest"][index]
                
                Button(action: { withAnimation { selectedTab = index } }) {
                    VStack(spacing: 8) {
                        Text(title)
                            .font(.subheadline.weight(.medium))
                            .foregroundColor(selectedTab == index ? .white : .lyxenTextSecondary)
                        
                        Rectangle()
                            .fill(selectedTab == index ? Color.lyxenPrimary : Color.clear)
                            .frame(height: 2)
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal)
        .background(Color.lyxenSurface)
    }
    
    // MARK: - My Strategies Tab
    private var myStrategiesTab: some View {
        ScrollView {
            LazyVStack(spacing: 16) {
                ForEach(strategyService.availableStrategies, id: \.self) { strategy in
                    StrategyCard(
                        name: strategy,
                        description: strategyDescription(for: strategy),
                        isEnabled: true,
                        onConfigure: {
                            // Navigate to strategy settings
                        }
                    )
                }
            }
            .padding()
        }
    }
    
    // MARK: - Marketplace Tab
    private var marketplaceTab: some View {
        Group {
            if strategyService.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if strategyService.marketplaceStrategies.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "storefront")
                        .font(.system(size: 60))
                        .foregroundColor(.lyxenTextMuted)
                    
                    Text("Marketplace Coming Soon")
                        .font(.title3.weight(.medium))
                        .foregroundColor(.white)
                    
                    Text("Trade strategies from top performers")
                        .font(.subheadline)
                        .foregroundColor(.lyxenTextSecondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                ScrollView {
                    LazyVStack(spacing: 16) {
                        ForEach(strategyService.marketplaceStrategies) { strategy in
                            MarketplaceStrategyCard(strategy: strategy)
                        }
                    }
                    .padding()
                }
            }
        }
        .task {
            await strategyService.fetchMarketplaceStrategies()
        }
    }
    
    // MARK: - Backtest Tab
    private var backtestTab: some View {
        BacktestView()
    }
    
    // MARK: - Helpers
    private func strategyDescription(for strategy: String) -> String {
        switch strategy.lowercased() {
        case "oi":
            return "Open Interest based signals - tracks large position changes"
        case "scryptomera":
            return "Volume delta analysis with trend confirmation"
        case "scalper":
            return "Quick scalping strategy for high frequency trading"
        case "elcaro":
            return "AI-powered multi-indicator strategy"
        case "fibonacci":
            return "Fibonacci retracement levels with trend analysis"
        case "rsi_bb":
            return "RSI with Bollinger Bands for reversal detection"
        default:
            return "Custom trading strategy"
        }
    }
}

// MARK: - Strategy Card
struct StrategyCard: View {
    let name: String
    let description: String
    let isEnabled: Bool
    let onConfigure: () -> Void
    
    @State private var isToggled: Bool = true
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                // Icon
                ZStack {
                    Circle()
                        .fill(Color.lyxenPrimary.opacity(0.2))
                        .frame(width: 44, height: 44)
                    
                    Image(systemName: strategyIcon)
                        .font(.title3)
                        .foregroundColor(.lyxenPrimary)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(name.uppercased())
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                        .lineLimit(2)
                }
                
                Spacer()
                
                Toggle("", isOn: $isToggled)
                    .toggleStyle(SwitchToggleStyle(tint: .lyxenPrimary))
                    .labelsHidden()
            }
            
            Divider().background(Color.lyxenCardHover)
            
            HStack {
                Button(action: onConfigure) {
                    HStack {
                        Image(systemName: "gearshape.fill")
                        Text("Configure")
                    }
                    .font(.subheadline)
                    .foregroundColor(.lyxenPrimary)
                }
                
                Spacer()
                
                // Status badge
                HStack(spacing: 4) {
                    Circle()
                        .fill(isToggled ? Color.lyxenGreen : Color.lyxenTextMuted)
                        .frame(width: 6, height: 6)
                    Text(isToggled ? "Active" : "Inactive")
                        .font(.caption)
                        .foregroundColor(isToggled ? .lyxenGreen : .lyxenTextMuted)
                }
            }
        }
        .padding()
        .lyxenCard()
    }
    
    private var strategyIcon: String {
        switch name.lowercased() {
        case "oi": return "chart.bar.fill"
        case "scryptomera": return "waveform.path.ecg"
        case "scalper": return "bolt.fill"
        case "elcaro": return "brain"
        case "fibonacci": return "function"
        case "rsi_bb": return "chart.line.uptrend.xyaxis"
        default: return "doc.text.fill"
        }
    }
}

// MARK: - Marketplace Strategy Card
struct MarketplaceStrategyCard: View {
    let strategy: MarketplaceStrategy
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(strategy.name)
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    Text("by \(strategy.author)")
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                }
                
                Spacer()
                
                // Rating
                HStack(spacing: 4) {
                    Image(systemName: "star.fill")
                        .foregroundColor(.lyxenYellow)
                    Text(String(format: "%.1f", strategy.rating))
                        .foregroundColor(.lyxenTextSecondary)
                }
                .font(.subheadline)
            }
            
            Text(strategy.description ?? "No description")
                .font(.subheadline)
                .foregroundColor(.lyxenTextSecondary)
                .lineLimit(3)
            
            Divider().background(Color.lyxenCardHover)
            
            HStack {
                // Stats
                HStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Win Rate")
                            .font(.caption)
                            .foregroundColor(.lyxenTextMuted)
                        Text("\(Int(strategy.winRate * 100))%")
                            .font(.subheadline.bold())
                            .foregroundColor(.lyxenGreen)
                    }
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Monthly PnL")
                            .font(.caption)
                            .foregroundColor(.lyxenTextMuted)
                        Text((strategy.monthlyPnl ?? 0).formattedPercent)
                            .font(.subheadline.bold())
                            .foregroundColor((strategy.monthlyPnl ?? 0) >= 0 ? .lyxenGreen : .lyxenRed)
                    }
                }
                
                Spacer()
                
                // Price/Subscribe
                Button(action: {}) {
                    Text(strategy.price > 0 ? "$\(Int(strategy.price))/mo" : "Free")
                        .font(.subheadline.bold())
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(Color.lyxenPrimary)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
            }
        }
        .padding()
        .lyxenCard()
    }
}

struct ResultMetric: View {
    let label: String
    let value: String
    var color: Color = .white
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(.caption)
                .foregroundColor(.lyxenTextMuted)
            Text(value)
                .font(.headline.bold())
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.lyxenSurface)
        .cornerRadius(8)
    }
}

#Preview {
    StrategiesView()
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
