//
//  MainTabView.swift
//  LyxenTrading
//
//  Main tab navigation
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
            
            // Strategies Tab
            StrategiesView()
                .tabItem {
                    Label("Strategies", systemImage: "brain")
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

#Preview {
    MainTabView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
