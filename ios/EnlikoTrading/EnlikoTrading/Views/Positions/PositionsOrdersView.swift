//
//  PositionsOrdersView.swift
//  EnlikoTrading
//
//  Combined Positions and Orders view with tab switching
//

import SwiftUI
import Combine

struct PositionsOrdersView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = PositionsOrdersViewModel()
    @State private var selectedTab: PositionsOrdersTab = .positions
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab Selector
            HStack(spacing: 0) {
                ForEach(PositionsOrdersTab.allCases, id: \.self) { tab in
                    Button {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedTab = tab
                        }
                    } label: {
                        VStack(spacing: 8) {
                            HStack(spacing: 6) {
                                Text(tab.title)
                                    .font(.subheadline.bold())
                                
                                if tab == .positions && viewModel.positions.count > 0 {
                                    Text("\(viewModel.positions.count)")
                                        .font(.caption2.bold())
                                        .foregroundColor(.white)
                                        .padding(.horizontal, 6)
                                        .padding(.vertical, 2)
                                        .background(Color.enlikoPrimary)
                                        .cornerRadius(8)
                                } else if tab == .orders && viewModel.orders.count > 0 {
                                    Text("\(viewModel.orders.count)")
                                        .font(.caption2.bold())
                                        .foregroundColor(.white)
                                        .padding(.horizontal, 6)
                                        .padding(.vertical, 2)
                                        .background(Color.orange)
                                        .cornerRadius(8)
                                }
                            }
                            
                            Rectangle()
                                .fill(selectedTab == tab ? Color.enlikoPrimary : Color.clear)
                                .frame(height: 2)
                        }
                        .foregroundColor(selectedTab == tab ? .white : .secondary)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .padding(.horizontal)
            .background(Color.enlikoSurface)
            
            // Content
            ScrollView {
                LazyVStack(spacing: 12) {
                    if viewModel.isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                            .padding(.top, 40)
                    } else {
                        switch selectedTab {
                        case .positions:
                            positionsContent
                        case .orders:
                            ordersContent
                        }
                    }
                }
                .padding()
            }
            .background(Color.enlikoBackground)
        }
        .navigationTitle(selectedTab.title)
        .navigationBarTitleDisplayMode(.inline)
        .refreshable {
            await viewModel.refresh(
                accountType: appState.currentAccountType.rawValue,
                exchange: appState.currentExchange.rawValue
            )
        }
        .onAppear {
            Task {
                await viewModel.refresh(
                    accountType: appState.currentAccountType.rawValue,
                    exchange: appState.currentExchange.rawValue
                )
            }
        }
        .onChange(of: appState.currentExchange) { _, _ in
            Task { await viewModel.refresh(accountType: appState.currentAccountType.rawValue, exchange: appState.currentExchange.rawValue) }
        }
        .onChange(of: appState.currentAccountType) { _, _ in
            Task { await viewModel.refresh(accountType: appState.currentAccountType.rawValue, exchange: appState.currentExchange.rawValue) }
        }
        .alert("error".localized, isPresented: .constant(viewModel.error != nil)) {
            Button("OK") { viewModel.error = nil }
        } message: {
            Text(viewModel.error ?? "")
        }
    }
    
    // MARK: - Positions Content
    @ViewBuilder
    private var positionsContent: some View {
        if viewModel.positions.isEmpty {
            emptyState(icon: "chart.line.uptrend.xyaxis", message: "no_open_positions".localized)
        } else {
            ForEach(viewModel.positions) { position in
                PositionCardView(
                    position: position,
                    onClose: {
                        Task {
                            await viewModel.closePosition(
                                position: position,
                                accountType: appState.currentAccountType.rawValue,
                                exchange: appState.currentExchange.rawValue
                            )
                        }
                    },
                    onModify: {
                        // Navigate to modify TP/SL
                    }
                )
            }
        }
    }
    
    // MARK: - Orders Content
    @ViewBuilder
    private var ordersContent: some View {
        if viewModel.orders.isEmpty {
            emptyState(icon: "clock.fill", message: "no_pending_orders".localized)
        } else {
            ForEach(viewModel.orders) { order in
                OrderCardView(
                    order: order,
                    onCancel: {
                        Task {
                            await viewModel.cancelOrder(
                                order: order,
                                accountType: appState.currentAccountType.rawValue,
                                exchange: appState.currentExchange.rawValue
                            )
                        }
                    }
                )
            }
        }
    }
    
    private func emptyState(icon: String, message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 48))
                .foregroundColor(.secondary.opacity(0.5))
            Text(message)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.top, 60)
    }
}

// MARK: - Tab Enum
enum PositionsOrdersTab: CaseIterable {
    case positions
    case orders
    
    var title: String {
        switch self {
        case .positions: return "positions".localized
        case .orders: return "orders".localized
        }
    }
}

// MARK: - Position Card View
struct PositionCardView: View {
    let position: Position
    let onClose: () -> Void
    let onModify: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(position.symbol)
                        .font(.headline.bold())
                        .foregroundColor(.white)
                    
                    HStack(spacing: 8) {
                        Text(position.side.uppercased())
                            .font(.caption.bold())
                            .foregroundColor(position.side.lowercased().contains("buy") ? .enlikoGreen : .enlikoRed)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background((position.side.lowercased().contains("buy") ? Color.enlikoGreen : Color.enlikoRed).opacity(0.2))
                            .cornerRadius(6)
                        
                        Text("\(position.leverage)x")
                            .font(.caption.bold())
                            .foregroundColor(.orange)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.orange.opacity(0.2))
                            .cornerRadius(6)
                    }
                }
                
                Spacer()
                
                // PnL
                VStack(alignment: .trailing, spacing: 4) {
                    Text(position.unrealizedPnl.formattedSignedAmount)
                        .font(.title3.bold())
                        .foregroundColor(position.unrealizedPnl >= 0 ? .enlikoGreen : .enlikoRed)
                    
                    Text("\(position.pnlPercent >= 0 ? "+" : "")\(String(format: "%.2f", position.pnlPercent))%")
                        .font(.caption.bold())
                        .foregroundColor(position.pnlPercent >= 0 ? .enlikoGreen : .enlikoRed)
                }
            }
            
            // Info Grid
            HStack(spacing: 16) {
                InfoColumn(title: "entry".localized, value: position.entryPrice.formattedPrice)
                InfoColumn(title: "mark".localized, value: position.markPrice.formattedPrice)
                InfoColumn(title: "size".localized, value: String(format: "%.4f", position.size))
            }
            
            Divider().background(Color.enlikoBorder)
            
            // Actions
            HStack(spacing: 12) {
                Button {
                    onModify()
                } label: {
                    HStack {
                        Image(systemName: "slider.horizontal.3")
                        Text("modify".localized)
                    }
                    .font(.subheadline.bold())
                    .foregroundColor(.enlikoPrimary)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(Color.enlikoPrimary.opacity(0.15))
                    .cornerRadius(10)
                }
                
                Button {
                    onClose()
                } label: {
                    HStack {
                        Image(systemName: "xmark.circle.fill")
                        Text("close".localized)
                    }
                    .font(.subheadline.bold())
                    .foregroundColor(.enlikoRed)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(Color.enlikoRed.opacity(0.15))
                    .cornerRadius(10)
                }
            }
        }
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
}

// MARK: - Order Card View
struct OrderCardView: View {
    let order: Order
    let onCancel: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(order.symbol)
                        .font(.headline.bold())
                        .foregroundColor(.white)
                    
                    HStack(spacing: 8) {
                        Text(order.side.uppercased())
                            .font(.caption.bold())
                            .foregroundColor(order.side.lowercased().contains("buy") ? .enlikoGreen : .enlikoRed)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background((order.side.lowercased().contains("buy") ? Color.enlikoGreen : Color.enlikoRed).opacity(0.2))
                            .cornerRadius(6)
                        
                        Text(order.orderType.uppercased())
                            .font(.caption.bold())
                            .foregroundColor(.cyan)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.cyan.opacity(0.2))
                            .cornerRadius(6)
                    }
                }
                
                Spacer()
                
                // Status
                Text((order.status ?? "pending").capitalized)
                    .font(.caption.bold())
                    .foregroundColor(.orange)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.orange.opacity(0.2))
                    .cornerRadius(8)
            }
            
            // Info
            HStack(spacing: 16) {
                InfoColumn(title: "price".localized, value: (order.price ?? 0).formattedPrice)
                InfoColumn(title: "size".localized, value: String(format: "%.4f", order.qty))
            }
            
            Divider().background(Color.enlikoBorder)
            
            // Cancel Button
            Button {
                onCancel()
            } label: {
                HStack {
                    Image(systemName: "xmark.circle.fill")
                    Text("cancel_order".localized)
                }
                .font(.subheadline.bold())
                .foregroundColor(.orange)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 10)
                .background(Color.orange.opacity(0.15))
                .cornerRadius(10)
            }
        }
        .padding(16)
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
}

// MARK: - Info Column
struct InfoColumn: View {
    let title: String
    let value: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
            Text(value)
                .font(.subheadline.bold())
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

// MARK: - ViewModel
@MainActor
class PositionsOrdersViewModel: ObservableObject {
    @Published var positions: [Position] = []
    @Published var orders: [Order] = []
    @Published var isLoading = false
    @Published var error: String?
    
    private let network = NetworkService.shared
    
    @MainActor
    func refresh(accountType: String, exchange: String) async {
        isLoading = true
        defer { isLoading = false }
        
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.fetchPositions(accountType: accountType, exchange: exchange) }
            group.addTask { await self.fetchOrders(accountType: accountType, exchange: exchange) }
        }
    }
    
    @MainActor
    private func fetchPositions(accountType: String, exchange: String) async {
        do {
            let response: PositionsResponse = try await network.get("/trading/positions", params: ["account_type": accountType, "exchange": exchange])
            positions = response.positionsData
        } catch {
            print("Failed to fetch positions: \(error)")
        }
    }
    
    @MainActor
    private func fetchOrders(accountType: String, exchange: String) async {
        do {
            // Try raw array first (server returns [...] directly)
            let rawOrders: [Order] = try await network.get("/trading/orders", params: ["account_type": accountType, "exchange": exchange])
            orders = rawOrders
        } catch {
            // Fallback to wrapped OrdersResponse
            do {
                let response: OrdersResponse = try await network.get("/trading/orders", params: ["account_type": accountType, "exchange": exchange])
                orders = response.ordersData
            } catch {
                print("Failed to fetch orders: \(error)")
            }
        }
    }
    
    @MainActor
    func closePosition(position: Position, accountType: String, exchange: String) async {
        do {
            let request = ClosePositionRequest(symbol: position.symbol, side: position.side, qty: nil, exchange: exchange, accountType: accountType)
            let _: EmptyResponse = try await network.post("/trading/close", body: request)
            await fetchPositions(accountType: accountType, exchange: exchange)
        } catch {
            self.error = "Failed to close position: \(error.localizedDescription)"
        }
    }
    
    @MainActor
    func cancelOrder(order: Order, accountType: String, exchange: String) async {
        do {
            // Build URL with query params
            let endpoint = "/trading/orders/\(order.orderId)?account_type=\(accountType)&exchange=\(exchange)"
            try await network.delete(endpoint)
            await fetchOrders(accountType: accountType, exchange: exchange)
        } catch {
            self.error = "Failed to cancel order: \(error.localizedDescription)"
        }
    }
}

// MARK: - Response Types (use existing from Models.swift)
// PositionsResponse, OrdersResponse, ClosePositionRequest - already in Models.swift

struct EmptyResult: Codable {}

#Preview {
    NavigationStack {
        PositionsOrdersView()
            .environmentObject(AppState.shared)
            .preferredColorScheme(.dark)
    }
}
