//
//  OrderbookView.swift
//  EnlikoTrading
//
//  Real-time orderbook display like Binance/Bybit
//  Features: Depth chart, Price ladder, Trade history
//

import SwiftUI

// MARK: - Orderbook Models
struct OrderbookLevel: Identifiable {
    let id = UUID()
    let price: Double
    let size: Double
    let total: Double
    let percentage: Double
}

struct OrderbookData {
    var bids: [OrderbookLevel] = []
    var asks: [OrderbookLevel] = []
    var lastPrice: Double = 0
    var priceChange: Double = 0
    var priceChangePercent: Double = 0
}

// MARK: - OrderbookView
struct OrderbookView: View {
    let symbol: String
    @State private var orderbook = OrderbookData()
    @State private var displayMode: DisplayMode = .orderbook
    @State private var depthLevels: Int = 10
    @State private var isLoading = true
    
    @Environment(\.dismiss) var dismiss
    
    enum DisplayMode: String, CaseIterable {
        case orderbook = "Orderbook"
        case depthChart = "Depth"
        case trades = "Trades"
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Mode Picker
                    Picker("", selection: $displayMode) {
                        ForEach(DisplayMode.allCases, id: \.self) { mode in
                            Text(mode.rawValue).tag(mode)
                        }
                    }
                    .pickerStyle(.segmented)
                    .padding()
                    
                    // Content
                    switch displayMode {
                    case .orderbook:
                        orderbookContent
                    case .depthChart:
                        depthChartContent
                    case .trades:
                        recentTradesContent
                    }
                }
            }
            .navigationTitle(symbol)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button { dismiss() } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
                
                ToolbarItem(placement: .principal) {
                    VStack(spacing: 2) {
                        Text(symbol)
                            .font(.headline)
                        
                        HStack(spacing: 4) {
                            Text("$\(orderbook.lastPrice, specifier: "%.2f")")
                                .font(.caption.bold())
                            
                            Text("\(orderbook.priceChangePercent >= 0 ? "+" : "")\(orderbook.priceChangePercent, specifier: "%.2f")%")
                                .font(.caption)
                                .foregroundColor(orderbook.priceChangePercent >= 0 ? .green : .red)
                        }
                    }
                }
            }
            .task {
                await fetchOrderbook()
            }
        }
    }
    
    // MARK: - Orderbook Content
    private var orderbookContent: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Price (USDT)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Spacer()
                Text("Size")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Spacer()
                Text("Total")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
            .background(Color.enlikoSurface)
            
            if isLoading {
                Spacer()
                ProgressView()
                Spacer()
            } else {
                // Asks (Sells) - reversed to show highest at top
                ScrollView {
                    LazyVStack(spacing: 1) {
                        ForEach(orderbook.asks.reversed()) { ask in
                            OrderbookRow(level: ask, side: .sell)
                        }
                    }
                }
                .frame(maxHeight: .infinity)
                
                // Spread & Last Price
                spreadSection
                
                // Bids (Buys)
                ScrollView {
                    LazyVStack(spacing: 1) {
                        ForEach(orderbook.bids) { bid in
                            OrderbookRow(level: bid, side: .buy)
                        }
                    }
                }
                .frame(maxHeight: .infinity)
            }
        }
    }
    
    private var spreadSection: some View {
        HStack {
            // Last Price
            VStack(alignment: .leading, spacing: 2) {
                Text("$\(orderbook.lastPrice, specifier: "%.2f")")
                    .font(.title2.bold())
                    .foregroundColor(orderbook.priceChangePercent >= 0 ? .green : .red)
                
                Text("\(orderbook.priceChangePercent >= 0 ? "+" : "")\(orderbook.priceChange, specifier: "%.2f")")
                    .font(.caption)
                    .foregroundColor(orderbook.priceChangePercent >= 0 ? .green : .red)
            }
            
            Spacer()
            
            // Spread
            VStack(alignment: .trailing, spacing: 2) {
                Text("Spread")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                if let bestAsk = orderbook.asks.first?.price,
                   let bestBid = orderbook.bids.first?.price {
                    let spread = bestAsk - bestBid
                    let spreadPercent = (spread / bestBid) * 100
                    Text("\(spread, specifier: "%.2f") (\(spreadPercent, specifier: "%.3f")%)")
                        .font(.caption.bold())
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Depth Chart
    private var depthChartContent: some View {
        VStack {
            if isLoading {
                Spacer()
                ProgressView()
                Spacer()
            } else {
                DepthChartView(bids: orderbook.bids, asks: orderbook.asks, lastPrice: orderbook.lastPrice)
            }
        }
    }
    
    // MARK: - Recent Trades
    private var recentTradesContent: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Price")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Spacer()
                Text("Size")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Spacer()
                Text("Time")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color.enlikoSurface)
            
            // Mock trades for now
            ScrollView {
                LazyVStack(spacing: 2) {
                    ForEach(0..<50, id: \.self) { i in
                        let isBuy = i % 3 != 0
                        let price = orderbook.lastPrice + Double.random(in: -50...50)
                        let size = Double.random(in: 0.01...2.5)
                        
                        HStack {
                            Text("$\(price, specifier: "%.2f")")
                                .font(.system(.caption, design: .monospaced))
                                .foregroundColor(isBuy ? .green : .red)
                            
                            Spacer()
                            
                            Text("\(size, specifier: "%.4f")")
                                .font(.system(.caption, design: .monospaced))
                            
                            Spacer()
                            
                            Text(formatTime(Date().addingTimeInterval(-Double(i * 2))))
                                .font(.system(.caption, design: .monospaced))
                                .foregroundColor(.secondary)
                        }
                        .padding(.horizontal)
                        .padding(.vertical, 6)
                    }
                }
            }
        }
    }
    
    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: date)
    }
    
    // MARK: - Fetch Data
    private func fetchOrderbook() async {
        // Simulate loading
        try? await Task.sleep(nanoseconds: 500_000_000)
        
        // Generate mock orderbook data
        let basePrice = symbol.contains("BTC") ? 98500.0 : 3200.0
        
        var bids: [OrderbookLevel] = []
        var asks: [OrderbookLevel] = []
        var totalBid = 0.0
        var totalAsk = 0.0
        
        for i in 0..<20 {
            let bidPrice = basePrice - Double(i) * 5
            let askPrice = basePrice + Double(i + 1) * 5
            
            let bidSize = Double.random(in: 0.5...10)
            let askSize = Double.random(in: 0.5...10)
            
            totalBid += bidSize
            totalAsk += askSize
            
            bids.append(OrderbookLevel(price: bidPrice, size: bidSize, total: totalBid, percentage: 0))
            asks.append(OrderbookLevel(price: askPrice, size: askSize, total: totalAsk, percentage: 0))
        }
        
        // Calculate percentages
        let maxTotal = max(totalBid, totalAsk)
        bids = bids.map { OrderbookLevel(price: $0.price, size: $0.size, total: $0.total, percentage: $0.total / maxTotal) }
        asks = asks.map { OrderbookLevel(price: $0.price, size: $0.size, total: $0.total, percentage: $0.total / maxTotal) }
        
        await MainActor.run {
            orderbook = OrderbookData(
                bids: bids,
                asks: asks,
                lastPrice: basePrice,
                priceChange: 150.5,
                priceChangePercent: 0.15
            )
            isLoading = false
        }
    }
}

// MARK: - Orderbook Row
struct OrderbookRow: View {
    let level: OrderbookLevel
    let side: OrderSide
    
    var body: some View {
        ZStack(alignment: side == .buy ? .leading : .trailing) {
            // Background depth bar
            GeometryReader { geo in
                Rectangle()
                    .fill(side == .buy ? Color.green.opacity(0.15) : Color.red.opacity(0.15))
                    .frame(width: geo.size.width * level.percentage)
            }
            
            HStack {
                Text("$\(level.price, specifier: "%.2f")")
                    .font(.system(.caption, design: .monospaced))
                    .foregroundColor(side == .buy ? .green : .red)
                
                Spacer()
                
                Text("\(level.size, specifier: "%.4f")")
                    .font(.system(.caption, design: .monospaced))
                
                Spacer()
                
                Text("\(level.total, specifier: "%.4f")")
                    .font(.system(.caption, design: .monospaced))
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal)
            .padding(.vertical, 6)
        }
    }
}

// MARK: - Depth Chart View
struct DepthChartView: View {
    let bids: [OrderbookLevel]
    let asks: [OrderbookLevel]
    let lastPrice: Double
    
    var body: some View {
        GeometryReader { geo in
            ZStack {
                // Grid lines
                ForEach(0..<5, id: \.self) { i in
                    let y = geo.size.height * CGFloat(i) / 4
                    Path { path in
                        path.move(to: CGPoint(x: 0, y: y))
                        path.addLine(to: CGPoint(x: geo.size.width, y: y))
                    }
                    .stroke(Color.secondary.opacity(0.2), lineWidth: 0.5)
                }
                
                // Bid area
                Path { path in
                    let width = geo.size.width / 2
                    let height = geo.size.height
                    
                    path.move(to: CGPoint(x: width, y: height))
                    
                    for (index, bid) in bids.enumerated() {
                        let x = width - (width * CGFloat(index) / CGFloat(bids.count))
                        let y = height - (height * CGFloat(bid.percentage))
                        path.addLine(to: CGPoint(x: x, y: y))
                    }
                    
                    path.addLine(to: CGPoint(x: 0, y: height))
                    path.closeSubpath()
                }
                .fill(
                    LinearGradient(
                        colors: [Color.green.opacity(0.4), Color.green.opacity(0.1)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                
                // Ask area
                Path { path in
                    let width = geo.size.width / 2
                    let height = geo.size.height
                    
                    path.move(to: CGPoint(x: width, y: height))
                    
                    for (index, ask) in asks.enumerated() {
                        let x = width + (width * CGFloat(index) / CGFloat(asks.count))
                        let y = height - (height * CGFloat(ask.percentage))
                        path.addLine(to: CGPoint(x: x, y: y))
                    }
                    
                    path.addLine(to: CGPoint(x: geo.size.width, y: height))
                    path.closeSubpath()
                }
                .fill(
                    LinearGradient(
                        colors: [Color.red.opacity(0.4), Color.red.opacity(0.1)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                
                // Center line
                Path { path in
                    path.move(to: CGPoint(x: geo.size.width / 2, y: 0))
                    path.addLine(to: CGPoint(x: geo.size.width / 2, y: geo.size.height))
                }
                .stroke(Color.white.opacity(0.5), style: StrokeStyle(lineWidth: 1, dash: [5, 5]))
                
                // Price label
                VStack {
                    Spacer()
                    Text("$\(lastPrice, specifier: "%.2f")")
                        .font(.caption.bold())
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.enlikoSurface)
                        .cornerRadius(4)
                    
                    Spacer()
                        .frame(height: 30)
                }
            }
        }
        .padding()
    }
}

#Preview {
    OrderbookView(symbol: "BTCUSDT")
        .preferredColorScheme(.dark)
}
