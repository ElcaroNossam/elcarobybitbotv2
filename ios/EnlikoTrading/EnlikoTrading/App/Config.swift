//
//  Config.swift
//  EnlikoTrading
//

import Foundation

struct Config {
    // App Name - configurable for rebranding
    // Change this value to rebrand the entire app
    static let appName = ProcessInfo.processInfo.environment["APP_NAME"] ?? "Enliko"
    static let appDisplayName = "\(appName) Trading"
    static let bundleId = "io.\(appName.lowercased()).trading"
    
    // API Configuration
    // DEBUG: Use production URL for real device testing
    // RELEASE: Production domain with nginx + SSL
    #if DEBUG
    // For simulator use localhost, for real device use production URL
    static let baseURL = "https://enliko.com"
    #else
    static let baseURL = "https://enliko.com"
    #endif
    
    static let apiURL = "\(baseURL)/api"
    static let wsURL = baseURL
        .replacingOccurrences(of: "https://", with: "wss://")
        .replacingOccurrences(of: "http://", with: "ws://")
    
    // API Endpoints
    struct Endpoints {
        // Auth
        static let login = "/auth/telegram"
        static let loginEmail = "/auth/email/login"
        static let register = "/auth/email/register"
        static let verify = "/auth/email/verify"
        static let refresh = "/auth/refresh"
        
        // Users
        static let me = "/users/me"
        static let settings = "/users/settings"
        static let profile = "/users/profile"
        static let apiKeys = "/users/api-keys"
        static let strategySettings = "/users/strategy-settings"
        static let strategySettingsMobile = "/users/strategy-settings/mobile"
        static let switchExchange = "/users/exchange"
        static let switchAccountType = "/users/switch-account-type"
        
        // Trading
        static let balance = "/trading/balance"
        static let balanceSpot = "/trading/balance/spot"  // HyperLiquid Spot balance
        static let positions = "/trading/positions"
        static let orders = "/trading/orders"
        static let symbols = "/trading/symbols"
        static let placeOrder = "/trading/order"
        static let closePosition = "/trading/close"
        static let closeAll = "/trading/close-all"
        static let cancelOrder = "/trading/cancel"
        static let cancelAllOrders = "/trading/cancel-all-orders"
        static let modifyTPSL = "/trading/modify-tpsl"
        static let setLeverage = "/trading/leverage"
        static let trades = "/trading/trades"
        static let stats = "/trading/stats"
        static let executionHistory = "/trading/execution-history"
        static let orderbook = "/trading/orderbook"
        static let recentTrades = "/trading/recent-trades"
        static let symbolInfo = "/trading/symbol-info"
        static let calculatePosition = "/trading/calculate-position"
        static let dcaLadder = "/trading/dca-ladder"
        static let accountInfo = "/trading/account-info"
        
        // Spot Trading
        static let spotBalance = "/spot/balance"
        static let spotHoldings = "/spot/holdings"
        static let spotTicker = "/spot/ticker"  // /{symbol}
        static let spotBuy = "/spot/buy"
        static let spotSell = "/spot/sell"
        static let spotHistory = "/spot/history"
        static let spotSettings = "/spot/settings"
        static let spotSymbols = "/spot/symbols"
        
        // Backtest
        static let backtestRun = "/backtest/run"
        static let backtestResults = "/backtest/results"
        static let backtestStrategies = "/backtest/strategies"
        
        // Marketplace (server router mounted at /api/marketplace)
        static let strategies = "/marketplace/marketplace"           // GET all listed strategies
        static let myStrategies = "/marketplace/strategies/my"       // GET user's own strategies
        static let purchasedStrategies = "/marketplace/marketplace/purchased"  // GET purchased strategies
        static let createStrategy = "/marketplace/strategies/create" // POST create new strategy
        static let listStrategy = "/marketplace/marketplace/list"    // POST list strategy for sale
        static let purchaseStrategy = "/marketplace/marketplace/purchase" // POST purchase strategy
        static let rateStrategy = "/marketplace/marketplace/rate"    // POST rate a strategy
        static let indicators = "/marketplace/indicators"            // GET available indicators
        
        // Stats & Analytics
        static let dailyStats = "/stats/daily"
        static let performanceChart = "/stats/performance"
        static let strategyStats = "/stats/strategy"
        static let dashboard = "/stats/dashboard"
        static let pnlHistory = "/stats/pnl-history"
        static let strategyReport = "/stats/strategy-report"
        static let positionsSummary = "/stats/positions-summary"
        
        // Screener (note: screener endpoints have /api prefix built-in)
        static let screenerSymbols = "/screener/symbols"
        static let screenerOverview = "/screener/overview"
        static let screenerSymbol = "/screener/symbol"  // /{symbol}
        static let wsScreener = "/ws/screener"
        
        // AI Agent
        static let aiAnalyze = "/ai/analyze"
        static let aiChat = "/ai/chat"
        static let aiMarketSentiment = "/ai/market-sentiment"
        
        // Activity Sync
        static let activityHistory = "/activity/history"
        static let activityRecent = "/activity/recent"
        static let activityStats = "/activity/stats"
        static let activityTriggerSync = "/activity/trigger-sync"
        
        // Signals
        static let signals = "/signals"
        static let signalsActive = "/signals/active"
        
        // ENLIKO Token
        static let elcBalance = "/elcaro/balance"
        static let elcTransactions = "/elcaro/transactions"
        static let elcPurchase = "/elcaro/purchase"
        
        // WebSocket
        static let wsMarket = "/ws/market"
        static let wsTrades = "/ws/trades"
        static let wsSettingsSync = "/ws/settings-sync"  // Requires auth: /ws/settings-sync/{user_id}?token=...
    }
    
    // App Settings
    static let tokenKey = "auth_token"
    static let refreshTokenKey = "refresh_token"
    static let userIdKey = "user_id"
    
    // Timeouts
    static let requestTimeout: TimeInterval = 30
    static let wsReconnectDelay: TimeInterval = 5
    
    // Pagination
    static let defaultPageSize = 50
    static let maxPageSize = 100
}
