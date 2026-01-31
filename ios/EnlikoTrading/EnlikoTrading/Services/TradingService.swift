//
//  TradingService.swift
//  EnlikoTrading
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
    @Published var symbols: [SymbolInfo] = []
    
    // Convenience accessor for symbol names (for backwards compatibility)
    var symbolNames: [String] { symbols.map { $0.symbol } }
    
    @Published var isLoadingBalance = false
    @Published var isLoadingPositions = false
    @Published var isLoadingOrders = false
    @Published var lastError: String?
    
    private let network = NetworkService.shared
    private let appState = AppState.shared
    private let logger = AppLogger.shared
    
    private init() {
        logger.info("TradingService initialized", category: .trading)
    }
    
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
        lastError = nil
        defer { isLoadingBalance = false }
        
        logger.debug("Fetching balance for \(appState.currentExchange.rawValue)/\(appState.currentAccountType.rawValue)", category: .trading)
        
        do {
            // Try direct Balance decode first (backend returns data directly)
            let balance: Balance = try await network.get(
                Config.Endpoints.balance,
                params: exchangeParams
            )
            self.balance = balance
            logger.logBalanceUpdate(equity: balance.totalEquity, available: balance.available)
        } catch {
            // Fallback to wrapped response
            do {
                let response: BalanceResponse = try await network.get(
                    Config.Endpoints.balance,
                    params: exchangeParams
                )
                if let balance = response.balanceData {
                    self.balance = balance
                    logger.logBalanceUpdate(equity: balance.totalEquity, available: balance.available)
                }
            } catch {
                logger.error("Failed to fetch balance: \(error)", category: .trading)
                lastError = error.localizedDescription
            }
        }
    }
    
    // MARK: - Positions
    @MainActor
    func fetchPositions() async {
        isLoadingPositions = true
        lastError = nil
        defer { isLoadingPositions = false }
        
        logger.debug("Fetching positions for \(appState.currentExchange.rawValue)/\(appState.currentAccountType.rawValue)", category: .trading)
        
        do {
            // First try array (most common response format)
            let positions: [Position] = try await network.get(
                Config.Endpoints.positions,
                params: exchangeParams
            )
            self.positions = positions
            logger.info("Fetched \(positions.count) positions", category: .trading)
        } catch {
            // Fallback: API may return wrapped response
            do {
                let response: PositionsResponse = try await network.get(
                    Config.Endpoints.positions,
                    params: exchangeParams
                )
                self.positions = response.positionsData
                logger.info("Fetched \(self.positions.count) positions (wrapped)", category: .trading)
            } catch {
                logger.error("Failed to fetch positions: \(error)", category: .trading)
                lastError = error.localizedDescription
            }
        }
    }
    
    // MARK: - Orders
    @MainActor
    func fetchOrders() async {
        isLoadingOrders = true
        lastError = nil
        defer { isLoadingOrders = false }
        
        logger.debug("Fetching orders for \(appState.currentExchange.rawValue)/\(appState.currentAccountType.rawValue)", category: .trading)
        
        do {
            // First try array (most common response format)
            let orders: [Order] = try await network.get(
                Config.Endpoints.orders,
                params: exchangeParams
            )
            self.orders = orders
            logger.info("Fetched \(orders.count) orders", category: .trading)
        } catch {
            // Fallback: API may return wrapped response
            do {
                let response: OrdersResponse = try await network.get(
                    Config.Endpoints.orders,
                    params: exchangeParams
                )
                self.orders = response.ordersData
                logger.info("Fetched \(self.orders.count) orders (wrapped)", category: .trading)
            } catch {
                logger.error("Failed to fetch orders: \(error)", category: .trading)
                lastError = error.localizedDescription
            }
        }
    }
    
    // MARK: - Symbols
    @MainActor
    func fetchSymbols() async {
        logger.debug("Fetching symbols for \(appState.currentExchange.rawValue)", category: .trading)
        
        do {
            let response: SymbolsResponse = try await network.get(
                Config.Endpoints.symbols,
                params: ["exchange": appState.currentExchange.rawValue]
            )
            self.symbols = response.symbolsData
            logger.info("Fetched \(self.symbols.count) symbols", category: .trading)
        } catch {
            // Fallback: API may return array directly
            do {
                let symbols: [SymbolInfo] = try await network.get(
                    Config.Endpoints.symbols,
                    params: ["exchange": appState.currentExchange.rawValue]
                )
                self.symbols = symbols
                logger.info("Fetched \(symbols.count) symbols (direct array)", category: .trading)
            } catch {
                logger.error("Failed to fetch symbols: \(error)", category: .trading)
            }
        }
    }
    
    // MARK: - Stats
    @MainActor
    func fetchStats() async {
        let params = exchangeParams
        logger.debug("Fetching stats with params: \(params)", category: .trading)
        
        do {
            // Try direct TradingStats decode first
            let stats: TradingStats = try await network.get(
                Config.Endpoints.stats,
                params: params
            )
            self.tradingStats = stats
            logger.info("Fetched stats: total=\(stats.totalTradesCount), totalTrades=\(stats.totalTrades ?? -1), win_rate=\(String(format: "%.1f", stats.winRateValue))%", category: .trading)
        } catch {
            logger.warning("Direct stats decode failed: \(error), trying wrapped response", category: .trading)
            // Fallback to wrapped response
            do {
                let response: StatsResponse = try await network.get(
                    Config.Endpoints.stats,
                    params: params
                )
                if let stats = response.statsData {
                    self.tradingStats = stats
                    logger.info("Fetched stats via wrapper: total=\(stats.totalTradesCount) trades", category: .trading)
                } else {
                    logger.error("Stats response has no data: success=\(response.success ?? false), error=\(response.error ?? "nil")", category: .trading)
                }
            } catch {
                logger.error("Failed to fetch stats: \(error)", category: .trading)
            }
        }
    }
    
    // MARK: - Trades History
    @MainActor
    func fetchTrades(limit: Int = 50) async {
        logger.debug("Fetching trades (limit: \(limit))", category: .trading)
        
        do {
            var params = exchangeParams
            params["limit"] = String(limit)
            
            let response: TradesResponse = try await network.get(
                Config.Endpoints.trades,
                params: params
            )
            self.trades = response.tradesData
            logger.info("Fetched \(self.trades.count) trades", category: .trading)
        } catch {
            // Fallback: API may return array directly
            do {
                var params = exchangeParams
                params["limit"] = String(limit)
                let trades: [Trade] = try await network.get(
                    Config.Endpoints.trades,
                    params: params
                )
                self.trades = trades
                logger.info("Fetched \(trades.count) trades (direct array)", category: .trading)
            } catch {
                logger.error("Failed to fetch trades: \(error)", category: .trading)
            }
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
        
        logger.logOrderPlaced(symbol: symbol, side: side.rawValue, type: orderType.rawValue, qty: quantity, price: price)
        
        do {
            let params = exchangeParams
            let response: PlaceOrderResponse = try await network.post(
                Config.Endpoints.placeOrder + "?\(params.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))",
                body: request
            )
            
            if response.success {
                logger.info("Order placed successfully: \(symbol) \(side.rawValue)", category: .trading)
                // Refresh positions and orders
                await fetchPositions()
                await fetchOrders()
                await fetchBalance()
                return true
            }
            
            logger.warning("Order placement returned success=false", category: .trading)
            return false
        } catch {
            logger.error("Failed to place order: \(error)", category: .trading)
            lastError = error.localizedDescription
            return false
        }
    }
    
    // MARK: - Close Position
    @MainActor
    func closePosition(symbol: String, side: String? = nil) async {
        let request = ClosePositionRequest(symbol: symbol, side: side, qty: nil)
        
        logger.info("Closing position: \(symbol) \(side ?? "all")", category: .trading)
        
        do {
            let params = exchangeParams
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.closePosition + "?\(params.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))",
                body: request
            )
            
            if response.success == true {
                logger.logPositionClosed(symbol: symbol, side: side ?? "unknown", pnl: nil)
                await fetchPositions()
                await fetchBalance()
            }
        } catch {
            logger.error("Failed to close position: \(error)", category: .trading)
            lastError = error.localizedDescription
        }
    }
    
    // MARK: - Close All Positions
    @MainActor
    func closeAllPositions() async {
        logger.info("Closing all positions", category: .trading)
        
        do {
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.closeAll + "?\(exchangeParams.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))"
            )
            
            if response.success == true {
                logger.info("All positions closed", category: .trading)
                await fetchPositions()
                await fetchBalance()
            }
        } catch {
            logger.error("Failed to close all positions: \(error)", category: .trading)
            lastError = error.localizedDescription
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
        
        logger.info("Modifying TP/SL for \(symbol): TP=\(takeProfit ?? 0), SL=\(stopLoss ?? 0)", category: .trading)
        
        do {
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.modifyTPSL + "?\(exchangeParams.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))",
                body: request
            )
            
            if response.success == true {
                logger.info("TP/SL modified successfully", category: .trading)
                await fetchPositions()
            }
        } catch {
            logger.error("Failed to modify TP/SL: \(error)", category: .trading)
            lastError = error.localizedDescription
        }
    }
    
    // MARK: - Cancel Order
    @MainActor
    func cancelOrder(symbol: String, orderId: String) async {
        logger.info("Cancelling order \(orderId) for \(symbol)", category: .trading)
        
        do {
            var params = exchangeParams
            params["order_id"] = orderId
            params["symbol"] = symbol
            
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.cancelOrder + "?\(params.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))"
            )
            
            if response.success == true {
                logger.info("Order cancelled: \(orderId)", category: .trading)
                await fetchOrders()
            }
        } catch {
            logger.error("Failed to cancel order: \(error)", category: .trading)
            lastError = error.localizedDescription
        }
    }
    
    // MARK: - Cancel All Orders
    @MainActor
    func cancelAllOrders() async {
        logger.info("Cancelling all orders", category: .trading)
        
        do {
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.cancelAllOrders + "?\(exchangeParams.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))"
            )
            
            if response.success == true {
                logger.info("All orders cancelled", category: .trading)
                await fetchOrders()
            }
        } catch {
            logger.error("Failed to cancel all orders: \(error)", category: .trading)
            lastError = error.localizedDescription
        }
    }
    
    // MARK: - Set Leverage
    @MainActor
    func setLeverage(symbol: String, leverage: Int) async -> Bool {
        logger.info("Setting leverage for \(symbol) to \(leverage)x", category: .trading)
        
        do {
            var params = exchangeParams
            params["symbol"] = symbol
            params["leverage"] = String(leverage)
            
            let response: SimpleResponse = try await network.post(
                Config.Endpoints.setLeverage + "?\(params.map { "\($0.key)=\($0.value)" }.joined(separator: "&"))"
            )
            
            let success = response.success == true
            if success {
                logger.info("Leverage set successfully", category: .trading)
            } else {
                logger.warning("Set leverage returned success=false", category: .trading)
            }
            return success
        } catch {
            logger.error("Failed to set leverage: \(error)", category: .trading)
            lastError = error.localizedDescription
            return false
        }
    }
    
    // MARK: - Refresh All
    @MainActor
    func refreshAll() async {
        logger.info("Refreshing all trading data", category: .trading)
        let startTime = Date()
        
        async let balance: () = fetchBalance()
        async let positions: () = fetchPositions()
        async let orders: () = fetchOrders()
        async let stats: () = fetchStats()
        async let trades: () = fetchTrades()
        
        _ = await (balance, positions, orders, stats, trades)
        
        let duration = Date().timeIntervalSince(startTime)
        logger.info("Refresh completed in \(String(format: "%.2f", duration))s", category: .trading)
    }
}
