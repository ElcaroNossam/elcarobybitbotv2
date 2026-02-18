//
//  TradingHubView.swift
//  EnlikoTrading
//
//  Trading Hub - Futures & Spot separated:
//  - Market type picker (Futures / Spot)
//  - Futures: Positions + Orders + Manual Trade
//  - Spot: Portfolio + DCA + Holdings
//

import SwiftUI

struct TradingHubView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    @StateObject private var spotService = SpotService.shared
    
    @State private var marketType = 0  // 0 = Futures, 1 = Spot
    @State private var selectedSegment = 0
    @State private var showManualTrade = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Market Type Picker (Futures / Spot)
            marketTypePicker
            
            // Exchange/Account Switcher
            exchangeAccountBar
            
            if marketType == 0 {
                // FUTURES content
                segmentPicker
                
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
            } else {
                // SPOT content
                spotContent
            }
        }
        .background(Color.enlikoBackground)
        .navigationTitle("trading".localized)
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                if marketType == 0 {
                    Button {
                        showManualTrade = true
                    } label: {
                        Image(systemName: "plus.circle.fill")
                            .foregroundColor(.enlikoPrimary)
                            .font(.title3)
                    }
                } else {
                    Button {
                        Task {
                            await spotService.fetchPerformance(accountType: appState.currentAccountType.rawValue)
                            await spotService.fetchBalance(accountType: appState.currentAccountType.rawValue)
                        }
                    } label: {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(.enlikoPrimary)
                            .font(.title3)
                    }
                }
            }
        }
        .sheet(isPresented: $showManualTrade) {
            ManualTradeView()
        }
        .onChange(of: marketType) { _, newValue in
            HapticManager.shared.perform(.selection)
            if newValue == 1 {
                Task {
                    await spotService.fetchPerformance(accountType: appState.currentAccountType.rawValue)
                    await spotService.fetchBalance(accountType: appState.currentAccountType.rawValue)
                    await spotService.fetchFearGreed()
                }
            }
        }
        // Refresh when exchange or account type changes
        .onChange(of: appState.currentExchange) { _, _ in
            Task { await tradingService.refreshAll() }
        }
        .onChange(of: appState.currentAccountType) { _, _ in
            Task { await tradingService.refreshAll() }
        }
        .task {
            // Initial data load for this view
            if tradingService.positions.isEmpty && !tradingService.isLoadingPositions {
                await tradingService.fetchPositions()
                await tradingService.fetchOrders()
            }
        }
    }
    
    // MARK: - Market Type Picker (Futures / Spot)
    private var marketTypePicker: some View {
        HStack(spacing: 0) {
            marketTypeButton(title: "futures".localized, icon: "chart.line.uptrend.xyaxis", index: 0)
            marketTypeButton(title: "spot".localized, icon: "dollarsign.circle.fill", index: 1)
        }
        .padding(.horizontal, 16)
        .padding(.top, 8)
        .padding(.bottom, 4)
    }
    
    private func marketTypeButton(title: String, icon: String, index: Int) -> some View {
        Button {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                marketType = index
            }
        } label: {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.caption.bold())
                Text(title)
                    .font(.subheadline.bold())
            }
            .foregroundColor(marketType == index ? .white : .secondary)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
            .background(
                Group {
                    if marketType == index {
                        LinearGradient(
                            colors: [Color.enlikoPrimary, Color.enlikoPrimary.opacity(0.7)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    } else {
                        Color.enlikoSurface.opacity(0.5)
                    }
                }
            )
            .cornerRadius(12)
        }
        .padding(.horizontal, 4)
    }
    
    // MARK: - Spot Content (Embedded)
    private var spotContent: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Spot Balance Card
                spotBalanceCard
                
                // Holdings
                spotHoldingsSection
                
                // Quick Actions
                spotQuickActions
                
                // Fear & Greed
                if let fg = spotService.fearGreed, fg.success {
                    FearGreedCard(fearGreed: fg)
                }
            }
            .padding()
        }
        .refreshable {
            await spotService.fetchPerformance(accountType: appState.currentAccountType.rawValue)
            await spotService.fetchBalance(accountType: appState.currentAccountType.rawValue)
            await spotService.fetchFearGreed()
        }
    }
    
    private var spotBalanceCard: some View {
        VStack(spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("spot_balance".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    if let perf = spotService.performance {
                        Text("$\(perf.totalCurrentValueAmount, specifier: "%.2f")")
                            .font(.system(size: 28, weight: .bold, design: .rounded))
                            .foregroundColor(.white)
                        
                        HStack(spacing: 4) {
                            Image(systemName: perf.roiPctValue >= 0 ? "arrow.up.right" : "arrow.down.right")
                                .font(.caption2)
                            Text("\(perf.roiPctValue >= 0 ? "+" : "")\(perf.roiPctValue, specifier: "%.2f")%")
                                .font(.caption.bold())
                            Text("ROI")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                        .foregroundColor(perf.roiPctValue >= 0 ? .green : .red)
                    } else if spotService.isLoading {
                        ProgressView()
                            .tint(.enlikoPrimary)
                    } else {
                        Text("$0.00")
                            .font(.system(size: 28, weight: .bold, design: .rounded))
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                // Spot icon
                Image(systemName: "dollarsign.circle.fill")
                    .font(.system(size: 40))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.orange, .yellow],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
            }
        }
        .padding(16)
        .background(Color.enlikoCard)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.orange.opacity(0.3), lineWidth: 1)
        )
    }
    
    private var spotHoldingsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "cube.fill")
                    .foregroundColor(.orange)
                Text("spot_holdings".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                
                Text("\(spotService.performance?.holdingsList.count ?? 0)")
                    .font(.caption.bold())
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.3))
                    .cornerRadius(8)
            }
            
            if let holdings = spotService.performance?.holdingsList, !holdings.isEmpty {
                ForEach(holdings) { holding in
                    SpotHoldingRow(holding: holding)
                }
            } else {
                VStack(spacing: 12) {
                    Image(systemName: "tray")
                        .font(.system(size: 36))
                        .foregroundColor(.secondary.opacity(0.5))
                    Text("spot_no_holdings".localized)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 24)
            }
        }
        .padding(16)
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    private var spotQuickActions: some View {
        HStack(spacing: 12) {
            NavigationLink(destination: SpotTradingView()) {
                HStack(spacing: 8) {
                    Image(systemName: "cart.fill")
                        .font(.subheadline)
                    Text("spot_buy_sell".localized)
                        .font(.subheadline.bold())
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(
                    LinearGradient(
                        colors: [.green, .green.opacity(0.7)],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .cornerRadius(12)
            }
            
            NavigationLink(destination: SpotTradingView()) {
                HStack(spacing: 8) {
                    Image(systemName: "arrow.triangle.2.circlepath")
                        .font(.subheadline)
                    Text("DCA")
                        .font(.subheadline.bold())
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(
                    LinearGradient(
                        colors: [.enlikoPrimary, .enlikoPrimary.opacity(0.7)],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .cornerRadius(12)
            }
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
    @State private var selectedPosition: Position?
    
    private var positionsContent: some View {
        Group {
            if tradingService.isLoadingPositions {
                VStack(spacing: 16) {
                    ProgressView()
                        .scaleEffect(1.5)
                        .tint(.enlikoPrimary)
                    Text("positions_loading".localized)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 40)
            } else if tradingService.positions.isEmpty {
                emptyPositionsView
            } else {
                ForEach(tradingService.positions) { position in
                    PositionCardEnhanced(
                        position: position,
                        onTap: {
                            selectedPosition = position
                        },
                        onClose: {
                            Task {
                                await tradingService.closePosition(symbol: position.symbol, side: position.side)
                            }
                        }
                    )
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
        .sheet(item: $selectedPosition) { position in
            PositionDetailView(position: position)
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

// MARK: - Manual Trade View - Now using AdvancedTradingView
struct ManualTradeView: View {
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        AdvancedTradingView()
    }
}

// MARK: - Enhanced Position Card with Tap & Swipe
struct PositionCardEnhanced: View {
    let position: Position
    let onTap: () -> Void
    let onClose: () -> Void
    
    @State private var offset: CGFloat = 0
    @State private var showCloseButton = false
    
    var body: some View {
        ZStack {
            // Close button background
            HStack {
                Spacer()
                Button {
                    onClose()
                } label: {
                    VStack(spacing: 4) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.title2)
                        Text("Close")
                            .font(.caption.bold())
                    }
                    .foregroundColor(.white)
                    .frame(width: 80)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color.red)
            .cornerRadius(12)
            
            // Main card
            Button {
                onTap()
            } label: {
                VStack(spacing: 12) {
                    // Header
                    HStack {
                        // Symbol & Side
                        HStack(spacing: 8) {
                            Text(position.side.lowercased() == "buy" ? "LONG" : "SHORT")
                                .font(.caption.bold())
                                .foregroundColor(.white)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(position.side.lowercased() == "buy" ? Color.green : Color.red)
                                .cornerRadius(6)
                            
                            Text(position.symbol)
                                .font(.headline.bold())
                                .foregroundColor(.white)
                            
                            Text("\(position.leverage)x")
                                .font(.caption)
                                .foregroundColor(.orange)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.orange.opacity(0.2))
                                .cornerRadius(4)
                        }
                        
                        Spacer()
                        
                        // PnL
                        VStack(alignment: .trailing, spacing: 2) {
                            Text(position.pnlDisplay)
                                .font(.headline.bold())
                                .foregroundColor(position.pnlColor)
                            
                            Text(position.pnlPercentDisplay)
                                .font(.caption)
                                .foregroundColor(position.pnlColor)
                        }
                    }
                    
                    // Details Row
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Entry")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("$\(position.entryPrice, specifier: "%.2f")")
                                .font(.caption.bold())
                                .foregroundColor(.white)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .center, spacing: 2) {
                            Text("Size")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("\(position.size, specifier: "%.4f")")
                                .font(.caption.bold())
                                .foregroundColor(.white)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 2) {
                            Text("Mark")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("$\(position.markPrice ?? position.entryPrice, specifier: "%.2f")")
                                .font(.caption.bold())
                                .foregroundColor(.white)
                        }
                    }
                    
                    // TP/SL Indicators
                    if position.takeProfit != nil || position.stopLoss != nil {
                        HStack(spacing: 16) {
                            if let tp = position.takeProfit, tp > 0 {
                                HStack(spacing: 4) {
                                    Image(systemName: "target")
                                        .font(.caption2)
                                        .foregroundColor(.green)
                                    Text("TP: $\(tp, specifier: "%.2f")")
                                        .font(.caption2)
                                        .foregroundColor(.green)
                                }
                            }
                            
                            if let sl = position.stopLoss, sl > 0 {
                                HStack(spacing: 4) {
                                    Image(systemName: "shield.fill")
                                        .font(.caption2)
                                        .foregroundColor(.red)
                                    Text("SL: $\(sl, specifier: "%.2f")")
                                        .font(.caption2)
                                        .foregroundColor(.red)
                                }
                            }
                            
                            Spacer()
                            
                            // Swipe hint
                            Image(systemName: "chevron.left")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                .padding(16)
                .background(
                    ZStack {
                        Color.enlikoCard
                        // Subtle side accent based on position side
                        HStack {
                            Rectangle()
                                .fill(position.side.lowercased() == "buy" ? Color.enlikoGreen : Color.enlikoRed)
                                .frame(width: 3)
                            Spacer()
                        }
                    }
                )
                .cornerRadius(16)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(
                            (position.side.lowercased() == "buy" ? Color.enlikoGreen : Color.enlikoRed).opacity(0.3),
                            lineWidth: 1
                        )
                )
            }
            .buttonStyle(.plain)
            .offset(x: offset)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        if value.translation.width < 0 {
                            offset = max(value.translation.width, -80)
                        }
                    }
                    .onEnded { value in
                        withAnimation(.spring()) {
                            if value.translation.width < -40 {
                                offset = -80
                                showCloseButton = true
                            } else {
                                offset = 0
                                showCloseButton = false
                            }
                        }
                    }
            )
            .onTapGesture {
                if showCloseButton {
                    withAnimation(.spring()) {
                        offset = 0
                        showCloseButton = false
                    }
                }
            }
        }
    }
}

// MARK: - Spot Holding Row (Compact for embedded view)
struct SpotHoldingRow: View {
    let holding: SpotHolding
    
    var body: some View {
        HStack(spacing: 12) {
            // Coin icon
            Text(coinEmoji(for: holding.coinName))
                .font(.title2)
                .frame(width: 36, height: 36)
                .background(Color.enlikoSurface)
                .cornerRadius(10)
            
            // Coin name & balance
            VStack(alignment: .leading, spacing: 2) {
                Text(holding.coinName)
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                Text("\(holding.balanceValue, specifier: "%.4f")")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // Value & PnL
            VStack(alignment: .trailing, spacing: 2) {
                Text("$\(holding.usdValueAmount, specifier: "%.2f")")
                    .font(.subheadline.bold())
                    .foregroundColor(.white)
                
                HStack(spacing: 2) {
                    Image(systemName: holding.pnlPctValue >= 0 ? "arrow.up.right" : "arrow.down.right")
                        .font(.system(size: 8))
                    Text("\(holding.pnlPctValue >= 0 ? "+" : "")\(holding.pnlPctValue, specifier: "%.1f")%")
                        .font(.caption2.bold())
                }
                .foregroundColor(holding.pnlPctValue >= 0 ? .green : .red)
            }
        }
        .padding(.vertical, 4)
    }
    
    private func coinEmoji(for coin: String) -> String {
        switch coin.uppercased() {
        case "BTC": return "₿"
        case "ETH": return "Ξ"
        case "SOL": return "◎"
        case "USDT", "USDC": return "$"
        default: return "🪙"
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
