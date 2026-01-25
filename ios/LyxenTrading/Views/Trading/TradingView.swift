//
//  TradingView.swift
//  LyxenTrading
//
//  Main trading screen with order placement
//

import SwiftUI

struct TradingView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    
    @State private var selectedSymbol = "BTCUSDT"
    @State private var orderSide: OrderSide = .buy
    @State private var orderType: OrderType = .market
    @State private var quantity = ""
    @State private var price = ""
    @State private var leverage = "10"
    @State private var takeProfit = ""
    @State private var stopLoss = ""
    @State private var showSymbolPicker = false
    @State private var isPlacingOrder = false
    @State private var showOrderResult = false
    @State private var orderResult: String = ""
    @State private var orderSuccess = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.lyxenBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Symbol Selector
                        symbolSelector
                        
                        // Price Info Card
                        priceInfoCard
                        
                        // Order Form
                        orderFormCard
                        
                        // Place Order Button
                        placeOrderButton
                    }
                    .padding()
                }
            }
            .navigationTitle("Trade")
            .navigationBarTitleDisplayMode(.large)
            .sheet(isPresented: $showSymbolPicker) {
                SymbolPickerView(selectedSymbol: $selectedSymbol)
            }
            .alert(orderSuccess ? "Order Placed" : "Order Failed", isPresented: $showOrderResult) {
                Button("OK") {}
            } message: {
                Text(orderResult)
            }
        }
    }
    
    // MARK: - Symbol Selector
    private var symbolSelector: some View {
        Button(action: { showSymbolPicker = true }) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(selectedSymbol)
                        .font(.title2.bold())
                        .foregroundColor(.white)
                    
                    Text(appState.selectedExchange.displayName)
                        .font(.caption)
                        .foregroundColor(.lyxenTextSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.down")
                    .foregroundColor(.lyxenTextSecondary)
            }
            .padding()
            .lyxenCard()
        }
    }
    
    // MARK: - Price Info Card
    private var priceInfoCard: some View {
        VStack(spacing: 12) {
            HStack {
                Text("Current Price")
                    .font(.subheadline)
                    .foregroundColor(.lyxenTextSecondary)
                Spacer()
                Text("$65,432.50")
                    .font(.title3.bold())
                    .foregroundColor(.white)
            }
            
            HStack {
                // 24h Change
                VStack(alignment: .leading, spacing: 4) {
                    Text("24h Change")
                        .font(.caption)
                        .foregroundColor(.lyxenTextMuted)
                    Text("+2.34%")
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(.lyxenGreen)
                }
                
                Spacer()
                
                // 24h Volume
                VStack(alignment: .leading, spacing: 4) {
                    Text("24h Volume")
                        .font(.caption)
                        .foregroundColor(.lyxenTextMuted)
                    Text("$1.2B")
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(.lyxenTextSecondary)
                }
                
                Spacer()
                
                // Open Interest
                VStack(alignment: .leading, spacing: 4) {
                    Text("Open Interest")
                        .font(.caption)
                        .foregroundColor(.lyxenTextMuted)
                    Text("$890M")
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(.lyxenTextSecondary)
                }
            }
        }
        .padding()
        .lyxenCard()
    }
    
    // MARK: - Order Form Card
    private var orderFormCard: some View {
        VStack(spacing: 16) {
            // Side Selector
            HStack(spacing: 0) {
                sideButton(side: .buy, title: "LONG", color: .lyxenGreen)
                sideButton(side: .sell, title: "SHORT", color: .lyxenRed)
            }
            .cornerRadius(10)
            
            // Order Type
            Picker("Order Type", selection: $orderType) {
                Text("Market").tag(OrderType.market)
                Text("Limit").tag(OrderType.limit)
            }
            .pickerStyle(.segmented)
            
            // Quantity
            OrderInputField(
                label: "Quantity (USDT)",
                placeholder: "100",
                text: $quantity,
                keyboardType: .decimalPad
            )
            
            // Price (for Limit orders)
            if orderType == .limit {
                OrderInputField(
                    label: "Price",
                    placeholder: "65000",
                    text: $price,
                    keyboardType: .decimalPad
                )
            }
            
            // Leverage
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("Leverage")
                        .font(.subheadline)
                        .foregroundColor(.lyxenTextSecondary)
                    Spacer()
                    Text("\(leverage)x")
                        .font(.subheadline.bold())
                        .foregroundColor(.lyxenPrimary)
                }
                
                Slider(
                    value: Binding(
                        get: { Double(leverage) ?? 10 },
                        set: { leverage = String(Int($0)) }
                    ),
                    in: 1...100,
                    step: 1
                )
                .tint(.lyxenPrimary)
            }
            
            Divider().background(Color.lyxenCardHover)
            
            // TP/SL Section
            VStack(spacing: 12) {
                Text("Take Profit / Stop Loss")
                    .font(.subheadline)
                    .foregroundColor(.lyxenTextSecondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                HStack(spacing: 12) {
                    OrderInputField(
                        label: "TP %",
                        placeholder: "8",
                        text: $takeProfit,
                        keyboardType: .decimalPad
                    )
                    
                    OrderInputField(
                        label: "SL %",
                        placeholder: "3",
                        text: $stopLoss,
                        keyboardType: .decimalPad
                    )
                }
            }
        }
        .padding()
        .lyxenCard()
    }
    
    // MARK: - Side Button
    private func sideButton(side: OrderSide, title: String, color: Color) -> some View {
        Button(action: { orderSide = side }) {
            Text(title)
                .font(.headline.weight(.bold))
                .frame(maxWidth: .infinity)
                .frame(height: 48)
                .background(orderSide == side ? color : Color.lyxenSurface)
                .foregroundColor(orderSide == side ? .white : .lyxenTextMuted)
        }
    }
    
    // MARK: - Place Order Button
    private var placeOrderButton: some View {
        Button(action: placeOrder) {
            HStack {
                if isPlacingOrder {
                    ProgressView()
                        .tint(.white)
                } else {
                    Image(systemName: orderSide == .buy ? "arrow.up.circle.fill" : "arrow.down.circle.fill")
                    Text("Place \(orderSide == .buy ? "Long" : "Short") Order")
                        .fontWeight(.bold)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 56)
            .background(orderSide == .buy ? Color.lyxenGreen : Color.lyxenRed)
            .foregroundColor(.white)
            .cornerRadius(12)
        }
        .disabled(quantity.isEmpty || isPlacingOrder)
    }
    
    // MARK: - Place Order Action
    private func placeOrder() {
        guard let qty = Double(quantity) else { return }
        
        isPlacingOrder = true
        
        Task {
            let success = await tradingService.placeOrder(
                symbol: selectedSymbol,
                side: orderSide,
                orderType: orderType,
                quantity: qty,
                price: Double(price),
                leverage: Int(leverage) ?? 10,
                takeProfit: Double(takeProfit),
                stopLoss: Double(stopLoss)
            )
            
            isPlacingOrder = false
            orderSuccess = success
            orderResult = success 
                ? "Your \(orderSide == .buy ? "long" : "short") order for \(selectedSymbol) has been placed successfully."
                : "Failed to place order. Please check your balance and try again."
            showOrderResult = true
            
            if success {
                quantity = ""
                price = ""
                takeProfit = ""
                stopLoss = ""
            }
        }
    }
}

// MARK: - Order Input Field
struct OrderInputField: View {
    let label: String
    let placeholder: String
    @Binding var text: String
    var keyboardType: UIKeyboardType = .default
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label)
                .font(.caption)
                .foregroundColor(.lyxenTextSecondary)
            
            TextField(placeholder, text: $text)
                .keyboardType(keyboardType)
                .padding()
                .background(Color.lyxenSurface)
                .foregroundColor(.white)
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.lyxenCardHover, lineWidth: 1)
                )
        }
    }
}

// OrderSide and OrderType enums are defined in AppState.swift

#Preview {
    TradingView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
