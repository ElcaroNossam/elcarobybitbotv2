//
//  ModernPositionsView.swift
//  EnlikoTrading
//
//  Professional positions and orders view with modern UI
//  Sleek cards, smooth animations, haptic feedback
//

import SwiftUI

struct ModernPositionsView: View {
    @StateObject private var tradingService = TradingService.shared
    @StateObject private var appState = AppState.shared
    @State private var selectedTab: Tab = .positions
    @State private var isRefreshing = false
    @State private var selectedPosition: Position?
    @State private var showCloseConfirmation = false
    @State private var positionToClose: Position?
    
    enum Tab: String, CaseIterable {
        case positions = "positions"
        case orders = "orders"
    }
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                headerSection
                
                // Tab Selector
                tabSelector
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                
                // Content
                ScrollView(.vertical, showsIndicators: false) {
                    LazyVStack(spacing: 12) {
                        switch selectedTab {
                        case .positions:
                            positionsContent
                        case .orders:
                            ordersContent
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                    .padding(.bottom, 100)
                }
                .refreshable {
                    await refreshData()
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showCloseConfirmation) {
            if let position = positionToClose {
                ClosePositionSheet(position: position)
                    .presentationDetents([.medium])
                    .presentationDragIndicator(.visible)
            }
        }
        .onAppear {
            Task { await refreshData() }
        }
    }
    
    // MARK: - Header
    private var headerSection: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(selectedTab == .positions ? "positions".localized : "orders".localized)
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.white)
                
                Text(summaryText)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            // Refresh button
            Button(action: { Task { await refreshData() } }) {
                ZStack {
                    Circle()
                        .fill(Color.enlikoCard)
                        .frame(width: 44, height: 44)
                    
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .rotationEffect(.degrees(isRefreshing ? 360 : 0))
                        .animation(isRefreshing ? .linear(duration: 1).repeatForever(autoreverses: false) : .default, value: isRefreshing)
                }
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 16)
    }
    
    private var summaryText: String {
        if selectedTab == .positions {
            let total = tradingService.positions.reduce(0) { $0 + $1.displayPnl }
            let sign = total >= 0 ? "+" : ""
            return "\(tradingService.positions.count) active • \(sign)$\(String(format: "%.2f", abs(total)))"
        } else {
            return "\(tradingService.orders.count) pending"
        }
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach(Tab.allCases, id: \.self) { tab in
                tabButton(tab)
            }
        }
        .padding(4)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.enlikoCard)
        )
    }
    
    private func tabButton(_ tab: Tab) -> some View {
        let isSelected = selectedTab == tab
        let count = tab == .positions ? tradingService.positions.count : tradingService.orders.count
        
        return Button(action: {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                selectedTab = tab
            }
            HapticManager.shared.perform(.selection)
        }) {
            HStack(spacing: 6) {
                Text(tab.rawValue.localized)
                    .font(.system(size: 14, weight: .semibold))
                
                if count > 0 {
                    Text("\(count)")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(isSelected ? .enlikoPrimary : .enlikoTextSecondary)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(
                            Capsule()
                                .fill(isSelected ? Color.enlikoPrimary.opacity(0.2) : Color.enlikoSurface)
                        )
                }
            }
            .foregroundColor(isSelected ? .white : .enlikoTextSecondary)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(
                isSelected ?
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.enlikoSurface) :
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.clear)
            )
        }
    }
    
    // MARK: - Positions Content
    private var positionsContent: some View {
        Group {
            if tradingService.positions.isEmpty {
                emptyState(
                    icon: "chart.bar.xaxis",
                    title: "no_positions".localized,
                    subtitle: "start_trading".localized
                )
            } else {
                ForEach(tradingService.positions) { position in
                    ModernPositionCard(
                        position: position,
                        onClose: {
                            positionToClose = position
                            showCloseConfirmation = true
                        }
                    )
                    .transition(.asymmetric(
                        insertion: .move(edge: .trailing).combined(with: .opacity),
                        removal: .move(edge: .leading).combined(with: .opacity)
                    ))
                }
            }
        }
    }
    
    // MARK: - Orders Content
    private var ordersContent: some View {
        Group {
            if tradingService.orders.isEmpty {
                emptyState(
                    icon: "clock.badge.questionmark",
                    title: "no_orders".localized,
                    subtitle: "place_order".localized
                )
            } else {
                ForEach(tradingService.orders) { order in
                    ModernOrderCard(order: order, onCancel: {
                        Task { await cancelOrder(order) }
                    })
                }
            }
        }
    }
    
    // MARK: - Empty State
    private func emptyState(icon: String, title: String, subtitle: String) -> some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(Color.enlikoCard)
                    .frame(width: 80, height: 80)
                
                Image(systemName: icon)
                    .font(.system(size: 32))
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            VStack(spacing: 4) {
                Text(title)
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
                
                Text(subtitle)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 60)
    }
    
    // MARK: - Actions
    private func refreshData() async {
        isRefreshing = true
        HapticManager.shared.perform(.light)
        await tradingService.refreshAll()
        isRefreshing = false
    }
    
    private func cancelOrder(_ order: Order) async {
        HapticManager.shared.perform(.warning)
        await tradingService.cancelOrder(symbol: order.symbol, orderId: order.orderId)
    }
}

// MARK: - Modern Position Card
struct ModernPositionCard: View {
    let position: Position
    let onClose: () -> Void
    
    @State private var isPressed = false
    @State private var showDetails = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Main Content
            HStack(spacing: 14) {
                // Side Indicator
                sideIndicator
                
                // Symbol & Details
                VStack(alignment: .leading, spacing: 6) {
                    HStack(spacing: 8) {
                        Text(position.displaySymbol)
                            .font(.system(size: 17, weight: .bold))
                            .foregroundColor(.white)
                        
                        ModernBadge(
                            text: "\(position.displayLeverage)x",
                            color: .enlikoAccent
                        )
                    }
                    
                    HStack(spacing: 12) {
                        detailItem(label: "Size", value: position.displaySize.formattedCrypto)
                        detailItem(label: "Entry", value: "$\(position.displayEntryPrice.formattedPrice)")
                    }
                }
                
                Spacer()
                
                // PnL
                VStack(alignment: .trailing, spacing: 4) {
                    Text(position.displayPnl.formattedCurrency)
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(position.displayPnl >= 0 ? .enlikoGreen : .enlikoRed)
                    
                    HStack(spacing: 3) {
                        Image(systemName: position.displayPnl >= 0 ? "arrow.up.right" : "arrow.down.right")
                            .font(.system(size: 10, weight: .bold))
                        
                        Text(String(format: "%.2f%%", abs(position.displayPnlPercent)))
                            .font(.system(size: 13, weight: .semibold))
                    }
                    .foregroundColor(position.displayPnl >= 0 ? .enlikoGreen : .enlikoRed)
                }
            }
            .padding(16)
            
            // Expanded Details
            if showDetails {
                Divider()
                    .background(Color.enlikoBorder)
                
                VStack(spacing: 12) {
                    HStack {
                        expandedDetailItem(label: "Mark Price", value: "$\(position.displayMarkPrice.formattedPrice)")
                        Spacer()
                        expandedDetailItem(label: "Liq. Price", value: "$\(position.displayLiqPrice.formattedPrice)")
                    }
                    
                    HStack {
                        expandedDetailItem(label: "TP", value: position.displayTpPrice > 0 ? "$\(position.displayTpPrice.formattedPrice)" : "-")
                        Spacer()
                        expandedDetailItem(label: "SL", value: position.displaySlPrice > 0 ? "$\(position.displaySlPrice.formattedPrice)" : "-")
                    }
                    
                    // Close Button
                    NeuButton(title: "close_position".localized, icon: "xmark.circle.fill", action: onClose, style: .danger)
                }
                .padding(16)
                .transition(.move(edge: .top).combined(with: .opacity))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.enlikoCard)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(
                            position.displayPnl >= 0 ?
                            Color.enlikoGreen.opacity(showDetails ? 0.5 : 0.2) :
                            Color.enlikoRed.opacity(showDetails ? 0.5 : 0.2),
                            lineWidth: 1
                        )
                )
        )
        .scaleEffect(isPressed ? 0.98 : 1)
        .onTapGesture {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                showDetails.toggle()
            }
            HapticManager.shared.perform(.selection)
        }
        .onLongPressGesture(minimumDuration: 0.1, pressing: { pressing in
            withAnimation(.easeInOut(duration: 0.1)) {
                isPressed = pressing
            }
        }, perform: {})
    }
    
    private var sideIndicator: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 12)
                .fill(position.isLong ? Color.enlikoGreen.opacity(0.15) : Color.enlikoRed.opacity(0.15))
                .frame(width: 50, height: 50)
            
            VStack(spacing: 2) {
                Image(systemName: position.isLong ? "arrow.up" : "arrow.down")
                    .font(.system(size: 18, weight: .bold))
                
                Text(position.isLong ? "LONG" : "SHORT")
                    .font(.system(size: 8, weight: .bold))
            }
            .foregroundColor(position.isLong ? .enlikoGreen : .enlikoRed)
        }
    }
    
    private func detailItem(label: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.system(size: 10, weight: .medium))
                .foregroundColor(.enlikoTextSecondary)
            
            Text(value)
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white.opacity(0.8))
        }
    }
    
    private func expandedDetailItem(label: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.system(size: 11, weight: .medium))
                .foregroundColor(.enlikoTextSecondary)
            
            Text(value)
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
        }
    }
}

// MARK: - Modern Order Card
struct ModernOrderCard: View {
    let order: Order
    let onCancel: () -> Void
    
    var body: some View {
        HStack(spacing: 14) {
            // Side Indicator
            ZStack {
                RoundedRectangle(cornerRadius: 12)
                    .fill(order.isLong ? Color.enlikoGreen.opacity(0.15) : Color.enlikoRed.opacity(0.15))
                    .frame(width: 50, height: 50)
                
                Image(systemName: order.isLong ? "arrow.up" : "arrow.down")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(order.isLong ? .enlikoGreen : .enlikoRed)
            }
            
            // Details
            VStack(alignment: .leading, spacing: 6) {
                HStack(spacing: 8) {
                    Text(order.displaySymbol)
                        .font(.system(size: 17, weight: .bold))
                        .foregroundColor(.white)
                    
                    ModernBadge(
                        text: order.displayOrderType.uppercased(),
                        color: .enlikoAccent
                    )
                }
                
                HStack(spacing: 12) {
                    Text("Qty: \(order.displayQty.formattedCrypto)")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.enlikoTextSecondary)
                    
                    Text("@ $\(order.displayPrice.formattedPrice)")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.enlikoTextSecondary)
                }
            }
            
            Spacer()
            
            // Cancel Button
            Button(action: {
                HapticManager.shared.perform(.warning)
                onCancel()
            }) {
                ZStack {
                    Circle()
                        .fill(Color.enlikoRed.opacity(0.15))
                        .frame(width: 40, height: 40)
                    
                    Image(systemName: "xmark")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundColor(.enlikoRed)
                }
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.enlikoCard)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.enlikoBorder, lineWidth: 1)
                )
        )
    }
}

// MARK: - Close Position Sheet
struct ClosePositionSheet: View {
    let position: Position
    @Environment(\.dismiss) var dismiss
    @State private var isClosing = false
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    ZStack {
                        Circle()
                            .fill(Color.enlikoRed.opacity(0.2))
                            .frame(width: 60, height: 60)
                        
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 30))
                            .foregroundColor(.enlikoRed)
                    }
                    
                    Text("close_position".localized)
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text("\(position.displaySymbol) • \(position.isLong ? "Long" : "Short")")
                        .font(.system(size: 15, weight: .medium))
                        .foregroundColor(.enlikoTextSecondary)
                }
                
                // Position Details
                VStack(spacing: 12) {
                    detailRow(label: "Size", value: position.displaySize.formattedCrypto)
                    detailRow(label: "Entry Price", value: "$\(position.displayEntryPrice.formattedPrice)")
                    detailRow(label: "Current Price", value: "$\(position.displayMarkPrice.formattedPrice)")
                    
                    Divider().background(Color.enlikoBorder)
                    
                    HStack {
                        Text("Unrealized PnL")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.enlikoTextSecondary)
                        
                        Spacer()
                        
                        Text(position.displayPnl.formattedCurrency)
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(position.displayPnl >= 0 ? .enlikoGreen : .enlikoRed)
                    }
                }
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.enlikoCard)
                )
                
                // Buttons
                VStack(spacing: 12) {
                    NeuButton(
                        title: "confirm_close".localized,
                        icon: "checkmark.circle.fill",
                        action: closePosition,
                        isLoading: isClosing,
                        style: .danger
                    )
                    
                    Button(action: { dismiss() }) {
                        Text("cancel".localized)
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.enlikoTextSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 16)
                    }
                }
            }
            .padding(24)
        }
    }
    
    private func detailRow(label: String, value: String) -> some View {
        HStack {
            Text(label)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.enlikoTextSecondary)
            
            Spacer()
            
            Text(value)
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.white)
        }
    }
    
    private func closePosition() {
        isClosing = true
        HapticManager.shared.perform(.heavy)
        
        Task {
            await TradingService.shared.closePosition(symbol: position.symbol)
            await MainActor.run {
                isClosing = false
                dismiss()
                HapticManager.shared.perform(.success)
            }
        }
    }
}

// MARK: - Extensions
extension Double {
    var formattedCrypto: String {
        if self >= 1000 {
            return String(format: "%.2f", self)
        } else if self >= 1 {
            return String(format: "%.4f", self)
        } else {
            return String(format: "%.6f", self)
        }
    }
}

// MARK: - Preview
#Preview {
    NavigationStack {
        ModernPositionsView()
    }
}
