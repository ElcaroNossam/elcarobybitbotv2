//
//  SignalsService.swift
//  EnlikoTrading
//
//  Trading signals service
//

import Foundation
import Combine

// MARK: - Signal Models

// Response from /signals endpoint
struct SignalsResponse: Codable {
    let success: Bool?
    let data: [TradingSignal]?
    let count: Int?
    let error: String?
}

struct TradingSignal: Codable, Identifiable {
    private let _id: Int?
    private let _symbol: String?
    private let _side: String?
    private let _strategy: String?
    let entryPrice: Double?
    let stopLoss: Double?
    let takeProfit: Double?
    let confidence: Double?
    private let _status: String?
    private let _createdAt: String?
    let executedAt: String?
    let pnl: Double?
    
    // Computed properties with defaults
    var id: Int { _id ?? 0 }
    var symbol: String { _symbol ?? "UNKNOWN" }
    var side: String { _side ?? "Buy" }
    var strategy: String { _strategy ?? "unknown" }
    var status: String { _status ?? "active" }
    var createdAt: String { _createdAt ?? "" }
    
    enum CodingKeys: String, CodingKey {
        case _id = "id"
        case _symbol = "symbol"
        case _side = "side"
        case _strategy = "strategy"
        case entryPrice = "entry_price"
        case stopLoss = "stop_loss"
        case takeProfit = "take_profit"
        case confidence
        case _status = "status"
        case _createdAt = "created_at"
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
    private let _totalSignals: Int?
    private let _activeSignals: Int?
    private let _executedSignals: Int?
    private let _winRate: Double?
    private let _totalPnl: Double?
    private let _avgPnlPerSignal: Double?
    
    var totalSignals: Int { _totalSignals ?? 0 }
    var activeSignals: Int { _activeSignals ?? 0 }
    var executedSignals: Int { _executedSignals ?? 0 }
    var winRate: Double { _winRate ?? 0 }
    var totalPnl: Double { _totalPnl ?? 0 }
    var avgPnlPerSignal: Double { _avgPnlPerSignal ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case _totalSignals = "total_signals"
        case _activeSignals = "active_signals"
        case _executedSignals = "executed_signals"
        case _winRate = "win_rate"
        case _totalPnl = "total_pnl"
        case _avgPnlPerSignal = "avg_pnl_per_signal"
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
            // Server returns {success, data: [...], count, error}
            let response: SignalsResponse = try await network.get(
                Config.Endpoints.signals,
                params: params
            )
            
            self.signals = response.data ?? []
        } catch {
            print("Failed to fetch signals: \(error)")
        }
    }
    
    // MARK: - Fetch Active Signals
    @MainActor
    func fetchActiveSignals() async {
        do {
            let response: SignalsResponse = try await network.get(
                Config.Endpoints.signalsActive
            )
            
            self.activeSignals = response.data ?? []
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
            // Try direct decode first
            let stats: SignalStats = try await network.get(
                "\(Config.Endpoints.signals)/stats",
                params: params
            )
            self.stats = stats
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
