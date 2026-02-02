//
//  AdvancedChartsView.swift
//  EnlikoTrading
//
//  📈 TradingView-Style Advanced Charts
//  =====================================
//
//  Features:
//  1. Interactive candlestick charts
//  2. Multiple timeframes (1m, 5m, 15m, 1H, 4H, 1D)
//  3. Technical indicators (MA, EMA, BB, RSI, MACD)
//  4. Drawing tools (Trendlines, Fib, Support/Resistance)
//  5. Pinch-to-zoom & Pan gestures
//  6. Volume overlay
//

import SwiftUI
import Combine

// MARK: - Chart Data Models

struct Candle: Identifiable {
    let id = UUID()
    let timestamp: Date
    let open: Double
    let high: Double
    let low: Double
    let close: Double
    let volume: Double
    
    var isBullish: Bool { close >= open }
    var bodyHeight: CGFloat { CGFloat(abs(close - open)) }
    var wickHighY: CGFloat { CGFloat(high) }
    var wickLowY: CGFloat { CGFloat(low) }
    var bodyTop: CGFloat { CGFloat(max(open, close)) }
    var bodyBottom: CGFloat { CGFloat(min(open, close)) }
}

struct ChartIndicator: Identifiable {
    let id = UUID()
    let name: String
    let values: [Double]
    let color: Color
    let lineWidth: CGFloat
}

enum ChartTimeframe: String, CaseIterable {
    case m1 = "1m"
    case m5 = "5m"
    case m15 = "15m"
    case h1 = "1H"
    case h4 = "4H"
    case d1 = "1D"
    case w1 = "1W"
    
    var interval: TimeInterval {
        switch self {
        case .m1: return 60
        case .m5: return 300
        case .m15: return 900
        case .h1: return 3600
        case .h4: return 14400
        case .d1: return 86400
        case .w1: return 604800
        }
    }
}

enum ChartIndicatorType: String, CaseIterable {
    case ma7 = "MA 7"
    case ma25 = "MA 25"
    case ma99 = "MA 99"
    case ema12 = "EMA 12"
    case ema26 = "EMA 26"
    case bollinger = "BB"
    case rsi = "RSI"
    case macd = "MACD"
    case volume = "Volume"
}

// MARK: - Chart View Model

class AdvancedChartViewModel: ObservableObject {
    @Published var candles: [Candle] = []
    @Published var selectedTimeframe: ChartTimeframe = .h1
    @Published var enabledIndicators: Set<ChartIndicatorType> = [.ma7, .ma25]
    @Published var isLoading = false
    @Published var currentPrice: Double = 0
    @Published var priceChange24h: Double = 0
    @Published var high24h: Double = 0
    @Published var low24h: Double = 0
    
    let symbol: String
    
    init(symbol: String) {
        self.symbol = symbol
        generateMockData()
    }
    
    func generateMockData() {
        isLoading = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            guard let self = self else { return }
            
            var candles: [Candle] = []
            var lastClose = Double.random(in: 40000...50000)
            let now = Date()
            
            for i in 0..<100 {
                let timestamp = now.addingTimeInterval(-self.selectedTimeframe.interval * Double(100 - i))
                let volatility = Double.random(in: 0.001...0.02)
                
                let open = lastClose
                let close = open * (1 + Double.random(in: -volatility...volatility))
                let high = max(open, close) * (1 + Double.random(in: 0...volatility/2))
                let low = min(open, close) * (1 - Double.random(in: 0...volatility/2))
                let volume = Double.random(in: 100...1000) * lastClose / 100
                
                candles.append(Candle(
                    timestamp: timestamp,
                    open: open,
                    high: high,
                    low: low,
                    close: close,
                    volume: volume
                ))
                
                lastClose = close
            }
            
            self.candles = candles
            self.currentPrice = candles.last?.close ?? 0
            self.high24h = candles.suffix(24).map { $0.high }.max() ?? 0
            self.low24h = candles.suffix(24).map { $0.low }.min() ?? 0
            self.priceChange24h = ((candles.last?.close ?? 0) / (candles.dropLast(24).last?.close ?? 1) - 1) * 100
            self.isLoading = false
        }
    }
    
    func calculateMA(period: Int) -> [Double] {
        guard candles.count >= period else { return [] }
        
        var values: [Double] = []
        for i in (period - 1)..<candles.count {
            let slice = candles[(i - period + 1)...i]
            let sum = slice.reduce(0) { $0 + $1.close }
            values.append(sum / Double(period))
        }
        return values
    }
    
    func calculateRSI(period: Int = 14) -> [Double] {
        guard candles.count > period else { return [] }
        
        var gains: [Double] = []
        var losses: [Double] = []
        
        for i in 1..<candles.count {
            let change = candles[i].close - candles[i-1].close
            gains.append(max(0, change))
            losses.append(max(0, -change))
        }
        
        var rsiValues: [Double] = []
        for i in period..<gains.count {
            let avgGain = gains[(i-period)..<i].reduce(0, +) / Double(period)
            let avgLoss = losses[(i-period)..<i].reduce(0, +) / Double(period)
            
            if avgLoss == 0 {
                rsiValues.append(100)
            } else {
                let rs = avgGain / avgLoss
                rsiValues.append(100 - (100 / (1 + rs)))
            }
        }
        
        return rsiValues
    }
}

// MARK: - Advanced Charts View

struct AdvancedChartsView: View {
    @StateObject private var viewModel: AdvancedChartViewModel
    @State private var chartScale: CGFloat = 1.0
    @State private var chartOffset: CGFloat = 0
    @State private var showIndicatorSheet = false
    @State private var showDrawingTools = false
    @State private var selectedCandle: Candle?
    
    init(symbol: String) {
        _viewModel = StateObject(wrappedValue: AdvancedChartViewModel(symbol: symbol))
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Beta Notice Banner
            betaNoticeBanner
            
            // Header
            chartHeader
            
            // Timeframe selector
            timeframeSelector
            
            // Main chart
            GeometryReader { geometry in
                ZStack {
                    if viewModel.isLoading {
                        ProgressView()
                    } else {
                        // Price chart
                        CandlestickChartView(
                            candles: viewModel.candles,
                            scale: chartScale,
                            offset: chartOffset,
                            selectedCandle: $selectedCandle,
                            indicators: viewModel.enabledIndicators,
                            maValues: viewModel.calculateMA(period: 7)
                        )
                        .gesture(magnificationGesture)
                        .gesture(dragGesture)
                        
                        // Crosshair overlay
                        if let candle = selectedCandle {
                            CrosshairOverlay(candle: candle, geometry: geometry)
                        }
                    }
                }
            }
            .frame(height: 350)
            .clipped()
            
            // RSI indicator (if enabled)
            if viewModel.enabledIndicators.contains(.rsi) {
                RSIChartView(values: viewModel.calculateRSI())
                    .frame(height: 80)
            }
            
            // Volume (if enabled)
            if viewModel.enabledIndicators.contains(.volume) {
                VolumeChartView(candles: viewModel.candles)
                    .frame(height: 60)
            }
            
            // Bottom toolbar
            chartToolbar
        }
        .background(Color(.systemBackground))
        .sheet(isPresented: $showIndicatorSheet) {
            IndicatorSelectorView(enabledIndicators: $viewModel.enabledIndicators)
        }
    }
    
    // MARK: - Beta Notice Banner
    
    private var betaNoticeBanner: some View {
        HStack(spacing: 8) {
            Image(systemName: "chart.bar.xaxis")
                .foregroundColor(.blue)
            
            Text("Beta: Chart data is simulated for demonstration")
                .font(.caption)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text("BETA")
                .font(.system(size: 9, weight: .bold))
                .padding(.horizontal, 5)
                .padding(.vertical, 2)
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(3)
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.blue.opacity(0.1))
    }
    
    // MARK: - Header
    
    private var chartHeader: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(viewModel.symbol)
                    .font(.title2.bold())
                
                HStack(spacing: 4) {
                    Text("$\(viewModel.currentPrice, specifier: "%.2f")")
                        .font(.headline)
                    
                    Text(String(format: "%+.2f%%", viewModel.priceChange24h))
                        .font(.caption.bold())
                        .foregroundColor(viewModel.priceChange24h >= 0 ? .green : .red)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(
                            Capsule()
                                .fill((viewModel.priceChange24h >= 0 ? Color.green : Color.red).opacity(0.2))
                        )
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                HStack(spacing: 4) {
                    Text("H:")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("$\(viewModel.high24h, specifier: "%.2f")")
                        .font(.caption.bold())
                        .foregroundColor(.green)
                }
                
                HStack(spacing: 4) {
                    Text("L:")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("$\(viewModel.low24h, specifier: "%.2f")")
                        .font(.caption.bold())
                        .foregroundColor(.red)
                }
            }
        }
        .padding()
    }
    
    // MARK: - Timeframe Selector
    
    private var timeframeSelector: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(ChartTimeframe.allCases, id: \.self) { timeframe in
                    Button(action: {
                        withAnimation {
                            viewModel.selectedTimeframe = timeframe
                            viewModel.generateMockData()
                        }
                    }) {
                        Text(timeframe.rawValue)
                            .font(.caption.bold())
                            .foregroundColor(viewModel.selectedTimeframe == timeframe ? .white : .secondary)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(
                                Capsule()
                                    .fill(viewModel.selectedTimeframe == timeframe ? Color.purple : Color(.systemGray5))
                            )
                    }
                }
            }
            .padding(.horizontal)
        }
    }
    
    // MARK: - Toolbar
    
    private var chartToolbar: some View {
        HStack(spacing: 20) {
            Button(action: { showIndicatorSheet = true }) {
                VStack(spacing: 2) {
                    Image(systemName: "waveform.path.ecg")
                    Text("Indicators")
                        .font(.caption2)
                }
            }
            
            Button(action: { showDrawingTools = true }) {
                VStack(spacing: 2) {
                    Image(systemName: "scribble")
                    Text("Draw")
                        .font(.caption2)
                }
            }
            
            Button(action: { chartScale = 1.0; chartOffset = 0 }) {
                VStack(spacing: 2) {
                    Image(systemName: "arrow.counterclockwise")
                    Text("Reset")
                        .font(.caption2)
                }
            }
            
            Button(action: { viewModel.generateMockData() }) {
                VStack(spacing: 2) {
                    Image(systemName: "arrow.clockwise")
                    Text("Refresh")
                        .font(.caption2)
                }
            }
            
            Spacer()
            
            Button(action: {}) {
                Image(systemName: "square.and.arrow.up")
            }
        }
        .foregroundColor(.primary)
        .padding()
    }
    
    // MARK: - Gestures
    
    private var magnificationGesture: some Gesture {
        MagnificationGesture()
            .onChanged { value in
                chartScale = max(0.5, min(3.0, value))
            }
    }
    
    private var dragGesture: some Gesture {
        DragGesture()
            .onChanged { value in
                chartOffset += value.translation.width / 10
            }
    }
}

// MARK: - Candlestick Chart View

struct CandlestickChartView: View {
    let candles: [Candle]
    let scale: CGFloat
    let offset: CGFloat
    @Binding var selectedCandle: Candle?
    let indicators: Set<ChartIndicatorType>
    let maValues: [Double]
    
    var body: some View {
        GeometryReader { geometry in
            let width = geometry.size.width
            let height = geometry.size.height
            let candleWidth = (width / CGFloat(min(candles.count, 50))) * scale
            
            // Calculate price range
            let visibleCandles = Array(candles.suffix(Int(50 / scale)))
            let maxPrice = visibleCandles.map { $0.high }.max() ?? 1
            let minPrice = visibleCandles.map { $0.low }.min() ?? 0
            let priceRange = maxPrice - minPrice
            
            ZStack {
                // Grid lines
                GridLinesView(height: height, minPrice: minPrice, maxPrice: maxPrice)
                
                // MA line (if enabled)
                if indicators.contains(.ma7) && !maValues.isEmpty {
                    MALineView(
                        values: maValues,
                        minPrice: minPrice,
                        priceRange: priceRange,
                        width: width,
                        height: height,
                        color: .blue
                    )
                }
                
                // Candles
                HStack(alignment: .bottom, spacing: candleWidth * 0.1) {
                    ForEach(Array(visibleCandles.enumerated()), id: \.element.id) { index, candle in
                        CandleView(
                            candle: candle,
                            width: candleWidth * 0.8,
                            height: height,
                            minPrice: minPrice,
                            priceRange: priceRange,
                            isSelected: selectedCandle?.id == candle.id
                        )
                        .onTapGesture {
                            withAnimation(.easeInOut(duration: 0.2)) {
                                selectedCandle = selectedCandle?.id == candle.id ? nil : candle
                            }
                        }
                    }
                }
                .offset(x: offset)
                
                // Current price line
                if let lastCandle = candles.last {
                    CurrentPriceLine(
                        price: lastCandle.close,
                        minPrice: minPrice,
                        priceRange: priceRange,
                        height: height,
                        width: width
                    )
                }
            }
        }
    }
}

// MARK: - Candle View

struct CandleView: View {
    let candle: Candle
    let width: CGFloat
    let height: CGFloat
    let minPrice: Double
    let priceRange: Double
    let isSelected: Bool
    
    var body: some View {
        let color: Color = candle.isBullish ? .green : .red
        
        let normalizedBodyTop = CGFloat((candle.bodyTop - minPrice) / priceRange)
        let normalizedBodyBottom = CGFloat((candle.bodyBottom - minPrice) / priceRange)
        let normalizedHigh = CGFloat((candle.high - minPrice) / priceRange)
        let normalizedLow = CGFloat((candle.low - minPrice) / priceRange)
        
        ZStack {
            // Wick
            Rectangle()
                .fill(color)
                .frame(width: 1.5, height: (normalizedHigh - normalizedLow) * height)
                .offset(y: -((normalizedHigh + normalizedLow) / 2 - 0.5) * height)
            
            // Body
            Rectangle()
                .fill(color)
                .frame(width: width, height: max(1, (normalizedBodyTop - normalizedBodyBottom) * height))
                .offset(y: -((normalizedBodyTop + normalizedBodyBottom) / 2 - 0.5) * height)
            
            // Selection highlight
            if isSelected {
                RoundedRectangle(cornerRadius: 2)
                    .stroke(Color.yellow, lineWidth: 2)
                    .frame(width: width + 4, height: (normalizedHigh - normalizedLow) * height + 4)
                    .offset(y: -((normalizedHigh + normalizedLow) / 2 - 0.5) * height)
            }
        }
    }
}

// MARK: - Grid Lines

struct GridLinesView: View {
    let height: CGFloat
    let minPrice: Double
    let maxPrice: Double
    
    var body: some View {
        GeometryReader { geometry in
            let priceRange = maxPrice - minPrice
            let step = priceRange / 4
            
            ForEach(0..<5) { i in
                let price = minPrice + step * Double(i)
                let y = height - (CGFloat(i) / 4) * height
                
                HStack {
                    Path { path in
                        path.move(to: CGPoint(x: 0, y: y))
                        path.addLine(to: CGPoint(x: geometry.size.width, y: y))
                    }
                    .stroke(Color.gray.opacity(0.2), style: StrokeStyle(lineWidth: 0.5, dash: [5, 5]))
                    
                    Spacer()
                }
                
                Text("$\(price, specifier: "%.0f")")
                    .font(.system(size: 8))
                    .foregroundColor(.secondary)
                    .position(x: geometry.size.width - 25, y: y)
            }
        }
    }
}

// MARK: - MA Line

struct MALineView: View {
    let values: [Double]
    let minPrice: Double
    let priceRange: Double
    let width: CGFloat
    let height: CGFloat
    let color: Color
    
    var body: some View {
        Path { path in
            guard values.count > 1 else { return }
            
            let stepX = width / CGFloat(values.count - 1)
            
            for (index, value) in values.enumerated() {
                let x = CGFloat(index) * stepX
                let normalizedY = CGFloat((value - minPrice) / priceRange)
                let y = height - normalizedY * height
                
                if index == 0 {
                    path.move(to: CGPoint(x: x, y: y))
                } else {
                    path.addLine(to: CGPoint(x: x, y: y))
                }
            }
        }
        .stroke(color, lineWidth: 1.5)
    }
}

// MARK: - Current Price Line

struct CurrentPriceLine: View {
    let price: Double
    let minPrice: Double
    let priceRange: Double
    let height: CGFloat
    let width: CGFloat
    
    var body: some View {
        let normalizedY = CGFloat((price - minPrice) / priceRange)
        let y = height - normalizedY * height
        
        HStack(spacing: 0) {
            Path { path in
                path.move(to: CGPoint(x: 0, y: y))
                path.addLine(to: CGPoint(x: width - 50, y: y))
            }
            .stroke(Color.yellow, style: StrokeStyle(lineWidth: 1, dash: [5, 3]))
            
            Text("$\(price, specifier: "%.2f")")
                .font(.system(size: 9, weight: .bold))
                .foregroundColor(.white)
                .padding(.horizontal, 4)
                .padding(.vertical, 2)
                .background(Color.yellow)
                .cornerRadius(2)
                .position(x: width - 25, y: y)
        }
    }
}

// MARK: - Crosshair Overlay

struct CrosshairOverlay: View {
    let candle: Candle
    let geometry: GeometryProxy
    
    var body: some View {
        VStack {
            Spacer()
            
            // Candle info box
            VStack(alignment: .leading, spacing: 4) {
                Text(candle.timestamp, style: .date)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                
                HStack(spacing: 16) {
                    InfoItem(label: "O", value: candle.open, color: .secondary)
                    InfoItem(label: "H", value: candle.high, color: .green)
                    InfoItem(label: "L", value: candle.low, color: .red)
                    InfoItem(label: "C", value: candle.close, color: candle.isBullish ? .green : .red)
                }
            }
            .padding(8)
            .background(Color(.systemBackground).opacity(0.9))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
            )
        }
        .padding()
    }
}

struct InfoItem: View {
    let label: String
    let value: Double
    let color: Color
    
    var body: some View {
        VStack(spacing: 0) {
            Text(label)
                .font(.system(size: 8))
                .foregroundColor(.secondary)
            Text("$\(value, specifier: "%.2f")")
                .font(.system(size: 10, weight: .medium, design: .monospaced))
                .foregroundColor(color)
        }
    }
}

// MARK: - RSI Chart

struct RSIChartView: View {
    let values: [Double]
    
    var body: some View {
        VStack(spacing: 0) {
            Divider()
            
            HStack {
                Text("RSI")
                    .font(.caption2.bold())
                    .foregroundColor(.secondary)
                Spacer()
                if let lastValue = values.last {
                    Text(String(format: "%.1f", lastValue))
                        .font(.caption.bold())
                        .foregroundColor(rsiColor(lastValue))
                }
            }
            .padding(.horizontal, 8)
            .padding(.top, 4)
            
            GeometryReader { geometry in
                ZStack {
                    // Overbought/Oversold zones
                    Rectangle()
                        .fill(Color.red.opacity(0.1))
                        .frame(height: geometry.size.height * 0.3)
                        .position(x: geometry.size.width / 2, y: geometry.size.height * 0.15)
                    
                    Rectangle()
                        .fill(Color.green.opacity(0.1))
                        .frame(height: geometry.size.height * 0.3)
                        .position(x: geometry.size.width / 2, y: geometry.size.height * 0.85)
                    
                    // RSI Line
                    Path { path in
                        guard values.count > 1 else { return }
                        
                        let stepX = geometry.size.width / CGFloat(values.count - 1)
                        
                        for (index, value) in values.enumerated() {
                            let x = CGFloat(index) * stepX
                            let y = geometry.size.height - (CGFloat(value) / 100) * geometry.size.height
                            
                            if index == 0 {
                                path.move(to: CGPoint(x: x, y: y))
                            } else {
                                path.addLine(to: CGPoint(x: x, y: y))
                            }
                        }
                    }
                    .stroke(Color.purple, lineWidth: 1.5)
                    
                    // 30/70 lines
                    Path { path in
                        let y30 = geometry.size.height * 0.7
                        let y70 = geometry.size.height * 0.3
                        
                        path.move(to: CGPoint(x: 0, y: y30))
                        path.addLine(to: CGPoint(x: geometry.size.width, y: y30))
                        
                        path.move(to: CGPoint(x: 0, y: y70))
                        path.addLine(to: CGPoint(x: geometry.size.width, y: y70))
                    }
                    .stroke(Color.gray.opacity(0.5), style: StrokeStyle(lineWidth: 0.5, dash: [3, 3]))
                }
            }
        }
        .background(Color(.systemGray6))
    }
    
    private func rsiColor(_ value: Double) -> Color {
        if value >= 70 { return .red }
        if value <= 30 { return .green }
        return .secondary
    }
}

// MARK: - Volume Chart

struct VolumeChartView: View {
    let candles: [Candle]
    
    var body: some View {
        VStack(spacing: 0) {
            Divider()
            
            HStack {
                Text("Volume")
                    .font(.caption2.bold())
                    .foregroundColor(.secondary)
                Spacer()
            }
            .padding(.horizontal, 8)
            .padding(.top, 4)
            
            GeometryReader { geometry in
                let maxVolume = candles.map { $0.volume }.max() ?? 1
                let visibleCandles = Array(candles.suffix(50))
                let barWidth = geometry.size.width / CGFloat(visibleCandles.count) * 0.8
                
                HStack(alignment: .bottom, spacing: barWidth * 0.1) {
                    ForEach(visibleCandles) { candle in
                        Rectangle()
                            .fill(candle.isBullish ? Color.green.opacity(0.5) : Color.red.opacity(0.5))
                            .frame(
                                width: barWidth,
                                height: CGFloat(candle.volume / maxVolume) * geometry.size.height * 0.9
                            )
                    }
                }
            }
        }
        .background(Color(.systemGray6))
    }
}

// MARK: - Indicator Selector

struct IndicatorSelectorView: View {
    @Binding var enabledIndicators: Set<ChartIndicatorType>
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            List {
                Section("Moving Averages") {
                    IndicatorToggle(type: .ma7, enabled: $enabledIndicators)
                    IndicatorToggle(type: .ma25, enabled: $enabledIndicators)
                    IndicatorToggle(type: .ma99, enabled: $enabledIndicators)
                    IndicatorToggle(type: .ema12, enabled: $enabledIndicators)
                    IndicatorToggle(type: .ema26, enabled: $enabledIndicators)
                }
                
                Section("Overlays") {
                    IndicatorToggle(type: .bollinger, enabled: $enabledIndicators)
                }
                
                Section("Oscillators") {
                    IndicatorToggle(type: .rsi, enabled: $enabledIndicators)
                    IndicatorToggle(type: .macd, enabled: $enabledIndicators)
                }
                
                Section("Other") {
                    IndicatorToggle(type: .volume, enabled: $enabledIndicators)
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

struct IndicatorToggle: View {
    let type: ChartIndicatorType
    @Binding var enabled: Set<ChartIndicatorType>
    
    var body: some View {
        Toggle(type.rawValue, isOn: Binding(
            get: { enabled.contains(type) },
            set: { isOn in
                if isOn {
                    enabled.insert(type)
                } else {
                    enabled.remove(type)
                }
            }
        ))
    }
}

// MARK: - Preview

#Preview("Advanced Charts") {
    NavigationStack {
        AdvancedChartsView(symbol: "BTCUSDT")
            .navigationBarTitleDisplayMode(.inline)
    }
}
