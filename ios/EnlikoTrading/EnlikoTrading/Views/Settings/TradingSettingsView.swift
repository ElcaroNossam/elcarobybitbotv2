//
//  TradingSettingsView.swift
//  EnlikoTrading
//
//  Global trading settings view (DCA, Order Type, Spot, ATR, Exchanges)
//

import SwiftUI

struct TradingSettingsView: View {
    @ObservedObject private var service = GlobalSettingsService.shared
    @ObservedObject private var localization = LocalizationManager.shared
    
    @State private var dcaEnabled = false
    @State private var dcaPct1 = 10.0
    @State private var dcaPct2 = 25.0
    
    @State private var orderType = "market"
    @State private var limitOffsetPct = 0.1
    
    @State private var spotEnabled = false
    @State private var spotDcaEnabled = false
    @State private var spotDcaPct = 5.0
    
    @State private var useAtr = true
    @State private var atrPeriods = 7
    @State private var atrMultiplierSl = 0.5
    @State private var atrTriggerPct = 3.0
    @State private var atrStepPct = 0.5
    
    @State private var bybitEnabled = true
    @State private var hyperliquidEnabled = false
    
    // Per-exchange settings
    @State private var bybitMarginMode = "cross"
    @State private var bybitLeverage = 10
    @State private var bybitOrderType = "market"
    @State private var bybitCoinsGroup = "ALL"
    
    @State private var hlMarginMode = "cross"
    @State private var hlLeverage = 10
    @State private var hlOrderType = "market"
    @State private var hlCoinsGroup = "ALL"
    
    @State private var showingSaveAlert = false
    @State private var isSaving = false
    
    private let leverageOptions = [1, 2, 3, 5, 10, 20, 25, 50, 100]
    private let coinsOptions = ["ALL", "TOP", "VOLATILE"]
    
    var body: some View {
        Form {
            // MARK: - Bybit Exchange Settings
            Section {
                Picker("margin_type".localized, selection: $bybitMarginMode) {
                    Text("🔄 CROSS").tag("cross")
                    Text("📦 ISOLATED").tag("isolated")
                }
                .pickerStyle(.segmented)
                
                Picker("leverage".localized, selection: $bybitLeverage) {
                    ForEach(leverageOptions, id: \.self) { lev in
                        Text("\(lev)x").tag(lev)
                    }
                }
                
                Picker("order_type".localized, selection: $bybitOrderType) {
                    Text("market".localized).tag("market")
                    Text("limit".localized).tag("limit")
                }
                .pickerStyle(.segmented)
                
                Picker("coins_filter".localized, selection: $bybitCoinsGroup) {
                    ForEach(coinsOptions, id: \.self) { group in
                        Text(coinsGroupLabel(group)).tag(group)
                    }
                }
            } header: {
                HStack {
                    Image(systemName: "circle.fill")
                        .foregroundColor(.orange)
                        .font(.caption2)
                    Text("Bybit")
                }
            }
            
            // MARK: - HyperLiquid Exchange Settings
            Section {
                Picker("margin_type".localized, selection: $hlMarginMode) {
                    Text("🔄 CROSS").tag("cross")
                    Text("📦 ISOLATED").tag("isolated")
                }
                .pickerStyle(.segmented)
                
                Picker("leverage".localized, selection: $hlLeverage) {
                    ForEach(leverageOptions, id: \.self) { lev in
                        Text("\(lev)x").tag(lev)
                    }
                }
                
                Picker("order_type".localized, selection: $hlOrderType) {
                    Text("market".localized).tag("market")
                    Text("limit".localized).tag("limit")
                }
                .pickerStyle(.segmented)
                
                Picker("coins_filter".localized, selection: $hlCoinsGroup) {
                    ForEach(coinsOptions, id: \.self) { group in
                        Text(coinsGroupLabel(group)).tag(group)
                    }
                }
            } header: {
                HStack {
                    Image(systemName: "circle.fill")
                        .foregroundColor(.blue)
                        .font(.caption2)
                    Text("HyperLiquid")
                }
            }
            
            // MARK: - Order Type Section
            Section {
                Picker("order_type".localized, selection: $orderType) {
                    Text("market".localized).tag("market")
                    Text("limit".localized).tag("limit")
                }
                .pickerStyle(.segmented)
                
                if orderType == "limit" {
                    HStack {
                        Text("limit_offset".localized)
                        Spacer()
                        TextField("0.1", value: $limitOffsetPct, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 60)
                        Text("%")
                    }
                }
            } header: {
                Text("order_settings".localized)
            } footer: {
                Text("order_type_hint".localized)
            }
            
            // MARK: - DCA Section
            Section {
                Toggle("dca_enabled".localized, isOn: $dcaEnabled)
                
                if dcaEnabled {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("dca_level_1".localized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        HStack {
                            Slider(value: $dcaPct1, in: 5...50, step: 1)
                            Text("\(Int(dcaPct1))%")
                                .frame(width: 50)
                        }
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("dca_level_2".localized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        HStack {
                            Slider(value: $dcaPct2, in: 10...100, step: 1)
                            Text("\(Int(dcaPct2))%")
                                .frame(width: 50)
                        }
                    }
                }
            } header: {
                Text("dca_settings".localized)
            } footer: {
                Text("dca_hint".localized)
            }
            
            // MARK: - Spot Trading Section
            Section {
                Toggle("spot_enabled".localized, isOn: $spotEnabled)
                
                if spotEnabled {
                    Toggle("spot_dca_enabled".localized, isOn: $spotDcaEnabled)
                    
                    if spotDcaEnabled {
                        HStack {
                            Text("spot_dca_pct".localized)
                            Spacer()
                            TextField("5", value: $spotDcaPct, format: .number)
                                .keyboardType(.decimalPad)
                                .multilineTextAlignment(.trailing)
                                .frame(width: 60)
                            Text("%")
                        }
                    }
                }
            } header: {
                Text("spot_trading".localized)
            }
            
            // MARK: - ATR Section
            Section {
                Toggle("use_atr".localized, isOn: $useAtr)
                
                if useAtr {
                    Stepper("atr_periods".localized + ": \(atrPeriods)", value: $atrPeriods, in: 3...50)
                    
                    HStack {
                        Text("atr_multiplier".localized)
                        Spacer()
                        TextField("0.5", value: $atrMultiplierSl, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 60)
                        Text("x")
                    }
                    
                    HStack {
                        Text("atr_trigger".localized)
                        Spacer()
                        TextField("3.0", value: $atrTriggerPct, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 60)
                        Text("%")
                    }
                    
                    HStack {
                        Text("atr_step".localized)
                        Spacer()
                        TextField("0.5", value: $atrStepPct, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 60)
                        Text("%")
                    }
                }
            } header: {
                Text("atr_trailing".localized)
            } footer: {
                Text("atr_hint".localized)
            }
            
            // MARK: - Exchanges Section
            Section {
                HStack {
                    Image(systemName: "circle.fill")
                        .foregroundColor(.orange)
                        .font(.caption)
                    Text("Bybit")
                    Spacer()
                    if service.exchangeStatus?.bybitConfigured == true {
                        Toggle("", isOn: $bybitEnabled)
                    } else {
                        Text("not_configured".localized)
                            .foregroundColor(.secondary)
                            .font(.caption)
                    }
                }
                
                HStack {
                    Image(systemName: "circle.fill")
                        .foregroundColor(.blue)
                        .font(.caption)
                    Text("HyperLiquid")
                    Spacer()
                    if service.exchangeStatus?.hyperliquidConfigured == true {
                        Toggle("", isOn: $hyperliquidEnabled)
                    } else {
                        Text("not_configured".localized)
                            .foregroundColor(.secondary)
                            .font(.caption)
                    }
                }
            } header: {
                Text("exchanges".localized)
            } footer: {
                Text("exchange_toggle_hint".localized)
            }
            
            // MARK: - Save Button
            Section {
                Button(action: saveSettings) {
                    HStack {
                        Spacer()
                        if isSaving {
                            ProgressView()
                                .padding(.trailing, 8)
                        }
                        Text("save_settings".localized)
                            .fontWeight(.semibold)
                        Spacer()
                    }
                }
                .disabled(isSaving)
            }
        }
        .navigationTitle("trading_settings".localized)
        .task {
            await loadSettings()
        }
        .refreshable {
            await loadSettings()
        }
        .alert("settings_saved".localized, isPresented: $showingSaveAlert) {
            Button("OK", role: .cancel) {}
        }
    }
    
    private func loadSettings() async {
        await service.fetchGlobalSettings()
        await service.fetchExchangeStatus()
        
        let settings = service.globalSettings
        dcaEnabled = settings.dcaEnabled
        dcaPct1 = settings.dcaPct1
        dcaPct2 = settings.dcaPct2
        orderType = settings.orderType
        limitOffsetPct = settings.limitOffsetPct
        spotEnabled = settings.spotEnabled
        spotDcaEnabled = settings.spotDcaEnabled
        spotDcaPct = settings.spotDcaPct
        useAtr = settings.useAtr
        atrPeriods = settings.atrPeriods
        atrMultiplierSl = settings.atrMultiplierSl
        atrTriggerPct = settings.atrTriggerPct
        atrStepPct = settings.atrStepPct
        
        // Per-exchange settings
        bybitMarginMode = settings.bybitMarginMode
        bybitLeverage = settings.bybitLeverage
        bybitOrderType = settings.bybitOrderType
        bybitCoinsGroup = settings.bybitCoinsGroup
        hlMarginMode = settings.hlMarginMode
        hlLeverage = settings.hlLeverage
        hlOrderType = settings.hlOrderType
        hlCoinsGroup = settings.hlCoinsGroup
        
        if let status = service.exchangeStatus {
            bybitEnabled = status.bybitEnabled
            hyperliquidEnabled = status.hyperliquidEnabled
        }
    }
    
    private func saveSettings() {
        Task {
            isSaving = true
            defer { isSaving = false }
            
            // Save all settings
            var success = true
            
            // DCA settings
            success = await service.updateDCASettings(
                enabled: dcaEnabled,
                pct1: dcaPct1,
                pct2: dcaPct2
            ) && success
            
            // Order type settings
            success = await service.updateOrderType(
                orderType,
                limitOffsetPct: limitOffsetPct
            ) && success
            
            // ATR settings
            success = await service.updateATRSettings(
                useAtr: useAtr,
                periods: atrPeriods,
                multiplierSl: atrMultiplierSl,
                triggerPct: atrTriggerPct,
                stepPct: atrStepPct
            ) && success
            
            // Spot settings
            success = await service.updateSpotSettings(
                enabled: spotEnabled,
                dcaEnabled: spotDcaEnabled,
                dcaPct: spotDcaPct
            ) && success
            
            // Exchange toggles
            if let status = service.exchangeStatus {
                if status.bybitConfigured && bybitEnabled != status.bybitEnabled {
                    success = await service.toggleExchange("bybit", enabled: bybitEnabled) && success
                }
                if status.hyperliquidConfigured && hyperliquidEnabled != status.hyperliquidEnabled {
                    success = await service.toggleExchange("hyperliquid", enabled: hyperliquidEnabled) && success
                }
            }
            
            // Per-exchange settings: Bybit
            success = await service.updateExchangeSettings(
                exchange: "bybit",
                marginMode: bybitMarginMode,
                leverage: bybitLeverage,
                orderType: bybitOrderType,
                coinsGroup: bybitCoinsGroup
            ) && success
            
            // Per-exchange settings: HyperLiquid
            success = await service.updateExchangeSettings(
                exchange: "hyperliquid",
                marginMode: hlMarginMode,
                leverage: hlLeverage,
                orderType: hlOrderType,
                coinsGroup: hlCoinsGroup
            ) && success
            
            if success {
                showingSaveAlert = true
            }
        }
    }
    
    private func coinsGroupLabel(_ group: String) -> String {
        switch group {
        case "ALL": return "🌐 ALL"
        case "TOP": return "💎 TOP"
        case "VOLATILE": return "🔥 VOLATILE"
        default: return group
        }
    }
}

// MARK: - Preview
#Preview {
    NavigationStack {
        TradingSettingsView()
    }
}
