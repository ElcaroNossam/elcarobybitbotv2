//
//  BacktestView.swift
//  EnlikoTrading
//
//  Backtesting interface with real API integration
//

import SwiftUI

struct BacktestView: View {
    @StateObject private var backtestService = BacktestService.shared
    
    @State private var selectedStrategy = "oi"
    @State private var selectedSymbol = "BTCUSDT"
    @State private var selectedTimeframe = "15m"
    @State private var selectedDataSource = "binance"
    @State private var days = 30
    @State private var initialBalance = "10000"
    @State private var riskPercent = "1.0"
    @State private var stopLossPercent = "3.0"
    @State private var takeProfitPercent = "8.0"
    @State private var leverage = 10
    
    @State private var isRunning = false
    @State private var result: BacktestResult?
    @State private var resultData: BacktestResultData?
    @State private var errorMessage: String?
    @State private var showSaveSheet = false
    @State private var saveName = ""
    @State private var showSavedList = false
    @State private var savedBacktests: [SavedBacktest] = []
    
    private let strategies = [
        ("oi", "OI Strategy"),
        ("scryptomera", "Scryptomera"),
        ("scalper", "Scalper"),
        ("elcaro", "Elcaro"),
        ("fibonacci", "Fibonacci"),
        ("rsi_bb", "RSI + BB")
    ]
    private let timeframes = ["5m", "15m", "1h", "4h", "1d"]
    private let symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]
    private let dataSources = [
        ("binance", "Binance"),
        ("bybit", "Bybit"),
        ("hyperliquid", "HyperLiquid")
    ]
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 20) {
                    // Header with History Button
                    headerView
                    
                    // Parameters Card
                    parametersCard
                    
                    // Run Button
                    runButton
                    
                    // Results
                    if let result = result {
                        resultsCard(result)
                    }
                    
                    // Error
                    if let error = errorMessage {
                        errorCard(error)
                    }
                }
                .padding()
            }
        }
        .sheet(isPresented: $showSaveSheet) {
            saveBacktestSheet
        }
        .sheet(isPresented: $showSavedList) {
            savedBacktestsSheet
        }
    }
    
    // MARK: - Header
    private var headerView: some View {
        HStack {
            Text("Backtest")
                .font(.title2.weight(.bold))
                .foregroundColor(.white)
            
            Spacer()
            
            Button(action: { loadSavedBacktests() }) {
                HStack(spacing: 4) {
                    Image(systemName: "clock.arrow.circlepath")
                    Text("History")
                }
                .font(.subheadline)
                .foregroundColor(.enlikoPrimary)
            }
        }
    }
    
    // MARK: - Parameters Card
    private var parametersCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Parameters")
                .font(.headline)
                .foregroundColor(.white)
            
            // Strategy Picker
            VStack(alignment: .leading, spacing: 8) {
                Text("Strategy")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                Picker("Strategy", selection: $selectedStrategy) {
                    ForEach(strategies, id: \.0) { strategy in
                        Text(strategy.1).tag(strategy.0)
                    }
                }
                .pickerStyle(.menu)
                .tint(.enlikoPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            
            // Symbol Picker
            VStack(alignment: .leading, spacing: 8) {
                Text("Symbol")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                Picker("Symbol", selection: $selectedSymbol) {
                    ForEach(symbols, id: \.self) { symbol in
                        Text(symbol).tag(symbol)
                    }
                }
                .pickerStyle(.segmented)
            }
            
            // Timeframe Picker
            VStack(alignment: .leading, spacing: 8) {
                Text("Timeframe")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                Picker("Timeframe", selection: $selectedTimeframe) {
                    ForEach(timeframes, id: \.self) { tf in
                        Text(tf).tag(tf)
                    }
                }
                .pickerStyle(.segmented)
            }
            
            // Data Source Picker
            VStack(alignment: .leading, spacing: 8) {
                Text("Data Source")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                Picker("Data Source", selection: $selectedDataSource) {
                    ForEach(dataSources, id: \.0) { source in
                        Text(source.1).tag(source.0)
                    }
                }
                .pickerStyle(.segmented)
            }
            
            Divider().background(Color.enlikoCardHover)
            
            // Days & Balance Row
            HStack(spacing: 16) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Days")
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                    Stepper("\(days)", value: $days, in: 7...365, step: 7)
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Initial $")
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                    TextField("10000", text: $initialBalance)
                        .keyboardType(.decimalPad)
                        .padding(8)
                        .background(Color.enlikoSurface)
                        .cornerRadius(8)
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Leverage")
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                    Stepper("\(leverage)x", value: $leverage, in: 1...100)
                        .foregroundColor(.white)
                }
            }
            
            Divider().background(Color.enlikoCardHover)
            
            // Risk Parameters
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Risk %")
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                    TextField("1.0", text: $riskPercent)
                        .keyboardType(.decimalPad)
                        .padding(8)
                        .background(Color.enlikoSurface)
                        .cornerRadius(8)
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("SL %")
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                    TextField("3.0", text: $stopLossPercent)
                        .keyboardType(.decimalPad)
                        .padding(8)
                        .background(Color.enlikoSurface)
                        .cornerRadius(8)
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("TP %")
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                    TextField("8.0", text: $takeProfitPercent)
                        .keyboardType(.decimalPad)
                        .padding(8)
                        .background(Color.enlikoSurface)
                        .cornerRadius(8)
                        .foregroundColor(.white)
                }
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(12)
    }
    
    // MARK: - Run Button
    private var runButton: some View {
        Button(action: runBacktest) {
            HStack {
                if isRunning {
                    ProgressView()
                        .tint(.white)
                    Text("Running...")
                } else {
                    Image(systemName: "play.fill")
                    Text("Run Backtest")
                        .fontWeight(.semibold)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(isRunning ? Color.gray : Color.enlikoPrimary)
            .foregroundColor(.white)
            .cornerRadius(12)
        }
        .disabled(isRunning)
    }
    
    // MARK: - Results Card
    private func resultsCard(_ result: BacktestResult) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Results")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                
                // Save Button
                Button(action: { showSaveSheet = true }) {
                    HStack(spacing: 4) {
                        Image(systemName: "square.and.arrow.down")
                        Text("Save")
                    }
                    .font(.caption.weight(.semibold))
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.enlikoPrimary.opacity(0.2))
                    .foregroundColor(.enlikoPrimary)
                    .cornerRadius(6)
                }
                
                Text((result.strategy ?? "").uppercased())
                    .font(.caption.weight(.bold))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.enlikoPrimary)
                    .foregroundColor(.white)
                    .cornerRadius(6)
            }
            
            // Stats Grid
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                resultStat(title: "Total Trades", value: "\(result.totalTrades)")
                resultStat(title: "Win Rate", value: String(format: "%.1f%%", result.winRate), color: result.winRate >= 50 ? .enlikoGreen : .enlikoRed)
                resultStat(title: "Total PnL", value: result.totalPnl.formattedCurrency, color: result.totalPnl >= 0 ? .enlikoGreen : .enlikoRed)
                resultStat(title: "Max Drawdown", value: String(format: "%.1f%%", result.maxDrawdown), color: .enlikoRed)
                resultStat(title: "Profit Factor", value: String(format: "%.2f", result.profitFactor), color: result.profitFactor >= 1 ? .enlikoGreen : .enlikoRed)
                if result.sharpeRatio != 0 {
                    resultStat(title: "Sharpe Ratio", value: String(format: "%.2f", result.sharpeRatio), color: result.sharpeRatio >= 1 ? .enlikoGreen : .enlikoYellow)
                }
            }
            
            // Additional metrics if available
            if let data = resultData {
                additionalMetrics(data)
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(12)
    }
    
    private func additionalMetrics(_ data: BacktestResultData) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Divider().background(Color.enlikoCardHover)
            
            Text("Details")
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.enlikoTextSecondary)
            
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible()), GridItem(.flexible())], spacing: 8) {
                if let wins = data.winningTrades {
                    miniStat(title: "Wins", value: "\(wins)")
                }
                if let losses = data.losingTrades {
                    miniStat(title: "Losses", value: "\(losses)")
                }
                if let avgWin = data.avgWin {
                    miniStat(title: "Avg Win", value: String(format: "$%.0f", avgWin))
                }
                if let avgLoss = data.avgLoss {
                    miniStat(title: "Avg Loss", value: String(format: "$%.0f", abs(avgLoss)))
                }
                if let finalBalance = data.finalBalance {
                    miniStat(title: "Final $", value: String(format: "$%.0f", finalBalance))
                }
                if let expectancy = data.expectancy {
                    miniStat(title: "Expectancy", value: String(format: "$%.1f", expectancy))
                }
            }
        }
    }
    
    private func miniStat(title: String, value: String) -> some View {
        VStack(spacing: 2) {
            Text(title)
                .font(.caption2)
                .foregroundColor(.enlikoTextSecondary)
            Text(value)
                .font(.caption.weight(.semibold))
                .foregroundColor(.white)
        }
        .padding(6)
        .frame(maxWidth: .infinity)
        .background(Color.enlikoSurface)
        .cornerRadius(6)
    }
    
    private func resultStat(title: String, value: String, color: Color = .white) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            Text(value)
                .font(.headline)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(8)
    }
    
    // MARK: - Error Card
    private func errorCard(_ error: String) -> some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.enlikoRed)
            Text(error)
                .foregroundColor(.enlikoRed)
                .font(.subheadline)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color.enlikoRed.opacity(0.1))
        .cornerRadius(12)
    }
    
    // MARK: - Save Sheet
    private var saveBacktestSheet: some View {
        NavigationView {
            VStack(spacing: 20) {
                TextField("Backtest name", text: $saveName)
                    .textFieldStyle(.roundedBorder)
                    .padding()
                
                Button("Save") {
                    saveCurrentBacktest()
                }
                .buttonStyle(.borderedProminent)
                .disabled(saveName.isEmpty)
                
                Spacer()
            }
            .navigationTitle("Save Backtest")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { showSaveSheet = false }
                }
            }
        }
        .presentationDetents([.medium])
    }
    
    // MARK: - Saved Backtests Sheet
    private var savedBacktestsSheet: some View {
        NavigationView {
            List {
                if savedBacktests.isEmpty {
                    Text("No saved backtests")
                        .foregroundColor(.secondary)
                } else {
                    ForEach(savedBacktests) { backtest in
                        savedBacktestRow(backtest)
                    }
                    .onDelete(perform: deleteBacktest)
                }
            }
            .navigationTitle("Saved Backtests")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { showSavedList = false }
                }
            }
        }
    }
    
    private func savedBacktestRow(_ backtest: SavedBacktest) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(backtest.name ?? backtest.strategy.uppercased())
                    .font(.headline)
                Spacer()
                Text(backtest.symbol)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            HStack {
                Text("Win: \(String(format: "%.1f%%", backtest.winRate ?? 0))")
                Text("•")
                Text("PnL: \((backtest.totalPnl ?? 0).formattedCurrency)")
                    .foregroundColor((backtest.totalPnl ?? 0) >= 0 ? .green : .red)
                Text("•")
                Text("\(backtest.totalTrades ?? 0) trades")
            }
            .font(.caption)
            .foregroundColor(.secondary)
        }
    }
    
    // MARK: - Actions
    
    private func runBacktest() {
        isRunning = true
        result = nil
        resultData = nil
        errorMessage = nil
        
        Task {
            do {
                let results = try await backtestService.runBacktest(
                    strategies: [selectedStrategy],
                    symbol: selectedSymbol,
                    timeframe: selectedTimeframe,
                    days: days,
                    initialBalance: Double(initialBalance) ?? 10000,
                    riskPerTrade: Double(riskPercent) ?? 1.0,
                    stopLossPercent: Double(stopLossPercent) ?? 3.0,
                    takeProfitPercent: Double(takeProfitPercent) ?? 8.0,
                    leverage: leverage,
                    dataSource: selectedDataSource
                )
                
                await MainActor.run {
                    if let data = results[selectedStrategy] {
                        self.resultData = data
                        self.result = data.toBacktestResult(
                            strategy: selectedStrategy,
                            symbol: selectedSymbol,
                            timeframe: selectedTimeframe
                        )
                    }
                    isRunning = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isRunning = false
                }
            }
        }
    }
    
    private func saveCurrentBacktest() {
        guard let data = resultData else { return }
        
        Task {
            do {
                _ = try await backtestService.saveBacktest(
                    name: saveName,
                    strategy: selectedStrategy,
                    symbol: selectedSymbol,
                    timeframe: selectedTimeframe,
                    result: data
                )
                await MainActor.run {
                    showSaveSheet = false
                    saveName = ""
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
    
    private func loadSavedBacktests() {
        Task {
            do {
                let backtests = try await backtestService.getSavedBacktests()
                await MainActor.run {
                    self.savedBacktests = backtests
                    self.showSavedList = true
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
    
    private func deleteBacktest(at offsets: IndexSet) {
        for index in offsets {
            let backtest = savedBacktests[index]
            Task {
                try? await backtestService.deleteBacktest(id: backtest.id)
            }
        }
        savedBacktests.remove(atOffsets: offsets)
    }
}

#Preview {
    BacktestView()
        .preferredColorScheme(.dark)
}
