//
//  StrategiesHubView.swift
//  EnlikoTrading
//
//  Strategies Hub - like Telegram bot strategy management:
//  - List of all strategies with quick toggles
//  - Per-strategy settings access
//  - Quick status overview
//

import SwiftUI
import Combine

struct StrategiesHubView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = StrategiesHubViewModel()
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Exchange/Account Switcher
                exchangeAccountSwitcher
                
                // Quick Actions
                quickActionsSection
                
                // Strategies List
                strategiesListSection
            }
            .padding()
        }
        .background(Color.enlikoBackground)
        .navigationTitle("strategies".localized)
        .navigationBarTitleDisplayMode(.large)
        .refreshable {
            await viewModel.loadStrategies(
                exchange: appState.currentExchange,
                accountType: appState.currentAccountType
            )
        }
        .onAppear {
            Task {
                await viewModel.loadStrategies(
                    exchange: appState.currentExchange,
                    accountType: appState.currentAccountType
                )
            }
        }
        .onChange(of: appState.currentExchange) { _, newExchange in
            Task {
                await viewModel.loadStrategies(
                    exchange: newExchange,
                    accountType: appState.currentAccountType
                )
            }
        }
        .onChange(of: appState.currentAccountType) { _, newAccount in
            Task {
                await viewModel.loadStrategies(
                    exchange: appState.currentExchange,
                    accountType: newAccount
                )
            }
        }
    }
    
    // MARK: - Exchange/Account Switcher
    private var exchangeAccountSwitcher: some View {
        HStack(spacing: 12) {
            // Exchange Picker
            Menu {
                Button {
                    appState.switchExchange(to: .bybit)
                } label: {
                    HStack {
                        Text("🟠 Bybit")
                        if appState.currentExchange == .bybit {
                            Image(systemName: "checkmark")
                        }
                    }
                }
                Button {
                    appState.switchExchange(to: .hyperliquid)
                } label: {
                    HStack {
                        Text("🔷 HyperLiquid")
                        if appState.currentExchange == .hyperliquid {
                            Image(systemName: "checkmark")
                        }
                    }
                }
            } label: {
                HStack(spacing: 6) {
                    Circle()
                        .fill(appState.currentExchange == .bybit ? Color.orange : Color.cyan)
                        .frame(width: 10, height: 10)
                    Text(appState.currentExchange.displayName)
                        .font(.subheadline.bold())
                    Image(systemName: "chevron.down")
                        .font(.caption)
                }
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color.enlikoSurface)
                .cornerRadius(20)
            }
            
            // Account Type Picker
            Menu {
                if appState.currentExchange == .bybit {
                    Button { appState.switchAccountType(to: .demo) } label: {
                        HStack {
                            Text("🎮 Demo")
                            if appState.currentAccountType == .demo { Image(systemName: "checkmark") }
                        }
                    }
                    Button { appState.switchAccountType(to: .real) } label: {
                        HStack {
                            Text("💎 Real")
                            if appState.currentAccountType == .real { Image(systemName: "checkmark") }
                        }
                    }
                } else {
                    Button { appState.switchAccountType(to: .testnet) } label: {
                        HStack {
                            Text("🧪 Testnet")
                            if appState.currentAccountType == .testnet { Image(systemName: "checkmark") }
                        }
                    }
                    Button { appState.switchAccountType(to: .mainnet) } label: {
                        HStack {
                            Text("🌐 Mainnet")
                            if appState.currentAccountType == .mainnet { Image(systemName: "checkmark") }
                        }
                    }
                }
            } label: {
                HStack(spacing: 6) {
                    Circle()
                        .fill(accountTypeColor)
                        .frame(width: 10, height: 10)
                    Text(accountTypeLabel)
                        .font(.subheadline.bold())
                    Image(systemName: "chevron.down")
                        .font(.caption)
                }
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color.enlikoSurface)
                .cornerRadius(20)
            }
            
            Spacer()
        }
    }
    
    private var accountTypeLabel: String {
        switch appState.currentAccountType {
        case .demo: return "Demo"
        case .real: return "Real"
        case .testnet: return "Testnet"
        case .mainnet: return "Mainnet"
        }
    }
    
    private var accountTypeColor: Color {
        switch appState.currentAccountType {
        case .demo, .testnet: return .orange
        case .real, .mainnet: return .green
        }
    }
    
    // MARK: - Quick Actions
    private var quickActionsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("quick_actions".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            HStack(spacing: 12) {
                QuickToggleCard(
                    title: "enable_all".localized,
                    icon: "checkmark.circle.fill",
                    color: .enlikoGreen
                ) {
                    Task { await viewModel.enableAllStrategies() }
                }
                
                QuickToggleCard(
                    title: "disable_all".localized,
                    icon: "xmark.circle.fill",
                    color: .enlikoRed
                ) {
                    Task { await viewModel.disableAllStrategies() }
                }
                
                NavigationLink(destination: GlobalSettingsView()) {
                    VStack(spacing: 8) {
                        Image(systemName: "slider.horizontal.3")
                            .font(.title2)
                            .foregroundColor(.enlikoPrimary)
                        Text("global_settings".localized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 80)
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                }
            }
        }
    }
    
    // MARK: - Strategies List
    private var strategiesListSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("strategies_list".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            if viewModel.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 40)
            } else {
                ForEach(viewModel.strategies, id: \.name) { strategy in
                    StrategyRowCard(strategy: strategy, viewModel: viewModel)
                }
            }
        }
    }
}

// MARK: - Quick Toggle Card
struct QuickToggleCard: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 80)
            .background(Color.enlikoSurface)
            .cornerRadius(12)
        }
    }
}

// MARK: - Strategy Row Card
struct StrategyRowCard: View {
    let strategy: StrategyConfig
    @ObservedObject var viewModel: StrategiesHubViewModel
    @State private var isExpanded = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Main Row - Tappable to expand
            Button {
                withAnimation(.spring(response: 0.3)) {
                    isExpanded.toggle()
                }
            } label: {
                HStack(spacing: 12) {
                    // Strategy Icon
                    Text(strategy.emoji)
                        .font(.title2)
                    
                    // Strategy Info
                    VStack(alignment: .leading, spacing: 2) {
                        Text(strategy.displayName)
                            .font(.subheadline.bold())
                            .foregroundColor(.white)
                        
                        HStack(spacing: 8) {
                            // Long Status
                            HStack(spacing: 4) {
                                Circle()
                                    .fill(strategy.longEnabled ? Color.enlikoGreen : Color.gray.opacity(0.5))
                                    .frame(width: 6, height: 6)
                                Text("LONG")
                                    .font(.caption2)
                                    .foregroundColor(strategy.longEnabled ? .enlikoGreen : .secondary)
                            }
                            
                            // Short Status
                            HStack(spacing: 4) {
                                Circle()
                                    .fill(strategy.shortEnabled ? Color.enlikoRed : Color.gray.opacity(0.5))
                                    .frame(width: 6, height: 6)
                                Text("SHORT")
                                    .font(.caption2)
                                    .foregroundColor(strategy.shortEnabled ? .enlikoRed : .secondary)
                            }
                        }
                    }
                    
                    Spacer()
                    
                    // Toggle & Chevron
                    Toggle("", isOn: Binding(
                        get: { strategy.longEnabled || strategy.shortEnabled },
                        set: { newValue in
                            Task {
                                await viewModel.toggleStrategy(strategy.name, enabled: newValue)
                            }
                        }
                    ))
                    .labelsHidden()
                    .tint(.enlikoPrimary)
                    
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .rotationEffect(.degrees(isExpanded ? 90 : 0))
                }
                .padding()
                .background(Color.enlikoSurface)
            }
            
            // Expanded Content
            if isExpanded {
                VStack(spacing: 12) {
                    Divider().background(Color.enlikoBorder)
                    
                    // Quick Stats
                    HStack(spacing: 16) {
                        statItem(label: "entry".localized, value: "\(Int(strategy.percent))%")
                        statItem(label: "TP", value: "\(Int(strategy.tpPercent))%")
                        statItem(label: "SL", value: "\(Int(strategy.slPercent))%")
                        statItem(label: "leverage".localized, value: "\(strategy.leverage)x")
                    }
                    
                    // Separate Long/Short Toggles
                    HStack(spacing: 12) {
                        sideToggle(
                            label: "LONG",
                            enabled: strategy.longEnabled,
                            color: .enlikoGreen
                        ) {
                            Task {
                                await viewModel.toggleStrategySide(strategy.name, side: "long", enabled: !strategy.longEnabled)
                            }
                        }
                        
                        sideToggle(
                            label: "SHORT",
                            enabled: strategy.shortEnabled,
                            color: .enlikoRed
                        ) {
                            Task {
                                await viewModel.toggleStrategySide(strategy.name, side: "short", enabled: !strategy.shortEnabled)
                            }
                        }
                    }
                    
                    // Settings Link
                    NavigationLink(destination: StrategyDetailView(strategyName: strategy.name)) {
                        HStack {
                            Image(systemName: "gearshape.fill")
                            Text("detailed_settings".localized)
                            Spacer()
                            Image(systemName: "chevron.right")
                        }
                        .font(.subheadline)
                        .foregroundColor(.enlikoPrimary)
                        .padding()
                        .background(Color.enlikoPrimary.opacity(0.1))
                        .cornerRadius(8)
                    }
                }
                .padding(.horizontal)
                .padding(.bottom)
                .background(Color.enlikoSurface)
            }
        }
        .cornerRadius(12)
        .animation(.spring(response: 0.3), value: isExpanded)
    }
    
    private func statItem(label: String, value: String) -> some View {
        VStack(spacing: 2) {
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
            Text(value)
                .font(.caption.bold())
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity)
    }
    
    private func sideToggle(label: String, enabled: Bool, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack {
                Circle()
                    .fill(enabled ? color : Color.gray.opacity(0.5))
                    .frame(width: 8, height: 8)
                Text(label)
                    .font(.caption.bold())
                    .foregroundColor(enabled ? color : .secondary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
            .background(enabled ? color.opacity(0.2) : Color.enlikoSurface)
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(enabled ? color.opacity(0.5) : Color.enlikoBorder, lineWidth: 1)
            )
        }
    }
}

// MARK: - Strategy Config Model
struct StrategyConfig: Identifiable {
    var id: String { name }
    let name: String
    let displayName: String
    let emoji: String
    var longEnabled: Bool
    var shortEnabled: Bool
    var percent: Double
    var tpPercent: Double
    var slPercent: Double
    var leverage: Int
    
    static let all: [StrategyConfig] = [
        StrategyConfig(name: "oi", displayName: "Open Interest", emoji: "📊", longEnabled: true, shortEnabled: true, percent: 1.0, tpPercent: 8.0, slPercent: 3.0, leverage: 10),
        StrategyConfig(name: "rsi_bb", displayName: "RSI + Bollinger", emoji: "📈", longEnabled: true, shortEnabled: true, percent: 1.0, tpPercent: 8.0, slPercent: 3.0, leverage: 10),
        StrategyConfig(name: "scryptomera", displayName: "Scryptomera", emoji: "🔮", longEnabled: true, shortEnabled: true, percent: 1.0, tpPercent: 8.0, slPercent: 3.0, leverage: 10),
        StrategyConfig(name: "scalper", displayName: "Scalper", emoji: "⚡", longEnabled: true, shortEnabled: true, percent: 1.0, tpPercent: 8.0, slPercent: 3.0, leverage: 10),
        StrategyConfig(name: "fibonacci", displayName: "Fibonacci", emoji: "🌀", longEnabled: true, shortEnabled: true, percent: 1.0, tpPercent: 8.0, slPercent: 3.0, leverage: 10),
        StrategyConfig(name: "elcaro", displayName: "Elcaro", emoji: "💎", longEnabled: true, shortEnabled: true, percent: 1.0, tpPercent: 8.0, slPercent: 3.0, leverage: 10),
    ]
}

// MARK: - ViewModel
@MainActor
class StrategiesHubViewModel: ObservableObject {
    @Published var strategies: [StrategyConfig] = StrategyConfig.all
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func loadStrategies(exchange: Exchange, accountType: AccountType) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response: [String: StrategySettingsResponse] = try await NetworkService.shared.get(
                "/strategy-settings",
                params: [
                    "exchange": exchange.rawValue,
                    "account_type": accountType.rawValue
                ]
            )
            
            // Update local strategies with server data
            for (name, settings) in response {
                if let index = strategies.firstIndex(where: { $0.name == name }) {
                    strategies[index].longEnabled = settings.long_enabled ?? true
                    strategies[index].shortEnabled = settings.short_enabled ?? true
                    strategies[index].percent = settings.percent ?? 1.0
                    strategies[index].tpPercent = settings.tp_percent ?? 8.0
                    strategies[index].slPercent = settings.sl_percent ?? 3.0
                    strategies[index].leverage = settings.leverage ?? 10
                }
            }
        } catch {
            errorMessage = error.localizedDescription
            print("Failed to load strategies: \(error)")
        }
    }
    
    func toggleStrategy(_ name: String, enabled: Bool) async {
        do {
            try await NetworkService.shared.postIgnoreResponse(
                "/strategy-settings/\(name)/toggle",
                body: ["long_enabled": enabled, "short_enabled": enabled]
            )
            
            if let index = strategies.firstIndex(where: { $0.name == name }) {
                strategies[index].longEnabled = enabled
                strategies[index].shortEnabled = enabled
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func toggleStrategySide(_ name: String, side: String, enabled: Bool) async {
        do {
            let key = side == "long" ? "long_enabled" : "short_enabled"
            try await NetworkService.shared.postIgnoreResponse(
                "/strategy-settings/\(name)/toggle",
                body: [key: enabled]
            )
            
            if let index = strategies.firstIndex(where: { $0.name == name }) {
                if side == "long" {
                    strategies[index].longEnabled = enabled
                } else {
                    strategies[index].shortEnabled = enabled
                }
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func enableAllStrategies() async {
        for strategy in strategies {
            await toggleStrategy(strategy.name, enabled: true)
        }
    }
    
    func disableAllStrategies() async {
        for strategy in strategies {
            await toggleStrategy(strategy.name, enabled: false)
        }
    }
}

// MARK: - Strategy Settings Response
struct StrategySettingsResponse: Codable {
    let long_enabled: Bool?
    let short_enabled: Bool?
    let percent: Double?
    let tp_percent: Double?
    let sl_percent: Double?
    let leverage: Int?
}

// MARK: - Placeholder Views
struct GlobalSettingsView: View {
    var body: some View {
        Text("Global Settings")
            .navigationTitle("global_settings".localized)
    }
}

struct StrategyDetailView: View {
    let strategyName: String
    
    var body: some View {
        StrategySettingsView()
    }
}

#Preview {
    NavigationStack {
        StrategiesHubView()
            .environmentObject(AppState.shared)
            .preferredColorScheme(.dark)
    }
}
