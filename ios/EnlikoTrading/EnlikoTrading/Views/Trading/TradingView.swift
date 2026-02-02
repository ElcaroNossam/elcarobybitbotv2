//
//  TradingView.swift
//  EnlikoTrading
//
//  Trading interface for placing orders
//

import SwiftUI

struct TradingView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var selectedSymbol = "BTCUSDT"
    @State private var selectedSide: OrderSide = .buy
    @State private var selectedOrderType: OrderType = .market
    @State private var amount: String = ""
    @State private var price: String = ""
    @State private var leverage: Double = 10
    @State private var showSymbolPicker = false
    @State private var isPlacingOrder = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Symbol Selector
                        symbolSelector
                        
                        // Side Selection (Buy/Sell)
                        sideSelector
                        
                        // Order Type (Market/Limit)
                        orderTypeSelector
                        
                        // Amount Input
                        amountInput
                        
                        // Price Input (for Limit orders)
                        if selectedOrderType == .limit {
                            priceInput
                        }
                        
                        // Leverage Slider
                        leverageSlider
                        
                        // Place Order Button
                        placeOrderButton
                    }
                    .padding()
                    .padding(.bottom, 100) // Space for tab bar
                }
            }
            .navigationTitle("trading_title".localized)
            .withRTLSupport()
            .sheet(isPresented: $showSymbolPicker) {
                SymbolPickerView(selectedSymbol: $selectedSymbol)
            }
        }
    }
    
    // MARK: - Symbol Selector
    private var symbolSelector: some View {
        Button {
            showSymbolPicker = true
        } label: {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Symbol")
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                    Text(selectedSymbol)
                        .font(.title2.bold())
                        .foregroundColor(.enlikoText)
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundColor(.enlikoTextSecondary)
            }
            .padding()
            .background(Color.enlikoCard)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Side Selector
    private var sideSelector: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Side")
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            
            HStack(spacing: 12) {
                ForEach(OrderSide.allCases, id: \.self) { side in
                    Button {
                        selectedSide = side
                    } label: {
                        Text(side.rawValue)
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(selectedSide == side ? side.color : Color.enlikoCard)
                            .foregroundColor(selectedSide == side ? .white : .enlikoText)
                            .cornerRadius(10)
                    }
                }
            }
        }
    }
    
    // MARK: - Order Type Selector
    private var orderTypeSelector: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Order Type")
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            
            HStack(spacing: 12) {
                ForEach(OrderType.allCases, id: \.self) { type in
                    Button {
                        selectedOrderType = type
                    } label: {
                        Text(type.rawValue)
                            .font(.subheadline.weight(.medium))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(selectedOrderType == type ? Color.enlikoPrimary : Color.enlikoCard)
                            .foregroundColor(selectedOrderType == type ? .white : .enlikoText)
                            .cornerRadius(10)
                    }
                }
            }
        }
    }
    
    // MARK: - Amount Input
    private var amountInput: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Amount (USDT)")
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            
            TextField("0.00", text: $amount)
                .keyboardType(.decimalPad)
                .font(.title2)
                .padding()
                .background(Color.enlikoCard)
                .cornerRadius(10)
        }
    }
    
    // MARK: - Price Input
    private var priceInput: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Price")
                .font(.caption)
                .foregroundColor(.enlikoTextSecondary)
            
            TextField("0.00", text: $price)
                .keyboardType(.decimalPad)
                .font(.title2)
                .padding()
                .background(Color.enlikoCard)
                .cornerRadius(10)
        }
    }
    
    // MARK: - Leverage Slider
    private var leverageSlider: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Leverage")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                Spacer()
                Text("\(Int(leverage))x")
                    .font(.headline)
                    .foregroundColor(.enlikoPrimary)
            }
            
            Slider(value: $leverage, in: 1...100, step: 1)
                .tint(.enlikoPrimary)
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(12)
    }
    
    // MARK: - Place Order Button
    private var placeOrderButton: some View {
        Button {
            placeOrder()
        } label: {
            HStack {
                if isPlacingOrder {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Text(selectedSide == .buy ? "Buy / Long" : "Sell / Short")
                        .font(.headline)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(selectedSide == .buy ? Color.enlikoGreen : Color.enlikoRed)
            .foregroundColor(.white)
            .cornerRadius(12)
        }
        .disabled(amount.isEmpty || isPlacingOrder)
        .opacity(amount.isEmpty ? 0.5 : 1)
    }
    
    // MARK: - Place Order Action
    private func placeOrder() {
        guard let amountValue = Double(amount) else { return }
        
        isPlacingOrder = true
        
        Task {
            let success = await tradingService.placeOrder(
                symbol: selectedSymbol,
                side: selectedSide,
                orderType: selectedOrderType,
                quantity: amountValue,
                price: selectedOrderType == .limit ? Double(price) : nil,
                leverage: Int(leverage)
            )
            
            await MainActor.run {
                isPlacingOrder = false
                if success {
                    amount = ""
                    price = ""
                }
            }
        }
    }
}

#Preview {
    TradingView()
        .environmentObject(AppState.shared)
        .environmentObject(TradingService.shared)
}
