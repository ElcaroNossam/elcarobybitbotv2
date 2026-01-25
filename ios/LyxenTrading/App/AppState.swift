//
//  AppState.swift
//  LyxenTrading
//

import SwiftUI
import Combine

// MARK: - App State
class AppState: ObservableObject {
    static let shared = AppState()
    
    @Published var currentExchange: Exchange = .bybit
    @Published var currentAccountType: AccountType = .demo
    @Published var tradingMode: TradingMode = .demo
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showError = false
    
    // Alias for backward compatibility
    var selectedExchange: Exchange {
        get { currentExchange }
        set { currentExchange = newValue }
    }
    
    var selectedAccountType: AccountType {
        get { currentAccountType }
        set { currentAccountType = newValue }
    }
    
    // WebSocket connection state
    @Published var isWebSocketConnected = false
    
    private init() {
        loadSavedPreferences()
    }
    
    func showError(_ message: String) {
        DispatchQueue.main.async {
            self.errorMessage = message
            self.showError = true
        }
    }
    
    func clearError() {
        errorMessage = nil
        showError = false
    }
    
    func loadSavedPreferences() {
        if let exchangeRaw = UserDefaults.standard.string(forKey: "currentExchange"),
           let exchange = Exchange(rawValue: exchangeRaw) {
            currentExchange = exchange
        }
        
        if let accountRaw = UserDefaults.standard.string(forKey: "currentAccountType"),
           let account = AccountType(rawValue: accountRaw) {
            currentAccountType = account
        }
    }
    
    func savePreferences() {
        UserDefaults.standard.set(currentExchange.rawValue, forKey: "currentExchange")
        UserDefaults.standard.set(currentAccountType.rawValue, forKey: "currentAccountType")
    }
    
    func switchExchange(to exchange: Exchange) {
        currentExchange = exchange
        // Reset account type based on exchange
        if exchange == .hyperliquid {
            currentAccountType = .testnet
        } else {
            currentAccountType = tradingMode == .real ? .real : .demo
        }
        savePreferences()
    }
    
    func switchAccountType(to type: AccountType) {
        currentAccountType = type
        savePreferences()
    }
}

// MARK: - Enums
enum Exchange: String, CaseIterable, Codable {
    case bybit = "bybit"
    case hyperliquid = "hyperliquid"
    
    var displayName: String {
        switch self {
        case .bybit: return "Bybit"
        case .hyperliquid: return "HyperLiquid"
        }
    }
    
    var icon: String {
        switch self {
        case .bybit: return "🟠"
        case .hyperliquid: return "🔷"
        }
    }
    
    var accountTypes: [AccountType] {
        switch self {
        case .bybit: return [.demo, .real]
        case .hyperliquid: return [.testnet, .mainnet]
        }
    }
}

enum AccountType: String, CaseIterable, Codable {
    case demo = "demo"
    case real = "real"
    case testnet = "testnet"
    case mainnet = "mainnet"
    
    var displayName: String {
        switch self {
        case .demo: return "Demo"
        case .real: return "Real"
        case .testnet: return "Testnet"
        case .mainnet: return "Mainnet"
        }
    }
    
    var icon: String {
        switch self {
        case .demo: return "🎮"
        case .real: return "💎"
        case .testnet: return "🧪"
        case .mainnet: return "🌐"
        }
    }
    
    var isLive: Bool {
        return self == .real || self == .mainnet
    }
}

enum TradingMode: String, CaseIterable, Codable {
    case demo = "demo"
    case real = "real"
    case both = "both"
}

enum OrderSide: String, CaseIterable, Codable {
    case buy = "Buy"
    case sell = "Sell"
    
    var color: Color {
        switch self {
        case .buy: return .lyxenGreen
        case .sell: return .lyxenRed
        }
    }
}

enum OrderType: String, CaseIterable, Codable {
    case market = "Market"
    case limit = "Limit"
}

enum PositionSide: String, Codable {
    case long = "Buy"
    case short = "Sell"
    
    var displayName: String {
        switch self {
        case .long: return "LONG"
        case .short: return "SHORT"
        }
    }
    
    var color: Color {
        switch self {
        case .long: return .lyxenGreen
        case .short: return .lyxenRed
        }
    }
}
