//
//  MainTabView.swift
//  EnlikoTrading
//
//  UPDATED: 4 tabs matching Telegram bot structure
//  Dashboard (Profile) | Positions | Trading | Settings
//  With proper safe area handling for tab bar
//

import SwiftUI

struct MainTabView: View {
    @State private var selectedTab = 0
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    @State private var showAICopilot = false
    @State private var showConfetti = false
    
    // Tab bar height for safe area calculations
    private let tabBarHeight: CGFloat = 85
    
    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .bottom) {
                // Content - 4 main tabs matching bot structure
                TabView(selection: $selectedTab) {
                    // Dashboard Tab (like Profile in bot - Balance + Stats + History)
                    NavigationStack {
                        DashboardView()
                    }
                    .tag(0)
                    
                    // Positions + Orders Tab (combined)
                    NavigationStack {
                        PositionsOrdersView()
                    }
                    .tag(1)
                    
                    // Trading Tab (Terminal)
                    NavigationStack {
                        TradingView()
                    }
                    .tag(2)
                    
                    // Settings Tab (API Keys + Strategy Settings prominent)
                    NavigationStack {
                        SettingsMainView()
                    }
                    .tag(3)
                }
                
                // Custom Tab Bar - Fixed safe area
                customTabBar
                    .frame(width: geometry.size.width)
                
                // 🔥 Floating AI Copilot Button
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        FloatingCopilotButton(isOpen: $showAICopilot)
                            .padding(.trailing, 16)
                            .padding(.bottom, tabBarHeight + 20) // Above tab bar
                    }
                }
                
                // Confetti celebration overlay
                if showConfetti {
                    ConfettiView()
                        .allowsHitTesting(false)
                }
            }
        }
        .ignoresSafeArea(.keyboard)
        .withRTLSupport()
        .sheet(isPresented: $showAICopilot) {
            AICopilotView()
        }
        .onAppear {
            Task {
                await tradingService.refreshAll()
                await tradingService.fetchSymbols()
            }
        }
        // Global exchange/account change handler
        .onChange(of: appState.currentExchange) { _, _ in
            Task { await tradingService.refreshAll() }
        }
        .onChange(of: appState.currentAccountType) { _, _ in
            Task { await tradingService.refreshAll() }
        }
        // Listen for profit milestones to trigger confetti
        .onReceive(NotificationCenter.default.publisher(for: .profitMilestoneReached)) { _ in
            triggerCelebration()
        }
    }
    
    // Celebration function
    private func triggerCelebration() {
        showConfetti = true
        SoundManager.shared.play(.profitClose)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            showConfetti = false
        }
    }
    
    // MARK: - Custom Tab Bar (4 tabs - bot structure)
    private var customTabBar: some View {
        VStack(spacing: 0) {
            // Top border
            Rectangle()
                .fill(
                    LinearGradient(
                        colors: [Color.enlikoPrimary.opacity(0.4), Color.enlikoPrimary.opacity(0.1)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .frame(height: 1)
            
            HStack(spacing: 0) {
                // Dashboard (Portfolio/Profile)
                tabBarItem(icon: "person.crop.circle.fill", label: "dashboard".localized, index: 0)
                
                // Positions + Orders
                tabBarItem(icon: "list.bullet.rectangle.fill", label: "positions".localized, index: 1, 
                          badge: tradingService.positions.count)
                
                // Trading (Terminal) - Primary action
                tabBarItem(icon: "arrow.up.arrow.down", label: "trading".localized, index: 2, isPrimary: true)
                
                // Settings
                tabBarItem(icon: "gearshape.fill", label: "settings".localized, index: 3)
            }
            .padding(.horizontal, 8)
            .padding(.top, 8)
            .padding(.bottom, 30) // Safe area for home indicator
        }
        .background(
            Rectangle()
                .fill(.ultraThinMaterial)
                .background(Color.enlikoBackground.opacity(0.9))
        )
    }
    
    private func tabBarItem(icon: String, label: String, index: Int, isPrimary: Bool = false, badge: Int = 0) -> some View {
        let isSelected = selectedTab == index
        
        return Button(action: {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                selectedTab = index
            }
            HapticManager.shared.perform(.selection)
        }) {
            VStack(spacing: 4) {
                ZStack {
                    if isPrimary {
                        // Special trading button
                        Circle()
                            .fill(
                                LinearGradient(
                                    colors: isSelected ? [Color.enlikoPrimary, Color.enlikoPrimary.opacity(0.8)] : [Color.enlikoCard],
                                    startPoint: .top,
                                    endPoint: .bottom
                                )
                            )
                            .frame(width: 50, height: 50)
                            .shadow(color: isSelected ? .enlikoPrimary.opacity(0.5) : .clear, radius: 10, y: 5)
                        
                        Image(systemName: icon)
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.white)
                    } else {
                        ZStack(alignment: .topTrailing) {
                            Image(systemName: icon)
                                .font(.system(size: 22, weight: isSelected ? .semibold : .regular))
                                .foregroundColor(isSelected ? .enlikoPrimary : .enlikoTextSecondary)
                            
                            // Badge for positions count
                            if badge > 0 {
                                Text("\(badge)")
                                    .font(.system(size: 10, weight: .bold))
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 5)
                                    .padding(.vertical, 2)
                                    .background(Color.enlikoPrimary)
                                    .clipShape(Capsule())
                                    .offset(x: 10, y: -5)
                            }
                        }
                    }
                }
                .frame(height: 50)
                
                if !isPrimary {
                    Text(label)
                        .font(.system(size: 10, weight: isSelected ? .semibold : .regular))
                        .foregroundColor(isSelected ? .enlikoPrimary : .enlikoTextSecondary)
                }
            }
            .frame(maxWidth: .infinity)
        }
    }
}

// MARK: - More View (Hub for additional features)
struct MoreView: View {
    @ObservedObject var localization = LocalizationManager.shared
    @State private var showAICopilot = false
    
    var body: some View {
        NavigationView {
            List {
                // 🔥 Premium Features Section (some features in beta)
                Section(header: Text("✨ Premium Features")) {
                    // AI Copilot - Live feature
                    NavigationLink(destination: AICopilotView()) {
                        MoreMenuItem(
                            icon: "sparkles",
                            title: "AI Trading Copilot",
                            subtitle: "Smart trading assistant",
                            color: .purple
                        )
                    }
                    
                    // Market Heatmap - Beta (uses fallback data)
                    NavigationLink(destination: MarketHeatmapView()) {
                        MoreMenuItemWithBeta(
                            icon: "square.grid.3x3.fill",
                            title: "Market Heatmap",
                            subtitle: "Visual market overview",
                            color: .orange,
                            isBeta: true
                        )
                    }
                    
                    // Social Trading - Coming Soon (mock data)
                    NavigationLink(destination: SocialTradingView()) {
                        MoreMenuItemWithBeta(
                            icon: "person.2.fill",
                            title: "Social Trading",
                            subtitle: "Copy top traders",
                            color: .green,
                            isBeta: true,
                            isComingSoon: true
                        )
                    }
                }
                
                Section(header: Text("Trading")) {
                    // Spot Trading - NEW!
                    NavigationLink(destination: SpotTradingView()) {
                        MoreMenuItem(
                            icon: "dollarsign.circle.fill",
                            title: "spot_trading".localized,
                            subtitle: "spot_trading_subtitle".localized,
                            color: .orange
                        )
                    }
                    
                    // Strategies
                    NavigationLink(destination: StrategiesView()) {
                        MoreMenuItem(
                            icon: "brain",
                            title: "strategies_title".localized,
                            subtitle: "strategies_subtitle".localized,
                            color: .purple
                        )
                    }
                    
                    // Signals
                    NavigationLink(destination: SignalsView()) {
                        MoreMenuItem(
                            icon: "bell.fill",
                            title: "signals_title".localized,
                            subtitle: "signals_subtitle".localized,
                            color: .red
                        )
                    }
                    
                    // Screener
                    NavigationLink(destination: ScreenerView()) {
                        MoreMenuItem(
                            icon: "magnifyingglass.circle.fill",
                            title: "screener_title".localized,
                            subtitle: "screener_subtitle".localized,
                            color: .orange
                        )
                    }
                }
                
                Section(header: Text("Analytics")) {
                    // Statistics
                    NavigationLink(destination: StatsView()) {
                        MoreMenuItem(
                            icon: "chart.bar.fill",
                            title: "stats_title".localized,
                            subtitle: "stats_subtitle".localized,
                            color: .blue
                        )
                    }
                    
                    // AI Analysis
                    NavigationLink(destination: AIView()) {
                        MoreMenuItem(
                            icon: "cpu",
                            title: "ai_title".localized,
                            subtitle: "ai_subtitle".localized,
                            color: .green
                        )
                    }
                }
                
                Section(header: Text("Sync & Notifications")) {
                    // Activity (Cross-platform sync)
                    NavigationLink(destination: ActivityView()) {
                        MoreMenuItem(
                            icon: "arrow.triangle.2.circlepath",
                            title: "activity_title".localized,
                            subtitle: "activity_subtitle".localized,
                            color: .cyan
                        )
                    }
                    
                    // Notifications
                    NavigationLink(destination: NotificationsView()) {
                        MoreMenuItemWithBadge(
                            icon: "bell.badge.fill",
                            title: "notifications".localized,
                            subtitle: "notifications_subtitle".localized,
                            color: .yellow,
                            badgeCount: PushNotificationService.shared.unreadCount
                        )
                    }
                }
                
                // 🔥 NEW: Siri Shortcuts Guide
                Section(header: Text("Quick Access")) {
                    if #available(iOS 16.0, *) {
                        NavigationLink(destination: ShortcutsTestView()) {
                            MoreMenuItem(
                                icon: "mic.fill",
                                title: "Siri Shortcuts",
                                subtitle: "Voice commands setup",
                                color: .pink
                            )
                        }
                    }
                }
            }
            .listStyle(InsetGroupedListStyle())
            .navigationTitle("nav_more".localized)
        }
        .withRTLSupport()
    }
}

struct MoreMenuItem: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.white)
                .frame(width: 44, height: 44)
                .background(color)
                .cornerRadius(10)
            
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

struct MoreMenuItemWithBadge: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    let badgeCount: Int
    
    var body: some View {
        HStack(spacing: 16) {
            ZStack(alignment: .topTrailing) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(color)
                    .cornerRadius(10)
                
                if badgeCount > 0 {
                    Text("\(badgeCount > 99 ? "99+" : "\(badgeCount)")")
                        .font(.system(size: 10, weight: .bold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 5)
                        .padding(.vertical, 2)
                        .background(Color.red)
                        .clipShape(Capsule())
                        .offset(x: 8, y: -6)
                }
            }
            
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

// MARK: - Beta/Coming Soon Menu Item
struct MoreMenuItemWithBeta: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    var isBeta: Bool = false
    var isComingSoon: Bool = false
    
    var body: some View {
        HStack(spacing: 16) {
            ZStack(alignment: .topTrailing) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(isComingSoon ? color.opacity(0.5) : color)
                    .cornerRadius(10)
                
                if isBeta || isComingSoon {
                    Text(isComingSoon ? "SOON" : "BETA")
                        .font(.system(size: 8, weight: .bold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 4)
                        .padding(.vertical, 2)
                        .background(isComingSoon ? Color.orange : Color.blue)
                        .clipShape(Capsule())
                        .offset(x: 8, y: -6)
                }
            }
            
            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(isComingSoon ? .secondary : .primary)
                }
                Text(isComingSoon ? "Coming soon!" : subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            if isComingSoon {
                Spacer()
                Image(systemName: "clock.fill")
                    .foregroundColor(.orange)
                    .font(.caption)
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    MainTabView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
