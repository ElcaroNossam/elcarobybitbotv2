//
//  AppState.swift
//  EnlikoTrading
//

import SwiftUI
import Combine

// MARK: - App Theme
enum AppTheme: String, CaseIterable {
    case dark = "dark"
    case light = "light"
    case system = "system"
    
    var displayName: String {
        switch self {
        case .dark: return "Dark"
        case .light: return "Light"
        case .system: return "System"
        }
    }
    
    var icon: String {
        switch self {
        case .dark: return "moon.fill"
        case .light: return "sun.max.fill"
        case .system: return "gear"
        }
    }
    
    /// Convert to ColorScheme for SwiftUI
    var colorScheme: ColorScheme? {
        switch self {
        case .dark: return .dark
        case .light: return .light
        case .system: return nil  // nil = use system setting
        }
    }
}

// MARK: - App State
class AppState: ObservableObject {
    static let shared = AppState()
    
    @Published var currentExchange: Exchange = .bybit
    @Published var currentAccountType: AccountType = .demo
    @Published var tradingMode: TradingMode = .demo
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showError = false
    
    // MARK: - Theme Support
    @Published var currentTheme: AppTheme = .dark {
        didSet {
            UserDefaults.standard.set(currentTheme.rawValue, forKey: "app_theme")
        }
    }
    
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
        
        // Load saved theme
        if let themeRaw = UserDefaults.standard.string(forKey: "app_theme"),
           let theme = AppTheme(rawValue: themeRaw) {
            currentTheme = theme
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
        
        // Notify via WebSocket for cross-platform sync
        WebSocketService.shared.sendExchangeSwitch(to: exchange.rawValue)
        
        // Sync with server in background
        Task {
            await syncExchangeWithServer(exchange: exchange)
        }
    }
    
    func switchAccountType(to type: AccountType) {
        currentAccountType = type
        savePreferences()
        
        // Notify via WebSocket for cross-platform sync
        WebSocketService.shared.sendAccountTypeSwitch(to: type.rawValue, exchange: currentExchange.rawValue)
        
        // Sync with server in background
        Task {
            await syncAccountTypeWithServer(accountType: type)
        }
    }
    
    // MARK: - Server Sync
    
    /// Sync exchange preference with server
    private func syncExchangeWithServer(exchange: Exchange) async {
        do {
            let _: EmptyResponse = try await NetworkService.shared.post(
                Config.Endpoints.switchExchange,
                body: ["exchange_type": exchange.rawValue]
            )
            print("✅ Exchange synced with server: \(exchange.rawValue)")
        } catch {
            print("⚠️ Failed to sync exchange with server: \(error.localizedDescription)")
            // Local preference is still saved, will sync on next opportunity
        }
    }
    
    /// Sync account type preference with server
    private func syncAccountTypeWithServer(accountType: AccountType) async {
        do {
            let _: EmptyResponse = try await NetworkService.shared.post(
                Config.Endpoints.switchAccountType,
                body: ["account_type": accountType.rawValue]
            )
            print("✅ Account type synced with server: \(accountType.rawValue)")
        } catch {
            print("⚠️ Failed to sync account type with server: \(error.localizedDescription)")
        }
    }
    
    /// Load exchange preference from server on login
    func syncFromServer() async {
        do {
            let serverSettings: ServerSettings = try await NetworkService.shared.get(
                Config.Endpoints.settings
            )
            
            await MainActor.run {
                if let exchangeRaw = serverSettings.exchangeType,
                   let exchange = Exchange(rawValue: exchangeRaw) {
                    self.currentExchange = exchange
                }
                
                if let modeRaw = serverSettings.tradingMode,
                   let mode = TradingMode(rawValue: modeRaw) {
                    self.tradingMode = mode
                }
                
                // Set appropriate account type based on exchange and mode
                if currentExchange == .hyperliquid {
                    currentAccountType = serverSettings.hlTestnet == true ? .testnet : .mainnet
                } else {
                    // For 'both' mode, check server's lastViewedAccount or default to demo
                    if tradingMode == .both {
                        if let lastAccount = serverSettings.lastViewedAccount,
                           let accountType = AccountType(rawValue: lastAccount) {
                            currentAccountType = accountType
                        } else {
                            currentAccountType = .demo
                        }
                    } else {
                        currentAccountType = tradingMode == .real ? .real : .demo
                    }
                }
                
                // Sync language from server
                if let serverLang = serverSettings.lang,
                   let appLanguage = AppLanguage(rawValue: serverLang) {
                    // Only update if different to avoid server sync loop
                    if LocalizationManager.shared.currentLanguage != appLanguage {
                        LocalizationManager.shared.setLanguageWithoutSync(appLanguage)
                    }
                }
                
                savePreferences()
            }
            print("✅ Settings synced from server")
        } catch {
            print("⚠️ Failed to sync settings from server: \(error.localizedDescription)")
        }
    }
}

// MARK: - Helper Models

struct EmptyResponse: Codable {}

struct ServerSettings: Codable {
    let lastViewedAccount: String?
    let exchangeType: String?
    let tradingMode: String?
    let hlTestnet: Bool?
    let lang: String?
    
    enum CodingKeys: String, CodingKey {
        case lastViewedAccount = "last_viewed_account"
        case exchangeType = "exchange_type"
        case tradingMode = "trading_mode"
        case hlTestnet = "hl_testnet"
        case lang
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
    
    var description: String {
        switch self {
        case .demo: return "Practice trading with virtual funds"
        case .real: return "Live trading with real money"
        case .testnet: return "Test network for practice"
        case .mainnet: return "Main network for live trading"
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
        case .buy: return .enlikoGreen
        case .sell: return .enlikoRed
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
        case .long: return .enlikoGreen
        case .short: return .enlikoRed
        }
    }
}
