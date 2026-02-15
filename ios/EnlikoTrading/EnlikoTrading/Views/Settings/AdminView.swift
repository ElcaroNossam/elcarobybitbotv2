import SwiftUI
import Combine

// MARK: - Admin Dashboard View
struct AdminView: View {
    @StateObject private var viewModel = AdminViewModel()
    @ObservedObject var localization = LocalizationManager.shared
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    if viewModel.isLoading {
                        ProgressView()
                            .padding(.top, 100)
                    } else if let error = viewModel.errorMessage {
                        errorView(message: error)
                    } else {
                        statsCardsSection
                        tradingStatsSection
                        quickActionsSection
                        pendingPaymentsSection
                    }
                }
                .padding()
            }
            .background(Color.black)
            .navigationTitle("admin_dashboard".localized)
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { Task { await viewModel.loadDashboard() } }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
        .task {
            await viewModel.loadDashboard()
        }
    }
    
    // MARK: - Stats Cards
    private var statsCardsSection: some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible())
        ], spacing: 16) {
            AdminStatCard(
                title: "total_users".localized,
                value: "\(viewModel.dashboard.users.total)",
                icon: "person.2.fill",
                color: .blue,
                subtitle: "+\(viewModel.dashboard.users.newToday) today"
            )
            AdminStatCard(
                title: "premium_users".localized,
                value: "\(viewModel.dashboard.users.premium)",
                icon: "star.fill",
                color: .purple,
                subtitle: "\(viewModel.premiumPercent)% of total"
            )
            AdminStatCard(
                title: "total_revenue".localized,
                value: "$\(viewModel.formatNumber(viewModel.dashboard.revenue.total))",
                icon: "dollarsign.circle.fill",
                color: .green,
                subtitle: "$\(viewModel.formatNumber(viewModel.dashboard.revenue.thisMonth)) this month"
            )
            AdminStatCard(
                title: "pending_payments".localized,
                value: "\(viewModel.dashboard.revenue.pending)",
                icon: "clock.fill",
                color: .yellow,
                subtitle: "awaiting approval"
            )
        }
    }
    
    // MARK: - Trading Stats
    private var tradingStatsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("trading_stats".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            HStack(spacing: 16) {
                TradingStatItem(
                    title: "positions".localized,
                    value: "\(viewModel.dashboard.trading.activePositions)",
                    icon: "chart.line.uptrend.xyaxis"
                )
                TradingStatItem(
                    title: "trades".localized,
                    value: "\(viewModel.dashboard.trading.totalTrades)",
                    icon: "arrow.left.arrow.right"
                )
                TradingStatItem(
                    title: "win_rate".localized,
                    value: "\(viewModel.winRate)%",
                    icon: "percent"
                )
            }
            
            // Today's PnL
            HStack {
                Text("today_pnl".localized)
                    .foregroundColor(.gray)
                Spacer()
                Text(viewModel.formatPnL(viewModel.dashboard.trading.todayPnl))
                    .foregroundColor(viewModel.dashboard.trading.todayPnl >= 0 ? .green : .red)
                    .fontWeight(.semibold)
            }
            .padding()
            .background(Color.enlikoCard)
            .cornerRadius(12)
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    // MARK: - Quick Actions
    private var quickActionsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("quick_actions".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            HStack(spacing: 12) {
                NavigationLink(destination: AdminSupportView()) {
                    QuickActionButton(title: "support_chats".localized, icon: "bubble.left.and.bubble.right", color: .purple)
                }
                NavigationLink(destination: AdminUsersView()) {
                    QuickActionButton(title: "manage_users".localized, icon: "person.2", color: .blue)
                }
            }
            HStack(spacing: 12) {
                NavigationLink(destination: AdminPaymentsView()) {
                    QuickActionButton(title: "payments".localized, icon: "creditcard", color: .green)
                }
                NavigationLink(destination: AdminLicensesView()) {
                    QuickActionButton(title: "licenses".localized, icon: "key", color: .orange)
                }
            }
            HStack(spacing: 12) {
                NavigationLink(destination: AdminErrorsView()) {
                    QuickActionButton(title: "errors".localized, icon: "exclamationmark.triangle", color: .red)
                }
                Spacer()
            }
        }
    }
    
    // MARK: - Pending Payments
    private var pendingPaymentsSection: some View {
        Group {
            if !viewModel.pendingPayments.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("pending_approvals".localized)
                            .font(.headline)
                            .foregroundColor(.white)
                        Spacer()
                        Text("\(viewModel.pendingPayments.count)")
                            .padding(.horizontal, 10)
                            .padding(.vertical, 4)
                            .background(Color.yellow)
                            .foregroundColor(.black)
                            .cornerRadius(12)
                    }
                    
                    ForEach(viewModel.pendingPayments.prefix(3)) { payment in
                        PendingPaymentRow(payment: payment, viewModel: viewModel)
                    }
                }
                .padding()
                .background(Color.enlikoCard)
                .cornerRadius(16)
            }
        }
    }
    
    private func errorView(message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 50))
                .foregroundColor(.red)
            Text(message)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
            Button("retry".localized) {
                Task { await viewModel.loadDashboard() }
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(.top, 100)
    }
}

// MARK: - Supporting Views

struct AdminStatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    let subtitle: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Spacer()
            }
            Text(value)
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(.white)
            Text(title)
                .font(.caption)
                .foregroundColor(.gray)
            Text(subtitle)
                .font(.caption2)
                .foregroundColor(color.opacity(0.8))
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
}

struct TradingStatItem: View {
    let title: String
    let value: String
    let icon: String
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .foregroundColor(.gray)
            Text(value)
                .font(.title3)
                .fontWeight(.semibold)
                .foregroundColor(.white)
            Text(title)
                .font(.caption)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.black.opacity(0.3))
        .cornerRadius(12)
    }
}

struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
            Text(title)
                .font(.caption)
        }
        .foregroundColor(color)
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.15))
        .cornerRadius(12)
    }
}

struct PendingPaymentRow: View {
    let payment: AdminPayment
    @ObservedObject var viewModel: AdminViewModel
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(payment.username ?? "User \(payment.userId)")
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                Text("$\(String(format: "%.2f", payment.amount)) • \(payment.currency)")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            Spacer()
            HStack(spacing: 12) {
                Button(action: {
                    Task { await viewModel.approvePayment(paymentId: payment.id) }
                }) {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                        .font(.title2)
                }
                Button(action: {
                    Task { await viewModel.rejectPayment(paymentId: payment.id) }
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.red)
                        .font(.title2)
                }
            }
        }
        .padding()
        .background(Color.black.opacity(0.3))
        .cornerRadius(12)
    }
}

// MARK: - Placeholder Views
struct AdminUsersView: View {
    var body: some View {
        Text("users_management".localized)
            .navigationTitle("manage_users".localized)
    }
}

struct AdminPaymentsView: View {
    var body: some View {
        Text("payments".localized)
            .navigationTitle("payments".localized)
    }
}

struct AdminLicensesView: View {
    var body: some View {
        Text("licenses".localized)
            .navigationTitle("licenses".localized)
    }
}

struct AdminErrorsView: View {
    var body: some View {
        Text("errors".localized)
            .navigationTitle("errors".localized)
    }
}

// MARK: - View Model

@MainActor
class AdminViewModel: ObservableObject {
    @Published var dashboard = AdminDashboard()
    @Published var pendingPayments: [AdminPayment] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    var premiumPercent: Int {
        guard dashboard.users.total > 0 else { return 0 }
        return Int(Double(dashboard.users.premium) / Double(dashboard.users.total) * 100)
    }
    
    var winRate: Int {
        guard dashboard.trading.totalTrades > 0 else { return 0 }
        return Int(Double(dashboard.trading.wins) / Double(dashboard.trading.totalTrades) * 100)
    }
    
    func loadDashboard() async {
        isLoading = true
        errorMessage = nil
        
        do {
            dashboard = try await NetworkService.shared.get("/admin/dashboard")
            // Load pending payments
            let paymentsResponse: AdminPaymentsResponse = try await NetworkService.shared.get("/admin/payments?status=pending&limit=5")
            pendingPayments = paymentsResponse.list
        } catch NetworkError.unauthorized {
            errorMessage = "Access denied. Admin only."
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    func approvePayment(paymentId: Int) async {
        do {
            try await NetworkService.shared.postIgnoreResponse("/admin/payments/\(paymentId)/approve")
            await loadDashboard()
        } catch {
            errorMessage = "Failed to approve: \(error.localizedDescription)"
        }
    }
    
    func rejectPayment(paymentId: Int) async {
        do {
            try await NetworkService.shared.postIgnoreResponse("/admin/payments/\(paymentId)/reject")
            await loadDashboard()
        } catch {
            errorMessage = "Failed to reject: \(error.localizedDescription)"
        }
    }
    
    func formatNumber(_ number: Double) -> String {
        if number >= 1000000 {
            return String(format: "%.1fM", number / 1000000)
        } else if number >= 1000 {
            return String(format: "%.1fK", number / 1000)
        }
        return String(format: "%.0f", number)
    }
    
    func formatPnL(_ value: Double) -> String {
        let sign = value >= 0 ? "+" : ""
        return "\(sign)$\(String(format: "%.2f", value))"
    }
}

// MARK: - Models

struct AdminDashboard: Codable {
    var users: AdminUsersStats = AdminUsersStats()
    var revenue: AdminRevenueStats = AdminRevenueStats()
    var trading: AdminTradingStats = AdminTradingStats()
}

struct AdminUsersStats: Codable {
    var total: Int = 0
    var active: Int = 0
    var premium: Int = 0
    var newToday: Int = 0
    
    enum CodingKeys: String, CodingKey {
        case total, active, premium
        case newToday = "new_today"
    }
}

struct AdminRevenueStats: Codable {
    var total: Double = 0
    var thisMonth: Double = 0
    var totalPayments: Int = 0
    var pending: Int = 0
    
    enum CodingKeys: String, CodingKey {
        case total, pending
        case thisMonth = "this_month"
        case totalPayments = "total_payments"
    }
}

struct AdminTradingStats: Codable {
    var activePositions: Int = 0
    var totalTrades: Int = 0
    var wins: Int = 0
    var totalPnl: Double = 0
    var todayTrades: Int = 0
    var todayPnl: Double = 0
    
    enum CodingKeys: String, CodingKey {
        case wins
        case activePositions = "active_positions"
        case totalTrades = "total_trades"
        case totalPnl = "total_pnl"
        case todayTrades = "today_trades"
        case todayPnl = "today_pnl"
    }
}

struct AdminPayment: Codable, Identifiable {
    let id: Int
    let userId: Int
    let username: String?
    let firstName: String?
    let amount: Double
    let currency: String
    let paymentType: String
    let status: String
    let txHash: String?
    let licenseType: String?
    let licenseDays: Int?
    let createdAt: String?
    
    enum CodingKeys: String, CodingKey {
        case id, username, amount, currency, status
        case userId = "user_id"
        case firstName = "first_name"
        case paymentType = "payment_type"
        case txHash = "tx_hash"
        case licenseType = "license_type"
        case licenseDays = "license_days"
        case createdAt = "created_at"
    }
}

struct AdminPaymentsResponse: Codable {
    let total: Int
    let pending: Int
    let totalRevenue: Double
    let page: Int
    let pages: Int
    let list: [AdminPayment]
    
    enum CodingKeys: String, CodingKey {
        case total, pending, page, pages, list
        case totalRevenue = "total_revenue"
    }
}

#Preview {
    AdminView()
}
