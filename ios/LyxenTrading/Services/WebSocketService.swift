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

// MARK: - WebSocket Service
class WebSocketService: NSObject, ObservableObject {
    static let shared = WebSocketService()
    
    @Published var isConnected = false
    @Published var lastTicker: WSTickerMessage?
    @Published var tickers: [String: WSTickerMessage] = [:]
    
    private var webSocket: URLSessionWebSocketTask?
    private var session: URLSession!
    private var reconnectTimer: Timer?
    private var subscribedSymbols: Set<String> = []
    
    private let tickerSubject = PassthroughSubject<WSTickerMessage, Never>()
    private let tradeSubject = PassthroughSubject<WSTradeMessage, Never>()
    
    var tickerPublisher: AnyPublisher<WSTickerMessage, Never> {
        tickerSubject.eraseToAnyPublisher()
    }
    
    var tradePublisher: AnyPublisher<WSTradeMessage, Never> {
        tradeSubject.eraseToAnyPublisher()
    }
    
    private override init() {
        super.init()
        session = URLSession(configuration: .default, delegate: self, delegateQueue: nil)
    }
    
    // MARK: - Connection
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
    
    // MARK: - Send Message
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
    
    // MARK: - Receive Message
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
    
    private func handleMessage(_ text: String) {
        guard let data = text.data(using: .utf8) else { return }
        
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
