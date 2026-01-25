//
//  StatsService.swift
//  LyxenTrading
//
//  Trading statistics and analytics service
//

import Foundation
import Combine

// MARK: - Stats Models
struct DashboardStats: Codable {
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
    let profitFactor: Double?
    
    enum CodingKeys: String, CodingKey {
        case totalPnl = "total_pnl"
        case todayPnl = "today_pnl"
        case weekPnl = "week_pnl"
        case monthPnl = "month_pnl"
        case totalTrades = "total_trades"
        case winRate = "win_rate"
        case avgProfit = "avg_profit"
        case avgLoss = "avg_loss"
        case bestTrade = "best_trade"
        case worstTrade = "worst_trade"
        case profitFactor = "profit_factor"
    }
}

struct PnlHistoryPoint: Codable, Identifiable {
    var id: String { date }
    
    let date: String
    let pnl: Double
    let cumulativePnl: Double
    let trades: Int
    
    enum CodingKeys: String, CodingKey {
        case date
        case pnl
        case cumulativePnl = "cumulative_pnl"
        case trades
    }
}

struct StrategyReport: Codable, Identifiable {
    var id: String { strategy }
    
    let strategy: String
    let totalTrades: Int
    let winRate: Double
    let totalPnl: Double
    let avgPnl: Double
    let profitFactor: Double?
    let maxDrawdown: Double?
    
    enum CodingKeys: String, CodingKey {
        case strategy
        case totalTrades = "total_trades"
        case winRate = "win_rate"
        case totalPnl = "total_pnl"
        case avgPnl = "avg_pnl"
        case profitFactor = "profit_factor"
        case maxDrawdown = "max_drawdown"
    }
}

struct PositionsSummary: Codable {
    let totalPositions: Int
    let longPositions: Int
    let shortPositions: Int
    let totalUnrealizedPnl: Double
    let totalMargin: Double
    let avgLeverage: Double
    
    enum CodingKeys: String, CodingKey {
        case totalPositions = "total_positions"
        case longPositions = "long_positions"
        case shortPositions = "short_positions"
        case totalUnrealizedPnl = "total_unrealized_pnl"
        case totalMargin = "total_margin"
        case avgLeverage = "avg_leverage"
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
                Config.Endpoints.statsDashboard,
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
                Config.Endpoints.statsPnlHistory,
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
                Config.Endpoints.statsStrategyReport,
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
                Config.Endpoints.statsPositionsSummary,
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
