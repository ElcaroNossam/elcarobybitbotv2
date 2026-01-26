//
//  StrategySettingsView.swift
//  LyxenTrading
//
//  Beautiful dynamic strategy settings with Long/Short support
//

import SwiftUI

// MARK: - Strategy Info
struct StrategyInfo {
    let id: String
    let name: String
    let description: String
    let icon: String
    let color: Color
    let supportsAtr: Bool
    let supportsDca: Bool
    
    static let all: [StrategyInfo] = [
        StrategyInfo(id: "oi", name: "Open Interest", description: "OI divergence signals", icon: "chart.bar.fill", color: .blue, supportsAtr: true, supportsDca: true),
        StrategyInfo(id: "scryptomera", name: "Scryptomera", description: "Volume delta analysis", icon: "waveform.path.ecg", color: .purple, supportsAtr: true, supportsDca: true),
        StrategyInfo(id: "scalper", name: "Scalper", description: "Momentum breakouts", icon: "bolt.fill", color: .orange, supportsAtr: true, supportsDca: true),
        StrategyInfo(id: "elcaro", name: "LYXEN AI", description: "AI-powered signals", icon: "brain.head.profile", color: .green, supportsAtr: false, supportsDca: false),
        StrategyInfo(id: "fibonacci", name: "Fibonacci", description: "Fib retracement levels", icon: "ruler.fill", color: .cyan, supportsAtr: true, supportsDca: true),
        StrategyInfo(id: "rsi_bb", name: "RSI + BB", description: "RSI & Bollinger Bands", icon: "chart.line.uptrend.xyaxis", color: .pink, supportsAtr: true, supportsDca: true)
    ]
}

// MARK: - Side Settings Model
struct SideSettings: Codable {
    var enabled: Bool
    var percent: Double
    var tpPercent: Double
    var slPercent: Double
    var leverage: Int
    var useAtr: Bool
    var atrTriggerPct: Double?
    var atrStepPct: Double?
    var dcaEnabled: Bool
    var dcaPct1: Double
    var dcaPct2: Double
    var orderType: String
    
    enum CodingKeys: String, CodingKey {
        case enabled, percent, leverage
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case useAtr = "use_atr"
        case atrTriggerPct = "atr_trigger_pct"
        case atrStepPct = "atr_step_pct"
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
        case orderType = "order_type"
    }
    
    static var `default`: SideSettings {
        SideSettings(
            enabled: true,
            percent: 1.0,
            tpPercent: 8.0,
            slPercent: 3.0,
            leverage: 10,
            useAtr: false,
            atrTriggerPct: 0.5,
            atrStepPct: 0.25,
            dcaEnabled: false,
            dcaPct1: 10.0,
            dcaPct2: 25.0,
            orderType: "market"
        )
    }
}

// StrategySettingsUpdateRequest is defined in Models.swift

// MARK: - Main View
struct StrategySettingsView: View {
    @ObservedObject var appState = AppState.shared
    @ObservedObject var localization = LocalizationManager.shared
    @StateObject private var strategyService = StrategyService.shared
    
    @State private var selectedStrategy: StrategyInfo = StrategyInfo.all[0]
    @State private var selectedSide: String = "long"
    
    @State private var longSettings: SideSettings = .default
    @State private var shortSettings: SideSettings = .default
    
    @State private var isLoading = false
    @State private var isSaving = false
    @State private var showSaveSuccess = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Strategy Picker
                strategyPicker
                
                // Side Selector (Long/Short)
                sidePicker
                
                // Current settings
                if selectedSide == "long" {
                    settingsCard(for: $longSettings, side: "long")
                } else {
                    settingsCard(for: $shortSettings, side: "short")
                }
                
                // Save Button
                saveButton
            }
            .padding()
        }
        .background(Color.lyxenBackground.ignoresSafeArea())
        .navigationTitle("strategy_settings".localized)
        .task {
            await loadSettings()
        }
        .alert("settings_saved".localized, isPresented: $showSaveSuccess) {
            Button("OK", role: .cancel) {}
        }
    }
    
    // MARK: - Strategy Picker
    private var strategyPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(StrategyInfo.all, id: \.id) { strategy in
                    StrategyChip(
                        strategy: strategy,
                        isSelected: selectedStrategy.id == strategy.id
                    ) {
                        withAnimation(.spring(response: 0.3)) {
                            selectedStrategy = strategy
                        }
                        Task { await loadSettings() }
                    }
                }
            }
            .padding(.horizontal, 4)
        }
    }
    
    // MARK: - Side Picker
    private var sidePicker: some View {
        HStack(spacing: 0) {
            SideTab(
                title: "LONG",
                icon: "arrow.up.circle.fill",
                color: .lyxenGreen,
                isSelected: selectedSide == "long"
            ) {
                withAnimation(.easeInOut(duration: 0.2)) {
                    selectedSide = "long"
                }
            }
            
            SideTab(
                title: "SHORT",
                icon: "arrow.down.circle.fill",
                color: .lyxenRed,
                isSelected: selectedSide == "short"
            ) {
                withAnimation(.easeInOut(duration: 0.2)) {
                    selectedSide = "short"
                }
            }
        }
        .background(Color.lyxenSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Settings Card
    private func settingsCard(for settings: Binding<SideSettings>, side: String) -> some View {
        VStack(spacing: 20) {
            // Enable Toggle
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("enable_\(side)".localized)
                        .font(.headline)
                    Text(selectedStrategy.description)
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                }
                Spacer()
                Toggle("", isOn: settings.enabled)
                    .labelsHidden()
                    .tint(side == "long" ? .lyxenGreen : .lyxenRed)
            }
            .padding()
            .background(Color.lyxenCard)
            .cornerRadius(12)
            
            // Main Parameters
            VStack(spacing: 16) {
                StrategySettingsRow(label: "entry_percent".localized, value: settings.percent, range: 0.1...100, step: 0.1, suffix: "%")
                StrategySettingsRow(label: "take_profit".localized, value: settings.tpPercent, range: 0.1...100, step: 0.1, suffix: "%")
                StrategySettingsRow(label: "stop_loss".localized, value: settings.slPercent, range: 0.1...50, step: 0.1, suffix: "%")
                LeverageRow(label: "leverage".localized, value: settings.leverage)
                
                // Order Type
                HStack {
                    Text("order_type".localized)
                        .foregroundColor(.lyxenTextSecondary)
                    Spacer()
                    Picker("", selection: settings.orderType) {
                        Text("Market").tag("market")
                        Text("Limit").tag("limit")
                    }
                    .pickerStyle(.segmented)
                    .frame(width: 150)
                }
            }
            .padding()
            .background(Color.lyxenCard)
            .cornerRadius(12)
            
            // ATR Section
            if selectedStrategy.supportsAtr {
                atrSection(for: settings)
            }
            
            // DCA Section
            if selectedStrategy.supportsDca {
                dcaSection(for: settings)
            }
        }
        .transition(.opacity.combined(with: .scale(scale: 0.98)))
    }
    
    // MARK: - ATR Section
    private func atrSection(for settings: Binding<SideSettings>) -> some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: "waveform.path.ecg")
                    .foregroundColor(.lyxenAccent)
                Text("atr_trailing".localized)
                    .font(.headline)
                Spacer()
                Toggle("", isOn: settings.useAtr)
                    .labelsHidden()
                    .tint(.lyxenAccent)
            }
            
            if settings.wrappedValue.useAtr {
                VStack(spacing: 12) {
                    StrategySettingsRow(label: "atr_trigger".localized, value: Binding(
                        get: { settings.wrappedValue.atrTriggerPct ?? 0.5 },
                        set: { settings.wrappedValue.atrTriggerPct = $0 }
                    ), range: 0.1...10, step: 0.1, suffix: "%")
                    
                    StrategySettingsRow(label: "atr_step".localized, value: Binding(
                        get: { settings.wrappedValue.atrStepPct ?? 0.25 },
                        set: { settings.wrappedValue.atrStepPct = $0 }
                    ), range: 0.1...5, step: 0.05, suffix: "%")
                }
                .transition(.opacity)
            }
        }
        .padding()
        .background(Color.lyxenCard)
        .cornerRadius(12)
    }
    
    // MARK: - DCA Section
    private func dcaSection(for settings: Binding<SideSettings>) -> some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: "plus.circle.fill")
                    .foregroundColor(.lyxenOrange)
                Text("dca_settings".localized)
                    .font(.headline)
                Spacer()
                Toggle("", isOn: settings.dcaEnabled)
                    .labelsHidden()
                    .tint(.lyxenOrange)
            }
            
            if settings.wrappedValue.dcaEnabled {
                VStack(spacing: 12) {
                    StrategySettingsRow(label: "dca_level_1".localized, value: settings.dcaPct1, range: 1...50, step: 1, suffix: "%")
                    StrategySettingsRow(label: "dca_level_2".localized, value: settings.dcaPct2, range: 5...100, step: 1, suffix: "%")
                }
                .transition(.opacity)
            }
        }
        .padding()
        .background(Color.lyxenCard)
        .cornerRadius(12)
    }
    
    // MARK: - Save Button
    private var saveButton: some View {
        Button(action: saveSettings) {
            HStack {
                if isSaving {
                    ProgressView()
                        .tint(.white)
                        .padding(.trailing, 8)
                }
                Text("save_settings".localized)
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(LinearGradient(colors: [.lyxenPrimary, .lyxenSecondary], startPoint: .leading, endPoint: .trailing))
            .foregroundColor(.white)
            .cornerRadius(16)
        }
        .disabled(isSaving)
    }
    
    // MARK: - Load Settings
    private func loadSettings() async {
        isLoading = true
        defer { isLoading = false }
        
        let exchange = appState.currentExchange.rawValue
        let accountType = appState.currentAccountType.rawValue
        
        do {
            let settings: [StrategySideSettings] = try await NetworkService.shared.get(
                "/users/strategy-settings/mobile",
                params: [
                    "strategy": selectedStrategy.id,
                    "exchange": exchange,
                    "account_type": accountType
                ]
            )
            
            for setting in settings {
                if setting.side == "long" {
                    longSettings = SideSettings(
                        enabled: setting.enabled,
                        percent: setting.percent,
                        tpPercent: setting.tpPercent,
                        slPercent: setting.slPercent,
                        leverage: setting.leverage,
                        useAtr: setting.useAtr,
                        atrTriggerPct: setting.atrTriggerPct,
                        atrStepPct: setting.atrStepPct,
                        dcaEnabled: setting.dcaEnabled,
                        dcaPct1: setting.dcaPct1,
                        dcaPct2: setting.dcaPct2,
                        orderType: setting.orderType
                    )
                } else if setting.side == "short" {
                    shortSettings = SideSettings(
                        enabled: setting.enabled,
                        percent: setting.percent,
                        tpPercent: setting.tpPercent,
                        slPercent: setting.slPercent,
                        leverage: setting.leverage,
                        useAtr: setting.useAtr,
                        atrTriggerPct: setting.atrTriggerPct,
                        atrStepPct: setting.atrStepPct,
                        dcaEnabled: setting.dcaEnabled,
                        dcaPct1: setting.dcaPct1,
                        dcaPct2: setting.dcaPct2,
                        orderType: setting.orderType
                    )
                }
            }
        } catch {
            print("Failed to load strategy settings: \(error)")
        }
    }
    
    // MARK: - Save Settings
    private func saveSettings() {
        Task {
            isSaving = true
            defer { isSaving = false }
            
            let exchange = appState.currentExchange.rawValue
            let accountType = appState.currentAccountType.rawValue
            
            // Save both sides
            for (side, settings) in [("long", longSettings), ("short", shortSettings)] {
                do {
                    let request = StrategySettingsUpdateRequest(
                        side: side,
                        exchange: exchange,
                        accountType: accountType,
                        enabled: settings.enabled,
                        percent: settings.percent,
                        tpPercent: settings.tpPercent,
                        slPercent: settings.slPercent,
                        leverage: settings.leverage,
                        useAtr: settings.useAtr,
                        atrTriggerPct: settings.atrTriggerPct ?? 0.5,
                        atrStepPct: settings.atrStepPct ?? 0.25,
                        dcaEnabled: settings.dcaEnabled,
                        dcaPct1: settings.dcaPct1,
                        dcaPct2: settings.dcaPct2,
                        orderType: settings.orderType
                    )
                    
                    let _: EmptyResponse = try await NetworkService.shared.put(
                        "/users/strategy-settings/mobile/\(selectedStrategy.id)",
                        body: request
                    )
                } catch {
                    print("Failed to save \(side) settings: \(error)")
                    AppState.shared.showError(error.localizedDescription)
                    return
                }
            }
            
            showSaveSuccess = true
        }
    }
}

// MARK: - API Response Model
struct StrategySideSettings: Codable {
    let strategy: String
    let side: String
    let exchange: String
    let accountType: String
    let enabled: Bool
    let percent: Double
    let tpPercent: Double
    let slPercent: Double
    let leverage: Int
    let useAtr: Bool
    let atrTriggerPct: Double?
    let atrStepPct: Double?
    let dcaEnabled: Bool
    let dcaPct1: Double
    let dcaPct2: Double
    let orderType: String
    
    enum CodingKeys: String, CodingKey {
        case strategy, side, exchange, enabled, percent, leverage
        case accountType = "account_type"
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case useAtr = "use_atr"
        case atrTriggerPct = "atr_trigger_pct"
        case atrStepPct = "atr_step_pct"
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
        case orderType = "order_type"
    }
}

// MARK: - Supporting Views

struct StrategyChip: View {
    let strategy: StrategyInfo
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Image(systemName: strategy.icon)
                    .font(.system(size: 14, weight: .semibold))
                Text(strategy.name)
                    .font(.system(size: 14, weight: .medium))
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(isSelected ? strategy.color.opacity(0.2) : Color.lyxenCard)
            .foregroundColor(isSelected ? strategy.color : .lyxenTextSecondary)
            .cornerRadius(20)
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(isSelected ? strategy.color : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(.plain)
    }
}

struct SideTab: View {
    let title: String
    let icon: String
    let color: Color
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(isSelected ? color.opacity(0.15) : Color.clear)
            .foregroundColor(isSelected ? color : .lyxenTextSecondary)
        }
        .buttonStyle(.plain)
    }
}

struct StrategySettingsRow: View {
    let label: String
    @Binding var value: Double
    let range: ClosedRange<Double>
    let step: Double
    let suffix: String
    
    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.lyxenTextSecondary)
            Spacer()
            HStack(spacing: 12) {
                Button(action: { if value > range.lowerBound { value -= step }}) {
                    Image(systemName: "minus.circle.fill")
                        .foregroundColor(.lyxenTextSecondary)
                }
                Text(String(format: step < 1 ? "%.1f%@" : "%.0f%@", value, suffix))
                    .font(.system(.body, design: .monospaced))
                    .frame(width: 70, alignment: .center)
                Button(action: { if value < range.upperBound { value += step }}) {
                    Image(systemName: "plus.circle.fill")
                        .foregroundColor(.lyxenPrimary)
                }
            }
        }
    }
}

struct LeverageRow: View {
    let label: String
    @Binding var value: Int
    
    let leverages = [1, 2, 3, 5, 10, 20, 25, 50, 75, 100, 125]
    
    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.lyxenTextSecondary)
            Spacer()
            Picker("", selection: $value) {
                ForEach(leverages, id: \.self) { lev in
                    Text("\(lev)x").tag(lev)
                }
            }
            .pickerStyle(.menu)
            .accentColor(.lyxenPrimary)
        }
    }
}

// MARK: - Preview
#Preview {
    NavigationStack {
        StrategySettingsView()
    }
}
