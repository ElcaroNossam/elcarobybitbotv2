//
//  AIService.swift
//  LyxenTrading
//
//  AI analysis and market sentiment service
//

import Foundation
import Combine

// MARK: - AI Models
struct AIAnalysis: Codable {
    let symbol: String
    let signal: String  // "LONG", "SHORT", "NEUTRAL"
    let confidence: Double
    let analysis: String
    let keyFactors: [String]
    let priceTargets: PriceTargets?
    let riskLevel: String
    let timestamp: String
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case signal
        case confidence
        case analysis
        case keyFactors = "key_factors"
        case priceTargets = "price_targets"
        case riskLevel = "risk_level"
        case timestamp
    }
}

struct PriceTargets: Codable {
    let entry: Double?
    let takeProfit: Double?
    let stopLoss: Double?
    let support: Double?
    let resistance: Double?
    
    enum CodingKeys: String, CodingKey {
        case entry
        case takeProfit = "take_profit"
        case stopLoss = "stop_loss"
        case support
        case resistance
    }
}

struct MarketSentiment: Codable {
    let overall: String  // "BULLISH", "BEARISH", "NEUTRAL"
    let score: Double    // -100 to +100
    let fearGreedIndex: Int?
    let btcDominance: Double?
    let topSignals: [SignalItem]
    let marketConditions: MarketConditions?
    let lastUpdated: String
    
    enum CodingKeys: String, CodingKey {
        case overall
        case score
        case fearGreedIndex = "fear_greed_index"
        case btcDominance = "btc_dominance"
        case topSignals = "top_signals"
        case marketConditions = "market_conditions"
        case lastUpdated = "last_updated"
    }
}

struct SignalItem: Codable, Identifiable {
    var id: String { symbol }
    
    let symbol: String
    let direction: String  // "LONG", "SHORT"
    let confidence: Double
    let strategy: String?
}

struct MarketConditions: Codable {
    let volatility: String  // "LOW", "MEDIUM", "HIGH"
    let trend: String       // "UPTREND", "DOWNTREND", "SIDEWAYS"
    let volume: String      // "LOW", "NORMAL", "HIGH"
    let openInterest: String?
    
    enum CodingKeys: String, CodingKey {
        case volatility
        case trend
        case volume
        case openInterest = "open_interest"
    }
}

// MARK: - AI Service
class AIService: ObservableObject {
    static let shared = AIService()
    
    @Published var currentAnalysis: AIAnalysis?
    @Published var marketSentiment: MarketSentiment?
    @Published var recentAnalyses: [AIAnalysis] = []
    @Published var isLoading = false
    @Published var isAnalyzing = false
    
    private let network = NetworkService.shared
    
    private init() {}
    
    // MARK: - Analyze Symbol
    @MainActor
    func analyzeSymbol(_ symbol: String, timeframe: String = "1h") async {
        isAnalyzing = true
        defer { isAnalyzing = false }
        
        do {
            let response: APIResponse<AIAnalysis> = try await network.post(
                Config.Endpoints.aiAnalyze,
                body: [
                    "symbol": symbol,
                    "timeframe": timeframe
                ]
            )
            
            if let analysis = response.data {
                self.currentAnalysis = analysis
                
                // Add to recent analyses
                if !recentAnalyses.contains(where: { $0.symbol == symbol }) {
                    recentAnalyses.insert(analysis, at: 0)
                    if recentAnalyses.count > 10 {
                        recentAnalyses.removeLast()
                    }
                }
            }
        } catch {
            print("Failed to analyze symbol: \(error)")
        }
    }
    
    // MARK: - Fetch Market Sentiment
    @MainActor
    func fetchMarketSentiment() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response: APIResponse<MarketSentiment> = try await network.get(
                Config.Endpoints.aiMarketSentiment
            )
            
            if let sentiment = response.data {
                self.marketSentiment = sentiment
            }
        } catch {
            print("Failed to fetch market sentiment: \(error)")
        }
    }
    
    // MARK: - Get Signal Color
    func signalColor(for signal: String) -> String {
        switch signal.uppercased() {
        case "LONG", "BULLISH", "BUY":
            return "green"
        case "SHORT", "BEARISH", "SELL":
            return "red"
        default:
            return "gray"
        }
    }
    
    // MARK: - Get Risk Color
    func riskColor(for risk: String) -> String {
        switch risk.uppercased() {
        case "LOW":
            return "green"
        case "MEDIUM":
            return "yellow"
        case "HIGH":
            return "red"
        default:
            return "gray"
        }
    }
}
