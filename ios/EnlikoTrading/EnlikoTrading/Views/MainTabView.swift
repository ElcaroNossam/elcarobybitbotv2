//
//  MainTabView.swift
//  EnlikoTrading
//
//  Modern tab navigation with sleek design
//  Custom tab bar with glass morphism effect
//

import SwiftUI

struct MainTabView: View {
    @State private var selectedTab = 0
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    @State private var showAICopilot = false
    @State private var showConfetti = false
    @State private var showRadialMenu = false
    
    var body: some View {
        ZStack(alignment: .bottom) {
            // Content
            TabView(selection: $selectedTab) {
                // Portfolio Tab - Modern Version
                NavigationStack {
                    ModernPortfolioView()
                }
                .tag(0)
                
                // Trading Tab - Modern Version
                NavigationStack {
                    ModernTradingView()
                }
                .tag(1)
                
                // Positions Tab - Modern Version
                NavigationStack {
                    ModernPositionsView()
                }
                .tag(2)
                
                // More Tab (contains additional features)
                MoreView()
                .tag(3)
                
                // Settings Tab
                SettingsView()
                .tag(4)
            }
            .tabViewStyle(.page(indexDisplayMode: .never))
            
            // Custom Tab Bar
            customTabBar
            
            // 🔥 NEW: Floating AI Copilot Button
            VStack {
                Spacer()
                HStack {
                    Spacer()
                    FloatingCopilotButton(isOpen: $showAICopilot)
                        .padding(.trailing, 16)
                        .padding(.bottom, 100) // Above tab bar
                }
            }
            
            // 🔥 NEW: Floating Radial Menu (hold for quick actions)
            if showRadialMenu {
                FloatingRadialMenu(
                    isOpen: $showRadialMenu,
                    items: [
                        FloatingRadialMenu.RadialMenuItem(
                            icon: "arrow.up.right",
                            color: .enlikoGreen,
                            action: {
                                HapticManager.shared.perform(.success)
                            }
                        ),
                        FloatingRadialMenu.RadialMenuItem(
                            icon: "arrow.down.right",
                            color: .enlikoRed,
                            action: {
                                HapticManager.shared.perform(.warning)
                            }
                        ),
                        FloatingRadialMenu.RadialMenuItem(
                            icon: "dollarsign.circle",
                            color: .enlikoAccent,
                            action: {
                                selectedTab = 0
                            }
                        ),
                        FloatingRadialMenu.RadialMenuItem(
                            icon: "chart.line.uptrend.xyaxis",
                            color: .enlikoPrimary,
                            action: {
                                // Navigate to charts
                            }
                        )
                    ]
                )
            }
            
            // 🔥 NEW: Confetti celebration overlay
            if showConfetti {
                ConfettiView()
                    .allowsHitTesting(false)
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
        // 🔥 NEW: Listen for profit milestones to trigger confetti
        .onReceive(NotificationCenter.default.publisher(for: .profitMilestoneReached)) { _ in
            triggerCelebration()
        }
        // 🔥 NEW: Long press anywhere to show radial menu
        .gesture(
            LongPressGesture(minimumDuration: 0.5)
                .onEnded { _ in
                    showRadialMenu = true
                    HapticManager.shared.perform(.heavy)
                }
        )
    }
    
    // 🔥 NEW: Celebration function
    private func triggerCelebration() {
        showConfetti = true
        SoundManager.shared.play(.profitClose)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            showConfetti = false
        }
    }
    
    // MARK: - Custom Tab Bar
    private var customTabBar: some View {
        HStack(spacing: 0) {
            tabBarItem(icon: "chart.pie.fill", label: "nav_portfolio".localized, index: 0)
            tabBarItem(icon: "arrow.up.arrow.down", label: "nav_trading".localized, index: 1, isPrimary: true)
            tabBarItem(icon: "list.bullet.rectangle.fill", label: "nav_positions".localized, index: 2)
            tabBarItem(icon: "square.grid.2x2.fill", label: "nav_more".localized, index: 3)
            tabBarItem(icon: "gearshape.fill", label: "nav_settings".localized, index: 4)
        }
        .padding(.horizontal, 8)
        .padding(.top, 12)
        .padding(.bottom, 24)
        .background(
            ZStack {
                // Blur background
                Rectangle()
                    .fill(.ultraThinMaterial)
                
                // Top border glow
                VStack {
                    Rectangle()
                        .fill(
                            LinearGradient(
                                colors: [Color.enlikoPrimary.opacity(0.3), Color.clear],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )
                        .frame(height: 1)
                    Spacer()
                }
            }
        )
    }
    
    private func tabBarItem(icon: String, label: String, index: Int, isPrimary: Bool = false) -> some View {
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
                        Image(systemName: icon)
                            .font(.system(size: 22, weight: isSelected ? .semibold : .regular))
                            .foregroundColor(isSelected ? .enlikoPrimary : .enlikoTextSecondary)
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
                // 🔥 NEW: AI Copilot - Premium Feature
                Section(header: Text("✨ Premium Features")) {
                    NavigationLink(destination: AICopilotView()) {
                        MoreMenuItem(
                            icon: "sparkles",
                            title: "AI Trading Copilot",
                            subtitle: "Smart trading assistant",
                            color: .purple
                        )
                    }
                    
                    // 🔥 NEW: Market Heatmap
                    NavigationLink(destination: MarketHeatmapView()) {
                        MoreMenuItem(
                            icon: "square.grid.3x3.fill",
                            title: "Market Heatmap",
                            subtitle: "Visual market overview",
                            color: .orange
                        )
                    }
                    
                    // 🔥 NEW: Advanced Charts
                    NavigationLink(destination: AdvancedChartsView(symbol: "BTCUSDT")) {
                        MoreMenuItem(
                            icon: "chart.xyaxis.line",
                            title: "Pro Charts",
                            subtitle: "TradingView-style analysis",
                            color: .blue
                        )
                    }
                }
                
                Section(header: Text("Trading")) {
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

#Preview {
    MainTabView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
