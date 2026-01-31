//
//  SubscriptionView.swift
//  EnlikoTrading
//
//  Subscription view with ELC-only payment system
//  Users buy ELC tokens with USDT (via OxaPay), then pay subscription with ELC
//

import SwiftUI
import UIKit

struct SubscriptionView: View {
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var paymentService = PaymentService.shared
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var selectedPlan: String = "premium"
    @State private var selectedDuration: String = "1m"
    @State private var elcBalance: Double = 0
    @State private var isLoading = false
    @State private var showBuyELCSheet = false
    @State private var showPayConfirmation = false
    @State private var errorMessage: String?
    @State private var successMessage: String?
    
    // Price in ELC (1 ELC = 1 USD)
    var priceELC: Double {
        paymentService.getPrice(for: selectedPlan, duration: selectedDuration) ?? 0
    }
    
    var hasEnoughELC: Bool {
        elcBalance >= priceELC
    }
    
    var neededELC: Double {
        max(0, priceELC - elcBalance)
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        // ELC Balance Card
                        elcBalanceCard
                        
                        // Current subscription status
                        currentSubscriptionCard
                        
                        // Plan selection
                        planSelectionSection
                        
                        // Duration selection
                        durationSelectionSection
                        
                        // Price summary
                        priceSummaryCard
                        
                        // Action buttons
                        actionButtons
                        
                        // Error/Success messages
                        if let error = errorMessage {
                            Text(error)
                                .foregroundColor(.red)
                                .font(.caption)
                                .padding()
                        }
                        
                        if let success = successMessage {
                            Text(success)
                                .foregroundColor(.green)
                                .font(.caption)
                                .padding()
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("subscription".localized)
            .navigationBarTitleDisplayMode(.large)
            .sheet(isPresented: $showBuyELCSheet) {
                BuyELCSheet(
                    onDismiss: { showBuyELCSheet = false },
                    onPurchaseComplete: { amount in
                        elcBalance += amount
                        showBuyELCSheet = false
                    }
                )
            }
            .alert("confirm_payment".localized, isPresented: $showPayConfirmation) {
                Button("cancel".localized, role: .cancel) { }
                Button("pay".localized, role: .destructive) {
                    Task { await payWithELC() }
                }
            } message: {
                Text("pay_elc_confirm".localized.replacingOccurrences(of: "{amount}", with: String(format: "%.0f", priceELC)))
            }
            .onAppear {
                Task { await fetchELCBalance() }
            }
        }
    }
    
    // MARK: - ELC Balance Card
    
    private var elcBalanceCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "circle.hexagongrid.fill")
                    .font(.title2)
                    .foregroundColor(.enlikoPrimary)
                
                Text("elc_balance".localized)
                    .font(.headline)
                    .foregroundColor(.enlikoTextSecondary)
                
                Spacer()
                
                Button {
                    showBuyELCSheet = true
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: "plus.circle.fill")
                        Text("buy".localized)
                    }
                    .font(.subheadline.weight(.medium))
                    .foregroundColor(.enlikoPrimary)
                }
            }
            
            Text("\(Int(elcBalance)) ELC")
                .font(.system(size: 36, weight: .bold))
                .foregroundColor(.white)
            
            Text("≈ $\(Int(elcBalance))")
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.enlikoCard)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.enlikoPrimary.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Current Subscription Card
    
    private var currentSubscriptionCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "crown.fill")
                    .foregroundColor(.enlikoSecondary)
                
                Text("current_plan".localized)
                    .font(.headline)
                
                Spacer()
                
                Text(authManager.currentUser?.subscriptionPlan ?? "Free")
                    .font(.headline)
                    .foregroundColor(.enlikoPrimary)
            }
            
            if let expires = authManager.currentUser?.subscriptionExpires {
                HStack {
                    Text("expires".localized)
                        .foregroundColor(.enlikoTextSecondary)
                    Spacer()
                    Text(expires)
                        .foregroundColor(.enlikoTextSecondary)
                }
                .font(.subheadline)
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(12)
    }
    
    // MARK: - Plan Selection
    
    private var planSelectionSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("select_plan".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                PlanCard(
                    name: "Basic",
                    description: "Essential trading features",
                    price: getBasePrice("basic"),
                    features: ["3 strategies", "Demo trading", "Email support"],
                    isSelected: selectedPlan == "basic",
                    action: { selectedPlan = "basic" }
                )
                
                PlanCard(
                    name: "Premium",
                    description: "Advanced trading tools",
                    price: getBasePrice("premium"),
                    features: ["All strategies", "Real trading", "Priority support", "API access"],
                    isSelected: selectedPlan == "premium",
                    action: { selectedPlan = "premium" }
                )
                
                PlanCard(
                    name: "Pro",
                    description: "Full platform access",
                    price: getBasePrice("pro"),
                    features: ["Everything in Premium", "Custom strategies", "Dedicated support", "White-label"],
                    isSelected: selectedPlan == "pro",
                    action: { selectedPlan = "pro" }
                )
            }
        }
    }
    
    // MARK: - Duration Selection
    
    private var durationSelectionSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("select_duration".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            HStack(spacing: 12) {
                DurationButton(
                    label: "1M",
                    discount: nil,
                    isSelected: selectedDuration == "1m",
                    action: { selectedDuration = "1m" }
                )
                
                DurationButton(
                    label: "3M",
                    discount: "10%",
                    isSelected: selectedDuration == "3m",
                    action: { selectedDuration = "3m" }
                )
                
                DurationButton(
                    label: "6M",
                    discount: "20%",
                    isSelected: selectedDuration == "6m",
                    action: { selectedDuration = "6m" }
                )
                
                DurationButton(
                    label: "1Y",
                    discount: "30%",
                    isSelected: selectedDuration == "1y",
                    action: { selectedDuration = "1y" }
                )
            }
        }
    }
    
    // MARK: - Price Summary
    
    private var priceSummaryCard: some View {
        VStack(spacing: 16) {
            HStack {
                Text("price".localized)
                    .foregroundColor(.enlikoTextSecondary)
                Spacer()
                Text("\(Int(priceELC)) ELC")
                    .font(.title2.weight(.bold))
                    .foregroundColor(.white)
            }
            
            HStack {
                Text("your_balance".localized)
                    .foregroundColor(.enlikoTextSecondary)
                Spacer()
                Text("\(Int(elcBalance)) ELC")
                    .foregroundColor(hasEnoughELC ? .enlikoGreen : .enlikoRed)
            }
            
            if !hasEnoughELC {
                HStack {
                    Text("need_more".localized)
                        .foregroundColor(.enlikoTextSecondary)
                    Spacer()
                    Text("\(Int(neededELC)) ELC")
                        .foregroundColor(.enlikoRed)
                        .fontWeight(.medium)
                }
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(12)
    }
    
    // MARK: - Action Buttons
    
    private var actionButtons: some View {
        VStack(spacing: 12) {
            if hasEnoughELC {
                Button {
                    showPayConfirmation = true
                } label: {
                    HStack {
                        if isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Image(systemName: "checkmark.circle.fill")
                            Text("pay_with_elc".localized)
                        }
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.enlikoGreen)
                    .cornerRadius(12)
                }
                .disabled(isLoading)
            } else {
                Button {
                    showBuyELCSheet = true
                } label: {
                    HStack {
                        Image(systemName: "cart.fill")
                        Text("buy_elc_to_pay".localized)
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.enlikoPrimary)
                    .cornerRadius(12)
                }
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func getBasePrice(_ plan: String) -> Int {
        switch plan {
        case "basic": return 50
        case "premium": return 100
        case "pro": return 500
        default: return 0
        }
    }
    
    private func fetchELCBalance() async {
        do {
            let balance = try await paymentService.fetchELCBalance()
            await MainActor.run {
                self.elcBalance = balance
            }
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
            }
        }
    }
    
    private func payWithELC() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let result = try await paymentService.payWithELC(plan: selectedPlan, duration: selectedDuration)
            await MainActor.run {
                isLoading = false
                if result.success {
                    successMessage = result.message ?? "subscription_activated".localized
                    elcBalance = result.newBalance ?? elcBalance
                } else {
                    errorMessage = result.message ?? "payment_failed".localized
                }
            }
        } catch {
            await MainActor.run {
                isLoading = false
                errorMessage = error.localizedDescription
            }
        }
    }
}

// MARK: - Buy ELC Sheet

struct BuyELCSheet: View {
    let onDismiss: () -> Void
    let onPurchaseComplete: (Double) -> Void
    
    @StateObject private var paymentService = PaymentService.shared
    @State private var selectedAmount: Int = 100
    @State private var currentInvoice: ELCPurchaseInvoice?
    @State private var isLoading = false
    @State private var paymentStatus: String = "pending"
    @State private var errorMessage: String?
    
    let amounts = [50, 100, 200, 500]
    
    var elcAmount: Double {
        Double(selectedAmount) * 0.995  // 0.5% fee
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        if let invoice = currentInvoice {
                            // Show payment details
                            PaymentDetailsView(
                                invoice: invoice,
                                paymentStatus: paymentStatus,
                                onCheckStatus: checkPaymentStatus
                            )
                        } else {
                            // Amount selection
                            VStack(alignment: .leading, spacing: 16) {
                                Text("select_amount".localized)
                                    .font(.headline)
                                    .foregroundColor(.white)
                                
                                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                                    ForEach(amounts, id: \.self) { amount in
                                        AmountButton(
                                            amount: amount,
                                            isSelected: selectedAmount == amount,
                                            action: { selectedAmount = amount }
                                        )
                                    }
                                }
                            }
                            
                            // Summary
                            VStack(spacing: 12) {
                                HStack {
                                    Text("you_pay".localized)
                                        .foregroundColor(.enlikoTextSecondary)
                                    Spacer()
                                    Text("\(selectedAmount) USDT")
                                        .fontWeight(.bold)
                                        .foregroundColor(.white)
                                }
                                
                                HStack {
                                    Text("you_get".localized)
                                        .foregroundColor(.enlikoTextSecondary)
                                    Spacer()
                                    Text(String(format: "%.2f ELC", elcAmount))
                                        .fontWeight(.bold)
                                        .foregroundColor(.enlikoGreen)
                                }
                                
                                HStack {
                                    Text("fee".localized)
                                        .foregroundColor(.enlikoTextSecondary)
                                    Spacer()
                                    Text("0.5%")
                                        .foregroundColor(.enlikoTextSecondary)
                                }
                            }
                            .padding()
                            .background(Color.enlikoCard)
                            .cornerRadius(12)
                            
                            // Buy button
                            Button {
                                Task { await createPurchase() }
                            } label: {
                                HStack {
                                    if isLoading {
                                        ProgressView()
                                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    } else {
                                        Image(systemName: "cart.fill")
                                        Text("buy_elc".localized)
                                    }
                                }
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.enlikoPrimary)
                                .cornerRadius(12)
                            }
                            .disabled(isLoading)
                        }
                        
                        if let error = errorMessage {
                            Text(error)
                                .foregroundColor(.red)
                                .font(.caption)
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("buy_elc".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("close".localized) {
                        onDismiss()
                    }
                }
            }
        }
    }
    
    private func createPurchase() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let invoice = try await paymentService.createELCPurchase(amount: Double(selectedAmount))
            await MainActor.run {
                self.currentInvoice = invoice
                isLoading = false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
    
    private func checkPaymentStatus() async {
        guard let paymentId = currentInvoice?.paymentId else { return }
        
        do {
            let response = try await paymentService.checkELCPaymentStatus(paymentId: paymentId)
            await MainActor.run {
                paymentStatus = response.status
                if response.status == "confirmed" {
                    onPurchaseComplete(currentInvoice?.elcAmount ?? elcAmount)
                }
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
        }
    }
}

// MARK: - Payment Details View

struct PaymentDetailsView: View {
    let invoice: ELCPurchaseInvoice
    let paymentStatus: String
    let onCheckStatus: () async -> Void
    
    @State private var isChecking = false
    
    var address: String {
        invoice.address ?? "Loading..."
    }
    
    var body: some View {
        VStack(spacing: 20) {
            // Status indicator
            VStack(spacing: 8) {
                Image(systemName: statusIcon)
                    .font(.system(size: 48))
                    .foregroundColor(statusColor)
                
                Text(statusText)
                    .font(.headline)
                    .foregroundColor(statusColor)
            }
            .padding()
            
            // Amount
            VStack(spacing: 4) {
                Text("send_exactly".localized)
                    .foregroundColor(.enlikoTextSecondary)
                
                Text("\(Int(invoice.amountUSD ?? 0)) USDT")
                    .font(.title.weight(.bold))
                    .foregroundColor(.white)
                
                Text("TRC20 Network")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            // Address
            VStack(spacing: 8) {
                Text("to_address".localized)
                    .foregroundColor(.enlikoTextSecondary)
                
                HStack {
                    Text(address)
                        .font(.system(.caption, design: .monospaced))
                        .foregroundColor(.white)
                        .lineLimit(1)
                        .truncationMode(.middle)
                    
                    Button {
                        UIPasteboard.general.string = address
                    } label: {
                        Image(systemName: "doc.on.doc")
                            .foregroundColor(.enlikoPrimary)
                    }
                }
                .padding()
                .background(Color.enlikoCard)
                .cornerRadius(8)
            }
            
            // Check status button
            if paymentStatus != "confirmed" {
                Button {
                    Task {
                        isChecking = true
                        await onCheckStatus()
                        isChecking = false
                    }
                } label: {
                    HStack {
                        if isChecking {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Image(systemName: "arrow.clockwise")
                            Text("check_status".localized)
                        }
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.enlikoBlue)
                    .cornerRadius(12)
                }
                .disabled(isChecking)
            }
            
            // You will receive
            HStack {
                Text("you_will_receive".localized)
                    .foregroundColor(.enlikoTextSecondary)
                Spacer()
                Text(String(format: "%.2f ELC", invoice.elcAmount ?? 0))
                    .fontWeight(.bold)
                    .foregroundColor(.enlikoGreen)
            }
            .padding()
            .background(Color.enlikoCard)
            .cornerRadius(8)
        }
    }
    
    private var statusIcon: String {
        switch paymentStatus {
        case "confirmed": return "checkmark.circle.fill"
        case "pending": return "clock.fill"
        default: return "exclamationmark.circle.fill"
        }
    }
    
    private var statusColor: Color {
        switch paymentStatus {
        case "confirmed": return .enlikoGreen
        case "pending": return .enlikoYellow
        default: return .enlikoRed
        }
    }
    
    private var statusText: String {
        switch paymentStatus {
        case "confirmed": return "payment_confirmed".localized
        case "pending": return "awaiting_payment".localized
        default: return "payment_status".localized
        }
    }
}

// MARK: - Plan Card

struct PlanCard: View {
    let name: String
    let description: String
    let price: Int
    let features: [String]
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button {
            action()
        } label: {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(name)
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Text("\(price) ELC/mo")
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(.enlikoPrimary)
                }
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                
                ForEach(features, id: \.self) { feature in
                    HStack(spacing: 4) {
                        Image(systemName: "checkmark.circle.fill")
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
        .buttonStyle(.plain)
    }
}

// MARK: - Duration Button

struct DurationButton: View {
    let label: String
    let discount: String?
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button {
            action()
        } label: {
            VStack(spacing: 4) {
                Text(label)
                    .font(.subheadline.weight(.medium))
                    .foregroundColor(.white)
                
                if let discount = discount {
                    Text("-\(discount)")
                        .font(.caption2)
                        .foregroundColor(.enlikoGreen)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(isSelected ? Color.enlikoPrimary : Color.enlikoCard)
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Amount Button

struct AmountButton: View {
    let amount: Int
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button {
            action()
        } label: {
            VStack(spacing: 4) {
                Text("\(amount) USDT")
                    .font(.headline)
                    .foregroundColor(.white)
                
                Text("≈ \(Int(Double(amount) * 0.995)) ELC")
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? Color.enlikoPrimary : Color.enlikoCard)
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Preview

#Preview {
    SubscriptionView()
        .environmentObject(AuthManager.shared)
}
