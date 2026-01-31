//
//  ModernPortfolioView.swift
//  EnlikoTrading
//
//  Sleek modern portfolio dashboard with glass morphism
//  Professional trading interface - 2026 Design
//

import SwiftUI

struct ModernPortfolioView: View {
    @StateObject private var tradingService = TradingService.shared
    @StateObject private var appState = AppState.shared
    @State private var isRefreshing = false
    @State private var showAccountPicker = false
    @State private var selectedTimeframe: Timeframe = .day
    
    enum Timeframe: String, CaseIterable {
        case hour = "1H"
        case day = "24H"
        case week = "7D"
        case month = "30D"
    }
    
    var body: some View {
        ZStack {
            // Background
            backgroundGradient
            
            ScrollView(.vertical, showsIndicators: false) {
                VStack(spacing: 24) {
                    // Header
                    headerSection
                    
                    // Main Balance Card
                    balanceCard
                    
                    // Quick Stats
                    quickStatsGrid
                    
                    // PnL Chart
                    pnlChartSection
                    
                    // Recent Activity
                    recentActivitySection
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 100)
            }
            .refreshable {
                await refreshData()
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            Task { await refreshData() }
        }
    }
    
    // MARK: - Background
    private var backgroundGradient: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            // Ambient glow
            Circle()
                .fill(Color.enlikoPrimary.opacity(0.1))
                .frame(width: 300, height: 300)
                .blur(radius: 100)
                .offset(x: -100, y: -200)
            
            Circle()
                .fill(Color.enlikoAccent.opacity(0.08))
                .frame(width: 250, height: 250)
                .blur(radius: 80)
                .offset(x: 150, y: 100)
        }
    }
    
    // MARK: - Header
    private var headerSection: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("portfolio".localized)
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.white)
                
                Text(exchangeLabel)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            // Account Switcher
            Button(action: { showAccountPicker = true }) {
                HStack(spacing: 6) {
                    Circle()
                        .fill(appState.currentExchange == .bybit ? Color.orange : Color.blue)
                        .frame(width: 8, height: 8)
                    
                    Text(accountLabel)
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white)
                    
                    Image(systemName: "chevron.down")
                        .font(.system(size: 10, weight: .bold))
                        .foregroundColor(.enlikoTextSecondary)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(
                    Capsule()
                        .fill(Color.enlikoCard)
                        .overlay(
                            Capsule()
                                .stroke(Color.enlikoBorder, lineWidth: 1)
                        )
                )
            }
        }
        .padding(.top, 16)
    }
    
    private var exchangeLabel: String {
        appState.currentExchange == .bybit ? "Bybit" : "HyperLiquid"
    }
    
    private var accountLabel: String {
        switch appState.currentAccountType {
        case .demo: return "Demo"
        case .real: return "Real"
        case .testnet: return "Testnet"
        case .mainnet: return "Mainnet"
        }
    }
    
    // MARK: - Balance Card
    private var balanceCard: some View {
        VStack(spacing: 20) {
            // Equity
            VStack(spacing: 8) {
                Text("total_equity".localized)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
                
                if isRefreshing {
                    SkeletonView(width: 180, height: 40, cornerRadius: 8)
                } else {
                    AnimatedCounter(
                        value: tradingService.balance?.displayEquity ?? 0,
                        prefix: "$",
                        suffix: "",
                        font: .system(size: 42, weight: .bold, design: .rounded),
                        color: .white
                    )
                }
            }
            
            // Unrealized PnL
            if let unrealizedPnl = tradingService.balance?.displayUnrealizedPnl, unrealizedPnl != 0 {
                HStack(spacing: 6) {
                    Image(systemName: unrealizedPnl >= 0 ? "arrow.up.right.circle.fill" : "arrow.down.right.circle.fill")
                        .font(.system(size: 16))
                    
                    Text(unrealizedPnl >= 0 ? "+$\(unrealizedPnl, specifier: "%.2f")" : "-$\(abs(unrealizedPnl), specifier: "%.2f")")
                        .font(.system(size: 18, weight: .bold))
                    
                    Text("unrealized".localized)
                        .font(.system(size: 12, weight: .medium))
                        .opacity(0.7)
                }
                .foregroundColor(unrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(
                    Capsule()
                        .fill((unrealizedPnl >= 0 ? Color.enlikoGreen : Color.enlikoRed).opacity(0.15))
                )
            }
            
            Divider()
                .background(Color.enlikoBorder)
            
            // Balance Details
            HStack(spacing: 0) {
                balanceDetailItem(
                    title: "available".localized,
                    value: tradingService.balance?.displayAvailable ?? 0,
                    icon: "wallet.pass.fill"
                )
                
                Rectangle()
                    .fill(Color.enlikoBorder)
                    .frame(width: 1, height: 50)
                
                balanceDetailItem(
                    title: "margin_used".localized,
                    value: tradingService.balance?.displayPositionMargin ?? 0,
                    icon: "lock.fill"
                )
            }
        }
        .padding(24)
        .background(
            ZStack {
                RoundedRectangle(cornerRadius: 24)
                    .fill(Color.enlikoCard)
                
                // Glow effect
                RoundedRectangle(cornerRadius: 24)
                    .fill(
                        LinearGradient(
                            colors: [
                                Color.enlikoPrimary.opacity(0.1),
                                Color.clear
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                
                // Border
                RoundedRectangle(cornerRadius: 24)
                    .stroke(
                        LinearGradient(
                            colors: [
                                Color.white.opacity(0.2),
                                Color.white.opacity(0.05)
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 1
                    )
            }
        )
    }
    
    private func balanceDetailItem(title: String, value: Double, icon: String) -> some View {
        VStack(spacing: 6) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 12))
                    .foregroundColor(.enlikoTextSecondary)
                
                Text(title)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Text("$\(value, specifier: "%.2f")")
                .font(.system(size: 18, weight: .bold, design: .rounded))
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - Quick Stats Grid
    private var quickStatsGrid: some View {
        LazyVGrid(columns: [
            GridItem(.flexible(), spacing: 12),
            GridItem(.flexible(), spacing: 12)
        ], spacing: 12) {
            StatTile(
                title: "positions".localized,
                value: "\(tradingService.positions.count)",
                icon: "chart.bar.fill",
                iconColor: .enlikoPrimary
            )
            
            StatTile(
                title: "24h_pnl".localized,
                value: tradingService.balance?.displayTodayPnl.formattedCurrency ?? "$0.00",
                icon: "chart.line.uptrend.xyaxis",
                iconColor: (tradingService.balance?.displayTodayPnl ?? 0) >= 0 ? .enlikoGreen : .enlikoRed,
                trend: calculateTrend()
            )
            
            StatTile(
                title: "win_rate".localized,
                value: "\(Int(tradingService.balance?.winRate ?? 58))%",
                icon: "trophy.fill",
                iconColor: .yellow
            )
            
            StatTile(
                title: "total_trades".localized,
                value: "\(tradingService.balance?.totalTrades ?? 0)",
                icon: "arrow.left.arrow.right",
                iconColor: .enlikoAccent
            )
        }
    }
    
    private func calculateTrend() -> Double? {
        let pnl = tradingService.balance?.displayTodayPnl ?? 0
        let equity = tradingService.balance?.displayEquity ?? 1
        guard equity > 0 else { return nil }
        return (pnl / equity) * 100
    }
    
    // MARK: - PnL Chart Section
    private var pnlChartSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("pnl_history".localized)
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
                
                Spacer()
                
                // Timeframe Picker
                HStack(spacing: 4) {
                    ForEach(Timeframe.allCases, id: \.self) { timeframe in
                        Button(action: { selectedTimeframe = timeframe }) {
                            Text(timeframe.rawValue)
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(selectedTimeframe == timeframe ? .white : .enlikoTextSecondary)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(
                                    selectedTimeframe == timeframe ?
                                    RoundedRectangle(cornerRadius: 8).fill(Color.enlikoPrimary) :
                                    RoundedRectangle(cornerRadius: 8).fill(Color.clear)
                                )
                        }
                    }
                }
                .padding(4)
                .background(
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.enlikoCard)
                )
            }
            
            // Chart Placeholder
            ZStack {
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.enlikoCard)
                    .frame(height: 180)
                
                // Simulated chart
                GeometryReader { geometry in
                    Path { path in
                        let width = geometry.size.width
                        let height = geometry.size.height
                        let points = generateChartPoints(width: width, height: height)
                        
                        guard let first = points.first else { return }
                        path.move(to: first)
                        
                        for point in points.dropFirst() {
                            path.addLine(to: point)
                        }
                    }
                    .stroke(
                        LinearGradient(
                            colors: [.enlikoGreen, .enlikoGreen.opacity(0.5)],
                            startPoint: .leading,
                            endPoint: .trailing
                        ),
                        style: StrokeStyle(lineWidth: 2, lineCap: .round, lineJoin: .round)
                    )
                    
                    // Gradient fill under chart
                    Path { path in
                        let width = geometry.size.width
                        let height = geometry.size.height
                        let points = generateChartPoints(width: width, height: height)
                        
                        guard let first = points.first else { return }
                        path.move(to: CGPoint(x: 0, y: height))
                        path.addLine(to: first)
                        
                        for point in points.dropFirst() {
                            path.addLine(to: point)
                        }
                        
                        path.addLine(to: CGPoint(x: width, y: height))
                        path.closeSubpath()
                    }
                    .fill(
                        LinearGradient(
                            colors: [.enlikoGreen.opacity(0.3), .clear],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                }
                .padding(16)
            }
            .frame(height: 180)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.enlikoSurface)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.enlikoBorder, lineWidth: 1)
                )
        )
    }
    
    private func generateChartPoints(width: CGFloat, height: CGFloat) -> [CGPoint] {
        let count = 20
        var points: [CGPoint] = []
        
        for i in 0..<count {
            let x = (width / CGFloat(count - 1)) * CGFloat(i)
            let randomVariation = CGFloat.random(in: -0.2...0.2)
            let trend = CGFloat(i) / CGFloat(count) * 0.3
            let y = height * (0.5 - trend + randomVariation)
            points.append(CGPoint(x: x, y: max(20, min(height - 20, y))))
        }
        
        return points
    }
    
    // MARK: - Recent Activity
    private var recentActivitySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("recent_activity".localized)
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
                
                Spacer()
                
                NavigationLink(destination: TradeHistoryView()) {
                    Text("view_all".localized)
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.enlikoPrimary)
                }
            }
            
            if tradingService.positions.isEmpty {
                emptyActivityState
            } else {
                ForEach(tradingService.positions.prefix(3)) { position in
                    activityRow(position: position)
                }
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.enlikoSurface)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.enlikoBorder, lineWidth: 1)
                )
        )
    }
    
    private var emptyActivityState: some View {
        VStack(spacing: 12) {
            Image(systemName: "chart.bar.doc.horizontal")
                .font(.system(size: 40))
                .foregroundColor(.enlikoTextSecondary.opacity(0.5))
            
            Text("no_positions".localized)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.enlikoTextSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 32)
    }
    
    private func activityRow(position: Position) -> some View {
        HStack(spacing: 12) {
            // Side indicator
            ZStack {
                Circle()
                    .fill(position.isLong ? Color.enlikoGreen.opacity(0.2) : Color.enlikoRed.opacity(0.2))
                    .frame(width: 40, height: 40)
                
                Image(systemName: position.isLong ? "arrow.up.right" : "arrow.down.right")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(position.isLong ? .enlikoGreen : .enlikoRed)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(position.displaySymbol)
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundColor(.white)
                
                Text("\(position.displayLeverage)x • \(position.isLong ? "Long" : "Short")")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text(position.displayPnl.formattedCurrency)
                    .font(.system(size: 15, weight: .bold))
                    .foregroundColor(position.displayPnl >= 0 ? .enlikoGreen : .enlikoRed)
                
                Text("\(position.displayPnlPercent, specifier: "%.2f")%")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(position.displayPnlPercent >= 0 ? .enlikoGreen : .enlikoRed)
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.enlikoCard)
        )
    }
    
    // MARK: - Actions
    private func refreshData() async {
        isRefreshing = true
        await tradingService.refreshAll()
        isRefreshing = false
    }
}

// MARK: - Preview
#Preview {
    NavigationStack {
        ModernPortfolioView()
    }
}
