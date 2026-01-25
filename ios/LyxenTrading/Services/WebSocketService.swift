//
//  WebSocketService.swift
//  LyxenTrading
//
//  Real-time market data via WebSocket
//

import Foundation
import Combine

// MARK: - WebSocket Message Types
struct WSTickerMessage: Codable, Identifiable {
    var id: String { symbol }
    
    let type: String
    let symbol: String
    let price: Double
    let change24h: Double
    let volume24h: Double
    let high24h: Double
    let low24h: Double
    
    // Compatibility with MarketView
    var priceChangePercent: Double { change24h }
    
    enum CodingKeys: String, CodingKey {
        case type
        case symbol
        case price
        case change24h = "change_24h"
        case volume24h = "volume_24h"
        case high24h = "high_24h"
        case low24h = "low_24h"
    }
}

struct WSTradeMessage: Codable {
    let type: String
    let symbol: String
    let side: String
    let price: Double
    let qty: Double
    let timestamp: String
}

struct WSOrderBookMessage: Codable {
    let type: String
    let symbol: String
    let bids: [[Double]]
    let asks: [[Double]]
}

// MARK: - Settings Sync Messages (NEW)
struct WSSyncMessage: Codable {
    let type: String  // "settings_changed", "exchange_switched", "account_switched", "sync_request"
    let source: String  // "webapp", "telegram", "ios"
    let action: String?
    let data: WSSyncData?
    
    enum CodingKeys: String, CodingKey {
        case type
        case source
        case action
        case data
    }
}

struct WSSyncData: Codable {
    let exchange: String?
    let accountType: String?
    let strategy: String?
    let setting: String?
    let oldValue: String?
    let newValue: String?
    let timestamp: String?
    
    enum CodingKeys: String, CodingKey {
        case exchange
        case accountType = "account_type"
        case strategy
        case setting
        case oldValue = "old_value"
        case newValue = "new_value"
        case timestamp
    }
}

// MARK: - WebSocket Service
class WebSocketService: NSObject, ObservableObject {
    static let shared = WebSocketService()
    
    @Published var isConnected = false
    @Published var isSyncConnected = false
    @Published var lastTicker: WSTickerMessage?
    @Published var tickers: [String: WSTickerMessage] = [:]
    
    // Market data WebSocket
    private var webSocket: URLSessionWebSocketTask?
    // Settings sync WebSocket (requires auth)
    private var syncWebSocket: URLSessionWebSocketTask?
    
    private var session: URLSession!
    private var reconnectTimer: Timer?
    private var syncReconnectTimer: Timer?
    private var subscribedSymbols: Set<String> = []
    
    private let tickerSubject = PassthroughSubject<WSTickerMessage, Never>()
    private let tradeSubject = PassthroughSubject<WSTradeMessage, Never>()
    private let syncSubject = PassthroughSubject<WSSyncMessage, Never>()
    
    var tickerPublisher: AnyPublisher<WSTickerMessage, Never> {
        tickerSubject.eraseToAnyPublisher()
    }
    
    var tradePublisher: AnyPublisher<WSTradeMessage, Never> {
        tradeSubject.eraseToAnyPublisher()
    }
    
    var syncPublisher: AnyPublisher<WSSyncMessage, Never> {
        syncSubject.eraseToAnyPublisher()
    }
    
    private override init() {
        super.init()
        session = URLSession(configuration: .default, delegate: self, delegateQueue: nil)
    }
    
    // MARK: - Market Data Connection
    func connect() {
        guard webSocket == nil else { return }
        
        guard let url = URL(string: Config.wsURL + Config.Endpoints.wsMarket) else {
            print("Invalid WebSocket URL")
            return
        }
        
        webSocket = session.webSocketTask(with: url)
        webSocket?.resume()
        
        receiveMessage()
        
        DispatchQueue.main.async {
            self.isConnected = true
            AppState.shared.isWebSocketConnected = true
        }
        
        // Resubscribe to symbols
        for symbol in subscribedSymbols {
            subscribe(to: symbol)
        }
    }
    
    func disconnect() {
        reconnectTimer?.invalidate()
        reconnectTimer = nil
        
        webSocket?.cancel(with: .goingAway, reason: nil)
        webSocket = nil
        
        DispatchQueue.main.async {
            self.isConnected = false
            AppState.shared.isWebSocketConnected = false
        }
    }
    
    // MARK: - Settings Sync Connection (Authenticated)
    func connectSync() {
        guard syncWebSocket == nil else { return }
        
        // Need user_id and token for authenticated connection
        guard let userId = UserDefaults.standard.object(forKey: Config.userIdKey) as? Int,
              let token = UserDefaults.standard.string(forKey: Config.tokenKey) else {
            print("Cannot connect to sync WebSocket: not authenticated")
            return
        }
        
        // Construct URL with user_id and token
        let urlString = "\(Config.wsURL)\(Config.Endpoints.wsSettingsSync)/\(userId)?token=\(token)"
        guard let url = URL(string: urlString) else {
            print("Invalid sync WebSocket URL")
            return
        }
        
        syncWebSocket = session.webSocketTask(with: url)
        syncWebSocket?.resume()
        
        receiveSyncMessage()
        
        DispatchQueue.main.async {
            self.isSyncConnected = true
        }
        print("✅ Settings sync WebSocket connected")
    }
    
    func disconnectSync() {
        syncReconnectTimer?.invalidate()
        syncReconnectTimer = nil
        
        syncWebSocket?.cancel(with: .goingAway, reason: nil)
        syncWebSocket = nil
        
        DispatchQueue.main.async {
            self.isSyncConnected = false
        }
    }
    
    // MARK: - Connect All (call after login)
    func connectAll() {
        connect()
        connectSync()
    }
    
    func disconnectAll() {
        disconnect()
        disconnectSync()
    }
    
    // MARK: - Subscriptions
    func subscribe(to symbol: String) {
        subscribedSymbols.insert(symbol)
        
        let message: [String: Any] = [
            "action": "subscribe",
            "channel": "ticker",
            "symbol": symbol
        ]
        
        send(message)
    }
    
    func unsubscribe(from symbol: String) {
        subscribedSymbols.remove(symbol)
        
        let message: [String: Any] = [
            "action": "unsubscribe",
            "channel": "ticker",
            "symbol": symbol
        ]
        
        send(message)
    }
    
    // MARK: - Send Message (Market WebSocket)
    private func send(_ dict: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: dict),
              let string = String(data: data, encoding: .utf8) else {
            return
        }
        
        webSocket?.send(.string(string)) { error in
            if let error = error {
                print("WebSocket send error: \(error)")
            }
        }
    }
    
    // MARK: - Send Sync Message (Sync WebSocket)
    private func sendSync(_ dict: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: dict),
              let string = String(data: data, encoding: .utf8) else {
            return
        }
        
        syncWebSocket?.send(.string(string)) { error in
            if let error = error {
                print("Sync WebSocket send error: \(error)")
            }
        }
    }
    
    // MARK: - Receive Message (Market WebSocket)
    private func receiveMessage() {
        webSocket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    self?.handleMessage(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        self?.handleMessage(text)
                    }
                @unknown default:
                    break
                }
                
                // Continue receiving
                self?.receiveMessage()
                
            case .failure(let error):
                print("WebSocket receive error: \(error)")
                self?.handleDisconnect()
            }
        }
    }
    
    // MARK: - Receive Sync Message (Sync WebSocket)
    private func receiveSyncMessage() {
        syncWebSocket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    self?.handleSyncWebSocketMessage(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        self?.handleSyncWebSocketMessage(text)
                    }
                @unknown default:
                    break
                }
                
                // Continue receiving
                self?.receiveSyncMessage()
                
            case .failure(let error):
                print("Sync WebSocket receive error: \(error)")
                self?.handleSyncDisconnect()
            }
        }
    }
    
    private func handleSyncWebSocketMessage(_ text: String) {
        guard let data = text.data(using: .utf8) else { return }
        
        // Handle ping/pong
        if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           json["type"] as? String == "ping" {
            sendSync(["type": "pong"])
            return
        }
        
        // Try to decode as sync message
        if let sync = try? JSONDecoder().decode(WSSyncMessage.self, from: data) {
            print("📡 Sync message from server: \(sync.type)")
            syncSubject.send(sync)
            handleSyncMessage(sync)
        }
    }
    
    private func handleSyncDisconnect() {
        DispatchQueue.main.async {
            self.isSyncConnected = false
        }
        
        syncWebSocket = nil
        
        // Schedule reconnect
        syncReconnectTimer?.invalidate()
        syncReconnectTimer = Timer.scheduledTimer(withTimeInterval: Config.wsReconnectDelay, repeats: false) { [weak self] _ in
            self?.connectSync()
        }
    }
    
    private func handleMessage(_ text: String) {
        guard let data = text.data(using: .utf8) else { return }
        
        // Try to decode as sync message first (settings sync) - for backwards compatibility
        if let sync = try? JSONDecoder().decode(WSSyncMessage.self, from: data),
           ["settings_changed", "exchange_switched", "account_switched", "sync_request"].contains(sync.type) {
            print("📡 Sync message received: \(sync.type) from \(sync.source)")
            syncSubject.send(sync)
            handleSyncMessage(sync)
            return
        }
        
        // Try to decode as ticker
        if let ticker = try? JSONDecoder().decode(WSTickerMessage.self, from: data) {
            DispatchQueue.main.async {
                self.lastTicker = ticker
                self.tickers[ticker.symbol] = ticker
            }
            tickerSubject.send(ticker)
            return
        }
        
        // Try to decode as trade
        if let trade = try? JSONDecoder().decode(WSTradeMessage.self, from: data) {
            tradeSubject.send(trade)
            return
        }
    }
    
    // MARK: - Sync Message Handling
    private func handleSyncMessage(_ sync: WSSyncMessage) {
        // Don't handle our own messages
        if sync.source == "ios" { return }
        
        DispatchQueue.main.async {
            switch sync.type {
            case "exchange_switched":
                if let newExchange = sync.data?.exchange {
                    print("🔄 Exchange switched to \(newExchange) from \(sync.source)")
                    AppState.shared.selectedExchange = newExchange == "hyperliquid" ? .hyperliquid : .bybit
                    NotificationCenter.default.post(name: .exchangeSwitched, object: nil, userInfo: ["exchange": newExchange, "source": sync.source])
                }
                
            case "account_switched":
                if let newAccountType = sync.data?.accountType {
                    print("🔄 Account switched to \(newAccountType) from \(sync.source)")
                    AppState.shared.selectedAccountType = newAccountType
                    NotificationCenter.default.post(name: .accountTypeSwitched, object: nil, userInfo: ["accountType": newAccountType, "source": sync.source])
                }
                
            case "settings_changed":
                print("⚙️ Settings changed from \(sync.source)")
                NotificationCenter.default.post(name: .settingsChanged, object: nil, userInfo: ["sync": sync])
                
            case "sync_request":
                // Server requests sync - reload all data
                print("🔄 Sync request from server")
                NotificationCenter.default.post(name: .syncRequested, object: nil)
                
            default:
                break
            }
        }
    }
    
    // MARK: - Send Sync Updates (via Sync WebSocket)
    func sendExchangeSwitch(to exchange: String) {
        let message: [String: Any] = [
            "type": "exchange_switched",
            "source": "ios",
            "data": [
                "exchange": exchange,
                "timestamp": ISO8601DateFormatter().string(from: Date())
            ]
        ]
        sendSync(message)
    }
    
    func sendAccountTypeSwitch(to accountType: String, exchange: String) {
        let message: [String: Any] = [
            "type": "account_switched",
            "source": "ios",
            "data": [
                "account_type": accountType,
                "exchange": exchange,
                "timestamp": ISO8601DateFormatter().string(from: Date())
            ]
        ]
        sendSync(message)
    }
    
    func sendSettingsChange(strategy: String, setting: String, oldValue: Any?, newValue: Any?) {
        let message: [String: Any] = [
            "type": "settings_changed",
            "source": "ios",
            "data": [
                "strategy": strategy,
                "setting": setting,
                "old_value": String(describing: oldValue ?? ""),
                "new_value": String(describing: newValue ?? ""),
                "timestamp": ISO8601DateFormatter().string(from: Date())
            ]
        ]
        sendSync(message)
    }
    
    // MARK: - Reconnection
    private func handleDisconnect() {
        DispatchQueue.main.async {
            self.isConnected = false
            AppState.shared.isWebSocketConnected = false
        }
        
        webSocket = nil
        
        // Schedule reconnect
        reconnectTimer?.invalidate()
        reconnectTimer = Timer.scheduledTimer(withTimeInterval: Config.wsReconnectDelay, repeats: false) { [weak self] _ in
            self?.connect()
        }
    }
}

// MARK: - URLSessionWebSocketDelegate
extension WebSocketService: URLSessionWebSocketDelegate {
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        print("WebSocket connected")
        DispatchQueue.main.async {
            self.isConnected = true
        }
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        print("WebSocket closed: \(closeCode)")
        handleDisconnect()
    }
}
