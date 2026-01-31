//
//  ModernTradingView.swift
//  EnlikoTrading
//
//  Professional trading interface with sleek design
//  Quick Long/Short, price display, order settings
//

import SwiftUI

struct ModernTradingView: View {
    @EnvironmentObject var tradingService: TradingService
    @EnvironmentObject var appState: AppState
    
    @State private var selectedSymbol = "BTCUSDT"
    @State private var selectedSide: TradeSide = .long
    @State private var selectedOrderType: TradeOrderType = .market
    @State private var quantity = ""
    @State private var price = ""
    @State private var leverage: Double = 10
    @State private var tpPercent = ""
    @State private var slPercent = ""
    @State private var showSymbolPicker = false
    @State private var isPlacingOrder = false
    @State private var showOrderConfirmation = false
    
    enum TradeSide: String, CaseIterable {
        case long = "Long"
        case short = "Short"
        
        var color: Color {
            self == .long ? .enlikoGreen : .enlikoRed
        }
        
        var icon: String {
            self == .long ? "arrow.up.right" : "arrow.down.right"
        }
        
        var toOrderSide: OrderSide {
            self == .long ? .buy : .sell
        }
    }
    
    enum TradeOrderType: String, CaseIterable {
        case market = "Market"
        case limit = "Limit"
        
        var toOrderType: OrderType {
            .init(rawValue: self.rawValue) ?? .market
        }
    }
    
    var body: some View {
        ZStack {
            backgroundGradient
            
            ScrollView(.vertical, showsIndicators: false) {
                VStack(spacing: 24) {
                    // Header
                    headerSection
                    
                    // Symbol Selector
                    symbolSelector
                    
                    // Price Display
                    priceDisplay
                    
                    // Order Type Selector
                    selectedOrderTypeSelector
                    
                    // Side Selector
                    sideSelector
                    
                    // Order Form
                    orderForm
                    
                    // Place Order Button
                    placeOrderButton
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 100)
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showSymbolPicker) {
            ModernSymbolPickerView(selectedSymbol: $selectedSymbol)
        }
        .sheet(isPresented: $showOrderConfirmation) {
            OrderConfirmationSheet(
                symbol: selectedSymbol,
                side: selectedSide,
                orderType: selectedOrderType,
                quantity: Double(quantity) ?? 0,
                price: Double(price) ?? getCurrentPrice(),
                leverage: leverage,
                tpPercent: Double(tpPercent),
                slPercent: Double(slPercent),
                isPlacing: $isPlacingOrder,
                onConfirm: placeOrder
            )
            .presentationDetents([.medium])
            .presentationDragIndicator(.visible)
        }
    }
    
    // MARK: - Background
    private var backgroundGradient: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            // Ambient glow based on selected side
            Circle()
                .fill(selectedSide.color.opacity(0.08))
                .frame(width: 400, height: 400)
                .blur(radius: 100)
                .offset(y: -100)
        }
    }
    
    // MARK: - Header
    private var headerSection: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("trading".localized)
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.white)
                
                Text("\(appState.currentExchange == .bybit ? "Bybit" : "HyperLiquid") • \(accountLabel)")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            // Balance Quick View
            VStack(alignment: .trailing, spacing: 2) {
                Text("Available")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
                
                Text("$\(tradingService.balance?.displayAvailable ?? 0, specifier: "%.2f")")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.white)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.enlikoCard)
            )
        }
        .padding(.top, 16)
    }
    
    private var accountLabel: String {
        switch appState.currentAccountType {
        case .demo: return "Demo"
        case .real: return "Real"
        case .testnet: return "Testnet"
        case .mainnet: return "Mainnet"
        }
    }
    
    // MARK: - Symbol Selector
    private var symbolSelector: some View {
        Button(action: { showSymbolPicker = true }) {
            HStack(spacing: 12) {
                // Symbol Icon
                ZStack {
                    Circle()
                        .fill(Color.enlikoPrimary.opacity(0.2))
                        .frame(width: 48, height: 48)
                    
                    Text(String(selectedSymbol.prefix(1)))
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.enlikoPrimary)
                }
                
                // Symbol Name
                VStack(alignment: .leading, spacing: 2) {
                    Text(selectedSymbol)
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text("Perpetual")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.enlikoTextSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.enlikoTextSecondary)
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.enlikoCard)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.enlikoBorder, lineWidth: 1)
                    )
            )
        }
    }
    
    // MARK: - Price Display
    private var priceDisplay: some View {
        VStack(spacing: 12) {
            HStack {
                Text("current_price".localized)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
                
                Spacer()
                
                HStack(spacing: 6) {
                    Circle()
                        .fill(Color.enlikoGreen)
                        .frame(width: 6, height: 6)
                    
                    Text("Live")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.enlikoGreen)
                }
            }
            
            Text("$\(getCurrentPrice(), specifier: "%.2f")")
                .font(.system(size: 38, weight: .bold, design: .rounded))
                .foregroundColor(.white)
                .contentTransition(.numericText())
            
            // 24h Change
            HStack(spacing: 4) {
                Image(systemName: "arrow.up.right")
                    .font(.system(size: 12, weight: .bold))
                
                Text("+2.45%")
                    .font(.system(size: 14, weight: .semibold))
                
                Text("24h")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
            .foregroundColor(.enlikoGreen)
        }
        .padding(20)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.enlikoCard)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.enlikoBorder, lineWidth: 1)
                )
        )
    }
    
    private func getCurrentPrice() -> Double {
        // Return mock price for now - will be replaced with real data
        selectedSymbol == "BTCUSDT" ? 97234.50 : 3456.78
    }
    
    // MARK: - Order Type Selector
    private var selectedOrderTypeSelector: some View {
        HStack(spacing: 0) {
            ForEach(TradeOrderType.allCases, id: \.self) { type in
                Button(action: {
                    withAnimation(.spring(response: 0.3)) {
                        selectedOrderType = type
                    }
                    HapticManager.shared.perform(.selection)
                }) {
                    Text(type.rawValue)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(selectedOrderType == type ? .white : .enlikoTextSecondary)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(
                            selectedOrderType == type ?
                            RoundedRectangle(cornerRadius: 10).fill(Color.enlikoAccent) :
                            RoundedRectangle(cornerRadius: 10).fill(Color.clear)
                        )
                }
            }
        }
        .padding(4)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.enlikoCard)
        )
    }
    
    // MARK: - Side Selector
    private var sideSelector: some View {
        HStack(spacing: 12) {
            ForEach(TradeSide.allCases, id: \.self) { side in
                Button(action: {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                        selectedSide = side
                    }
                    HapticManager.shared.perform(.medium)
                }) {
                    HStack(spacing: 8) {
                        Image(systemName: side.icon)
                            .font(.system(size: 18, weight: .bold))
                        
                        Text(side.rawValue)
                            .font(.system(size: 16, weight: .bold))
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 18)
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(
                                selectedSide == side ?
                                LinearGradient(colors: [side.color, side.color.opacity(0.8)], startPoint: .top, endPoint: .bottom) :
                                LinearGradient(colors: [Color.enlikoCard], startPoint: .top, endPoint: .bottom)
                            )
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(
                                selectedSide == side ? side.color : Color.enlikoBorder,
                                lineWidth: selectedSide == side ? 2 : 1
                            )
                    )
                    .shadow(color: selectedSide == side ? side.color.opacity(0.4) : .clear, radius: 10, y: 5)
                }
            }
        }
    }
    
    // MARK: - Order Form
    private var orderForm: some View {
        VStack(spacing: 16) {
            // Leverage Slider
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("Leverage")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.enlikoTextSecondary)
                    
                    Spacer()
                    
                    Text("\(Int(leverage))x")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.enlikoPrimary)
                }
                
                HStack(spacing: 12) {
                    Slider(value: $leverage, in: 1...100, step: 1)
                        .tint(.enlikoPrimary)
                    
                    // Quick leverage buttons
                    HStack(spacing: 6) {
                        ForEach([5, 10, 25, 50], id: \.self) { lev in
                            Button(action: { leverage = Double(lev) }) {
                                Text("\(lev)x")
                                    .font(.system(size: 11, weight: .bold))
                                    .foregroundColor(leverage == Double(lev) ? .white : .enlikoTextSecondary)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 6)
                                    .background(
                                        RoundedRectangle(cornerRadius: 6)
                                            .fill(leverage == Double(lev) ? Color.enlikoPrimary : Color.enlikoSurface)
                                    )
                            }
                        }
                    }
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.enlikoCard)
            )
            
            // Quantity Input
            inputField(
                title: "Quantity",
                placeholder: "0.00",
                text: $quantity,
                suffix: selectedSymbol.replacingOccurrences(of: "USDT", with: "")
            )
            
            // Price Input (for Limit orders)
            if selectedOrderType == .limit {
                inputField(
                    title: "Price",
                    placeholder: String(format: "%.2f", getCurrentPrice()),
                    text: $price,
                    suffix: "USDT"
                )
            }
            
            // TP/SL Section
            HStack(spacing: 12) {
                inputField(
                    title: "Take Profit %",
                    placeholder: "e.g. 5",
                    text: $tpPercent,
                    suffix: "%",
                    compact: true
                )
                
                inputField(
                    title: "Stop Loss %",
                    placeholder: "e.g. 3",
                    text: $slPercent,
                    suffix: "%",
                    compact: true
                )
            }
        }
    }
    
    private func inputField(title: String, placeholder: String, text: Binding<String>, suffix: String, compact: Bool = false) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.enlikoTextSecondary)
            
            HStack {
                TextField(placeholder, text: text)
                    .font(.system(size: compact ? 16 : 18, weight: .semibold))
                    .foregroundColor(.white)
                    .keyboardType(.decimalPad)
                
                Text(suffix)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.enlikoTextSecondary)
            }
            .padding(compact ? 12 : 16)
            .background(
                RoundedRectangle(cornerRadius: compact ? 12 : 16)
                    .fill(Color.enlikoSurface)
                    .overlay(
                        RoundedRectangle(cornerRadius: compact ? 12 : 16)
                            .stroke(Color.enlikoBorder, lineWidth: 1)
                    )
            )
        }
    }
    
    // MARK: - Place Order Button
    private var placeOrderButton: some View {
        Button(action: {
            HapticManager.shared.perform(.medium)
            showOrderConfirmation = true
        }) {
            HStack(spacing: 10) {
                Image(systemName: selectedSide.icon)
                    .font(.system(size: 18, weight: .bold))
                
                Text("\(selectedSide.rawValue) \(selectedSymbol)")
                    .font(.system(size: 17, weight: .bold))
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 18)
            .background(selectedSide.color.gradient)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .shadow(color: selectedSide.color.opacity(0.5), radius: 15, y: 8)
        }
        .disabled(quantity.isEmpty)
        .opacity(quantity.isEmpty ? 0.5 : 1)
    }
    
    // MARK: - Actions
    private func placeOrder() {
        isPlacingOrder = true
        
        Task {
            // Convert local enums to global enums
            let globalSide: OrderSide = selectedSide.toOrderSide
            let globalType: OrderType = selectedOrderType.toOrderType
            let orderPrice = selectedOrderType == .limit ? Double(price) ?? 0 : nil
            
            _ = await tradingService.placeOrder(
                symbol: selectedSymbol,
                side: globalSide,
                orderType: globalType,
                quantity: Double(quantity) ?? 0,
                price: orderPrice
            )
            
            await MainActor.run {
                isPlacingOrder = false
                showOrderConfirmation = false
                quantity = ""
                price = ""
                HapticManager.shared.perform(.success)
            }
        }
    }
}

// MARK: - Order Confirmation Sheet
struct OrderConfirmationSheet: View {
    let symbol: String
    let side: ModernTradingView.TradeSide
    let orderType: ModernTradingView.TradeOrderType
    let quantity: Double
    let price: Double
    let leverage: Double
    let tpPercent: Double?
    let slPercent: Double?
    @Binding var isPlacing: Bool
    let onConfirm: () -> Void
    
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    ZStack {
                        Circle()
                            .fill(side.color.opacity(0.2))
                            .frame(width: 60, height: 60)
                        
                        Image(systemName: side.icon)
                            .font(.system(size: 26, weight: .bold))
                            .foregroundColor(side.color)
                    }
                    
                    Text("confirm_order".localized)
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.white)
                }
                
                // Order Details
                VStack(spacing: 12) {
                    detailRow(label: "Symbol", value: symbol)
                    detailRow(label: "Side", value: side.rawValue, color: side.color)
                    detailRow(label: "Type", value: orderType.rawValue)
                    detailRow(label: "Quantity", value: quantity.formattedCrypto)
                    detailRow(label: "Price", value: "$\(price.formattedPrice)")
                    detailRow(label: "Leverage", value: "\(Int(leverage))x")
                    
                    if let tp = tpPercent, tp > 0 {
                        detailRow(label: "Take Profit", value: String(format: "+%.1f%%", tp), color: .enlikoGreen)
                    }
                    if let sl = slPercent, sl > 0 {
                        detailRow(label: "Stop Loss", value: String(format: "-%.1f%%", sl), color: .enlikoRed)
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
                        title: "place_order".localized,
                        icon: "checkmark.circle.fill",
                        action: onConfirm,
                        isLoading: isPlacing,
                        style: side == .long ? .success : .danger
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
    
    private func detailRow(label: String, value: String, color: Color = .white) -> some View {
        HStack {
            Text(label)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.enlikoTextSecondary)
            
            Spacer()
            
            Text(value)
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(color)
        }
    }
}

// MARK: - Modern Symbol Picker
struct ModernSymbolPickerView: View {
    @Binding var selectedSymbol: String
    @Environment(\.dismiss) var dismiss
    @State private var searchText = ""
    
    let popularSymbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT"]
    let allSymbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "ATOMUSDT", "LTCUSDT"]
    
    var filteredSymbols: [String] {
        if searchText.isEmpty {
            return allSymbols
        }
        return allSymbols.filter { $0.lowercased().contains(searchText.lowercased()) }
    }
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            VStack(spacing: 20) {
                // Header
                HStack {
                    Text("select_symbol".localized)
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 28))
                            .foregroundColor(.enlikoTextSecondary)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)
                
                // Search
                HStack(spacing: 12) {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.enlikoTextSecondary)
                    
                    TextField("search".localized, text: $searchText)
                        .foregroundColor(.white)
                }
                .padding(14)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.enlikoCard)
                )
                .padding(.horizontal, 20)
                
                // Popular
                if searchText.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Popular")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.enlikoTextSecondary)
                            .padding(.horizontal, 20)
                        
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 10) {
                                ForEach(popularSymbols, id: \.self) { symbol in
                                    Button(action: {
                                        selectedSymbol = symbol
                                        dismiss()
                                    }) {
                                        Text(symbol)
                                            .font(.system(size: 14, weight: .semibold))
                                            .foregroundColor(selectedSymbol == symbol ? .white : .enlikoTextSecondary)
                                            .padding(.horizontal, 16)
                                            .padding(.vertical, 10)
                                            .background(
                                                Capsule()
                                                    .fill(selectedSymbol == symbol ? Color.enlikoPrimary : Color.enlikoCard)
                                            )
                                    }
                                }
                            }
                            .padding(.horizontal, 20)
                        }
                    }
                }
                
                // All Symbols
                ScrollView(.vertical, showsIndicators: false) {
                    LazyVStack(spacing: 8) {
                        ForEach(filteredSymbols, id: \.self) { symbol in
                            Button(action: {
                                selectedSymbol = symbol
                                dismiss()
                                HapticManager.shared.perform(.selection)
                            }) {
                                HStack(spacing: 12) {
                                    ZStack {
                                        Circle()
                                            .fill(Color.enlikoPrimary.opacity(0.2))
                                            .frame(width: 40, height: 40)
                                        
                                        Text(String(symbol.prefix(1)))
                                            .font(.system(size: 16, weight: .bold))
                                            .foregroundColor(.enlikoPrimary)
                                    }
                                    
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(symbol)
                                            .font(.system(size: 16, weight: .semibold))
                                            .foregroundColor(.white)
                                        
                                        Text("Perpetual")
                                            .font(.system(size: 12, weight: .medium))
                                            .foregroundColor(.enlikoTextSecondary)
                                    }
                                    
                                    Spacer()
                                    
                                    if selectedSymbol == symbol {
                                        Image(systemName: "checkmark.circle.fill")
                                            .font(.system(size: 22))
                                            .foregroundColor(.enlikoPrimary)
                                    }
                                }
                                .padding(14)
                                .background(
                                    RoundedRectangle(cornerRadius: 14)
                                        .fill(selectedSymbol == symbol ? Color.enlikoPrimary.opacity(0.1) : Color.enlikoCard)
                                )
                            }
                        }
                    }
                    .padding(.horizontal, 20)
                }
            }
        }
    }
}

// MARK: - Preview
#Preview {
    NavigationStack {
        ModernTradingView()
    }
}
