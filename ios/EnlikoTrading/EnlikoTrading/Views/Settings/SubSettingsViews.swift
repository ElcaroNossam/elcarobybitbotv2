//
//  SubSettingsViews.swift
//  EnlikoTrading
//
//  Additional settings screens
//

import SwiftUI

// MARK: - Exchange Settings View
struct ExchangeSettingsView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            List {
                Section {
                    ForEach(Exchange.allCases, id: \.self) { exchange in
                        Button(action: { 
                            appState.switchExchange(to: exchange)
                            dismiss()
                        }) {
                            HStack {
                                Text(exchange.icon)
                                    .font(.title2)
                                
                                VStack(alignment: .leading) {
                                    Text(exchange.displayName)
                                        .foregroundColor(.white)
                                    Text(exchange == .bybit ? "Demo & Real accounts" : "Testnet & Mainnet")
                                        .font(.caption)
                                        .foregroundColor(.enlikoTextSecondary)
                                }
                                
                                Spacer()
                                
                                if appState.currentExchange == exchange {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.enlikoPrimary)
                                }
                            }
                        }
                    }
                } header: {
                    Text("Select Exchange")
                }
                .listRowBackground(Color.enlikoCard)
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
        }
        .navigationTitle("Exchange")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Leverage Settings View
struct LeverageSettingsView: View {
    @State private var selectedLeverage: Double = 10
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            VStack(spacing: 24) {
                // Current Leverage
                VStack(spacing: 8) {
                    Text("Default Leverage")
                        .font(.headline)
                        .foregroundColor(.enlikoTextSecondary)
                    
                    Text("\(Int(selectedLeverage))x")
                        .font(.system(size: 48, weight: .bold, design: .rounded))
                        .foregroundColor(.enlikoPrimary)
                }
                .padding(.top, 40)
                
                // Slider
                VStack(spacing: 12) {
                    Slider(value: $selectedLeverage, in: 1...100, step: 1)
                        .tint(.enlikoPrimary)
                    
                    HStack {
                        Text("1x")
                        Spacer()
                        Text("25x")
                        Spacer()
                        Text("50x")
                        Spacer()
                        Text("75x")
                        Spacer()
                        Text("100x")
                    }
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                }
                .padding()
                .background(Color.enlikoCard)
                .cornerRadius(12)
                .padding(.horizontal)
                
                // Quick Select Buttons
                HStack(spacing: 12) {
                    ForEach([5, 10, 20, 50], id: \.self) { lev in
                        Button(action: { selectedLeverage = Double(lev) }) {
                            Text("\(lev)x")
                                .font(.headline)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(selectedLeverage == Double(lev) ? Color.enlikoPrimary : Color.enlikoCard)
                                .foregroundColor(selectedLeverage == Double(lev) ? .white : .enlikoTextSecondary)
                                .cornerRadius(10)
                        }
                    }
                }
                .padding(.horizontal)
                
                // Warning
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.enlikoYellow)
                    Text("Higher leverage increases risk of liquidation")
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                }
                .padding()
                .background(Color.enlikoYellow.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)
                
                Spacer()
            }
        }
        .navigationTitle("Leverage")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Risk Settings View
struct RiskSettingsView: View {
    @State private var entryPercent: Double = 1.0
    @State private var takeProfitPercent: Double = 8.0
    @State private var stopLossPercent: Double = 3.0
    @State private var useATR = false
    @State private var dcaEnabled = false
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            List {
                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Entry %")
                            Spacer()
                            Text("\(entryPercent, specifier: "%.1f")%")
                                .foregroundColor(.enlikoPrimary)
                        }
                        Slider(value: $entryPercent, in: 0.1...10, step: 0.1)
                            .tint(.enlikoPrimary)
                    }
                    .padding(.vertical, 4)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Take Profit %")
                            Spacer()
                            Text("\(takeProfitPercent, specifier: "%.1f")%")
                                .foregroundColor(.enlikoGreen)
                        }
                        Slider(value: $takeProfitPercent, in: 1...50, step: 0.5)
                            .tint(.enlikoGreen)
                    }
                    .padding(.vertical, 4)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Stop Loss %")
                            Spacer()
                            Text("\(stopLossPercent, specifier: "%.1f")%")
                                .foregroundColor(.enlikoRed)
                        }
                        Slider(value: $stopLossPercent, in: 0.5...20, step: 0.5)
                            .tint(.enlikoRed)
                    }
                    .padding(.vertical, 4)
                } header: {
                    Text("Position Sizing")
                }
                .listRowBackground(Color.enlikoCard)
                
                Section {
                    Toggle("Use ATR for SL/TP", isOn: $useATR)
                        .tint(.enlikoPrimary)
                    Toggle("Enable DCA", isOn: $dcaEnabled)
                        .tint(.enlikoPrimary)
                } header: {
                    Text("Advanced")
                } footer: {
                    Text("ATR adjusts SL/TP based on market volatility. DCA adds to positions at drawdown levels.")
                }
                .listRowBackground(Color.enlikoCard)
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
        }
        .navigationTitle("Risk Management")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - NotificationSettingsView moved to NotificationSettingsView.swift
// (with full localization and improved UI synced with Android/WebApp)

// MARK: - Appearance Settings View
struct AppearanceSettingsView: View {
    @State private var selectedTheme = "dark"
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            List {
                Section {
                    ForEach(["dark", "light", "system"], id: \.self) { theme in
                        Button(action: { selectedTheme = theme }) {
                            HStack {
                                Image(systemName: themeIcon(theme))
                                    .foregroundColor(.enlikoPrimary)
                                    .frame(width: 28)
                                
                                Text(theme.capitalized)
                                    .foregroundColor(.white)
                                
                                Spacer()
                                
                                if selectedTheme == theme {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.enlikoPrimary)
                                }
                            }
                        }
                    }
                } header: {
                    Text("Theme")
                } footer: {
                    Text("Dark mode is recommended for trading.")
                }
                .listRowBackground(Color.enlikoCard)
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
        }
        .navigationTitle("Appearance")
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private func themeIcon(_ theme: String) -> String {
        switch theme {
        case "dark": return "moon.fill"
        case "light": return "sun.max.fill"
        default: return "gear"
        }
    }
}

// MARK: - About View
struct AboutView: View {
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 24) {
                    // Logo
                    ZStack {
                        Circle()
                            .fill(Color.enlikoGradient)
                            .frame(width: 100, height: 100)
                        
                        Image(systemName: "chart.line.uptrend.xyaxis")
                            .font(.system(size: 44))
                            .foregroundColor(.white)
                    }
                    .padding(.top, 40)
                    
                    VStack(spacing: 8) {
                        Text("ENLIKO")
                            .font(.title.bold())
                            .foregroundColor(.white)
                        
                        Text("Professional Trading Platform")
                            .font(.subheadline)
                            .foregroundColor(.enlikoTextSecondary)
                        
                        Text("Version 1.0.0 (1)")
                            .font(.caption)
                            .foregroundColor(.enlikoTextMuted)
                    }
                    
                    // Links
                    VStack(spacing: 0) {
                        linkRow(icon: "globe", title: "Website", url: "https://enliko.com")
                        Divider().background(Color.enlikoCardHover)
                        linkRow(icon: "envelope", title: "Support", url: "mailto:support@enliko.com")
                        Divider().background(Color.enlikoCardHover)
                        linkRow(icon: "bubble.left", title: "Telegram", url: "https://t.me/enliko_trading")
                    }
                    .background(Color.enlikoCard)
                    .cornerRadius(12)
                    .padding(.horizontal)
                    
                    Text("© 2026 Enliko Trading. All rights reserved.")
                        .font(.caption)
                        .foregroundColor(.enlikoTextMuted)
                        .padding(.top, 20)
                    
                    Spacer()
                }
            }
        }
        .navigationTitle("About")
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private func linkRow(icon: String, title: String, url: String) -> some View {
        Link(destination: URL(string: url)!) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(.enlikoPrimary)
                    .frame(width: 28)
                
                Text(title)
                    .foregroundColor(.white)
                
                Spacer()
                
                Image(systemName: "arrow.up.right")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            .padding()
        }
    }
}

// MARK: - API Keys Sheet
struct APIKeysSheetView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var appState = AppState.shared
    
    @State private var selectedTab = 0
    @State private var isLoading = false
    @State private var isSaving = false
    @State private var showSaveSuccess = false
    @State private var showDeleteConfirm = false
    @State private var keyToDelete: APIKeyType?
    
    // Bybit Keys
    @State private var bybitDemoKey = ""
    @State private var bybitDemoSecret = ""
    @State private var bybitRealKey = ""
    @State private var bybitRealSecret = ""
    
    // HyperLiquid Keys
    @State private var hlTestnetKey = ""
    @State private var hlMainnetKey = ""
    
    // Key Status
    @State private var bybitDemoStatus: APIKeyStatus = .notConfigured
    @State private var bybitRealStatus: APIKeyStatus = .notConfigured
    @State private var hlTestnetStatus: APIKeyStatus = .notConfigured
    @State private var hlMainnetStatus: APIKeyStatus = .notConfigured
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                if isLoading {
                    loadingView
                } else {
                    VStack(spacing: 0) {
                        // Tab Selector
                        exchangeTabPicker
                        
                        ScrollView {
                            if selectedTab == 0 {
                                bybitSection
                            } else {
                                hyperliquidSection
                            }
                        }
                    }
                }
            }
            .navigationTitle("api_keys".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("cancel".localized) { dismiss() }
                        .foregroundColor(.enlikoTextSecondary)
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: saveKeys) {
                        if isSaving {
                            ProgressView()
                                .tint(.enlikoPrimary)
                        } else {
                            Text("save".localized)
                                .fontWeight(.semibold)
                        }
                    }
                    .foregroundColor(.enlikoPrimary)
                    .disabled(isSaving)
                }
            }
            .task {
                await loadKeyStatus()
            }
            .alert("key_deleted".localized, isPresented: $showSaveSuccess) {
                Button("OK", role: .cancel) {}
            }
            .confirmationDialog("delete_key_confirm".localized, isPresented: $showDeleteConfirm, titleVisibility: .visible) {
                Button("delete".localized, role: .destructive) {
                    if let key = keyToDelete {
                        deleteKey(key)
                    }
                }
                Button("cancel".localized, role: .cancel) {}
            }
        }
    }
    
    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
            Text("loading_keys".localized)
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
        }
    }
    
    private var exchangeTabPicker: some View {
        HStack(spacing: 0) {
            ExchangeTab(
                name: "Bybit",
                icon: "chart.bar.fill",
                color: .orange,
                isSelected: selectedTab == 0,
                hasKeys: bybitDemoStatus == .valid || bybitRealStatus == .valid
            ) {
                withAnimation { selectedTab = 0 }
            }
            
            ExchangeTab(
                name: "HyperLiquid",
                icon: "link.circle.fill",
                color: .blue,
                isSelected: selectedTab == 1,
                hasKeys: hlTestnetStatus == .valid || hlMainnetStatus == .valid
            ) {
                withAnimation { selectedTab = 1 }
            }
        }
        .background(Color.enlikoSurface)
        .cornerRadius(16)
        .padding()
    }
    
    // MARK: - Bybit Section
    private var bybitSection: some View {
        VStack(spacing: 20) {
            // Demo Account Card
            APIKeyCard(
                title: "Demo Account",
                subtitle: "Practice trading with testnet",
                icon: "gamecontroller.fill",
                color: .enlikoGreen,
                status: bybitDemoStatus,
                apiKey: $bybitDemoKey,
                apiSecret: $bybitDemoSecret,
                onTest: { await testBybitKey(isDemo: true) },
                onDelete: {
                    keyToDelete = .bybitDemo
                    showDeleteConfirm = true
                }
            )
            
            // Real Account Card
            APIKeyCard(
                title: "Real Account",
                subtitle: "Live trading with real funds",
                icon: "dollarsign.circle.fill",
                color: .enlikoYellow,
                status: bybitRealStatus,
                apiKey: $bybitRealKey,
                apiSecret: $bybitRealSecret,
                onTest: { await testBybitKey(isDemo: false) },
                onDelete: {
                    keyToDelete = .bybitReal
                    showDeleteConfirm = true
                }
            )
            
            // Security Info
            securityInfoCard
        }
        .padding()
    }
    
    // MARK: - HyperLiquid Section
    private var hyperliquidSection: some View {
        VStack(spacing: 20) {
            // Testnet Card
            HLKeyCard(
                title: "Testnet",
                subtitle: "Practice with test funds",
                icon: "testtube.2",
                color: .enlikoGreen,
                status: hlTestnetStatus,
                privateKey: $hlTestnetKey,
                onDelete: {
                    keyToDelete = .hlTestnet
                    showDeleteConfirm = true
                }
            )
            
            // Mainnet Card
            HLKeyCard(
                title: "Mainnet",
                subtitle: "Real funds trading",
                icon: "flame.fill",
                color: .enlikoYellow,
                status: hlMainnetStatus,
                privateKey: $hlMainnetKey,
                onDelete: {
                    keyToDelete = .hlMainnet
                    showDeleteConfirm = true
                }
            )
            
            // Warning Card
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.enlikoYellow)
                    Text("security_warning".localized)
                        .font(.headline)
                }
                
                Text("hl_security_warning".localized)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            .padding()
            .background(Color.enlikoYellow.opacity(0.1))
            .cornerRadius(12)
        }
        .padding()
    }
    
    private var securityInfoCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "shield.checkered")
                    .foregroundColor(.enlikoGreen)
                Text("security_tips".localized)
                    .font(.headline)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                SecurityTip(icon: "checkmark.circle.fill", text: "enable_ip_whitelist".localized)
                SecurityTip(icon: "checkmark.circle.fill", text: "enable_2fa".localized)
                SecurityTip(icon: "checkmark.circle.fill", text: "only_trading_permissions".localized)
                SecurityTip(icon: "xmark.circle.fill", text: "no_withdrawal_permissions".localized, isWarning: true)
            }
        }
        .padding()
        .background(Color.enlikoGreen.opacity(0.1))
        .cornerRadius(12)
    }
    
    // MARK: - Actions
    private func loadKeyStatus() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response: APIKeysStatusResponse = try await NetworkService.shared.get("/users/api-keys/status")
            
            bybitDemoStatus = response.bybitDemo?.isValid == true ? .valid : (response.bybitDemo?.hasKey == true ? .invalid : .notConfigured)
            bybitRealStatus = response.bybitReal?.isValid == true ? .valid : (response.bybitReal?.hasKey == true ? .invalid : .notConfigured)
            hlTestnetStatus = response.hlTestnet?.hasKey == true ? .valid : .notConfigured
            hlMainnetStatus = response.hlMainnet?.hasKey == true ? .valid : .notConfigured
        } catch {
            AppLogger.shared.error("Failed to load key status: \(error)", category: .network)
        }
    }
    
    private func testBybitKey(isDemo: Bool) async {
        let key = isDemo ? bybitDemoKey : bybitRealKey
        let secret = isDemo ? bybitDemoSecret : bybitRealSecret
        
        guard !key.isEmpty && !secret.isEmpty else { return }
        
        do {
            let request = TestAPIKeyRequest(apiKey: key, apiSecret: secret, isDemo: isDemo)
            let response: TestAPIKeyResponse = try await NetworkService.shared.post("/users/api-keys/bybit/test", body: request)
            
            if isDemo {
                bybitDemoStatus = response.valid ? .valid : .invalid
            } else {
                bybitRealStatus = response.valid ? .valid : .invalid
            }
            
            // Haptic feedback
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(response.valid ? .success : .error)
        } catch {
            if isDemo {
                bybitDemoStatus = .invalid
            } else {
                bybitRealStatus = .invalid
            }
        }
    }
    
    private func saveKeys() {
        Task {
            isSaving = true
            defer { isSaving = false }
            
            do {
                // Save Bybit keys
                if !bybitDemoKey.isEmpty || !bybitDemoSecret.isEmpty {
                    let request = SaveAPIKeyRequest(
                        exchange: "bybit",
                        accountType: "demo",
                        apiKey: bybitDemoKey.isEmpty ? nil : bybitDemoKey,
                        apiSecret: bybitDemoSecret.isEmpty ? nil : bybitDemoSecret,
                        privateKey: nil
                    )
                    let _: EmptyResponse = try await NetworkService.shared.post("/users/api-keys", body: request)
                }
                
                if !bybitRealKey.isEmpty || !bybitRealSecret.isEmpty {
                    let request = SaveAPIKeyRequest(
                        exchange: "bybit",
                        accountType: "real",
                        apiKey: bybitRealKey.isEmpty ? nil : bybitRealKey,
                        apiSecret: bybitRealSecret.isEmpty ? nil : bybitRealSecret,
                        privateKey: nil
                    )
                    let _: EmptyResponse = try await NetworkService.shared.post("/users/api-keys", body: request)
                }
                
                // Save HyperLiquid keys
                if !hlTestnetKey.isEmpty {
                    let request = SaveAPIKeyRequest(
                        exchange: "hyperliquid",
                        accountType: "testnet",
                        apiKey: nil,
                        apiSecret: nil,
                        privateKey: hlTestnetKey
                    )
                    let _: EmptyResponse = try await NetworkService.shared.post("/users/api-keys", body: request)
                }
                
                if !hlMainnetKey.isEmpty {
                    let request = SaveAPIKeyRequest(
                        exchange: "hyperliquid",
                        accountType: "mainnet",
                        apiKey: nil,
                        apiSecret: nil,
                        privateKey: hlMainnetKey
                    )
                    let _: EmptyResponse = try await NetworkService.shared.post("/users/api-keys", body: request)
                }
                
                // Haptic success
                let generator = UINotificationFeedbackGenerator()
                generator.notificationOccurred(.success)
                
                dismiss()
            } catch {
                AppLogger.shared.error("Failed to save keys: \(error)", category: .network)
                appState.showError(error.localizedDescription)
            }
        }
    }
    
    private func deleteKey(_ keyType: APIKeyType) {
        Task {
            do {
                let endpoint: String
                switch keyType {
                case .bybitDemo:
                    endpoint = "/users/api-keys/bybit/demo"
                case .bybitReal:
                    endpoint = "/users/api-keys/bybit/real"
                case .hlTestnet:
                    endpoint = "/users/api-keys/hyperliquid/testnet"
                case .hlMainnet:
                    endpoint = "/users/api-keys/hyperliquid/mainnet"
                }
                
                let _: EmptyResponse = try await NetworkService.shared.delete(endpoint)
                
                // Update status
                switch keyType {
                case .bybitDemo:
                    bybitDemoStatus = .notConfigured
                    bybitDemoKey = ""
                    bybitDemoSecret = ""
                case .bybitReal:
                    bybitRealStatus = .notConfigured
                    bybitRealKey = ""
                    bybitRealSecret = ""
                case .hlTestnet:
                    hlTestnetStatus = .notConfigured
                    hlTestnetKey = ""
                case .hlMainnet:
                    hlMainnetStatus = .notConfigured
                    hlMainnetKey = ""
                }
                
                showSaveSuccess = true
            } catch {
                AppLogger.shared.error("Failed to delete key: \(error)", category: .network)
            }
        }
    }
}

// MARK: - Supporting Types
enum APIKeyStatus {
    case notConfigured
    case valid
    case invalid
    
    var color: Color {
        switch self {
        case .notConfigured: return .enlikoTextMuted
        case .valid: return .enlikoGreen
        case .invalid: return .enlikoRed
        }
    }
    
    var icon: String {
        switch self {
        case .notConfigured: return "minus.circle.fill"
        case .valid: return "checkmark.circle.fill"
        case .invalid: return "xmark.circle.fill"
        }
    }
    
    var text: String {
        switch self {
        case .notConfigured: return "not_configured".localized
        case .valid: return "valid".localized
        case .invalid: return "invalid".localized
        }
    }
}

enum APIKeyType {
    case bybitDemo
    case bybitReal
    case hlTestnet
    case hlMainnet
}

// MARK: - API Models
struct APIKeysStatusResponse: Codable {
    let bybitDemo: KeyStatus?
    let bybitReal: KeyStatus?
    let hlTestnet: KeyStatus?
    let hlMainnet: KeyStatus?
    
    enum CodingKeys: String, CodingKey {
        case bybitDemo = "bybit_demo"
        case bybitReal = "bybit_real"
        case hlTestnet = "hl_testnet"
        case hlMainnet = "hl_mainnet"
    }
    
    struct KeyStatus: Codable {
        let hasKey: Bool
        let isValid: Bool?
        
        enum CodingKeys: String, CodingKey {
            case hasKey = "has_key"
            case isValid = "is_valid"
        }
    }
}

struct TestAPIKeyRequest: Codable {
    let apiKey: String
    let apiSecret: String
    let isDemo: Bool
    
    enum CodingKeys: String, CodingKey {
        case apiKey = "api_key"
        case apiSecret = "api_secret"
        case isDemo = "is_demo"
    }
}

struct TestAPIKeyResponse: Codable {
    let valid: Bool
    let balance: Double?
    let error: String?
}

struct SaveAPIKeyRequest: Codable {
    let exchange: String
    let accountType: String
    let apiKey: String?
    let apiSecret: String?
    let privateKey: String?
    
    enum CodingKeys: String, CodingKey {
        case exchange
        case accountType = "account_type"
        case apiKey = "api_key"
        case apiSecret = "api_secret"
        case privateKey = "private_key"
    }
}

// MARK: - Supporting Views
struct ExchangeTab: View {
    let name: String
    let icon: String
    let color: Color
    let isSelected: Bool
    let hasKeys: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                Text(name)
                    .fontWeight(.semibold)
                if hasKeys {
                    Circle()
                        .fill(Color.enlikoGreen)
                        .frame(width: 6, height: 6)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(isSelected ? color.opacity(0.15) : Color.clear)
            .foregroundColor(isSelected ? color : .enlikoTextSecondary)
        }
    }
}

struct APIKeyCard: View {
    let title: String
    let subtitle: String
    let icon: String
    let color: Color
    let status: APIKeyStatus
    @Binding var apiKey: String
    @Binding var apiSecret: String
    let onTest: () async -> Void
    let onDelete: () -> Void
    
    @State private var isTesting = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.headline)
                Spacer()
                // Status Badge
                HStack(spacing: 4) {
                    Image(systemName: status.icon)
                    Text(status.text)
                        .font(.caption)
                }
                .foregroundColor(status.color)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(status.color.opacity(0.15))
                .cornerRadius(8)
            }
            
            Text(subtitle)
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            
            // Input Fields
            SecureInputField(placeholder: "API Key", text: $apiKey)
            SecureInputField(placeholder: "API Secret", text: $apiSecret)
            
            // Actions
            HStack {
                Button(action: {
                    Task {
                        isTesting = true
                        await onTest()
                        isTesting = false
                    }
                }) {
                    HStack {
                        if isTesting {
                            ProgressView()
                                .tint(.enlikoPrimary)
                        } else {
                            Image(systemName: "checkmark.shield")
                        }
                        Text("test_key".localized)
                    }
                    .font(.subheadline.weight(.medium))
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(Color.enlikoPrimary.opacity(0.2))
                    .foregroundColor(.enlikoPrimary)
                    .cornerRadius(10)
                }
                .disabled(apiKey.isEmpty || apiSecret.isEmpty || isTesting)
                
                Spacer()
                
                if status != .notConfigured {
                    Button(action: onDelete) {
                        Image(systemName: "trash")
                            .foregroundColor(.enlikoRed)
                            .padding(10)
                            .background(Color.enlikoRed.opacity(0.15))
                            .cornerRadius(10)
                    }
                }
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(status == .valid ? color.opacity(0.3) : Color.clear, lineWidth: 2)
        )
    }
}

struct HLKeyCard: View {
    let title: String
    let subtitle: String
    let icon: String
    let color: Color
    let status: APIKeyStatus
    @Binding var privateKey: String
    let onDelete: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.headline)
                Spacer()
                HStack(spacing: 4) {
                    Image(systemName: status.icon)
                    Text(status.text)
                        .font(.caption)
                }
                .foregroundColor(status.color)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(status.color.opacity(0.15))
                .cornerRadius(8)
            }
            
            Text(subtitle)
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            
            SecureInputField(placeholder: "Private Key (0x...)", text: $privateKey)
            
            if status != .notConfigured {
                HStack {
                    Spacer()
                    Button(action: onDelete) {
                        HStack {
                            Image(systemName: "trash")
                            Text("delete_key".localized)
                        }
                        .font(.subheadline)
                        .foregroundColor(.enlikoRed)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(Color.enlikoRed.opacity(0.15))
                        .cornerRadius(10)
                    }
                }
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(status == .valid ? color.opacity(0.3) : Color.clear, lineWidth: 2)
        )
    }
}

struct SecurityTip: View {
    let icon: String
    let text: String
    var isWarning: Bool = false
    
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: icon)
                .foregroundColor(isWarning ? .enlikoRed : .enlikoGreen)
                .font(.caption)
            Text(text)
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
        }
    }
}

// MARK: - Secure Input Field
struct SecureInputField: View {
    let placeholder: String
    @Binding var text: String
    @State private var isSecure = true
    
    var body: some View {
        HStack {
            if isSecure {
                SecureField(placeholder, text: $text)
            } else {
                TextField(placeholder, text: $text)
            }
            
            Button(action: { isSecure.toggle() }) {
                Image(systemName: isSecure ? "eye.slash" : "eye")
                    .foregroundColor(.enlikoTextSecondary)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .foregroundColor(.white)
        .cornerRadius(10)
    }
}

#Preview("Exchange Settings") {
    NavigationStack {
        ExchangeSettingsView()
            .environmentObject(AppState.shared)
    }
    .preferredColorScheme(.dark)
}

#Preview("About") {
    NavigationStack {
        AboutView()
    }
    .preferredColorScheme(.dark)
}
