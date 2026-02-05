//
//  MarketHubView.swift
//  EnlikoTrading
//
//  Unified market data view like Binance/Bybit
//  Features: Crypto list, Search, Favorites, Charts, Orderbook
//

import SwiftUI

// MARK: - Market Models
struct CoinMarketData: Identifiable, Codable {
    var id: String { symbol }
    let symbol: String
    let price: Double
    let change24h: Double
    let volume24h: Double
    let high24h: Double?
    let low24h: Double?
    let fundingRate: Double?
    let openInterest: Double?
    
    var priceDisplay: String {
        if price >= 1000 {
            return String(format: "$%.2f", price)
        } else if price >= 1 {
            return String(format: "$%.4f", price)
        } else {
            return String(format: "$%.6f", price)
        }
    }
    
    var changeDisplay: String {
        let sign = change24h >= 0 ? "+" : ""
        return String(format: "%@%.2f%%", sign, change24h)
    }
    
    var changeColor: Color {
        change24h >= 0 ? .green : .red
    }
    
    var volumeDisplay: String {
        if volume24h >= 1_000_000_000 {
            return String(format: "$%.2fB", volume24h / 1_000_000_000)
        } else if volume24h >= 1_000_000 {
            return String(format: "$%.2fM", volume24h / 1_000_000)
        } else {
            return String(format: "$%.2fK", volume24h / 1_000)
        }
    }
}

struct MarketHubView: View {
    @EnvironmentObject var appState: AppState
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var selectedTab: MarketTab = .all
    @State private var searchText = ""
    @State private var coins: [CoinMarketData] = []
    @State private var favorites: Set<String> = []
    @State private var isLoading = true
    @State private var selectedCoin: CoinMarketData?
    @State private var showChart = false
    @State private var showOrderbook = false
    @State private var sortBy: SortOption = .volume
    @State private var sortAscending = false
    
    enum MarketTab: String, CaseIterable {
        case all = "All"
        case favorites = "⭐"
        case gainers = "🚀 Gainers"
        case losers = "📉 Losers"
        case funding = "💰 Funding"
    }
    
    enum SortOption: String, CaseIterable {
        case symbol = "Symbol"
        case price = "Price"
        case change = "24h %"
        case volume = "Volume"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Search Bar
            searchBar
            
            // Tab Bar
            tabBar
            
            // Sort Options
            sortBar
            
            // Market List
            if isLoading {
                Spacer()
                ProgressView()
                Spacer()
            } else {
                marketList
            }
        }
        .background(Color.enlikoBackground)
        .navigationTitle("market".localized)
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task { await refreshMarketData() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(.enlikoPrimary)
                }
            }
        }
        .sheet(item: $selectedCoin) { coin in
            CoinDetailSheet(coin: coin, isFavorite: favorites.contains(coin.symbol)) {
                toggleFavorite(coin.symbol)
            }
        }
        .task {
            loadFavorites()
            await refreshMarketData()
        }
    }
    
    // MARK: - Search Bar
    private var searchBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
            
            TextField("Search coins...", text: $searchText)
                .textFieldStyle(.plain)
            
            if !searchText.isEmpty {
                Button {
                    searchText = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(12)
        .padding(.horizontal)
        .padding(.top, 8)
    }
    
    // MARK: - Tab Bar
    private var tabBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(MarketTab.allCases, id: \.self) { tab in
                    Button {
                        withAnimation { selectedTab = tab }
                    } label: {
                        Text(tab.rawValue)
                            .font(.subheadline.bold())
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(selectedTab == tab ? Color.enlikoPrimary : Color.enlikoSurface)
                            .foregroundColor(selectedTab == tab ? .white : .secondary)
                            .cornerRadius(20)
                    }
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
        }
    }
    
    // MARK: - Sort Bar
    private var sortBar: some View {
        HStack {
            ForEach(SortOption.allCases, id: \.self) { option in
                Button {
                    if sortBy == option {
                        sortAscending.toggle()
                    } else {
                        sortBy = option
                        sortAscending = false
                    }
                } label: {
                    HStack(spacing: 4) {
                        Text(option.rawValue)
                            .font(.caption)
                        
                        if sortBy == option {
                            Image(systemName: sortAscending ? "chevron.up" : "chevron.down")
                                .font(.caption2)
                        }
                    }
                    .foregroundColor(sortBy == option ? .enlikoPrimary : .secondary)
                }
                
                if option != .volume {
                    Spacer()
                }
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.enlikoSurface.opacity(0.5))
    }
    
    // MARK: - Market List
    private var marketList: some View {
        ScrollView {
            LazyVStack(spacing: 1) {
                ForEach(filteredCoins) { coin in
                    CoinRow(
                        coin: coin,
                        isFavorite: favorites.contains(coin.symbol),
                        onTap: { selectedCoin = coin },
                        onFavorite: { toggleFavorite(coin.symbol) }
                    )
                }
            }
        }
        .refreshable {
            await refreshMarketData()
        }
    }
    
    // MARK: - Filtered & Sorted Coins
    private var filteredCoins: [CoinMarketData] {
        var result = coins
        
        // Search filter
        if !searchText.isEmpty {
            result = result.filter { $0.symbol.lowercased().contains(searchText.lowercased()) }
        }
        
        // Tab filter
        switch selectedTab {
        case .all:
            break
        case .favorites:
            result = result.filter { favorites.contains($0.symbol) }
        case .gainers:
            result = result.filter { $0.change24h > 0 }.sorted { $0.change24h > $1.change24h }
        case .losers:
            result = result.filter { $0.change24h < 0 }.sorted { $0.change24h < $1.change24h }
        case .funding:
            result = result.filter { $0.fundingRate != nil }.sorted { ($0.fundingRate ?? 0) > ($1.fundingRate ?? 0) }
        }
        
        // Sort
        if selectedTab == .all || selectedTab == .favorites {
            switch sortBy {
            case .symbol:
                result = result.sorted { sortAscending ? $0.symbol < $1.symbol : $0.symbol > $1.symbol }
            case .price:
                result = result.sorted { sortAscending ? $0.price < $1.price : $0.price > $1.price }
            case .change:
                result = result.sorted { sortAscending ? $0.change24h < $1.change24h : $0.change24h > $1.change24h }
            case .volume:
                result = result.sorted { sortAscending ? $0.volume24h < $1.volume24h : $0.volume24h > $1.volume24h }
            }
        }
        
        return result
    }
    
    // MARK: - Actions
    private func refreshMarketData() async {
        isLoading = true
        
        // Simulate API call - in production, fetch from /api/screener/coins
        try? await Task.sleep(nanoseconds: 500_000_000)
        
        // Mock data
        let mockCoins: [CoinMarketData] = [
            CoinMarketData(symbol: "BTCUSDT", price: 98500, change24h: 2.5, volume24h: 5_800_000_000, high24h: 99200, low24h: 96800, fundingRate: 0.01, openInterest: 12_000_000_000),
            CoinMarketData(symbol: "ETHUSDT", price: 3200, change24h: 1.8, volume24h: 2_100_000_000, high24h: 3250, low24h: 3120, fundingRate: 0.008, openInterest: 5_000_000_000),
            CoinMarketData(symbol: "SOLUSDT", price: 180, change24h: 5.2, volume24h: 800_000_000, high24h: 185, low24h: 170, fundingRate: 0.015, openInterest: 800_000_000),
            CoinMarketData(symbol: "BNBUSDT", price: 620, change24h: -0.5, volume24h: 450_000_000, high24h: 630, low24h: 610, fundingRate: 0.005, openInterest: nil),
            CoinMarketData(symbol: "XRPUSDT", price: 2.5, change24h: 8.3, volume24h: 1_200_000_000, high24h: 2.6, low24h: 2.3, fundingRate: 0.02, openInterest: nil),
            CoinMarketData(symbol: "ADAUSDT", price: 0.85, change24h: -2.1, volume24h: 320_000_000, high24h: 0.88, low24h: 0.82, fundingRate: -0.005, openInterest: nil),
            CoinMarketData(symbol: "DOGEUSDT", price: 0.32, change24h: 12.5, volume24h: 900_000_000, high24h: 0.35, low24h: 0.28, fundingRate: 0.03, openInterest: nil),
            CoinMarketData(symbol: "DOTUSDT", price: 7.2, change24h: -1.3, volume24h: 180_000_000, high24h: 7.4, low24h: 7.0, fundingRate: 0.002, openInterest: nil),
            CoinMarketData(symbol: "AVAXUSDT", price: 38, change24h: 3.7, volume24h: 280_000_000, high24h: 39, low24h: 36, fundingRate: 0.01, openInterest: nil),
            CoinMarketData(symbol: "LINKUSDT", price: 22, change24h: 4.2, volume24h: 350_000_000, high24h: 23, low24h: 21, fundingRate: 0.008, openInterest: nil),
        ]
        
        await MainActor.run {
            coins = mockCoins
            isLoading = false
        }
    }
    
    private func toggleFavorite(_ symbol: String) {
        if favorites.contains(symbol) {
            favorites.remove(symbol)
        } else {
            favorites.insert(symbol)
        }
        saveFavorites()
    }
    
    private func loadFavorites() {
        if let saved = UserDefaults.standard.array(forKey: "market_favorites") as? [String] {
            favorites = Set(saved)
        }
    }
    
    private func saveFavorites() {
        UserDefaults.standard.set(Array(favorites), forKey: "market_favorites")
    }
}

// MARK: - Coin Row
struct CoinRow: View {
    let coin: CoinMarketData
    let isFavorite: Bool
    let onTap: () -> Void
    let onFavorite: () -> Void
    
    var body: some View {
        Button {
            onTap()
        } label: {
            HStack {
                // Favorite Button
                Button {
                    onFavorite()
                } label: {
                    Image(systemName: isFavorite ? "star.fill" : "star")
                        .foregroundColor(isFavorite ? .yellow : .secondary)
                        .font(.caption)
                }
                .buttonStyle(.plain)
                
                // Symbol
                VStack(alignment: .leading, spacing: 2) {
                    Text(coin.symbol.replacingOccurrences(of: "USDT", with: ""))
                        .font(.headline.bold())
                        .foregroundColor(.white)
                    
                    Text("USDT")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                .frame(width: 70, alignment: .leading)
                
                Spacer()
                
                // Price
                VStack(alignment: .trailing, spacing: 2) {
                    Text(coin.priceDisplay)
                        .font(.subheadline.bold())
                        .foregroundColor(.white)
                    
                    Text(coin.volumeDisplay)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                .frame(width: 100, alignment: .trailing)
                
                // Change
                Text(coin.changeDisplay)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                    .frame(width: 80)
                    .padding(.vertical, 8)
                    .background(coin.changeColor)
                    .cornerRadius(8)
            }
            .padding(.horizontal)
            .padding(.vertical, 12)
            .background(Color.enlikoSurface)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Coin Detail Sheet
struct CoinDetailSheet: View {
    let coin: CoinMarketData
    let isFavorite: Bool
    let onToggleFavorite: () -> Void
    
    @Environment(\.dismiss) var dismiss
    @State private var showChart = false
    @State private var showOrderbook = false
    @State private var showTrade = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    VStack(spacing: 8) {
                        Text(coin.symbol)
                            .font(.largeTitle.bold())
                        
                        Text(coin.priceDisplay)
                            .font(.title.bold())
                            .foregroundColor(.enlikoPrimary)
                        
                        Text(coin.changeDisplay)
                            .font(.headline)
                            .foregroundColor(coin.changeColor)
                    }
                    .padding(.top)
                    
                    // Stats Grid
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                        statCard("24h High", String(format: "$%.2f", coin.high24h ?? 0), .green)
                        statCard("24h Low", String(format: "$%.2f", coin.low24h ?? 0), .red)
                        statCard("24h Volume", coin.volumeDisplay, .secondary)
                        
                        if let funding = coin.fundingRate {
                            statCard("Funding Rate", String(format: "%.4f%%", funding), funding >= 0 ? .green : .red)
                        }
                        
                        if let oi = coin.openInterest {
                            statCard("Open Interest", formatNumber(oi), .secondary)
                        }
                    }
                    .padding()
                    
                    // Action Buttons
                    VStack(spacing: 12) {
                        HStack(spacing: 12) {
                            Button {
                                showChart = true
                            } label: {
                                Label("Chart", systemImage: "chart.xyaxis.line")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.enlikoSurface)
                                    .foregroundColor(.white)
                                    .cornerRadius(12)
                            }
                            
                            Button {
                                showOrderbook = true
                            } label: {
                                Label("Orderbook", systemImage: "list.bullet.rectangle")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.enlikoSurface)
                                    .foregroundColor(.white)
                                    .cornerRadius(12)
                            }
                        }
                        
                        HStack(spacing: 12) {
                            Button {
                                showTrade = true
                            } label: {
                                HStack {
                                    Image(systemName: "arrow.up.circle.fill")
                                    Text("Long")
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.green)
                                .foregroundColor(.white)
                                .cornerRadius(12)
                            }
                            
                            Button {
                                showTrade = true
                            } label: {
                                HStack {
                                    Image(systemName: "arrow.down.circle.fill")
                                    Text("Short")
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.red)
                                .foregroundColor(.white)
                                .cornerRadius(12)
                            }
                        }
                    }
                    .padding()
                }
            }
            .background(Color.enlikoBackground)
            .navigationTitle(coin.symbol)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button { dismiss() } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
                
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        onToggleFavorite()
                    } label: {
                        Image(systemName: isFavorite ? "star.fill" : "star")
                            .foregroundColor(isFavorite ? .yellow : .secondary)
                    }
                }
            }
            .sheet(isPresented: $showChart) {
                ChartView(symbol: coin.symbol)
            }
            .sheet(isPresented: $showOrderbook) {
                OrderbookView(symbol: coin.symbol)
            }
            .sheet(isPresented: $showTrade) {
                AdvancedTradingView()
            }
        }
    }
    
    private func statCard(_ title: String, _ value: String, _ color: Color) -> some View {
        VStack(spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.headline.bold())
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(12)
    }
    
    private func formatNumber(_ num: Double) -> String {
        if num >= 1_000_000_000 {
            return String(format: "$%.2fB", num / 1_000_000_000)
        } else if num >= 1_000_000 {
            return String(format: "$%.2fM", num / 1_000_000)
        }
        return String(format: "$%.0f", num)
    }
}

#Preview {
    NavigationStack {
        MarketHubView()
            .environmentObject(AppState.shared)
            .preferredColorScheme(.dark)
    }
}
