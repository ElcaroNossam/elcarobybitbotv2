//
//  PositionsView.swift
//  LyxenTrading
//
//  Active positions and orders management
//

import SwiftUI

struct PositionsView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @State private var selectedTab = 0
    @State private var showCloseConfirmation = false
    @State private var positionToClose: Position?
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.lyxenBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Tab Selector
                    tabSelector
                    
                    // Content
                    TabView(selection: $selectedTab) {
                        positionsList
                            .tag(0)
                        
                        ordersList
                            .tag(1)
                    }
                    .tabViewStyle(.page(indexDisplayMode: .never))
                }
            }
            .navigationTitle("Positions")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { Task { await tradingService.refreshAll() } }) {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(.lyxenPrimary)
                    }
                }
            }
            .alert("Close Position", isPresented: $showCloseConfirmation) {
                Button("Cancel", role: .cancel) {}
                Button("Close", role: .destructive) {
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
        }
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach(["Positions", "Orders"].indices, id: \.self) { index in
                let title = ["Positions", "Orders"][index]
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
                                    .background(Color.lyxenPrimary)
                                    .foregroundColor(.white)
                                    .clipShape(Capsule())
                            }
                        }
                        .foregroundColor(selectedTab == index ? .white : .lyxenTextSecondary)
                        
                        Rectangle()
                            .fill(selectedTab == index ? Color.lyxenPrimary : Color.clear)
                            .frame(height: 2)
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal)
        .background(Color.lyxenSurface)
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
            Text("Loading positions...")
                .foregroundColor(.lyxenTextSecondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var emptyPositionsView: some View {
        VStack(spacing: 16) {
            Image(systemName: "chart.line.downtrend.xyaxis")
                .font(.system(size: 60))
                .foregroundColor(.lyxenTextMuted)
            
            Text("No Open Positions")
                .font(.title3.weight(.medium))
                .foregroundColor(.white)
            
            Text("Your active trades will appear here")
                .font(.subheadline)
                .foregroundColor(.lyxenTextSecondary)
            
            NavigationLink(destination: TradingView()) {
                HStack {
                    Image(systemName: "plus.circle.fill")
                    Text("Open Position")
                }
                .font(.headline)
                .padding()
                .background(Color.lyxenPrimary)
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
                .foregroundColor(.lyxenTextMuted)
            
            Text("No Pending Orders")
                .font(.title3.weight(.medium))
                .foregroundColor(.white)
            
            Text("Limit orders will appear here")
                .font(.subheadline)
                .foregroundColor(.lyxenTextSecondary)
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
                    .fill(isLong ? Color.lyxenGreen : Color.lyxenRed)
                    .frame(width: 4)
                
                VStack(spacing: 12) {
                    // Header
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            HStack(spacing: 8) {
                                Text(position.symbol)
                                    .font(.headline.bold())
                                    .foregroundColor(.white)
                                
                                Text("\(position.leverage ?? 10)x")
                                    .font(.caption.weight(.medium))
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color.lyxenCard)
                                    .foregroundColor(.lyxenYellow)
                                    .cornerRadius(4)
                            }
                            
                            Text(isLong ? "LONG" : "SHORT")
                                .font(.caption.weight(.bold))
                                .foregroundColor(isLong ? .lyxenGreen : .lyxenRed)
                        }
                        
                        Spacer()
                        
                        // PnL
                        VStack(alignment: .trailing, spacing: 4) {
                            Text(position.unrealizedPnl.formattedCurrency)
                                .font(.headline.bold())
                                .foregroundColor(position.unrealizedPnl >= 0 ? .lyxenGreen : .lyxenRed)
                            
                            Text((position.pnlPercent ?? 0).formattedPercent)
                                .font(.caption)
                                .foregroundColor(.lyxenTextSecondary)
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
                        Divider().background(Color.lyxenCardHover)
                        
                        HStack {
                            if let tp = position.takeProfit, tp > 0 {
                                StatItem(label: "Take Profit", value: "$\(tp.formattedPrice)", color: .lyxenGreen)
                            }
                            Spacer()
                            if let sl = position.stopLoss, sl > 0 {
                                StatItem(label: "Stop Loss", value: "$\(sl.formattedPrice)", color: .lyxenRed)
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
                            .background(Color.lyxenRed.opacity(0.2))
                            .foregroundColor(.lyxenRed)
                            .cornerRadius(8)
                        }
                        .padding(.top, 4)
                    }
                }
                .padding(12)
            }
        }
        .background(Color.lyxenCard)
        .cornerRadius(12)
        .onTapGesture { withAnimation { isExpanded.toggle() } }
    }
}

struct StatItem: View {
    let label: String
    let value: String
    var color: Color = .lyxenTextSecondary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.caption)
                .foregroundColor(.lyxenTextMuted)
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
                .fill(isBuy ? Color.lyxenGreen : Color.lyxenRed)
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
                        .background(Color.lyxenPrimary.opacity(0.2))
                        .foregroundColor(.lyxenPrimary)
                        .cornerRadius(4)
                    
                    Spacer()
                    
                    Button(action: onCancel) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.lyxenRed)
                    }
                }
                
                HStack {
                    Text("Qty: \(order.qty.formattedPrice)")
                    Spacer()
                    Text("Price: $\((order.price ?? 0).formattedPrice)")
                }
                .font(.caption)
                .foregroundColor(.lyxenTextSecondary)
            }
            .padding(12)
        }
        .background(Color.lyxenCard)
        .cornerRadius(12)
    }
}

#Preview {
    PositionsView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
