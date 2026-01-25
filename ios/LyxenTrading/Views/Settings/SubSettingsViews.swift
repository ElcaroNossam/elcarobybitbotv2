//
//  SubSettingsViews.swift
//  LyxenTrading
//
//  Additional settings screens
//

import SwiftUI

// MARK: - Exchange Settings View
struct ExchangeSettingsView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            Color.lyxenBackground.ignoresSafeArea()
            
            List {
                Section {
                    ForEach(Exchange.allCases, id: \.self) { exchange in
                        Button(action: { 
                            appState.switchExchange(to: exchange)
                            dismiss()
                        }) {
                            HStack {
                                Text(exchange.icon)
                                    .font(.title2)
                                
                                VStack(alignment: .leading) {
                                    Text(exchange.displayName)
                                        .foregroundColor(.white)
                                    Text(exchange == .bybit ? "Demo & Real accounts" : "Testnet & Mainnet")
                                        .font(.caption)
                                        .foregroundColor(.lyxenTextSecondary)
                                }
                                
                                Spacer()
                                
                                if appState.currentExchange == exchange {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.lyxenPrimary)
                                }
                            }
                        }
                    }
                } header: {
                    Text("Select Exchange")
                }
                .listRowBackground(Color.lyxenCard)
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
        }
        .navigationTitle("Exchange")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Leverage Settings View
struct LeverageSettingsView: View {
    @State private var selectedLeverage: Double = 10
    
    var body: some View {
        ZStack {
            Color.lyxenBackground.ignoresSafeArea()
            
            VStack(spacing: 24) {
                // Current Leverage
                VStack(spacing: 8) {
                    Text("Default Leverage")
                        .font(.headline)
                        .foregroundColor(.lyxenTextSecondary)
                    
                    Text("\(Int(selectedLeverage))x")
                        .font(.system(size: 48, weight: .bold, design: .rounded))
                        .foregroundColor(.lyxenPrimary)
                }
                .padding(.top, 40)
                
                // Slider
                VStack(spacing: 12) {
                    Slider(value: $selectedLeverage, in: 1...100, step: 1)
                        .tint(.lyxenPrimary)
                    
                    HStack {
                        Text("1x")
                        Spacer()
                        Text("25x")
                        Spacer()
                        Text("50x")
                        Spacer()
                        Text("75x")
                        Spacer()
                        Text("100x")
                    }
                    .font(.caption)
                    .foregroundColor(.lyxenTextSecondary)
                }
                .padding()
                .background(Color.lyxenCard)
                .cornerRadius(12)
                .padding(.horizontal)
                
                // Quick Select Buttons
                HStack(spacing: 12) {
                    ForEach([5, 10, 20, 50], id: \.self) { lev in
                        Button(action: { selectedLeverage = Double(lev) }) {
                            Text("\(lev)x")
                                .font(.headline)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(selectedLeverage == Double(lev) ? Color.lyxenPrimary : Color.lyxenCard)
                                .foregroundColor(selectedLeverage == Double(lev) ? .white : .lyxenTextSecondary)
                                .cornerRadius(10)
                        }
                    }
                }
                .padding(.horizontal)
                
                // Warning
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.lyxenYellow)
                    Text("Higher leverage increases risk of liquidation")
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                }
                .padding()
                .background(Color.lyxenYellow.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)
                
                Spacer()
            }
        }
        .navigationTitle("Leverage")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Risk Settings View
struct RiskSettingsView: View {
    @State private var entryPercent: Double = 1.0
    @State private var takeProfitPercent: Double = 8.0
    @State private var stopLossPercent: Double = 3.0
    @State private var useATR = false
    @State private var dcaEnabled = false
    
    var body: some View {
        ZStack {
            Color.lyxenBackground.ignoresSafeArea()
            
            List {
                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Entry %")
                            Spacer()
                            Text("\(entryPercent, specifier: "%.1f")%")
                                .foregroundColor(.lyxenPrimary)
                        }
                        Slider(value: $entryPercent, in: 0.1...10, step: 0.1)
                            .tint(.lyxenPrimary)
                    }
                    .padding(.vertical, 4)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Take Profit %")
                            Spacer()
                            Text("\(takeProfitPercent, specifier: "%.1f")%")
                                .foregroundColor(.lyxenGreen)
                        }
                        Slider(value: $takeProfitPercent, in: 1...50, step: 0.5)
                            .tint(.lyxenGreen)
                    }
                    .padding(.vertical, 4)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Stop Loss %")
                            Spacer()
                            Text("\(stopLossPercent, specifier: "%.1f")%")
                                .foregroundColor(.lyxenRed)
                        }
                        Slider(value: $stopLossPercent, in: 0.5...20, step: 0.5)
                            .tint(.lyxenRed)
                    }
                    .padding(.vertical, 4)
                } header: {
                    Text("Position Sizing")
                }
                .listRowBackground(Color.lyxenCard)
                
                Section {
                    Toggle("Use ATR for SL/TP", isOn: $useATR)
                        .tint(.lyxenPrimary)
                    Toggle("Enable DCA", isOn: $dcaEnabled)
                        .tint(.lyxenPrimary)
                } header: {
                    Text("Advanced")
                } footer: {
                    Text("ATR adjusts SL/TP based on market volatility. DCA adds to positions at drawdown levels.")
                }
                .listRowBackground(Color.lyxenCard)
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
        }
        .navigationTitle("Risk Management")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Notification Settings View
struct NotificationSettingsView: View {
    @State private var tradeAlerts = true
    @State private var priceAlerts = true
    @State private var signalAlerts = true
    @State private var dailySummary = false
    
    var body: some View {
        ZStack {
            Color.lyxenBackground.ignoresSafeArea()
            
            List {
                Section {
                    Toggle("Trade Alerts", isOn: $tradeAlerts)
                    Toggle("Price Alerts", isOn: $priceAlerts)
                    Toggle("Signal Alerts", isOn: $signalAlerts)
                } header: {
                    Text("Trading")
                }
                .listRowBackground(Color.lyxenCard)
                
                Section {
                    Toggle("Daily Summary", isOn: $dailySummary)
                } header: {
                    Text("Reports")
                }
                .listRowBackground(Color.lyxenCard)
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
            .tint(.lyxenPrimary)
        }
        .navigationTitle("Notifications")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Appearance Settings View
struct AppearanceSettingsView: View {
    @State private var selectedTheme = "dark"
    
    var body: some View {
        ZStack {
            Color.lyxenBackground.ignoresSafeArea()
            
            List {
                Section {
                    ForEach(["dark", "light", "system"], id: \.self) { theme in
                        Button(action: { selectedTheme = theme }) {
                            HStack {
                                Image(systemName: themeIcon(theme))
                                    .foregroundColor(.lyxenPrimary)
                                    .frame(width: 28)
                                
                                Text(theme.capitalized)
                                    .foregroundColor(.white)
                                
                                Spacer()
                                
                                if selectedTheme == theme {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.lyxenPrimary)
                                }
                            }
                        }
                    }
                } header: {
                    Text("Theme")
                } footer: {
                    Text("Dark mode is recommended for trading.")
                }
                .listRowBackground(Color.lyxenCard)
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
        }
        .navigationTitle("Appearance")
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private func themeIcon(_ theme: String) -> String {
        switch theme {
        case "dark": return "moon.fill"
        case "light": return "sun.max.fill"
        default: return "gear"
        }
    }
}

// MARK: - About View
struct AboutView: View {
    var body: some View {
        ZStack {
            Color.lyxenBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 24) {
                    // Logo
                    ZStack {
                        Circle()
                            .fill(Color.lyxenGradient)
                            .frame(width: 100, height: 100)
                        
                        Image(systemName: "chart.line.uptrend.xyaxis")
                            .font(.system(size: 44))
                            .foregroundColor(.white)
                    }
                    .padding(.top, 40)
                    
                    VStack(spacing: 8) {
                        Text("LYXEN")
                            .font(.title.bold())
                            .foregroundColor(.white)
                        
                        Text("Professional Trading Platform")
                            .font(.subheadline)
                            .foregroundColor(.lyxenTextSecondary)
                        
                        Text("Version 1.0.0 (1)")
                            .font(.caption)
                            .foregroundColor(.lyxenTextMuted)
                    }
                    
                    // Links
                    VStack(spacing: 0) {
                        linkRow(icon: "globe", title: "Website", url: "https://lyxen.io")
                        Divider().background(Color.lyxenCardHover)
                        linkRow(icon: "envelope", title: "Support", url: "mailto:support@lyxen.io")
                        Divider().background(Color.lyxenCardHover)
                        linkRow(icon: "bubble.left", title: "Telegram", url: "https://t.me/lyxen_trading")
                    }
                    .background(Color.lyxenCard)
                    .cornerRadius(12)
                    .padding(.horizontal)
                    
                    Text("© 2026 Lyxen Trading. All rights reserved.")
                        .font(.caption)
                        .foregroundColor(.lyxenTextMuted)
                        .padding(.top, 20)
                    
                    Spacer()
                }
            }
        }
        .navigationTitle("About")
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private func linkRow(icon: String, title: String, url: String) -> some View {
        Link(destination: URL(string: url)!) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(.lyxenPrimary)
                    .frame(width: 28)
                
                Text(title)
                    .foregroundColor(.white)
                
                Spacer()
                
                Image(systemName: "arrow.up.right")
                    .font(.caption)
                    .foregroundColor(.lyxenTextSecondary)
            }
            .padding()
        }
    }
}

// MARK: - API Keys Sheet
struct APIKeysSheetView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var bybitDemoKey = ""
    @State private var bybitDemoSecret = ""
    @State private var bybitRealKey = ""
    @State private var bybitRealSecret = ""
    @State private var hlPrivateKey = ""
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.lyxenBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Tab Selector
                    Picker("Exchange", selection: $selectedTab) {
                        Text("Bybit").tag(0)
                        Text("HyperLiquid").tag(1)
                    }
                    .pickerStyle(.segmented)
                    .padding()
                    
                    ScrollView {
                        if selectedTab == 0 {
                            bybitSection
                        } else {
                            hyperliquidSection
                        }
                    }
                }
            }
            .navigationTitle("API Keys")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(.lyxenTextSecondary)
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Save") { saveKeys() }
                        .foregroundColor(.lyxenPrimary)
                        .fontWeight(.semibold)
                }
            }
        }
    }
    
    private var bybitSection: some View {
        VStack(spacing: 20) {
            // Demo Account
            VStack(alignment: .leading, spacing: 12) {
                Label("Demo Account", systemImage: "gamecontroller.fill")
                    .font(.headline)
                    .foregroundColor(.lyxenTextSecondary)
                
                SecureInputField(placeholder: "API Key", text: $bybitDemoKey)
                SecureInputField(placeholder: "API Secret", text: $bybitDemoSecret)
            }
            .padding()
            .background(Color.lyxenCard)
            .cornerRadius(12)
            
            // Real Account
            VStack(alignment: .leading, spacing: 12) {
                Label("Real Account", systemImage: "dollarsign.circle.fill")
                    .font(.headline)
                    .foregroundColor(.lyxenYellow)
                
                SecureInputField(placeholder: "API Key", text: $bybitRealKey)
                SecureInputField(placeholder: "API Secret", text: $bybitRealSecret)
                
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.lyxenYellow)
                    Text("Use IP whitelist for security")
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                }
            }
            .padding()
            .background(Color.lyxenCard)
            .cornerRadius(12)
        }
        .padding()
    }
    
    private var hyperliquidSection: some View {
        VStack(spacing: 20) {
            VStack(alignment: .leading, spacing: 12) {
                Label("HyperLiquid", systemImage: "link.circle.fill")
                    .font(.headline)
                    .foregroundColor(.lyxenBlue)
                
                SecureInputField(placeholder: "Private Key (0x...)", text: $hlPrivateKey)
                
                Text("Enter your wallet private key. Never share this with anyone.")
                    .font(.caption)
                    .foregroundColor(.lyxenTextSecondary)
            }
            .padding()
            .background(Color.lyxenCard)
            .cornerRadius(12)
        }
        .padding()
    }
    
    private func saveKeys() {
        // TODO: Save to backend
        dismiss()
    }
}

// MARK: - Secure Input Field
struct SecureInputField: View {
    let placeholder: String
    @Binding var text: String
    @State private var isSecure = true
    
    var body: some View {
        HStack {
            if isSecure {
                SecureField(placeholder, text: $text)
            } else {
                TextField(placeholder, text: $text)
            }
            
            Button(action: { isSecure.toggle() }) {
                Image(systemName: isSecure ? "eye.slash" : "eye")
                    .foregroundColor(.lyxenTextSecondary)
            }
        }
        .padding()
        .background(Color.lyxenSurface)
        .foregroundColor(.white)
        .cornerRadius(10)
    }
}

// MARK: - API Key Type
enum APIKeyType {
    case bybitDemo
    case bybitReal
    case hyperliquid
}

#Preview("Exchange Settings") {
    NavigationStack {
        ExchangeSettingsView()
            .environmentObject(AppState.shared)
    }
    .preferredColorScheme(.dark)
}

#Preview("About") {
    NavigationStack {
        AboutView()
    }
    .preferredColorScheme(.dark)
}
