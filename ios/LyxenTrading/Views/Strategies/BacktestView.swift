//
//  BacktestView.swift
//  LyxenTrading
//
//  Backtesting interface
//

import SwiftUI

struct BacktestView: View {
    @State private var selectedStrategy = "oi"
    @State private var selectedSymbol = "BTCUSDT"
    @State private var selectedTimeframe = "15m"
    @State private var days = 30
    @State private var initialBalance = "10000"
    @State private var riskPercent = "1.0"
    @State private var stopLossPercent = "3.0"
    @State private var takeProfitPercent = "8.0"
    
    @State private var isRunning = false
    @State private var result: BacktestResult?
    @State private var errorMessage: String?
    
    private let strategies = ["oi", "scryptomera", "scalper", "elcaro", "fibonacci", "rsi_bb"]
    private let timeframes = ["5m", "15m", "1h", "4h", "1d"]
    
    var body: some View {
        ZStack {
            Color.lyxenBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 20) {
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
    }
    
    // MARK: - Parameters Card
    private var parametersCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Backtest Parameters")
                .font(.headline)
                .foregroundColor(.white)
            
            // Strategy Picker
            HStack {
                Text("Strategy")
                    .foregroundColor(.lyxenTextSecondary)
                Spacer()
                Picker("Strategy", selection: $selectedStrategy) {
                    ForEach(strategies, id: \.self) { strategy in
                        Text(strategy.uppercased()).tag(strategy)
                    }
                }
                .pickerStyle(.menu)
                .tint(.lyxenPrimary)
            }
            
            // Symbol
            HStack {
                Text("Symbol")
                    .foregroundColor(.lyxenTextSecondary)
                Spacer()
                TextField("BTCUSDT", text: $selectedSymbol)
                    .textInputAutocapitalization(.characters)
                    .multilineTextAlignment(.trailing)
                    .foregroundColor(.white)
                    .frame(width: 120)
            }
            
            // Timeframe Picker
            HStack {
                Text("Timeframe")
                    .foregroundColor(.lyxenTextSecondary)
                Spacer()
                Picker("Timeframe", selection: $selectedTimeframe) {
                    ForEach(timeframes, id: \.self) { tf in
                        Text(tf).tag(tf)
                    }
                }
                .pickerStyle(.segmented)
                .frame(width: 200)
            }
            
            Divider().background(Color.lyxenCardHover)
            
            // Days
            HStack {
                Text("History (days)")
                    .foregroundColor(.lyxenTextSecondary)
                Spacer()
                Stepper("\(days)", value: $days, in: 7...365, step: 7)
                    .foregroundColor(.white)
            }
            
            // Initial Balance
            HStack {
                Text("Initial Balance")
                    .foregroundColor(.lyxenTextSecondary)
                Spacer()
                HStack {
                    Text("$")
                        .foregroundColor(.lyxenTextSecondary)
                    TextField("10000", text: $initialBalance)
                        .keyboardType(.decimalPad)
                        .multilineTextAlignment(.trailing)
                        .foregroundColor(.white)
                        .frame(width: 80)
                }
            }
            
            Divider().background(Color.lyxenCardHover)
            
            // Risk Parameters
            HStack {
                VStack(alignment: .leading) {
                    Text("Risk %")
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                    TextField("1.0", text: $riskPercent)
                        .keyboardType(.decimalPad)
                        .padding(8)
                        .background(Color.lyxenSurface)
                        .cornerRadius(8)
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading) {
                    Text("SL %")
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                    TextField("3.0", text: $stopLossPercent)
                        .keyboardType(.decimalPad)
                        .padding(8)
                        .background(Color.lyxenSurface)
                        .cornerRadius(8)
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading) {
                    Text("TP %")
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                    TextField("8.0", text: $takeProfitPercent)
                        .keyboardType(.decimalPad)
                        .padding(8)
                        .background(Color.lyxenSurface)
                        .cornerRadius(8)
                        .foregroundColor(.white)
                }
            }
        }
        .padding()
        .background(Color.lyxenCard)
        .cornerRadius(12)
    }
    
    // MARK: - Run Button
    private var runButton: some View {
        Button(action: runBacktest) {
            HStack {
                if isRunning {
                    ProgressView()
                        .tint(.white)
                } else {
                    Image(systemName: "play.fill")
                    Text("Run Backtest")
                        .fontWeight(.semibold)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(Color.lyxenPrimary)
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
                Text(result.strategy.uppercased())
                    .font(.caption.weight(.bold))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.lyxenPrimary)
                    .foregroundColor(.white)
                    .cornerRadius(6)
            }
            
            // Stats Grid
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                resultStat(title: "Total Trades", value: "\(result.totalTrades)")
                resultStat(title: "Win Rate", value: String(format: "%.1f%%", result.winRate), color: result.winRate >= 50 ? .lyxenGreen : .lyxenRed)
                resultStat(title: "Total PnL", value: result.totalPnl.formattedCurrency, color: result.totalPnl >= 0 ? .lyxenGreen : .lyxenRed)
                resultStat(title: "Max Drawdown", value: String(format: "%.1f%%", result.maxDrawdown), color: .lyxenRed)
                resultStat(title: "Profit Factor", value: String(format: "%.2f", result.profitFactor))
                if let sharpe = result.sharpeRatio {
                    resultStat(title: "Sharpe Ratio", value: String(format: "%.2f", sharpe))
                }
            }
        }
        .padding()
        .background(Color.lyxenCard)
        .cornerRadius(12)
    }
    
    private func resultStat(title: String, value: String, color: Color = .white) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.lyxenTextSecondary)
            Text(value)
                .font(.headline)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color.lyxenSurface)
        .cornerRadius(8)
    }
    
    // MARK: - Error Card
    private func errorCard(_ error: String) -> some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.lyxenRed)
            Text(error)
                .foregroundColor(.lyxenRed)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color.lyxenRed.opacity(0.1))
        .cornerRadius(12)
    }
    
    // MARK: - Run Backtest
    private func runBacktest() {
        isRunning = true
        result = nil
        errorMessage = nil
        
        Task {
            // Simulate API call
            try? await Task.sleep(nanoseconds: 2_000_000_000)
            
            await MainActor.run {
                // Mock result for now
                result = BacktestResult(
                    id: UUID().uuidString,
                    strategy: selectedStrategy,
                    symbol: selectedSymbol,
                    timeframe: selectedTimeframe,
                    totalTrades: 156,
                    winRate: 62.5,
                    totalPnl: 2340.50,
                    maxDrawdown: 12.3,
                    profitFactor: 1.85,
                    sharpeRatio: 1.42,
                    trades: nil
                )
                isRunning = false
            }
        }
    }
}

#Preview {
    BacktestView()
        .preferredColorScheme(.dark)
}
