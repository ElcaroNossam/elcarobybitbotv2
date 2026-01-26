//
//  TradingSettingsView.swift
//  LyxenTrading
//
//  Global trading settings view (DCA, Order Type, Spot, ATR, Exchanges)
//

import SwiftUI

struct TradingSettingsView: View {
    @StateObject private var service = GlobalSettingsService.shared
    @ObservedObject private var localization = LocalizationManager.shared
    
    @State private var dcaEnabled = false
    @State private var dcaPct1 = 10.0
    @State private var dcaPct2 = 25.0
    
    @State private var orderType = "market"
    @State private var limitOffsetPct = 0.1
    
    @State private var spotEnabled = false
    @State private var spotDcaEnabled = false
    @State private var spotDcaPct = 5.0
    
    @State private var useAtr = false
    @State private var atrPeriods = 14
    @State private var atrTriggerPct = 0.5
    @State private var atrStepPct = 0.25
    
    @State private var bybitEnabled = true
    @State private var hyperliquidEnabled = false
    
    @State private var showingSaveAlert = false
    @State private var isSaving = false
    
    var body: some View {
        Form {
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
                    Stepper("atr_periods".localized + ": \(atrPeriods)", value: $atrPeriods, in: 5...50)
                    
                    HStack {
                        Text("atr_trigger".localized)
                        Spacer()
                        TextField("0.5", value: $atrTriggerPct, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 60)
                        Text("%")
                    }
                    
                    HStack {
                        Text("atr_step".localized)
                        Spacer()
                        TextField("0.25", value: $atrStepPct, format: .number)
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
        atrTriggerPct = settings.atrTriggerPct
        atrStepPct = settings.atrStepPct
        
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
                multiplierSl: 1.5,  // Default multiplier
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
            
            if success {
                showingSaveAlert = true
            }
        }
    }
}

// MARK: - Preview
#Preview {
    NavigationStack {
        TradingSettingsView()
    }
}
