//
//  UnifiedSettingsView.swift
//  EnlikoTrading
//
//  Unified settings view combining Settings + More in one clean interface
//  Simplified navigation, grouped by category
//

import SwiftUI

struct UnifiedSettingsView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var authManager: AuthManager
    @ObservedObject var localization = LocalizationManager.shared
    @State private var showLogoutAlert = false
    @State private var showAICopilot = false
    
    var body: some View {
        List {
            // MARK: - Account Section
            Section {
                // Account Info Card
                accountInfoCard
            }
            
            // MARK: - Quick Actions (Most Used)
            Section(header: sectionHeader("quick_actions".localized, icon: "bolt.fill")) {
                // Positions (quick access)
                NavigationLink(destination: PositionsView()) {
                    quickActionItem(
                        icon: "list.bullet.rectangle.fill",
                        title: "nav_positions".localized,
                        subtitle: "\(appState.openPositionsCount) open",
                        color: .blue
                    )
                }
                
                // Trade History
                NavigationLink(destination: TradeHistoryView()) {
                    quickActionItem(
                        icon: "clock.arrow.circlepath",
                        title: "trade_history".localized,
                        subtitle: "View all trades",
                        color: .purple
                    )
                }
                
                // AI Copilot
                Button {
                    showAICopilot = true
                } label: {
                    quickActionItem(
                        icon: "sparkles",
                        title: "ai_copilot".localized,
                        subtitle: "Smart assistant",
                        color: .pink
                    )
                }
            }
            
            // MARK: - Trading Tools
            Section(header: sectionHeader("trading_tools".localized, icon: "wrench.and.screwdriver.fill")) {
                // Strategies
                NavigationLink(destination: StrategiesView()) {
                    settingsRow(
                        icon: "brain",
                        title: "strategies_title".localized,
                        color: .purple
                    )
                }
                
                // Signals
                NavigationLink(destination: SignalsView()) {
                    settingsRow(
                        icon: "bell.fill",
                        title: "signals_title".localized,
                        color: .red
                    )
                }
                
                // Screener
                NavigationLink(destination: ScreenerView()) {
                    settingsRow(
                        icon: "magnifyingglass.circle.fill",
                        title: "screener_title".localized,
                        color: .orange
                    )
                }
                
                // Spot Trading
                NavigationLink(destination: SpotTradingView()) {
                    settingsRow(
                        icon: "dollarsign.circle.fill",
                        title: "spot_trading".localized,
                        color: .green
                    )
                }
            }
            
            // MARK: - Trading Settings
            Section(header: sectionHeader("trading_settings".localized, icon: "slider.horizontal.3")) {
                // Strategy Settings
                NavigationLink(destination: StrategySettingsView()) {
                    settingsRow(
                        icon: "gearshape.2.fill",
                        title: "strategy_settings".localized,
                        color: .indigo
                    )
                }
                
                // Trading Settings
                NavigationLink(destination: TradingSettingsView()) {
                    settingsRow(
                        icon: "chart.line.uptrend.xyaxis",
                        title: "trading_preferences".localized,
                        color: .cyan
                    )
                }
                
                // Exchange Connection
                NavigationLink(destination: ExchangeSettingsView()) {
                    HStack {
                        settingsRow(
                            icon: "link.circle.fill",
                            title: "exchange_connection".localized,
                            color: .teal
                        )
                        
                        Spacer()
                        
                        // Status indicator
                        HStack(spacing: 4) {
                            Circle()
                                .fill(appState.isConnected ? .green : .red)
                                .frame(width: 8, height: 8)
                            Text(appState.currentExchange.displayName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
            
            // MARK: - App Settings
            Section(header: sectionHeader("app_settings".localized, icon: "iphone")) {
                // Language
                NavigationLink(destination: LanguageSettingsView()) {
                    HStack {
                        settingsRow(
                            icon: "globe",
                            title: "language".localized,
                            color: .blue
                        )
                        
                        Spacer()
                        
                        Text(localization.currentLanguage.displayName)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                // Notifications
                NavigationLink(destination: NotificationSettingsView()) {
                    settingsRow(
                        icon: "bell.badge.fill",
                        title: "notifications".localized,
                        color: .yellow
                    )
                }
                
                // Appearance
                NavigationLink(destination: AppearanceSettingsView()) {
                    settingsRow(
                        icon: "paintbrush.fill",
                        title: "appearance".localized,
                        color: .pink
                    )
                }
                
                // Security (Biometrics)
                NavigationLink(destination: SecuritySettingsView()) {
                    settingsRow(
                        icon: "faceid",
                        title: "security".localized,
                        color: .green
                    )
                }
            }
            
            // MARK: - Account Actions
            Section(header: sectionHeader("account".localized, icon: "person.fill")) {
                // Activity (Cross-platform sync)
                NavigationLink(destination: ActivityView()) {
                    settingsRow(
                        icon: "arrow.triangle.2.circlepath",
                        title: "activity_sync".localized,
                        color: .cyan
                    )
                }
                
                // Premium / Subscription
                NavigationLink(destination: SubscriptionView()) {
                    HStack {
                        settingsRow(
                            icon: "crown.fill",
                            title: "premium".localized,
                            color: .yellow
                        )
                        
                        Spacer()
                        
                        if appState.isPremium {
                            Text("Active")
                                .font(.caption.bold())
                                .foregroundColor(.yellow)
                        }
                    }
                }
                
                // Help & Support
                NavigationLink(destination: HelpView()) {
                    settingsRow(
                        icon: "questionmark.circle.fill",
                        title: "help_support".localized,
                        color: .gray
                    )
                }
                
                // Logout
                Button {
                    showLogoutAlert = true
                } label: {
                    settingsRow(
                        icon: "rectangle.portrait.and.arrow.right",
                        title: "logout".localized,
                        color: .red
                    )
                }
            }
            
            // MARK: - App Info
            Section {
                HStack {
                    Spacer()
                    VStack(spacing: 4) {
                        Text("Enliko Trading")
                            .font(.caption.bold())
                        Text("Version \(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0")")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                }
                .padding(.vertical, 8)
            }
        }
        .listStyle(InsetGroupedListStyle())
        .navigationTitle("nav_settings".localized)
        .sheet(isPresented: $showAICopilot) {
            AICopilotView()
        }
        .alert("logout_confirm".localized, isPresented: $showLogoutAlert) {
            Button("cancel".localized, role: .cancel) { }
            Button("logout".localized, role: .destructive) {
                authManager.logout()
            }
        } message: {
            Text("logout_message".localized)
        }
    }
    
    // MARK: - Account Info Card
    private var accountInfoCard: some View {
        HStack(spacing: 16) {
            // Avatar
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.enlikoPrimary, .enlikoPrimary.opacity(0.7)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 60, height: 60)
                
                Text(authManager.currentUser?.displayName.prefix(1).uppercased() ?? "U")
                    .font(.title2.bold())
                    .foregroundColor(.white)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(authManager.currentUser?.displayName ?? "User")
                    .font(.headline)
                
                if let email = authManager.currentUser?.email {
                    Text(email)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                // Account type badge
                HStack(spacing: 8) {
                    accountTypeBadge
                    exchangeBadge
                }
            }
            
            Spacer()
        }
        .padding(.vertical, 8)
    }
    
    private var accountTypeBadge: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(appState.currentAccountType == .demo ? .orange : .green)
                .frame(width: 6, height: 6)
            Text(appState.currentAccountType == .demo ? "Demo" : "Real")
                .font(.caption2.bold())
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(Color.enlikoCard)
        .cornerRadius(8)
    }
    
    private var exchangeBadge: some View {
        Text(appState.currentExchange.displayName)
            .font(.caption2.bold())
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.enlikoCard)
            .cornerRadius(8)
    }
    
    // MARK: - Helper Views
    private func sectionHeader(_ title: String, icon: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: icon)
                .font(.caption2)
                .foregroundColor(.enlikoPrimary)
            Text(title)
        }
    }
    
    private func settingsRow(icon: String, title: String, color: Color) -> some View {
        HStack(spacing: 14) {
            Image(systemName: icon)
                .font(.body)
                .foregroundColor(.white)
                .frame(width: 32, height: 32)
                .background(color)
                .cornerRadius(8)
            
            Text(title)
                .font(.body)
        }
    }
    
    private func quickActionItem(icon: String, title: String, subtitle: String, color: Color) -> some View {
        HStack(spacing: 14) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(.white)
                .frame(width: 44, height: 44)
                .background(
                    LinearGradient(
                        colors: [color, color.opacity(0.8)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .cornerRadius(12)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.headline)
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Placeholder Views for missing destinations
struct ExchangeSettingsView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        List {
            Section(header: Text("exchange".localized)) {
                ForEach(Exchange.allCases, id: \.self) { exchange in
                    Button {
                        appState.currentExchange = exchange
                    } label: {
                        HStack {
                            Text(exchange.displayName)
                            Spacer()
                            if appState.currentExchange == exchange {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.enlikoPrimary)
                            }
                        }
                    }
                    .foregroundColor(.primary)
                }
            }
            
            Section(header: Text("account_type".localized)) {
                ForEach(AccountType.allCases, id: \.self) { type in
                    Button {
                        appState.currentAccountType = type
                    } label: {
                        HStack {
                            Circle()
                                .fill(type == .demo ? .orange : .green)
                                .frame(width: 8, height: 8)
                            Text(type == .demo ? "Demo" : "Real")
                            Spacer()
                            if appState.currentAccountType == type {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.enlikoPrimary)
                            }
                        }
                    }
                    .foregroundColor(.primary)
                }
            }
            
            Section(header: Text("api_keys".localized)) {
                NavigationLink(destination: APIKeysView()) {
                    HStack {
                        Image(systemName: "key.fill")
                            .foregroundColor(.yellow)
                        Text("manage_api_keys".localized)
                    }
                }
            }
        }
        .navigationTitle("exchange_connection".localized)
    }
}

struct AppearanceSettingsView: View {
    @AppStorage("colorScheme") private var colorScheme = 0 // 0=system, 1=light, 2=dark
    
    var body: some View {
        List {
            Section(header: Text("theme".localized)) {
                Picker("color_scheme".localized, selection: $colorScheme) {
                    Text("system".localized).tag(0)
                    Text("light".localized).tag(1)
                    Text("dark".localized).tag(2)
                }
                .pickerStyle(SegmentedPickerStyle())
            }
        }
        .navigationTitle("appearance".localized)
    }
}

struct SecuritySettingsView: View {
    @AppStorage("useBiometrics") private var useBiometrics = false
    @AppStorage("requireAuthOnOpen") private var requireAuthOnOpen = false
    
    var body: some View {
        List {
            Section(header: Text("biometric_auth".localized)) {
                Toggle(isOn: $useBiometrics) {
                    HStack {
                        Image(systemName: "faceid")
                            .foregroundColor(.green)
                        Text("use_face_id".localized)
                    }
                }
                
                if useBiometrics {
                    Toggle(isOn: $requireAuthOnOpen) {
                        HStack {
                            Image(systemName: "lock.fill")
                                .foregroundColor(.blue)
                            Text("require_on_launch".localized)
                        }
                    }
                }
            }
        }
        .navigationTitle("security".localized)
    }
}

struct HelpView: View {
    var body: some View {
        List {
            Section {
                Link(destination: URL(string: "https://enliko.com/docs")!) {
                    HStack {
                        Image(systemName: "book.fill")
                            .foregroundColor(.blue)
                        Text("documentation".localized)
                        Spacer()
                        Image(systemName: "arrow.up.right")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Link(destination: URL(string: "https://t.me/enliko_support")!) {
                    HStack {
                        Image(systemName: "paperplane.fill")
                            .foregroundColor(.blue)
                        Text("telegram_support".localized)
                        Spacer()
                        Image(systemName: "arrow.up.right")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Link(destination: URL(string: "mailto:support@enliko.com")!) {
                    HStack {
                        Image(systemName: "envelope.fill")
                            .foregroundColor(.orange)
                        Text("email_support".localized)
                        Spacer()
                        Image(systemName: "arrow.up.right")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .navigationTitle("help_support".localized)
    }
}

struct APIKeysView: View {
    var body: some View {
        List {
            Section(header: Text("Bybit API")) {
                NavigationLink("Demo API Key") {
                    Text("API Key configuration")
                }
                NavigationLink("Real API Key") {
                    Text("API Key configuration")
                }
            }
            
            Section(header: Text("HyperLiquid")) {
                NavigationLink("Testnet Key") {
                    Text("Private key configuration")
                }
                NavigationLink("Mainnet Key") {
                    Text("Private key configuration")
                }
            }
        }
        .navigationTitle("api_keys".localized)
    }
}

#Preview {
    NavigationStack {
        UnifiedSettingsView()
            .environmentObject(AppState.shared)
            .environmentObject(AuthManager.shared)
            .preferredColorScheme(.dark)
    }
}
