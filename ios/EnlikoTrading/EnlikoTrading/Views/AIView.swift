//
//  AIView.swift
//  EnlikoTrading
//
//  AI analysis and market sentiment view with localization
//

import SwiftUI

struct AIView: View {
    @ObservedObject private var ai = AIService.shared
    @ObservedObject var localization = LocalizationManager.shared
    @State private var selectedSymbol = "BTCUSDT"
    @State private var selectedTimeframe = "1h"
    @State private var showingSymbolPicker = false
    
    let timeframes = ["5m", "15m", "1h", "4h", "1d"]
    let popularSymbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 16) {
                    // Market Sentiment Card
                    if let sentiment = ai.marketSentiment {
                        MarketSentimentCard(sentiment: sentiment)
                    }
                    
                    // Symbol Analysis Section
                    SymbolAnalysisSection(
                        selectedSymbol: $selectedSymbol,
                        selectedTimeframe: $selectedTimeframe,
                        timeframes: timeframes,
                        popularSymbols: popularSymbols,
                        isAnalyzing: ai.isAnalyzing,
                        onAnalyze: {
                            Task {
                                await ai.analyzeSymbol(selectedSymbol, timeframe: selectedTimeframe)
                            }
                        }
                    )
                    
                    // Current Analysis
                    if let analysis = ai.currentAnalysis {
                        AnalysisResultCard(analysis: analysis)
                    }
                    
                    // Recent Analyses
                    if !ai.recentAnalyses.isEmpty {
                        RecentAnalysesSection(analyses: ai.recentAnalyses) { symbol in
                            selectedSymbol = symbol
                            Task {
                                await ai.analyzeSymbol(symbol, timeframe: selectedTimeframe)
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("ai_title".localized)
            .withRTLSupport()
            .refreshable {
                await ai.fetchMarketSentiment()
            }
            .task {
                await ai.fetchMarketSentiment()
            }
        }
    }
}

// MARK: - Market Sentiment Card
struct MarketSentimentCard: View {
    let sentiment: MarketSentiment
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Market Sentiment")
                    .font(.headline)
                Spacer()
                Text(sentiment.lastUpdated)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            HStack(spacing: 20) {
                // Sentiment Score
                VStack {
                    Text(sentiment.overall)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(sentimentColor(sentiment.overall))
                    
                    // Score Bar
                    GeometryReader { geometry in
                        ZStack(alignment: .leading) {
                            Rectangle()
                                .fill(Color(.systemGray5))
                                .frame(height: 8)
                                .cornerRadius(4)
                            
                            Rectangle()
                                .fill(sentimentColor(sentiment.overall))
                                .frame(
                                    width: max(0, geometry.size.width * CGFloat((sentiment.score + 100) / 200)),
                                    height: 8
                                )
                                .cornerRadius(4)
                        }
                    }
                    .frame(height: 8)
                    
                    Text(String(format: "%.0f", sentiment.score))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                // Fear & Greed
                if let fgi = sentiment.fearGreedIndex {
                    VStack {
                        Text("\(fgi)")
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(fgiColor(fgi))
                        Text("Fear & Greed")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                // BTC Dominance
                if let btcDom = sentiment.btcDominance {
                    VStack {
                        Text(String(format: "%.1f%%", btcDom))
                            .font(.title)
                            .fontWeight(.bold)
                        Text("BTC Dom")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            // Market Conditions
            if let conditions = sentiment.marketConditions {
                Divider()
                HStack(spacing: 16) {
                    ConditionBadge(label: "Volatility", value: conditions.volatility)
                    ConditionBadge(label: "Trend", value: conditions.trend)
                    ConditionBadge(label: "Volume", value: conditions.volume)
                }
            }
            
            // Top Signals
            if !sentiment.topSignals.isEmpty {
                Divider()
                Text("Top Signals")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                ForEach(sentiment.topSignals.prefix(3)) { signal in
                    HStack {
                        Text(signal.symbol)
                            .font(.caption)
                            .fontWeight(.medium)
                        Text(signal.direction)
                            .font(.caption)
                            .foregroundColor(signal.direction == "LONG" ? .green : .red)
                        Spacer()
                        Text(String(format: "%.0f%% conf", signal.confidence * 100))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
    
    private func sentimentColor(_ sentiment: String) -> Color {
        switch sentiment.uppercased() {
        case "BULLISH": return .green
        case "BEARISH": return .red
        default: return .gray
        }
    }
    
    private func fgiColor(_ fgi: Int) -> Color {
        if fgi <= 25 { return .red }
        if fgi <= 45 { return .orange }
        if fgi <= 55 { return .gray }
        if fgi <= 75 { return .green }
        return .green
    }
}

struct ConditionBadge: View {
    let label: String
    let value: String
    
    var body: some View {
        VStack(spacing: 2) {
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
            Text(value)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(conditionColor(value))
        }
    }
    
    private func conditionColor(_ value: String) -> Color {
        switch value.uppercased() {
        case "HIGH", "UPTREND": return .green
        case "LOW", "DOWNTREND": return .red
        default: return .primary
        }
    }
}

// MARK: - Symbol Analysis Section
struct SymbolAnalysisSection: View {
    @Binding var selectedSymbol: String
    @Binding var selectedTimeframe: String
    let timeframes: [String]
    let popularSymbols: [String]
    let isAnalyzing: Bool
    let onAnalyze: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Analyze Symbol")
                .font(.headline)
            
            // Symbol Picker
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(popularSymbols, id: \.self) { symbol in
                        Button {
                            selectedSymbol = symbol
                        } label: {
                            Text(symbol.replacingOccurrences(of: "USDT", with: ""))
                                .font(.caption)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(selectedSymbol == symbol ? Color.accentColor : Color(.systemGray5))
                                .foregroundColor(selectedSymbol == symbol ? .white : .primary)
                                .cornerRadius(16)
                        }
                    }
                }
            }
            
            // Timeframe Picker
            HStack(spacing: 8) {
                ForEach(timeframes, id: \.self) { tf in
                    Button {
                        selectedTimeframe = tf
                    } label: {
                        Text(tf)
                            .font(.caption)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 4)
                            .background(selectedTimeframe == tf ? Color.accentColor : Color(.systemGray5))
                            .foregroundColor(selectedTimeframe == tf ? .white : .primary)
                            .cornerRadius(8)
                    }
                }
            }
            
            // Analyze Button
            Button(action: onAnalyze) {
                HStack {
                    if isAnalyzing {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(0.8)
                    } else {
                        Image(systemName: "brain.head.profile")
                    }
                    Text(isAnalyzing ? "Analyzing..." : "Analyze \(selectedSymbol)")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.accentColor)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(isAnalyzing)
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
}

// MARK: - Analysis Result Card
struct AnalysisResultCard: View {
    let analysis: AIAnalysis
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(analysis.symbol)
                    .font(.headline)
                
                Spacer()
                
                Text(analysis.signal)
                    .font(.headline)
                    .foregroundColor(signalColor(analysis.signal))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 4)
                    .background(signalColor(analysis.signal).opacity(0.2))
                    .cornerRadius(8)
            }
            
            // Confidence
            HStack {
                Text("Confidence")
                    .foregroundColor(.secondary)
                Spacer()
                Text(String(format: "%.0f%%", analysis.confidence * 100))
                    .fontWeight(.medium)
            }
            
            // Risk Level
            HStack {
                Text("Risk")
                    .foregroundColor(.secondary)
                Spacer()
                Text(analysis.riskLevel)
                    .foregroundColor(riskColor(analysis.riskLevel))
            }
            
            Divider()
            
            // Analysis Text
            Text(analysis.analysis)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            // Key Factors
            if !analysis.keyFactors.isEmpty {
                Divider()
                Text("Key Factors")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                ForEach(analysis.keyFactors, id: \.self) { factor in
                    HStack(alignment: .top) {
                        Text("•")
                        Text(factor)
                            .font(.caption)
                    }
                    .foregroundColor(.secondary)
                }
            }
            
            // Price Targets
            if let targets = analysis.priceTargets {
                Divider()
                Text("Price Targets")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                HStack {
                    if let entry = targets.entry {
                        VStack {
                            Text("Entry")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text(formatPrice(entry))
                                .font(.caption)
                        }
                    }
                    Spacer()
                    if let tp = targets.takeProfit {
                        VStack {
                            Text("TP")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text(formatPrice(tp))
                                .font(.caption)
                                .foregroundColor(.green)
                        }
                    }
                    Spacer()
                    if let sl = targets.stopLoss {
                        VStack {
                            Text("SL")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text(formatPrice(sl))
                                .font(.caption)
                                .foregroundColor(.red)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
    
    private func signalColor(_ signal: String) -> Color {
        switch signal.uppercased() {
        case "LONG", "BUY": return .green
        case "SHORT", "SELL": return .red
        default: return .gray
        }
    }
    
    private func riskColor(_ risk: String) -> Color {
        switch risk.uppercased() {
        case "LOW": return .green
        case "MEDIUM": return .orange
        case "HIGH": return .red
        default: return .gray
        }
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

// MARK: - Recent Analyses Section
struct RecentAnalysesSection: View {
    let analyses: [AIAnalysis]
    let onSelect: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Analyses")
                .font(.headline)
            
            ForEach(analyses, id: \.symbol) { analysis in
                Button {
                    onSelect(analysis.symbol)
                } label: {
                    HStack {
                        Text(analysis.symbol)
                            .font(.subheadline)
                        
                        Text(analysis.signal)
                            .font(.caption)
                            .foregroundColor(analysis.signal == "LONG" ? .green : .red)
                        
                        Spacer()
                        
                        Text(String(format: "%.0f%%", analysis.confidence * 100))
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 8)
                }
                .buttonStyle(PlainButtonStyle())
                
                if analysis.symbol != analyses.last?.symbol {
                    Divider()
                }
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
}

#Preview {
    AIView()
}
