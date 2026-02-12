//
//  Models.swift
//  EnlikoTrading
//
//  Data Models matching backend API responses
//

import Foundation
import SwiftUI  // For Color in Position model

// MARK: - AnyCodable Helper
// Used to decode any JSON value (object, array, string, number, bool, null)
struct AnyCodable: Codable, Hashable {
    let value: Any?
    
    init(_ value: Any?) {
        self.value = value
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if container.decodeNil() {
            value = nil
        } else if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if let string = try? container.decode(String.self) {
            value = string
        } else if let array = try? container.decode([AnyCodable].self) {
            value = array.map { $0.value }
        } else if let dict = try? container.decode([String: AnyCodable].self) {
            value = dict.mapValues { $0.value }
        } else {
            value = nil
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        if value == nil {
            try container.encodeNil()
        } else if let bool = value as? Bool {
            try container.encode(bool)
        } else if let int = value as? Int {
            try container.encode(int)
        } else if let double = value as? Double {
            try container.encode(double)
        } else if let string = value as? String {
            try container.encode(string)
        } else if let array = value as? [Any] {
            try container.encode(array.map { AnyCodable($0) })
        } else if let dict = value as? [String: Any] {
            try container.encode(dict.mapValues { AnyCodable($0) })
        } else {
            try container.encodeNil()
        }
    }
    
    // Hashable conformance (required for some Swift usage patterns)
    func hash(into hasher: inout Hasher) {
        if let string = value as? String {
            hasher.combine(string)
        } else if let int = value as? Int {
            hasher.combine(int)
        } else if let double = value as? Double {
            hasher.combine(double)
        } else if let bool = value as? Bool {
            hasher.combine(bool)
        }
    }
    
    static func == (lhs: AnyCodable, rhs: AnyCodable) -> Bool {
        // Simple equality check for common types
        if let lhsString = lhs.value as? String, let rhsString = rhs.value as? String {
            return lhsString == rhsString
        }
        if let lhsInt = lhs.value as? Int, let rhsInt = rhs.value as? Int {
            return lhsInt == rhsInt
        }
        if let lhsDouble = lhs.value as? Double, let rhsDouble = rhs.value as? Double {
            return lhsDouble == rhsDouble
        }
        if let lhsBool = lhs.value as? Bool, let rhsBool = rhs.value as? Bool {
            return lhsBool == rhsBool
        }
        if lhs.value == nil && rhs.value == nil {
            return true
        }
        return false
    }
}

// MARK: - User Models
struct User: Codable, Identifiable {
    // id is optional because server may only return user_id
    // Identifiable.id is computed from userId ?? _id ?? 0
    private let _id: Int?
    let userId: Int?
    let username: String?
    let email: String?
    let firstName: String?
    let lastName: String?
    let name: String?  // Server may return 'name' instead of firstName/lastName
    let lang: String?
    let exchangeType: String?
    let tradingMode: String?
    let hlTestnet: Bool?
    let isAllowed: Bool?
    let isPremium: Bool?
    let isAdmin: Bool?  // From verify endpoint
    let licenseType: String?
    let licenseExpiry: String?
    
    // Linked accounts info (Unified Auth)
    let telegramId: Int?
    let telegramUsername: String?
    let emailVerified: Bool?
    let authProvider: String?  // 'telegram', 'email', 'both'
    
    // Identifiable conformance - use userId or _id
    var id: Int {
        userId ?? _id ?? 0
    }
    
    enum CodingKeys: String, CodingKey {
        case _id = "id"
        case userId = "user_id"
        case username
        case email
        case firstName = "first_name"
        case lastName = "last_name"
        case name
        case lang
        case exchangeType = "exchange_type"
        case tradingMode = "trading_mode"
        case hlTestnet = "hl_testnet"
        case isAllowed = "is_allowed"
        case isPremium = "is_premium"
        case isAdmin = "is_admin"
        case licenseType = "license_type"
        case licenseExpiry = "license_expiry"
        // Linked accounts
        case telegramId = "telegram_id"
        case telegramUsername = "telegram_username"
        case emailVerified = "email_verified"
        case authProvider = "auth_provider"
    }
    
    var displayName: String {
        // Try name first (from verify), then firstName + lastName
        if let n = name, !n.isEmpty {
            return n
        }
        if let first = firstName {
            return lastName != nil ? "\(first) \(lastName!)" : first
        }
        return username ?? email ?? "User \(id)"
    }
    
    // Check if Telegram is linked
    var hasTelegramLinked: Bool {
        telegramId != nil || (userId ?? 0) > 0
    }
    
    // Check if email is linked
    var hasEmailLinked: Bool {
        email != nil && !(email?.isEmpty ?? true)
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
    // Core fields - all optional to handle API error responses
    private let _equity: Double?
    private let _available: Double?
    private let _unrealizedPnl: Double?
    let marginBalance: Double?
    let positionMarginFromAPI: Double?  // NEW: Direct from API
    let accountType: String?
    private let _currency: String?  // API returns "USDT" for Bybit, "USDC" for HL
    let error: String?  // API may return error message
    
    // Public accessors with defaults
    var equity: Double { _equity ?? 0 }
    var available: Double { _available ?? 0 }
    var unrealizedPnl: Double { _unrealizedPnl ?? 0 }
    
    // Computed properties for compatibility
    var totalEquity: Double { equity }
    // Use API value first, then compute fallback
    var positionMargin: Double { 
        positionMarginFromAPI ?? marginBalance ?? max(0, equity - available)
    }
    var currency: String { _currency ?? "USDT" }
    var hasError: Bool { error != nil }
    
    enum CodingKeys: String, CodingKey {
        case _equity = "equity"
        case _available = "available"
        case _unrealizedPnl = "unrealized_pnl"
        case marginBalance = "margin_balance"
        case positionMarginFromAPI = "position_margin"  // Maps to API field
        case accountType = "account_type"
        case _currency = "currency"
        case error
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
    
    // MARK: - Display Properties for Modern UI
    var displayEquity: Double { equity }
    var displayAvailable: Double { available }
    var displayUnrealizedPnl: Double { unrealizedPnl }
    var displayPositionMargin: Double { positionMargin }
    var displayTodayPnl: Double { unrealizedPnl } // Alias for compatibility
    
    // Additional stats (placeholder values, should come from API)
    var winRate: Double? { nil }
    var totalTrades: Int? { nil }
}

// MARK: - HyperLiquid Spot Balance
struct HLSpotToken: Codable, Identifiable {
    var id: String { token }
    let token: String
    let total: Double
    let available: Double
    let hold: Double
    let usdValue: Double
    
    enum CodingKeys: String, CodingKey {
        case token, total, available, hold
        case usdValue = "usd_value"
    }
}

struct HLSpotBalance: Codable {
    let tokens: [HLSpotToken]
    let totalUsdValue: Double
    let numTokens: Int
    let error: String?
    
    enum CodingKeys: String, CodingKey {
        case tokens
        case totalUsdValue = "total_usd_value"
        case numTokens = "num_tokens"
        case error
    }
    
    var hasBalance: Bool { totalUsdValue > 0 }
}

struct BalanceResponse: Codable {
    let success: Bool?
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
    // All numeric fields optional to handle API variations
    private let _size: Double?
    private let _entryPrice: Double?
    private let _markPrice: Double?
    private let _leverage: Int?
    // API returns either pnl or unrealized_pnl
    private let _pnl: Double?
    private let _unrealizedPnl: Double?
    // API returns either roe or pnl_percent
    private let _roe: Double?
    private let _pnlPercent: Double?
    // API returns either liq_price or liquidation_price
    private let _liqPrice: Double?
    private let _liquidationPrice: Double?
    // Backend returns tp_price/sl_price, also handle take_profit/stop_loss
    private let _takeProfit: Double?
    private let _stopLoss: Double?
    private let _tpPrice: Double?
    private let _slPrice: Double?
    // Computed: use tp_price (backend primary) with take_profit as fallback
    var takeProfit: Double? { _tpPrice ?? _takeProfit }
    var stopLoss: Double? { _slPrice ?? _stopLoss }
    let strategy: String?
    let createdAt: String?
    // API returns either margin or position_margin
    private let _margin: Double?
    private let _positionValue: Double?
    private let _positionMarginValue: Double?
    // Additional fields from API
    let exchange: String?
    let accountType: String?
    let env: String?
    let useAtr: Bool?
    let atrActivated: Bool?
    let error: String?
    
    // Public accessors with fallbacks
    var size: Double { _size ?? 0 }
    var entryPrice: Double { _entryPrice ?? 0 }
    var markPrice: Double { _markPrice ?? 0 }
    var leverage: Int { _leverage ?? 10 }
    var unrealizedPnl: Double { _pnl ?? _unrealizedPnl ?? 0 }
    var pnlPercent: Double { _roe ?? _pnlPercent ?? 0 }
    var liquidationPrice: Double? { _liqPrice ?? _liquidationPrice }
    var positionValue: Double { _positionValue ?? (size * markPrice) }
    var positionMarginValue: Double { _margin ?? _positionMarginValue ?? (positionValue / Double(leverage)) }
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case _size = "size"
        case _entryPrice = "entry_price"
        case _markPrice = "mark_price"
        case _leverage = "leverage"
        case _pnl = "pnl"
        case _unrealizedPnl = "unrealized_pnl"
        case _roe = "roe"
        case _pnlPercent = "pnl_percent"
        case _liqPrice = "liq_price"
        case _liquidationPrice = "liquidation_price"
        case _takeProfit = "take_profit"
        case _stopLoss = "stop_loss"
        case _tpPrice = "tp_price"
        case _slPrice = "sl_price"
        case strategy
        case createdAt = "created_at"
        case _margin = "margin"
        case _positionValue = "position_value"
        case _positionMarginValue = "position_margin"
        case exchange
        case accountType = "account_type"
        case env
        case useAtr = "use_atr"
        case atrActivated = "atr_activated"
        case error
    }
    
    // Custom decoder to handle leverage as String (Bybit API) or Int
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        symbol = try container.decode(String.self, forKey: .symbol)
        side = try container.decode(String.self, forKey: .side)
        _size = try container.decodeIfPresent(Double.self, forKey: ._size)
        _entryPrice = try container.decodeIfPresent(Double.self, forKey: ._entryPrice)
        _markPrice = try container.decodeIfPresent(Double.self, forKey: ._markPrice)
        // Leverage: Bybit returns as string "10", HL returns as int 10
        if let intVal = try? container.decodeIfPresent(Int.self, forKey: ._leverage) {
            _leverage = intVal
        } else if let strVal = try? container.decodeIfPresent(String.self, forKey: ._leverage),
                  let parsed = Int(strVal) {
            _leverage = parsed
        } else {
            _leverage = nil
        }
        _pnl = try container.decodeIfPresent(Double.self, forKey: ._pnl)
        _unrealizedPnl = try container.decodeIfPresent(Double.self, forKey: ._unrealizedPnl)
        _roe = try container.decodeIfPresent(Double.self, forKey: ._roe)
        _pnlPercent = try container.decodeIfPresent(Double.self, forKey: ._pnlPercent)
        _liqPrice = try container.decodeIfPresent(Double.self, forKey: ._liqPrice)
        _liquidationPrice = try container.decodeIfPresent(Double.self, forKey: ._liquidationPrice)
        _takeProfit = try container.decodeIfPresent(Double.self, forKey: ._takeProfit)
        _stopLoss = try container.decodeIfPresent(Double.self, forKey: ._stopLoss)
        _tpPrice = try container.decodeIfPresent(Double.self, forKey: ._tpPrice)
        _slPrice = try container.decodeIfPresent(Double.self, forKey: ._slPrice)
        strategy = try container.decodeIfPresent(String.self, forKey: .strategy)
        createdAt = try container.decodeIfPresent(String.self, forKey: .createdAt)
        _margin = try container.decodeIfPresent(Double.self, forKey: ._margin)
        _positionValue = try container.decodeIfPresent(Double.self, forKey: ._positionValue)
        _positionMarginValue = try container.decodeIfPresent(Double.self, forKey: ._positionMarginValue)
        exchange = try container.decodeIfPresent(String.self, forKey: .exchange)
        accountType = try container.decodeIfPresent(String.self, forKey: .accountType)
        env = try container.decodeIfPresent(String.self, forKey: .env)
        useAtr = try container.decodeIfPresent(Bool.self, forKey: .useAtr)
        atrActivated = try container.decodeIfPresent(Bool.self, forKey: .atrActivated)
        error = try container.decodeIfPresent(String.self, forKey: .error)
    }
    
    var isLong: Bool { side.lowercased() == "buy" || side.lowercased() == "long" }
    var positionSide: PositionSide { isLong ? .long : .short }
    
    var formattedPnl: String {
        let sign = unrealizedPnl >= 0 ? "+" : ""
        return String(format: "%@$%.2f (%.2f%%)", sign, unrealizedPnl, pnlPercent)
    }
    
    var notionalValue: Double { positionValue }
    var positionMargin: Double { positionMarginValue }
    var hasError: Bool { error != nil }
    
    // MARK: - Display Properties for Modern UI
    var displaySymbol: String { symbol.replacingOccurrences(of: "USDT", with: "") }
    var displayLeverage: Int { leverage }
    var displayPnl: Double { unrealizedPnl }
    var displayPnlPercent: Double { pnlPercent }
    var displayEntryPrice: Double { entryPrice }
    var displayMarkPrice: Double { markPrice }
    var displaySize: Double { size }
    var displayLiqPrice: Double { liquidationPrice ?? 0 }
    // TP/SL display uses computed takeProfit/stopLoss which already combines both keys
    var displayTpPrice: Double { takeProfit ?? 0 }
    var displaySlPrice: Double { stopLoss ?? 0 }
    
    // MARK: - Properties for PositionDetailView
    var pnl: Double { unrealizedPnl }
    var margin: Double? { _margin ?? _positionMarginValue }
    var maintenanceMargin: Double? { (positionValue / Double(leverage)) * 0.005 }
    var openTime: Date? {
        guard let created = createdAt else { return nil }
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter.date(from: created)
    }
    
    // Formatted display strings
    var pnlDisplay: String {
        let sign = pnl >= 0 ? "+" : ""
        return String(format: "%@$%.2f", sign, pnl)
    }
    
    var pnlPercentDisplay: String {
        let sign = pnlPercent >= 0 ? "+" : ""
        return String(format: "%@%.2f%%", sign, pnlPercent)
    }
    
    var pnlColor: Color {
        pnl >= 0 ? Color.green : Color.red
    }
}

extension Position: Hashable {
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
    
    static func == (lhs: Position, rhs: Position) -> Bool {
        lhs.id == rhs.id
    }
    
    // MARK: - Mock for Previews
    static var mock: Position {
        let json = """
        {
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": 0.5,
            "entry_price": 95000,
            "mark_price": 96250,
            "leverage": 10,
            "pnl": 1250.50,
            "pnl_percent": 2.63,
            "take_profit": 100000,
            "stop_loss": 92000,
            "strategy": "oi"
        }
        """.data(using: .utf8)!
        return try! JSONDecoder().decode(Position.self, from: json)
    }
    
    static var mockShort: Position {
        let json = """
        {
            "symbol": "ETHUSDT",
            "side": "Sell",
            "size": 2.0,
            "entry_price": 3400,
            "mark_price": 3350,
            "leverage": 5,
            "pnl": 100.0,
            "pnl_percent": 1.47,
            "take_profit": 3200,
            "stop_loss": 3500,
            "strategy": "scryptomera"
        }
        """.data(using: .utf8)!
        return try! JSONDecoder().decode(Position.self, from: json)
    }
}

struct PositionsResponse: Codable {
    let success: Bool?
    let positions: [Position]?
    let data: [Position]?  // API may return positions in data field
    let error: String?
    
    // Get positions from either field
    var positionsData: [Position] {
        return positions ?? data ?? []
    }
}

// MARK: - Order Models
struct Order: Codable, Identifiable {
    // orderId may come as order_id, orderId, or id
    private let _orderId: String?
    private let _orderIdAlt: String?
    private let _id: String?  // API may also return just "id"
    let symbol: String
    let side: String
    private let _orderType: String?
    private let _orderTypeAlt: String?  // Backend may also return "type"
    private let _qty: Double?
    private let _size: Double?  // Backend may return "size" instead of "qty"
    let price: Double?
    let triggerPrice: Double?
    let status: String?
    let createdAt: String?
    let error: String?
    
    // Bug #8 Fix: Don't use UUID fallback - return "unknown" for debugging
    // This prevents accidental cancel of random orders
    var orderId: String { _orderId ?? _orderIdAlt ?? _id ?? "unknown_\(symbol)_\(side)" }
    var id: String { orderId }
    var orderType: String { _orderType ?? _orderTypeAlt ?? "limit" }
    var qty: Double { _qty ?? _size ?? 0 }
    var hasValidOrderId: Bool { _orderId != nil || _orderIdAlt != nil || _id != nil }
    
    enum CodingKeys: String, CodingKey {
        case _orderId = "order_id"
        case _orderIdAlt = "orderId"
        case _id = "id"
        case symbol
        case side
        case _orderType = "order_type"
        case _orderTypeAlt = "type"
        case _qty = "qty"
        case _size = "size"
        case price
        case triggerPrice = "trigger_price"
        case status
        case createdAt = "created_at"
        case error
    }
    
    var isLimitOrder: Bool { orderType.lowercased() == "limit" }
    var hasError: Bool { error != nil }
    
    // MARK: - Display Properties for Modern UI
    var isLong: Bool { side.lowercased() == "buy" || side.lowercased() == "long" }
    var displaySymbol: String { symbol.replacingOccurrences(of: "USDT", with: "") }
    var displayOrderType: String { orderType }
    var displayQty: Double { qty }
    var displayPrice: Double { price ?? 0 }
}

struct OrdersResponse: Codable {
    let success: Bool?
    let orders: [Order]?
    let data: [Order]?  // API may return orders in data field
    let error: String?
    
    var ordersData: [Order] {
        return orders ?? data ?? []
    }
}

// MARK: - Trade Models
struct Trade: Codable, Identifiable {
    var id: String { "\(symbol)-\(timestamp)" }
    
    let symbol: String
    let side: String
    private let _entryPrice: Double?
    private let _exitPrice: Double?
    let exitReason: String?
    private let _pnl: Double?
    private let _pnlPct: Double?
    let strategy: String?
    // API returns ts, but may also return timestamp
    private let _ts: String?
    private let _timestamp: String?
    let error: String?
    
    var entryPrice: Double { _entryPrice ?? 0 }
    var exitPrice: Double? { _exitPrice }
    var pnl: Double? { _pnl }
    var pnlPct: Double? { _pnlPct }
    var timestamp: String { _ts ?? _timestamp ?? "" }
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case _entryPrice = "entry_price"
        case _exitPrice = "exit_price"
        case exitReason = "exit_reason"
        case _pnl = "pnl"
        case _pnlPct = "pnl_pct"
        case strategy
        case _ts = "ts"
        case _timestamp = "timestamp"
        case error
    }
    
    var isProfitable: Bool { (pnl ?? 0) > 0 }
    var hasError: Bool { error != nil }
}

struct TradesResponse: Codable {
    let success: Bool?
    let trades: [Trade]?
    let data: [Trade]?  // API may return trades in data field
    let total: Int?
    let error: String?
    
    var tradesData: [Trade] {
        return trades ?? data ?? []
    }
}

// MARK: - Stats Models
struct TradingStats: Codable {
    // All fields optional - API may return different field names
    // Total trades
    let total: Int?
    let totalTrades: Int?
    // Wins
    let wins: Int?
    let winningTrades: Int?
    // Losses
    let losses: Int?
    let losingTrades: Int?
    // EOD (end of day) trades
    let eodTrades: Int?
    // Win rate
    let winrate: Double?
    let winRate: Double?
    // PnL
    let totalPnl: Double?
    let avgPnl: Double?
    let avgPnlValue: Double?
    let avgWin: Double?
    let avgLoss: Double?
    let grossProfit: Double?
    let grossLoss: Double?
    // Performance metrics
    let profitFactor: Double?
    let maxDrawdown: Double?
    // Best/Worst trades
    let bestPnl: Double?
    let bestTrade: Double?
    let worstPnl: Double?
    let worstTrade: Double?
    // Long/Short breakdown
    let longCount: Int?
    let shortCount: Int?
    let longWinrate: Double?
    let shortWinrate: Double?
    // Open positions count
    let openCount: Int?
    // Error
    let error: String?
    
    enum CodingKeys: String, CodingKey {
        case total
        case totalTrades = "total_trades"
        case wins
        case winningTrades = "winning_trades"
        case losses
        case losingTrades = "losing_trades"
        case eodTrades = "eod_trades"
        case winrate
        case winRate = "win_rate"
        case totalPnl = "total_pnl"
        case avgPnl = "avg_pnl"
        case avgPnlValue = "avg_pnl_value"
        case avgWin = "avg_win"
        case avgLoss = "avg_loss"
        case grossProfit = "gross_profit"
        case grossLoss = "gross_loss"
        case profitFactor = "profit_factor"
        case maxDrawdown = "max_drawdown"
        case bestPnl = "best_pnl"
        case bestTrade = "best_trade"
        case worstPnl = "worst_pnl"
        case worstTrade = "worst_trade"
        case longCount = "long_count"
        case shortCount = "short_count"
        case longWinrate = "long_winrate"
        case shortWinrate = "short_winrate"
        case openCount = "open_count"
        case error
    }
    
    // Computed properties for unified access
    var totalTradesCount: Int { total ?? totalTrades ?? 0 }
    var winningCount: Int { wins ?? winningTrades ?? 0 }
    var losingCount: Int { losses ?? losingTrades ?? 0 }
    var eodCount: Int { eodTrades ?? 0 }
    var winRateValue: Double { winrate ?? winRate ?? 0 }
    var avgPnlPct: Double { avgPnl ?? avgPnlValue ?? 0 }
    var best: Double { bestPnl ?? bestTrade ?? 0 }
    var worst: Double { worstPnl ?? worstTrade ?? 0 }
    var hasError: Bool { error != nil }
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
    
    // API returns these fields (from /symbols endpoint)
    private let _base: String?
    private let _price: Double?
    private let _change24h: Double?
    private let _high24h: Double?
    private let _low24h: Double?
    private let _volume24h: Double?
    private let _volumeFormatted: String?
    private let _fundingRate: Double?
    private let _openInterest: Double?
    
    // Legacy fields (for backwards compatibility)
    private let _baseCoin: String?
    private let _quoteCoin: String?
    private let _minOrderQty: Double?
    private let _maxOrderQty: Double?
    private let _minPrice: Double?
    private let _maxPrice: Double?
    private let _tickSize: Double?
    private let _qtyStep: Double?
    private let _maxLeverage: Int?
    
    // MARK: - Computed Properties
    var base: String { _base ?? _baseCoin ?? symbol.replacingOccurrences(of: "USDT", with: "") }
    var quoteCoin: String { _quoteCoin ?? "USDT" }
    var price: Double { _price ?? 0 }
    var change24h: Double { _change24h ?? 0 }
    var high24h: Double { _high24h ?? 0 }
    var low24h: Double { _low24h ?? 0 }
    var volume24h: Double { _volume24h ?? 0 }
    var volumeFormatted: String { _volumeFormatted ?? "$0" }
    var fundingRate: Double { _fundingRate ?? 0 }
    var openInterest: Double { _openInterest ?? 0 }
    
    // Legacy accessors
    var minOrderQty: Double { _minOrderQty ?? 0.001 }
    var maxOrderQty: Double { _maxOrderQty ?? 10000 }
    var minPrice: Double { _minPrice ?? 0.0001 }
    var maxPrice: Double { _maxPrice ?? 1000000 }
    var tickSize: Double { _tickSize ?? 0.01 }
    var qtyStep: Double { _qtyStep ?? 0.001 }
    var maxLeverage: Int { _maxLeverage ?? 100 }
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case _base = "base"
        case _price = "price"
        case _change24h = "change_24h"
        case _high24h = "high_24h"
        case _low24h = "low_24h"
        case _volume24h = "volume_24h"
        case _volumeFormatted = "volume_formatted"
        case _fundingRate = "funding_rate"
        case _openInterest = "open_interest"
        // Legacy
        case _baseCoin = "base_coin"
        case _quoteCoin = "quote_coin"
        case _minOrderQty = "min_order_qty"
        case _maxOrderQty = "max_order_qty"
        case _minPrice = "min_price"
        case _maxPrice = "max_price"
        case _tickSize = "tick_size"
        case _qtyStep = "qty_step"
        case _maxLeverage = "max_leverage"
    }
}

struct SymbolsResponse: Codable {
    private let _success: Bool?
    let symbols: [SymbolInfo]?
    let data: [SymbolInfo]?
    let total: Int?
    let error: String?
    
    var success: Bool { _success ?? (symbols != nil || data != nil) }
    var symbolsData: [SymbolInfo] { symbols ?? data ?? [] }
    var hasError: Bool { error != nil }
    
    enum CodingKeys: String, CodingKey {
        case _success = "success"
        case symbols, data, total, error
    }
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
    let exchange: String?
    let accountType: String?
    
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
        case exchange
        case accountType = "account_type"
    }
}

struct PlaceOrderResponse: Codable {
    private let _success: Bool?
    private let _orderId: String?
    private let _orderIdSnake: String?
    let message: String?
    let error: String?
    let exchange: String?
    let accountType: String?
    let symbol: String?
    let side: String?
    let size: Double?
    
    var success: Bool { _success ?? false }
    var orderId: String { _orderId ?? _orderIdSnake ?? "" }
    var hasError: Bool { error != nil || !success }
    
    enum CodingKeys: String, CodingKey {
        case _success = "success"
        case _orderId = "orderId"
        case _orderIdSnake = "order_id"
        case message, error, exchange, symbol, side, size
        case accountType = "account_type"
    }
}

struct ClosePositionRequest: Codable {
    let symbol: String
    let side: String?
    let qty: Double?
    let exchange: String?
    let accountType: String?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case qty
        case exchange
        case accountType = "account_type"
    }
}

struct ModifyTPSLRequest: Codable {
    let symbol: String
    let side: String
    let takeProfit: Double?
    let stopLoss: Double?
    let exchange: String?
    let accountType: String?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case side
        case takeProfit = "take_profit"
        case stopLoss = "stop_loss"
        case exchange
        case accountType = "account_type"
    }
}

// MARK: - Strategy Models
struct Strategy: Codable, Identifiable {
    private let _id: Int?
    private let _name: String?
    let description: String?
    private let _baseStrategy: String?
    private let _visibility: String?
    private let _price: Double?
    let performance: StrategyPerformance?
    let createdAt: String?
    
    // Computed properties
    var id: Int { _id ?? 0 }
    var name: String { _name ?? "Unknown" }
    var baseStrategy: String { _baseStrategy ?? "custom" }
    var visibility: String { _visibility ?? "private" }
    var price: Double { _price ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case _id = "id"
        case _name = "name"
        case description
        case _baseStrategy = "base_strategy"
        case _visibility = "visibility"
        case _price = "price"
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
    private let _id: Int?
    let name: String?
    let author: String?
    let description: String?
    private let _rating: Double?
    private let _winRate: Double?
    let monthlyPnl: Double?
    let subscribers: Int?
    private let _price: Double?
    let baseStrategy: String?
    
    // Computed properties
    var id: Int { _id ?? 0 }
    var rating: Double { _rating ?? 0 }
    var winRate: Double { _winRate ?? 0 }
    var price: Double { _price ?? 0 }
    var displayName: String { name ?? "Unknown Strategy" }
    var displayAuthor: String { author ?? "Unknown" }
    
    enum CodingKeys: String, CodingKey {
        case _id = "id"
        case name, author, description
        case _rating = "rating"
        case _winRate = "win_rate"
        case monthlyPnl = "monthly_pnl"
        case subscribers
        case _price = "price"
        case baseStrategy = "base_strategy"
    }
}

// MARK: - Strategy Settings (4D Schema)
struct StrategySettings: Codable, Identifiable {
    var id: String { "\(strategy)_\(side)_\(exchange)" }
    
    let strategy: String
    let side: String
    let exchange: String
    let accountType: String
    let percent: Double
    let tpPercent: Double
    let slPercent: Double
    let leverage: Int
    let useAtr: Bool
    let atrTriggerPct: Double?
    let atrStepPct: Double?
    let dcaEnabled: Bool
    let dcaPct1: Double?
    let dcaPct2: Double?
    let maxPositions: Int
    let coinsGroup: String
    let direction: String
    let orderType: String
    let enabled: Bool
    // Break-Even fields
    let beEnabled: Bool
    let beTriggerPct: Double?
    // Partial Take Profit fields
    let partialTpEnabled: Bool
    let partialTp1TriggerPct: Double?
    let partialTp1ClosePct: Double?
    let partialTp2TriggerPct: Double?
    let partialTp2ClosePct: Double?
    
    enum CodingKeys: String, CodingKey {
        case strategy
        case side
        case exchange
        case accountType = "account_type"
        case percent
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case leverage
        case useAtr = "use_atr"
        case atrTriggerPct = "atr_trigger_pct"
        case atrStepPct = "atr_step_pct"
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
        case maxPositions = "max_positions"
        case coinsGroup = "coins_group"
        case direction
        case orderType = "order_type"
        case enabled
        case beEnabled = "be_enabled"
        case beTriggerPct = "be_trigger_pct"
        case partialTpEnabled = "partial_tp_enabled"
        case partialTp1TriggerPct = "partial_tp_1_trigger_pct"
        case partialTp1ClosePct = "partial_tp_1_close_pct"
        case partialTp2TriggerPct = "partial_tp_2_trigger_pct"
        case partialTp2ClosePct = "partial_tp_2_close_pct"
    }
    
    // Default values for optional fields
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        strategy = try container.decode(String.self, forKey: .strategy)
        side = try container.decode(String.self, forKey: .side)
        exchange = try container.decodeIfPresent(String.self, forKey: .exchange) ?? "bybit"
        accountType = try container.decodeIfPresent(String.self, forKey: .accountType) ?? "demo"
        percent = try container.decodeIfPresent(Double.self, forKey: .percent) ?? 1.0
        tpPercent = try container.decodeIfPresent(Double.self, forKey: .tpPercent) ?? 8.0
        slPercent = try container.decodeIfPresent(Double.self, forKey: .slPercent) ?? 3.0
        leverage = try container.decodeIfPresent(Int.self, forKey: .leverage) ?? 10
        useAtr = try container.decodeIfPresent(Bool.self, forKey: .useAtr) ?? false
        atrTriggerPct = try container.decodeIfPresent(Double.self, forKey: .atrTriggerPct)
        atrStepPct = try container.decodeIfPresent(Double.self, forKey: .atrStepPct)
        dcaEnabled = try container.decodeIfPresent(Bool.self, forKey: .dcaEnabled) ?? false
        dcaPct1 = try container.decodeIfPresent(Double.self, forKey: .dcaPct1)
        dcaPct2 = try container.decodeIfPresent(Double.self, forKey: .dcaPct2)
        maxPositions = try container.decodeIfPresent(Int.self, forKey: .maxPositions) ?? 0
        coinsGroup = try container.decodeIfPresent(String.self, forKey: .coinsGroup) ?? "ALL"
        direction = try container.decodeIfPresent(String.self, forKey: .direction) ?? "all"
        orderType = try container.decodeIfPresent(String.self, forKey: .orderType) ?? "market"
        enabled = try container.decodeIfPresent(Bool.self, forKey: .enabled) ?? true
        beEnabled = try container.decodeIfPresent(Bool.self, forKey: .beEnabled) ?? false
        beTriggerPct = try container.decodeIfPresent(Double.self, forKey: .beTriggerPct)
        partialTpEnabled = try container.decodeIfPresent(Bool.self, forKey: .partialTpEnabled) ?? false
        partialTp1TriggerPct = try container.decodeIfPresent(Double.self, forKey: .partialTp1TriggerPct)
        partialTp1ClosePct = try container.decodeIfPresent(Double.self, forKey: .partialTp1ClosePct)
        partialTp2TriggerPct = try container.decodeIfPresent(Double.self, forKey: .partialTp2TriggerPct)
        partialTp2ClosePct = try container.decodeIfPresent(Double.self, forKey: .partialTp2ClosePct)
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
    // Primary fields
    private let _id: String?
    let strategy: String?
    let symbol: String?
    let timeframe: String?
    
    // Metrics (all optional for safety)
    private let _totalTrades: Int?
    private let _winningTrades: Int?
    private let _losingTrades: Int?
    private let _winRate: Double?
    private let _totalPnl: Double?
    private let _totalPnlPercent: Double?
    private let _maxDrawdown: Double?
    private let _maxDrawdownPercent: Double?
    private let _profitFactor: Double?
    private let _sharpeRatio: Double?
    private let _finalBalance: Double?
    
    let trades: [BacktestTrade]?
    let equityCurve: [[Double]]?
    
    // MARK: - Computed Properties
    var id: String { _id ?? UUID().uuidString }
    var totalTrades: Int { _totalTrades ?? 0 }
    var winningTrades: Int { _winningTrades ?? 0 }
    var losingTrades: Int { _losingTrades ?? 0 }
    var winRate: Double { _winRate ?? 0 }
    var totalPnl: Double { _totalPnl ?? 0 }
    var totalPnlPercent: Double { _totalPnlPercent ?? 0 }
    var maxDrawdown: Double { _maxDrawdown ?? _maxDrawdownPercent ?? 0 }
    var profitFactor: Double { _profitFactor ?? 0 }
    var sharpeRatio: Double { _sharpeRatio ?? 0 }
    var finalBalance: Double { _finalBalance ?? 0 }
    
    // MARK: - Convenience Init (for testing/mocking)
    init(
        id: String = UUID().uuidString,
        strategy: String? = nil,
        symbol: String? = nil,
        timeframe: String? = nil,
        totalTrades: Int = 0,
        winRate: Double = 0,
        totalPnl: Double = 0,
        maxDrawdown: Double = 0,
        profitFactor: Double = 0,
        sharpeRatio: Double = 0,
        trades: [BacktestTrade]? = nil
    ) {
        self._id = id
        self.strategy = strategy
        self.symbol = symbol
        self.timeframe = timeframe
        self._totalTrades = totalTrades
        self._winningTrades = nil
        self._losingTrades = nil
        self._winRate = winRate
        self._totalPnl = totalPnl
        self._totalPnlPercent = nil
        self._maxDrawdown = maxDrawdown
        self._maxDrawdownPercent = nil
        self._profitFactor = profitFactor
        self._sharpeRatio = sharpeRatio
        self._finalBalance = nil
        self.trades = trades
        self.equityCurve = nil
    }
    
    enum CodingKeys: String, CodingKey {
        case _id = "id"
        case strategy, symbol, timeframe
        case _totalTrades = "total_trades"
        case _winningTrades = "winning_trades"
        case _losingTrades = "losing_trades"
        case _winRate = "win_rate"
        case _totalPnl = "total_pnl"
        case _totalPnlPercent = "total_pnl_percent"
        case _maxDrawdown = "max_drawdown"
        case _maxDrawdownPercent = "max_drawdown_percent"
        case _profitFactor = "profit_factor"
        case _sharpeRatio = "sharpe_ratio"
        case _finalBalance = "final_balance"
        case trades
        case equityCurve = "equity_curve"
    }
}

struct BacktestTrade: Codable, Identifiable {
    var id: String { "\(entryTime)-\(side)" }
    
    let side: String
    private let _entryPrice: Double?
    private let _exitPrice: Double?
    private let _entryTime: String?
    private let _exitTime: String?
    private let _pnl: Double?
    private let _pnlPercent: Double?
    
    // Computed properties
    var entryPrice: Double { _entryPrice ?? 0 }
    var exitPrice: Double { _exitPrice ?? 0 }
    var entryTime: String { _entryTime ?? "" }
    var exitTime: String { _exitTime ?? "" }
    var pnl: Double { _pnl ?? 0 }
    var pnlPercent: Double { _pnlPercent ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case side
        case _entryPrice = "entry_price"
        case _exitPrice = "exit_price"
        case _entryTime = "entry_time"
        case _exitTime = "exit_time"
        case _pnl = "pnl"
        case _pnlPercent = "pnl_percent"
    }
}

// MARK: - ENLIKO Token Models
struct ELCBalance: Codable {
    // Primary fields from API
    private let _available: Double?
    private let _staked: Double?
    private let _locked: Double?
    private let _total: Double?
    
    // Legacy fields (backwards compatibility)
    private let _balance: Double?
    private let _lockedBalance: Double?
    private let _totalEarned: Double?
    let walletAddress: String?
    
    // MARK: - Computed Properties
    var available: Double { _available ?? _balance ?? 0 }
    var staked: Double { _staked ?? 0 }
    var locked: Double { _locked ?? _lockedBalance ?? 0 }
    var total: Double { _total ?? _totalEarned ?? (available + staked + locked) }
    
    // Legacy accessors
    var balance: Double { available }
    var lockedBalance: Double { locked }
    var totalEarned: Double { total }
    
    enum CodingKeys: String, CodingKey {
        case _available = "available"
        case _staked = "staked"
        case _locked = "locked"
        case _total = "total"
        case _balance = "balance"
        case _lockedBalance = "locked_balance"
        case _totalEarned = "total_earned"
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
    // API returns flat structure, not nested
    let demoApiKey: String?
    let realApiKey: String?
    let hlWalletAddress: String?
    let hlVaultAddress: String?
    let hlTestnet: Bool?
    let hlHasKey: Bool?
    
    // Convenience accessors
    var hasBybitDemo: Bool { demoApiKey != nil && !demoApiKey!.isEmpty }
    var hasBybitReal: Bool { realApiKey != nil && !realApiKey!.isEmpty }
    var hasHyperliquid: Bool { hlHasKey ?? false }
    
    // For backward compatibility - synthesize nested structure
    var bybit: ExchangeAPIStatus {
        ExchangeAPIStatus(
            configured: hasBybitDemo || hasBybitReal,
            hasDemo: hasBybitDemo,
            hasReal: hasBybitReal,
            hasTestnet: nil,
            hasMainnet: nil
        )
    }
    
    var hyperliquid: ExchangeAPIStatus {
        ExchangeAPIStatus(
            configured: hasHyperliquid,
            hasDemo: nil,
            hasReal: nil,
            hasTestnet: hlTestnet ?? false,
            hasMainnet: hlTestnet == false
        )
    }
    
    enum CodingKeys: String, CodingKey {
        case demoApiKey = "demo_api_key"
        case realApiKey = "real_api_key"
        case hlWalletAddress = "hl_wallet_address"
        case hlVaultAddress = "hl_vault_address"
        case hlTestnet = "hl_testnet"
        case hlHasKey = "hl_has_key"
    }
    
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
    private let _success: Bool?
    let data: T?
    let error: String?
    let message: String?
    
    var success: Bool { _success ?? (error == nil && data != nil) }
    
    enum CodingKeys: String, CodingKey {
        case _success = "success"
        case data, error, message
    }
}

struct SimpleResponse: Codable {
    private let _success: Bool?
    let message: String?
    let error: String?
    
    var success: Bool { _success ?? (error == nil) }
    var hasError: Bool { error != nil }
    
    enum CodingKeys: String, CodingKey {
        case _success = "success"
        case message, error
    }
}

// MARK: - Validation Error Response (FastAPI format)
struct ValidationErrorResponse: Codable {
    let detail: [ValidationErrorDetail]?
    
    struct ValidationErrorDetail: Codable {
        let type: String?
        let loc: [LocValue]?
        let msg: String
        let input: String?
        let ctx: AnyCodable?  // Can be any JSON object
        
        // Ignore unknown fields
        enum CodingKeys: String, CodingKey {
            case type, loc, msg, input, ctx
        }
        
        // Custom decoder for loc which can be String or Int
        enum LocValue: Codable {
            case string(String)
            case int(Int)
            
            init(from decoder: Decoder) throws {
                let container = try decoder.singleValueContainer()
                if let stringValue = try? container.decode(String.self) {
                    self = .string(stringValue)
                } else if let intValue = try? container.decode(Int.self) {
                    self = .int(intValue)
                } else {
                    self = .string("unknown")
                }
            }
            
            func encode(to encoder: Encoder) throws {
                var container = encoder.singleValueContainer()
                switch self {
                case .string(let value): try container.encode(value)
                case .int(let value): try container.encode(value)
                }
            }
            
            var stringValue: String {
                switch self {
                case .string(let s): return s
                case .int(let i): return String(i)
                }
            }
        }
        
        // Get field name from loc array
        var fieldName: String {
            guard let loc = loc, loc.count > 1 else { return "" }
            return loc.last?.stringValue ?? ""
        }
        
        // Get user-friendly message
        var userFriendlyMessage: String {
            let field = fieldName.capitalized
            
            // Remove "Value error, " prefix from Pydantic messages
            let cleanMsg = msg.replacingOccurrences(of: "Value error, ", with: "")
            
            // Parse common validation messages
            if cleanMsg.lowercased().contains("at least 8 characters") {
                return "error_password_min_8".localized
            }
            if cleanMsg.lowercased().contains("letters and numbers") || cleanMsg.lowercased().contains("contain letters and numbers") {
                return "error_password_alphanumeric".localized
            }
            if cleanMsg.lowercased().contains("valid email") || cleanMsg.lowercased().contains("@-sign") || cleanMsg.lowercased().contains("email address") {
                return "error_invalid_email".localized
            }
            if cleanMsg.lowercased().contains("field required") || cleanMsg.lowercased().contains("required") {
                return String(format: "error_field_required".localized, field)
            }
            
            // Default: return cleaned message
            return cleanMsg
        }
    }
    
    // Get combined user-friendly error message
    var userFriendlyMessage: String {
        guard let details = detail, !details.isEmpty else {
            return "error_validation".localized
        }
        
        // Return all unique error messages
        let messages = details.map { $0.userFriendlyMessage }
        return messages.joined(separator: "\n")
    }
}

// MARK: - Strategy Settings Update Request (for API calls)
struct StrategySettingsUpdateRequest: Codable {
    let side: String
    let exchange: String
    let accountType: String
    let enabled: Bool
    let percent: Double
    let tpPercent: Double
    let slPercent: Double
    let leverage: Int
    let useAtr: Bool
    let atrTriggerPct: Double
    let atrStepPct: Double
    let dcaEnabled: Bool
    let dcaPct1: Double
    let dcaPct2: Double
    let orderType: String
    // Order limits
    let maxPositions: Int
    let coinsGroup: String
    // Break-Even
    let beEnabled: Bool
    let beTriggerPct: Double
    // Partial Take Profit
    let partialTpEnabled: Bool
    let partialTp1TriggerPct: Double
    let partialTp1ClosePct: Double
    let partialTp2TriggerPct: Double
    let partialTp2ClosePct: Double
    
    enum CodingKeys: String, CodingKey {
        case side, exchange, enabled, percent, leverage
        case accountType = "account_type"
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case useAtr = "use_atr"
        case atrTriggerPct = "atr_trigger_pct"
        case atrStepPct = "atr_step_pct"
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
        case orderType = "order_type"
        case maxPositions = "max_positions"
        case coinsGroup = "coins_group"
        case beEnabled = "be_enabled"
        case beTriggerPct = "be_trigger_pct"
        case partialTpEnabled = "partial_tp_enabled"
        case partialTp1TriggerPct = "partial_tp_1_trigger_pct"
        case partialTp1ClosePct = "partial_tp_1_close_pct"
        case partialTp2TriggerPct = "partial_tp_2_trigger_pct"
        case partialTp2ClosePct = "partial_tp_2_close_pct"
    }
}

// MARK: - Display Extensions for Trading View
extension Position {
    var sideDisplay: String {
        isLong ? "LONG" : "SHORT"
    }
    
    var leverageDisplay: String {
        "\(leverage)"
    }
    
    var sizeDisplay: String {
        String(format: "%.4f", size)
    }
}

extension Order {
    var sideDisplay: String {
        side.lowercased() == "buy" ? "LONG" : "SHORT"
    }
    
    var qtyDisplay: String {
        String(format: "%.4f", qty)
    }
}

extension Trade {
    var sideDisplay: String {
        side.lowercased() == "buy" ? "LONG" : "SHORT"
    }
    
    var timeDisplay: String {
        // Format timestamp to readable date
        if timestamp.isEmpty { return "-" }
        // Try to parse ISO8601 date
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: timestamp) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateStyle = .short
            displayFormatter.timeStyle = .short
            return displayFormatter.string(from: date)
        }
        return timestamp
    }
}

// MARK: - Dashboard Models
struct StrategyBreakdownItem: Codable, Identifiable {
    var id: String { strategy }
    let strategy: String
    let trades: Int
    let wins: Int
    let losses: Int
    let pnl: Double
    let winRate: Double
    
    var color: Color {
        switch strategy.lowercased() {
        case "oi": return .orange
        case "scryptomera": return .cyan
        case "scalper": return .purple
        case "elcaro": return .blue
        case "fibonacci": return .green
        case "rsi_bb", "rsi-bb": return .pink
        case "manual": return .gray
        default: return .white
        }
    }
    
    enum CodingKeys: String, CodingKey {
        case strategy, trades, wins, losses, pnl
        case winRate = "win_rate"
    }
}

struct RecentTrade: Codable, Identifiable {
    var id: String { "\(symbol)-\(closedAtString)-\(pnl)" }
    let symbol: String
    let side: String
    let entryPrice: Double
    let exitPrice: Double
    let size: Double
    let pnl: Double
    let pnlPercent: Double
    let closedAtString: String
    let strategy: String?
    let exitReason: String?
    
    var closedAt: Date {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter.date(from: closedAtString) ?? Date()
    }
    
    enum CodingKeys: String, CodingKey {
        case symbol, side, size, pnl, strategy
        case entryPrice = "entry_price"
        case exitPrice = "exit_price"
        case pnlPercent = "pnl_percent"
        case closedAtString = "closed_at"
        case exitReason = "exit_reason"
    }
}

import SwiftUI
