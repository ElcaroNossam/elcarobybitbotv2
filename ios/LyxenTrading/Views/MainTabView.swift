//
//  MainTabView.swift
//  LyxenTrading
//
//  Main tab navigation with all features and localization
//

import SwiftUI

struct MainTabView: View {
    @State private var selectedTab = 0
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Portfolio Tab
            PortfolioView()
                .tabItem {
                    Label("nav_portfolio".localized, systemImage: "chart.pie.fill")
                }
                .tag(0)
            
            // Trading Tab
            TradingView()
                .tabItem {
                    Label("nav_trading".localized, systemImage: "arrow.left.arrow.right")
                }
                .tag(1)
            
            // Positions Tab
            PositionsView()
                .tabItem {
                    Label("nav_positions".localized, systemImage: "list.bullet.rectangle")
                }
                .tag(2)
            
            // More Tab (contains additional features)
            MoreView()
                .tabItem {
                    Label("nav_more".localized, systemImage: "square.grid.2x2.fill")
                }
                .tag(3)
            
            // Settings Tab
            SettingsView()
                .tabItem {
                    Label("nav_settings".localized, systemImage: "gearshape.fill")
                }
                .tag(4)
        }
        .tint(Color.lyxenPrimary)
        .withRTLSupport()
        .onAppear {
            Task {
                await tradingService.refreshAll()
                await tradingService.fetchSymbols()
            }
        }
    }
}

// MARK: - More View (Hub for additional features)
struct MoreView: View {
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        NavigationView {
            List {
                // Strategies
                NavigationLink(destination: StrategiesView()) {
                    MoreMenuItem(
                        icon: "brain",
                        title: "AI Strategies",
                        subtitle: "Manage trading strategies",
                        color: .purple
                    )
                }
                
                // Statistics
                NavigationLink(destination: StatsView()) {
                    MoreMenuItem(
                        icon: "chart.bar.fill",
                        title: "stats_title".localized,
                        subtitle: "Trading performance analytics",
                        color: .blue
                    )
                }
                
                // Screener
                NavigationLink(destination: ScreenerView()) {
                    MoreMenuItem(
                        icon: "magnifyingglass.circle.fill",
                        title: "screener_title".localized,
                        subtitle: "Market scanner & filters",
                        color: .orange
                    )
                }
                
                // AI Analysis
                NavigationLink(destination: AIView()) {
                    MoreMenuItem(
                        icon: "cpu",
                        title: "ai_title".localized,
                        subtitle: "AI-powered market insights",
                        color: .green
                    )
                }
                
                // Signals
                NavigationLink(destination: SignalsView()) {
                    MoreMenuItem(
                        icon: "bell.fill",
                        title: "signals_title".localized,
                        subtitle: "Trading signals & alerts",
                        color: .red
                    )
                }
                
                // Activity (Cross-platform sync)
                NavigationLink(destination: ActivityView()) {
                    MoreMenuItem(
                        icon: "arrow.triangle.2.circlepath",
                        title: "activity_title".localized,
                        subtitle: "Cross-platform sync history",
                        color: .cyan
                    )
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

#Preview {
    MainTabView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
