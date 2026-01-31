//
//  PaymentService.swift
//  EnlikoTrading
//
//  Crypto payment service for OxaPay integration
//

import Foundation
import Combine

// MARK: - Payment Models

struct PaymentPlan: Identifiable, Codable {
    let id = UUID()
    let name: String
    let displayName: String
    let features: [String]
    let prices: [String: Double]
    
    enum CodingKeys: String, CodingKey {
        case name, displayName = "display_name", features, prices
    }
}

struct PaymentCurrency: Identifiable, Codable {
    let id = UUID()
    let symbol: String
    let name: String
    let networks: [String]
    let minAmount: Double
    
    enum CodingKeys: String, CodingKey {
        case symbol, name, networks, minAmount = "min_amount"
    }
}

struct CreatePaymentRequest: Codable {
    let plan: String
    let duration: String
    let currency: String
    let network: String
    let promoCode: String?
    
    enum CodingKeys: String, CodingKey {
        case plan, duration, currency, network, promoCode = "promo_code"
    }
}

struct PaymentInvoice: Codable {
    let paymentId: String
    let address: String
    let amountUsd: Double
    let amountCrypto: Double
    let currency: String
    let network: String
    let expiresAt: String
    let status: String
    let qrCodeUrl: String?
    let discountPercent: Double?
    let originalAmount: Double?
    
    enum CodingKeys: String, CodingKey {
        case paymentId = "payment_id"
        case address
        case amountUsd = "amount_usd"
        case amountCrypto = "amount_crypto"
        case currency, network
        case expiresAt = "expires_at"
        case status
        case qrCodeUrl = "qr_code_url"
        case discountPercent = "discount_percent"
        case originalAmount = "original_amount"
    }
}

struct PaymentStatusResponse: Codable {
    let paymentId: String
    let status: String
    let amountUsd: Double
    let amountCrypto: Double
    let currency: String
    let txHash: String?
    let confirmedAt: String?
    let plan: String
    let duration: String
    
    enum CodingKeys: String, CodingKey {
        case paymentId = "payment_id"
        case status
        case amountUsd = "amount_usd"
        case amountCrypto = "amount_crypto"
        case currency
        case txHash = "tx_hash"
        case confirmedAt = "confirmed_at"
        case plan, duration
    }
    
    var isConfirmed: Bool { status == "confirmed" }
    var isPending: Bool { status == "pending" }
    var isExpired: Bool { status == "expired" }
    var isConfirming: Bool { status == "confirming" }
}

struct PromoCodeResponse: Codable {
    let valid: Bool
    let discountPercent: Double?
    let finalAmount: Double?
    let originalAmount: Double?
    let message: String
    
    enum CodingKeys: String, CodingKey {
        case valid
        case discountPercent = "discount_percent"
        case finalAmount = "final_amount"
        case originalAmount = "original_amount"
        case message
    }
}

struct PaymentHistoryItem: Identifiable, Codable {
    let id = UUID()
    let paymentId: String
    let amountUsd: Double
    let currency: String
    let status: String
    let plan: String
    let duration: String
    let createdAt: String
    let confirmedAt: String?
    
    enum CodingKeys: String, CodingKey {
        case paymentId = "payment_id"
        case amountUsd = "amount_usd"
        case currency, status, plan, duration
        case createdAt = "created_at"
        case confirmedAt = "confirmed_at"
    }
}

// MARK: - PaymentService

class PaymentService: ObservableObject {
    static let shared = PaymentService()
    
    @Published var plans: [PaymentPlan] = []
    @Published var currencies: [PaymentCurrency] = []
    @Published var currentInvoice: PaymentInvoice?
    @Published var paymentHistory: [PaymentHistoryItem] = []
    @Published var isLoading = false
    @Published var error: String?
    
    private let networkService = NetworkService.shared
    
    // MARK: - Fetch Plans
    
    func fetchPlans() async {
        await MainActor.run { isLoading = true }
        
        do {
            let fetchedPlans: [PaymentPlan] = try await networkService.get("/crypto/plans")
            await MainActor.run {
                self.plans = fetchedPlans
                self.isLoading = false
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
                self.isLoading = false
            }
        }
    }
    
    // MARK: - Fetch Currencies
    
    func fetchCurrencies() async {
        do {
            let fetched: [PaymentCurrency] = try await networkService.get("/crypto/currencies")
            await MainActor.run {
                self.currencies = fetched
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
        }
    }
    
    // MARK: - Create Payment
    
    func createPayment(plan: String, duration: String, currency: String, network: String, promoCode: String? = nil) async throws -> PaymentInvoice {
        let request = CreatePaymentRequest(
            plan: plan,
            duration: duration,
            currency: currency,
            network: network,
            promoCode: promoCode
        )
        
        let invoice: PaymentInvoice = try await networkService.post("/crypto/create", body: request)
        
        await MainActor.run {
            self.currentInvoice = invoice
        }
        
        return invoice
    }
    
    // MARK: - Check Payment Status
    
    func checkPaymentStatus(paymentId: String) async throws -> PaymentStatusResponse {
        let status: PaymentStatusResponse = try await networkService.get("/crypto/status/\(paymentId)")
        return status
    }
    
    // MARK: - Apply Promo Code
    
    func applyPromoCode(code: String, plan: String, duration: String) async throws -> PromoCodeResponse {
        struct PromoRequest: Codable {
            let code: String
            let plan: String
            let duration: String
        }
        
        let request = PromoRequest(code: code, plan: plan, duration: duration)
        let response: PromoCodeResponse = try await networkService.post("/crypto/apply-promo", body: request)
        return response
    }
    
    // MARK: - Fetch Payment History
    
    func fetchPaymentHistory() async {
        do {
            let history: [PaymentHistoryItem] = try await networkService.get("/crypto/history")
            await MainActor.run {
                self.paymentHistory = history
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
        }
    }
    
    // MARK: - Plan Pricing Helpers
    
    func getPrice(for plan: String, duration: String) -> Double? {
        guard let planData = plans.first(where: { $0.name == plan }) else { return nil }
        return planData.prices[duration]
    }
    
    func getPlanDisplayName(_ plan: String) -> String {
        plans.first(where: { $0.name == plan })?.displayName ?? plan.capitalized
    }
    
    func getDurationDisplayName(_ duration: String) -> String {
        switch duration {
        case "1m": return "1 month"
        case "3m": return "3 months"
        case "6m": return "6 months"
        case "1y": return "1 year"
        default: return duration
        }
    }
}
