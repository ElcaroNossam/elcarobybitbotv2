//
//  ScreenerService.swift
//  LyxenTrading
//
//  Market screener service with real-time data
//

import Foundation
import Combine

// MARK: - Screener Models
struct ScreenerSymbol: Codable, Identifiable {
    var id: String { symbol }
    
    let symbol: String
    let price: Double
    let change24h: Double
    let volume24h: Double
    let oiChange: Double?
    let sentiment: String?
    let signalStrength: Int?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case price
        case change24h = "change_24h"
        case volume24h = "volume_24h"
        case oiChange = "oi_change"
        case sentiment
        case signalStrength = "signal_strength"
    }
}

struct ScreenerOverview: Codable {
    let totalSymbols: Int
    let bullishCount: Int
    let bearishCount: Int
    let neutralCount: Int
    let topGainers: [ScreenerSymbol]
    let topLosers: [ScreenerSymbol]
    let highVolume: [ScreenerSymbol]
    
    enum CodingKeys: String, CodingKey {
        case totalSymbols = "total_symbols"
        case bullishCount = "bullish_count"
        case bearishCount = "bearish_count"
        case neutralCount = "neutral_count"
        case topGainers = "top_gainers"
        case topLosers = "top_losers"
        case highVolume = "high_volume"
    }
}

struct SymbolDetails: Codable {
    let symbol: String
    let price: Double
    let change24h: Double
    let volume24h: Double
    let high24h: Double
    let low24h: Double
    let openInterest: Double?
    let fundingRate: Double?
    let indicators: SymbolIndicators?
    
    enum CodingKeys: String, CodingKey {
        case symbol, price
        case change24h = "change_24h"
        case volume24h = "volume_24h"
        case high24h = "high_24h"
        case low24h = "low_24h"
        case openInterest = "open_interest"
        case fundingRate = "funding_rate"
        case indicators
    }
}

struct SymbolIndicators: Codable {
    let rsi: Double?
    let macd: Double?
    let macdSignal: Double?
    let bbUpper: Double?
    let bbLower: Double?
    let ema20: Double?
    let ema50: Double?
    let atr: Double?
    
    enum CodingKeys: String, CodingKey {
        case rsi
        case macd
        case macdSignal = "macd_signal"
        case bbUpper = "bb_upper"
        case bbLower = "bb_lower"
        case ema20 = "ema_20"
        case ema50 = "ema_50"
        case atr
    }
}

// MARK: - Screener Service
class ScreenerService: ObservableObject {
    static let shared = ScreenerService()
    
    @Published var symbols: [ScreenerSymbol] = []
    @Published var overview: ScreenerOverview?
    @Published var selectedSymbol: SymbolDetails?
    @Published var isLoading = false
    @Published var filter: ScreenerFilter = .all
    
    private let network = NetworkService.shared
    private var cancellables = Set<AnyCancellable>()
    
    enum ScreenerFilter: String, CaseIterable {
        case all = "all"
        case gainers = "gainers"
        case losers = "losers"
        case volume = "volume"
        case bullish = "bullish"
        case bearish = "bearish"
    }
    
    private init() {}
    
    // MARK: - Fetch Symbols
    @MainActor
    func fetchSymbols(filter: ScreenerFilter = .all) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response: APIResponse<[ScreenerSymbol]> = try await network.get(
                Config.Endpoints.screenerSymbols,
                params: ["filter": filter.rawValue]
            )
            
            if let symbols = response.data {
                self.symbols = symbols
            }
        } catch {
            print("Failed to fetch screener symbols: \(error)")
        }
    }
    
    // MARK: - Fetch Overview
    @MainActor
    func fetchOverview() async {
        do {
            let response: APIResponse<ScreenerOverview> = try await network.get(Config.Endpoints.screenerOverview)
            
            if let overview = response.data {
                self.overview = overview
            }
        } catch {
            print("Failed to fetch screener overview: \(error)")
        }
    }
    
    // MARK: - Fetch Symbol Details
    @MainActor
    func fetchSymbolDetails(symbol: String) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response: APIResponse<SymbolDetails> = try await network.get(
                "\(Config.Endpoints.screenerSymbol)/\(symbol)"
            )
            
            if let details = response.data {
                self.selectedSymbol = details
            }
        } catch {
            print("Failed to fetch symbol details: \(error)")
        }
    }
    
    // MARK: - Refresh All
    @MainActor
    func refreshAll() async {
        async let fetchSymbols: () = fetchSymbols(filter: filter)
        async let fetchOverview: () = fetchOverview()
        _ = await (fetchSymbols, fetchOverview)
    }
}
