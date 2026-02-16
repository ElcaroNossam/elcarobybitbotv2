//
//  ViewModels.swift
//  EnlikoTrading
//
//  Observable ViewModels for views
//

import SwiftUI
import Combine

// MARK: - Portfolio ViewModel
@MainActor
class PortfolioViewModel: ObservableObject {
    @Published var balance: Balance?
    @Published var stats: TradingStats?
    @Published var recentTrades: [Trade] = []
    @Published var isLoading = false
    @Published var error: String?
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        // Observe TradingService
        TradingService.shared.$balance
            .receive(on: DispatchQueue.main)
            .assign(to: &$balance)
        
        TradingService.shared.$tradingStats
            .receive(on: DispatchQueue.main)
            .assign(to: &$stats)
        
        TradingService.shared.$trades
            .receive(on: DispatchQueue.main)
            .map { Array($0.prefix(5)) }
            .assign(to: &$recentTrades)
    }
    
    func refresh() async {
        isLoading = true
        await TradingService.shared.refreshAll()
        isLoading = false
    }
}

// MARK: - Trading ViewModel
@MainActor
class TradingViewModel: ObservableObject {
    @Published var selectedSymbol = "BTCUSDT"
    @Published var orderSide: OrderSide = .buy
    @Published var orderType: OrderType = .market
    @Published var quantity = ""
    @Published var price = ""
    @Published var leverage = 10
    @Published var takeProfit = ""
    @Published var stopLoss = ""
    
    @Published var isPlacing = false
    @Published var orderResult: OrderResult?
    
    struct OrderResult: Identifiable {
        let id = UUID()
        let success: Bool
        let message: String
    }
    
    var isValid: Bool {
        guard let qty = Double(quantity), qty > 0 else { return false }
        if orderType == .limit {
            guard let p = Double(price), p > 0 else { return false }
        }
        return true
    }
    
    func placeOrder() async {
        guard isValid else { return }
        
        isPlacing = true
        
        let success = await TradingService.shared.placeOrder(
            symbol: selectedSymbol,
            side: orderSide,
            orderType: orderType,
            quantity: Double(quantity) ?? 0,
            price: Double(price),
            leverage: leverage,
            takeProfit: Double(takeProfit),
            stopLoss: Double(stopLoss)
        )
        
        isPlacing = false
        
        orderResult = OrderResult(
            success: success,
            message: success 
                ? "Order placed successfully for \(selectedSymbol)"
                : "Failed to place order. Check balance and try again."
        )
        
        if success {
            resetForm()
        }
    }
    
    func resetForm() {
        quantity = ""
        price = ""
        takeProfit = ""
        stopLoss = ""
    }
}

// MARK: - Positions ViewModel
@MainActor
class PositionsViewModel: ObservableObject {
    @Published var positions: [Position] = []
    @Published var orders: [Order] = []
    @Published var isLoading = false
    @Published var selectedTab = 0
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        TradingService.shared.$positions
            .receive(on: DispatchQueue.main)
            .assign(to: &$positions)
        
        TradingService.shared.$orders
            .receive(on: DispatchQueue.main)
            .assign(to: &$orders)
    }
    
    func refresh() async {
        isLoading = true
        await TradingService.shared.fetchPositions()
        await TradingService.shared.fetchOrders()
        isLoading = false
    }
    
    func closePosition(_ position: Position) async {
        await TradingService.shared.closePosition(symbol: position.symbol, side: position.side)
    }
    
    func cancelOrder(_ order: Order) async {
        await TradingService.shared.cancelOrder(symbol: order.symbol, orderId: order.orderId)
    }
    
    func closeAllPositions() async {
        await TradingService.shared.closeAllPositions()
    }
}

// MARK: - Market ViewModel
@MainActor
class MarketViewModel: ObservableObject {
    @Published var tickers: [MarketTicker] = []
    @Published var searchText = ""
    @Published var sortOption: SortOption = .volume
    @Published var isConnected = false
    
    enum SortOption: String, CaseIterable {
        case volume = "Volume"
        case change = "Change"
        case name = "Name"
    }
    
    private var cancellables = Set<AnyCancellable>()
    
    var filteredTickers: [MarketTicker] {
        var result = tickers
        
        if !searchText.isEmpty {
            result = result.filter { 
                $0.symbol.localizedCaseInsensitiveContains(searchText) 
            }
        }
        
        switch sortOption {
        case .volume:
            result.sort { $0.volume24h > $1.volume24h }
        case .change:
            result.sort { $0.priceChangePercent > $1.priceChangePercent }
        case .name:
            result.sort { $0.symbol < $1.symbol }
        }
        
        return result
    }
    
    init() {
        WebSocketService.shared.$isConnected
            .receive(on: DispatchQueue.main)
            .assign(to: &$isConnected)
    }
    
    func connect() {
        WebSocketService.shared.connect()
    }
    
    func disconnect() {
        WebSocketService.shared.disconnect()
    }
}

// MARK: - Backtest ViewModel
@MainActor
class BacktestViewModel: ObservableObject {
    @Published var selectedStrategy = "OI"
    @Published var selectedSymbol = "BTCUSDT"
    @Published var selectedTimeframe = "1h"
    @Published var days = 30
    @Published var initialBalance = 10000.0
    @Published var riskPerTrade = 1.0
    @Published var slPercent = 30.0
    @Published var tpPercent = 25.0
    @Published var result: BacktestResult?
    @Published var isRunning = false
    @Published var error: String?
    
    let availableStrategies = ["oi", "scryptomera", "scalper", "elcaro", "fibonacci", "rsi_bb"]
    let availableTimeframes = ["5m", "15m", "1h", "4h", "1d"]
    
    func runBacktest() async {
        isRunning = true
        error = nil
        
        result = await StrategyService.shared.runBacktest(
            strategy: selectedStrategy,
            symbol: selectedSymbol,
            timeframe: selectedTimeframe,
            days: days,
            initialBalance: initialBalance,
            riskPerTrade: riskPerTrade,
            slPercent: slPercent,
            tpPercent: tpPercent
        )
        
        if result == nil {
            error = "Backtest failed. Please try again."
        }
        
        isRunning = false
    }
}

// MARK: - Settings ViewModel
@MainActor
class SettingsViewModel: ObservableObject {
    @Published var defaultExchange: Exchange = .bybit
    @Published var defaultLeverage = 10
    @Published var defaultTP = 8.0
    @Published var defaultSL = 3.0
    @Published var maxPositions = 5
    @Published var tradeNotifications = true
    @Published var signalNotifications = true
    
    @Published var isSaving = false
    @Published var saveSuccess = false
    
    init() {
        loadSettings()
    }
    
    func loadSettings() {
        // Load from UserDefaults or API
        defaultExchange = AppState.shared.selectedExchange
        defaultLeverage = UserDefaults.standard.integer(forKey: "defaultLeverage")
        if defaultLeverage == 0 { defaultLeverage = 10 }
        defaultTP = UserDefaults.standard.double(forKey: "defaultTP")
        if defaultTP == 0 { defaultTP = 8.0 }
        defaultSL = UserDefaults.standard.double(forKey: "defaultSL")
        if defaultSL == 0 { defaultSL = 3.0 }
    }
    
    func saveSettings() async {
        isSaving = true
        
        // Save to UserDefaults
        UserDefaults.standard.set(defaultLeverage, forKey: "defaultLeverage")
        UserDefaults.standard.set(defaultTP, forKey: "defaultTP")
        UserDefaults.standard.set(defaultSL, forKey: "defaultSL")
        UserDefaults.standard.set(maxPositions, forKey: "maxPositions")
        
        // Update AppState
        AppState.shared.selectedExchange = defaultExchange
        
        // Simulate API call
        try? await Task.sleep(nanoseconds: 500_000_000)
        
        isSaving = false
        saveSuccess = true
        
        // Reset success after delay
        try? await Task.sleep(nanoseconds: 2_000_000_000)
        saveSuccess = false
    }
}

// MARK: - API Keys ViewModel
@MainActor
class APIKeysViewModel: ObservableObject {
    @Published var bybitDemoKey = ""
    @Published var bybitDemoSecret = ""
    @Published var bybitRealKey = ""
    @Published var bybitRealSecret = ""
    @Published var hlTestnetKey = ""
    @Published var hlMainnetKey = ""
    
    @Published var isSaving = false
    @Published var saveResult: SaveResult?
    
    struct SaveResult: Identifiable {
        let id = UUID()
        let success: Bool
        let message: String
    }
    
    // Request bodies
    struct BybitKeysRequest: Encodable {
        let api_key: String
        let api_secret: String
    }
    
    struct HLKeyRequest: Encodable {
        let private_key: String
        let testnet: Bool
    }
    
    func saveBybitKeys(demo: Bool) async {
        isSaving = true
        
        let key = demo ? bybitDemoKey : bybitRealKey
        let secret = demo ? bybitDemoSecret : bybitRealSecret
        
        // Call API to save keys
        do {
            let endpoint = demo ? "/api/v1/api-keys/bybit/demo" : "/api/v1/api-keys/bybit/real"
            let body = BybitKeysRequest(api_key: key, api_secret: secret)
            
            let _: EmptyResponse = try await NetworkService.shared.post(endpoint, body: body)
            
            saveResult = SaveResult(success: true, message: "API keys saved successfully")
        } catch {
            saveResult = SaveResult(success: false, message: "Failed to save API keys")
        }
        
        isSaving = false
    }
    
    func saveHLKey(testnet: Bool) async {
        isSaving = true
        
        let key = testnet ? hlTestnetKey : hlMainnetKey
        
        do {
            let endpoint = "/api/v1/api-keys/hyperliquid"
            let body = HLKeyRequest(private_key: key, testnet: testnet)
            
            let _: EmptyResponse = try await NetworkService.shared.post(endpoint, body: body)
            
            saveResult = SaveResult(success: true, message: "HyperLiquid key saved successfully")
        } catch {
            saveResult = SaveResult(success: false, message: "Failed to save HyperLiquid key")
        }
        
        isSaving = false
    }
}

// EmptyResponse is defined in AppState.swift
