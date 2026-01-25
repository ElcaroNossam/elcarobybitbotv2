//
//  LyxenTradingApp.swift
//  LyxenTrading
//
//  Professional Trading Platform for iOS
//  Integrated with Lyxen Backend API
//  Full localization support for 15 languages
//

import SwiftUI

@main
struct LyxenTradingApp: App {
    @StateObject private var authManager = AuthManager.shared
    @StateObject private var appState = AppState.shared
    @StateObject private var tradingService = TradingService.shared
    @StateObject private var localization = LocalizationManager.shared
    
    init() {
        configureAppearance()
    }
    
    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(authManager)
                .environmentObject(appState)
                .environmentObject(tradingService)
                .environmentObject(localization)
                .preferredColorScheme(.dark)
                .withRTLSupport()
        }
    }
    
    private func configureAppearance() {
        // Navigation bar
        let navAppearance = UINavigationBarAppearance()
        navAppearance.configureWithOpaqueBackground()
        navAppearance.backgroundColor = UIColor(Color.lyxenBackground)
        navAppearance.titleTextAttributes = [.foregroundColor: UIColor.white]
        navAppearance.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
        
        UINavigationBar.appearance().standardAppearance = navAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = navAppearance
        
        // Tab bar
        let tabAppearance = UITabBarAppearance()
        tabAppearance.configureWithOpaqueBackground()
        tabAppearance.backgroundColor = UIColor(Color.lyxenBackground)
        
        UITabBar.appearance().standardAppearance = tabAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabAppearance
    }
}

// MARK: - Root View
struct RootView: View {
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var appState: AppState
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView()
                    .transition(.opacity)
            } else {
                LoginView()
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.3), value: authManager.isAuthenticated)
        .onAppear {
            authManager.checkAuthStatus()
        }
        .alert("common_error".localized, isPresented: $appState.showError) {
            Button("common_ok".localized) { appState.clearError() }
        } message: {
            Text(appState.errorMessage ?? "error_unknown".localized)
        }
    }
}
