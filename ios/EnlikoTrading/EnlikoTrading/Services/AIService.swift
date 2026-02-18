//
//  AIService.swift
//  EnlikoTrading
//
//  AI analysis and market sentiment service
//

import Foundation
import Combine

// MARK: - AI Models
struct AIAnalysis: Codable {
    private let _symbol: String?
    private let _signal: String?
    private let _confidence: Double?
    private let _analysis: String?
    private let _keyFactors: [String]?
    let priceTargets: PriceTargets?
    private let _riskLevel: String?
    private let _timestamp: String?
    
    var symbol: String { _symbol ?? "UNKNOWN" }
    var signal: String { _signal ?? "NEUTRAL" }
    var confidence: Double { _confidence ?? 0 }
    var analysis: String { _analysis ?? "" }
    var keyFactors: [String] { _keyFactors ?? [] }
    var riskLevel: String { _riskLevel ?? "MEDIUM" }
    var timestamp: String { _timestamp ?? "" }
    
    enum CodingKeys: String, CodingKey {
        case _symbol = "symbol"
        case _signal = "signal"
        case _confidence = "confidence"
        case _analysis = "analysis"
        case _keyFactors = "key_factors"
        case priceTargets = "price_targets"
        case _riskLevel = "risk_level"
        case _timestamp = "timestamp"
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
    private let _overall: String?
    private let _score: Double?
    let fearGreedIndex: Int?
    let btcDominance: Double?
    private let _topSignals: [SignalItem]?
    let marketConditions: MarketConditions?
    private let _lastUpdated: String?
    
    var overall: String { _overall ?? "NEUTRAL" }
    var score: Double { _score ?? 0 }
    var topSignals: [SignalItem] { _topSignals ?? [] }
    var lastUpdated: String { _lastUpdated ?? "" }
    
    enum CodingKeys: String, CodingKey {
        case _overall = "overall"
        case _score = "score"
        case fearGreedIndex = "fear_greed_index"
        case btcDominance = "btc_dominance"
        case _topSignals = "top_signals"
        case marketConditions = "market_conditions"
        case _lastUpdated = "last_updated"
    }
}

struct SignalItem: Codable, Identifiable {
    var id: String { _symbol ?? UUID().uuidString }
    
    private let _symbol: String?
    private let _direction: String?
    private let _confidence: Double?
    let strategy: String?
    
    var symbol: String { _symbol ?? "UNKNOWN" }
    var direction: String { _direction ?? "LONG" }
    var confidence: Double { _confidence ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case _symbol = "symbol"
        case _direction = "direction"
        case _confidence = "confidence"
        case strategy
    }
}

struct MarketConditions: Codable {
    private let _volatility: String?
    private let _trend: String?
    private let _volume: String?
    let openInterest: String?
    
    var volatility: String { _volatility ?? "MEDIUM" }
    var trend: String { _trend ?? "SIDEWAYS" }
    var volume: String { _volume ?? "NORMAL" }
    
    enum CodingKeys: String, CodingKey {
        case _volatility = "volatility"
        case _trend = "trend"
        case _volume = "volume"
        case openInterest = "open_interest"
    }
}

// MARK: - AI Service
@MainActor
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
    
    // MARK: - Ask AI (Chat Interface)
    /// Send a question to the AI and get a response in user's language
    @MainActor
    func askAI(question: String) async throws -> String {
        struct AIQuestionRequest: Codable {
            let question: String
            let language: String
        }
        
        /// Backend /ai/chat returns: {"success": true, "response": "..."} — NOT wrapped in data
        struct AIChatResponse: Codable {
            let success: Bool?
            let response: String?
            let answer: String?
            let message: String?
            let error: String?
            
            var text: String {
                response ?? answer ?? message ?? "I couldn't process that request."
            }
        }
        
        // Get user's current language
        let userLanguage = LocalizationManager.shared.currentLanguage.rawValue
        
        let response: AIChatResponse = try await network.post(
            Config.Endpoints.aiChat,
            body: AIQuestionRequest(question: question, language: userLanguage)
        )
        
        if let error = response.error {
            throw NetworkError.serverError(500, error)
        }
        
        return response.text
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
