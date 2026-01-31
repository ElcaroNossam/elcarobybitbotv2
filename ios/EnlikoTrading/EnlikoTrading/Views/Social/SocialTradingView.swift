//
//  SocialTradingView.swift
//  EnlikoTrading
//
//  👥 Social Trading & Copy Trading Features
//  ==========================================
//
//  Features:
//  1. Leaderboard of top traders
//  2. Copy trading setup
//  3. Trader profiles
//  4. Performance charts
//  5. Follow/Unfollow system
//

import SwiftUI
import Combine

// MARK: - Models

struct TopTrader: Identifiable, Codable {
    let id: String
    let username: String
    let avatar: String?
    let rank: Int
    let roi30d: Double
    let winRate: Double
    let totalTrades: Int
    let followers: Int
    let maxDrawdown: Double
    let strategies: [String]
    let isVerified: Bool
    
    var displayName: String {
        username.isEmpty ? "Trader #\(rank)" : username
    }
}

struct CopySettings: Codable {
    var traderId: String
    var copyPercentage: Double // % of their trade size to copy
    var maxPositionSize: Double // Max USDT per position
    var copyType: CopyType
    var isActive: Bool
    
    enum CopyType: String, Codable {
        case proportional = "proportional" // Copy proportionally to their trade size
        case fixed = "fixed" // Fixed amount per trade
    }
}

struct TraderStats: Identifiable {
    let id = UUID()
    let date: Date
    let pnl: Double
    let cumulativePnL: Double
}

// MARK: - View Model

class SocialTradingViewModel: ObservableObject {
    @Published var topTraders: [TopTrader] = []
    @Published var followedTraders: [TopTrader] = []
    @Published var selectedTimeframe: Timeframe = .month
    @Published var isLoading = false
    @Published var searchQuery = ""
    
    enum Timeframe: String, CaseIterable {
        case week = "7D"
        case month = "30D"
        case quarter = "90D"
        case all = "All"
    }
    
    init() {
        loadMockData()
    }
    
    func loadMockData() {
        isLoading = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            self?.topTraders = [
                TopTrader(
                    id: "1", username: "CryptoWhale", avatar: nil, rank: 1,
                    roi30d: 127.5, winRate: 78.4, totalTrades: 342,
                    followers: 12500, maxDrawdown: -8.2,
                    strategies: ["OI", "Scalper"], isVerified: true
                ),
                TopTrader(
                    id: "2", username: "BTCMaster", avatar: nil, rank: 2,
                    roi30d: 95.3, winRate: 72.1, totalTrades: 189,
                    followers: 8700, maxDrawdown: -12.5,
                    strategies: ["Fibonacci"], isVerified: true
                ),
                TopTrader(
                    id: "3", username: "AlphaTrader", avatar: nil, rank: 3,
                    roi30d: 82.1, winRate: 68.9, totalTrades: 456,
                    followers: 6200, maxDrawdown: -15.3,
                    strategies: ["Scryptomera", "RSI"], isVerified: false
                ),
                TopTrader(
                    id: "4", username: "SwingKing", avatar: nil, rank: 4,
                    roi30d: 67.8, winRate: 81.2, totalTrades: 98,
                    followers: 4300, maxDrawdown: -5.1,
                    strategies: ["Wyckoff"], isVerified: true
                ),
                TopTrader(
                    id: "5", username: "ScalperPro", avatar: nil, rank: 5,
                    roi30d: 58.2, winRate: 65.7, totalTrades: 1250,
                    followers: 3100, maxDrawdown: -18.7,
                    strategies: ["Scalper"], isVerified: false
                )
            ]
            
            self?.isLoading = false
        }
    }
    
    var filteredTraders: [TopTrader] {
        if searchQuery.isEmpty {
            return topTraders
        }
        return topTraders.filter {
            $0.username.localizedCaseInsensitiveContains(searchQuery) ||
            $0.strategies.contains { $0.localizedCaseInsensitiveContains(searchQuery) }
        }
    }
}

// MARK: - Social Trading View

struct SocialTradingView: View {
    @StateObject private var viewModel = SocialTradingViewModel()
    @State private var showCopySheet = false
    @State private var selectedTrader: TopTrader?
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Header Stats
                statsHeader
                
                // Timeframe Selector
                timeframeSelector
                
                // Search Bar
                searchBar
                
                // Leaderboard
                leaderboardSection
                
                // Followed Traders
                if !viewModel.followedTraders.isEmpty {
                    followedTradersSection
                }
            }
            .padding()
        }
        .navigationTitle("Social Trading")
        .sheet(item: $selectedTrader) { trader in
            TraderProfileSheet(trader: trader)
        }
    }
    
    // MARK: - Stats Header
    
    private var statsHeader: some View {
        HStack(spacing: 16) {
            SocialStatCard(
                title: "Top ROI",
                value: "+127.5%",
                subtitle: "30 days",
                icon: "chart.line.uptrend.xyaxis",
                color: .green
            )
            
            SocialStatCard(
                title: "Traders",
                value: "2.4K",
                subtitle: "Active",
                icon: "person.2.fill",
                color: .blue
            )
            
            SocialStatCard(
                title: "Volume",
                value: "$12.5M",
                subtitle: "Copied",
                icon: "dollarsign.circle.fill",
                color: .orange
            )
        }
    }
    
    // MARK: - Timeframe Selector
    
    private var timeframeSelector: some View {
        HStack(spacing: 8) {
            ForEach(SocialTradingViewModel.Timeframe.allCases, id: \.self) { timeframe in
                Button(action: {
                    withAnimation {
                        viewModel.selectedTimeframe = timeframe
                    }
                }) {
                    Text(timeframe.rawValue)
                        .font(.caption.bold())
                        .foregroundColor(viewModel.selectedTimeframe == timeframe ? .white : .secondary)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(
                            Capsule()
                                .fill(viewModel.selectedTimeframe == timeframe ? Color.purple : Color(.systemGray5))
                        )
                }
            }
            Spacer()
        }
    }
    
    // MARK: - Search Bar
    
    private var searchBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
            
            TextField("Search traders or strategies...", text: $viewModel.searchQuery)
                .textFieldStyle(.plain)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    // MARK: - Leaderboard Section
    
    private var leaderboardSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("🏆 Leaderboard")
                    .font(.headline)
                Spacer()
                Button("See All") {}
                    .font(.caption)
                    .foregroundColor(.purple)
            }
            
            if viewModel.isLoading {
                ForEach(0..<3, id: \.self) { _ in
                    TraderRowSkeleton()
                }
            } else {
                ForEach(viewModel.filteredTraders) { trader in
                    TraderRow(trader: trader) {
                        selectedTrader = trader
                    }
                }
            }
        }
    }
    
    // MARK: - Followed Traders Section
    
    private var followedTradersSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("👀 Following")
                    .font(.headline)
                Spacer()
                Text("\(viewModel.followedTraders.count) traders")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            ForEach(viewModel.followedTraders) { trader in
                TraderRow(trader: trader) {
                    selectedTrader = trader
                }
            }
        }
    }
}

// MARK: - Stat Card

struct SocialStatCard: View {
    let title: String
    let value: String
    let subtitle: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Spacer()
            }
            
            Text(value)
                .font(.title2.bold())
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

// MARK: - Trader Row

struct TraderRow: View {
    let trader: TopTrader
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 12) {
                // Rank
                ZStack {
                    Circle()
                        .fill(rankColor)
                        .frame(width: 32, height: 32)
                    
                    Text("\(trader.rank)")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundColor(.white)
                }
                
                // Avatar
                ZStack {
                    Circle()
                        .fill(Color.purple.opacity(0.3))
                        .frame(width: 44, height: 44)
                    
                    Text(String(trader.username.prefix(2)).uppercased())
                        .font(.system(size: 14, weight: .bold))
                        .foregroundColor(.purple)
                }
                
                // Info
                VStack(alignment: .leading, spacing: 2) {
                    HStack(spacing: 4) {
                        Text(trader.displayName)
                            .font(.subheadline.bold())
                            .foregroundColor(.primary)
                        
                        if trader.isVerified {
                            Image(systemName: "checkmark.seal.fill")
                                .font(.caption)
                                .foregroundColor(.blue)
                        }
                    }
                    
                    HStack(spacing: 8) {
                        Text("\(trader.followers) followers")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Text("•")
                            .foregroundColor(.secondary)
                        
                        Text(trader.strategies.first ?? "")
                            .font(.caption)
                            .foregroundColor(.purple)
                    }
                }
                
                Spacer()
                
                // ROI
                VStack(alignment: .trailing, spacing: 2) {
                    Text(String(format: "%+.1f%%", trader.roi30d))
                        .font(.subheadline.bold())
                        .foregroundColor(trader.roi30d >= 0 ? .green : .red)
                    
                    Text("Win: \(String(format: "%.0f%%", trader.winRate))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemBackground))
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.05), radius: 5)
        }
        .buttonStyle(.plain)
    }
    
    var rankColor: Color {
        switch trader.rank {
        case 1: return Color.yellow
        case 2: return Color.gray
        case 3: return Color.orange
        default: return Color.purple
        }
    }
}

// MARK: - Trader Row Skeleton

struct TraderRowSkeleton: View {
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(Color(.systemGray5))
                .frame(width: 32, height: 32)
            
            Circle()
                .fill(Color(.systemGray5))
                .frame(width: 44, height: 44)
            
            VStack(alignment: .leading, spacing: 4) {
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color(.systemGray5))
                    .frame(width: 120, height: 14)
                
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color(.systemGray5))
                    .frame(width: 80, height: 10)
            }
            
            Spacer()
            
            RoundedRectangle(cornerRadius: 4)
                .fill(Color(.systemGray5))
                .frame(width: 60, height: 16)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shimmer()
    }
}

// MARK: - Trader Profile Sheet

struct TraderProfileSheet: View {
    let trader: TopTrader
    @Environment(\.dismiss) private var dismiss
    @State private var copyAmount: Double = 100
    @State private var isCopying = false
    @State private var showCopyConfirm = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Profile Header
                    profileHeader
                    
                    // Stats Grid
                    statsGrid
                    
                    // Performance Chart
                    performanceChart
                    
                    // Recent Trades
                    recentTrades
                    
                    // Copy Trading Button
                    copyButton
                }
                .padding()
            }
            .navigationTitle("Trader Profile")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { dismiss() }
                }
            }
        }
        .alert("Start Copy Trading?", isPresented: $showCopyConfirm) {
            Button("Cancel", role: .cancel) {}
            Button("Confirm") {
                startCopyTrading()
            }
        } message: {
            Text("You will automatically copy \(trader.displayName)'s trades with $\(Int(copyAmount)) per position.")
        }
    }
    
    // MARK: - Profile Header
    
    private var profileHeader: some View {
        VStack(spacing: 12) {
            // Avatar
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.purple, .blue],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 80, height: 80)
                
                Text(String(trader.username.prefix(2)).uppercased())
                    .font(.title.bold())
                    .foregroundColor(.white)
            }
            
            // Name
            HStack(spacing: 6) {
                Text(trader.displayName)
                    .font(.title2.bold())
                
                if trader.isVerified {
                    Image(systemName: "checkmark.seal.fill")
                        .foregroundColor(.blue)
                }
            }
            
            // Followers
            Text("\(trader.followers.formatted()) followers")
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            // Strategies
            HStack(spacing: 8) {
                ForEach(trader.strategies, id: \.self) { strategy in
                    Text(strategy)
                        .font(.caption.bold())
                        .foregroundColor(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.purple)
                        .cornerRadius(20)
                }
            }
        }
    }
    
    // MARK: - Stats Grid
    
    private var statsGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            StatBox(title: "30D ROI", value: String(format: "%+.1f%%", trader.roi30d), color: .green)
            StatBox(title: "Win Rate", value: String(format: "%.1f%%", trader.winRate), color: .blue)
            StatBox(title: "Total Trades", value: "\(trader.totalTrades)", color: .purple)
            StatBox(title: "Max Drawdown", value: String(format: "%.1f%%", trader.maxDrawdown), color: .red)
        }
    }
    
    // MARK: - Performance Chart
    
    private var performanceChart: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Performance")
                .font(.headline)
            
            // Mock chart
            GeometryReader { geometry in
                Path { path in
                    let width = geometry.size.width
                    let height = geometry.size.height
                    let points = generateMockPoints(count: 30, width: width, height: height)
                    
                    path.move(to: points[0])
                    for point in points.dropFirst() {
                        path.addLine(to: point)
                    }
                }
                .stroke(
                    LinearGradient(
                        colors: [.purple, .blue],
                        startPoint: .leading,
                        endPoint: .trailing
                    ),
                    style: StrokeStyle(lineWidth: 2, lineCap: .round, lineJoin: .round)
                )
                
                // Gradient fill
                Path { path in
                    let width = geometry.size.width
                    let height = geometry.size.height
                    let points = generateMockPoints(count: 30, width: width, height: height)
                    
                    path.move(to: CGPoint(x: 0, y: height))
                    path.addLine(to: points[0])
                    for point in points.dropFirst() {
                        path.addLine(to: point)
                    }
                    path.addLine(to: CGPoint(x: width, y: height))
                    path.closeSubpath()
                }
                .fill(
                    LinearGradient(
                        colors: [Color.purple.opacity(0.3), Color.clear],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
            }
            .frame(height: 150)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private func generateMockPoints(count: Int, width: CGFloat, height: CGFloat) -> [CGPoint] {
        var points: [CGPoint] = []
        var cumulative: CGFloat = 0.5
        
        for i in 0..<count {
            cumulative += CGFloat.random(in: -0.05...0.08)
            cumulative = max(0.1, min(0.9, cumulative))
            
            let x = width * CGFloat(i) / CGFloat(count - 1)
            let y = height * (1 - cumulative)
            points.append(CGPoint(x: x, y: y))
        }
        
        return points
    }
    
    // MARK: - Recent Trades
    
    private var recentTrades: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Trades")
                .font(.headline)
            
            ForEach(0..<3, id: \.self) { i in
                HStack {
                    Circle()
                        .fill(i % 2 == 0 ? Color.green : Color.red)
                        .frame(width: 8, height: 8)
                    
                    Text(["BTCUSDT", "ETHUSDT", "SOLUSDT"][i])
                        .font(.subheadline.bold())
                    
                    Text(i % 2 == 0 ? "Long" : "Short")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text(["+$125.50", "-$42.30", "+$89.00"][i])
                        .font(.subheadline.bold())
                        .foregroundColor(i == 1 ? .red : .green)
                }
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(8)
            }
        }
    }
    
    // MARK: - Copy Button
    
    private var copyButton: some View {
        VStack(spacing: 16) {
            // Amount slider
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("Copy Amount")
                        .font(.subheadline)
                    Spacer()
                    Text("$\(Int(copyAmount))")
                        .font(.subheadline.bold())
                }
                
                Slider(value: $copyAmount, in: 10...1000, step: 10)
                    .tint(.purple)
            }
            
            Button(action: { showCopyConfirm = true }) {
                HStack {
                    Image(systemName: "doc.on.doc.fill")
                    Text("Start Copy Trading")
                        .font(.headline)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(
                    LinearGradient(
                        colors: [.purple, .blue],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .cornerRadius(12)
            }
        }
    }
    
    private func startCopyTrading() {
        isCopying = true
        HapticManager.shared.perform(.success)
        
        // API call to start copy trading
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            isCopying = false
        }
    }
}

struct SocialStatBox: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3.bold())
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

// MARK: - Preview

#Preview("Social Trading") {
    NavigationStack {
        SocialTradingView()
    }
}

#Preview("Trader Profile") {
    TraderProfileSheet(trader: TopTrader(
        id: "1", username: "CryptoWhale", avatar: nil, rank: 1,
        roi30d: 127.5, winRate: 78.4, totalTrades: 342,
        followers: 12500, maxDrawdown: -8.2,
        strategies: ["OI", "Scalper"], isVerified: true
    ))
}
