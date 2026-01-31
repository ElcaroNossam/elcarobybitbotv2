//
//  StatsService.swift
//  EnlikoTrading
//
//  Trading statistics and analytics service
//

import Foundation
import Combine

// MARK: - Stats Models
struct DashboardStats: Codable {
    private let _totalPnl: Double?
    private let _todayPnl: Double?
    private let _weekPnl: Double?
    private let _monthPnl: Double?
    private let _totalTrades: Int?
    private let _winRate: Double?
    private let _avgProfit: Double?
    private let _avgLoss: Double?
    private let _bestTrade: Double?
    private let _worstTrade: Double?
    let profitFactor: Double?
    
    var totalPnl: Double { _totalPnl ?? 0 }
    var todayPnl: Double { _todayPnl ?? 0 }
    var weekPnl: Double { _weekPnl ?? 0 }
    var monthPnl: Double { _monthPnl ?? 0 }
    var totalTrades: Int { _totalTrades ?? 0 }
    var winRate: Double { _winRate ?? 0 }
    var avgProfit: Double { _avgProfit ?? 0 }
    var avgLoss: Double { _avgLoss ?? 0 }
    var bestTrade: Double { _bestTrade ?? 0 }
    var worstTrade: Double { _worstTrade ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case _totalPnl = "total_pnl"
        case _todayPnl = "today_pnl"
        case _weekPnl = "week_pnl"
        case _monthPnl = "month_pnl"
        case _totalTrades = "total_trades"
        case _winRate = "win_rate"
        case _avgProfit = "avg_profit"
        case _avgLoss = "avg_loss"
        case _bestTrade = "best_trade"
        case _worstTrade = "worst_trade"
        case profitFactor = "profit_factor"
    }
}

struct PnlHistoryPoint: Codable, Identifiable {
    var id: String { _date ?? UUID().uuidString }
    
    private let _date: String?
    private let _pnl: Double?
    private let _cumulativePnl: Double?
    private let _trades: Int?
    
    var date: String { _date ?? "" }
    var pnl: Double { _pnl ?? 0 }
    var cumulativePnl: Double { _cumulativePnl ?? 0 }
    var trades: Int { _trades ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case _date = "date"
        case _pnl = "pnl"
        case _cumulativePnl = "cumulative_pnl"
        case _trades = "trades"
    }
}

struct StrategyReport: Codable, Identifiable {
    var id: String { _strategy ?? UUID().uuidString }
    
    private let _strategy: String?
    private let _totalTrades: Int?
    private let _winRate: Double?
    private let _totalPnl: Double?
    private let _avgPnl: Double?
    let profitFactor: Double?
    let maxDrawdown: Double?
    
    var strategy: String { _strategy ?? "unknown" }
    var totalTrades: Int { _totalTrades ?? 0 }
    var winRate: Double { _winRate ?? 0 }
    var totalPnl: Double { _totalPnl ?? 0 }
    var avgPnl: Double { _avgPnl ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case _strategy = "strategy"
        case _totalTrades = "total_trades"
        case _winRate = "win_rate"
        case _totalPnl = "total_pnl"
        case _avgPnl = "avg_pnl"
        case profitFactor = "profit_factor"
        case maxDrawdown = "max_drawdown"
    }
}

struct PositionsSummary: Codable {
    private let _totalPositions: Int?
    private let _longPositions: Int?
    private let _shortPositions: Int?
    private let _totalUnrealizedPnl: Double?
    private let _totalMargin: Double?
    private let _avgLeverage: Double?
    
    var totalPositions: Int { _totalPositions ?? 0 }
    var longPositions: Int { _longPositions ?? 0 }
    var shortPositions: Int { _shortPositions ?? 0 }
    var totalUnrealizedPnl: Double { _totalUnrealizedPnl ?? 0 }
    var totalMargin: Double { _totalMargin ?? 0 }
    var avgLeverage: Double { _avgLeverage ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case _totalPositions = "total_positions"
        case _longPositions = "long_positions"
        case _shortPositions = "short_positions"
        case _totalUnrealizedPnl = "total_unrealized_pnl"
        case _totalMargin = "total_margin"
        case _avgLeverage = "avg_leverage"
    }
}

// MARK: - Stats Service
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
    func fetchDashboard(accountType: String = "demo") async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response: APIResponse<DashboardStats> = try await network.get(
                Config.Endpoints.dashboard,
                params: ["account_type": accountType]
            )
            
            if let data = response.data {
                self.dashboard = data
            }
        } catch {
            print("Failed to fetch dashboard: \(error)")
        }
    }
    
    // MARK: - Fetch PnL History
    @MainActor
    func fetchPnlHistory(period: StatsPeriod = .week, accountType: String = "demo") async {
        do {
            let response: APIResponse<[PnlHistoryPoint]> = try await network.get(
                Config.Endpoints.pnlHistory,
                params: [
                    "period": period.rawValue,
                    "account_type": accountType
                ]
            )
            
            if let data = response.data {
                self.pnlHistory = data
            }
        } catch {
            print("Failed to fetch PnL history: \(error)")
        }
    }
    
    // MARK: - Fetch Strategy Reports
    @MainActor
    func fetchStrategyReports(accountType: String = "demo") async {
        do {
            let response: APIResponse<[StrategyReport]> = try await network.get(
                Config.Endpoints.strategyReport,
                params: ["account_type": accountType]
            )
            
            if let data = response.data {
                self.strategyReports = data
            }
        } catch {
            print("Failed to fetch strategy reports: \(error)")
        }
    }
    
    // MARK: - Fetch Positions Summary
    @MainActor
    func fetchPositionsSummary(accountType: String = "demo") async {
        do {
            let response: APIResponse<PositionsSummary> = try await network.get(
                Config.Endpoints.positionsSummary,
                params: ["account_type": accountType]
            )
            
            if let data = response.data {
                self.positionsSummary = data
            }
        } catch {
            print("Failed to fetch positions summary: \(error)")
        }
    }
    
    // MARK: - Refresh All Stats
    @MainActor
    func refreshAll(accountType: String = "demo") async {
        isLoading = true
        defer { isLoading = false }
        
        async let fetchDashboard: () = fetchDashboard(accountType: accountType)
        async let fetchPnlHistory: () = fetchPnlHistory(period: selectedPeriod, accountType: accountType)
        async let fetchStrategyReports: () = fetchStrategyReports(accountType: accountType)
        async let fetchPositionsSummary: () = fetchPositionsSummary(accountType: accountType)
        
        _ = await (fetchDashboard, fetchPnlHistory, fetchStrategyReports, fetchPositionsSummary)
    }
}
