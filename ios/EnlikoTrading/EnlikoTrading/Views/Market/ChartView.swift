//
//  ChartView.swift
//  EnlikoTrading
//
//  Professional trading chart like Binance/Bybit
//  Features: Candlestick chart, Timeframes, Indicators, Drawing tools
//

import SwiftUI
import Charts

// MARK: - Chart Models
struct CandleData: Identifiable {
    let id = UUID()
    let timestamp: Date
    let open: Double
    let high: Double
    let low: Double
    let close: Double
    let volume: Double
    
    var isGreen: Bool { close >= open }
    var bodyTop: Double { max(open, close) }
    var bodyBottom: Double { min(open, close) }
}

struct ChartIndicator: Identifiable {
    let id = UUID()
    let name: String
    var enabled: Bool
    let color: Color
}

// MARK: - ChartView
struct ChartView: View {
    let symbol: String
    
    @State private var candles: [CandleData] = []
    @State private var selectedTimeframe: Timeframe = .h1
    @State private var chartType: ChartType = .candle
    @State private var isLoading = true
    @State private var showIndicators = false
    @State private var selectedCandle: CandleData?
    
    @State private var indicators: [ChartIndicator] = [
        ChartIndicator(name: "MA(7)", enabled: true, color: .yellow),
        ChartIndicator(name: "MA(25)", enabled: true, color: .blue),
        ChartIndicator(name: "MA(99)", enabled: false, color: .purple),
        ChartIndicator(name: "EMA(9)", enabled: false, color: .orange),
        ChartIndicator(name: "BB(20)", enabled: false, color: .cyan),
        ChartIndicator(name: "RSI(14)", enabled: false, color: .pink),
        ChartIndicator(name: "MACD", enabled: false, color: .green),
    ]
    
    @Environment(\.dismiss) var dismiss
    
    enum Timeframe: String, CaseIterable {
        case m1 = "1m"
        case m5 = "5m"
        case m15 = "15m"
        case m30 = "30m"
        case h1 = "1H"
        case h4 = "4H"
        case d1 = "1D"
        case w1 = "1W"
    }
    
    enum ChartType: String, CaseIterable {
        case candle = "Candle"
        case line = "Line"
        case area = "Area"
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Chart Controls
                    chartControls
                    
                    // Price Info
                    priceInfoBar
                    
                    // Chart Area
                    if isLoading {
                        Spacer()
                        ProgressView()
                        Spacer()
                    } else {
                        // Main Chart
                        mainChart
                            .padding(.horizontal, 8)
                        
                        // Volume Chart
                        volumeChart
                            .frame(height: 80)
                            .padding(.horizontal, 8)
                        
                        // Selected Candle Info
                        if let candle = selectedCandle {
                            candleInfoBar(candle)
                        }
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
                
                ToolbarItem(placement: .primaryAction) {
                    Menu {
                        Button {
                            showIndicators = true
                        } label: {
                            Label("Indicators", systemImage: "waveform.path.ecg")
                        }
                        
                        Menu("Chart Type") {
                            ForEach(ChartType.allCases, id: \.self) { type in
                                Button {
                                    chartType = type
                                } label: {
                                    HStack {
                                        Text(type.rawValue)
                                        if chartType == type {
                                            Image(systemName: "checkmark")
                                        }
                                    }
                                }
                            }
                        }
                    } label: {
                        Image(systemName: "slider.horizontal.3")
                            .foregroundColor(.enlikoPrimary)
                    }
                }
            }
            .sheet(isPresented: $showIndicators) {
                IndicatorSheet(indicators: $indicators)
            }
            .task {
                await loadChartData()
            }
            .onChange(of: selectedTimeframe) { _ in
                Task { await loadChartData() }
            }
        }
    }
    
    // MARK: - Chart Controls
    private var chartControls: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(Timeframe.allCases, id: \.self) { tf in
                    Button {
                        selectedTimeframe = tf
                    } label: {
                        Text(tf.rawValue)
                            .font(.caption.bold())
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(selectedTimeframe == tf ? Color.enlikoPrimary : Color.enlikoSurface)
                            .foregroundColor(selectedTimeframe == tf ? .white : .secondary)
                            .cornerRadius(8)
                    }
                }
            }
            .padding(.horizontal)
        }
        .padding(.vertical, 8)
        .background(Color.enlikoSurface.opacity(0.5))
    }
    
    // MARK: - Price Info Bar
    private var priceInfoBar: some View {
        HStack {
            if let lastCandle = candles.last {
                VStack(alignment: .leading, spacing: 2) {
                    Text("$\(lastCandle.close, specifier: "%.2f")")
                        .font(.title2.bold())
                        .foregroundColor(lastCandle.isGreen ? .green : .red)
                    
                    let change = lastCandle.close - (candles.first?.open ?? lastCandle.open)
                    let changePercent = (change / (candles.first?.open ?? lastCandle.open)) * 100
                    Text("\(change >= 0 ? "+" : "")\(change, specifier: "%.2f") (\(changePercent, specifier: "%.2f")%)")
                        .font(.caption)
                        .foregroundColor(change >= 0 ? .green : .red)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 2) {
                    HStack(spacing: 12) {
                        VStack(alignment: .trailing) {
                            Text("H")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("$\(candles.map(\.high).max() ?? 0, specifier: "%.2f")")
                                .font(.caption.bold())
                                .foregroundColor(.green)
                        }
                        
                        VStack(alignment: .trailing) {
                            Text("L")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("$\(candles.map(\.low).min() ?? 0, specifier: "%.2f")")
                                .font(.caption.bold())
                                .foregroundColor(.red)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Main Chart
    private var mainChart: some View {
        Chart {
            switch chartType {
            case .candle:
                ForEach(candles) { candle in
                    // Wick
                    RectangleMark(
                        x: .value("Time", candle.timestamp),
                        yStart: .value("Low", candle.low),
                        yEnd: .value("High", candle.high),
                        width: 1
                    )
                    .foregroundStyle(candle.isGreen ? Color.green : Color.red)
                    
                    // Body
                    RectangleMark(
                        x: .value("Time", candle.timestamp),
                        yStart: .value("Open", candle.bodyBottom),
                        yEnd: .value("Close", candle.bodyTop),
                        width: 6
                    )
                    .foregroundStyle(candle.isGreen ? Color.green : Color.red)
                }
                
            case .line:
                ForEach(candles) { candle in
                    LineMark(
                        x: .value("Time", candle.timestamp),
                        y: .value("Price", candle.close)
                    )
                    .foregroundStyle(Color.enlikoPrimary)
                    .lineStyle(StrokeStyle(lineWidth: 2))
                }
                
            case .area:
                ForEach(candles) { candle in
                    AreaMark(
                        x: .value("Time", candle.timestamp),
                        y: .value("Price", candle.close)
                    )
                    .foregroundStyle(
                        LinearGradient(
                            colors: [Color.enlikoPrimary.opacity(0.5), Color.enlikoPrimary.opacity(0.1)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    
                    LineMark(
                        x: .value("Time", candle.timestamp),
                        y: .value("Price", candle.close)
                    )
                    .foregroundStyle(Color.enlikoPrimary)
                    .lineStyle(StrokeStyle(lineWidth: 2))
                }
            }
            
            // MA Lines
            if indicators.first(where: { $0.name == "MA(7)" })?.enabled == true {
                ForEach(calculateMA(period: 7)) { point in
                    LineMark(
                        x: .value("Time", point.timestamp),
                        y: .value("MA7", point.close)
                    )
                    .foregroundStyle(Color.yellow)
                    .lineStyle(StrokeStyle(lineWidth: 1))
                }
            }
            
            if indicators.first(where: { $0.name == "MA(25)" })?.enabled == true {
                ForEach(calculateMA(period: 25)) { point in
                    LineMark(
                        x: .value("Time", point.timestamp),
                        y: .value("MA25", point.close)
                    )
                    .foregroundStyle(Color.blue)
                    .lineStyle(StrokeStyle(lineWidth: 1))
                }
            }
        }
        .chartXAxis {
            AxisMarks(values: .automatic(desiredCount: 5)) { value in
                AxisValueLabel {
                    if let date = value.as(Date.self) {
                        Text(formatDate(date))
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .chartYAxis {
            AxisMarks(position: .trailing) { value in
                AxisGridLine()
                    .foregroundStyle(Color.secondary.opacity(0.2))
                AxisValueLabel {
                    if let price = value.as(Double.self) {
                        Text("$\(price, specifier: "%.0f")")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .chartOverlay { proxy in
            GeometryReader { geo in
                Rectangle()
                    .fill(Color.clear)
                    .contentShape(Rectangle())
                    .gesture(
                        DragGesture(minimumDistance: 0)
                            .onChanged { value in
                                guard let plotFrame = proxy.plotFrame else { return }
                                let x = value.location.x - geo[plotFrame].origin.x
                                if let date: Date = proxy.value(atX: x) {
                                    selectedCandle = candles.min(by: { abs($0.timestamp.timeIntervalSince(date)) < abs($1.timestamp.timeIntervalSince(date)) })
                                }
                            }
                            .onEnded { _ in
                                selectedCandle = nil
                            }
                    )
            }
        }
        .frame(height: 300)
    }
    
    // MARK: - Volume Chart
    private var volumeChart: some View {
        Chart {
            ForEach(candles) { candle in
                BarMark(
                    x: .value("Time", candle.timestamp),
                    y: .value("Volume", candle.volume)
                )
                .foregroundStyle(candle.isGreen ? Color.green.opacity(0.5) : Color.red.opacity(0.5))
            }
        }
        .chartXAxis(.hidden)
        .chartYAxis {
            AxisMarks(position: .trailing) { value in
                AxisValueLabel {
                    if let vol = value.as(Double.self) {
                        Text(formatVolume(vol))
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
    }
    
    // MARK: - Candle Info Bar
    private func candleInfoBar(_ candle: CandleData) -> some View {
        HStack(spacing: 16) {
            VStack(alignment: .leading) {
                Text("O: $\(candle.open, specifier: "%.2f")")
                    .font(.caption)
            }
            VStack(alignment: .leading) {
                Text("H: $\(candle.high, specifier: "%.2f")")
                    .font(.caption)
                    .foregroundColor(.green)
            }
            VStack(alignment: .leading) {
                Text("L: $\(candle.low, specifier: "%.2f")")
                    .font(.caption)
                    .foregroundColor(.red)
            }
            VStack(alignment: .leading) {
                Text("C: $\(candle.close, specifier: "%.2f")")
                    .font(.caption)
            }
            Spacer()
            Text(formatDateTime(candle.timestamp))
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Helper Functions
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = selectedTimeframe == .d1 || selectedTimeframe == .w1 ? "MM/dd" : "HH:mm"
        return formatter.string(from: date)
    }
    
    private func formatDateTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MM/dd HH:mm"
        return formatter.string(from: date)
    }
    
    private func formatVolume(_ vol: Double) -> String {
        if vol >= 1_000_000 {
            return String(format: "%.1fM", vol / 1_000_000)
        } else if vol >= 1_000 {
            return String(format: "%.1fK", vol / 1_000)
        }
        return String(format: "%.0f", vol)
    }
    
    private func calculateMA(period: Int) -> [CandleData] {
        guard candles.count >= period else { return [] }
        
        var result: [CandleData] = []
        for i in (period - 1)..<candles.count {
            let sum = candles[(i - period + 1)...i].reduce(0) { $0 + $1.close }
            let ma = sum / Double(period)
            result.append(CandleData(
                timestamp: candles[i].timestamp,
                open: ma, high: ma, low: ma, close: ma, volume: 0
            ))
        }
        return result
    }
    
    // MARK: - Load Data
    private func loadChartData() async {
        isLoading = true
        
        // Simulate API call
        try? await Task.sleep(nanoseconds: 500_000_000)
        
        // Generate mock candle data
        let basePrice = symbol.contains("BTC") ? 98500.0 : 3200.0
        var mockCandles: [CandleData] = []
        var currentPrice = basePrice
        
        let candleCount = 100
        let now = Date()
        
        let interval: TimeInterval
        switch selectedTimeframe {
        case .m1: interval = 60
        case .m5: interval = 5 * 60
        case .m15: interval = 15 * 60
        case .m30: interval = 30 * 60
        case .h1: interval = 60 * 60
        case .h4: interval = 4 * 60 * 60
        case .d1: interval = 24 * 60 * 60
        case .w1: interval = 7 * 24 * 60 * 60
        }
        
        for i in 0..<candleCount {
            let timestamp = now.addingTimeInterval(-Double(candleCount - i) * interval)
            
            let change = Double.random(in: -0.02...0.02)
            let open = currentPrice
            let close = currentPrice * (1 + change)
            let high = max(open, close) * (1 + Double.random(in: 0...0.01))
            let low = min(open, close) * (1 - Double.random(in: 0...0.01))
            let volume = Double.random(in: 100_000...5_000_000)
            
            mockCandles.append(CandleData(
                timestamp: timestamp,
                open: open,
                high: high,
                low: low,
                close: close,
                volume: volume
            ))
            
            currentPrice = close
        }
        
        await MainActor.run {
            candles = mockCandles
            isLoading = false
        }
    }
}

// MARK: - Indicator Sheet
struct IndicatorSheet: View {
    @Binding var indicators: [ChartIndicator]
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            List {
                Section("Moving Averages") {
                    ForEach($indicators.filter { $0.wrappedValue.name.contains("MA") || $0.wrappedValue.name.contains("EMA") }) { $indicator in
                        Toggle(isOn: $indicator.enabled) {
                            HStack {
                                Circle()
                                    .fill(indicator.color)
                                    .frame(width: 12, height: 12)
                                Text(indicator.name)
                            }
                        }
                    }
                }
                
                Section("Oscillators") {
                    ForEach($indicators.filter { $0.wrappedValue.name.contains("RSI") || $0.wrappedValue.name.contains("MACD") }) { $indicator in
                        Toggle(isOn: $indicator.enabled) {
                            HStack {
                                Circle()
                                    .fill(indicator.color)
                                    .frame(width: 12, height: 12)
                                Text(indicator.name)
                            }
                        }
                    }
                }
                
                Section("Volatility") {
                    ForEach($indicators.filter { $0.wrappedValue.name.contains("BB") }) { $indicator in
                        Toggle(isOn: $indicator.enabled) {
                            HStack {
                                Circle()
                                    .fill(indicator.color)
                                    .frame(width: 12, height: 12)
                                Text(indicator.name)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Indicators")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}

#Preview {
    ChartView(symbol: "BTCUSDT")
        .preferredColorScheme(.dark)
}
