//
//  BacktestService.swift
//  EnlikoTrading
//
//  Backtest API service with real server integration
//

import Foundation

// MARK: - Request Models

struct BacktestRunRequest: Codable {
    let strategies: [String]
    let symbol: String
    let timeframe: String
    let days: Int
    let initialBalance: Double
    let riskPerTrade: Double
    let stopLossPercent: Double
    let takeProfitPercent: Double
    let leverage: Int?
    let dataSource: String
    
    enum CodingKeys: String, CodingKey {
        case strategies
        case symbol
        case timeframe
        case days
        case initialBalance = "initial_balance"
        case riskPerTrade = "risk_per_trade"
        case stopLossPercent = "stop_loss_percent"
        case takeProfitPercent = "take_profit_percent"
        case leverage
        case dataSource = "data_source"
    }
    
    init(
        strategies: [String],
        symbol: String,
        timeframe: String,
        days: Int,
        initialBalance: Double,
        riskPerTrade: Double,
        stopLossPercent: Double,
        takeProfitPercent: Double,
        leverage: Int? = 10,
        dataSource: String = "binance"
    ) {
        self.strategies = strategies
        self.symbol = symbol
        self.timeframe = timeframe
        self.days = days
        self.initialBalance = initialBalance
        self.riskPerTrade = riskPerTrade
        self.stopLossPercent = stopLossPercent
        self.takeProfitPercent = takeProfitPercent
        self.leverage = leverage
        self.dataSource = dataSource
    }
}

// MARK: - Response Models

struct BacktestRunResponse: Codable {
    let success: Bool
    let results: [String: BacktestResultData]?
    let error: String?
}

struct BacktestResultData: Codable {
    // Core metrics
    let totalTrades: Int?
    let winningTrades: Int?
    let losingTrades: Int?
    let winRate: Double?
    let totalPnl: Double?
    let totalPnlPercent: Double?
    let maxDrawdown: Double?
    let maxDrawdownPercent: Double?
    let profitFactor: Double?
    let sharpeRatio: Double?
    let sortinoRatio: Double?
    let calmarRatio: Double?
    let finalBalance: Double?
    let initialBalance: Double?
    
    // Additional metrics
    let avgWin: Double?
    let avgLoss: Double?
    let largestWin: Double?
    let largestLoss: Double?
    let avgHoldingTime: Double?
    let expectancy: Double?
    
    // Trade list
    let trades: [BacktestTradeData]?
    let equityCurve: [[Double]]?
    
    enum CodingKeys: String, CodingKey {
        case totalTrades = "total_trades"
        case winningTrades = "winning_trades"
        case losingTrades = "losing_trades"
        case winRate = "win_rate"
        case totalPnl = "total_pnl"
        case totalPnlPercent = "total_pnl_percent"
        case maxDrawdown = "max_drawdown"
        case maxDrawdownPercent = "max_drawdown_percent"
        case profitFactor = "profit_factor"
        case sharpeRatio = "sharpe_ratio"
        case sortinoRatio = "sortino_ratio"
        case calmarRatio = "calmar_ratio"
        case finalBalance = "final_balance"
        case initialBalance = "initial_balance"
        case avgWin = "avg_win"
        case avgLoss = "avg_loss"
        case largestWin = "largest_win"
        case largestLoss = "largest_loss"
        case avgHoldingTime = "avg_holding_time"
        case expectancy
        case trades
        case equityCurve = "equity_curve"
    }
}

struct BacktestTradeData: Codable, Identifiable {
    var id: String { "\(entryTimestamp ?? 0)_\(direction ?? "")_\(symbol ?? "")" }
    
    let symbol: String?
    let direction: String?
    let entryPrice: Double?
    let exitPrice: Double?
    let entryTimestamp: Double?
    let exitTimestamp: Double?
    let qty: Double?
    let pnl: Double?
    let pnlPercent: Double?
    let exitReason: String?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case direction
        case entryPrice = "entry_price"
        case exitPrice = "exit_price"
        case entryTimestamp = "entry_timestamp"
        case exitTimestamp = "exit_timestamp"
        case qty
        case pnl
        case pnlPercent = "pnl_percent"
        case exitReason = "exit_reason"
    }
}

// MARK: - Strategies Response

struct StrategiesResponse: Codable {
    let success: Bool
    let strategies: [StrategyInfo]?
    let error: String?
}

struct StrategyInfo: Codable, Identifiable {
    var id: String { name }
    
    let name: String
    let displayName: String?
    let description: String?
    let category: String?
    let defaultParams: [String: AnyCodable]?
    
    enum CodingKeys: String, CodingKey {
        case name
        case displayName = "display_name"
        case description
        case category
        case defaultParams = "default_params"
    }
}

// MARK: - Saved Backtests

struct SavedBacktestsResponse: Codable {
    let success: Bool
    let backtests: [SavedBacktest]?
    let error: String?
}

struct SavedBacktest: Codable, Identifiable {
    let id: Int
    let name: String?
    let strategy: String
    let symbol: String
    let timeframe: String
    let totalTrades: Int?
    let winRate: Double?
    let totalPnl: Double?
    let maxDrawdown: Double?
    let sharpeRatio: Double?
    let profitFactor: Double?
    let createdAt: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case strategy
        case symbol
        case timeframe
        case totalTrades = "total_trades"
        case winRate = "win_rate"
        case totalPnl = "total_pnl"
        case maxDrawdown = "max_drawdown"
        case sharpeRatio = "sharpe_ratio"
        case profitFactor = "profit_factor"
        case createdAt = "created_at"
    }
}

// MARK: - BacktestService

class BacktestService: ObservableObject {
    static let shared = BacktestService()
    
    @Published var isRunning = false
    @Published var progress: Double = 0
    @Published var statusMessage: String = ""
    @Published var lastError: String?
    
    private let networkService = NetworkService.shared
    
    private init() {}
    
    // MARK: - Run Backtest
    
    func runBacktest(
        strategies: [String],
        symbol: String,
        timeframe: String,
        days: Int,
        initialBalance: Double,
        riskPerTrade: Double,
        stopLossPercent: Double,
        takeProfitPercent: Double,
        leverage: Int = 10,
        dataSource: String = "binance"
    ) async throws -> [String: BacktestResultData] {
        
        let request = BacktestRunRequest(
            strategies: strategies,
            symbol: symbol,
            timeframe: timeframe,
            days: days,
            initialBalance: initialBalance,
            riskPerTrade: riskPerTrade,
            stopLossPercent: stopLossPercent,
            takeProfitPercent: takeProfitPercent,
            leverage: leverage,
            dataSource: dataSource
        )
        
        await MainActor.run {
            self.isRunning = true
            self.progress = 0
            self.statusMessage = "Starting backtest..."
            self.lastError = nil
        }
        
        do {
            let response: BacktestRunResponse = try await networkService.post("/backtest/run", body: request)
            
            await MainActor.run {
                self.isRunning = false
                self.progress = 100
                self.statusMessage = "Backtest complete"
            }
            
            if response.success, let results = response.results {
                return results
            } else {
                throw BacktestError.serverError(response.error ?? "Unknown error")
            }
        } catch {
            await MainActor.run {
                self.isRunning = false
                self.lastError = error.localizedDescription
            }
            throw error
        }
    }
    
    // MARK: - Get Available Strategies
    
    func getStrategies() async throws -> [StrategyInfo] {
        let response: StrategiesResponse = try await networkService.get("/backtest/strategies")
        
        if response.success, let strategies = response.strategies {
            return strategies
        } else {
            throw BacktestError.serverError(response.error ?? "Failed to fetch strategies")
        }
    }
    
    // MARK: - Get Saved Backtests
    
    func getSavedBacktests() async throws -> [SavedBacktest] {
        let response: SavedBacktestsResponse = try await networkService.get("/backtest/saved")
        
        if response.success, let backtests = response.backtests {
            return backtests
        } else {
            throw BacktestError.serverError(response.error ?? "Failed to fetch saved backtests")
        }
    }
    
    // MARK: - Save Backtest Result
    
    func saveBacktest(
        name: String,
        strategy: String,
        symbol: String,
        timeframe: String,
        result: BacktestResultData
    ) async throws -> Int {
        
        struct SaveRequest: Codable {
            let name: String
            let strategy: String
            let symbol: String
            let timeframe: String
            let totalTrades: Int
            let winRate: Double
            let totalPnl: Double
            let maxDrawdown: Double
            let sharpeRatio: Double
            let profitFactor: Double
            
            enum CodingKeys: String, CodingKey {
                case name, strategy, symbol, timeframe
                case totalTrades = "total_trades"
                case winRate = "win_rate"
                case totalPnl = "total_pnl"
                case maxDrawdown = "max_drawdown"
                case sharpeRatio = "sharpe_ratio"
                case profitFactor = "profit_factor"
            }
        }
        
        struct SaveResponse: Codable {
            let success: Bool
            let id: Int?
            let error: String?
        }
        
        let request = SaveRequest(
            name: name,
            strategy: strategy,
            symbol: symbol,
            timeframe: timeframe,
            totalTrades: result.totalTrades ?? 0,
            winRate: result.winRate ?? 0,
            totalPnl: result.totalPnl ?? 0,
            maxDrawdown: result.maxDrawdown ?? 0,
            sharpeRatio: result.sharpeRatio ?? 0,
            profitFactor: result.profitFactor ?? 0
        )
        
        let response: SaveResponse = try await networkService.post("/backtest/save", body: request)
        
        if response.success, let id = response.id {
            return id
        } else {
            throw BacktestError.serverError(response.error ?? "Failed to save backtest")
        }
    }
    
    // MARK: - Delete Saved Backtest
    
    func deleteBacktest(id: Int) async throws {
        struct DeleteResponse: Codable {
            let success: Bool
            let error: String?
        }
        
        let response: DeleteResponse = try await networkService.delete("/backtest/saved/\(id)")
        
        if !response.success {
            throw BacktestError.serverError(response.error ?? "Failed to delete backtest")
        }
    }
    
    // MARK: - Compare Backtests
    
    func compareBacktests(ids: [Int]) async throws -> [SavedBacktest] {
        struct CompareResponse: Codable {
            let success: Bool
            let backtests: [SavedBacktest]?
            let error: String?
        }
        
        let idsParam = ids.map(String.init).joined(separator: ",")
        let response: CompareResponse = try await networkService.get("/backtest/compare?ids=\(idsParam)")
        
        if response.success, let backtests = response.backtests {
            return backtests
        } else {
            throw BacktestError.serverError(response.error ?? "Failed to compare backtests")
        }
    }
}

// MARK: - Errors

enum BacktestError: LocalizedError {
    case serverError(String)
    case invalidParameters(String)
    case rateLimited
    case notAuthenticated
    
    var errorDescription: String? {
        switch self {
        case .serverError(let message):
            return message
        case .invalidParameters(let message):
            return "Invalid parameters: \(message)"
        case .rateLimited:
            return "Too many requests. Please wait before running another backtest."
        case .notAuthenticated:
            return "Please log in to run backtests."
        }
    }
}

// MARK: - Helper Extensions

extension BacktestResultData {
    /// Convert to BacktestResult model for UI display
    func toBacktestResult(strategy: String, symbol: String, timeframe: String) -> BacktestResult {
        return BacktestResult(
            id: UUID().uuidString,
            strategy: strategy,
            symbol: symbol,
            timeframe: timeframe,
            totalTrades: totalTrades ?? 0,
            winRate: winRate ?? 0,
            totalPnl: totalPnl ?? 0,
            maxDrawdown: maxDrawdown ?? 0,
            profitFactor: profitFactor ?? 0,
            sharpeRatio: sharpeRatio ?? 0,
            trades: nil
        )
    }
}
