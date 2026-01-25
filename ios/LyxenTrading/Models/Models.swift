//
//  Models.swift
//  LyxenTrading
//
//  Data Models matching backend API responses
//

import Foundation

// MARK: - User Models
struct User: Codable, Identifiable {
    let id: Int
    let userId: Int?
    let username: String?
    let email: String?
    let firstName: String?
    let lastName: String?
    let lang: String?
    let exchangeType: String?
    let tradingMode: String?
    let isAllowed: Bool?
    let isPremium: Bool?
    let licenseType: String?
    let licenseExpiry: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case username
        case email
        case firstName = "first_name"
        case lastName = "last_name"
        case lang
        case exchangeType = "exchange_type"
        case tradingMode = "trading_mode"
        case isAllowed = "is_allowed"
        case isPremium = "is_premium"
        case licenseType = "license_type"
        case licenseExpiry = "license_expiry"
    }
    
    var displayName: String {
        if let first = firstName {
            return lastName != nil ? "\(first) \(lastName!)" : first
        }
        return username ?? "User \(userId ?? id)"
    }
}

struct UserSettings: Codable {
    let percent: Double
    let tpPercent: Double
    let slPercent: Double
    let leverage: Int
    let useAtr: Bool
    let dcaEnabled: Bool
    let dcaPct1: Double
    let dcaPct2: Double
    
    enum CodingKeys: String, CodingKey {
        case percent
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case leverage
        case useAtr = "use_atr"
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
    }
}

// MARK: - Balance Models
struct Balance: Codable {
    let equity: Double
    let available: Double
    let unrealizedPnl: Double
    let marginBalance: Double?
    let accountType: String?
    
    // Computed properties for compatibility
    var totalEquity: Double { equity }
    var positionMargin: Double { marginBalance ?? (equity - available) }
    var currency: String { "USDT" }
    
    enum CodingKeys: String, CodingKey {
        case equity
        case available
        case unrealizedPnl = "unrealized_pnl"
        case marginBalance = "margin_balance"
        case accountType = "account_type"
    }
    
    var formattedEquity: String {
        String(format: "%.2f %@", equity, currency)
    }
    
    var formattedAvailable: String {
        String(format: "%.2f %@", available, currency)
    }
    
    var formattedPnl: String {
        let sign = unrealizedPnl >= 0 ? "+" : ""
        return String(format: "%@%.2f %@", sign, unrealizedPnl, currency)
    }
}

struct BalanceResponse: Codable {
    let success: Bool
    let balance: Balance?
    let data: Balance?  // Backend may return data directly
    let error: String?
    
    // Computed property to get balance from either field
    var balanceData: Balance? {
        return balance ?? data
    }
}

// MARK: - Position Models
struct Position: Codable, Identifiable {
    var id: String { "\(symbol)-\(side)" }
    
    let symbol: String
    let side: String
    let size: Double
    let entryPrice: Double
    let markPrice: Double
    let leverage: Int?
    let unrealizedPnl: Double
    let pnlPercent: Double?
    let liquidationPrice: Double?
    let takeProfit: Double?
    let stopLoss: Double?
    let strategy: String?
    let createdAt: String?
    let positionValue: Double?
    let positionMarginValue: Double?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case size
        case entryPrice = "entry_price"
        case markPrice = "mark_price"
        case leverage
        case unrealizedPnl = "unrealized_pnl"
        case pnlPercent = "pnl_percent"
        case liquidationPrice = "liquidation_price"
        case takeProfit = "take_profit"
        case stopLoss = "stop_loss"
        case strategy
        case createdAt = "created_at"
        case positionValue = "position_value"
        case positionMarginValue = "position_margin"
    }
    
    var isLong: Bool { side.lowercased() == "buy" || side.lowercased() == "long" }
    var positionSide: PositionSide { isLong ? .long : .short }
    
    var formattedPnl: String {
        let sign = unrealizedPnl >= 0 ? "+" : ""
        let pct = pnlPercent ?? 0
        return String(format: "%@$%.2f (%.2f%%)", sign, unrealizedPnl, pct)
    }
    
    var notionalValue: Double {
        positionValue ?? (size * markPrice)
    }
    
    var positionMargin: Double {
        positionMarginValue ?? (notionalValue / Double(leverage ?? 10))
    }
}

struct PositionsResponse: Codable {
    let success: Bool
    let positions: [Position]?
    let error: String?
}

// MARK: - Order Models
struct Order: Codable, Identifiable {
    let orderId: String
    let symbol: String
    let side: String
    let orderType: String
    let qty: Double
    let price: Double?
    let triggerPrice: Double?
    let status: String?
    let createdAt: String?
    
    var id: String { orderId }
    
    enum CodingKeys: String, CodingKey {
        case orderId = "order_id"
        case symbol
        case side
        case orderType = "order_type"
        case qty
        case price
        case triggerPrice = "trigger_price"
        case status
        case createdAt = "created_at"
    }
    
    var isLimitOrder: Bool { orderType.lowercased() == "limit" }
}

struct OrdersResponse: Codable {
    let success: Bool
    let orders: [Order]?
    let error: String?
}

// MARK: - Trade Models
struct Trade: Codable, Identifiable {
    var id: String { "\(symbol)-\(timestamp)" }
    
    let symbol: String
    let side: String
    let entryPrice: Double
    let exitPrice: Double?
    let exitReason: String?
    let pnl: Double?
    let pnlPct: Double?
    let strategy: String?
    let timestamp: String
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case entryPrice = "entry_price"
        case exitPrice = "exit_price"
        case exitReason = "exit_reason"
        case pnl
        case pnlPct = "pnl_pct"
        case strategy
        case timestamp = "ts"
    }
    
    var isProfitable: Bool { (pnl ?? 0) > 0 }
}

struct TradesResponse: Codable {
    let success: Bool
    let trades: [Trade]?
    let total: Int?
    let error: String?
}

// MARK: - Stats Models
struct TradingStats: Codable {
    let total: Int?
    let totalTrades: Int?
    let wins: Int?
    let winningTrades: Int?
    let losses: Int?
    let losingTrades: Int?
    let winrate: Double?
    let winRate: Double?
    let totalPnl: Double?
    let avgPnlValue: Double?
    let avgWin: Double?
    let avgLoss: Double?
    let profitFactor: Double?
    let maxDrawdown: Double?
    let bestPnl: Double?
    let bestTrade: Double?
    let worstPnl: Double?
    let worstTrade: Double?
    
    enum CodingKeys: String, CodingKey {
        case total
        case totalTrades = "total_trades"
        case wins
        case winningTrades = "winning_trades"
        case losses
        case losingTrades = "losing_trades"
        case winrate
        case winRate = "win_rate"
        case totalPnl = "total_pnl"
        case avgPnlValue = "avg_pnl"
        case avgWin = "avg_win"
        case avgLoss = "avg_loss"
        case profitFactor = "profit_factor"
        case maxDrawdown = "max_drawdown"
        case bestPnl = "best_pnl"
        case bestTrade = "best_trade"
        case worstPnl = "worst_pnl"
        case worstTrade = "worst_trade"
    }
    
    // Computed properties for unified access
    var totalTradesCount: Int { total ?? totalTrades ?? 0 }
    var winningCount: Int { wins ?? winningTrades ?? 0 }
    var losingCount: Int { losses ?? losingTrades ?? 0 }
    var winRateValue: Double { winrate ?? winRate ?? 0 }
    var avgPnl: Double { avgPnlValue ?? 0 }
    var best: Double { bestPnl ?? bestTrade ?? 0 }
    var worst: Double { worstPnl ?? worstTrade ?? 0 }
}

struct StatsResponse: Codable {
    let success: Bool?
    let stats: TradingStats?
    let data: TradingStats?  // Backend may return data directly
    let error: String?
    
    // Get stats from either field or directly decode
    var statsData: TradingStats? {
        return stats ?? data
    }
}

// MARK: - Symbol Models
struct SymbolInfo: Codable, Identifiable {
    var id: String { symbol }
    
    let symbol: String
    let baseCoin: String
    let quoteCoin: String
    let minOrderQty: Double
    let maxOrderQty: Double
    let minPrice: Double
    let maxPrice: Double
    let tickSize: Double
    let qtyStep: Double
    let maxLeverage: Int
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case baseCoin = "base_coin"
        case quoteCoin = "quote_coin"
        case minOrderQty = "min_order_qty"
        case maxOrderQty = "max_order_qty"
        case minPrice = "min_price"
        case maxPrice = "max_price"
        case tickSize = "tick_size"
        case qtyStep = "qty_step"
        case maxLeverage = "max_leverage"
    }
}

struct SymbolsResponse: Codable {
    let success: Bool
    let symbols: [String]?
    let error: String?
}

// MARK: - Order Request/Response
struct PlaceOrderRequest: Codable {
    let symbol: String
    let side: String
    let orderType: String
    let qty: Double
    let price: Double?
    let takeProfit: Double?
    let stopLoss: Double?
    let leverage: Int?
    let reduceOnly: Bool?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case orderType = "order_type"
        case qty
        case price
        case takeProfit = "take_profit"
        case stopLoss = "stop_loss"
        case leverage
        case reduceOnly = "reduce_only"
    }
}

struct PlaceOrderResponse: Codable {
    let success: Bool
    let orderId: String?
    let message: String?
    let error: String?
    
    enum CodingKeys: String, CodingKey {
        case success
        case orderId = "order_id"
        case message
        case error
    }
}

struct ClosePositionRequest: Codable {
    let symbol: String
    let side: String?
    let qty: Double?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case qty
    }
}

struct ModifyTPSLRequest: Codable {
    let symbol: String
    let side: String
    let takeProfit: Double?
    let stopLoss: Double?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case takeProfit = "take_profit"
        case stopLoss = "stop_loss"
    }
}

// MARK: - Strategy Models
struct Strategy: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String?
    let baseStrategy: String
    let visibility: String
    let price: Double
    let performance: StrategyPerformance?
    let createdAt: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case description
        case baseStrategy = "base_strategy"
        case visibility
        case price
        case performance
        case createdAt = "created_at"
    }
}

struct StrategyPerformance: Codable {
    let winRate: Double?
    let totalPnl: Double?
    let totalTrades: Int?
    let profitFactor: Double?
    
    enum CodingKeys: String, CodingKey {
        case winRate = "win_rate"
        case totalPnl = "total_pnl"
        case totalTrades = "total_trades"
        case profitFactor = "profit_factor"
    }
}

// Marketplace strategy model for browsing/purchasing
struct MarketplaceStrategy: Codable, Identifiable {
    let id: Int
    let name: String
    let author: String
    let description: String?
    let rating: Double
    let winRate: Double
    let monthlyPnl: Double?
    let subscribers: Int?
    let price: Double
    let baseStrategy: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case author
        case description
        case rating
        case winRate = "win_rate"
        case monthlyPnl = "monthly_pnl"
        case subscribers
        case price
        case baseStrategy = "base_strategy"
    }
}

struct StrategySettings: Codable {
    let strategy: String
    let side: String
    let percent: Double
    let tpPercent: Double
    let slPercent: Double
    let leverage: Int
    let useAtr: Bool
    let dcaEnabled: Bool
    let direction: String
    let enabled: Bool
    
    enum CodingKeys: String, CodingKey {
        case strategy
        case side
        case percent
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case leverage
        case useAtr = "use_atr"
        case dcaEnabled = "dca_enabled"
        case direction
        case enabled
    }
}

// MARK: - Backtest Models
struct BacktestRequest: Codable {
    let strategy: String
    let symbol: String
    let timeframe: String
    let days: Int
    let initialBalance: Double
    let riskPerTrade: Double
    let stopLossPercent: Double
    let takeProfitPercent: Double
    
    enum CodingKeys: String, CodingKey {
        case strategy
        case symbol
        case timeframe
        case days
        case initialBalance = "initial_balance"
        case riskPerTrade = "risk_per_trade"
        case stopLossPercent = "stop_loss_percent"
        case takeProfitPercent = "take_profit_percent"
    }
}

struct BacktestResult: Codable, Identifiable {
    let id: String
    let strategy: String
    let symbol: String
    let timeframe: String
    let totalTrades: Int
    let winRate: Double
    let totalPnl: Double
    let maxDrawdown: Double
    let profitFactor: Double
    let sharpeRatio: Double?
    let trades: [BacktestTrade]?
    
    enum CodingKeys: String, CodingKey {
        case id
        case strategy
        case symbol
        case timeframe
        case totalTrades = "total_trades"
        case winRate = "win_rate"
        case totalPnl = "total_pnl"
        case maxDrawdown = "max_drawdown"
        case profitFactor = "profit_factor"
        case sharpeRatio = "sharpe_ratio"
        case trades
    }
}

struct BacktestTrade: Codable, Identifiable {
    var id: String { "\(entryTime)-\(side)" }
    
    let side: String
    let entryPrice: Double
    let exitPrice: Double
    let entryTime: String
    let exitTime: String
    let pnl: Double
    let pnlPercent: Double
    
    enum CodingKeys: String, CodingKey {
        case side
        case entryPrice = "entry_price"
        case exitPrice = "exit_price"
        case entryTime = "entry_time"
        case exitTime = "exit_time"
        case pnl
        case pnlPercent = "pnl_percent"
    }
}

// MARK: - LYXEN Token Models
struct ELCBalance: Codable {
    let balance: Double
    let lockedBalance: Double
    let totalEarned: Double
    let walletAddress: String?
    
    enum CodingKeys: String, CodingKey {
        case balance
        case lockedBalance = "locked_balance"
        case totalEarned = "total_earned"
        case walletAddress = "wallet_address"
    }
}

struct ELCTransaction: Codable, Identifiable {
    let id: Int
    let type: String
    let amount: Double
    let description: String?
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case type
        case amount
        case description
        case createdAt = "created_at"
    }
}

// MARK: - API Keys Models
struct APIKeysStatus: Codable {
    let bybit: ExchangeAPIStatus
    let hyperliquid: ExchangeAPIStatus
    
    struct ExchangeAPIStatus: Codable {
        let configured: Bool
        let hasDemo: Bool?
        let hasReal: Bool?
        let hasTestnet: Bool?
        let hasMainnet: Bool?
        
        enum CodingKeys: String, CodingKey {
            case configured
            case hasDemo = "has_demo"
            case hasReal = "has_real"
            case hasTestnet = "has_testnet"
            case hasMainnet = "has_mainnet"
        }
    }
}

// MARK: - Generic API Response
struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let error: String?
    let message: String?
}

struct SimpleResponse: Codable {
    let success: Bool
    let message: String?
    let error: String?
}
