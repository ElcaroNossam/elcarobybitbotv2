//
//  EnlikoTradingApp.swift
//  EnlikoTrading
//
//  Professional Trading Platform for iOS
//  Integrated with Enliko Backend API
//  Full localization support for 15 languages
//

import SwiftUI

// MARK: - App Delegate for UIKit Appearance
class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
        configureAppearance()
        return true
    }
    
    private func configureAppearance() {
        // Navigation bar - use default styling to avoid visual style warnings
        let navAppearance = UINavigationBarAppearance()
        navAppearance.configureWithDefaultBackground()
        navAppearance.backgroundColor = UIColor(red: 0.04, green: 0.04, blue: 0.04, alpha: 1.0) // #0A0A0A
        navAppearance.titleTextAttributes = [.foregroundColor: UIColor.white]
        navAppearance.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
        navAppearance.shadowColor = .clear
        
        UINavigationBar.appearance().standardAppearance = navAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = navAppearance
        UINavigationBar.appearance().compactAppearance = navAppearance
        UINavigationBar.appearance().tintColor = .white
        
        // Tab bar - use default styling
        let tabAppearance = UITabBarAppearance()
        tabAppearance.configureWithDefaultBackground()
        tabAppearance.backgroundColor = UIColor(red: 0.04, green: 0.04, blue: 0.04, alpha: 1.0)
        tabAppearance.shadowColor = .clear
        
        UITabBar.appearance().standardAppearance = tabAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabAppearance
        UITabBar.appearance().tintColor = UIColor(red: 0.86, green: 0.15, blue: 0.15, alpha: 1.0) // #DC2626
    }
}

@main
struct EnlikoTradingApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var authManager = AuthManager.shared
    @StateObject private var appState = AppState.shared
    @StateObject private var tradingService = TradingService.shared
    @StateObject private var localization = LocalizationManager.shared
    
    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(authManager)
                .environmentObject(appState)
                .environmentObject(tradingService)
                .environmentObject(localization)
                .preferredColorScheme(appState.currentTheme.colorScheme)
                .withRTLSupport()
                .onOpenURL { url in
                    // Handle deep links from Telegram bot
                    // Format: enliko://login?token=XXX&tid=12345
                    authManager.handleURL(url)
                }
        }
    }
}

// MARK: - Root View
struct RootView: View {
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var appState: AppState
    @ObservedObject var localization = LocalizationManager.shared
    @ObservedObject var notificationService = PushNotificationService.shared
    @AppStorage("disclaimer_accepted") private var disclaimerAccepted = false
    
    var body: some View {
        ZStack {
            Group {
                if !disclaimerAccepted {
                    // Must show disclaimer first - legal compliance
                    DisclaimerView(
                        onAccept: {
                            disclaimerAccepted = true
                        },
                        onDecline: {
                            // Exit app - user declined
                            exit(0)
                        }
                    )
                    .transition(.opacity)
                } else if authManager.isAuthenticated {
                    MainTabView()
                        .transition(.opacity)
                } else {
                    LoginView()
                        .transition(.opacity)
                }
            }
            
            // In-app notification banner overlay
            NotificationBannerView()
        }
        .animation(.easeInOut(duration: 0.3), value: authManager.isAuthenticated)
        .animation(.easeInOut(duration: 0.3), value: disclaimerAccepted)
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
