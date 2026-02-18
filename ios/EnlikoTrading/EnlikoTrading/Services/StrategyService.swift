//
//  StrategyService.swift
//  EnlikoTrading
//
//  Strategy and Backtest service
//

import Foundation
import Combine

@MainActor
class StrategyService: ObservableObject {
    static let shared = StrategyService()
    
    @Published var strategies: [Strategy] = []
    @Published var myStrategies: [Strategy] = []
    @Published var purchasedStrategies: [Strategy] = []
    @Published var strategySettings: [StrategySettings] = []
    @Published var backtestResults: [BacktestResult] = []
    @Published var marketplaceStrategies: [MarketplaceStrategy] = []
    
    @Published var isLoading = false
    
    private let network = NetworkService.shared
    
    // Built-in strategy names
    let availableStrategies = ["oi", "scryptomera", "scalper", "elcaro", "fibonacci", "rsi_bb", "manual"]
    
    // Last backtest result for quick access
    var backtestResult: BacktestResult? {
        backtestResults.first
    }
    
    private init() {}
    
    // MARK: - Fetch Marketplace Strategies
    @MainActor
    func fetchMarketplaceStrategies() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response: APIResponse<[MarketplaceStrategy]> = try await network.get(Config.Endpoints.strategies)
            if let strategies = response.data {
                self.marketplaceStrategies = strategies
            }
        } catch {
            print("Failed to fetch marketplace strategies: \(error)")
        }
    }
    
    // MARK: - Fetch My Strategies
    @MainActor
    func fetchMyStrategies() async {
        do {
            let response: APIResponse<[Strategy]> = try await network.get(Config.Endpoints.myStrategies)
            if let strategies = response.data {
                self.myStrategies = strategies
            }
        } catch {
            print("Failed to fetch my strategies: \(error)")
        }
    }
    
    // MARK: - Fetch Purchased Strategies
    @MainActor
    func fetchPurchasedStrategies() async {
        do {
            let response: APIResponse<[Strategy]> = try await network.get(Config.Endpoints.purchasedStrategies)
            if let strategies = response.data {
                self.purchasedStrategies = strategies
            }
        } catch {
            print("Failed to fetch purchased strategies: \(error)")
        }
    }
    
    // MARK: - Fetch Strategy Settings (Mobile API)
    @MainActor
    func fetchStrategySettings(strategy: String? = nil, exchange: String = "bybit", accountType: String = "demo") async {
        do {
            var params: [String: String] = [
                "exchange": exchange,
                "account_type": accountType
            ]
            if let strategy = strategy {
                params["strategy"] = strategy
            }
            
            let response: APIResponse<[StrategySettings]> = try await network.get(
                Config.Endpoints.strategySettingsMobile,
                params: params
            )
            if let settings = response.data {
                self.strategySettings = settings
            }
        } catch {
            print("Failed to fetch strategy settings: \(error)")
        }
    }
    
    // MARK: - Update Strategy Settings (Mobile API)
    @MainActor
    func updateStrategySettings(
        strategy: String,
        request: StrategySettingsUpdateRequest
    ) async -> Bool {
        do {
            let _: APIResponse<EmptyResponse> = try await network.put(
                "\(Config.Endpoints.strategySettingsMobile)/\(strategy)",
                body: request
            )
            
            // Refresh settings after update
            await fetchStrategySettings(strategy: strategy, exchange: request.exchange, accountType: request.accountType)
            return true
        } catch {
            print("Failed to update strategy settings: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Run Backtest
    @MainActor
    func runBacktest(
        strategy: String,
        symbol: String,
        timeframe: String,
        days: Int,
        initialBalance: Double,
        riskPerTrade: Double,
        slPercent: Double,
        tpPercent: Double
    ) async -> BacktestResult? {
        isLoading = true
        defer { isLoading = false }
        
        let request = BacktestRequest(
            strategy: strategy,
            symbol: symbol,
            timeframe: timeframe,
            days: days,
            initialBalance: initialBalance,
            riskPerTrade: riskPerTrade,
            stopLossPercent: slPercent,
            takeProfitPercent: tpPercent
        )
        
        do {
            let response: APIResponse<BacktestResult> = try await network.post(
                Config.Endpoints.backtestRun,
                body: request
            )
            
            if let result = response.data {
                backtestResults.insert(result, at: 0)
                return result
            }
        } catch {
            print("Failed to run backtest: \(error)")
            AppState.shared.showError(error.localizedDescription)
        }
        
        return nil
    }
    
    // MARK: - Available Strategies
    static let availableStrategies = [
        "oi": "Open Interest",
        "scryptomera": "Scryptomera",
        "scalper": "Scalper",
        "elcaro": "ENLIKO AI",
        "fibonacci": "Fibonacci",
        "rsi_bb": "RSI + Bollinger",
        "manual": "Manual Trading"
    ]
    
    static let timeframes = [
        "1m": "1 Minute",
        "5m": "5 Minutes",
        "15m": "15 Minutes",
        "30m": "30 Minutes",
        "1h": "1 Hour",
        "4h": "4 Hours",
        "1d": "1 Day"
    ]
}
