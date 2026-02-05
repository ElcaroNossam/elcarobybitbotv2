//
//  HyperLiquidView.swift
//  EnlikoTrading
//
//  HyperLiquid DEX Integration View
//  Features: Vault operations, Transfers, Staking, DEX-specific features
//

import SwiftUI

// MARK: - HyperLiquid Models
struct HLVaultInfo: Identifiable {
    let id = UUID()
    let name: String
    let tvl: Double
    let apr: Double
    let userDeposit: Double
    let pnl: Double
}

struct HLTransferItem: Identifiable {
    let id = UUID()
    let type: TransferType
    let amount: Double
    let asset: String
    let timestamp: Date
    let status: String
    
    enum TransferType: String {
        case deposit = "Deposit"
        case withdraw = "Withdraw"
        case spotToPerp = "Spot → Perp"
        case perpToSpot = "Perp → Spot"
    }
}

struct HyperLiquidView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var selectedTab: HLTab = .overview
    @State private var isLoading = true
    @State private var perpBalance: Double = 0
    @State private var spotBalance: Double = 0
    @State private var vaults: [HLVaultInfo] = []
    @State private var transfers: [HLTransferItem] = []
    @State private var showDeposit = false
    @State private var showWithdraw = false
    @State private var showTransfer = false
    
    enum HLTab: String, CaseIterable {
        case overview = "Overview"
        case vaults = "Vaults"
        case transfers = "Transfers"
        case points = "Points"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Network Badge
            networkBadge
            
            // Balance Header
            balanceHeader
            
            // Tab Selector
            tabSelector
            
            // Content
            if isLoading {
                Spacer()
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .enlikoPrimary))
                Spacer()
            } else {
                contentView
            }
        }
        .background(Color.enlikoBackground)
        .navigationTitle("HyperLiquid")
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task { await refreshData() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(.enlikoPrimary)
                }
            }
        }
        .sheet(isPresented: $showDeposit) {
            HLDepositSheet()
        }
        .sheet(isPresented: $showWithdraw) {
            HLWithdrawSheet()
        }
        .sheet(isPresented: $showTransfer) {
            HLInternalTransferSheet()
        }
        .task {
            await refreshData()
        }
    }
    
    // MARK: - Network Badge
    private var networkBadge: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(appState.currentAccountType == .testnet ? Color.orange : Color.green)
                .frame(width: 8, height: 8)
            
            Text(appState.currentAccountType == .testnet ? "Testnet" : "Mainnet")
                .font(.caption.bold())
                .foregroundColor(appState.currentAccountType == .testnet ? .orange : .green)
            
            Spacer()
            
            // Switch Network Button
            Button {
                // Toggle network
                appState.currentAccountType = appState.currentAccountType == .testnet ? .mainnet : .testnet
            } label: {
                HStack(spacing: 4) {
                    Image(systemName: "arrow.triangle.2.circlepath")
                    Text("Switch")
                }
                .font(.caption)
                .foregroundColor(.enlikoPrimary)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Balance Header
    private var balanceHeader: some View {
        VStack(spacing: 16) {
            // Total Balance
            VStack(spacing: 4) {
                Text("Total Balance")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text("$\(perpBalance + spotBalance, specifier: "%.2f")")
                    .font(.system(size: 32, weight: .bold))
                    .foregroundColor(.white)
            }
            
            // Perp vs Spot
            HStack(spacing: 24) {
                VStack(spacing: 4) {
                    Text("Perp")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("$\(perpBalance, specifier: "%.2f")")
                        .font(.headline)
                        .foregroundColor(.white)
                }
                
                Rectangle()
                    .fill(Color.secondary.opacity(0.3))
                    .frame(width: 1, height: 30)
                
                VStack(spacing: 4) {
                    Text("Spot")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("$\(spotBalance, specifier: "%.2f")")
                        .font(.headline)
                        .foregroundColor(.white)
                }
            }
            
            // Action Buttons
            HStack(spacing: 16) {
                actionButton(title: "Deposit", icon: "arrow.down.circle.fill", color: .green) {
                    showDeposit = true
                }
                
                actionButton(title: "Withdraw", icon: "arrow.up.circle.fill", color: .orange) {
                    showWithdraw = true
                }
                
                actionButton(title: "Transfer", icon: "arrow.left.arrow.right", color: .blue) {
                    showTransfer = true
                }
            }
        }
        .padding()
        .background(
            LinearGradient(
                colors: [Color.blue.opacity(0.2), Color.enlikoBackground],
                startPoint: .top,
                endPoint: .bottom
            )
        )
    }
    
    private func actionButton(title: String, icon: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .frame(width: 80)
        }
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 0) {
                ForEach(HLTab.allCases, id: \.self) { tab in
                    Button {
                        withAnimation { selectedTab = tab }
                    } label: {
                        VStack(spacing: 6) {
                            Text(tab.rawValue)
                                .font(.subheadline.bold())
                                .foregroundColor(selectedTab == tab ? .white : .secondary)
                                .padding(.horizontal, 16)
                            
                            Rectangle()
                                .fill(selectedTab == tab ? Color.enlikoPrimary : Color.clear)
                                .frame(height: 2)
                        }
                    }
                }
            }
        }
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Content View
    @ViewBuilder
    private var contentView: some View {
        switch selectedTab {
        case .overview:
            overviewTab
        case .vaults:
            vaultsTab
        case .transfers:
            transfersTab
        case .points:
            pointsTab
        }
    }
    
    // MARK: - Overview Tab
    private var overviewTab: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Quick Stats
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 12) {
                    statCard(title: "24h Volume", value: "$125.4K", icon: "chart.bar.fill", color: .blue)
                    statCard(title: "Open Interest", value: "$45.2K", icon: "circle.grid.cross.fill", color: .purple)
                    statCard(title: "Funding Rate", value: "0.0023%", icon: "percent", color: .green)
                    statCard(title: "Positions", value: "3", icon: "rectangle.stack.fill", color: .orange)
                }
                
                // Margin Info
                VStack(alignment: .leading, spacing: 12) {
                    Text("Margin Details")
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Account Margin")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text("$\(perpBalance * 0.85, specifier: "%.2f")")
                                .font(.subheadline.bold())
                                .foregroundColor(.white)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 4) {
                            Text("Margin Ratio")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text("42.5%")
                                .font(.subheadline.bold())
                                .foregroundColor(.green)
                        }
                    }
                    
                    // Margin bar
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            Rectangle()
                                .fill(Color.gray.opacity(0.3))
                                .frame(height: 8)
                            
                            Rectangle()
                                .fill(
                                    LinearGradient(
                                        colors: [.green, .yellow, .red],
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )
                                .frame(width: geo.size.width * 0.425, height: 8)
                        }
                        .cornerRadius(4)
                    }
                    .frame(height: 8)
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                
                // Recent Activity
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("Recent Activity")
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        Spacer()
                        
                        Button {
                            selectedTab = .transfers
                        } label: {
                            Text("See All")
                                .font(.caption)
                                .foregroundColor(.enlikoPrimary)
                        }
                    }
                    
                    ForEach(transfers.prefix(3)) { transfer in
                        HStack {
                            Image(systemName: transfer.type == .deposit ? "arrow.down.circle" : "arrow.up.circle")
                                .foregroundColor(transfer.type == .deposit ? .green : .orange)
                            
                            VStack(alignment: .leading, spacing: 2) {
                                Text(transfer.type.rawValue)
                                    .font(.subheadline)
                                    .foregroundColor(.white)
                                Text(formatDate(transfer.timestamp))
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                            
                            Text("\(transfer.amount, specifier: "%.2f") \(transfer.asset)")
                                .font(.subheadline.bold())
                                .foregroundColor(.white)
                        }
                        .padding(.vertical, 4)
                    }
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
            }
            .padding()
        }
    }
    
    private func statCard(title: String, value: String, icon: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Spacer()
            }
            
            Text(value)
                .font(.headline.bold())
                .foregroundColor(.white)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(12)
    }
    
    // MARK: - Vaults Tab
    private var vaultsTab: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(vaults) { vault in
                    VaultRow(vault: vault)
                }
            }
            .padding()
        }
    }
    
    // MARK: - Transfers Tab
    private var transfersTab: some View {
        Group {
            if transfers.isEmpty {
                VStack {
                    Spacer()
                    Image(systemName: "arrow.left.arrow.right")
                        .font(.system(size: 50))
                        .foregroundColor(.secondary.opacity(0.5))
                    Text("No transfers yet")
                        .font(.headline)
                        .foregroundColor(.secondary)
                    Spacer()
                }
            } else {
                ScrollView {
                    LazyVStack(spacing: 1) {
                        ForEach(transfers) { transfer in
                            TransferRow(transfer: transfer)
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Points Tab
    private var pointsTab: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Points Card
                VStack(spacing: 16) {
                    Image(systemName: "star.circle.fill")
                        .font(.system(size: 50))
                        .foregroundColor(.yellow)
                    
                    Text("12,450")
                        .font(.system(size: 40, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text("HyperLiquid Points")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 24)
                .frame(maxWidth: .infinity)
                .background(
                    LinearGradient(
                        colors: [Color.yellow.opacity(0.2), Color.enlikoSurface],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .cornerRadius(16)
                
                // Earning Methods
                VStack(alignment: .leading, spacing: 16) {
                    Text("How to Earn")
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    earningMethod(icon: "arrow.left.arrow.right", title: "Trading Volume", description: "Earn 1 point per $1,000 traded", points: "+10 pts/day")
                    earningMethod(icon: "person.2.fill", title: "Referrals", description: "Invite friends to join", points: "+100 pts")
                    earningMethod(icon: "clock.fill", title: "Daily Login", description: "Check in every day", points: "+5 pts")
                    earningMethod(icon: "star.fill", title: "Vault Deposits", description: "Deposit to earn extra", points: "+2x")
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
            }
            .padding()
        }
    }
    
    private func earningMethod(icon: String, title: String, description: String, points: String) -> some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.enlikoPrimary)
                .frame(width: 40)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Text(points)
                .font(.caption.bold())
                .foregroundColor(.yellow)
        }
    }
    
    // MARK: - Helpers
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d, HH:mm"
        return formatter.string(from: date)
    }
    
    // MARK: - Refresh
    private func refreshData() async {
        isLoading = true
        
        // Fetch HL balance
        await tradingService.fetchBalance()
        
        try? await Task.sleep(nanoseconds: 300_000_000)
        
        await MainActor.run {
            if let balance = tradingService.balance {
                perpBalance = balance.totalEquity * 0.7
                spotBalance = balance.totalEquity * 0.3
            }
            
            vaults = [
                HLVaultInfo(name: "HL Market Making", tvl: 125_000_000, apr: 15.5, userDeposit: 5000, pnl: 234.56),
                HLVaultInfo(name: "Delta Neutral", tvl: 45_000_000, apr: 12.3, userDeposit: 0, pnl: 0),
                HLVaultInfo(name: "Momentum Alpha", tvl: 28_000_000, apr: 22.1, userDeposit: 0, pnl: 0),
            ]
            
            transfers = [
                HLTransferItem(type: .deposit, amount: 1000, asset: "USDC", timestamp: Date().addingTimeInterval(-3600), status: "Completed"),
                HLTransferItem(type: .spotToPerp, amount: 500, asset: "USDC", timestamp: Date().addingTimeInterval(-7200), status: "Completed"),
                HLTransferItem(type: .withdraw, amount: 250, asset: "USDC", timestamp: Date().addingTimeInterval(-86400), status: "Completed"),
            ]
            
            isLoading = false
        }
    }
}

// MARK: - Vault Row
struct VaultRow: View {
    let vault: HLVaultInfo
    @State private var showVaultDetail = false
    
    var body: some View {
        Button {
            showVaultDetail = true
        } label: {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(vault.name)
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        Text("TVL: $\(formatLargeNumber(vault.tvl))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("\(vault.apr, specifier: "%.1f")% APR")
                            .font(.headline)
                            .foregroundColor(.green)
                        
                        if vault.userDeposit > 0 {
                            Text("Your: $\(vault.userDeposit, specifier: "%.0f")")
                                .font(.caption)
                                .foregroundColor(.enlikoPrimary)
                        }
                    }
                }
                
                if vault.userDeposit > 0 {
                    HStack {
                        Text("PnL:")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Text("+$\(vault.pnl, specifier: "%.2f")")
                            .font(.caption.bold())
                            .foregroundColor(.green)
                    }
                }
            }
            .padding()
            .background(Color.enlikoSurface)
            .cornerRadius(12)
        }
        .sheet(isPresented: $showVaultDetail) {
            VaultDetailSheet(vault: vault)
        }
    }
    
    private func formatLargeNumber(_ num: Double) -> String {
        if num >= 1_000_000_000 {
            return String(format: "%.1fB", num / 1_000_000_000)
        } else if num >= 1_000_000 {
            return String(format: "%.1fM", num / 1_000_000)
        } else if num >= 1_000 {
            return String(format: "%.1fK", num / 1_000)
        }
        return String(format: "%.0f", num)
    }
}

// MARK: - Transfer Row
struct TransferRow: View {
    let transfer: HLTransferItem
    
    var body: some View {
        HStack {
            Image(systemName: iconForType)
                .foregroundColor(colorForType)
                .frame(width: 30)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(transfer.type.rawValue)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                
                Text(formatDate(transfer.timestamp))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text("\(transfer.amount, specifier: "%.2f") \(transfer.asset)")
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                
                Text(transfer.status)
                    .font(.caption)
                    .foregroundColor(.green)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
    }
    
    private var iconForType: String {
        switch transfer.type {
        case .deposit: return "arrow.down.circle.fill"
        case .withdraw: return "arrow.up.circle.fill"
        case .spotToPerp, .perpToSpot: return "arrow.left.arrow.right.circle.fill"
        }
    }
    
    private var colorForType: Color {
        switch transfer.type {
        case .deposit: return .green
        case .withdraw: return .orange
        case .spotToPerp, .perpToSpot: return .blue
        }
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d, HH:mm"
        return formatter.string(from: date)
    }
}

// MARK: - Sheets
struct HLDepositSheet: View {
    @Environment(\.dismiss) var dismiss
    @State private var amount = ""
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Image(systemName: "arrow.down.circle.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.green)
                
                Text("Deposit USDC")
                    .font(.title2.bold())
                
                TextField("Amount", text: $amount)
                    .keyboardType(.decimalPad)
                    .font(.title)
                    .multilineTextAlignment(.center)
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                
                Text("Deposit from your Arbitrum wallet")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Button {
                    dismiss()
                } label: {
                    Text("Deposit")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
            }
            .padding()
            .background(Color.enlikoBackground)
            .navigationTitle("Deposit")
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

struct HLWithdrawSheet: View {
    @Environment(\.dismiss) var dismiss
    @State private var amount = ""
    @State private var address = ""
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.orange)
                
                Text("Withdraw USDC")
                    .font(.title2.bold())
                
                TextField("Amount", text: $amount)
                    .keyboardType(.decimalPad)
                    .font(.title)
                    .multilineTextAlignment(.center)
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                
                TextField("Destination Address", text: $address)
                    .font(.caption)
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                
                Text("Withdraw to Arbitrum network")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Button {
                    dismiss()
                } label: {
                    Text("Withdraw")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.orange)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
            }
            .padding()
            .background(Color.enlikoBackground)
            .navigationTitle("Withdraw")
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

struct HLInternalTransferSheet: View {
    @Environment(\.dismiss) var dismiss
    @State private var amount = ""
    @State private var fromPerp = true
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Image(systemName: "arrow.left.arrow.right.circle.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.blue)
                
                Text("Internal Transfer")
                    .font(.title2.bold())
                
                // From/To Toggle
                HStack(spacing: 16) {
                    VStack {
                        Text("From")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(fromPerp ? "Perp" : "Spot")
                            .font(.headline)
                    }
                    
                    Button {
                        fromPerp.toggle()
                    } label: {
                        Image(systemName: "arrow.left.arrow.right")
                            .font(.title2)
                            .foregroundColor(.enlikoPrimary)
                    }
                    
                    VStack {
                        Text("To")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(fromPerp ? "Spot" : "Perp")
                            .font(.headline)
                    }
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                
                TextField("Amount", text: $amount)
                    .keyboardType(.decimalPad)
                    .font(.title)
                    .multilineTextAlignment(.center)
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                
                Spacer()
                
                Button {
                    dismiss()
                } label: {
                    Text("Transfer")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
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

struct VaultDetailSheet: View {
    @Environment(\.dismiss) var dismiss
    let vault: HLVaultInfo
    @State private var depositAmount = ""
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    VStack(spacing: 8) {
                        Text(vault.name)
                            .font(.title2.bold())
                            .foregroundColor(.white)
                        
                        Text(String(format: "%.1f%% APR", vault.apr))
                            .font(.title.bold())
                            .foregroundColor(.green)
                    }
                    
                    // Stats
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        statItem(title: "TVL", value: "$\(Int(vault.tvl / 1_000_000))M")
                        statItem(title: "Your Deposit", value: String(format: "$%.0f", vault.userDeposit))
                        statItem(title: "Your PnL", value: String(format: "+$%.2f", vault.pnl))
                        statItem(title: "30d Return", value: "+2.5%")
                    }
                    
                    // Deposit
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Deposit")
                            .font(.headline)
                        
                        TextField("Amount", text: $depositAmount)
                            .keyboardType(.decimalPad)
                            .padding()
                            .background(Color.enlikoSurface)
                            .cornerRadius(12)
                        
                        Button {
                            // Deposit action
                        } label: {
                            Text("Deposit to Vault")
                                .font(.headline)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.enlikoPrimary)
                                .foregroundColor(.white)
                                .cornerRadius(12)
                        }
                    }
                    
                    // Withdraw (if deposited)
                    if vault.userDeposit > 0 {
                        Button {
                            // Withdraw action
                        } label: {
                            Text("Withdraw")
                                .font(.headline)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.enlikoSurface)
                                .foregroundColor(.white)
                                .cornerRadius(12)
                        }
                    }
                }
                .padding()
            }
            .background(Color.enlikoBackground)
            .navigationTitle("Vault Details")
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
    
    private func statItem(title: String, value: String) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.headline)
                .foregroundColor(.white)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(8)
    }
}

#Preview {
    NavigationStack {
        HyperLiquidView()
            .environmentObject(AppState.shared)
            .environmentObject(TradingService.shared)
            .preferredColorScheme(.dark)
    }
}
