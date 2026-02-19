//
//  GlobalSettingsService.swift
//  EnlikoTrading
//
//  Global trading settings service (DCA, Order Type, Spot, ATR, Exchange status)
//

import Foundation
import Combine

// MARK: - Models

struct GlobalSettings: Codable {
    // Private backing optionals for Codable
    private var _percent: Double?
    private var _tpPercent: Double?
    private var _slPercent: Double?
    private var _leverage: Int?
    private var _dcaEnabled: Bool?
    private var _dcaPct1: Double?
    private var _dcaPct2: Double?
    private var _orderType: String?
    private var _limitOffsetPct: Double?
    private var _spotDcaEnabled: Bool?
    private var _spotDcaPct: Double?
    private var _spotEnabled: Bool?
    private var _useAtr: Bool?
    private var _atrPeriods: Int?
    private var _atrMultiplierSl: Double?
    private var _atrTriggerPct: Double?
    private var _atrStepPct: Double?
    // Per-exchange settings
    private var _bybitMarginMode: String?
    private var _bybitLeverage: Int?
    private var _bybitOrderType: String?
    private var _bybitCoinsGroup: String?
    private var _hlMarginMode: String?
    private var _hlLeverage: Int?
    private var _hlOrderType: String?
    private var _hlCoinsGroup: String?
    
    // Public computed properties with defaults
    var percent: Double { _percent ?? 1.0 }
    var tpPercent: Double { _tpPercent ?? 10.0 }
    var slPercent: Double { _slPercent ?? 30.0 }
    var leverage: Int { _leverage ?? 10 }
    var dcaEnabled: Bool { _dcaEnabled ?? false }
    var dcaPct1: Double { _dcaPct1 ?? 10.0 }
    var dcaPct2: Double { _dcaPct2 ?? 25.0 }
    var orderType: String { _orderType ?? "market" }
    var limitOffsetPct: Double { _limitOffsetPct ?? 0.1 }
    var spotDcaEnabled: Bool { _spotDcaEnabled ?? false }
    var spotDcaPct: Double { _spotDcaPct ?? 5.0 }
    var spotEnabled: Bool { _spotEnabled ?? false }
    var useAtr: Bool { _useAtr ?? false }
    var atrPeriods: Int { _atrPeriods ?? 7 }
    var atrMultiplierSl: Double { _atrMultiplierSl ?? 0.5 }
    var atrTriggerPct: Double { _atrTriggerPct ?? 3.0 }
    var atrStepPct: Double { _atrStepPct ?? 0.5 }
    // Per-exchange computed
    var bybitMarginMode: String { _bybitMarginMode ?? "cross" }
    var bybitLeverage: Int { _bybitLeverage ?? 10 }
    var bybitOrderType: String { _bybitOrderType ?? "market" }
    var bybitCoinsGroup: String { _bybitCoinsGroup ?? "ALL" }
    var hlMarginMode: String { _hlMarginMode ?? "cross" }
    var hlLeverage: Int { _hlLeverage ?? 10 }
    var hlOrderType: String { _hlOrderType ?? "market" }
    var hlCoinsGroup: String { _hlCoinsGroup ?? "ALL" }
    
    enum CodingKeys: String, CodingKey {
        case _percent = "percent"
        case _tpPercent = "tp_percent"
        case _slPercent = "sl_percent"
        case _leverage = "leverage"
        case _dcaEnabled = "dca_enabled"
        case _dcaPct1 = "dca_pct_1"
        case _dcaPct2 = "dca_pct_2"
        case _orderType = "order_type"
        case _limitOffsetPct = "limit_offset_pct"
        case _spotDcaEnabled = "spot_dca_enabled"
        case _spotDcaPct = "spot_dca_pct"
        case _spotEnabled = "spot_enabled"
        case _useAtr = "use_atr"
        case _atrPeriods = "atr_periods"
        case _atrMultiplierSl = "atr_multiplier_sl"
        case _atrTriggerPct = "atr_trigger_pct"
        case _atrStepPct = "atr_step_pct"
        // Per-exchange
        case _bybitMarginMode = "bybit_margin_mode"
        case _bybitLeverage = "bybit_leverage"
        case _bybitOrderType = "bybit_order_type"
        case _bybitCoinsGroup = "bybit_coins_group"
        case _hlMarginMode = "hl_margin_mode"
        case _hlLeverage = "hl_leverage"
        case _hlOrderType = "hl_order_type"
        case _hlCoinsGroup = "hl_coins_group"
    }
    
    static var `default`: GlobalSettings {
        // Decode from empty dict to get all defaults safely
        guard let data = "{}".data(using: .utf8),
              let decoded = try? JSONDecoder().decode(GlobalSettings.self, from: data) else {
            // If decoding fails, return a manually constructed default
            return GlobalSettings()
        }
        return decoded
    }
    
    // Manual default initializer
    init() {
        self._percent = nil
        self._tpPercent = nil
        self._slPercent = nil
        self._leverage = nil
        self._dcaEnabled = nil
        self._dcaPct1 = nil
        self._dcaPct2 = nil
        self._orderType = nil
        self._limitOffsetPct = nil
        self._spotDcaEnabled = nil
        self._spotDcaPct = nil
        self._spotEnabled = nil
        self._useAtr = nil
        self._atrPeriods = nil
        self._atrMultiplierSl = nil
        self._atrTriggerPct = nil
        self._atrStepPct = nil
        self._bybitMarginMode = nil
        self._bybitLeverage = nil
        self._bybitOrderType = nil
        self._bybitCoinsGroup = nil
        self._hlMarginMode = nil
        self._hlLeverage = nil
        self._hlOrderType = nil
        self._hlCoinsGroup = nil
    }
}

struct ExchangeStatus: Codable {
    private let _bybitEnabled: Bool?
    private let _bybitConfigured: Bool?
    private let _hyperliquidEnabled: Bool?
    private let _hyperliquidConfigured: Bool?
    
    var bybitEnabled: Bool { _bybitEnabled ?? false }
    var bybitConfigured: Bool { _bybitConfigured ?? false }
    var hyperliquidEnabled: Bool { _hyperliquidEnabled ?? false }
    var hyperliquidConfigured: Bool { _hyperliquidConfigured ?? false }
    
    enum CodingKeys: String, CodingKey {
        case _bybitEnabled = "bybit_enabled"
        case _bybitConfigured = "bybit_configured"
        case _hyperliquidEnabled = "hyperliquid_enabled"
        case _hyperliquidConfigured = "hyperliquid_configured"
    }
}

// MARK: - Settings Update Requests
struct DCASettingsUpdate: Codable {
    let dcaEnabled: Bool
    let dcaPct1: Double
    let dcaPct2: Double
    
    enum CodingKeys: String, CodingKey {
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
    }
}

struct OrderTypeUpdate: Codable {
    let orderType: String
    let limitOffsetPct: Double
    
    enum CodingKeys: String, CodingKey {
        case orderType = "order_type"
        case limitOffsetPct = "limit_offset_pct"
    }
}

struct SpotSettingsUpdate: Codable {
    let spotEnabled: Bool
    let spotDcaEnabled: Bool
    let spotDcaPct: Double
    
    enum CodingKeys: String, CodingKey {
        case spotEnabled = "spot_enabled"
        case spotDcaEnabled = "spot_dca_enabled"
        case spotDcaPct = "spot_dca_pct"
    }
}

struct ATRSettingsUpdate: Codable {
    let useAtr: Bool
    let atrPeriods: Int
    let atrMultiplierSl: Double
    let atrTriggerPct: Double
    let atrStepPct: Double
    
    enum CodingKeys: String, CodingKey {
        case useAtr = "use_atr"
        case atrPeriods = "atr_periods"
        case atrMultiplierSl = "atr_multiplier_sl"
        case atrTriggerPct = "atr_trigger_pct"
        case atrStepPct = "atr_step_pct"
    }
}

struct LeverageUpdate: Codable {
    let leverage: Int
}

struct RiskSettingsUpdate: Codable {
    let percent: Double
    let tpPercent: Double
    let slPercent: Double
    let useAtr: Bool
    let dcaEnabled: Bool
    
    enum CodingKeys: String, CodingKey {
        case percent
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case useAtr = "use_atr"
        case dcaEnabled = "dca_enabled"
    }
}

struct ExchangeToggleUpdate: Codable {
    let exchange: String
    let enabled: Bool
}

struct ExchangeSettingsUpdate: Codable {
    let marginMode: String?
    let leverage: Int?
    let orderType: String?
    let coinsGroup: String?
    
    enum CodingKeys: String, CodingKey {
        case marginMode = "margin_mode"
        case leverage
        case orderType = "order_type"
        case coinsGroup = "coins_group"
    }
}

// MARK: - Service

@MainActor
class GlobalSettingsService: ObservableObject {
    static let shared = GlobalSettingsService()
    
    @Published var globalSettings: GlobalSettings = .default
    @Published var exchangeStatus: ExchangeStatus?
    @Published var isLoading = false
    
    private let network = NetworkService.shared
    
    private init() {}
    
    // MARK: - Fetch Global Settings
    @MainActor
    func fetchGlobalSettings() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let settings: GlobalSettings = try await network.get("/users/global-settings")
            self.globalSettings = settings
        } catch {
            print("Failed to fetch global settings: \(error)")
        }
    }
    
    // MARK: - Update DCA Settings
    @MainActor
    func updateDCASettings(enabled: Bool, pct1: Double, pct2: Double) async -> Bool {
        do {
            let update = DCASettingsUpdate(dcaEnabled: enabled, dcaPct1: pct1, dcaPct2: pct2)
            let _: EmptyResponse = try await network.put("/users/global-settings", body: update)
            await fetchGlobalSettings()
            return true
        } catch {
            print("Failed to update DCA settings: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Update Order Type
    @MainActor
    func updateOrderType(_ orderType: String, limitOffsetPct: Double = 0.1) async -> Bool {
        do {
            let update = OrderTypeUpdate(orderType: orderType, limitOffsetPct: limitOffsetPct)
            let _: EmptyResponse = try await network.put("/users/global-settings", body: update)
            await fetchGlobalSettings()
            return true
        } catch {
            print("Failed to update order type: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Update Spot Settings
    @MainActor
    func updateSpotSettings(enabled: Bool, dcaEnabled: Bool, dcaPct: Double) async -> Bool {
        do {
            let update = SpotSettingsUpdate(spotEnabled: enabled, spotDcaEnabled: dcaEnabled, spotDcaPct: dcaPct)
            let _: EmptyResponse = try await network.put("/users/spot-settings", body: update)
            await fetchGlobalSettings()
            return true
        } catch {
            print("Failed to update spot settings: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Update ATR Settings
    @MainActor
    func updateATRSettings(
        useAtr: Bool,
        periods: Int = 7,
        multiplierSl: Double = 0.5,
        triggerPct: Double = 3.0,
        stepPct: Double = 0.5
    ) async -> Bool {
        do {
            let update = ATRSettingsUpdate(
                useAtr: useAtr,
                atrPeriods: periods,
                atrMultiplierSl: multiplierSl,
                atrTriggerPct: triggerPct,
                atrStepPct: stepPct
            )
            let _: EmptyResponse = try await network.put("/users/global-settings", body: update)
            await fetchGlobalSettings()
            return true
        } catch {
            print("Failed to update ATR settings: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Update Leverage
    @MainActor
    func updateLeverage(_ leverage: Int) async -> Bool {
        do {
            let update = LeverageUpdate(leverage: leverage)
            let _: EmptyResponse = try await network.put("/users/global-settings", body: update)
            await fetchGlobalSettings()
            return true
        } catch {
            print("Failed to update leverage: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Update Risk Settings (Entry%, TP%, SL%)
    @MainActor
    func updateRiskSettings(percent: Double, tpPercent: Double, slPercent: Double, useAtr: Bool, dcaEnabled: Bool) async -> Bool {
        do {
            let update = RiskSettingsUpdate(
                percent: percent,
                tpPercent: tpPercent,
                slPercent: slPercent,
                useAtr: useAtr,
                dcaEnabled: dcaEnabled
            )
            let _: EmptyResponse = try await network.put("/users/global-settings", body: update)
            await fetchGlobalSettings()
            return true
        } catch {
            print("Failed to update risk settings: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Fetch Exchange Status
    @MainActor
    func fetchExchangeStatus() async {
        do {
            let status: ExchangeStatus = try await network.get("/users/exchange-trading-status")
            self.exchangeStatus = status
        } catch {
            print("Failed to fetch exchange status: \(error)")
        }
    }
    
    // MARK: - Toggle Exchange
    @MainActor
    func toggleExchange(_ exchange: String, enabled: Bool) async -> Bool {
        do {
            let update = ExchangeToggleUpdate(exchange: exchange, enabled: enabled)
            let _: EmptyResponse = try await network.put("/users/exchange-trading-status", body: update)
            await fetchExchangeStatus()
            return true
        } catch {
            print("Failed to toggle exchange: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Update Per-Exchange Settings (Margin, Leverage, Order Type, Coins)
    @MainActor
    func updateExchangeSettings(
        exchange: String,
        marginMode: String? = nil,
        leverage: Int? = nil,
        orderType: String? = nil,
        coinsGroup: String? = nil
    ) async -> Bool {
        do {
            let update = ExchangeSettingsUpdate(
                marginMode: marginMode,
                leverage: leverage,
                orderType: orderType,
                coinsGroup: coinsGroup
            )
            let _: EmptyResponse = try await network.put("/users/exchange-settings/\(exchange)", body: update)
            await fetchGlobalSettings()
            return true
        } catch {
            print("Failed to update \(exchange) settings: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
}
