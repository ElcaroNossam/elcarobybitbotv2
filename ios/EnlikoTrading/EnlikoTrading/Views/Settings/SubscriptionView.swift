//
//  SubscriptionView.swift
//  EnlikoTrading
//
//  Subscription and crypto payment view with OxaPay integration
//

import SwiftUI

struct SubscriptionView: View {
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var paymentService = PaymentService.shared
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var selectedPlan: String = "premium"
    @State private var selectedDuration: String = "1m"
    @State private var selectedCurrency: String = "USDT"
    @State private var selectedNetwork: String = "TRC20"
    @State private var promoCode: String = ""
    @State private var promoApplied: PromoCodeResponse?
    
    @State private var showPaymentSheet = false
    @State private var showCurrencyPicker = false
    @State private var isCreatingPayment = false
    @State private var paymentError: String?
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        // Current subscription status
                        currentSubscriptionCard
                        
                        // Plan selection
                        planSelectionSection
                        
                        // Duration selection
                        durationSelectionSection
                        
                        // Promo code
                        promoCodeSection
                        
                        // Price summary
                        priceSummarySection
                        
                        // Pay button
                        payButton
                        
                        // Payment history
                        paymentHistorySection
                    }
                    .padding()
                }
            }
            .navigationTitle("subscription".localized)
            .navigationBarTitleDisplayMode(.large)
            .sheet(isPresented: $showPaymentSheet) {
                if let invoice = paymentService.currentInvoice {
                    PaymentInvoiceSheet(invoice: invoice)
                }
            }
            .sheet(isPresented: $showCurrencyPicker) {
                CurrencyPickerSheet(
                    currencies: paymentService.currencies,
                    selectedCurrency: $selectedCurrency,
                    selectedNetwork: $selectedNetwork
                )
            }
            .task {
                await paymentService.fetchPlans()
                await paymentService.fetchCurrencies()
                await paymentService.fetchPaymentHistory()
            }
        }
    }
    
    // MARK: - Current Subscription Card
    
    private var currentSubscriptionCard: some View {
        VStack(spacing: 12) {
            if let user = authManager.currentUser, user.isPremium == true {
                HStack {
                    Image(systemName: "crown.fill")
                        .font(.title2)
                        .foregroundColor(.enlikoYellow)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("premium_active".localized)
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        if let expiresAt = user.licenseExpiry {
                            Text("expires_at".localized + ": \(expiresAt)")
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                    }
                    
                    Spacer()
                    
                    Image(systemName: "checkmark.seal.fill")
                        .font(.title)
                        .foregroundColor(.enlikoGreen)
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.enlikoGreen.opacity(0.1))
                        .overlay(
                            RoundedRectangle(cornerRadius: 16)
                                .stroke(Color.enlikoGreen.opacity(0.3), lineWidth: 1)
                        )
                )
            } else {
                HStack {
                    Image(systemName: "gift.fill")
                        .font(.title2)
                        .foregroundColor(.enlikoOrange)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("no_subscription".localized)
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        Text("upgrade_now".localized)
                            .font(.caption)
                            .foregroundColor(.enlikoTextSecondary)
                    }
                    
                    Spacer()
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.enlikoCard)
                )
            }
        }
    }
    
    // MARK: - Plan Selection
    
    private var planSelectionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("select_plan".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                PlanCard(
                    name: "basic",
                    displayName: "🥈 Basic",
                    features: ["Demo trading", "3 strategies", "Email support"],
                    isSelected: selectedPlan == "basic",
                    action: { selectedPlan = "basic" }
                )
                
                PlanCard(
                    name: "premium",
                    displayName: "💎 Premium",
                    features: ["Demo + Real trading", "All strategies", "Priority support", "AI signals"],
                    isSelected: selectedPlan == "premium",
                    action: { selectedPlan = "premium" }
                )
                .overlay(
                    Text("POPULAR")
                        .font(.caption2.bold())
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.enlikoPrimary)
                        .cornerRadius(8)
                        .offset(x: 0, y: -10),
                    alignment: .topTrailing
                )
                
                PlanCard(
                    name: "enterprise",
                    displayName: "🏢 Enterprise",
                    features: ["Everything in Premium", "Dedicated account manager", "Custom strategies", "API access"],
                    isSelected: selectedPlan == "enterprise",
                    action: { selectedPlan = "enterprise" }
                )
            }
        }
    }
    
    // MARK: - Duration Selection
    
    private var durationSelectionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("select_duration".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            HStack(spacing: 12) {
                DurationButton(
                    duration: "1m",
                    label: "1 month",
                    price: paymentService.getPrice(for: selectedPlan, duration: "1m") ?? 0,
                    isSelected: selectedDuration == "1m",
                    action: { selectedDuration = "1m" }
                )
                
                DurationButton(
                    duration: "3m",
                    label: "3 months",
                    price: paymentService.getPrice(for: selectedPlan, duration: "3m") ?? 0,
                    isSelected: selectedDuration == "3m",
                    discount: 10,
                    action: { selectedDuration = "3m" }
                )
            }
            
            HStack(spacing: 12) {
                DurationButton(
                    duration: "6m",
                    label: "6 months",
                    price: paymentService.getPrice(for: selectedPlan, duration: "6m") ?? 0,
                    isSelected: selectedDuration == "6m",
                    discount: 20,
                    action: { selectedDuration = "6m" }
                )
                
                DurationButton(
                    duration: "1y",
                    label: "1 year",
                    price: paymentService.getPrice(for: selectedPlan, duration: "1y") ?? 0,
                    isSelected: selectedDuration == "1y",
                    discount: 30,
                    action: { selectedDuration = "1y" }
                )
            }
        }
    }
    
    // MARK: - Promo Code
    
    private var promoCodeSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("promo_code".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            HStack {
                TextField("enter_code".localized, text: $promoCode)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .autocapitalization(.allCharacters)
                
                Button(action: applyPromo) {
                    Text("apply".localized)
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(.enlikoPrimary)
                }
            }
            
            if let promo = promoApplied {
                HStack {
                    Image(systemName: promo.valid ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .foregroundColor(promo.valid ? .enlikoGreen : .enlikoRed)
                    Text(promo.message)
                        .font(.caption)
                        .foregroundColor(promo.valid ? .enlikoGreen : .enlikoRed)
                }
            }
        }
    }
    
    // MARK: - Price Summary
    
    private var priceSummarySection: some View {
        VStack(spacing: 12) {
            // Currency selection
            Button(action: { showCurrencyPicker = true }) {
                HStack {
                    Text("payment_method".localized)
                        .foregroundColor(.enlikoTextSecondary)
                    Spacer()
                    Text("\(selectedCurrency) (\(selectedNetwork))")
                        .foregroundColor(.white)
                    Image(systemName: "chevron.right")
                        .foregroundColor(.enlikoTextMuted)
                }
                .padding()
                .background(Color.enlikoCard)
                .cornerRadius(12)
            }
            
            // Price breakdown
            VStack(spacing: 8) {
                let basePrice = paymentService.getPrice(for: selectedPlan, duration: selectedDuration) ?? 0
                let finalPrice = promoApplied?.finalAmount ?? basePrice
                
                HStack {
                    Text("subtotal".localized)
                        .foregroundColor(.enlikoTextSecondary)
                    Spacer()
                    Text("$\(basePrice, specifier: "%.0f")")
                        .foregroundColor(.white)
                }
                
                if let discount = promoApplied?.discountPercent, discount > 0 {
                    HStack {
                        Text("discount".localized)
                            .foregroundColor(.enlikoGreen)
                        Spacer()
                        Text("-\(discount, specifier: "%.0f")%")
                            .foregroundColor(.enlikoGreen)
                    }
                }
                
                Divider().background(Color.enlikoBorder)
                
                HStack {
                    Text("total".localized)
                        .font(.headline)
                        .foregroundColor(.white)
                    Spacer()
                    Text("$\(finalPrice, specifier: "%.0f")")
                        .font(.title2.bold())
                        .foregroundColor(.enlikoPrimary)
                }
            }
            .padding()
            .background(Color.enlikoCard)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Pay Button
    
    @ViewBuilder
    private var payButton: some View {
        Button(action: createPayment) {
            HStack {
                if isCreatingPayment {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Image(systemName: "creditcard.fill")
                    Text("pay_with_crypto".localized)
                }
            }
            .font(.headline)
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.enlikoPrimary)
            .cornerRadius(16)
        }
        .disabled(isCreatingPayment)
        
        if let error = paymentError {
            Text(error)
                .font(.caption)
                .foregroundColor(.enlikoRed)
        }
    }
    
    // MARK: - Payment History
    
    private var paymentHistorySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("payment_history".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            if paymentService.paymentHistory.isEmpty {
                Text("no_payments_yet".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
                    .padding()
            } else {
                ForEach(paymentService.paymentHistory.prefix(5)) { payment in
                    PaymentHistoryRow(payment: payment)
                }
            }
        }
    }
    
    // MARK: - Actions
    
    private func applyPromo() {
        guard !promoCode.isEmpty else { return }
        
        Task {
            do {
                let response = try await paymentService.applyPromoCode(
                    code: promoCode,
                    plan: selectedPlan,
                    duration: selectedDuration
                )
                await MainActor.run {
                    promoApplied = response
                }
            } catch {
                await MainActor.run {
                    promoApplied = PromoCodeResponse(
                        valid: false,
                        discountPercent: nil,
                        finalAmount: nil,
                        originalAmount: nil,
                        message: error.localizedDescription
                    )
                }
            }
        }
    }
    
    private func createPayment() {
        isCreatingPayment = true
        paymentError = nil
        
        Task {
            do {
                _ = try await paymentService.createPayment(
                    plan: selectedPlan,
                    duration: selectedDuration,
                    currency: selectedCurrency,
                    network: selectedNetwork,
                    promoCode: promoApplied?.valid == true ? promoCode : nil
                )
                
                await MainActor.run {
                    isCreatingPayment = false
                    showPaymentSheet = true
                }
            } catch {
                await MainActor.run {
                    isCreatingPayment = false
                    paymentError = error.localizedDescription
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct PlanCard: View {
    let name: String
    let displayName: String
    let features: [String]
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(displayName)
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    if isSelected {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.enlikoPrimary)
                    }
                }
                
                ForEach(features, id: \.self) { feature in
                    HStack(spacing: 6) {
                        Image(systemName: "checkmark")
                            .font(.caption)
                            .foregroundColor(.enlikoGreen)
                        Text(feature)
                            .font(.caption)
                            .foregroundColor(.enlikoTextSecondary)
                    }
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.enlikoCard)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(isSelected ? Color.enlikoPrimary : Color.enlikoBorder, lineWidth: isSelected ? 2 : 1)
                    )
            )
        }
    }
}

struct DurationButton: View {
    let duration: String
    let label: String
    let price: Double
    let isSelected: Bool
    var discount: Int = 0
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Text(label)
                    .font(.subheadline.weight(.medium))
                    .foregroundColor(.white)
                
                Text("$\(price, specifier: "%.0f")")
                    .font(.headline)
                    .foregroundColor(isSelected ? .enlikoPrimary : .enlikoTextSecondary)
                
                if discount > 0 {
                    Text("-\(discount)%")
                        .font(.caption2)
                        .foregroundColor(.enlikoGreen)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.enlikoCard)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(isSelected ? Color.enlikoPrimary : Color.enlikoBorder, lineWidth: isSelected ? 2 : 1)
                    )
            )
        }
    }
}

struct PaymentHistoryRow: View {
    let payment: PaymentHistoryItem
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(payment.plan.capitalized)
                    .font(.subheadline.weight(.medium))
                    .foregroundColor(.white)
                
                Text(payment.createdAt)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("$\(payment.amountUsd, specifier: "%.0f")")
                    .font(.subheadline.weight(.medium))
                    .foregroundColor(.white)
                
                Text(payment.status.capitalized)
                    .font(.caption)
                    .foregroundColor(payment.status == "confirmed" ? .enlikoGreen : .enlikoYellow)
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(12)
    }
}

struct PaymentInvoiceSheet: View {
    let invoice: PaymentInvoice
    @Environment(\.dismiss) var dismiss
    @StateObject private var paymentService = PaymentService.shared
    @State private var isChecking = false
    @State private var statusMessage: String?
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        // QR Code
                        if let qrUrl = invoice.qrCodeUrl, let url = URL(string: qrUrl) {
                            AsyncImage(url: url) { image in
                                image
                                    .resizable()
                                    .scaledToFit()
                                    .frame(width: 200, height: 200)
                            } placeholder: {
                                ProgressView()
                                    .frame(width: 200, height: 200)
                            }
                            .background(Color.white)
                            .cornerRadius(12)
                        }
                        
                        // Amount
                        VStack(spacing: 8) {
                            Text("send_exactly".localized)
                                .font(.subheadline)
                                .foregroundColor(.enlikoTextSecondary)
                            
                            Text("\(invoice.amountCrypto, specifier: "%.6f") \(invoice.currency)")
                                .font(.title.bold())
                                .foregroundColor(.enlikoPrimary)
                            
                            Text("~$\(invoice.amountUsd, specifier: "%.0f")")
                                .font(.subheadline)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                        
                        // Address
                        VStack(spacing: 8) {
                            Text("to_address".localized)
                                .font(.subheadline)
                                .foregroundColor(.enlikoTextSecondary)
                            
                            Text(invoice.address)
                                .font(.system(.caption, design: .monospaced))
                                .foregroundColor(.white)
                                .padding()
                                .background(Color.enlikoCard)
                                .cornerRadius(8)
                            
                            Button(action: copyAddress) {
                                HStack {
                                    Image(systemName: "doc.on.doc")
                                    Text("copy_address".localized)
                                }
                                .font(.subheadline)
                                .foregroundColor(.enlikoPrimary)
                            }
                        }
                        
                        // Network
                        HStack {
                            Text("network".localized)
                                .foregroundColor(.enlikoTextSecondary)
                            Spacer()
                            Text(invoice.network)
                                .foregroundColor(.white)
                        }
                        .padding()
                        .background(Color.enlikoCard)
                        .cornerRadius(12)
                        
                        // Status
                        if let message = statusMessage {
                            Text(message)
                                .font(.subheadline)
                                .foregroundColor(.enlikoYellow)
                        }
                        
                        // Check button
                        Button(action: checkStatus) {
                            HStack {
                                if isChecking {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                } else {
                                    Image(systemName: "arrow.clockwise")
                                    Text("check_payment".localized)
                                }
                            }
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.enlikoPrimary)
                            .cornerRadius(16)
                        }
                        .disabled(isChecking)
                        
                        // Warning
                        VStack(spacing: 8) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.enlikoYellow)
                            Text("payment_warning".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                                .multilineTextAlignment(.center)
                        }
                        .padding()
                    }
                    .padding()
                }
            }
            .navigationTitle("payment_invoice".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("close".localized) {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func copyAddress() {
        UIPasteboard.general.string = invoice.address
        statusMessage = "address_copied".localized
    }
    
    private func checkStatus() {
        isChecking = true
        
        Task {
            do {
                let status = try await paymentService.checkPaymentStatus(paymentId: invoice.paymentId)
                
                await MainActor.run {
                    isChecking = false
                    if status.isConfirmed {
                        statusMessage = "✅ " + "payment_confirmed".localized
                    } else if status.isConfirming {
                        statusMessage = "⏳ " + "payment_confirming".localized
                    } else if status.isExpired {
                        statusMessage = "❌ " + "payment_expired".localized
                    } else {
                        statusMessage = "⏳ " + "payment_pending".localized
                    }
                }
            } catch {
                await MainActor.run {
                    isChecking = false
                    statusMessage = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
}

struct CurrencyPickerSheet: View {
    let currencies: [PaymentCurrency]
    @Binding var selectedCurrency: String
    @Binding var selectedNetwork: String
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                List {
                    ForEach(currencies) { currency in
                        Section(header: Text("\(currency.symbol) - \(currency.name)")) {
                            ForEach(currency.networks, id: \.self) { network in
                                Button(action: {
                                    selectedCurrency = currency.symbol
                                    selectedNetwork = network
                                    dismiss()
                                }) {
                                    HStack {
                                        Text(network)
                                            .foregroundColor(.white)
                                        Spacer()
                                        if selectedCurrency == currency.symbol && selectedNetwork == network {
                                            Image(systemName: "checkmark")
                                                .foregroundColor(.enlikoPrimary)
                                        }
                                    }
                                }
                            }
                        }
                        .listRowBackground(Color.enlikoCard)
                    }
                }
                .listStyle(.insetGrouped)
                .scrollContentBackground(.hidden)
            }
            .navigationTitle("select_currency".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("done".localized) {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    SubscriptionView()
        .environmentObject(AuthManager.shared)
        .preferredColorScheme(.dark)
}
