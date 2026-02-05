//
//  WalletView.swift
//  EnlikoTrading
//
//  Full wallet view like Binance/Bybit
//  Features: Balance, Assets breakdown, Transfer, History
//

import SwiftUI

// MARK: - Wallet Models
struct WalletAsset: Identifiable {
    let id = UUID()
    let coin: String
    let balance: Double
    let availableBalance: Double
    let lockedBalance: Double
    let usdValue: Double
    let change24h: Double
    
    var formattedBalance: String {
        if balance >= 1000 {
            return String(format: "%.2f", balance)
        } else if balance >= 1 {
            return String(format: "%.4f", balance)
        } else {
            return String(format: "%.8f", balance)
        }
    }
    
    var formattedUSD: String {
        String(format: "$%.2f", usdValue)
    }
}

struct WalletView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var assets: [WalletAsset] = []
    @State private var isLoading = true
    @State private var showTransfer = false
    @State private var selectedTab: WalletTab = .spot
    @State private var hideSmallBalances = true
    @State private var totalEquity: Double = 0
    @State private var totalPnL24h: Double = 0
    @State private var totalPnLPercent: Double = 0
    
    enum WalletTab: String, CaseIterable {
        case spot = "Spot"
        case futures = "Futures"
        case margin = "Margin"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header Card
            walletHeader
            
            // Tab Selector
            tabSelector
            
            // Options Bar
            optionsBar
            
            // Assets List
            if isLoading {
                Spacer()
                ProgressView()
                Spacer()
            } else {
                assetsList
            }
        }
        .background(Color.enlikoBackground)
        .navigationTitle("wallet".localized)
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task { await refreshWallet() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(.enlikoPrimary)
                }
            }
        }
        .sheet(isPresented: $showTransfer) {
            TransferSheet()
        }
        .task {
            await refreshWallet()
        }
    }
    
    // MARK: - Wallet Header
    private var walletHeader: some View {
        VStack(spacing: 16) {
            // Total Balance
            VStack(spacing: 4) {
                Text("Total Balance")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text("$\(totalEquity, specifier: "%.2f")")
                    .font(.system(size: 36, weight: .bold))
                    .foregroundColor(.white)
                
                HStack(spacing: 8) {
                    Text(totalPnL24h >= 0 ? "+$\(totalPnL24h, specifier: "%.2f")" : "-$\(abs(totalPnL24h), specifier: "%.2f")")
                        .font(.subheadline.bold())
                        .foregroundColor(totalPnL24h >= 0 ? .green : .red)
                    
                    Text("(\(totalPnLPercent, specifier: "%.2f")%)")
                        .font(.caption)
                        .foregroundColor(totalPnLPercent >= 0 ? .green : .red)
                    
                    Text("24h")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            // Quick Actions
            HStack(spacing: 20) {
                quickActionButton(icon: "arrow.down.circle.fill", label: "Deposit", color: .green)
                quickActionButton(icon: "arrow.up.circle.fill", label: "Withdraw", color: .orange)
                quickActionButton(icon: "arrow.left.arrow.right.circle.fill", label: "Transfer", color: .blue) {
                    showTransfer = true
                }
                quickActionButton(icon: "clock.fill", label: "History", color: .purple)
            }
        }
        .padding()
        .background(
            LinearGradient(
                colors: [Color.enlikoPrimary.opacity(0.3), Color.enlikoBackground],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }
    
    private func quickActionButton(icon: String, label: String, color: Color, action: (() -> Void)? = nil) -> some View {
        Button {
            action?()
        } label: {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(label)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .frame(width: 70)
        }
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach(WalletTab.allCases, id: \.self) { tab in
                Button {
                    withAnimation { selectedTab = tab }
                } label: {
                    VStack(spacing: 6) {
                        Text(tab.rawValue)
                            .font(.subheadline.bold())
                            .foregroundColor(selectedTab == tab ? .white : .secondary)
                        
                        Rectangle()
                            .fill(selectedTab == tab ? Color.enlikoPrimary : Color.clear)
                            .frame(height: 2)
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal)
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Options Bar
    private var optionsBar: some View {
        HStack {
            Toggle(isOn: $hideSmallBalances) {
                Text("Hide small balances")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .toggleStyle(SwitchToggleStyle(tint: .enlikoPrimary))
            .labelsHidden()
            
            Text("Hide small balances")
                .font(.caption)
                .foregroundColor(.secondary)
            
            Spacer()
            
            // Sort Menu
            Menu {
                Button("By Value") {}
                Button("By Name") {}
                Button("By Change") {}
            } label: {
                HStack(spacing: 4) {
                    Text("Sort")
                        .font(.caption)
                    Image(systemName: "chevron.down")
                        .font(.caption2)
                }
                .foregroundColor(.secondary)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
    
    // MARK: - Assets List
    private var assetsList: some View {
        ScrollView {
            LazyVStack(spacing: 1) {
                ForEach(filteredAssets) { asset in
                    AssetRow(asset: asset)
                }
            }
        }
        .refreshable {
            await refreshWallet()
        }
    }
    
    private var filteredAssets: [WalletAsset] {
        var result = assets
        if hideSmallBalances {
            result = result.filter { $0.usdValue > 1 }
        }
        return result.sorted { $0.usdValue > $1.usdValue }
    }
    
    // MARK: - Refresh
    private func refreshWallet() async {
        isLoading = true
        
        // Fetch balance from trading service
        await tradingService.fetchBalance()
        
        // Simulate additional wallet data
        try? await Task.sleep(nanoseconds: 300_000_000)
        
        await MainActor.run {
            if let balance = tradingService.balance {
                totalEquity = balance.totalEquity
                totalPnL24h = balance.unrealizedPnl ?? 0
                totalPnLPercent = totalEquity > 0 ? (totalPnL24h / totalEquity * 100) : 0
            }
            
            // Mock assets - in production, fetch from API
            assets = [
                WalletAsset(coin: "USDT", balance: totalEquity, availableBalance: totalEquity * 0.7, lockedBalance: totalEquity * 0.3, usdValue: totalEquity, change24h: 0),
                WalletAsset(coin: "BTC", balance: 0.05, availableBalance: 0.05, lockedBalance: 0, usdValue: 4925, change24h: 2.5),
                WalletAsset(coin: "ETH", balance: 1.2, availableBalance: 1.2, lockedBalance: 0, usdValue: 3840, change24h: 1.8),
                WalletAsset(coin: "SOL", balance: 25, availableBalance: 20, lockedBalance: 5, usdValue: 4500, change24h: 5.2),
            ]
            
            isLoading = false
        }
    }
}

// MARK: - Asset Row
struct AssetRow: View {
    let asset: WalletAsset
    
    var body: some View {
        HStack {
            // Coin Icon & Name
            HStack(spacing: 12) {
                // Placeholder coin icon
                Circle()
                    .fill(Color.enlikoPrimary.opacity(0.2))
                    .frame(width: 40, height: 40)
                    .overlay(
                        Text(String(asset.coin.prefix(1)))
                            .font(.headline.bold())
                            .foregroundColor(.enlikoPrimary)
                    )
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(asset.coin)
                        .font(.headline.bold())
                        .foregroundColor(.white)
                    
                    Text(asset.formattedBalance)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            // USD Value & Change
            VStack(alignment: .trailing, spacing: 2) {
                Text(asset.formattedUSD)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                
                if asset.change24h != 0 {
                    Text(String(format: "%@%.2f%%", asset.change24h >= 0 ? "+" : "", asset.change24h))
                        .font(.caption)
                        .foregroundColor(asset.change24h >= 0 ? .green : .red)
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
    }
}

// MARK: - Transfer Sheet
struct TransferSheet: View {
    @Environment(\.dismiss) var dismiss
    
    @State private var fromAccount = "Spot"
    @State private var toAccount = "Futures"
    @State private var amount = ""
    @State private var selectedCoin = "USDT"
    
    let accounts = ["Spot", "Futures", "Margin", "Funding"]
    let coins = ["USDT", "BTC", "ETH", "SOL"]
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // From/To Section
                VStack(spacing: 16) {
                    // From
                    HStack {
                        Text("From")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        Picker("", selection: $fromAccount) {
                            ForEach(accounts, id: \.self) { account in
                                Text(account).tag(account)
                            }
                        }
                        .pickerStyle(.menu)
                    }
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                    
                    // Swap Button
                    Button {
                        let temp = fromAccount
                        fromAccount = toAccount
                        toAccount = temp
                    } label: {
                        Image(systemName: "arrow.up.arrow.down.circle.fill")
                            .font(.title)
                            .foregroundColor(.enlikoPrimary)
                    }
                    
                    // To
                    HStack {
                        Text("To")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        Picker("", selection: $toAccount) {
                            ForEach(accounts, id: \.self) { account in
                                Text(account).tag(account)
                            }
                        }
                        .pickerStyle(.menu)
                    }
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                }
                
                // Coin Picker
                HStack {
                    Text("Coin")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Picker("", selection: $selectedCoin) {
                        ForEach(coins, id: \.self) { coin in
                            Text(coin).tag(coin)
                        }
                    }
                    .pickerStyle(.menu)
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                
                // Amount
                VStack(alignment: .leading, spacing: 8) {
                    Text("Amount")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    HStack {
                        TextField("0.00", text: $amount)
                            .keyboardType(.decimalPad)
                            .font(.title2)
                        
                        Button {
                            // Set max
                        } label: {
                            Text("MAX")
                                .font(.caption.bold())
                                .foregroundColor(.enlikoPrimary)
                        }
                    }
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                    
                    Text("Available: 10,000.00 USDT")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                // Transfer Button
                Button {
                    // Execute transfer
                    dismiss()
                } label: {
                    Text("Transfer")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.enlikoPrimary)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
                .disabled(amount.isEmpty)
            }
            .padding()
            .background(Color.enlikoBackground)
            .navigationTitle("Transfer")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button { dismiss() } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
    }
}

#Preview {
    NavigationStack {
        WalletView()
            .environmentObject(AppState.shared)
            .environmentObject(TradingService.shared)
            .preferredColorScheme(.dark)
    }
}
