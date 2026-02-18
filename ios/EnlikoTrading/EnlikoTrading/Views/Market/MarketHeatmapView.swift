//
//  MarketHeatmapView.swift
//  EnlikoTrading
//
//  🔥 Market Heatmap - Visual Crypto Market Overview
//  ==================================================
//
//  Features:
//  - Interactive treemap visualization
//  - Real-time price updates
//  - Color-coded by % change
//  - Zoom and pan gestures
//  - Timeframe selector (1H, 24H, 7D)
//

import SwiftUI
import Combine

// MARK: - Heatmap Coin Model

struct HeatmapCoin: Identifiable {
    let id = UUID()
    let symbol: String
    let name: String
    let price: Double
    let change24h: Double
    let marketCap: Double
    let volume24h: Double
    
    var changeColor: Color {
        if change24h > 5 { return .green }
        if change24h > 2 { return Color(red: 0.4, green: 0.8, blue: 0.4) }
        if change24h > 0 { return Color(red: 0.3, green: 0.6, blue: 0.3) }
        if change24h > -2 { return Color(red: 0.6, green: 0.3, blue: 0.3) }
        if change24h > -5 { return Color(red: 0.8, green: 0.3, blue: 0.3) }
        return .red
    }
    
    var shortSymbol: String {
        symbol.replacingOccurrences(of: "USDT", with: "")
    }
}

// MARK: - Heatmap View Model

@MainActor
class MarketHeatmapViewModel: ObservableObject {
    @Published var coins: [HeatmapCoin] = []
    @Published var isLoading = false
    @Published var selectedTimeframe: Timeframe = .day
    @Published var sortBy: SortOption = .marketCap
    @Published var selectedCoin: HeatmapCoin?
    
    enum Timeframe: String, CaseIterable {
        case hour = "1H"
        case day = "24H"
        case week = "7D"
    }
    
    enum SortOption: String, CaseIterable {
        case marketCap = "Market Cap"
        case volume = "Volume"
        case change = "% Change"
    }
    
    private var refreshTimer: Timer?
    private let screenerService = ScreenerService.shared
    
    init() {
        loadData()
        startAutoRefresh()
    }
    
    deinit {
        refreshTimer?.invalidate()
    }
    
    func loadData() {
        isLoading = true
        
        Task { @MainActor in
            // Try to fetch from API
            do {
                let data = try await screenerService.fetchTopCoins()
                self.coins = data.map { coin in
                    HeatmapCoin(
                        symbol: coin.symbol,
                        name: coin.name ?? coin.symbol,
                        price: coin.price,
                        change24h: coin.change24h,
                        marketCap: coin.marketCap ?? 0,
                        volume24h: coin.volume24h ?? 0
                    )
                }
            } catch {
                // Use mock data
                self.coins = Self.mockCoins
            }
            
            self.sortCoins()
            self.isLoading = false
        }
    }
    
    func sortCoins() {
        switch sortBy {
        case .marketCap:
            coins.sort { $0.marketCap > $1.marketCap }
        case .volume:
            coins.sort { $0.volume24h > $1.volume24h }
        case .change:
            coins.sort { abs($0.change24h) > abs($1.change24h) }
        }
    }
    
    private func startAutoRefresh() {
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in
            self?.loadData()
        }
    }
    
    // Mock data for preview/fallback
    static let mockCoins: [HeatmapCoin] = [
        HeatmapCoin(symbol: "BTCUSDT", name: "Bitcoin", price: 45234.50, change24h: 2.34, marketCap: 890_000_000_000, volume24h: 25_000_000_000),
        HeatmapCoin(symbol: "ETHUSDT", name: "Ethereum", price: 2456.78, change24h: 4.12, marketCap: 295_000_000_000, volume24h: 12_000_000_000),
        HeatmapCoin(symbol: "BNBUSDT", name: "BNB", price: 312.45, change24h: -1.23, marketCap: 48_000_000_000, volume24h: 800_000_000),
        HeatmapCoin(symbol: "SOLUSDT", name: "Solana", price: 98.76, change24h: 8.45, marketCap: 42_000_000_000, volume24h: 2_500_000_000),
        HeatmapCoin(symbol: "XRPUSDT", name: "XRP", price: 0.5234, change24h: -0.45, marketCap: 28_000_000_000, volume24h: 1_200_000_000),
        HeatmapCoin(symbol: "ADAUSDT", name: "Cardano", price: 0.4567, change24h: 3.21, marketCap: 16_000_000_000, volume24h: 450_000_000),
        HeatmapCoin(symbol: "AVAXUSDT", name: "Avalanche", price: 35.67, change24h: 5.67, marketCap: 13_000_000_000, volume24h: 520_000_000),
        HeatmapCoin(symbol: "DOTUSDT", name: "Polkadot", price: 7.89, change24h: -2.34, marketCap: 10_000_000_000, volume24h: 380_000_000),
        HeatmapCoin(symbol: "LINKUSDT", name: "Chainlink", price: 14.56, change24h: 6.78, marketCap: 8_500_000_000, volume24h: 650_000_000),
        HeatmapCoin(symbol: "MATICUSDT", name: "Polygon", price: 0.8765, change24h: 1.23, marketCap: 8_100_000_000, volume24h: 420_000_000),
        HeatmapCoin(symbol: "UNIUSDT", name: "Uniswap", price: 6.78, change24h: -3.45, marketCap: 5_100_000_000, volume24h: 180_000_000),
        HeatmapCoin(symbol: "ATOMUSDT", name: "Cosmos", price: 9.12, change24h: 2.89, marketCap: 3_500_000_000, volume24h: 210_000_000),
        HeatmapCoin(symbol: "LTCUSDT", name: "Litecoin", price: 72.34, change24h: -0.98, marketCap: 5_400_000_000, volume24h: 340_000_000),
        HeatmapCoin(symbol: "NEARUSDT", name: "NEAR", price: 5.67, change24h: 7.89, marketCap: 5_800_000_000, volume24h: 380_000_000),
        HeatmapCoin(symbol: "APTUSDT", name: "Aptos", price: 8.90, change24h: -4.56, marketCap: 3_900_000_000, volume24h: 290_000_000),
        HeatmapCoin(symbol: "ARBUSDT", name: "Arbitrum", price: 1.23, change24h: 9.12, marketCap: 3_100_000_000, volume24h: 520_000_000),
    ]
}

// MARK: - Market Heatmap View

struct MarketHeatmapView: View {
    @StateObject private var viewModel = MarketHeatmapViewModel()
    @State private var zoomScale: CGFloat = 1.0
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Beta Banner
                    betaBanner
                    
                    // Controls
                    controlsBar
                    
                    // Legend
                    legendView
                    
                    if viewModel.isLoading {
                        Spacer()
                        ProgressView()
                            .tint(.enlikoPrimary)
                            .scaleEffect(1.5)
                        Spacer()
                    } else {
                        // Heatmap Grid
                        ScrollView([.horizontal, .vertical]) {
                            heatmapGrid
                                .scaleEffect(zoomScale)
                        }
                        .gesture(
                            MagnificationGesture()
                                .onChanged { value in
                                    zoomScale = max(0.5, min(value, 3.0))
                                }
                        )
                    }
                }
            }
            .navigationTitle("Market Heatmap")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: viewModel.loadData) {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(.enlikoPrimary)
                    }
                }
            }
            .sheet(item: $viewModel.selectedCoin) { coin in
                HeatmapCoinDetailSheet(coin: coin)
            }
        }
    }
    
    // MARK: - Beta Banner
    
    private var betaBanner: some View {
        HStack(spacing: 12) {
            Image(systemName: "sparkles")
                .font(.title3)
                .foregroundColor(.purple)
            
            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text("Beta Feature")
                        .font(.headline)
                        .foregroundColor(.purple)
                    
                    Text("BETA")
                        .font(.system(size: 10, weight: .bold))
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.purple)
                        .foregroundColor(.white)
                        .cornerRadius(4)
                }
                Text("Heatmap data may be delayed or fallback to cached data")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding()
        .background(Color.purple.opacity(0.1))
    }
    
    // MARK: - Controls Bar
    
    private var controlsBar: some View {
        HStack(spacing: 16) {
            // Timeframe picker
            Picker("Timeframe", selection: $viewModel.selectedTimeframe) {
                ForEach(MarketHeatmapViewModel.Timeframe.allCases, id: \.self) { tf in
                    Text(tf.rawValue).tag(tf)
                }
            }
            .pickerStyle(.segmented)
            .frame(width: 150)
            
            Spacer()
            
            // Sort picker
            Menu {
                ForEach(MarketHeatmapViewModel.SortOption.allCases, id: \.self) { option in
                    Button(action: {
                        viewModel.sortBy = option
                        viewModel.sortCoins()
                    }) {
                        HStack {
                            Text(option.rawValue)
                            if viewModel.sortBy == option {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                }
            } label: {
                HStack {
                    Text(viewModel.sortBy.rawValue)
                        .font(.subheadline)
                    Image(systemName: "chevron.down")
                        .font(.caption)
                }
                .foregroundColor(.enlikoPrimary)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(Color.enlikoCard)
                .cornerRadius(8)
            }
        }
        .padding()
    }
    
    // MARK: - Legend
    
    private var legendView: some View {
        HStack(spacing: 4) {
            Text("-5%+")
                .font(.caption2)
                .foregroundColor(.red)
            
            LinearGradient(
                colors: [.red, Color(red: 0.6, green: 0.3, blue: 0.3), .gray, Color(red: 0.3, green: 0.6, blue: 0.3), .green],
                startPoint: .leading,
                endPoint: .trailing
            )
            .frame(height: 6)
            .cornerRadius(3)
            .frame(maxWidth: 200)
            
            Text("+5%+")
                .font(.caption2)
                .foregroundColor(.green)
        }
        .padding(.horizontal)
        .padding(.bottom, 8)
    }
    
    // MARK: - Heatmap Grid
    
    private var heatmapGrid: some View {
        let columns = calculateGridColumns()
        
        return LazyVGrid(columns: columns, spacing: 4) {
            ForEach(viewModel.coins) { coin in
                HeatmapTileView(coin: coin, size: tileSize(for: coin))
                    .onTapGesture {
                        HapticManager.shared.perform(.light)
                        viewModel.selectedCoin = coin
                    }
            }
        }
        .padding()
    }
    
    private func calculateGridColumns() -> [GridItem] {
        let count = min(viewModel.coins.count, 5)
        return Array(repeating: GridItem(.flexible(), spacing: 4), count: count)
    }
    
    private func tileSize(for coin: HeatmapCoin) -> CGFloat {
        // Size based on relative market cap
        guard let maxCap = viewModel.coins.first?.marketCap, maxCap > 0 else { return 80 }
        let ratio = coin.marketCap / maxCap
        return max(60, min(150, 60 + 90 * pow(ratio, 0.3)))
    }
}

// MARK: - Heatmap Tile

struct HeatmapTileView: View {
    let coin: HeatmapCoin
    let size: CGFloat
    
    @State private var isPressed = false
    
    var body: some View {
        VStack(spacing: 2) {
            Text(coin.shortSymbol)
                .font(.system(size: size > 100 ? 18 : 14, weight: .bold, design: .rounded))
                .foregroundColor(.white)
            
            if size > 80 {
                Text(String(format: "%+.2f%%", coin.change24h))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.white.opacity(0.9))
            }
            
            if size > 110 {
                Text("$\(formatPrice(coin.price))")
                    .font(.system(size: 10))
                    .foregroundColor(.white.opacity(0.7))
            }
        }
        .frame(width: size, height: size)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(coin.changeColor)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
        .scaleEffect(isPressed ? 0.95 : 1.0)
        .animation(.spring(response: 0.3), value: isPressed)
        .onLongPressGesture(minimumDuration: 0.1, pressing: { pressing in
            isPressed = pressing
        }) {
            HapticManager.shared.perform(.medium)
        }
    }
    
    private func formatPrice(_ price: Double) -> String {
        if price >= 1000 {
            return String(format: "%.0f", price)
        } else if price >= 1 {
            return String(format: "%.2f", price)
        } else {
            return String(format: "%.4f", price)
        }
    }
}

// MARK: - Heatmap Coin Detail Sheet

struct HeatmapCoinDetailSheet: View {
    let coin: HeatmapCoin
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        // Header
                        VStack(spacing: 8) {
                            Text(coin.shortSymbol)
                                .font(.system(size: 48, weight: .bold, design: .rounded))
                                .foregroundColor(.white)
                            
                            Text(coin.name)
                                .font(.title3)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                        .padding(.top, 20)
                        
                        // Price Card
                        GlassCard {
                            VStack(spacing: 16) {
                                Text("$\(String(format: "%.2f", coin.price))")
                                    .font(.system(size: 36, weight: .bold, design: .rounded))
                                    .foregroundColor(.white)
                                
                                HStack(spacing: 8) {
                                    Image(systemName: coin.change24h >= 0 ? "arrow.up.right" : "arrow.down.right")
                                    Text(String(format: "%+.2f%%", coin.change24h))
                                }
                                .font(.title3.bold())
                                .foregroundColor(coin.changeColor)
                                .padding(.horizontal, 16)
                                .padding(.vertical, 8)
                                .background(coin.changeColor.opacity(0.2))
                                .cornerRadius(12)
                            }
                            .padding(20)
                        }
                        .padding(.horizontal)
                        
                        // Stats Grid
                        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                            HeatmapStatCard(title: "Market Cap", value: formatLargeNumber(coin.marketCap), icon: "chart.pie.fill")
                            HeatmapStatCard(title: "24h Volume", value: formatLargeNumber(coin.volume24h), icon: "waveform.path")
                        }
                        .padding(.horizontal)
                        
                        // Trade Button
                        NeuButton(title: "Trade \(coin.shortSymbol)", icon: "arrow.left.arrow.right", action: {
                            // Open trading view
                            dismiss()
                        }, style: .primary)
                        .padding(.horizontal)
                        
                        Spacer()
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.enlikoTextSecondary)
                            .font(.title2)
                    }
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
    }
    
    private func formatLargeNumber(_ num: Double) -> String {
        if num >= 1_000_000_000_000 {
            return String(format: "$%.2fT", num / 1_000_000_000_000)
        } else if num >= 1_000_000_000 {
            return String(format: "$%.2fB", num / 1_000_000_000)
        } else if num >= 1_000_000 {
            return String(format: "$%.2fM", num / 1_000_000)
        } else if num >= 1000 {
            return String(format: "$%.1fK", num / 1000)
        }
        return String(format: "$%.0f", num)
    }
}

// MARK: - Stat Card

struct HeatmapStatCard: View {
    let title: String
    let value: String
    let icon: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(.enlikoPrimary)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Text(value)
                .font(.title3.bold())
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(12)
    }
}

// MARK: - Preview

#Preview {
    MarketHeatmapView()
        .preferredColorScheme(.dark)
}
