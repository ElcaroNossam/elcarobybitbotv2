//
//  SettingsView.swift
//  EnlikoTrading
//
//  User settings and configuration with full localization support
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var showLogoutConfirmation = false
    @State private var showAPIKeySheet = false
    @State private var selectedAPIType: APIKeyType = .bybitDemo
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                List {
                    // Account Section
                    Section {
                        if let user = authManager.currentUser {
                            HStack(spacing: 16) {
                                // Avatar
                                ZStack {
                                    Circle()
                                        .fill(Color.enlikoGradient)
                                        .frame(width: 60, height: 60)
                                    
                                    Text(user.displayName.prefix(1).uppercased())
                                        .font(.title2.bold())
                                        .foregroundColor(.white)
                                }
                                
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(user.displayName)
                                        .font(.headline)
                                        .foregroundColor(.white)
                                    
                                    Text(user.email ?? "ID: \(user.id)")
                                        .font(.caption)
                                        .foregroundColor(.enlikoTextSecondary)
                                    
                                    // Premium badge
                                    if user.isPremium == true {
                                        HStack(spacing: 4) {
                                            Image(systemName: "crown.fill")
                                                .font(.caption2)
                                            Text("premium_active".localized)
                                                .font(.caption2.weight(.medium))
                                        }
                                        .foregroundColor(.enlikoYellow)
                                    }
                                }
                            }
                            .padding(.vertical, 8)
                        }
                    } header: {
                        Text("settings_account".localized)
                    }
                    .listRowBackground(Color.enlikoCard)
                    
                    // Linked Accounts Section (Unified Auth)
                    Section {
                        if let user = authManager.currentUser {
                            // Telegram Link Status
                            if user.hasTelegramLinked {
                                HStack {
                                    Image(systemName: "paperplane.fill")
                                        .foregroundColor(.blue)
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text("Telegram")
                                            .font(.body)
                                            .foregroundColor(.white)
                                        if let username = user.telegramUsername {
                                            Text("@\(username)")
                                                .font(.caption)
                                                .foregroundColor(.enlikoTextSecondary)
                                        } else if let tid = user.telegramId {
                                            Text("ID: \(tid)")
                                                .font(.caption)
                                                .foregroundColor(.enlikoTextSecondary)
                                        }
                                    }
                                    Spacer()
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.green)
                                }
                            } else {
                                Button(action: openTelegramToLink) {
                                    HStack {
                                        Image(systemName: "paperplane")
                                            .foregroundColor(.blue)
                                        Text("link_telegram".localized)
                                            .foregroundColor(.white)
                                        Spacer()
                                        Image(systemName: "arrow.up.forward.app")
                                            .foregroundColor(.enlikoTextSecondary)
                                    }
                                }
                            }
                            
                            // Email Link Status
                            if user.hasEmailLinked {
                                HStack {
                                    Image(systemName: "envelope.fill")
                                        .foregroundColor(.orange)
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text("Email")
                                            .font(.body)
                                            .foregroundColor(.white)
                                        Text(user.email ?? "")
                                            .font(.caption)
                                            .foregroundColor(.enlikoTextSecondary)
                                    }
                                    Spacer()
                                    if user.emailVerified == true {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundColor(.green)
                                    } else {
                                        Text("not_verified".localized)
                                            .font(.caption)
                                            .foregroundColor(.orange)
                                    }
                                }
                            } else {
                                NavigationLink {
                                    LinkEmailView()
                                } label: {
                                    HStack {
                                        Image(systemName: "envelope")
                                            .foregroundColor(.orange)
                                        Text("link_email".localized)
                                            .foregroundColor(.white)
                                        Spacer()
                                    }
                                }
                            }
                        }
                    } header: {
                        Text("linked_accounts".localized)
                    }
                    .listRowBackground(Color.enlikoCard)
                    
                    // Subscription Section
                    Section {
                        NavigationLink {
                            SubscriptionView()
                        } label: {
                            SettingsRow(
                                icon: "crown.fill",
                                iconColor: .enlikoYellow,
                                title: "subscription".localized,
                                value: authManager.currentUser?.isPremium == true ? "premium_active".localized : "upgrade".localized
                            )
                        }
                    } header: {
                        Text("subscription".localized)
                    }
                    .listRowBackground(Color.enlikoCard)
                    
                    // Trading Settings Section
                    Section {
                        // Default Exchange
                        NavigationLink {
                            ExchangeSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "arrow.left.arrow.right.circle.fill",
                                iconColor: .enlikoPrimary,
                                title: "settings_exchange".localized,
                                value: appState.selectedExchange.displayName
                            )
                        }
                        
                        // Trading Settings (DCA, Order Type, ATR, Spot)
                        NavigationLink {
                            TradingSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "gearshape.2.fill",
                                iconColor: .enlikoPurple,
                                title: "trading_settings".localized,
                                value: ""
                            )
                        }
                        
                        // Strategy Settings (Long/Short per strategy)
                        NavigationLink {
                            StrategySettingsView()
                        } label: {
                            SettingsRow(
                                icon: "slider.horizontal.3",
                                iconColor: .enlikoBlue,
                                title: "strategy_settings".localized,
                                value: ""
                            )
                        }
                        
                        // API Keys
                        Button(action: { showAPIKeySheet = true }) {
                            SettingsRow(
                                icon: "key.fill",
                                iconColor: .enlikoYellow,
                                title: "settings_api_keys".localized,
                                value: ""
                            )
                        }
                        
                        // Default Leverage
                        NavigationLink {
                            LeverageSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "dial.medium.fill",
                                iconColor: .enlikoOrange,
                                title: "settings_leverage".localized,
                                value: "10x"
                            )
                        }
                        
                        // Risk Settings
                        NavigationLink {
                            RiskSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "shield.fill",
                                iconColor: .enlikoGreen,
                                title: "settings_risk".localized,
                                value: ""
                            )
                        }
                    } header: {
                        Text("settings_trading".localized)
                    }
                    .listRowBackground(Color.enlikoCard)
                    
                    // Notifications Section
                    Section {
                        NavigationLink {
                            NotificationSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "bell.fill",
                                iconColor: .enlikoBlue,
                                title: "settings_notifications".localized,
                                value: ""
                            )
                        }
                    } header: {
                        Text("settings_notifications".localized)
                    }
                    .listRowBackground(Color.enlikoCard)
                    
                    // App Section
                    Section {
                        // Language
                        NavigationLink {
                            LanguageSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "globe",
                                iconColor: .enlikoBlue,
                                title: "settings_language".localized,
                                value: "\(localization.currentLanguage.flag) \(localization.currentLanguage.displayName)"
                            )
                        }
                        
                        NavigationLink {
                            AppearanceSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "paintbrush.fill",
                                iconColor: .purple,
                                title: "settings_appearance".localized,
                                value: "Dark"
                            )
                        }
                        
                        NavigationLink {
                            AboutView()
                        } label: {
                            SettingsRow(
                                icon: "info.circle.fill",
                                iconColor: .enlikoTextSecondary,
                                title: "settings_about".localized,
                                value: "v1.0.0"
                            )
                        }
                        
                        // Privacy Policy
                        Link(destination: URL(string: "https://enliko.com/privacy")!) {
                            SettingsRow(
                                icon: "hand.raised.fill",
                                iconColor: .enlikoTextMuted,
                                title: "settings_privacy".localized,
                                value: "",
                                showChevron: false
                            )
                        }
                        
                        // Terms of Service
                        Link(destination: URL(string: "https://enliko.com/terms")!) {
                            SettingsRow(
                                icon: "doc.text.fill",
                                iconColor: .enlikoTextMuted,
                                title: "settings_terms".localized,
                                value: "",
                                showChevron: false
                            )
                        }
                        
                        // Debug Console
                        NavigationLink {
                            DebugView()
                        } label: {
                            SettingsRow(
                                icon: "ant.fill",
                                iconColor: .orange,
                                title: "Debug Console",
                                value: ""
                            )
                        }
                    } header: {
                        Text("settings_app".localized)
                    }
                    .listRowBackground(Color.enlikoCard)
                    
                    // Admin Section (only visible for admins)
                    if authManager.currentUser?.isAdmin == true {
                        Section {
                            NavigationLink {
                                AdminView()
                            } label: {
                                SettingsRow(
                                    icon: "shield.checkered",
                                    iconColor: .red,
                                    title: "admin_dashboard".localized,
                                    value: ""
                                )
                            }
                        } header: {
                            HStack {
                                Text("admin_section".localized)
                                Image(systemName: "lock.shield")
                                    .foregroundColor(.red)
                            }
                        }
                        .listRowBackground(Color.enlikoCard)
                    }
                    
                    // Logout Section
                    Section {
                        Button(action: { showLogoutConfirmation = true }) {
                            HStack {
                                Spacer()
                                Text("settings_logout".localized)
                                    .foregroundColor(.enlikoRed)
                                    .fontWeight(.medium)
                                Spacer()
                            }
                        }
                    }
                    .listRowBackground(Color.enlikoCard)
                }
                .listStyle(.insetGrouped)
                .scrollContentBackground(.hidden)
            }
            .navigationTitle("settings_title".localized)
            .navigationBarTitleDisplayMode(.large)
            .alert("settings_logout".localized, isPresented: $showLogoutConfirmation) {
                Button("common_cancel".localized, role: .cancel) {}
                Button("settings_logout".localized, role: .destructive) {
                    authManager.logout()
                }
            } message: {
                Text("settings_logout_confirm".localized)
            }
            .sheet(isPresented: $showAPIKeySheet) {
                APIKeysSheetView()
            }
            .withRTLSupport()
        }
    }
    
    // MARK: - Open Telegram to link account
    private func openTelegramToLink() {
        // Open Telegram bot to get login link
        if let url = URL(string: "https://t.me/EnlikoBot?start=link_app") {
            UIApplication.shared.open(url)
        }
    }
}

// MARK: - Settings Row
struct SettingsRow: View {
    let icon: String
    let iconColor: Color
    let title: String
    let value: String
    var showChevron: Bool = true
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(iconColor)
                .frame(width: 28)
            
            Text(title)
                .foregroundColor(.white)
            
            Spacer()
            
            if !value.isEmpty {
                Text(value)
                    .foregroundColor(.enlikoTextSecondary)
            }
        }
        .padding(.vertical, 4)
    }
}

// All sub-views (APIKeyType, APIKeysSheetView, ExchangeSettingsView, LeverageSettingsView,
// RiskSettingsView, NotificationSettingsView, AppearanceSettingsView, AboutView)
// are defined in SubSettingsViews.swift

#Preview {
    SettingsView()
        .environmentObject(AppState.shared)
        .environmentObject(AuthManager.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
