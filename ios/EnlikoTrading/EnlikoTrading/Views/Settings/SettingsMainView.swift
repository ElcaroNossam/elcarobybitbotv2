//
//  SettingsMainView.swift
//  EnlikoTrading
//
//  Main Settings with prominent API Keys and Strategy Settings buttons
//

import SwiftUI
import Combine

struct SettingsMainView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var viewModel = SettingsMainViewModel()
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Exchange & Account Selector
                exchangeAccountSection
                
                // PROMINENT: API Keys
                apiKeysSection
                
                // PROMINENT: Strategy Settings
                strategySettingsSection
                
                // Quick Tools Grid
                quickToolsSection
                
                // Logout
                logoutSection
            }
            .padding()
        }
        .background(Color.enlikoBackground)
        .navigationTitle("settings".localized)
        .navigationBarTitleDisplayMode(.large)
        .onAppear {
            Task {
                await viewModel.fetchAPIStatus()
            }
        }
    }
    
    // MARK: - Exchange & Account Section
    private var exchangeAccountSection: some View {
        VStack(spacing: 12) {
            // Exchange Toggle
            HStack(spacing: 12) {
                ExchangeToggleButton(
                    title: "Bybit",
                    icon: "chart.bar.fill",
                    isSelected: appState.currentExchange == .bybit,
                    color: .orange
                ) {
                    appState.switchExchange(to: .bybit)
                }
                
                ExchangeToggleButton(
                    title: "HyperLiquid",
                    icon: "bolt.fill",
                    isSelected: appState.currentExchange == .hyperliquid,
                    color: .cyan
                ) {
                    appState.switchExchange(to: .hyperliquid)
                }
            }
            
            // Account Type Toggle
            HStack(spacing: 12) {
                AccountTypeButton(
                    title: appState.currentExchange == .bybit ? "Demo" : "Testnet",
                    isSelected: appState.currentAccountType == .demo,
                    color: .orange
                ) {
                    appState.switchAccountType(to: .demo)
                }
                
                AccountTypeButton(
                    title: appState.currentExchange == .bybit ? "Real" : "Mainnet",
                    isSelected: appState.currentAccountType == .real,
                    color: .green
                ) {
                    appState.switchAccountType(to: .real)
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - API Keys Section (PROMINENT)
    private var apiKeysSection: some View {
        NavigationLink {
            APIKeysSheetView()
        } label: {
            HStack(spacing: 16) {
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.enlikoPrimary, Color.enlikoPrimary.opacity(0.6)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 56, height: 56)
                    
                    Image(systemName: "key.fill")
                        .font(.title2)
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("api_keys".localized)
                        .font(.headline.bold())
                        .foregroundColor(.white)
                    
                    Text(viewModel.apiStatusText)
                        .font(.caption)
                        .foregroundColor(viewModel.apiConfigured ? .enlikoGreen : .orange)
                }
                
                Spacer()
                
                if !viewModel.apiConfigured {
                    Text("!")
                        .font(.caption.bold())
                        .foregroundColor(.white)
                        .frame(width: 20, height: 20)
                        .background(Color.orange)
                        .clipShape(Circle())
                }
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(
                LinearGradient(
                    colors: [Color.enlikoPrimary.opacity(0.2), Color.enlikoSurface],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(16)
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color.enlikoPrimary.opacity(0.3), lineWidth: 1)
            )
        }
    }
    
    // MARK: - Strategy Settings Section (PROMINENT)
    private var strategySettingsSection: some View {
        NavigationLink {
            StrategySettingsView()
        } label: {
            HStack(spacing: 16) {
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.purple, Color.purple.opacity(0.6)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 56, height: 56)
                    
                    Image(systemName: "gearshape.2.fill")
                        .font(.title2)
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("strategy_settings".localized)
                        .font(.headline.bold())
                        .foregroundColor(.white)
                    
                    Text("configure_all_strategies".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(
                LinearGradient(
                    colors: [Color.purple.opacity(0.2), Color.enlikoSurface],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(16)
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color.purple.opacity(0.3), lineWidth: 1)
            )
        }
    }
    
    // MARK: - Quick Tools Grid
    private var quickToolsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("quick_tools".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                NavigationLink {
                    LanguageSettingsView()
                } label: {
                    QuickToolCard(
                        icon: "globe",
                        title: "language".localized,
                        subtitle: LocalizationManager.shared.currentLanguage.displayName
                    )
                }
                
                NavigationLink {
                    NotificationSettingsView()
                } label: {
                    QuickToolCard(
                        icon: "bell.fill",
                        title: "notifications".localized,
                        subtitle: "configured".localized
                    )
                }
                
                NavigationLink {
                    SubscriptionView()
                } label: {
                    QuickToolCard(
                        icon: "crown.fill",
                        title: "premium".localized,
                        subtitle: "upgrade".localized
                    )
                }
                
                NavigationLink {
                    TradeHistoryView()
                } label: {
                    QuickToolCard(
                        icon: "clock.arrow.circlepath",
                        title: "trade_history".localized,
                        subtitle: "view_trades".localized
                    )
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Logout Section
    private var logoutSection: some View {
        Button {
            authManager.logout()
        } label: {
            HStack {
                Image(systemName: "rectangle.portrait.and.arrow.right")
                Text("logout".localized)
            }
            .font(.headline)
            .foregroundColor(.enlikoRed)
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.enlikoRed.opacity(0.15))
            .cornerRadius(16)
        }
    }
}

// MARK: - Supporting Views
struct ExchangeToggleButton: View {
    let title: String
    let icon: String
    let isSelected: Bool
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                    .font(.subheadline)
                Text(title)
                    .font(.subheadline.bold())
            }
            .foregroundColor(isSelected ? .white : .secondary)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(isSelected ? color : Color.enlikoBackground)
            .cornerRadius(12)
        }
    }
}

struct AccountTypeButton: View {
    let title: String
    let isSelected: Bool
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline.bold())
                .foregroundColor(isSelected ? .white : .secondary)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 10)
                .background(isSelected ? color : Color.enlikoBackground)
                .cornerRadius(10)
        }
    }
}

struct QuickToolCard: View {
    let icon: String
    let title: String
    let subtitle: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.enlikoPrimary)
            
            Text(title)
                .font(.subheadline.bold())
                .foregroundColor(.white)
            
            Text(subtitle)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.enlikoBackground)
        .cornerRadius(12)
    }
}

// MARK: - ViewModel
@MainActor
class SettingsMainViewModel: ObservableObject {
    @Published var apiConfigured = false
    @Published var apiStatusText = "tap_to_configure".localized
    
    private let network = NetworkService.shared
    
    @MainActor
    func fetchAPIStatus() async {
        do {
            let status: APIKeysStatus = try await network.get("/users/api-keys/status")
            apiConfigured = status.bybit.configured || status.hyperliquid.configured
            
            if apiConfigured {
                var parts: [String] = []
                if status.bybit.configured { parts.append("Bybit") }
                if status.hyperliquid.configured { parts.append("HL") }
                apiStatusText = parts.joined(separator: " + ") + " " + "connected".localized
            } else {
                apiStatusText = "tap_to_configure".localized
            }
        } catch {
            print("Failed to fetch API status: \(error)")
            apiStatusText = "tap_to_configure".localized
        }
    }
}

#Preview {
    NavigationStack {
        SettingsMainView()
            .environmentObject(AppState.shared)
            .environmentObject(AuthManager.shared)
            .preferredColorScheme(.dark)
    }
}
