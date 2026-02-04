//
//  SpotTradingView.swift
//  EnlikoTrading
//
//  Comprehensive Spot Trading interface with portfolios, DCA, and performance
//

import SwiftUI

struct SpotTradingView: View {
    @StateObject private var spotService = SpotService.shared
    @EnvironmentObject var appState: AppState
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var selectedTab = 0
    @State private var showBuySheet = false
    @State private var showSellSheet = false
    @State private var showSettingsSheet = false
    @State private var showRebalanceSheet = false
    @State private var selectedCoin = ""
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Tab Picker
                Picker("", selection: $selectedTab) {
                    Text("💰 " + "spot_portfolio".localized).tag(0)
                    Text("📈 DCA").tag(1)
                    Text("⚙️ " + "settings".localized).tag(2)
                }
                .pickerStyle(.segmented)
                .padding()
                
                TabView(selection: $selectedTab) {
                    // Portfolio Tab
                    SpotPortfolioTab(
                        spotService: spotService,
                        showBuySheet: $showBuySheet,
                        showSellSheet: $showSellSheet,
                        selectedCoin: $selectedCoin
                    )
                    .tag(0)
                    
                    // DCA Tab
                    SpotDCATab(spotService: spotService)
                    .tag(1)
                    
                    // Settings Tab
                    SpotSettingsTab(
                        spotService: spotService,
                        showRebalanceSheet: $showRebalanceSheet
                    )
                    .tag(2)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
            }
            .navigationTitle("spot_trading".localized)
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { Task { await refresh() } }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .onAppear {
                Task {
                    await spotService.fetchPerformance(accountType: appState.currentAccountType.rawValue)
                    await spotService.fetchBalance(accountType: appState.currentAccountType.rawValue)
                    await spotService.fetchFearGreed()
                }
            }
            .sheet(isPresented: $showBuySheet) {
                SpotBuySheet(spotService: spotService, accountType: appState.currentAccountType.rawValue)
            }
            .sheet(isPresented: $showSellSheet) {
                SpotSellSheet(spotService: spotService, coin: selectedCoin, accountType: appState.currentAccountType.rawValue)
            }
            .sheet(isPresented: $showRebalanceSheet) {
                SpotRebalanceSheet(spotService: spotService, accountType: appState.currentAccountType.rawValue)
            }
        }
    }
    
    private func refresh() async {
        await spotService.fetchPerformance(accountType: appState.currentAccountType.rawValue)
        await spotService.fetchBalance(accountType: appState.currentAccountType.rawValue)
        await spotService.fetchFearGreed()
    }
}

// MARK: - Portfolio Tab

struct SpotPortfolioTab: View {
    @ObservedObject var spotService: SpotService
    @Binding var showBuySheet: Bool
    @Binding var showSellSheet: Bool
    @Binding var selectedCoin: String
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Performance Card
                if let perf = spotService.performance {
                    SpotPerformanceCard(performance: perf)
                }
                
                // Fear & Greed Index
                if let fg = spotService.fearGreed, fg.success {
                    FearGreedCard(fearGreed: fg)
                }
                
                // Holdings
                if let perf = spotService.performance, !perf.holdings.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("📦 " + "spot_holdings".localized)
                                .font(.headline)
                            Spacer()
                            Button(action: { showBuySheet = true }) {
                                Label("Buy", systemImage: "plus.circle.fill")
                                    .foregroundColor(.enlikoGreen)
                            }
                        }
                        
                        ForEach(perf.holdings) { holding in
                            SpotHoldingCard(holding: holding) {
                                selectedCoin = holding.coin
                                showSellSheet = true
                            }
                        }
                    }
                    .padding()
                    .background(Color.enlikoCard)
                    .cornerRadius(16)
                } else {
                    EmptyHoldingsView(onBuy: { showBuySheet = true })
                }
            }
            .padding()
        }
        .refreshable {
            await spotService.fetchPerformance()
        }
    }
}

// MARK: - DCA Tab

struct SpotDCATab: View {
    @ObservedObject var spotService: SpotService
    @State private var selectedStrategy = "fixed"
    @State private var dcaAmount: String = "10"
    @State private var selectedCoin = "BTC"
    @State private var isExecuting = false
    
    let coins = ["BTC", "ETH", "SOL", "BNB", "AVAX", "MATIC", "LINK", "UNI", "AAVE"]
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                // DCA Strategies
                VStack(alignment: .leading, spacing: 12) {
                    Text("🎯 " + "spot_dca_strategy".localized)
                        .font(.headline)
                    
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        DCAStrategyButton(
                            emoji: "📊", name: "Fixed", description: "Same amount",
                            isSelected: selectedStrategy == "fixed",
                            action: { selectedStrategy = "fixed" }
                        )
                        DCAStrategyButton(
                            emoji: "📈", name: "Value Avg", description: "Buy dips more",
                            isSelected: selectedStrategy == "value_avg",
                            action: { selectedStrategy = "value_avg" }
                        )
                        DCAStrategyButton(
                            emoji: "😱", name: "Fear/Greed", description: "Fear = Buy more",
                            isSelected: selectedStrategy == "fear_greed",
                            action: { selectedStrategy = "fear_greed" }
                        )
                        DCAStrategyButton(
                            emoji: "🚨", name: "Crash Boost", description: "3x on -15%",
                            isSelected: selectedStrategy == "crash_boost",
                            action: { selectedStrategy = "crash_boost" }
                        )
                        DCAStrategyButton(
                            emoji: "🚀", name: "Momentum", description: "Follow trend",
                            isSelected: selectedStrategy == "momentum",
                            action: { selectedStrategy = "momentum" }
                        )
                        DCAStrategyButton(
                            emoji: "📐", name: "RSI Smart", description: "RSI < 30 buy",
                            isSelected: selectedStrategy == "rsi_based",
                            action: { selectedStrategy = "rsi_based" }
                        )
                    }
                }
                .padding()
                .background(Color.enlikoCard)
                .cornerRadius(16)
                
                // Quick DCA Execute
                VStack(alignment: .leading, spacing: 12) {
                    Text("⚡ " + "quick_dca".localized)
                        .font(.headline)
                    
                    HStack {
                        // Coin Picker
                        Picker("Coin", selection: $selectedCoin) {
                            ForEach(coins, id: \.self) { coin in
                                Text(coin).tag(coin)
                            }
                        }
                        .pickerStyle(.menu)
                        .frame(width: 100)
                        
                        // Amount
                        TextField("Amount", text: $dcaAmount)
                            .keyboardType(.decimalPad)
                            .textFieldStyle(.roundedBorder)
                        
                        Text("USDT")
                            .foregroundColor(.secondary)
                    }
                    
                    Button(action: executeDCA) {
                        HStack {
                            if isExecuting {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Image(systemName: "arrow.down.circle.fill")
                            }
                            Text("Execute DCA")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.enlikoGreen)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .disabled(isExecuting)
                }
                .padding()
                .background(Color.enlikoCard)
                .cornerRadius(16)
                
                // Fear & Greed for context
                if let fg = spotService.fearGreed, fg.success {
                    HStack {
                        Text("Current Fear & Greed:")
                        Spacer()
                        Text("\(fg.value ?? 50)")
                            .fontWeight(.bold)
                            .foregroundColor(fearGreedColor(fg.value ?? 50))
                        Text(fg.classification ?? "Neutral")
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color.enlikoCard)
                    .cornerRadius(12)
                }
            }
            .padding()
        }
    }
    
    private func executeDCA() {
        guard let amount = Double(dcaAmount), amount >= 5 else { return }
        isExecuting = true
        
        Task {
            let success = await spotService.executeDCA(
                coin: selectedCoin,
                amount: amount,
                strategy: selectedStrategy
            )
            await MainActor.run {
                isExecuting = false
                if success {
                    HapticManager.shared.perform(.success)
                }
            }
        }
    }
    
    private func fearGreedColor(_ value: Int) -> Color {
        switch value {
        case 0..<25: return .red
        case 25..<45: return .orange
        case 45..<55: return .gray
        case 55..<75: return .green
        default: return .enlikoGreen
        }
    }
}

// MARK: - Settings Tab

struct SpotSettingsTab: View {
    @ObservedObject var spotService: SpotService
    @Binding var showRebalanceSheet: Bool
    
    @State private var dcaEnabled = false
    @State private var tpEnabled = false
    @State private var trailingEnabled = false
    @State private var profitLockEnabled = false
    @State private var rebalanceEnabled = false
    @State private var selectedPortfolio = "custom"
    @State private var selectedTPProfile = "balanced"
    
    var body: some View {
        Form {
            // Portfolio Selection
            Section(header: Text("📊 " + "spot_portfolio".localized)) {
                Picker("Portfolio", selection: $selectedPortfolio) {
                    Text("💎 Blue Chips").tag("blue_chip")
                    Text("🏦 DeFi").tag("defi")
                    Text("⚡ Layer 2").tag("layer2")
                    Text("🤖 AI & Data").tag("ai_narrative")
                    Text("🎮 Gaming").tag("gaming")
                    Text("🐕 Memecoins").tag("meme")
                    Text("⚔️ L1 Killers").tag("l1_killers")
                    Text("🏛️ RWA").tag("rwa")
                    Text("🔧 Infrastructure").tag("infrastructure")
                    Text("₿ BTC Only").tag("btc_only")
                    Text("💰 ETH+BTC").tag("eth_btc")
                    Text("⚙️ Custom").tag("custom")
                }
                
                Button(action: { showRebalanceSheet = true }) {
                    Label("Rebalance Now", systemImage: "arrow.triangle.2.circlepath")
                }
            }
            
            // Auto DCA
            Section(header: Text("📈 Auto DCA")) {
                Toggle("Enable Auto DCA", isOn: $dcaEnabled)
                
                if dcaEnabled {
                    Picker("Strategy", selection: .constant("fixed")) {
                        Text("📊 Fixed").tag("fixed")
                        Text("📈 Value Averaging").tag("value_avg")
                        Text("😱 Fear & Greed").tag("fear_greed")
                        Text("🚨 Crash Boost").tag("crash_boost")
                    }
                    
                    Picker("Frequency", selection: .constant("daily")) {
                        Text("⏰ Hourly").tag("hourly")
                        Text("📅 Daily").tag("daily")
                        Text("📆 Weekly").tag("weekly")
                    }
                }
            }
            
            // Take Profit
            Section(header: Text("🎯 Take Profit")) {
                Toggle("Enable TP Levels", isOn: $tpEnabled)
                
                if tpEnabled {
                    Picker("TP Profile", selection: $selectedTPProfile) {
                        Text("🐢 Conservative").tag("conservative")
                        Text("⚖️ Balanced").tag("balanced")
                        Text("🦁 Aggressive").tag("aggressive")
                        Text("🌙 Moonbag").tag("moonbag")
                    }
                }
                
                Toggle("Trailing TP", isOn: $trailingEnabled)
            }
            
            // Advanced Features
            Section(header: Text("⚙️ Advanced")) {
                Toggle("🔒 Profit Lock", isOn: $profitLockEnabled)
                if profitLockEnabled {
                    Text("Sell 50% when +30% profit")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Toggle("⚖️ Auto Rebalance", isOn: $rebalanceEnabled)
                if rebalanceEnabled {
                    Text("Rebalance when >10% drift")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct SpotPerformanceCard: View {
    let performance: SpotPerformance
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Text("📊 " + "spot_performance".localized)
                    .font(.headline)
                Spacer()
            }
            
            HStack {
                VStack(alignment: .leading) {
                    Text("Invested")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("$\(performance.totalInvested, specifier: "%.2f")")
                        .font(.title3)
                        .fontWeight(.semibold)
                }
                
                Spacer()
                
                VStack(alignment: .trailing) {
                    Text("Current Value")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("$\(performance.totalCurrentValue, specifier: "%.2f")")
                        .font(.title3)
                        .fontWeight(.semibold)
                }
            }
            
            Divider()
            
            HStack {
                Text("Unrealized PnL")
                    .foregroundColor(.secondary)
                Spacer()
                Text("\(performance.totalUnrealizedPnl >= 0 ? "+" : "")$\(performance.totalUnrealizedPnl, specifier: "%.2f")")
                    .foregroundColor(performance.totalUnrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
                Text("(\(performance.roiPct >= 0 ? "+" : "")\(performance.roiPct, specifier: "%.1f")%)")
                    .foregroundColor(performance.roiPct >= 0 ? .enlikoGreen : .enlikoRed)
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
}

struct FearGreedCard: View {
    let fearGreed: FearGreedIndex
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text("Fear & Greed Index")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                Text(fearGreed.classification ?? "Neutral")
                    .font(.headline)
            }
            
            Spacer()
            
            ZStack {
                Circle()
                    .stroke(lineWidth: 6)
                    .opacity(0.3)
                    .foregroundColor(fearGreedColor)
                
                Circle()
                    .trim(from: 0, to: CGFloat(fearGreed.value ?? 50) / 100)
                    .stroke(style: StrokeStyle(lineWidth: 6, lineCap: .round))
                    .foregroundColor(fearGreedColor)
                    .rotationEffect(.degrees(-90))
                
                Text("\(fearGreed.value ?? 50)")
                    .font(.title2)
                    .fontWeight(.bold)
            }
            .frame(width: 60, height: 60)
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    var fearGreedColor: Color {
        let value = fearGreed.value ?? 50
        switch value {
        case 0..<25: return .red
        case 25..<45: return .orange
        case 45..<55: return .gray
        case 55..<75: return .green
        default: return .enlikoGreen
        }
    }
}

struct SpotHoldingCard: View {
    let holding: SpotHolding
    let onSell: () -> Void
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(holding.coin)
                    .font(.headline)
                Text("\(holding.balance, specifier: "%.6f")")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("$\(holding.usdValue, specifier: "%.2f")")
                    .font(.headline)
                HStack(spacing: 4) {
                    Text("\(holding.pnlPct >= 0 ? "+" : "")\(holding.pnlPct, specifier: "%.1f")%")
                        .font(.caption)
                        .foregroundColor(holding.pnlPct >= 0 ? .enlikoGreen : .enlikoRed)
                    Text("$\(holding.unrealizedPnl, specifier: "%.2f")")
                        .font(.caption)
                        .foregroundColor(holding.unrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
                }
            }
            
            Button(action: onSell) {
                Image(systemName: "minus.circle.fill")
                    .foregroundColor(.enlikoRed)
                    .font(.title2)
            }
        }
        .padding(.vertical, 8)
    }
}

struct DCAStrategyButton: View {
    let emoji: String
    let name: String
    let description: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Text(emoji)
                    .font(.title2)
                Text(name)
                    .font(.caption)
                    .fontWeight(.semibold)
                Text(description)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(isSelected ? Color.enlikoPrimary.opacity(0.2) : Color.enlikoCard)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isSelected ? Color.enlikoPrimary : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(.plain)
    }
}

struct EmptyHoldingsView: View {
    let onBuy: () -> Void
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "tray")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            
            Text("No Spot Holdings")
                .font(.headline)
            
            Text("Start building your portfolio with DCA")
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            Button(action: onBuy) {
                Label("Buy Crypto", systemImage: "plus.circle.fill")
                    .padding()
                    .background(Color.enlikoGreen)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(32)
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
}

// MARK: - Sheets

struct SpotBuySheet: View {
    @ObservedObject var spotService: SpotService
    let accountType: String
    @Environment(\.dismiss) var dismiss
    
    @State private var selectedCoin = "BTC"
    @State private var amount = ""
    @State private var isLoading = false
    
    let coins = ["BTC", "ETH", "SOL", "BNB", "AVAX", "MATIC", "LINK", "UNI", "AAVE", "DOGE", "SHIB"]
    
    var body: some View {
        NavigationStack {
            Form {
                Section(header: Text("Select Coin")) {
                    Picker("Coin", selection: $selectedCoin) {
                        ForEach(coins, id: \.self) { coin in
                            Text(coin).tag(coin)
                        }
                    }
                    .pickerStyle(.wheel)
                }
                
                Section(header: Text("Amount (USDT)")) {
                    TextField("Enter amount", text: $amount)
                        .keyboardType(.decimalPad)
                    
                    HStack {
                        ForEach([10, 25, 50, 100], id: \.self) { value in
                            Button("$\(value)") {
                                amount = "\(value)"
                            }
                            .buttonStyle(.bordered)
                        }
                    }
                }
                
                Section {
                    Button(action: executeBuy) {
                        HStack {
                            if isLoading {
                                ProgressView()
                            } else {
                                Image(systemName: "cart.fill.badge.plus")
                            }
                            Text("Buy \(selectedCoin)")
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .disabled(isLoading || (Double(amount) ?? 0) < 5)
                }
            }
            .navigationTitle("Buy Crypto")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
    
    private func executeBuy() {
        guard let amt = Double(amount), amt >= 5 else { return }
        isLoading = true
        
        Task {
            let success = await spotService.buySpot(coin: selectedCoin, amount: amt, accountType: accountType)
            await MainActor.run {
                isLoading = false
                if success { dismiss() }
            }
        }
    }
}

struct SpotSellSheet: View {
    @ObservedObject var spotService: SpotService
    let coin: String
    let accountType: String
    @Environment(\.dismiss) var dismiss
    
    @State private var percentage: Double = 100
    @State private var isLoading = false
    
    var body: some View {
        NavigationStack {
            Form {
                Section(header: Text("Sell \(coin)")) {
                    VStack {
                        Text("\(Int(percentage))%")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                        
                        Slider(value: $percentage, in: 10...100, step: 10)
                        
                        HStack {
                            ForEach([25, 50, 75, 100], id: \.self) { value in
                                Button("\(value)%") {
                                    percentage = Double(value)
                                }
                                .buttonStyle(.bordered)
                            }
                        }
                    }
                }
                
                Section {
                    Button(action: executeSell) {
                        HStack {
                            if isLoading {
                                ProgressView()
                            } else {
                                Image(systemName: "arrow.down.circle.fill")
                            }
                            Text("Sell \(Int(percentage))% of \(coin)")
                        }
                        .frame(maxWidth: .infinity)
                        .foregroundColor(.enlikoRed)
                    }
                    .disabled(isLoading)
                }
            }
            .navigationTitle("Sell \(coin)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
    
    private func executeSell() {
        isLoading = true
        
        Task {
            let success = await spotService.sellSpot(coin: coin, percentage: percentage, accountType: accountType)
            await MainActor.run {
                isLoading = false
                if success { dismiss() }
            }
        }
    }
}

struct SpotRebalanceSheet: View {
    @ObservedObject var spotService: SpotService
    let accountType: String
    @Environment(\.dismiss) var dismiss
    
    @State private var selectedPortfolio = "blue_chip"
    @State private var additionalInvestment = ""
    @State private var isLoading = false
    
    var body: some View {
        NavigationStack {
            Form {
                Section(header: Text("Select Portfolio")) {
                    Picker("Portfolio", selection: $selectedPortfolio) {
                        Text("💎 Blue Chips").tag("blue_chip")
                        Text("🏦 DeFi").tag("defi")
                        Text("⚡ Layer 2").tag("layer2")
                        Text("🤖 AI & Data").tag("ai_narrative")
                        Text("🎮 Gaming").tag("gaming")
                        Text("🐕 Memecoins").tag("meme")
                        Text("⚔️ L1 Killers").tag("l1_killers")
                        Text("₿ BTC Only").tag("btc_only")
                        Text("💰 ETH+BTC").tag("eth_btc")
                    }
                }
                
                Section(header: Text("Additional Investment (optional)")) {
                    TextField("Amount USDT", text: $additionalInvestment)
                        .keyboardType(.decimalPad)
                }
                
                Section {
                    Button(action: executeRebalance) {
                        HStack {
                            if isLoading {
                                ProgressView()
                            } else {
                                Image(systemName: "arrow.triangle.2.circlepath")
                            }
                            Text("Rebalance Portfolio")
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .disabled(isLoading)
                }
            }
            .navigationTitle("Rebalance Portfolio")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
    
    private func executeRebalance() {
        let investment = Double(additionalInvestment) ?? 0
        isLoading = true
        
        Task {
            let success = await spotService.rebalancePortfolio(
                portfolio: selectedPortfolio,
                investment: investment,
                accountType: accountType
            )
            await MainActor.run {
                isLoading = false
                if success { dismiss() }
            }
        }
    }
}

#Preview {
    SpotTradingView()
        .environmentObject(AppState.shared)
}
