//
//  MarketView.swift
//  EnlikoTrading
//
//  Market overview and screener
//

import SwiftUI

struct MarketView: View {
    @EnvironmentObject var tradingService: TradingService
    @StateObject private var webSocket = WebSocketService.shared
    
    @State private var searchText = ""
    @State private var sortBy: SortOption = .volume
    @State private var showFilters = false
    
    enum SortOption: String, CaseIterable {
        case volume = "Volume"
        case change = "24h Change"
        case name = "Name"
    }
    
    var filteredSymbols: [WSTickerMessage] {
        var tickersList = Array(webSocket.tickers.values)
        
        if !searchText.isEmpty {
            tickersList = tickersList.filter { $0.symbol.localizedCaseInsensitiveContains(searchText) }
        }
        
        switch sortBy {
        case .volume:
            tickersList.sort { $0.volume24h > $1.volume24h }
        case .change:
            tickersList.sort { $0.priceChangePercent > $1.priceChangePercent }
        case .name:
            tickersList.sort { $0.symbol < $1.symbol }
        }
        
        return tickersList
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Sort Options
                    sortOptionsBar
                    
                    // Market List
                    if webSocket.tickers.isEmpty {
                        emptyState
                    } else {
                        marketList
                    }
                }
            }
            .navigationTitle("Market")
            .navigationBarTitleDisplayMode(.large)
            .searchable(text: $searchText, prompt: "Search symbols...")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { webSocket.connect() }) {
                        Circle()
                            .fill(webSocket.isConnected ? Color.enlikoGreen : Color.enlikoRed)
                            .frame(width: 8, height: 8)
                    }
                }
            }
            .onAppear {
                if !webSocket.isConnected {
                    webSocket.connect()
                }
            }
        }
    }
    
    // MARK: - Sort Options Bar
    private var sortOptionsBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(SortOption.allCases, id: \.self) { option in
                    Button(action: { sortBy = option }) {
                        Text(option.rawValue)
                            .font(.caption.weight(.medium))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(sortBy == option ? Color.enlikoPrimary : Color.enlikoCard)
                            .foregroundColor(sortBy == option ? .white : .enlikoTextSecondary)
                            .cornerRadius(16)
                    }
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 12)
        }
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Empty State
    private var emptyState: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
            
            Text("Connecting to market data...")
                .foregroundColor(.enlikoTextSecondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // MARK: - Market List
    private var marketList: some View {
        List {
            ForEach(filteredSymbols) { ticker in
                NavigationLink {
                    SymbolDetailView(symbol: ticker.symbol)
                } label: {
                    MarketTickerRow(ticker: ticker)
                }
                .listRowBackground(Color.enlikoCard)
                .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
            }
        }
        .listStyle(.plain)
        .scrollContentBackground(.hidden)
    }
}

// MARK: - Market Ticker Row
struct MarketTickerRow: View {
    let ticker: WSTickerMessage
    
    var body: some View {
        HStack {
            // Symbol Info
            VStack(alignment: .leading, spacing: 4) {
                Text(ticker.symbol.replacingOccurrences(of: "USDT", with: ""))
                    .font(.headline)
                    .foregroundColor(.white)
                
                Text("/ USDT")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            // Price & Change
            VStack(alignment: .trailing, spacing: 4) {
                Text("$\(ticker.price.formattedPrice)")
                    .font(.headline)
                    .foregroundColor(.white)
                
                HStack(spacing: 4) {
                    Image(systemName: ticker.priceChangePercent >= 0 ? "arrow.up" : "arrow.down")
                        .font(.caption2.weight(.bold))
                    Text(String(format: "%.2f%%", abs(ticker.priceChangePercent)))
                }
                .font(.caption.weight(.medium))
                .foregroundColor(ticker.priceChangePercent >= 0 ? .enlikoGreen : .enlikoRed)
            }
            
            // Volume Badge
            Text(ticker.volume24h.compactFormatted)
                .font(.caption.weight(.medium))
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.enlikoSurface)
                .foregroundColor(.enlikoTextSecondary)
                .cornerRadius(8)
                .frame(width: 70)
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Market Ticker Model
struct MarketTicker: Identifiable {
    let id = UUID()
    let symbol: String
    let lastPrice: Double
    let priceChangePercent: Double
    let volume24h: Double
    let high24h: Double
    let low24h: Double
}

// MARK: - Symbol Detail View
struct SymbolDetailView: View {
    let symbol: String
    @EnvironmentObject var tradingService: TradingService
    @State private var showTradingSheet = false
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 20) {
                    // Price Card
                    priceCard
                    
                    // Chart Placeholder
                    chartPlaceholder
                    
                    // Stats
                    statsGrid
                    
                    // Trade Button
                    Button(action: { showTradingSheet = true }) {
                        HStack {
                            Image(systemName: "arrow.left.arrow.right")
                            Text("Trade \(symbol.replacingOccurrences(of: "USDT", with: ""))")
                        }
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(Color.enlikoPrimary)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                }
                .padding()
            }
        }
        .navigationTitle(symbol)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showTradingSheet) {
            TradingView()
        }
    }
    
    private var priceCard: some View {
        VStack(spacing: 12) {
            Text("$65,432.50")
                .font(.system(size: 40, weight: .bold, design: .rounded))
                .foregroundColor(.white)
            
            HStack(spacing: 4) {
                Image(systemName: "arrow.up")
                    .font(.caption.weight(.bold))
                Text("+2.34%")
                Text("($1,495.20)")
                    .foregroundColor(.enlikoTextSecondary)
            }
            .font(.subheadline)
            .foregroundColor(.enlikoGreen)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .enlikoCard()
    }
    
    private var chartPlaceholder: some View {
        VStack {
            // Timeframe selector
            HStack(spacing: 16) {
                ForEach(["1H", "4H", "1D", "1W"], id: \.self) { tf in
                    Text(tf)
                        .font(.caption.weight(.medium))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(tf == "1D" ? Color.enlikoPrimary : Color.clear)
                        .foregroundColor(tf == "1D" ? .white : .enlikoTextSecondary)
                        .cornerRadius(8)
                }
            }
            
            // Chart placeholder
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.enlikoSurface)
                .frame(height: 200)
                .overlay(
                    Text("Chart coming soon")
                        .foregroundColor(.enlikoTextMuted)
                )
        }
        .padding()
        .enlikoCard()
    }
    
    private var statsGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            StatBox(title: "24h High", value: "$67,890.00", color: .enlikoGreen)
            StatBox(title: "24h Low", value: "$63,210.00", color: .enlikoRed)
            StatBox(title: "24h Volume", value: "$1.2B", color: .enlikoBlue)
            StatBox(title: "Open Interest", value: "$890M", color: .enlikoYellow)
        }
    }
}

struct StatBox: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            
            Text(value)
                .font(.headline)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .enlikoCard()
    }
}

#Preview {
    MarketView()
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
