//
//  AdvancedTradingView.swift
//  EnlikoTrading
//
//  Full-featured trading interface like Binance/Bybit
//  Features: All order types, TP/SL, Leverage, Position calculator
//

import SwiftUI

// MARK: - Order Types (Extended)
enum ExtendedOrderType: String, CaseIterable {
    case market = "Market"
    case limit = "Limit"
    case stopMarket = "Stop Market"
    case stopLimit = "Stop Limit"
    case takeProfit = "Take Profit"
    case trailingStop = "Trailing Stop"
    
    var icon: String {
        switch self {
        case .market: return "bolt.fill"
        case .limit: return "clock.fill"
        case .stopMarket: return "exclamationmark.triangle.fill"
        case .stopLimit: return "exclamationmark.shield.fill"
        case .takeProfit: return "target"
        case .trailingStop: return "chart.line.uptrend.xyaxis"
        }
    }
}

// MARK: - Position Size Mode
enum PositionSizeMode: String, CaseIterable {
    case usdt = "USDT"
    case percent = "% Equity"
    case contracts = "Contracts"
}

struct AdvancedTradingView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @Environment(\.dismiss) var dismiss
    @ObservedObject var localization = LocalizationManager.shared
    
    // Symbol
    @State private var selectedSymbol = "BTCUSDT"
    @State private var showSymbolPicker = false
    @State private var currentPrice: Double = 0
    
    // Side
    @State private var selectedSide: OrderSide = .buy
    
    // Order Type
    @State private var selectedOrderType: ExtendedOrderType = .market
    
    // Position Size
    @State private var sizeMode: PositionSizeMode = .usdt
    @State private var sizeValue: String = ""
    @State private var leverage: Double = 10
    
    // Prices
    @State private var limitPrice: String = ""
    @State private var stopPrice: String = ""
    
    // TP/SL
    @State private var tpEnabled = false
    @State private var slEnabled = false
    @State private var tpPrice: String = ""
    @State private var slPrice: String = ""
    @State private var tpPercent: String = "8"
    @State private var slPercent: String = "3"
    @State private var tpslMode: TPSLMode = .price
    
    // State
    @State private var isPlacing = false
    @State private var showOrderPreview = false
    
    enum TPSLMode: String, CaseIterable {
        case price = "Price"
        case percent = "Percent"
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        // Symbol & Price Header
                        symbolPriceHeader
                        
                        // Buy/Sell Toggle
                        sideToggle
                        
                        // Order Type Picker
                        orderTypePicker
                        
                        // Position Size Section
                        positionSizeSection
                        
                        // Price Inputs (conditional)
                        priceInputsSection
                        
                        // Leverage Slider
                        leverageSection
                        
                        // TP/SL Section
                        tpslSection
                        
                        // Order Summary
                        orderSummary
                        
                        // Place Order Button
                        placeOrderButton
                        
                        Spacer(minLength: 100)
                    }
                    .padding()
                }
            }
            .navigationTitle("open_position".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("close".localized) { dismiss() }
                }
            }
            .sheet(isPresented: $showSymbolPicker) {
                SymbolPickerView(selectedSymbol: $selectedSymbol)
            }
            .sheet(isPresented: $showOrderPreview) {
                OrderPreviewSheet(
                    symbol: selectedSymbol,
                    side: selectedSide,
                    orderType: selectedOrderType,
                    size: calculatedSize,
                    price: effectivePrice,
                    leverage: Int(leverage),
                    tp: tpEnabled ? Double(tpPrice) : nil,
                    sl: slEnabled ? Double(slPrice) : nil,
                    onConfirm: executeOrder
                )
            }
            .task {
                await fetchCurrentPrice()
            }
        }
    }
    
    // MARK: - Symbol & Price Header
    private var symbolPriceHeader: some View {
        Button {
            showSymbolPicker = true
        } label: {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(selectedSymbol)
                        .font(.title.bold())
                        .foregroundColor(.white)
                    
                    HStack(spacing: 8) {
                        Text("$\(currentPrice, specifier: "%.2f")")
                            .font(.headline)
                            .foregroundColor(.enlikoPrimary)
                        
                        Text("\(appState.currentExchange.displayName)")
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(appState.currentExchange == .bybit ? Color.orange.opacity(0.2) : Color.cyan.opacity(0.2))
                            .foregroundColor(appState.currentExchange == .bybit ? .orange : .cyan)
                            .cornerRadius(8)
                    }
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color.enlikoSurface)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Side Toggle (Buy/Sell)
    private var sideToggle: some View {
        HStack(spacing: 0) {
            ForEach(OrderSide.allCases, id: \.self) { side in
                Button {
                    withAnimation(.spring(response: 0.3)) {
                        selectedSide = side
                    }
                } label: {
                    VStack(spacing: 4) {
                        Image(systemName: side == .buy ? "arrow.up.circle.fill" : "arrow.down.circle.fill")
                            .font(.title2)
                        Text(side == .buy ? "Long" : "Short")
                            .font(.headline)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(
                        selectedSide == side
                        ? (side == .buy ? Color.enlikoGreen : Color.enlikoRed)
                        : Color.enlikoSurface
                    )
                    .foregroundColor(selectedSide == side ? .white : .secondary)
                }
            }
        }
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(selectedSide == .buy ? Color.enlikoGreen : Color.enlikoRed, lineWidth: 2)
        )
    }
    
    // MARK: - Order Type Picker
    private var orderTypePicker: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("order_type".localized)
                .font(.caption)
                .foregroundColor(.secondary)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(ExtendedOrderType.allCases, id: \.self) { type in
                        Button {
                            selectedOrderType = type
                        } label: {
                            HStack(spacing: 6) {
                                Image(systemName: type.icon)
                                    .font(.caption)
                                Text(type.rawValue)
                                    .font(.caption.bold())
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 10)
                            .background(selectedOrderType == type ? Color.enlikoPrimary : Color.enlikoSurface)
                            .foregroundColor(selectedOrderType == type ? .white : .secondary)
                            .cornerRadius(20)
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Position Size Section
    private var positionSizeSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("position_size".localized)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                // Size Mode Picker
                Picker("", selection: $sizeMode) {
                    ForEach(PositionSizeMode.allCases, id: \.self) { mode in
                        Text(mode.rawValue).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
                .frame(width: 200)
            }
            
            HStack {
                TextField("0.00", text: $sizeValue)
                    .keyboardType(.decimalPad)
                    .font(.title2.bold())
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                
                // Quick Size Buttons
                VStack(spacing: 4) {
                    quickSizeButton("25%", 0.25)
                    quickSizeButton("50%", 0.50)
                    quickSizeButton("100%", 1.0)
                }
            }
            
            // Calculated Size Display
            if let equity = tradingService.balance?.totalEquity, !sizeValue.isEmpty {
                HStack {
                    Text("≈ \(calculatedSize, specifier: "%.4f") \(baseAsset)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text("~$\(calculatedUSDT, specifier: "%.2f") USDT")
                        .font(.caption.bold())
                        .foregroundColor(.enlikoPrimary)
                }
                .padding(.horizontal, 4)
            }
        }
        .padding()
        .background(Color.enlikoSurface.opacity(0.5))
        .cornerRadius(12)
    }
    
    private func quickSizeButton(_ label: String, _ percent: Double) -> some View {
        Button {
            if let equity = tradingService.balance?.totalEquity {
                let adjustedEquity = equity * leverage / currentPrice
                sizeValue = String(format: "%.2f", equity * percent)
                sizeMode = .usdt
            }
        } label: {
            Text(label)
                .font(.caption2.bold())
                .padding(.horizontal, 8)
                .padding(.vertical, 6)
                .background(Color.enlikoSurface)
                .cornerRadius(6)
        }
    }
    
    // MARK: - Price Inputs Section
    @ViewBuilder
    private var priceInputsSection: some View {
        if selectedOrderType != .market {
            VStack(spacing: 12) {
                // Limit Price (for Limit, Stop-Limit)
                if [.limit, .stopLimit].contains(selectedOrderType) {
                    priceInput(label: "limit_price".localized, value: $limitPrice, placeholder: "\(currentPrice)")
                }
                
                // Stop/Trigger Price (for Stop orders)
                if [.stopMarket, .stopLimit, .takeProfit, .trailingStop].contains(selectedOrderType) {
                    priceInput(label: "trigger_price".localized, value: $stopPrice, placeholder: "0.00")
                }
            }
        }
    }
    
    private func priceInput(label: String, value: Binding<String>, placeholder: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            
            HStack {
                TextField(placeholder, text: value)
                    .keyboardType(.decimalPad)
                    .font(.title3)
                
                Button {
                    value.wrappedValue = "\(currentPrice)"
                } label: {
                    Text("Last")
                        .font(.caption.bold())
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color.enlikoPrimary.opacity(0.2))
                        .cornerRadius(8)
                }
            }
            .padding()
            .background(Color.enlikoSurface)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Leverage Section
    private var leverageSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("leverage".localized)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Text("\(Int(leverage))x")
                    .font(.title2.bold())
                    .foregroundColor(leverageColor)
            }
            
            // Leverage Slider
            Slider(value: $leverage, in: 1...125, step: 1)
                .tint(leverageColor)
            
            // Quick Leverage Buttons
            HStack(spacing: 8) {
                ForEach([1, 5, 10, 25, 50, 100], id: \.self) { lev in
                    Button {
                        leverage = Double(lev)
                    } label: {
                        Text("\(lev)x")
                            .font(.caption.bold())
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 8)
                            .background(Int(leverage) == lev ? leverageColor : Color.enlikoSurface)
                            .foregroundColor(Int(leverage) == lev ? .white : .secondary)
                            .cornerRadius(8)
                    }
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface.opacity(0.5))
        .cornerRadius(12)
    }
    
    private var leverageColor: Color {
        if leverage <= 10 {
            return .green
        } else if leverage <= 50 {
            return .orange
        } else {
            return .red
        }
    }
    
    // MARK: - TP/SL Section
    private var tpslSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("tp_sl".localized)
                    .font(.subheadline.bold())
                
                Spacer()
                
                // Mode Toggle
                Picker("", selection: $tpslMode) {
                    ForEach(TPSLMode.allCases, id: \.self) { mode in
                        Text(mode.rawValue).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
                .frame(width: 150)
            }
            
            // Take Profit
            HStack {
                Toggle("TP", isOn: $tpEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .green))
                    .labelsHidden()
                
                Text("Take Profit")
                    .font(.subheadline)
                    .foregroundColor(tpEnabled ? .white : .secondary)
                
                Spacer()
                
                if tpEnabled {
                    if tpslMode == .price {
                        TextField("Price", text: $tpPrice)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 120)
                            .padding(8)
                            .background(Color.enlikoSurface)
                            .cornerRadius(8)
                    } else {
                        HStack {
                            TextField("%", text: $tpPercent)
                                .keyboardType(.decimalPad)
                                .multilineTextAlignment(.trailing)
                                .frame(width: 60)
                            Text("%")
                                .foregroundColor(.secondary)
                        }
                        .padding(8)
                        .background(Color.enlikoSurface)
                        .cornerRadius(8)
                    }
                }
            }
            
            // Stop Loss
            HStack {
                Toggle("SL", isOn: $slEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .red))
                    .labelsHidden()
                
                Text("Stop Loss")
                    .font(.subheadline)
                    .foregroundColor(slEnabled ? .white : .secondary)
                
                Spacer()
                
                if slEnabled {
                    if tpslMode == .price {
                        TextField("Price", text: $slPrice)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 120)
                            .padding(8)
                            .background(Color.enlikoSurface)
                            .cornerRadius(8)
                    } else {
                        HStack {
                            TextField("%", text: $slPercent)
                                .keyboardType(.decimalPad)
                                .multilineTextAlignment(.trailing)
                                .frame(width: 60)
                            Text("%")
                                .foregroundColor(.secondary)
                        }
                        .padding(8)
                        .background(Color.enlikoSurface)
                        .cornerRadius(8)
                    }
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface.opacity(0.5))
        .cornerRadius(12)
    }
    
    // MARK: - Order Summary
    private var orderSummary: some View {
        VStack(spacing: 8) {
            summaryRow("Symbol", selectedSymbol)
            summaryRow("Side", selectedSide == .buy ? "Long" : "Short", color: selectedSide == .buy ? .green : .red)
            summaryRow("Type", selectedOrderType.rawValue)
            summaryRow("Size", String(format: "%.4f %@", calculatedSize, baseAsset))
            summaryRow("Leverage", "\(Int(leverage))x", color: leverageColor)
            
            if selectedOrderType == .limit, let price = Double(limitPrice) {
                summaryRow("Limit Price", String(format: "$%.2f", price))
            }
            
            if tpEnabled, let tp = Double(tpPrice) {
                summaryRow("Take Profit", String(format: "$%.2f", tp), color: .green)
            }
            
            if slEnabled, let sl = Double(slPrice) {
                summaryRow("Stop Loss", String(format: "$%.2f", sl), color: .red)
            }
            
            Divider()
            
            // Estimated Liquidation
            summaryRow("Est. Liq. Price", String(format: "$%.2f", estimatedLiquidation), color: .orange)
            
            // Max Loss
            summaryRow("Max Loss", String(format: "-$%.2f", maxLoss), color: .red)
        }
        .padding()
        .background(Color.enlikoSurface.opacity(0.5))
        .cornerRadius(12)
    }
    
    private func summaryRow(_ label: String, _ value: String, color: Color = .white) -> some View {
        HStack {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .font(.caption.bold())
                .foregroundColor(color)
        }
    }
    
    // MARK: - Place Order Button
    private var placeOrderButton: some View {
        Button {
            showOrderPreview = true
        } label: {
            HStack {
                if isPlacing {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Image(systemName: selectedSide == .buy ? "arrow.up.circle.fill" : "arrow.down.circle.fill")
                    Text(selectedSide == .buy ? "Open Long" : "Open Short")
                        .font(.headline)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 18)
            .background(selectedSide == .buy ? Color.enlikoGreen : Color.enlikoRed)
            .foregroundColor(.white)
            .cornerRadius(16)
        }
        .disabled(sizeValue.isEmpty || isPlacing)
        .opacity(sizeValue.isEmpty ? 0.5 : 1)
    }
    
    // MARK: - Computed Properties
    private var baseAsset: String {
        selectedSymbol.replacingOccurrences(of: "USDT", with: "")
    }
    
    private var calculatedSize: Double {
        guard let value = Double(sizeValue), currentPrice > 0 else { return 0 }
        
        switch sizeMode {
        case .usdt:
            return (value * leverage) / currentPrice
        case .percent:
            if let equity = tradingService.balance?.totalEquity {
                return (equity * value / 100 * leverage) / currentPrice
            }
            return 0
        case .contracts:
            return value
        }
    }
    
    private var calculatedUSDT: Double {
        calculatedSize * currentPrice / leverage
    }
    
    private var effectivePrice: Double {
        if selectedOrderType == .market {
            return currentPrice
        } else if let price = Double(limitPrice) {
            return price
        }
        return currentPrice
    }
    
    private var estimatedLiquidation: Double {
        guard leverage > 0, currentPrice > 0 else { return 0 }
        let margin = 1.0 / leverage
        if selectedSide == .buy {
            return currentPrice * (1 - margin + 0.005) // 0.5% maintenance margin
        } else {
            return currentPrice * (1 + margin - 0.005)
        }
    }
    
    private var maxLoss: Double {
        calculatedUSDT
    }
    
    // MARK: - Actions
    private func fetchCurrentPrice() async {
        // TODO: Fetch from API - for now use mock
        currentPrice = selectedSymbol.contains("BTC") ? 98500 : 3200
    }
    
    private func executeOrder() {
        isPlacing = true
        
        Task {
            // Convert percent to price if needed
            var finalTP: Double? = nil
            var finalSL: Double? = nil
            
            if tpEnabled {
                if tpslMode == .price, let tp = Double(tpPrice) {
                    finalTP = tp
                } else if tpslMode == .percent, let pct = Double(tpPercent) {
                    finalTP = selectedSide == .buy
                        ? currentPrice * (1 + pct / 100)
                        : currentPrice * (1 - pct / 100)
                }
            }
            
            if slEnabled {
                if tpslMode == .price, let sl = Double(slPrice) {
                    finalSL = sl
                } else if tpslMode == .percent, let pct = Double(slPercent) {
                    finalSL = selectedSide == .buy
                        ? currentPrice * (1 - pct / 100)
                        : currentPrice * (1 + pct / 100)
                }
            }
            
            let success = await tradingService.placeOrder(
                symbol: selectedSymbol,
                side: selectedSide,
                orderType: selectedOrderType == .market ? .market : .limit,
                quantity: calculatedUSDT,
                price: selectedOrderType == .limit ? Double(limitPrice) : nil,
                leverage: Int(leverage),
                takeProfit: finalTP,
                stopLoss: finalSL
            )
            
            await MainActor.run {
                isPlacing = false
                if success {
                    dismiss()
                }
            }
        }
    }
}

// MARK: - Order Preview Sheet
struct OrderPreviewSheet: View {
    let symbol: String
    let side: OrderSide
    let orderType: ExtendedOrderType
    let size: Double
    let price: Double
    let leverage: Int
    let tp: Double?
    let sl: Double?
    let onConfirm: () -> Void
    
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    Image(systemName: side == .buy ? "arrow.up.circle.fill" : "arrow.down.circle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(side == .buy ? .green : .red)
                    
                    Text("Confirm Order")
                        .font(.title.bold())
                }
                .padding(.top, 24)
                
                // Details
                VStack(spacing: 16) {
                    detailRow("Symbol", symbol)
                    detailRow("Direction", side == .buy ? "Long" : "Short", color: side == .buy ? .green : .red)
                    detailRow("Order Type", orderType.rawValue)
                    detailRow("Size", String(format: "%.4f", size))
                    detailRow("Entry Price", String(format: "$%.2f", price))
                    detailRow("Leverage", "\(leverage)x")
                    
                    if let tp = tp {
                        detailRow("Take Profit", String(format: "$%.2f", tp), color: .green)
                    }
                    
                    if let sl = sl {
                        detailRow("Stop Loss", String(format: "$%.2f", sl), color: .red)
                    }
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(16)
                
                Spacer()
                
                // Buttons
                VStack(spacing: 12) {
                    Button {
                        onConfirm()
                        dismiss()
                    } label: {
                        Text("Confirm Order")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(side == .buy ? Color.enlikoGreen : Color.enlikoRed)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                    }
                    
                    Button {
                        dismiss()
                    } label: {
                        Text("Cancel")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
            .background(Color.enlikoBackground)
            .navigationBarHidden(true)
        }
        .presentationDetents([.medium])
    }
    
    private func detailRow(_ label: String, _ value: String, color: Color = .white) -> some View {
        HStack {
            Text(label)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .bold()
                .foregroundColor(color)
        }
    }
}

#Preview {
    AdvancedTradingView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
