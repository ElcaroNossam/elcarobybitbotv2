//
//  MarketOverviewView.swift
//  EnlikoTrading
//
//  Market Overview — BTC, Fear & Greed, S&P 500, Gold, Dominance,
//  Top Coins, Altseason Index, Total Market Cap
//  Data from /api/home/market endpoint
//

import SwiftUI
import Charts
import Combine

// MARK: - Market Overview View
struct MarketOverviewView: View {
    @StateObject private var viewModel = MarketOverviewViewModel()
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                // BTC Price Hero Card
                btcHeroCard
                
                // Fear & Greed + Altseason Row
                HStack(spacing: 12) {
                    fearGreedCard
                    altseasonCard
                }
                
                // Traditional Markets Row
                HStack(spacing: 12) {
                    sp500Card
                    goldCard
                }
                
                // Dominance Section
                dominanceSection
                
                // ALT Signal
                altSignalCard
                
                // Top Coins by Market Cap
                topCoinsSection
                
                // Total Market Cap
                marketCapSection
                
                // Navigate to full screener
                NavigationLink {
                    MarketHubView()
                } label: {
                    HStack {
                        Image(systemName: "chart.bar.fill")
                        Text("full_screener".localized)
                            .font(.subheadline.bold())
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .foregroundColor(.enlikoPrimary)
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                }
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 20)
        }
        .background(Color.enlikoBackground)
        .navigationTitle("market_overview".localized)
        .navigationBarTitleDisplayMode(.large)
        .refreshable {
            await viewModel.refresh()
        }
        .task {
            await viewModel.refresh()
        }
    }
    
    // MARK: - BTC Hero Card
    private var btcHeroCard: some View {
        VStack(spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 6) {
                    HStack(spacing: 8) {
                        Text("₿")
                            .font(.system(size: 28, weight: .bold, design: .rounded))
                            .foregroundColor(.orange)
                        Text("Bitcoin")
                            .font(.title2.bold())
                            .foregroundColor(.white)
                    }
                    
                    Text(viewModel.btcPrice.formattedLargePrice)
                        .font(.system(size: 36, weight: .heavy, design: .rounded))
                        .foregroundColor(.white)
                    
                    HStack(spacing: 6) {
                        Image(systemName: viewModel.btcChange >= 0 ? "arrow.up.right" : "arrow.down.right")
                            .font(.caption.bold())
                        Text(String(format: "%@%.2f%%", viewModel.btcChange >= 0 ? "+" : "", viewModel.btcChange))
                            .font(.subheadline.bold())
                    }
                    .foregroundColor(viewModel.btcChange >= 0 ? .enlikoGreen : .enlikoRed)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background((viewModel.btcChange >= 0 ? Color.enlikoGreen : Color.enlikoRed).opacity(0.15))
                    .cornerRadius(8)
                }
                
                Spacer()
                
                // BTC 7d mini chart
                if !viewModel.btcChartData.isEmpty {
                    Chart {
                        ForEach(Array(viewModel.btcChartData.enumerated()), id: \.offset) { idx, point in
                            LineMark(
                                x: .value("Time", idx),
                                y: .value("Price", point)
                            )
                            .foregroundStyle(viewModel.btcChange >= 0 ? Color.enlikoGreen : Color.enlikoRed)
                            
                            AreaMark(
                                x: .value("Time", idx),
                                y: .value("Price", point)
                            )
                            .foregroundStyle(
                                LinearGradient(
                                    colors: [
                                        (viewModel.btcChange >= 0 ? Color.enlikoGreen : Color.enlikoRed).opacity(0.3),
                                        .clear
                                    ],
                                    startPoint: .top,
                                    endPoint: .bottom
                                )
                            )
                        }
                    }
                    .chartXAxis(.hidden)
                    .chartYAxis(.hidden)
                    .frame(width: 120, height: 60)
                }
            }
            
            // 24h High/Low/Volume
            HStack(spacing: 0) {
                miniStat("24h High", viewModel.btcHigh.formattedLargePrice)
                Divider().frame(height: 30).background(Color.enlikoBorder)
                miniStat("24h Low", viewModel.btcLow.formattedLargePrice)
                Divider().frame(height: 30).background(Color.enlikoBorder)
                miniStat("Volume", viewModel.btcVolume.compactFormatted)
            }
        }
        .padding(20)
        .background(
            ZStack {
                LinearGradient(
                    colors: [Color.orange.opacity(0.15), Color.enlikoCard],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                RoundedRectangle(cornerRadius: 20)
                    .fill(.ultraThinMaterial.opacity(0.3))
            }
        )
        .cornerRadius(20)
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(Color.orange.opacity(0.3), lineWidth: 1)
        )
    }
    
    // MARK: - Fear & Greed Card
    private var fearGreedCard: some View {
        VStack(spacing: 10) {
            Text("Fear & Greed")
                .font(.caption)
                .foregroundColor(.secondary)
            
            ZStack {
                Circle()
                    .trim(from: 0, to: 0.75)
                    .stroke(Color.enlikoBorder, lineWidth: 6)
                    .rotationEffect(.degrees(135))
                    .frame(width: 70, height: 70)
                
                Circle()
                    .trim(from: 0, to: 0.75 * (Double(viewModel.fearGreedValue) / 100))
                    .stroke(
                        fearGreedColor,
                        style: StrokeStyle(lineWidth: 6, lineCap: .round)
                    )
                    .rotationEffect(.degrees(135))
                    .frame(width: 70, height: 70)
                
                VStack(spacing: 0) {
                    Text("\(viewModel.fearGreedValue)")
                        .font(.title2.bold())
                        .foregroundColor(.white)
                }
            }
            
            Text(viewModel.fearGreedLabel)
                .font(.caption.bold())
                .foregroundColor(fearGreedColor)
                .lineLimit(1)
                .minimumScaleFactor(0.7)
        }
        .frame(maxWidth: .infinity)
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.enlikoBorder, lineWidth: 0.5)
        )
    }
    
    private var fearGreedColor: Color {
        switch viewModel.fearGreedValue {
        case 0..<25: return .red
        case 25..<45: return .orange
        case 45..<55: return .yellow
        case 55..<75: return .enlikoGreen
        default: return .green
        }
    }
    
    // MARK: - Altseason Card
    private var altseasonCard: some View {
        VStack(spacing: 10) {
            Text("Altseason Index")
                .font(.caption)
                .foregroundColor(.secondary)
            
            ZStack {
                Circle()
                    .trim(from: 0, to: 0.75)
                    .stroke(Color.enlikoBorder, lineWidth: 6)
                    .rotationEffect(.degrees(135))
                    .frame(width: 70, height: 70)
                
                Circle()
                    .trim(from: 0, to: 0.75 * (Double(viewModel.altseasonIndex) / 100))
                    .stroke(
                        altseasonColor,
                        style: StrokeStyle(lineWidth: 6, lineCap: .round)
                    )
                    .rotationEffect(.degrees(135))
                    .frame(width: 70, height: 70)
                
                VStack(spacing: 0) {
                    Text("\(viewModel.altseasonIndex)")
                        .font(.title2.bold())
                        .foregroundColor(.white)
                }
            }
            
            Text(viewModel.altseasonIndex >= 75 ? "🚀 Altseason" : viewModel.altseasonIndex <= 25 ? "❄️ BTC Season" : "⚖️ Neutral")
                .font(.caption.bold())
                .foregroundColor(altseasonColor)
                .lineLimit(1)
                .minimumScaleFactor(0.7)
        }
        .frame(maxWidth: .infinity)
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.enlikoBorder, lineWidth: 0.5)
        )
    }
    
    private var altseasonColor: Color {
        switch viewModel.altseasonIndex {
        case 0..<25: return .cyan
        case 25..<50: return .blue
        case 50..<75: return .purple
        default: return .enlikoPrimary
        }
    }
    
    // MARK: - S&P 500 Card
    private var sp500Card: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 6) {
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .foregroundColor(.blue)
                    .font(.caption)
                Text("S&P 500")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Text(viewModel.sp500Price > 0 ? String(format: "$%.0f", viewModel.sp500Price) : "—")
                .font(.title3.bold())
                .foregroundColor(.white)
            
            HStack(spacing: 4) {
                Image(systemName: viewModel.sp500Change >= 0 ? "arrow.up.right" : "arrow.down.right")
                    .font(.caption2)
                Text(String(format: "%@%.2f%%", viewModel.sp500Change >= 0 ? "+" : "", viewModel.sp500Change))
                    .font(.caption.bold())
            }
            .foregroundColor(viewModel.sp500Change >= 0 ? .enlikoGreen : .enlikoRed)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.enlikoBorder, lineWidth: 0.5)
        )
    }
    
    // MARK: - Gold Card
    private var goldCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 6) {
                Text("🥇")
                    .font(.caption)
                Text("Gold")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Text(viewModel.goldPrice > 0 ? String(format: "$%.0f", viewModel.goldPrice) : "—")
                .font(.title3.bold())
                .foregroundColor(.white)
            
            HStack(spacing: 4) {
                Image(systemName: viewModel.goldChange >= 0 ? "arrow.up.right" : "arrow.down.right")
                    .font(.caption2)
                Text(String(format: "%@%.2f%%", viewModel.goldChange >= 0 ? "+" : "", viewModel.goldChange))
                    .font(.caption.bold())
            }
            .foregroundColor(viewModel.goldChange >= 0 ? .enlikoGreen : .enlikoRed)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.enlikoBorder, lineWidth: 0.5)
        )
    }
    
    // MARK: - Dominance Section
    private var dominanceSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Dominance")
                .font(.headline)
                .foregroundColor(.white)
            
            HStack(spacing: 12) {
                dominanceBar(label: "BTC", value: viewModel.btcDominance, color: .orange)
                dominanceBar(label: "USDT", value: viewModel.usdtDominance, color: .green)
            }
        }
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    private func dominanceBar(label: String, value: Double, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(label)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                Spacer()
                Text(String(format: "%.1f%%", value))
                    .font(.subheadline.bold())
                    .foregroundColor(color)
            }
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.enlikoBorder)
                    RoundedRectangle(cornerRadius: 4)
                        .fill(color)
                        .frame(width: geo.size.width * min(value / 100, 1))
                }
            }
            .frame(height: 8)
        }
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - ALT Signal Card
    private var altSignalCard: some View {
        HStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 4) {
                Text("ALT Signal")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                Text(viewModel.altSignal)
                    .font(.title2.bold())
                    .foregroundColor(altSignalColor)
            }
            
            Spacer()
            
            // Signal icon
            ZStack {
                Circle()
                    .fill(altSignalColor.opacity(0.2))
                    .frame(width: 50, height: 50)
                Image(systemName: altSignalIcon)
                    .font(.title2)
                    .foregroundColor(altSignalColor)
            }
        }
        .padding(16)
        .background(
            LinearGradient(
                colors: [altSignalColor.opacity(0.1), Color.enlikoSurface],
                startPoint: .leading,
                endPoint: .trailing
            )
        )
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(altSignalColor.opacity(0.3), lineWidth: 1)
        )
    }
    
    private var altSignalColor: Color {
        switch viewModel.altSignal {
        case "LONG": return .enlikoGreen
        case "SHORT": return .enlikoRed
        default: return .yellow
        }
    }
    
    private var altSignalIcon: String {
        switch viewModel.altSignal {
        case "LONG": return "arrow.up.circle.fill"
        case "SHORT": return "arrow.down.circle.fill"
        default: return "arrow.left.arrow.right.circle.fill"
        }
    }
    
    // MARK: - Top Coins Section
    private var topCoinsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Top Coins by Dominance")
                .font(.headline)
                .foregroundColor(.white)
            
            if viewModel.topCoins.isEmpty && !viewModel.isLoading {
                Text("No data available")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
            } else {
                ForEach(viewModel.topCoins) { coin in
                    HStack(spacing: 12) {
                        Text(coin.symbol)
                            .font(.subheadline.bold())
                            .foregroundColor(.white)
                            .frame(width: 50, alignment: .leading)
                        
                        // Dominance bar
                        GeometryReader { geo in
                            ZStack(alignment: .leading) {
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.enlikoBorder)
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.enlikoPrimary)
                                    .frame(width: geo.size.width * min(coin.dominance / 20, 1))
                            }
                        }
                        .frame(height: 8)
                        
                        VStack(alignment: .trailing, spacing: 2) {
                            Text(String(format: "%.1f%%", coin.dominance))
                                .font(.caption.bold())
                                .foregroundColor(.white)
                            Text(String(format: "$%.0fB", coin.mcapB))
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                        .frame(width: 60)
                        
                        // 24h change
                        Text(String(format: "%@%.1f%%", coin.change24h >= 0 ? "+" : "", coin.change24h))
                            .font(.caption.bold())
                            .foregroundColor(coin.change24h >= 0 ? .enlikoGreen : .enlikoRed)
                            .frame(width: 55, alignment: .trailing)
                    }
                    .padding(.vertical, 6)
                    
                    if coin.id != viewModel.topCoins.last?.id {
                        Divider().background(Color.enlikoBorder)
                    }
                }
            }
        }
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Total Market Cap
    private var marketCapSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Total Market Cap")
                .font(.headline)
                .foregroundColor(.white)
            
            HStack(spacing: 12) {
                mcapCard("Total", viewModel.totalMarketCap1, .enlikoPrimary)
                mcapCard("Ex-BTC", viewModel.totalMarketCap2, .purple)
                mcapCard("Ex-ETH", viewModel.totalMarketCap3, .cyan)
            }
        }
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    private func mcapCard(_ label: String, _ value: Double, _ color: Color) -> some View {
        VStack(spacing: 6) {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value > 0 ? String(format: "$%.2fT", value) : "—")
                .font(.subheadline.bold())
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
        .padding(12)
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
    
    // MARK: - Helper
    private func miniStat(_ label: String, _ value: String) -> some View {
        VStack(spacing: 4) {
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
            Text(value)
                .font(.caption.bold())
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Top Coin Model
struct TopCoinItem: Codable, Identifiable {
    var id: String { symbol }
    let symbol: String
    let mcapB: Double
    let dominance: Double
    let price: Double
    let change24h: Double
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case mcapB = "mcap_b"
        case dominance
        case price
        case change24h = "change_24h"
    }
}

// MARK: - Market Data Response
struct MarketDataResponse: Codable {
    let btc: BTCData?
    let usdtDominance: Double?
    let sp500: SP500Data?
    let gold: GoldData?
    let fearGreed: FearGreedData?
    let altseasonIndex: Int?
    let altSignal: String?
    let topCoins: [TopCoinItem]?
    let totalMarketCap: TotalMarketCapData?
    
    enum CodingKeys: String, CodingKey {
        case btc
        case usdtDominance = "usdt_dominance"
        case sp500, gold
        case fearGreed = "fear_greed"
        case altseasonIndex = "altseason_index"
        case altSignal = "alt_signal"
        case topCoins = "top_coins"
        case totalMarketCap = "total_market_cap"
    }
    
    struct BTCData: Codable {
        let price: Double?
        let change24h: Double?
        let dominance: Double?
        
        enum CodingKeys: String, CodingKey {
            case price
            case change24h = "change_24h"
            case dominance
        }
    }
    
    struct SP500Data: Codable {
        let price: Double?
        let change: Double?
    }
    
    struct GoldData: Codable {
        let price: Double?
        let change: Double?
    }
    
    struct FearGreedData: Codable {
        let value: Int?
        let label: String?
    }
    
    struct TotalMarketCapData: Codable {
        let total1: Double?
        let total2: Double?
        let total3: Double?
    }
}

// MARK: - BTC Chart Response
struct BTCChartResponse: Codable {
    let price: Double?
    let change24h: Double?
    let high24h: Double?
    let low24h: Double?
    let volume24h: Double?
    let chart: [[Double]]?
    
    enum CodingKeys: String, CodingKey {
        case price
        case change24h = "change24h"  // source uses "change24h" without underscore
        case high24h = "high24h"
        case low24h = "low24h"
        case volume24h = "volume24h"
        case chart
    }
}

// MARK: - ViewModel
@MainActor
class MarketOverviewViewModel: ObservableObject {
    @Published var isLoading = false
    
    // BTC
    @Published var btcPrice: Double = 0
    @Published var btcChange: Double = 0
    @Published var btcDominance: Double = 0
    @Published var btcHigh: Double = 0
    @Published var btcLow: Double = 0
    @Published var btcVolume: Double = 0
    @Published var btcChartData: [Double] = []
    
    // Market Indices
    @Published var sp500Price: Double = 0
    @Published var sp500Change: Double = 0
    @Published var goldPrice: Double = 0
    @Published var goldChange: Double = 0
    
    // Crypto Metrics
    @Published var usdtDominance: Double = 0
    @Published var fearGreedValue: Int = 0
    @Published var fearGreedLabel: String = "N/A"
    @Published var altseasonIndex: Int = 0
    @Published var altSignal: String = "NEUTRAL"
    
    // Top Coins
    @Published var topCoins: [TopCoinItem] = []
    
    // Market Cap
    @Published var totalMarketCap1: Double = 0
    @Published var totalMarketCap2: Double = 0
    @Published var totalMarketCap3: Double = 0
    
    private let network = NetworkService.shared
    
    func refresh() async {
        isLoading = true
        defer { isLoading = false }
        
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.fetchMarketData() }
            group.addTask { await self.fetchBTCChart() }
        }
    }
    
    private func fetchMarketData() async {
        do {
            let data: MarketDataResponse = try await network.get("/home/market", params: [:])
            
            // BTC
            btcPrice = data.btc?.price ?? 0
            btcChange = data.btc?.change24h ?? 0
            btcDominance = data.btc?.dominance ?? 0
            
            // USDT
            usdtDominance = data.usdtDominance ?? 0
            
            // S&P 500
            sp500Price = data.sp500?.price ?? 0
            sp500Change = data.sp500?.change ?? 0
            
            // Gold
            goldPrice = data.gold?.price ?? 0
            goldChange = data.gold?.change ?? 0
            
            // Fear & Greed
            fearGreedValue = data.fearGreed?.value ?? 0
            fearGreedLabel = data.fearGreed?.label ?? "N/A"
            
            // Altseason
            altseasonIndex = data.altseasonIndex ?? 0
            altSignal = data.altSignal ?? "NEUTRAL"
            
            // Top coins
            topCoins = data.topCoins ?? []
            
            // Market cap
            totalMarketCap1 = data.totalMarketCap?.total1 ?? 0
            totalMarketCap2 = data.totalMarketCap?.total2 ?? 0
            totalMarketCap3 = data.totalMarketCap?.total3 ?? 0
        } catch {
            print("MarketOverview: Failed to fetch market data: \(error)")
        }
    }
    
    private func fetchBTCChart() async {
        do {
            let data: BTCChartResponse = try await network.get("/home/btc", params: [:])
            
            btcHigh = data.high24h ?? 0
            btcLow = data.low24h ?? 0
            btcVolume = data.volume24h ?? 0
            
            // Extract close prices from chart array [[timestamp, closePrice], ...]
            if let chartPoints = data.chart {
                btcChartData = chartPoints.compactMap { point in
                    point.count >= 2 ? point[1] : nil
                }
            }
        } catch {
            print("MarketOverview: Failed to fetch BTC chart: \(error)")
        }
    }
}

// MARK: - Double Extension for large prices
extension Double {
    var formattedLargePrice: String {
        if self >= 10000 {
            return String(format: "$%,.0f", self)
        } else if self >= 100 {
            return String(format: "$%.2f", self)
        } else if self >= 1 {
            return String(format: "$%.4f", self)
        } else if self > 0 {
            return String(format: "$%.6f", self)
        }
        return "$0"
    }
}

#Preview {
    NavigationStack {
        MarketOverviewView()
            .preferredColorScheme(.dark)
    }
}
