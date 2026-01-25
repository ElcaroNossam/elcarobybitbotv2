//
//  Config.swift
//  LyxenTrading
//

import Foundation

struct Config {
    // API Configuration
    // DEBUG: localhost for iOS Simulator
    // RELEASE: Production Cloudflare URL
    #if DEBUG
    static let baseURL = "http://localhost:8765"
    #else
    static let baseURL = "https://racks-exterior-traveling-acid.trycloudflare.com"
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
        
        // Backtest
        static let backtestRun = "/backtest/run"
        static let backtestResults = "/backtest/results"
        static let backtestStrategies = "/backtest/strategies"
        
        // Marketplace
        static let strategies = "/marketplace/strategies"
        static let myStrategies = "/marketplace/my-strategies"
        static let purchasedStrategies = "/marketplace/purchased"
        
        // Stats
        static let dailyStats = "/stats/daily"
        static let performanceChart = "/stats/performance"
        static let strategyStats = "/stats/strategy"
        
        // LYXEN Token
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
