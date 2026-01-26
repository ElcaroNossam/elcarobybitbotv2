//
//  GlobalSettingsService.swift
//  LyxenTrading
//
//  Global trading settings service (DCA, Order Type, Spot, ATR, Exchange status)
//

import Foundation
import Combine

// MARK: - Models

struct GlobalSettings: Codable {
    let dcaEnabled: Bool
    let dcaPct1: Double
    let dcaPct2: Double
    let orderType: String
    let limitOffsetPct: Double
    let spotDcaEnabled: Bool
    let spotDcaPct: Double
    let spotEnabled: Bool
    let useAtr: Bool
    let atrPeriods: Int
    let atrMultiplierSl: Double
    let atrTriggerPct: Double
    let atrStepPct: Double
    
    enum CodingKeys: String, CodingKey {
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
        case orderType = "order_type"
        case limitOffsetPct = "limit_offset_pct"
        case spotDcaEnabled = "spot_dca_enabled"
        case spotDcaPct = "spot_dca_pct"
        case spotEnabled = "spot_enabled"
        case useAtr = "use_atr"
        case atrPeriods = "atr_periods"
        case atrMultiplierSl = "atr_multiplier_sl"
        case atrTriggerPct = "atr_trigger_pct"
        case atrStepPct = "atr_step_pct"
    }
    
    static var `default`: GlobalSettings {
        GlobalSettings(
            dcaEnabled: false,
            dcaPct1: 10.0,
            dcaPct2: 25.0,
            orderType: "market",
            limitOffsetPct: 0.1,
            spotDcaEnabled: false,
            spotDcaPct: 5.0,
            spotEnabled: false,
            useAtr: false,
            atrPeriods: 14,
            atrMultiplierSl: 1.5,
            atrTriggerPct: 0.5,
            atrStepPct: 0.25
        )
    }
}

struct ExchangeStatus: Codable {
    let bybitEnabled: Bool
    let bybitConfigured: Bool
    let hyperliquidEnabled: Bool
    let hyperliquidConfigured: Bool
    
    enum CodingKeys: String, CodingKey {
        case bybitEnabled = "bybit_enabled"
        case bybitConfigured = "bybit_configured"
        case hyperliquidEnabled = "hyperliquid_enabled"
        case hyperliquidConfigured = "hyperliquid_configured"
    }
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
    
    // MARK: - Update Global Settings
    @MainActor
    func updateGlobalSettings(_ updates: [String: Any]) async -> Bool {
        do {
            let _: EmptyResponse = try await network.put("/users/global-settings", body: updates)
            await fetchGlobalSettings()
            return true
        } catch {
            print("Failed to update global settings: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
    
    // MARK: - Update DCA Settings
    @MainActor
    func updateDCASettings(enabled: Bool, pct1: Double, pct2: Double) async -> Bool {
        return await updateGlobalSettings([
            "dca_enabled": enabled,
            "dca_pct_1": pct1,
            "dca_pct_2": pct2
        ])
    }
    
    // MARK: - Update Order Type
    @MainActor
    func updateOrderType(_ orderType: String, limitOffsetPct: Double = 0.1) async -> Bool {
        return await updateGlobalSettings([
            "order_type": orderType,
            "limit_offset_pct": limitOffsetPct
        ])
    }
    
    // MARK: - Update Spot Settings
    @MainActor
    func updateSpotSettings(enabled: Bool, dcaEnabled: Bool, dcaPct: Double) async -> Bool {
        do {
            let _: EmptyResponse = try await network.put("/users/spot-settings", body: [
                "spot_enabled": enabled,
                "spot_dca_enabled": dcaEnabled,
                "spot_dca_pct": dcaPct
            ])
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
        return await updateGlobalSettings([
            "use_atr": useAtr,
            "atr_periods": periods,
            "atr_multiplier_sl": multiplierSl,
            "atr_trigger_pct": triggerPct,
            "atr_step_pct": stepPct
        ])
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
            let _: EmptyResponse = try await network.put("/users/exchange-trading-status", body: [
                "exchange": exchange,
                "enabled": enabled
            ])
            await fetchExchangeStatus()
            return true
        } catch {
            print("Failed to toggle exchange: \(error)")
            AppState.shared.showError(error.localizedDescription)
            return false
        }
    }
}
