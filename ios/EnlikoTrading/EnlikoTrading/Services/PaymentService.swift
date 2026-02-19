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
    let name: String?
    let displayName: String?
    let features: [String]?
    let prices: [String: Double]?
    
    var nameValue: String { name ?? "" }
    var displayNameValue: String { displayName ?? nameValue.capitalized }
    var featuresList: [String] { features ?? [] }
    var pricesMap: [String: Double] { prices ?? [:] }
    
    enum CodingKeys: String, CodingKey {
        case name, displayName = "display_name", features, prices
    }
}

struct PaymentCurrency: Identifiable, Codable {
    let id = UUID()
    let symbol: String?
    let name: String?
    let networks: [String]?
    let minAmount: Double?
    
    var symbolValue: String { symbol ?? "USDT" }
    var nameValue: String { name ?? symbolValue }
    var networksList: [String] { networks ?? [] }
    var minAmountValue: Double { minAmount ?? 5.0 }
    
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
    let paymentId: String?
    let address: String?
    let amountUsd: Double?
    let amountCrypto: Double?
    let currency: String?
    let network: String?
    let expiresAt: String?
    let status: String?
    let qrCodeUrl: String?
    let discountPercent: Double?
    let originalAmount: Double?
    
    var paymentIdValue: String { paymentId ?? "" }
    var addressValue: String { address ?? "" }
    var amountUsdValue: Double { amountUsd ?? 0 }
    var amountCryptoValue: Double { amountCrypto ?? 0 }
    var currencyValue: String { currency ?? "USDT" }
    var networkValue: String { network ?? "TRC20" }
    var expiresAtValue: String { expiresAt ?? "" }
    var statusValue: String { status ?? "pending" }
    
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
    let paymentId: String?
    let status: String?
    let amountUsd: Double?
    let amountCrypto: Double?
    let currency: String?
    let txHash: String?
    let confirmedAt: String?
    let plan: String?
    let duration: String?
    
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
    
    // Safe accessors
    var statusValue: String { status ?? "unknown" }
    var amountUsdValue: Double { amountUsd ?? 0 }
    var amountCryptoValue: Double { amountCrypto ?? 0 }
    var currencyValue: String { currency ?? "USDT" }
    var planValue: String { plan ?? "" }
    var durationValue: String { duration ?? "" }
    
    var isConfirmed: Bool { statusValue == "confirmed" }
    var isPending: Bool { statusValue == "pending" }
    var isExpired: Bool { statusValue == "expired" }
    var isConfirming: Bool { status == "confirming" }
}

struct PromoCodeResponse: Codable {
    let valid: Bool?
    let discountPercent: Double?
    let finalAmount: Double?
    let originalAmount: Double?
    let message: String?
    
    var isValid: Bool { valid ?? false }
    var messageValue: String { message ?? "" }
    
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
    let paymentId: String?
    let amountUsd: Double?
    let currency: String?
    let status: String?
    let plan: String?
    let duration: String?
    let createdAt: String?
    let confirmedAt: String?
    
    var paymentIdValue: String { paymentId ?? "" }
    var amountUsdValue: Double { amountUsd ?? 0 }
    var currencyValue: String { currency ?? "USDT" }
    var statusValue: String { status ?? "unknown" }
    var planValue: String { plan ?? "" }
    var durationValue: String { duration ?? "" }
    var createdAtValue: String { createdAt ?? "" }
    
    enum CodingKeys: String, CodingKey {
        case paymentId = "payment_id"
        case amountUsd = "amount_usd"
        case currency, status, plan, duration
        case createdAt = "created_at"
        case confirmedAt = "confirmed_at"
    }
}

// MARK: - PaymentService

@MainActor
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
    
    // Default prices in ELC (synced with server LICENSE_PRICES)
    private let defaultPrices: [String: [String: Double]] = [
        "basic": ["1m": 50, "3m": 135, "6m": 240, "1y": 420],
        "premium": ["1m": 100, "3m": 270, "6m": 480, "1y": 840],
        "pro": ["1m": 500, "3m": 1350, "6m": 2400, "1y": 4200]
    ]
    
    func getPrice(for plan: String, duration: String) -> Double? {
        // Try from loaded plans first
        if let planData = plans.first(where: { $0.nameValue == plan }),
           let price = planData.pricesMap[duration] {
            return price
        }
        // Fallback to default prices
        return defaultPrices[plan]?[duration]
    }
    
    func getPlanDisplayName(_ plan: String) -> String {
        plans.first(where: { $0.nameValue == plan })?.displayNameValue ?? plan.capitalized
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
    
    // MARK: - ELC Balance
    
    func fetchELCBalance() async throws -> Double {
        struct BalanceResponse: Codable {
            let available: Double?
            let staked: Double?
            let total: Double?
        }
        
        let response: BalanceResponse = try await networkService.get(Config.Endpoints.elcBalance)
        return response.available ?? 0
    }
    
    // MARK: - Create ELC Purchase
    
    func createELCPurchase(amount: Double) async throws -> ELCPurchaseInvoice {
        struct PurchaseRequest: Codable {
            let amount: Double
        }
        
        let request = PurchaseRequest(amount: amount)
        let invoice: ELCPurchaseInvoice = try await networkService.post(Config.Endpoints.elcBuyUsdt, body: request)
        return invoice
    }
    
    // MARK: - Check ELC Payment Status
    
    func checkELCPaymentStatus(paymentId: String) async throws -> ELCPaymentStatusResponse {
        let response: ELCPaymentStatusResponse = try await networkService.get("\(Config.Endpoints.elcPaymentStatus)/\(paymentId)")
        return response
    }
    
    // MARK: - Pay with ELC
    
    func payWithELC(plan: String, duration: String) async throws -> ELCPaymentResult {
        struct PayRequest: Codable {
            let plan: String
            let duration: String
        }
        
        let request = PayRequest(plan: plan, duration: duration)
        let result: ELCPaymentResult = try await networkService.post(Config.Endpoints.elcPayWithELC, body: request)
        return result
    }
}

// MARK: - ELC Models

struct ELCPurchaseInvoice: Codable {
    let success: Bool?
    let paymentId: String?
    let address: String?
    
    var isSuccess: Bool { success ?? false }
    var paymentIdValue: String { paymentId ?? "" }
    let amountUSD: Double?
    let elcAmount: Double?
    let fee: Double?
    let feePercent: Double?
    let currency: String?
    let network: String?
    let expiresAt: String?
    let qrCodeUrl: String?
    let instructions: [String]?
}

struct ELCPaymentStatusResponse: Codable {
    let paymentId: String?
    let status: String?
    let amountUSD: Double?
    
    var paymentIdValue: String { paymentId ?? "" }
    var statusValue: String { status ?? "unknown" }
    let elcAmount: Double?
    let currency: String?
    let network: String?
    let address: String?
    let createdAt: String?
    let confirmedAt: String?
}

struct ELCPaymentResult: Codable {
    let success: Bool?
    let subscriptionActivated: Bool?
    
    var isSuccess: Bool { success ?? false }
    let plan: String?
    let duration: String?
    let elcPaid: Double?
    let newBalance: Double?
    let expiresInDays: Int?
    let message: String?
    let error: String?
    let required: Double?
    let available: Double?
    let shortfall: Double?
}
