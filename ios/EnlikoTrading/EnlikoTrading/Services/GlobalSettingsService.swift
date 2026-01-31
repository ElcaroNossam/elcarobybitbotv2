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
    private let _dcaEnabled: Bool?
    private let _dcaPct1: Double?
    private let _dcaPct2: Double?
    private let _orderType: String?
    private let _limitOffsetPct: Double?
    private let _spotDcaEnabled: Bool?
    private let _spotDcaPct: Double?
    private let _spotEnabled: Bool?
    private let _useAtr: Bool?
    private let _atrPeriods: Int?
    private let _atrMultiplierSl: Double?
    private let _atrTriggerPct: Double?
    private let _atrStepPct: Double?
    
    var dcaEnabled: Bool { _dcaEnabled ?? false }
    var dcaPct1: Double { _dcaPct1 ?? 10.0 }
    var dcaPct2: Double { _dcaPct2 ?? 25.0 }
    var orderType: String { _orderType ?? "market" }
    var limitOffsetPct: Double { _limitOffsetPct ?? 0.1 }
    var spotDcaEnabled: Bool { _spotDcaEnabled ?? false }
    var spotDcaPct: Double { _spotDcaPct ?? 5.0 }
    var spotEnabled: Bool { _spotEnabled ?? false }
    var useAtr: Bool { _useAtr ?? false }
    var atrPeriods: Int { _atrPeriods ?? 14 }
    var atrMultiplierSl: Double { _atrMultiplierSl ?? 1.5 }
    var atrTriggerPct: Double { _atrTriggerPct ?? 0.5 }
    var atrStepPct: Double { _atrStepPct ?? 0.25 }
    
    enum CodingKeys: String, CodingKey {
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
    }
    
    static var `default`: GlobalSettings {
        // Decode from empty dict to get all defaults
        let json = "{}"
        let data = json.data(using: .utf8)!
        return try! JSONDecoder().decode(GlobalSettings.self, from: data)
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

struct ExchangeToggleUpdate: Codable {
    let exchange: String
    let enabled: Bool
}

// MARK: - Service

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
        periods: Int = 14,
        multiplierSl: Double = 1.5,
        triggerPct: Double = 0.5,
        stepPct: Double = 0.25
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
}
