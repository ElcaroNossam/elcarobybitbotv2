//
//  ScreenerView.swift
//  EnlikoTrading
//
//  Market screener view with filters and localization
//

import SwiftUI

struct ScreenerView: View {
    @StateObject private var screener = ScreenerService.shared
    @ObservedObject var localization = LocalizationManager.shared
    @State private var searchText = ""
    @State private var selectedSymbol: ScreenerSymbol?
    @State private var showingDetail = false
    
    var filteredSymbols: [ScreenerSymbol] {
        if searchText.isEmpty {
            return screener.symbols
        }
        return screener.symbols.filter { $0.symbol.localizedCaseInsensitiveContains(searchText) }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Filter Picker
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(ScreenerService.ScreenerFilter.allCases, id: \.self) { filter in
                            FilterChip(
                                title: filter.rawValue.capitalized,
                                isSelected: screener.filter == filter
                            ) {
                                screener.filter = filter
                                Task {
                                    await screener.fetchSymbols(filter: filter)
                                }
                            }
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical, 8)
                .background(Color(.systemBackground))
                
                // Overview Cards
                if let overview = screener.overview {
                    OverviewSection(overview: overview)
                }
                
                // Symbols List
                if screener.isLoading {
                    Spacer()
                    ProgressView()
                    Spacer()
                } else {
                    List(filteredSymbols) { symbol in
                        SymbolRowView(symbol: symbol)
                            .onTapGesture {
                                selectedSymbol = symbol
                                showingDetail = true
                            }
                    }
                    .listStyle(PlainListStyle())
                }
            }
            .navigationTitle("screener_title".localized)
            .searchable(text: $searchText, prompt: "market_search".localized)
            .withRTLSupport()
            .refreshable {
                await screener.refreshAll()
            }
            .task {
                await screener.refreshAll()
            }
            .sheet(isPresented: $showingDetail) {
                if let symbol = selectedSymbol {
                    SymbolDetailSheet(symbol: symbol.symbol)
                }
            }
        }
    }
}

// MARK: - Filter Chip
struct FilterChip: View {
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

// MARK: - Overview Section
struct OverviewSection: View {
    let overview: ScreenerOverview
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                OverviewCard(
                    title: "Total",
                    value: "\(overview.totalSymbols)",
                    icon: "chart.bar.fill"
                )
                OverviewCard(
                    title: "Gainers",
                    value: "\(overview.bullishCount)",
                    icon: "arrow.up.circle.fill",
                    color: .green
                )
                OverviewCard(
                    title: "Losers",
                    value: "\(overview.bearishCount)",
                    icon: "arrow.down.circle.fill",
                    color: .red
                )
                
                // BTC Price Card
                if let btc = overview.btc {
                    OverviewCard(
                        title: "BTC",
                        value: "$\(Int(btc.price ?? 0).formattedWithSeparator)",
                        icon: "bitcoinsign.circle.fill",
                        color: (btc.change ?? 0) >= 0 ? .orange : .red
                    )
                }
            }
            .padding(.horizontal)
        }
        .padding(.vertical, 8)
    }
}

struct OverviewCard: View {
    let title: String
    let value: String
    let icon: String
    var color: Color = .accentColor
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
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
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

// MARK: - Symbol Row
struct SymbolRowView: View {
    let symbol: ScreenerSymbol
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(symbol.symbol)
                    .font(.headline)
                if let sentiment = symbol.sentiment {
                    Text(sentiment)
                        .font(.caption)
                        .foregroundColor(sentimentColor(sentiment))
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text(formatPrice(symbol.price))
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                HStack(spacing: 4) {
                    Image(systemName: symbol.change24h >= 0 ? "arrow.up" : "arrow.down")
                        .font(.caption2)
                    Text(String(format: "%.2f%%", symbol.change24h))
                        .font(.caption)
                }
                .foregroundColor(symbol.change24h >= 0 ? .green : .red)
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
    
    private func sentimentColor(_ sentiment: String) -> Color {
        switch sentiment.lowercased() {
        case "bullish": return .green
        case "bearish": return .red
        default: return .gray
        }
    }
}

// MARK: - Symbol Detail Sheet
struct SymbolDetailSheet: View {
    let symbol: String
    @StateObject private var screener = ScreenerService.shared
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                if let details = screener.selectedSymbol {
                    VStack(spacing: 16) {
                        // Price Card
                        PriceCard(details: details)
                        
                        // Indicators Card
                        if let indicators = details.indicators {
                            IndicatorsCard(indicators: indicators)
                        }
                        
                        // Market Data Card
                        MarketDataCard(details: details)
                    }
                    .padding()
                } else if screener.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .navigationTitle(symbol)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
            .task {
                await screener.fetchSymbolDetails(symbol: symbol)
            }
        }
    }
}

struct PriceCard: View {
    let details: SymbolDetails
    
    var body: some View {
        VStack(spacing: 12) {
            Text(String(format: "$%.4f", details.price))
                .font(.system(size: 36, weight: .bold, design: .rounded))
            
            HStack(spacing: 16) {
                VStack {
                    Text("24h Change")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "%.2f%%", details.change24h))
                        .foregroundColor(details.change24h >= 0 ? .green : .red)
                }
                
                VStack {
                    Text("24h High")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "$%.4f", details.high24h))
                }
                
                VStack {
                    Text("24h Low")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "$%.4f", details.low24h))
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
}

struct IndicatorsCard: View {
    let indicators: SymbolIndicators
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Technical Indicators")
                .font(.headline)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                if let rsi = indicators.rsi {
                    IndicatorItem(name: "RSI", value: String(format: "%.1f", rsi), color: rsiColor(rsi))
                }
                if let macd = indicators.macd {
                    IndicatorItem(name: "MACD", value: String(format: "%.4f", macd))
                }
                if let ema20 = indicators.ema20 {
                    IndicatorItem(name: "EMA 20", value: String(format: "%.4f", ema20))
                }
                if let ema50 = indicators.ema50 {
                    IndicatorItem(name: "EMA 50", value: String(format: "%.4f", ema50))
                }
                if let atr = indicators.atr {
                    IndicatorItem(name: "ATR", value: String(format: "%.4f", atr))
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
    
    private func rsiColor(_ rsi: Double) -> Color {
        if rsi > 70 { return .red }
        if rsi < 30 { return .green }
        return .primary
    }
}

struct IndicatorItem: View {
    let name: String
    let value: String
    var color: Color = .primary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(name)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct MarketDataCard: View {
    let details: SymbolDetails
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Market Data")
                .font(.headline)
            
            if let oi = details.openInterest {
                HStack {
                    Text("Open Interest")
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(formatLargeNumber(oi))
                }
            }
            
            if let fr = details.fundingRate {
                HStack {
                    Text("Funding Rate")
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(String(format: "%.4f%%", fr * 100))
                        .foregroundColor(fr >= 0 ? .green : .red)
                }
            }
            
            HStack {
                Text("24h Volume")
                    .foregroundColor(.secondary)
                Spacer()
                Text(formatLargeNumber(details.volume24h))
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
    
    private func formatLargeNumber(_ num: Double) -> String {
        if num >= 1_000_000_000 {
            return String(format: "%.2fB", num / 1_000_000_000)
        } else if num >= 1_000_000 {
            return String(format: "%.2fM", num / 1_000_000)
        } else if num >= 1_000 {
            return String(format: "%.2fK", num / 1_000)
        }
        return String(format: "%.0f", num)
    }
}

#Preview {
    ScreenerView()
}
