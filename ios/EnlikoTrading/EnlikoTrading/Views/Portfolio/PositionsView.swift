//
//  PositionsView.swift
//  EnlikoTrading
//
//  Active positions and orders management
//

import SwiftUI

struct PositionsView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    @State private var selectedTab = 0
    @State private var showCloseConfirmation = false
    @State private var positionToClose: Position?
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Account Selector
                    accountSelector
                        .padding(.horizontal)
                        .padding(.vertical, 8)
                    
                    // Tab Selector
                    tabSelector
                    
                    // Content — conditional rendering (no TabView.page to avoid scroll blocking)
                    if selectedTab == 0 {
                        positionsList
                    } else {
                        ordersList
                    }
                }
            }
            .navigationTitle("positions_title".localized)
            .navigationBarTitleDisplayMode(.large)
            .withRTLSupport()
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { Task { await tradingService.refreshAll() } }) {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(.enlikoPrimary)
                    }
                }
            }
            .alert("positions_close".localized, isPresented: $showCloseConfirmation) {
                Button("common_cancel".localized, role: .cancel) {}
                Button("positions_close".localized, role: .destructive) {
                    if let position = positionToClose {
                        closePosition(position)
                    }
                }
            } message: {
                if let position = positionToClose {
                    Text("Are you sure you want to close your \(position.symbol) position?")
                }
            }
            .refreshable {
                await tradingService.fetchPositions()
                await tradingService.fetchOrders()
            }
            // Refresh when exchange or account type changes
            .onChange(of: appState.currentExchange) { _, _ in
                Task {
                    await tradingService.fetchPositions()
                    await tradingService.fetchOrders()
                }
            }
            .onChange(of: appState.currentAccountType) { _, _ in
                Task {
                    await tradingService.fetchPositions()
                    await tradingService.fetchOrders()
                }
            }
            .task {
                // Initial load
                await tradingService.fetchPositions()
                await tradingService.fetchOrders()
            }
        }
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach(["positions_title".localized, "orders_title".localized].indices, id: \.self) { index in
                let title = ["positions_title".localized, "orders_title".localized][index]
                let count = index == 0 ? tradingService.positions.count : tradingService.orders.count
                
                Button(action: { withAnimation { selectedTab = index } }) {
                    VStack(spacing: 8) {
                        HStack(spacing: 6) {
                            Text(title)
                                .font(.subheadline.weight(.medium))
                            
                            if count > 0 {
                                Text("\(count)")
                                    .font(.caption2.weight(.bold))
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color.enlikoPrimary)
                                    .foregroundColor(.white)
                                    .clipShape(Capsule())
                            }
                        }
                        .foregroundColor(selectedTab == index ? .white : .enlikoTextSecondary)
                        
                        Rectangle()
                            .fill(selectedTab == index ? Color.enlikoPrimary : Color.clear)
                            .frame(height: 2)
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal)
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Account Selector
    private var accountSelector: some View {
        HStack(spacing: 12) {
            // Exchange Picker
            Menu {
                ForEach(Exchange.allCases, id: \.self) { exchange in
                    Button(action: { appState.switchExchange(to: exchange) }) {
                        HStack {
                            Text(exchange.displayName)
                            if appState.currentExchange == exchange {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                }
            } label: {
                HStack {
                    Image(systemName: appState.currentExchange == .bybit ? "b.circle.fill" : "h.circle.fill")
                    Text(appState.currentExchange.displayName)
                    Image(systemName: "chevron.down")
                }
                .font(.subheadline.weight(.medium))
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color.enlikoCard)
                .cornerRadius(10)
            }
            
            // Account Type Picker - use switchAccountType for proper sync
            Picker("Account", selection: Binding(
                get: { appState.currentAccountType },
                set: { appState.switchAccountType(to: $0) }
            )) {
                ForEach(appState.currentExchange.accountTypes, id: \.self) { type in
                    Text(type.displayName).tag(type)
                }
            }
            .pickerStyle(.segmented)
            
            // Account indicator
            Text(appState.currentAccountType.icon)
                .font(.title2)
        }
    }
    
    // MARK: - Positions List
    private var positionsList: some View {
        Group {
            if tradingService.isLoadingPositions {
                loadingView
            } else if tradingService.positions.isEmpty {
                emptyPositionsView
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(tradingService.positions) { position in
                            PositionCard(
                                position: position,
                                onClose: {
                                    positionToClose = position
                                    showCloseConfirmation = true
                                }
                            )
                        }
                    }
                    .padding()
                }
            }
        }
    }
    
    // MARK: - Orders List
    private var ordersList: some View {
        Group {
            if tradingService.orders.isEmpty {
                emptyOrdersView
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(tradingService.orders) { order in
                            OrderCard(
                                order: order,
                                onCancel: { cancelOrder(order) }
                            )
                        }
                    }
                    .padding()
                }
            }
        }
    }
    
    // MARK: - Empty States
    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
            Text("positions_loading".localized)
                .foregroundColor(.enlikoTextSecondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var emptyPositionsView: some View {
        VStack(spacing: 16) {
            Image(systemName: "chart.line.downtrend.xyaxis")
                .font(.system(size: 60))
                .foregroundColor(.enlikoTextMuted)
            
            Text("positions_no_open_title".localized)
                .font(.title3.weight(.medium))
                .foregroundColor(.white)
            
            Text("positions_no_open_subtitle".localized)
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
            
            NavigationLink(destination: TradingView()) {
                HStack {
                    Image(systemName: "plus.circle.fill")
                    Text("Open Position")
                }
                .font(.headline)
                .padding()
                .background(Color.enlikoPrimary)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .padding(.top, 8)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var emptyOrdersView: some View {
        VStack(spacing: 16) {
            Image(systemName: "doc.text")
                .font(.system(size: 60))
                .foregroundColor(.enlikoTextMuted)
            
            Text("positions_no_orders".localized)
                .font(.title3.weight(.medium))
                .foregroundColor(.white)
            
            Text("positions_no_orders_subtitle".localized)
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // MARK: - Actions
    private func closePosition(_ position: Position) {
        Task {
            await tradingService.closePosition(symbol: position.symbol, side: position.side)
        }
    }
    
    private func cancelOrder(_ order: Order) {
        Task {
            await tradingService.cancelOrder(symbol: order.symbol, orderId: order.orderId)
        }
    }
}

// MARK: - Position Card
struct PositionCard: View {
    let position: Position
    let onClose: () -> Void
    @State private var isExpanded = false
    
    private var isLong: Bool {
        position.side.lowercased() == "buy" || position.side.lowercased() == "long"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Main Content
            HStack(alignment: .top) {
                // Side indicator
                Rectangle()
                    .fill(isLong ? Color.enlikoGreen : Color.enlikoRed)
                    .frame(width: 4)
                
                VStack(spacing: 12) {
                    // Header
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            HStack(spacing: 8) {
                                Text(position.symbol)
                                    .font(.headline.bold())
                                    .foregroundColor(.white)
                                
                                Text("\(position.leverage)x")
                                    .font(.caption.weight(.medium))
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color.enlikoCard)
                                    .foregroundColor(.enlikoYellow)
                                    .cornerRadius(4)
                            }
                            
                            Text(isLong ? "LONG" : "SHORT")
                                .font(.caption.weight(.bold))
                                .foregroundColor(isLong ? .enlikoGreen : .enlikoRed)
                        }
                        
                        Spacer()
                        
                        // PnL
                        VStack(alignment: .trailing, spacing: 4) {
                            Text(position.unrealizedPnl.formattedCurrency)
                                .font(.headline.bold())
                                .foregroundColor(position.unrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
                            
                            Text(position.pnlPercent.formattedPercent)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                    }
                    
                    // Stats Row
                    HStack {
                        StatItem(label: "Size", value: "$\(position.notionalValue.compactFormatted)")
                        Spacer()
                        StatItem(label: "Entry", value: "$\(position.entryPrice.formattedPrice)")
                        Spacer()
                        StatItem(label: "Mark", value: "$\(position.markPrice.formattedPrice)")
                    }
                    
                    // Expanded Details
                    if isExpanded {
                        Divider().background(Color.enlikoCardHover)
                        
                        HStack {
                            if let tp = position.takeProfit, tp > 0 {
                                StatItem(label: "Take Profit", value: "$\(tp.formattedPrice)", color: .enlikoGreen)
                            }
                            Spacer()
                            if let sl = position.stopLoss, sl > 0 {
                                StatItem(label: "Stop Loss", value: "$\(sl.formattedPrice)", color: .enlikoRed)
                            }
                            Spacer()
                            StatItem(label: "Margin", value: "$\(position.positionMargin.formattedPrice)")
                        }
                        
                        // Close Button
                        Button(action: onClose) {
                            HStack {
                                Image(systemName: "xmark.circle.fill")
                                Text("Close Position")
                            }
                            .font(.subheadline.weight(.medium))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(Color.enlikoRed.opacity(0.2))
                            .foregroundColor(.enlikoRed)
                            .cornerRadius(8)
                        }
                        .padding(.top, 4)
                    }
                }
                .padding(12)
            }
        }
        .background(
            ZStack {
                Color.enlikoCard
                // Gradient overlay based on PnL
                LinearGradient(
                    colors: [
                        (position.unrealizedPnl >= 0 ? Color.enlikoGreen : Color.enlikoRed).opacity(0.08),
                        Color.clear
                    ],
                    startPoint: .topTrailing,
                    endPoint: .bottomLeading
                )
            }
        )
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(
                    (isLong ? Color.enlikoGreen : Color.enlikoRed).opacity(0.25),
                    lineWidth: 1
                )
        )
        .shadow(color: (isLong ? Color.enlikoGreen : Color.enlikoRed).opacity(0.1), radius: 8, y: 4)
        .onTapGesture { withAnimation(.spring(response: 0.3)) { isExpanded.toggle() } }
    }
}

struct StatItem: View {
    let label: String
    let value: String
    var color: Color = .enlikoTextSecondary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.caption)
                .foregroundColor(.enlikoTextMuted)
            Text(value)
                .font(.subheadline.weight(.medium))
                .foregroundColor(color)
        }
    }
}

// MARK: - Order Card
struct OrderCard: View {
    let order: Order
    let onCancel: () -> Void
    
    private var isBuy: Bool {
        order.side.lowercased() == "buy"
    }
    
    var body: some View {
        HStack {
            Rectangle()
                .fill(isBuy ? Color.enlikoGreen : Color.enlikoRed)
                .frame(width: 4)
            
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(order.symbol)
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    Text(order.orderType.uppercased())
                        .font(.caption.weight(.medium))
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.enlikoPrimary.opacity(0.2))
                        .foregroundColor(.enlikoPrimary)
                        .cornerRadius(4)
                    
                    Spacer()
                    
                    Button(action: onCancel) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.enlikoRed)
                    }
                }
                
                HStack {
                    Text("Qty: \(order.qty.formattedPrice)")
                    Spacer()
                    Text("Price: $\((order.price ?? 0).formattedPrice)")
                }
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            }
            .padding(12)
        }
        .background(
            ZStack {
                Color.enlikoCard
                LinearGradient(
                    colors: [Color.orange.opacity(0.05), Color.clear],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            }
        )
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color.orange.opacity(0.2), lineWidth: 1)
        )
    }
}

#Preview {
    PositionsView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
