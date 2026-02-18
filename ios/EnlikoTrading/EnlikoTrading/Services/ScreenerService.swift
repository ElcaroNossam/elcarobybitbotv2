//
//  ScreenerService.swift
//  EnlikoTrading
//
//  Market screener service with real-time data
//

import Foundation
import Combine

// MARK: - Screener Models

// Response from /screener/symbols endpoint
struct SymbolListResponse: Codable {
    let symbols: [String]
}

// Placeholder for symbol when we only have the name
func ScreenerSymbolPlaceholder(symbol: String) -> ScreenerSymbol {
    // Create a ScreenerSymbol from just the name
    // Use safe decoding instead of force unwrap
    guard let data = try? JSONSerialization.data(withJSONObject: ["symbol": symbol]),
          let decoded = try? JSONDecoder().decode(ScreenerSymbol.self, from: data) else {
        // Fallback: return a minimal valid symbol
        return ScreenerSymbol(symbol: symbol)
    }
    return decoded
}

struct ScreenerSymbol: Codable, Identifiable {
    var id: String { _symbol ?? UUID().uuidString }
    
    private let _symbol: String?
    private let _price: Double?
    private let _change24h: Double?
    private let _volume24h: Double?
    let oiChange: Double?
    let sentiment: String?
    let signalStrength: Int?
    
    var symbol: String { _symbol ?? "UNKNOWN" }
    var price: Double { _price ?? 0 }
    var change24h: Double { _change24h ?? 0 }
    var volume24h: Double { _volume24h ?? 0 }
    
    // Manual initializer for placeholder creation (safe fallback)
    init(symbol: String) {
        self._symbol = symbol
        self._price = nil
        self._change24h = nil
        self._volume24h = nil
        self.oiChange = nil
        self.sentiment = nil
        self.signalStrength = nil
    }
    
    enum CodingKeys: String, CodingKey {
        case _symbol = "symbol"
        case _price = "price"
        case _change24h = "change_24h"
        case _volume24h = "volume_24h"
        case oiChange = "oi_change"
        case sentiment
        case signalStrength = "signal_strength"
    }
}

struct ScreenerOverview: Codable {
    // New API format (from server)
    private let _total: Int?
    private let _gainers: Int?
    private let _losers: Int?
    private let _totalVolume: Double?
    let btc: BTCData?
    let lastUpdate: String?
    
    // Legacy format
    private let _totalSymbols: Int?
    private let _bullishCount: Int?
    private let _bearishCount: Int?
    private let _neutralCount: Int?
    private let _topGainers: [ScreenerSymbol]?
    private let _topLosers: [ScreenerSymbol]?
    private let _highVolume: [ScreenerSymbol]?
    
    // Computed properties with fallbacks
    var totalSymbols: Int { _total ?? _totalSymbols ?? 0 }
    var bullishCount: Int { _gainers ?? _bullishCount ?? 0 }
    var bearishCount: Int { _losers ?? _bearishCount ?? 0 }
    var neutralCount: Int { _neutralCount ?? (totalSymbols - bullishCount - bearishCount) }
    var totalVolume: Double { _totalVolume ?? 0 }
    var topGainers: [ScreenerSymbol] { _topGainers ?? [] }
    var topLosers: [ScreenerSymbol] { _topLosers ?? [] }
    var highVolume: [ScreenerSymbol] { _highVolume ?? [] }
    
    enum CodingKeys: String, CodingKey {
        // New format
        case _total = "total"
        case _gainers = "gainers"
        case _losers = "losers"
        case _totalVolume = "total_volume"
        case btc
        case lastUpdate = "last_update"
        // Legacy format
        case _totalSymbols = "total_symbols"
        case _bullishCount = "bullish_count"
        case _bearishCount = "bearish_count"
        case _neutralCount = "neutral_count"
        case _topGainers = "top_gainers"
        case _topLosers = "top_losers"
        case _highVolume = "high_volume"
    }
}

struct BTCData: Codable {
    let price: Double?
    let change: Double?
}

struct SymbolDetails: Codable {
    private let _symbol: String?
    private let _price: Double?
    private let _change24h: Double?
    private let _volume24h: Double?
    private let _high24h: Double?
    private let _low24h: Double?
    let openInterest: Double?
    let fundingRate: Double?
    let indicators: SymbolIndicators?
    
    var symbol: String { _symbol ?? "UNKNOWN" }
    var price: Double { _price ?? 0 }
    var change24h: Double { _change24h ?? 0 }
    var volume24h: Double { _volume24h ?? 0 }
    var high24h: Double { _high24h ?? 0 }
    var low24h: Double { _low24h ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case _symbol = "symbol"
        case _price = "price"
        case _change24h = "change_24h"
        case _volume24h = "volume_24h"
        case _high24h = "high_24h"
        case _low24h = "low_24h"
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
@MainActor
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
            // Server returns {symbols: [String]} - just list of symbol names
            // We need to get data from overview or individual symbol endpoint
            let response: SymbolListResponse = try await network.get(
                Config.Endpoints.screenerSymbols,
                params: ["filter": filter.rawValue]
            )
            
            // Convert symbol names to ScreenerSymbol objects with placeholder data
            // Real data comes from overview endpoint or websocket
            self.symbols = response.symbols.map { symbolName in
                ScreenerSymbolPlaceholder(symbol: symbolName)
            }
        } catch {
            print("Failed to fetch screener symbols: \(error)")
        }
    }
    
    // MARK: - Fetch Overview
    @MainActor
    func fetchOverview() async {
        do {
            // Server returns overview directly, not wrapped in APIResponse
            let overview: ScreenerOverview = try await network.get(Config.Endpoints.screenerOverview)
            self.overview = overview
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
            // Server returns symbol data directly
            let details: SymbolDetails = try await network.get(
                "\(Config.Endpoints.screenerSymbol)/\(symbol)"
            )
            self.selectedSymbol = details
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
    
    // MARK: - Fetch Top Coins (for Heatmap)
    /// Returns top coins data for market heatmap visualization
    struct TopCoin {
        let symbol: String
        let name: String?
        let price: Double
        let change24h: Double
        let marketCap: Double?
        let volume24h: Double?
    }
    
    @MainActor
    func fetchTopCoins() async throws -> [TopCoin] {
        // Fetch overview which contains top gainers/losers
        let overview: ScreenerOverview = try await network.get(Config.Endpoints.screenerOverview)
        
        // Combine top gainers and losers, then map to TopCoin
        var allCoins: [TopCoin] = []
        
        for symbol in overview.topGainers {
            allCoins.append(TopCoin(
                symbol: symbol.symbol,
                name: nil,
                price: symbol.price,
                change24h: symbol.change24h,
                marketCap: nil,
                volume24h: symbol.volume24h
            ))
        }
        
        for symbol in overview.topLosers {
            allCoins.append(TopCoin(
                symbol: symbol.symbol,
                name: nil,
                price: symbol.price,
                change24h: symbol.change24h,
                marketCap: nil,
                volume24h: symbol.volume24h
            ))
        }
        
        return allCoins
    }
}
