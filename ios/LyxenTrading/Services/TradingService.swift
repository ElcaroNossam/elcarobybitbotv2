//
//  TradingService.swift
//  LyxenTrading
//
//  Trading operations service
//

import Foundation
import Combine

class TradingService: ObservableObject {
    static let shared = TradingService()
    
    @Published var balance: Balance?
    @Published var positions: [Position] = []
    @Published var orders: [Order] = []
    @Published var trades: [Trade] = []
    @Published var tradingStats: TradingStats?
    @Published var symbols: [String] = []
    
    @Published var isLoadingBalance = false
    @Published var isLoadingPositions = false
    @Published var isLoadingOrders = false
    
    private let network = NetworkService.shared
    private let appState = AppState.shared
    
    private init() {}
    
    // MARK: - Query Parameters
    private var exchangeParams: [String: String] {
        [
            "exchange": appState.currentExchange.rawValue,
            "account_type": appState.currentAccountType.rawValue
        ]
    }
    
    // MARK: - Balance
    @MainActor
    func fetchBalance() async {
        isLoadingBalance = true
        defer { isLoadingBalance = false }
        
        do {
            // Try direct Balance decode first (backend returns data directly)
            let balance: Balance = try await network.get(
                Config.Endpoints.balance,
                params: exchangeParams
            )
            self.balance = balance
        } catch {
            // Fallback to wrapped response
            do {
                let response: BalanceResponse = try await network.get(
                    Config.Endpoints.balance,
                    params: exchangeParams
                )
                if let balance = response.balanceData {
                    self.balance = balance
                }
            } catch {
                print("Failed to fetch balance: \(error)")
            }
        }
    }
    
    // MARK: - Positions
    @MainActor
    func fetchPositions() async {
        isLoadingPositions = true
        defer { isLoadingPositions = false }
        
        do {
            let response: PositionsResponse = try await network.get(
                Config.Endpoints.positions,
                params: exchangeParams
            )
            
            if let positions = response.positions {
                self.positions = positions
            }
        } catch {
            print("Failed to fetch positions: \(error)")
            appState.showError(error.localizedDescription)
        }
    }
    
    // MARK: - Orders
    @MainActor
    func fetchOrders() async {
        isLoadingOrders = true
        defer { isLoadingOrders = false }
        
        do {
            let response: OrdersResponse = try await network.get(
                Config.Endpoints.orders,
                params: exchangeParams
            )
            
            if let orders = response.orders {
                self.orders = orders
            }
        } catch {
            print("Failed to fetch orders: \(error)")
            appState.showError(error.localizedDescription)
        }
    }
    
    // MARK: - Symbols
    @MainActor
    func fetchSymbols() async {
        do {
            let response: SymbolsResponse = try await network.get(
                Config.Endpoints.symbols,
                params: ["exchange": appState.currentExchange.rawValue]
            )
            
            if let symbols = response.symbols {
                self.symbols = symbols
            }
        } catch {
            print("Failed to fetch symbols: \(error)")
        }
    }
    
    // MARK: - Stats
    @MainActor
    func fetchStats() async {
        do {
            // Try direct TradingStats decode first
            let stats: TradingStats = try await network.get(
                Config.Endpoints.stats,
                params: exchangeParams
            )
            self.tradingStats = stats
        } catch {
            // Fallback to wrapped response
            do {
                let response: StatsResponse = try await network.get(
                    Config.Endpoints.stats,
                    params: exchangeParams
                )
                if let stats = response.statsData {
                    self.tradingStats = stats
                }
            } catch {
                print("Failed to fetch stats: \(error)")
            }
        }
    }
    
    // MARK: - Trades History
    @MainActor
    func fetchTrades(limit: Int = 50) async {
        do {
            var params = exchangeParams
            params["limit"] = String(limit)
            
            let response: TradesResponse = try await network.get(
                Config.Endpoints.trades,
                params: params
            )
            
            if let trades = response.trades {
                self.trades = trades
            }
        } catch {
            print("Failed to fetch trades: \(error)")
        }
    }
    
    // MARK: - Place Order
    @MainActor
    func placeOrder(
        symbol: String,
        side: OrderSide,
        orderType: OrderType,
        quantity: Double,
        price: Double? = nil,
        leverage: Int = 10,
        takeProfit: Double? = nil,
        stopLoss: Double? = nil
    ) async -> Bool {
        let request = PlaceOrderRequest(
            symbol: symbol,
            side: side.rawValue,
            orderType: orderType.rawValue,
            qty: quantity,
            price: orderType == .limit ? price : nil,
            takeProfit: takeProfit,
            stopLoss: stopLoss,
            leverage: leverage,
            reduceOnly: false
        )
        
        do {
            let params = exchangeParams
            let response: PlaceOrderResponse = try await network.post(
                Config.Endpoints.placeOrder + "?\(params.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))",
                body: request
            )
            
            if response.success {
                // Refresh positions and orders
                await fetchPositions()
                await fetchOrders()
                await fetchBalance()
                return true
            }
            
            return false
        } catch {
            print("Failed to place order: \(error)")
            return false
        }
    }
    
    // MARK: - Close Position
    @MainActor
    func closePosition(symbol: String, side: String? = nil) async {
        let request = ClosePositionRequest(symbol: symbol, side: side, qty: nil)
        
        do {
            let params = exchangeParams
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.closePosition + "?\(params.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))",
                body: request
            )
            
            if response.success == true {
                await fetchPositions()
                await fetchBalance()
            }
        } catch {
            print("Failed to close position: \(error)")
        }
    }
    
    // MARK: - Close All Positions
    @MainActor
    func closeAllPositions() async {
        do {
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.closeAll + "?\(exchangeParams.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))"
            )
            
            if response.success == true {
                await fetchPositions()
                await fetchBalance()
            }
        } catch {
            print("Failed to close all positions: \(error)")
        }
    }
    
    // MARK: - Modify TP/SL
    @MainActor
    func modifyTPSL(
        symbol: String,
        side: String,
        takeProfit: Double?,
        stopLoss: Double?
    ) async {
        let request = ModifyTPSLRequest(
            symbol: symbol,
            side: side,
            takeProfit: takeProfit,
            stopLoss: stopLoss
        )
        
        do {
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.modifyTPSL + "?\(exchangeParams.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))",
                body: request
            )
            
            if response.success == true {
                await fetchPositions()
            }
        } catch {
            print("Failed to modify TP/SL: \(error)")
        }
    }
    
    // MARK: - Cancel Order
    @MainActor
    func cancelOrder(symbol: String, orderId: String) async {
        do {
            var params = exchangeParams
            params["order_id"] = orderId
            params["symbol"] = symbol
            
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.cancelOrder + "?\(params.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))"
            )
            
            if response.success == true {
                await fetchOrders()
            }
        } catch {
            print("Failed to cancel order: \(error)")
        }
    }
    
    // MARK: - Cancel All Orders
    @MainActor
    func cancelAllOrders() async {
        do {
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.cancelAllOrders + "?\(exchangeParams.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))"
            )
            
            if response.success == true {
                await fetchOrders()
            }
        } catch {
            print("Failed to cancel all orders: \(error)")
        }
    }
    
    // MARK: - Set Leverage
    @MainActor
    func setLeverage(symbol: String, leverage: Int) async -> Bool {
        do {
            var params = exchangeParams
            params["symbol"] = symbol
            params["leverage"] = String(leverage)
            
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.setLeverage + "?\(params.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))"
            )
            
            return response.success == true
        } catch {
            print("Failed to set leverage: \(error)")
            return false
        }
    }
    
    // MARK: - Refresh All
    @MainActor
    func refreshAll() async {
        async let balance: () = fetchBalance()
        async let positions: () = fetchPositions()
        async let orders: () = fetchOrders()
        async let stats: () = fetchStats()
        async let trades: () = fetchTrades()
        
        _ = await (balance, positions, orders, stats, trades)
    }
}
