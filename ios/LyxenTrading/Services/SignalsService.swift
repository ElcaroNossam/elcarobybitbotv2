//
//  SignalsService.swift
//  LyxenTrading
//
//  Trading signals service
//

import Foundation
import Combine

// MARK: - Signal Models
struct TradingSignal: Codable, Identifiable {
    let id: Int
    let symbol: String
    let side: String        // "Buy", "Sell"
    let strategy: String
    let entryPrice: Double?
    let stopLoss: Double?
    let takeProfit: Double?
    let confidence: Double?
    let status: String      // "active", "executed", "expired", "cancelled"
    let createdAt: String
    let executedAt: String?
    let pnl: Double?
    
    enum CodingKeys: String, CodingKey {
        case id
        case symbol
        case side
        case strategy
        case entryPrice = "entry_price"
        case stopLoss = "stop_loss"
        case takeProfit = "take_profit"
        case confidence
        case status
        case createdAt = "created_at"
        case executedAt = "executed_at"
        case pnl
    }
    
    var sideIcon: String {
        side.lowercased() == "buy" ? "📈" : "📉"
    }
    
    var statusIcon: String {
        switch status.lowercased() {
        case "active": return "🟢"
        case "executed": return "✅"
        case "expired": return "⏰"
        case "cancelled": return "❌"
        default: return "⚪"
        }
    }
}

struct SignalStats: Codable {
    let totalSignals: Int
    let activeSignals: Int
    let executedSignals: Int
    let winRate: Double
    let totalPnl: Double
    let avgPnlPerSignal: Double
    
    enum CodingKeys: String, CodingKey {
        case totalSignals = "total_signals"
        case activeSignals = "active_signals"
        case executedSignals = "executed_signals"
        case winRate = "win_rate"
        case totalPnl = "total_pnl"
        case avgPnlPerSignal = "avg_pnl_per_signal"
    }
}

// MARK: - Signals Service
class SignalsService: ObservableObject {
    static let shared = SignalsService()
    
    @Published var signals: [TradingSignal] = []
    @Published var activeSignals: [TradingSignal] = []
    @Published var stats: SignalStats?
    @Published var isLoading = false
    @Published var selectedStrategy: String?
    
    private let network = NetworkService.shared
    
    private init() {}
    
    // MARK: - Fetch All Signals
    @MainActor
    func fetchSignals(strategy: String? = nil, status: String? = nil, limit: Int = 50) async {
        isLoading = true
        defer { isLoading = false }
        
        var params: [String: String] = ["limit": String(limit)]
        if let strategy = strategy { params["strategy"] = strategy }
        if let status = status { params["status"] = status }
        
        do {
            let response: APIResponse<[TradingSignal]> = try await network.get(
                Config.Endpoints.signals,
                params: params
            )
            
            if let data = response.data {
                self.signals = data
            }
        } catch {
            print("Failed to fetch signals: \(error)")
        }
    }
    
    // MARK: - Fetch Active Signals
    @MainActor
    func fetchActiveSignals() async {
        do {
            let response: APIResponse<[TradingSignal]> = try await network.get(
                Config.Endpoints.signalsActive
            )
            
            if let data = response.data {
                self.activeSignals = data
            }
        } catch {
            print("Failed to fetch active signals: \(error)")
        }
    }
    
    // MARK: - Fetch Signal Stats
    @MainActor
    func fetchStats(strategy: String? = nil) async {
        var params: [String: String] = [:]
        if let strategy = strategy { params["strategy"] = strategy }
        
        do {
            let response: APIResponse<SignalStats> = try await network.get(
                "\(Config.Endpoints.signals)/stats",
                params: params
            )
            
            if let data = response.data {
                self.stats = data
            }
        } catch {
            print("Failed to fetch signal stats: \(error)")
        }
    }
    
    // MARK: - Get Signals by Strategy
    func signalsByStrategy() -> [String: [TradingSignal]] {
        Dictionary(grouping: signals, by: { $0.strategy })
    }
    
    // MARK: - Refresh All
    @MainActor
    func refreshAll() async {
        isLoading = true
        defer { isLoading = false }
        
        async let fetchSignals: () = fetchSignals(strategy: selectedStrategy)
        async let fetchActiveSignals: () = fetchActiveSignals()
        async let fetchStats: () = fetchStats(strategy: selectedStrategy)
        
        _ = await (fetchSignals, fetchActiveSignals, fetchStats)
    }
}
