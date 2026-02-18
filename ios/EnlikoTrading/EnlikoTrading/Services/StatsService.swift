//
//  StatsService.swift
//  EnlikoTrading
//
//  Trading statistics and analytics service
//

import Foundation
import Combine

// MARK: - Stats Models

// Backend /stats/dashboard returns: {"success": true, "data": {"summary": {...}, "pnlHistory": [...], "byStrategy": {...}}}
// DashboardStats maps to the "summary" object inside "data"
struct DashboardSummary: Codable {
    // Backend uses camelCase: totalPnL, totalTrades, winRate, avgWin, avgLoss, etc.
    let totalPnL: Double?
    let returnPct: Double?
    let totalTrades: Int?
    let winRate: Double?
    let profitFactor: Double?
    let maxDrawdown: Double?
    let avgWin: Double?
    let avgLoss: Double?
    let bestStreak: Int?
    let worstStreak: Int?
    let avgDuration: String?
    let tradesPerDay: Double?
    let pnlChange: Double?
    let wins: Int?
    let losses: Int?
    let maxDrawdownAbs: Double?
    // Period PnL fields - computed on backend from trade_logs
    let todayPnl: Double?
    let weekPnl: Double?
    let monthPnl: Double?
    // Best/Worst trade values
    let bestTrade: Double?
    let worstTrade: Double?
}

// Wrapper for the full dashboard response "data" object
struct DashboardData: Codable {
    let summary: DashboardSummary?
    let pnlHistory: [[String: AnyCodable]]?
    let byStrategy: [String: AnyCodable]?
    let byExchange: [String: AnyCodable]?
    let bySymbol: [String: AnyCodable]?
    let topTrades: [String: AnyCodable]?
}

// Convenience wrapper matching old DashboardStats interface for Views
struct DashboardStats {
    let totalPnl: Double
    let todayPnl: Double
    let weekPnl: Double
    let monthPnl: Double
    let totalTrades: Int
    let winRate: Double
    let avgProfit: Double
    let avgLoss: Double
    let bestTrade: Double
    let worstTrade: Double
    let profitFactor: Double
    let returnPct: Double
    let maxDrawdown: Double
    let pnlChange: Double
    
    init(from summary: DashboardSummary?) {
        let s = summary
        self.totalPnl = s?.totalPnL ?? 0
        self.todayPnl = s?.todayPnl ?? 0
        self.weekPnl = s?.weekPnl ?? 0
        self.monthPnl = s?.monthPnl ?? 0
        self.totalTrades = s?.totalTrades ?? 0
        self.winRate = s?.winRate ?? 0
        self.avgProfit = s?.avgWin ?? 0
        self.avgLoss = s?.avgLoss ?? 0
        self.bestTrade = s?.bestTrade ?? 0
        self.worstTrade = s?.worstTrade ?? 0
        self.profitFactor = s?.profitFactor ?? 0
        self.returnPct = s?.returnPct ?? 0
        self.maxDrawdown = s?.maxDrawdown ?? 0
        self.pnlChange = s?.pnlChange ?? 0
    }
}

// Backend /stats/pnl-history returns: {"labels": ["Jan 01", ...], "values": [0, 15.5, ...], "period": "7d"}
// We convert this to array of PnlHistoryPoint for the chart
struct PnlHistoryResponse: Codable {
    let labels: [String]?
    let values: [Double]?
    let period: String?
    let error: String?
}

struct PnlHistoryPoint: Identifiable {
    var id: String { date }
    let date: String
    let pnl: Double
    let cumulativePnl: Double
    let trades: Int
}

// Backend /stats/strategy-report returns: {"success": true, "strategies": [...], "totals": {...}}
// Each strategy object: {"name": "oi", "trades": 10, "wins": 6, "losses": 4, "win_rate": 60.0, "pnl": 15.5, "avg_pnl": 1.55, "profit_factor": 2.1, ...}
struct StrategyReportResponse: Codable {
    let success: Bool?
    let strategies: [StrategyReport]?
    let totals: [String: AnyCodable]?
    let period: String?
    let exchange: String?
    let error: String?
}

struct StrategyReport: Codable, Identifiable {
    var id: String { name ?? UUID().uuidString }
    
    let name: String?
    let displayName: String?
    let trades: Int?
    let wins: Int?
    let losses: Int?
    let winRate: Double?
    let pnl: Double?
    let avgPnl: Double?
    let profitFactor: Double?
    let totalVolume: Double?
    
    // Convenience computed properties matching old interface
    var strategy: String { name ?? "unknown" }
    var totalTrades: Int { trades ?? 0 }
    var totalPnl: Double { pnl ?? 0 }
    var maxDrawdown: Double? { nil }
    
    enum CodingKeys: String, CodingKey {
        case name
        case displayName = "display_name"
        case trades, wins, losses
        case winRate = "win_rate"
        case pnl
        case avgPnl = "avg_pnl"
        case profitFactor = "profit_factor"
        case totalVolume = "total_volume"
    }
}

// Backend /stats/positions-summary returns: {"success": true, "positions": [...], "summary": {"total_positions": 5, "total_pnl": ..., "long_count": 3, "short_count": 2, ...}}
struct PositionsSummaryResponse: Codable {
    let success: Bool?
    let positions: [AnyCodable]?
    let summary: PositionsSummary?
    let error: String?
}

struct PositionsSummary: Codable {
    private let _totalPositions: Int?
    private let _longCount: Int?
    private let _shortCount: Int?
    private let _totalPnl: Double?
    
    var totalPositions: Int { _totalPositions ?? 0 }
    var longPositions: Int { _longCount ?? 0 }
    var shortPositions: Int { _shortCount ?? 0 }
    var totalUnrealizedPnl: Double { _totalPnl ?? 0 }
    var totalMargin: Double { 0 }
    var avgLeverage: Double { 0 }
    
    enum CodingKeys: String, CodingKey {
        case _totalPositions = "total_positions"
        case _longCount = "long_count"
        case _shortCount = "short_count"
        case _totalPnl = "total_pnl"
    }
}

// MARK: - Stats Service
@MainActor
class StatsService: ObservableObject {
    static let shared = StatsService()
    
    @Published var dashboard: DashboardStats?
    @Published var pnlHistory: [PnlHistoryPoint] = []
    @Published var strategyReports: [StrategyReport] = []
    @Published var positionsSummary: PositionsSummary?
    @Published var isLoading = false
    @Published var selectedPeriod: StatsPeriod = .week
    
    private let network = NetworkService.shared
    
    enum StatsPeriod: String, CaseIterable {
        case day = "1d"
        case week = "7d"
        case month = "30d"
        case quarter = "90d"
        case year = "365d"
        case all = "all"
        
        var displayName: String {
            switch self {
            case .day: return "Today"
            case .week: return "Week"
            case .month: return "Month"
            case .quarter: return "3 Months"
            case .year: return "Year"
            case .all: return "All Time"
            }
        }
    }
    
    private init() {}
    
    // MARK: - Fetch Dashboard
    @MainActor
    func fetchDashboard(accountType: String = "demo", exchange: String = "all") async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            // Backend returns {"success": true, "data": {"summary": {...}, "pnlHistory": [...], ...}}
            let response: APIResponse<DashboardData> = try await network.get(
                Config.Endpoints.dashboard,
                params: ["account_type": accountType, "exchange": exchange]
            )
            
            if let data = response.data {
                self.dashboard = DashboardStats(from: data.summary)
            }
        } catch {
            print("Failed to fetch dashboard: \(error)")
        }
    }
    
    // MARK: - Fetch PnL History
    @MainActor
    func fetchPnlHistory(period: StatsPeriod = .week, accountType: String = "demo", exchange: String = "all") async {
        do {
            // Backend returns {"labels": [...], "values": [...], "period": "7d"} — NOT wrapped in APIResponse
            let response: PnlHistoryResponse = try await network.get(
                Config.Endpoints.pnlHistory,
                params: [
                    "period": period.rawValue,
                    "account_type": accountType,
                    "exchange": exchange
                ]
            )
            
            let labels = response.labels ?? []
            let values = response.values ?? []
            var points: [PnlHistoryPoint] = []
            for i in 0..<min(labels.count, values.count) {
                points.append(PnlHistoryPoint(
                    date: labels[i],
                    pnl: i > 0 ? values[i] - values[max(0, i - 1)] : values[i],
                    cumulativePnl: values[i],
                    trades: 0
                ))
            }
            self.pnlHistory = points
        } catch {
            print("Failed to fetch PnL history: \(error)")
        }
    }
    
    // MARK: - Fetch Strategy Reports
    @MainActor
    func fetchStrategyReports(accountType: String = "demo", exchange: String = "all") async {
        do {
            // Backend returns {"success": true, "strategies": [...], "totals": {...}} — NOT data wrapper
            let response: StrategyReportResponse = try await network.get(
                Config.Endpoints.strategyReport,
                params: ["account_type": accountType, "exchange": exchange]
            )
            
            if let strategies = response.strategies {
                self.strategyReports = strategies
            }
        } catch {
            print("Failed to fetch strategy reports: \(error)")
        }
    }
    
    // MARK: - Fetch Positions Summary
    @MainActor
    func fetchPositionsSummary(accountType: String = "demo", exchange: String = "all") async {
        do {
            // Backend returns {"success": true, "positions": [...], "summary": {...}} — NOT data wrapper
            let response: PositionsSummaryResponse = try await network.get(
                Config.Endpoints.positionsSummary,
                params: ["account_type": accountType, "exchange": exchange]
            )
            
            if let summary = response.summary {
                self.positionsSummary = summary
            }
        } catch {
            print("Failed to fetch positions summary: \(error)")
        }
    }
    
    // MARK: - Refresh All Stats
    @MainActor
    func refreshAll(accountType: String = "demo", exchange: String = "all") async {
        isLoading = true
        defer { isLoading = false }
        
        async let fetchDashboard: () = fetchDashboard(accountType: accountType, exchange: exchange)
        async let fetchPnlHistory: () = fetchPnlHistory(period: selectedPeriod, accountType: accountType, exchange: exchange)
        async let fetchStrategyReports: () = fetchStrategyReports(accountType: accountType, exchange: exchange)
        async let fetchPositionsSummary: () = fetchPositionsSummary(accountType: accountType, exchange: exchange)
        
        _ = await (fetchDashboard, fetchPnlHistory, fetchStrategyReports, fetchPositionsSummary)
    }
}
