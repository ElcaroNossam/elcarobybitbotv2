//
//  MainTabView.swift
//  LyxenTrading
//
//  Main tab navigation with all features
//

import SwiftUI

struct MainTabView: View {
    @State private var selectedTab = 0
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Portfolio Tab
            PortfolioView()
                .tabItem {
                    Label("Portfolio", systemImage: "chart.pie.fill")
                }
                .tag(0)
            
            // Trading Tab
            TradingView()
                .tabItem {
                    Label("Trade", systemImage: "arrow.left.arrow.right")
                }
                .tag(1)
            
            // Positions Tab
            PositionsView()
                .tabItem {
                    Label("Positions", systemImage: "list.bullet.rectangle")
                }
                .tag(2)
            
            // More Tab (contains additional features)
            MoreView()
                .tabItem {
                    Label("More", systemImage: "square.grid.2x2.fill")
                }
                .tag(3)
            
            // Settings Tab
            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gearshape.fill")
                }
                .tag(4)
        }
        .tint(Color.lyxenPrimary)
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
                        title: "Statistics",
                        subtitle: "Trading performance analytics",
                        color: .blue
                    )
                }
                
                // Screener
                NavigationLink(destination: ScreenerView()) {
                    MoreMenuItem(
                        icon: "magnifyingglass.circle.fill",
                        title: "Screener",
                        subtitle: "Market scanner & filters",
                        color: .orange
                    )
                }
                
                // AI Analysis
                NavigationLink(destination: AIView()) {
                    MoreMenuItem(
                        icon: "cpu",
                        title: "AI Analysis",
                        subtitle: "AI-powered market insights",
                        color: .green
                    )
                }
                
                // Signals
                NavigationLink(destination: SignalsView()) {
                    MoreMenuItem(
                        icon: "bell.fill",
                        title: "Signals",
                        subtitle: "Trading signals & alerts",
                        color: .red
                    )
                }
                
                // Activity (Cross-platform sync)
                NavigationLink(destination: ActivityView()) {
                    MoreMenuItem(
                        icon: "arrow.triangle.2.circlepath",
                        title: "Activity",
                        subtitle: "Cross-platform sync history",
                        color: .cyan
                    )
                }
            }
            .listStyle(InsetGroupedListStyle())
            .navigationTitle("More")
        }
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
