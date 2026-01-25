//
//  SettingsView.swift
//  LyxenTrading
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
                Color.lyxenBackground.ignoresSafeArea()
                
                List {
                    // Account Section
                    Section {
                        if let user = authManager.currentUser {
                            HStack(spacing: 16) {
                                // Avatar
                                ZStack {
                                    Circle()
                                        .fill(Color.lyxenGradient)
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
                                        .foregroundColor(.lyxenTextSecondary)
                                    
                                    // Premium badge
                                    if user.isPremium == true {
                                        HStack(spacing: 4) {
                                            Image(systemName: "crown.fill")
                                                .font(.caption2)
                                            Text("premium_active".localized)
                                                .font(.caption2.weight(.medium))
                                        }
                                        .foregroundColor(.lyxenYellow)
                                    }
                                }
                            }
                            .padding(.vertical, 8)
                        }
                    } header: {
                        Text("settings_account".localized)
                    }
                    .listRowBackground(Color.lyxenCard)
                    
                    // Trading Settings Section
                    Section {
                        // Default Exchange
                        NavigationLink {
                            ExchangeSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "arrow.left.arrow.right.circle.fill",
                                iconColor: .lyxenPrimary,
                                title: "settings_exchange".localized,
                                value: appState.selectedExchange.displayName
                            )
                        }
                        
                        // API Keys
                        Button(action: { showAPIKeySheet = true }) {
                            SettingsRow(
                                icon: "key.fill",
                                iconColor: .lyxenYellow,
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
                                iconColor: .lyxenOrange,
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
                                iconColor: .lyxenGreen,
                                title: "settings_risk".localized,
                                value: ""
                            )
                        }
                    } header: {
                        Text("settings_trading".localized)
                    }
                    .listRowBackground(Color.lyxenCard)
                    
                    // Notifications Section
                    Section {
                        NavigationLink {
                            NotificationSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "bell.fill",
                                iconColor: .lyxenBlue,
                                title: "settings_notifications".localized,
                                value: ""
                            )
                        }
                    } header: {
                        Text("settings_notifications".localized)
                    }
                    .listRowBackground(Color.lyxenCard)
                    
                    // App Section
                    Section {
                        // Language
                        NavigationLink {
                            LanguageSettingsView()
                        } label: {
                            SettingsRow(
                                icon: "globe",
                                iconColor: .lyxenBlue,
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
                                iconColor: .lyxenTextSecondary,
                                title: "settings_about".localized,
                                value: "v1.0.0"
                            )
                        }
                        
                        // Privacy Policy
                        Link(destination: URL(string: "https://lyxen.io/privacy")!) {
                            SettingsRow(
                                icon: "hand.raised.fill",
                                iconColor: .lyxenTextMuted,
                                title: "settings_privacy".localized,
                                value: "",
                                showChevron: false
                            )
                        }
                        
                        // Terms of Service
                        Link(destination: URL(string: "https://lyxen.io/terms")!) {
                            SettingsRow(
                                icon: "doc.text.fill",
                                iconColor: .lyxenTextMuted,
                                title: "settings_terms".localized,
                                value: "",
                                showChevron: false
                            )
                        }
                    } header: {
                        Text("settings_app".localized)
                    }
                    .listRowBackground(Color.lyxenCard)
                    
                    // Logout Section
                    Section {
                        Button(action: { showLogoutConfirmation = true }) {
                            HStack {
                                Spacer()
                                Text("settings_logout".localized)
                                    .foregroundColor(.lyxenRed)
                                    .fontWeight(.medium)
                                Spacer()
                            }
                        }
                    }
                    .listRowBackground(Color.lyxenCard)
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
                    .foregroundColor(.lyxenTextSecondary)
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
