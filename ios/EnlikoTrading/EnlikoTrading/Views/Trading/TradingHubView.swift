//
//  TradingHubView.swift
//  EnlikoTrading
//
//  Trading Hub - Combined view like Telegram bot:
//  - Positions list with quick actions
//  - Pending orders
//  - Manual trading button
//

import SwiftUI

struct TradingHubView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    @State private var selectedSegment = 0
    @State private var showManualTrade = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Exchange/Account Switcher at top
            exchangeAccountBar
            
            // Segment Control
            segmentPicker
            
            // Content based on segment
            ScrollView {
                VStack(spacing: 16) {
                    if selectedSegment == 0 {
                        positionsContent
                    } else {
                        ordersContent
                    }
                }
                .padding()
            }
            .refreshable {
                await tradingService.refreshAll()
            }
        }
        .background(Color.enlikoBackground)
        .navigationTitle("trading".localized)
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    showManualTrade = true
                } label: {
                    Image(systemName: "plus.circle.fill")
                        .foregroundColor(.enlikoPrimary)
                        .font(.title3)
                }
            }
        }
        .sheet(isPresented: $showManualTrade) {
            ManualTradeView()
        }
    }
    
    // MARK: - Exchange/Account Bar
    private var exchangeAccountBar: some View {
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
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
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
    
    // MARK: - Segment Picker
    private var segmentPicker: some View {
        HStack(spacing: 0) {
            Button {
                withAnimation { selectedSegment = 0 }
            } label: {
                VStack(spacing: 6) {
                    HStack(spacing: 6) {
                        Text("positions".localized)
                            .font(.subheadline.bold())
                        if tradingService.positions.count > 0 {
                            Text("\(tradingService.positions.count)")
                                .font(.caption.bold())
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.enlikoPrimary)
                                .cornerRadius(8)
                        }
                    }
                    .foregroundColor(selectedSegment == 0 ? .white : .secondary)
                    
                    Rectangle()
                        .fill(selectedSegment == 0 ? Color.enlikoPrimary : Color.clear)
                        .frame(height: 2)
                }
            }
            .frame(maxWidth: .infinity)
            
            Button {
                withAnimation { selectedSegment = 1 }
            } label: {
                VStack(spacing: 6) {
                    HStack(spacing: 6) {
                        Text("orders".localized)
                            .font(.subheadline.bold())
                        if tradingService.orders.count > 0 {
                            Text("\(tradingService.orders.count)")
                                .font(.caption.bold())
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.orange)
                                .cornerRadius(8)
                        }
                    }
                    .foregroundColor(selectedSegment == 1 ? .white : .secondary)
                    
                    Rectangle()
                        .fill(selectedSegment == 1 ? Color.enlikoPrimary : Color.clear)
                        .frame(height: 2)
                }
            }
            .frame(maxWidth: .infinity)
        }
        .padding(.horizontal, 16)
        .padding(.top, 8)
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Positions Content
    private var positionsContent: some View {
        Group {
            if tradingService.positions.isEmpty {
                emptyPositionsView
            } else {
                ForEach(tradingService.positions) { position in
                    PositionCard(position: position, onClose: {
                        Task {
                            await tradingService.closePosition(symbol: position.symbol, side: position.side)
                        }
                    })
                }
                
                // Close All Button
                if tradingService.positions.count > 1 {
                    Button {
                        Task {
                            await tradingService.closeAllPositions()
                        }
                    } label: {
                        HStack {
                            Image(systemName: "xmark.circle.fill")
                            Text("close_all".localized)
                        }
                        .font(.subheadline.bold())
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.enlikoRed)
                        .cornerRadius(12)
                    }
                }
            }
        }
    }
    
    private var emptyPositionsView: some View {
        VStack(spacing: 16) {
            Image(systemName: "chart.line.uptrend.xyaxis")
                .font(.system(size: 60))
                .foregroundColor(.secondary.opacity(0.5))
            
            Text("no_positions".localized)
                .font(.headline)
                .foregroundColor(.secondary)
            
            Text("no_positions_hint".localized)
                .font(.caption)
                .foregroundColor(.secondary.opacity(0.7))
                .multilineTextAlignment(.center)
            
            Button {
                showManualTrade = true
            } label: {
                HStack {
                    Image(systemName: "plus.circle.fill")
                    Text("open_position".localized)
                }
                .font(.subheadline.bold())
                .foregroundColor(.white)
                .padding()
                .background(Color.enlikoPrimary)
                .cornerRadius(12)
            }
        }
        .padding(.vertical, 40)
    }
    
    // MARK: - Orders Content
    private var ordersContent: some View {
        Group {
            if tradingService.orders.isEmpty {
                emptyOrdersView
            } else {
                ForEach(tradingService.orders) { order in
                    OrderCard(order: order, onCancel: {
                        Task {
                            await tradingService.cancelOrder(symbol: order.symbol, orderId: order.id)
                        }
                    })
                }
                
                // Cancel All Button
                if tradingService.orders.count > 1 {
                    Button {
                        Task {
                            await tradingService.cancelAllOrders()
                        }
                    } label: {
                        HStack {
                            Image(systemName: "xmark.circle.fill")
                            Text("cancel_all".localized)
                        }
                        .font(.subheadline.bold())
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.orange)
                        .cornerRadius(12)
                    }
                }
            }
        }
    }
    
    private var emptyOrdersView: some View {
        VStack(spacing: 16) {
            Image(systemName: "clock.fill")
                .font(.system(size: 60))
                .foregroundColor(.secondary.opacity(0.5))
            
            Text("no_orders".localized)
                .font(.headline)
                .foregroundColor(.secondary)
            
            Text("no_orders_hint".localized)
                .font(.caption)
                .foregroundColor(.secondary.opacity(0.7))
                .multilineTextAlignment(.center)
        }
        .padding(.vertical, 40)
    }
}

// MARK: - Modify TP/SL View (placeholder)
struct ModifyTPSLView: View {
    let position: Position
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            VStack {
                Text("modify_tpsl".localized)
                    .font(.headline)
                // TODO: Full TP/SL modification UI
            }
            .navigationTitle("modify_tpsl".localized)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("cancel".localized) { dismiss() }
                }
            }
        }
    }
}

// MARK: - Manual Trade View (placeholder)
struct ManualTradeView: View {
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            TradingView()
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("close".localized) { dismiss() }
                    }
                }
        }
    }
}

#Preview {
    NavigationStack {
        TradingHubView()
            .environmentObject(AppState.shared)
            .environmentObject(TradingService.shared)
            .preferredColorScheme(.dark)
    }
}
