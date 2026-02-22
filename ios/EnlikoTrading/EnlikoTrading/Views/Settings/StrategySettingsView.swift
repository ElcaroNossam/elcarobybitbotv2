//
//  StrategySettingsView.swift
//  EnlikoTrading
//
//  Beautiful dynamic strategy settings with Long/Short support
//  Full feature parity with Telegram bot: BE, Partial TP, ATR, DCA
//

import SwiftUI

// MARK: - Strategy Info
struct StrategyInfo: Identifiable {
    var id: String { code }
    let code: String
    let name: String
    let description: String
    let icon: String
    let color: Color
    let supportsAtr: Bool
    let supportsDca: Bool
    let supportsBE: Bool
    let supportsPartialTP: Bool
    
    static let all: [StrategyInfo] = [
        StrategyInfo(code: "oi", name: "Open Interest", description: "OI divergence signals", icon: "chart.bar.fill", color: .blue, supportsAtr: true, supportsDca: true, supportsBE: true, supportsPartialTP: true),
        StrategyInfo(code: "scryptomera", name: "Scryptomera", description: "Volume delta analysis", icon: "waveform.path.ecg", color: .purple, supportsAtr: true, supportsDca: true, supportsBE: true, supportsPartialTP: true),
        StrategyInfo(code: "scalper", name: "Scalper", description: "Momentum breakouts", icon: "bolt.fill", color: .orange, supportsAtr: true, supportsDca: true, supportsBE: true, supportsPartialTP: true),
        StrategyInfo(code: "elcaro", name: "ENLIKO AI", description: "AI-powered signals", icon: "brain.head.profile", color: .green, supportsAtr: true, supportsDca: true, supportsBE: true, supportsPartialTP: true),
        StrategyInfo(code: "fibonacci", name: "Fibonacci", description: "Fib retracement levels", icon: "ruler.fill", color: .cyan, supportsAtr: true, supportsDca: true, supportsBE: true, supportsPartialTP: true),
        StrategyInfo(code: "rsi_bb", name: "RSI + BB", description: "RSI & Bollinger Bands", icon: "chart.line.uptrend.xyaxis", color: .pink, supportsAtr: true, supportsDca: true, supportsBE: true, supportsPartialTP: true),
        StrategyInfo(code: "manual", name: "Manual Trading", description: "Custom manual trades", icon: "hand.tap.fill", color: .gray, supportsAtr: true, supportsDca: true, supportsBE: true, supportsPartialTP: true)
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
    var atrPeriods: Int?
    var atrMultiplierSl: Double?
    var dcaEnabled: Bool
    var dcaPct1: Double
    var dcaPct2: Double
    var orderType: String
    var maxPositions: Int
    var coinsGroup: String
    var direction: String
    var limitOffsetPct: Double?
    // Break-Even
    var beEnabled: Bool
    var beTriggerPct: Double
    // Partial Take Profit (2-step)
    var partialTpEnabled: Bool
    var partialTp1TriggerPct: Double
    var partialTp1ClosePct: Double
    var partialTp2TriggerPct: Double
    var partialTp2ClosePct: Double
    
    enum CodingKeys: String, CodingKey {
        case enabled, percent, leverage
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case useAtr = "use_atr"
        case atrTriggerPct = "atr_trigger_pct"
        case atrStepPct = "atr_step_pct"
        case atrPeriods = "atr_periods"
        case atrMultiplierSl = "atr_multiplier_sl"
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
        case orderType = "order_type"
        case maxPositions = "max_positions"
        case coinsGroup = "coins_group"
        case direction
        case limitOffsetPct = "limit_offset_pct"
        case beEnabled = "be_enabled"
        case beTriggerPct = "be_trigger_pct"
        case partialTpEnabled = "partial_tp_enabled"
        case partialTp1TriggerPct = "partial_tp_1_trigger_pct"
        case partialTp1ClosePct = "partial_tp_1_close_pct"
        case partialTp2TriggerPct = "partial_tp_2_trigger_pct"
        case partialTp2ClosePct = "partial_tp_2_close_pct"
    }
    
    static var `default`: SideSettings {
        SideSettings(
            enabled: true,
            percent: 1.0,
            tpPercent: 25.0,
            slPercent: 30.0,
            leverage: 10,
            useAtr: true,
            atrTriggerPct: 3.0,
            atrStepPct: 0.5,
            atrPeriods: 7,
            atrMultiplierSl: 0.5,
            dcaEnabled: false,
            dcaPct1: 10.0,
            dcaPct2: 25.0,
            orderType: "market",
            maxPositions: 0,
            coinsGroup: "ALL",
            direction: "all",
            limitOffsetPct: 0.1,
            beEnabled: false,
            beTriggerPct: 1.0,
            partialTpEnabled: false,
            partialTp1TriggerPct: 2.0,
            partialTp1ClosePct: 30.0,
            partialTp2TriggerPct: 5.0,
            partialTp2ClosePct: 30.0
        )
    }
}

// StrategySettingsUpdateRequest is defined in Models.swift

// MARK: - Main View
struct StrategySettingsView: View {
    @ObservedObject var appState = AppState.shared
    @ObservedObject var localization = LocalizationManager.shared
    @ObservedObject private var strategyService = StrategyService.shared
    
    @State private var selectedStrategy: StrategyInfo
    @State private var selectedSide: String = "long"
    
    @State private var longSettings: SideSettings = .default
    @State private var shortSettings: SideSettings = .default
    
    @State private var isLoading = false
    @State private var isSaving = false
    @State private var showSaveSuccess = false
    @State private var ptpValidationError: String? = nil
    @State private var animateChange = false
    
    init(initialStrategy: String? = nil) {
        if let name = initialStrategy,
           let found = StrategyInfo.all.first(where: { $0.code == name }) {
            _selectedStrategy = State(wrappedValue: found)
        } else {
            _selectedStrategy = State(wrappedValue: StrategyInfo.all[0])
        }
    }
    
    var currentSettings: Binding<SideSettings> {
        selectedSide == "long" ? $longSettings : $shortSettings
    }
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            if isLoading {
                loadingView
            } else {
                ScrollView {
                    VStack(spacing: 20) {
                        // Strategy Picker
                        strategyPicker
                        
                        // Exchange Info Bar
                        exchangeInfoBar
                        
                        // Side Selector (Long/Short)
                        sidePicker
                        
                        // Settings Content
                        settingsContent
                            .id(selectedSide + selectedStrategy.code)
                        
                        // Save Button
                        saveButton
                    }
                    .padding()
                }
            }
        }
        .navigationTitle("strategy_settings".localized)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await loadSettings()
        }
        .onChange(of: appState.currentExchange) { _, _ in
            Task { await loadSettings() }
        }
        .onChange(of: appState.currentAccountType) { _, _ in
            Task { await loadSettings() }
        }
        .alert("settings_saved".localized, isPresented: $showSaveSuccess) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("strategy_settings_saved_message".localized)
        }
        .alert("⚠️ Validation Error", isPresented: Binding(
            get: { ptpValidationError != nil },
            set: { if !$0 { ptpValidationError = nil } }
        )) {
            Button("OK", role: .cancel) { ptpValidationError = nil }
        } message: {
            Text(ptpValidationError ?? "")
        }
    }
    
    // MARK: - Loading View
    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
            Text("loading".localized)
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
        }
    }
    
    // MARK: - Exchange Info Bar
    private var exchangeInfoBar: some View {
        HStack {
            HStack(spacing: 8) {
                Circle()
                    .fill(appState.currentExchange == .bybit ? Color.orange : Color.blue)
                    .frame(width: 8, height: 8)
                Text(appState.currentExchange.displayName)
                    .font(.caption.weight(.medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            Text(appState.currentAccountType.displayName)
                .font(.caption.weight(.medium))
                .foregroundColor(appState.currentAccountType.rawValue.contains("demo") || appState.currentAccountType.rawValue.contains("testnet") ? .yellow : .green)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.enlikoCard)
                .cornerRadius(6)
        }
        .padding(.horizontal, 4)
    }
    
    // MARK: - Strategy Picker
    private var strategyPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(StrategyInfo.all) { strategy in
                    StrategyChip(
                        strategy: strategy,
                        isSelected: selectedStrategy.code == strategy.code
                    ) {
                        withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                            selectedStrategy = strategy
                            animateChange = true
                        }
                        Task { await loadSettings() }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            animateChange = false
                        }
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
                color: .enlikoGreen,
                isSelected: selectedSide == "long",
                isEnabled: longSettings.enabled
            ) {
                withAnimation(.easeInOut(duration: 0.2)) {
                    selectedSide = "long"
                }
            }
            
            SideTab(
                title: "SHORT",
                icon: "arrow.down.circle.fill",
                color: .enlikoRed,
                isSelected: selectedSide == "short",
                isEnabled: shortSettings.enabled
            ) {
                withAnimation(.easeInOut(duration: 0.2)) {
                    selectedSide = "short"
                }
            }
        }
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Settings Content
    private var settingsContent: some View {
        VStack(spacing: 16) {
            // Enable Toggle Card
            enableToggleCard
            
            // Main Parameters
            mainParametersCard
            
            // ATR Section
            if selectedStrategy.supportsAtr {
                atrSection
            }
            
            // Break-Even Section
            if selectedStrategy.supportsBE {
                breakEvenSection
            }
            
            // Partial Take Profit Section
            if selectedStrategy.supportsPartialTP {
                partialTPSection
            }
            
            // DCA Section
            if selectedStrategy.supportsDca {
                dcaSection
            }
        }
        .transition(.asymmetric(
            insertion: .opacity.combined(with: .move(edge: .trailing)),
            removal: .opacity.combined(with: .move(edge: .leading))
        ))
    }
    
    // MARK: - Enable Toggle Card
    private var enableToggleCard: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 8) {
                    Image(systemName: selectedStrategy.icon)
                        .foregroundColor(selectedStrategy.color)
                    Text(selectedSide == "long" ? "enable_long".localized : "enable_short".localized)
                        .font(.headline)
                }
                Text(selectedStrategy.description)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            Spacer()
            Toggle("", isOn: currentSettings.enabled)
                .labelsHidden()
                .tint(selectedSide == "long" ? .enlikoGreen : .enlikoRed)
                .scaleEffect(1.1)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.enlikoCard)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(
                            currentSettings.wrappedValue.enabled 
                                ? (selectedSide == "long" ? Color.enlikoGreen : Color.enlikoRed).opacity(0.5) 
                                : Color.clear,
                            lineWidth: 2
                        )
                )
        )
    }
    
    // MARK: - Main Parameters Card
    private var mainParametersCard: some View {
        VStack(spacing: 16) {
            SectionHeader(title: "main_parameters".localized, icon: "slider.horizontal.3")
            
            AnimatedSettingsRow(
                label: "entry_percent".localized, 
                value: currentSettings.percent, 
                range: 0.1...10, 
                step: 0.1, 
                suffix: "%",
                color: .enlikoPrimary
            )
            
            AnimatedSettingsRow(
                label: "take_profit".localized, 
                value: currentSettings.tpPercent, 
                range: 0.1...100, 
                step: 0.5, 
                suffix: "%",
                color: .enlikoGreen
            )
            
            AnimatedSettingsRow(
                label: "stop_loss".localized, 
                value: currentSettings.slPercent, 
                range: 0.1...100, 
                step: 0.1, 
                suffix: "%",
                color: .enlikoRed
            )
            
            // Max Positions
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("max_positions".localized)
                        .foregroundColor(.enlikoTextSecondary)
                    Text("0 = unlimited")
                        .font(.caption2)
                        .foregroundColor(.enlikoTextMuted)
                }
                Spacer()
                Stepper("\(currentSettings.wrappedValue.maxPositions)", value: currentSettings.maxPositions, in: 0...20)
                    .frame(width: 120)
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    // MARK: - ATR Section
    private var atrSection: some View {
        ExpandableSettingsCard(
            title: "atr_trailing".localized,
            icon: "waveform.path.ecg",
            color: .enlikoAccent,
            isEnabled: currentSettings.useAtr
        ) {
            VStack(spacing: 12) {
                AnimatedSettingsRow(
                    label: "atr_trigger".localized,
                    value: Binding(
                        get: { currentSettings.wrappedValue.atrTriggerPct ?? 3.0 },
                        set: { currentSettings.wrappedValue.atrTriggerPct = $0 }
                    ),
                    range: 0.1...10,
                    step: 0.1,
                    suffix: "%",
                    color: .enlikoAccent
                )
                
                AnimatedSettingsRow(
                    label: "atr_step".localized,
                    value: Binding(
                        get: { currentSettings.wrappedValue.atrStepPct ?? 0.5 },
                        set: { currentSettings.wrappedValue.atrStepPct = $0 }
                    ),
                    range: 0.1...5,
                    step: 0.05,
                    suffix: "%",
                    color: .enlikoAccent
                )
            }
        }
    }
    
    // MARK: - Break-Even Section
    private var breakEvenSection: some View {
        ExpandableSettingsCard(
            title: "break_even".localized,
            icon: "equal.circle.fill",
            color: .yellow,
            isEnabled: currentSettings.beEnabled
        ) {
            VStack(spacing: 12) {
                HStack {
                    Image(systemName: "info.circle")
                        .foregroundColor(.yellow)
                    Text("be_info".localized)
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                }
                .padding(.bottom, 4)
                
                AnimatedSettingsRow(
                    label: "be_trigger".localized,
                    value: currentSettings.beTriggerPct,
                    range: 0.1...10,
                    step: 0.1,
                    suffix: "%",
                    color: .yellow
                )
            }
        }
    }
    
    // MARK: - Partial Take Profit Section
    private var partialTPSection: some View {
        ExpandableSettingsCard(
            title: "partial_tp".localized,
            icon: "chart.pie.fill",
            color: .cyan,
            isEnabled: currentSettings.partialTpEnabled
        ) {
            VStack(spacing: 16) {
                HStack {
                    Image(systemName: "info.circle")
                        .foregroundColor(.cyan)
                    Text("partial_tp_info".localized)
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                }
                
                // Step 1
                VStack(alignment: .leading, spacing: 8) {
                    Text("Step 1")
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.cyan)
                    
                    HStack(spacing: 16) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("@ profit")
                                .font(.caption2)
                                .foregroundColor(.enlikoTextMuted)
                            StepperField(value: currentSettings.partialTp1TriggerPct, range: 0.5...20, step: 0.5, suffix: "%")
                        }
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Close %")
                                .font(.caption2)
                                .foregroundColor(.enlikoTextMuted)
                            StepperField(value: currentSettings.partialTp1ClosePct, range: 10...90, step: 5, suffix: "%")
                        }
                    }
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(10)
                
                // Step 2
                VStack(alignment: .leading, spacing: 8) {
                    Text("Step 2")
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.cyan)
                    
                    HStack(spacing: 16) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("@ profit")
                                .font(.caption2)
                                .foregroundColor(.enlikoTextMuted)
                            StepperField(value: currentSettings.partialTp2TriggerPct, range: 1...30, step: 0.5, suffix: "%")
                        }
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Close %")
                                .font(.caption2)
                                .foregroundColor(.enlikoTextMuted)
                            StepperField(value: currentSettings.partialTp2ClosePct, range: 10...100, step: 5, suffix: "%")
                        }
                    }
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(10)
            }
        }
    }
    
    // MARK: - DCA Section
    private var dcaSection: some View {
        ExpandableSettingsCard(
            title: "dca_settings".localized,
            icon: "plus.circle.fill",
            color: .enlikoOrange,
            isEnabled: currentSettings.dcaEnabled
        ) {
            VStack(spacing: 12) {
                AnimatedSettingsRow(
                    label: "dca_level_1".localized,
                    value: currentSettings.dcaPct1,
                    range: 1...50,
                    step: 1,
                    suffix: "%",
                    color: .enlikoOrange
                )
                
                AnimatedSettingsRow(
                    label: "dca_level_2".localized,
                    value: currentSettings.dcaPct2,
                    range: 5...100,
                    step: 1,
                    suffix: "%",
                    color: .enlikoOrange
                )
            }
        }
    }
    
    // MARK: - Save Button
    private var saveButton: some View {
        Button(action: saveSettings) {
            HStack(spacing: 12) {
                if isSaving {
                    ProgressView()
                        .tint(.white)
                } else {
                    Image(systemName: "checkmark.circle.fill")
                }
                Text("save_settings".localized)
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 56)
            .background(
                LinearGradient(
                    colors: [.enlikoPrimary, .enlikoSecondary],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .foregroundColor(.white)
            .cornerRadius(16)
            .shadow(color: .enlikoPrimary.opacity(0.3), radius: 10, y: 5)
        }
        .disabled(isSaving)
        .padding(.top, 8)
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
                    "strategy": selectedStrategy.code,
                    "exchange": exchange,
                    "account_type": accountType
                ]
            )
            
            for setting in settings {
                let sideSettings = SideSettings(
                    enabled: setting.enabled ?? true,
                    percent: setting.percent ?? 1.0,
                    tpPercent: setting.tpPercent ?? 25.0,
                    slPercent: setting.slPercent ?? 30.0,
                    leverage: setting.leverage ?? 10,
                    useAtr: setting.useAtr ?? true,
                    atrTriggerPct: setting.atrTriggerPct ?? 3.0,
                    atrStepPct: setting.atrStepPct ?? 0.5,
                    atrPeriods: setting.atrPeriods ?? 7,
                    atrMultiplierSl: setting.atrMultiplierSl ?? 0.5,
                    dcaEnabled: setting.dcaEnabled ?? false,
                    dcaPct1: setting.dcaPct1 ?? 10.0,
                    dcaPct2: setting.dcaPct2 ?? 25.0,
                    orderType: setting.orderType ?? "market",
                    maxPositions: setting.maxPositions ?? 0,
                    coinsGroup: setting.coinsGroup ?? "ALL",
                    direction: setting.direction ?? "all",
                    limitOffsetPct: setting.limitOffsetPct ?? 0.1,
                    beEnabled: setting.beEnabled ?? false,
                    beTriggerPct: setting.beTriggerPct ?? 1.0,
                    partialTpEnabled: setting.partialTpEnabled ?? false,
                    partialTp1TriggerPct: setting.partialTp1TriggerPct ?? 2.0,
                    partialTp1ClosePct: setting.partialTp1ClosePct ?? 30.0,
                    partialTp2TriggerPct: setting.partialTp2TriggerPct ?? 5.0,
                    partialTp2ClosePct: setting.partialTp2ClosePct ?? 30.0
                )
                
                if setting.side == "long" {
                    longSettings = sideSettings
                } else {
                    shortSettings = sideSettings
                }
            }
        } catch {
            AppLogger.shared.error("Failed to load strategy settings: \(error)", category: .network)
        }
    }
    
    // MARK: - Save Settings
    private func saveSettings() {
        // Validate PTP Step1 + Step2 <= 100% for both sides
        for (side, settings) in [("Long", longSettings), ("Short", shortSettings)] {
            if settings.partialTpEnabled {
                let step1 = settings.partialTp1ClosePct
                let step2 = settings.partialTp2ClosePct
                if step1 + step2 > 100.0 {
                    ptpValidationError = "\(side): PTP Step1 (\(Int(step1))%) + Step2 (\(Int(step2))%) = \(Int(step1 + step2))% > 100%"
                    return
                }
            }
        }
        ptpValidationError = nil
        
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
                        atrTriggerPct: settings.atrTriggerPct ?? 3.0,
                        atrStepPct: settings.atrStepPct ?? 0.5,
                        atrPeriods: settings.atrPeriods ?? 7,
                        atrMultiplierSl: settings.atrMultiplierSl ?? 0.5,
                        dcaEnabled: settings.dcaEnabled,
                        dcaPct1: settings.dcaPct1,
                        dcaPct2: settings.dcaPct2,
                        orderType: settings.orderType,
                        limitOffsetPct: settings.limitOffsetPct ?? 0.1,
                        direction: settings.direction,
                        maxPositions: settings.maxPositions,
                        coinsGroup: settings.coinsGroup,
                        beEnabled: settings.beEnabled,
                        beTriggerPct: settings.beTriggerPct,
                        partialTpEnabled: settings.partialTpEnabled,
                        partialTp1TriggerPct: settings.partialTp1TriggerPct,
                        partialTp1ClosePct: settings.partialTp1ClosePct,
                        partialTp2TriggerPct: settings.partialTp2TriggerPct,
                        partialTp2ClosePct: settings.partialTp2ClosePct
                    )
                    
                    let _: EmptyResponse = try await NetworkService.shared.put(
                        "/users/strategy-settings/mobile/\(selectedStrategy.code)",
                        body: request
                    )
                } catch {
                    AppLogger.shared.error("Failed to save \(side) settings: \(error)", category: .network)
                    AppState.shared.showError(error.localizedDescription)
                    return
                }
            }
            
            // Haptic feedback
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(.success)
            
            showSaveSuccess = true
        }
    }
}

// MARK: - API Response Model
struct StrategySideSettings: Codable {
    let strategy: String?
    let side: String?
    let exchange: String?
    let accountType: String?
    let enabled: Bool?
    let percent: Double?
    let tpPercent: Double?
    let slPercent: Double?
    let leverage: Int?
    let useAtr: Bool?
    let atrTriggerPct: Double?
    let atrStepPct: Double?
    let atrPeriods: Int?
    let atrMultiplierSl: Double?
    let dcaEnabled: Bool?
    let dcaPct1: Double?
    let dcaPct2: Double?
    let orderType: String?
    let maxPositions: Int?
    let coinsGroup: String?
    let direction: String?
    let limitOffsetPct: Double?
    // Break-Even
    let beEnabled: Bool?
    let beTriggerPct: Double?
    // Partial Take Profit
    let partialTpEnabled: Bool?
    let partialTp1TriggerPct: Double?
    let partialTp1ClosePct: Double?
    let partialTp2TriggerPct: Double?
    let partialTp2ClosePct: Double?
    
    // Safe accessors with defaults
    var strategyValue: String { strategy ?? "" }
    var sideValue: String { side ?? "long" }
    var exchangeValue: String { exchange ?? "bybit" }
    var accountTypeValue: String { accountType ?? "demo" }
    var isEnabled: Bool { enabled ?? true }
    var percentValue: Double { percent ?? 1.0 }
    var tpPercentValue: Double { tpPercent ?? 25.0 }
    var slPercentValue: Double { slPercent ?? 30.0 }
    var leverageValue: Int { leverage ?? 10 }
    var isAtrEnabled: Bool { useAtr ?? true }
    var isDcaEnabled: Bool { dcaEnabled ?? false }
    var dcaPct1Value: Double { dcaPct1 ?? 10.0 }
    var dcaPct2Value: Double { dcaPct2 ?? 25.0 }
    var orderTypeValue: String { orderType ?? "market" }
    var isBeEnabled: Bool { beEnabled ?? false }
    var beTriggerPctValue: Double { beTriggerPct ?? 1.0 }
    var isPtpEnabled: Bool { partialTpEnabled ?? false }
    var ptp1TriggerValue: Double { partialTp1TriggerPct ?? 2.0 }
    var ptp1CloseValue: Double { partialTp1ClosePct ?? 30.0 }
    var ptp2TriggerValue: Double { partialTp2TriggerPct ?? 5.0 }
    var ptp2CloseValue: Double { partialTp2ClosePct ?? 30.0 }
    
    enum CodingKeys: String, CodingKey {
        case strategy, side, exchange, enabled, percent, leverage, direction
        case accountType = "account_type"
        case tpPercent = "tp_percent"
        case slPercent = "sl_percent"
        case useAtr = "use_atr"
        case atrTriggerPct = "atr_trigger_pct"
        case atrStepPct = "atr_step_pct"
        case atrPeriods = "atr_periods"
        case atrMultiplierSl = "atr_multiplier_sl"
        case dcaEnabled = "dca_enabled"
        case dcaPct1 = "dca_pct_1"
        case dcaPct2 = "dca_pct_2"
        case orderType = "order_type"
        case maxPositions = "max_positions"
        case coinsGroup = "coins_group"
        case limitOffsetPct = "limit_offset_pct"
        case beEnabled = "be_enabled"
        case beTriggerPct = "be_trigger_pct"
        case partialTpEnabled = "partial_tp_enabled"
        case partialTp1TriggerPct = "partial_tp_1_trigger_pct"
        case partialTp1ClosePct = "partial_tp_1_close_pct"
        case partialTp2TriggerPct = "partial_tp_2_trigger_pct"
        case partialTp2ClosePct = "partial_tp_2_close_pct"
    }
}

// MARK: - Supporting Views

struct SectionHeader: View {
    let title: String
    let icon: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.enlikoPrimary)
            Text(title)
                .font(.headline)
                .foregroundColor(.white)
            Spacer()
        }
    }
}

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
            .background(isSelected ? strategy.color.opacity(0.2) : Color.enlikoCard)
            .foregroundColor(isSelected ? strategy.color : .enlikoTextSecondary)
            .cornerRadius(20)
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(isSelected ? strategy.color : Color.clear, lineWidth: 2)
            )
            .scaleEffect(isSelected ? 1.05 : 1.0)
        }
        .buttonStyle(.plain)
        .animation(.spring(response: 0.3), value: isSelected)
    }
}

struct SideTab: View {
    let title: String
    let icon: String
    let color: Color
    let isSelected: Bool
    let isEnabled: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                Text(title)
                    .fontWeight(.semibold)
                if !isEnabled {
                    Image(systemName: "moon.zzz.fill")
                        .font(.caption2)
                        .foregroundColor(.enlikoTextMuted)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(isSelected ? color.opacity(0.15) : Color.clear)
            .foregroundColor(isSelected ? color : .enlikoTextSecondary)
        }
        .buttonStyle(.plain)
    }
}

struct AnimatedSettingsRow: View {
    let label: String
    @Binding var value: Double
    let range: ClosedRange<Double>
    let step: Double
    let suffix: String
    let color: Color
    
    @State private var isEditing = false
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text(label)
                    .foregroundColor(.enlikoTextSecondary)
                Spacer()
                Text(String(format: step < 1 ? "%.1f%@" : "%.0f%@", value, suffix))
                    .font(.system(.body, design: .monospaced).weight(.semibold))
                    .foregroundColor(color)
                    .scaleEffect(isEditing ? 1.1 : 1.0)
            }
            
            HStack(spacing: 16) {
                Button(action: {
                    if value > range.lowerBound {
                        withAnimation(.spring(response: 0.2)) {
                            value = max(range.lowerBound, value - step)
                            isEditing = true
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                            isEditing = false
                        }
                    }
                }) {
                    Image(systemName: "minus.circle.fill")
                        .font(.title2)
                        .foregroundColor(value > range.lowerBound ? color : .enlikoTextMuted)
                }
                
                Slider(value: $value, in: range, step: step) { editing in
                    isEditing = editing
                }
                .tint(color)
                
                Button(action: {
                    if value < range.upperBound {
                        withAnimation(.spring(response: 0.2)) {
                            value = min(range.upperBound, value + step)
                            isEditing = true
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                            isEditing = false
                        }
                    }
                }) {
                    Image(systemName: "plus.circle.fill")
                        .font(.title2)
                        .foregroundColor(value < range.upperBound ? color : .enlikoTextMuted)
                }
            }
        }
    }
}

struct ExpandableSettingsCard<Content: View>: View {
    let title: String
    let icon: String
    let color: Color
    @Binding var isEnabled: Bool
    @ViewBuilder let content: () -> Content
    
    var body: some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.headline)
                Spacer()
                Toggle("", isOn: $isEnabled)
                    .labelsHidden()
                    .tint(color)
            }
            
            if isEnabled {
                content()
                    .transition(.opacity.combined(with: .scale(scale: 0.95)))
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(isEnabled ? color.opacity(0.3) : Color.clear, lineWidth: 1)
        )
        .animation(.spring(response: 0.3), value: isEnabled)
    }
}

struct StepperField: View {
    @Binding var value: Double
    let range: ClosedRange<Double>
    let step: Double
    let suffix: String
    
    var body: some View {
        HStack(spacing: 8) {
            Button(action: {
                if value > range.lowerBound {
                    value -= step
                }
            }) {
                Image(systemName: "minus.circle.fill")
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Text(String(format: step < 1 ? "%.1f%@" : "%.0f%@", value, suffix))
                .font(.system(.caption, design: .monospaced).weight(.medium))
                .foregroundColor(.white)
                .frame(width: 50)
            
            Button(action: {
                if value < range.upperBound {
                    value += step
                }
            }) {
                Image(systemName: "plus.circle.fill")
                    .foregroundColor(.enlikoPrimary)
            }
        }
    }
}

// MARK: - Preview
#Preview {
    NavigationStack {
        StrategySettingsView()
    }
}
