//
//  SpotService.swift
//  EnlikoTrading
//
//  Spot trading service with portfolios, DCA strategies, and performance tracking
//

import Foundation
import Combine

// MARK: - Models

struct SpotPortfolio: Codable, Identifiable {
    let id: String
    let name: String
    let emoji: String
    let coins: [String: Int]
    let riskLevel: String
    
    enum CodingKeys: String, CodingKey {
        case id, name, emoji, coins
        case riskLevel = "risk_level"
    }
    
    var riskColor: String {
        switch riskLevel {
        case "low": return "green"
        case "medium": return "yellow"
        case "high": return "orange"
        case "very_high": return "red"
        default: return "gray"
        }
    }
}

struct DCAStrategy: Codable, Identifiable {
    let id: String
    let name: String
    let emoji: String
    let description: String
}

struct TPProfile: Codable, Identifiable {
    let id: String
    let name: String
    let emoji: String
    let levels: [TPLevel]
}

struct TPLevel: Codable {
    let gainPct: Double
    let sellPct: Double
    
    enum CodingKeys: String, CodingKey {
        case gainPct = "gain_pct"
        case sellPct = "sell_pct"
    }
}

struct SpotHolding: Codable, Identifiable {
    var id: String { coin ?? "unknown" }
    let coin: String?
    let balance: Double?
    let usdValue: Double?
    let avgPrice: Double?
    let totalCost: Double?
    let unrealizedPnl: Double?
    let pnlPct: Double?
    
    // Safe accessors
    var coinName: String { coin ?? "?" }
    var balanceValue: Double { balance ?? 0 }
    var usdValueAmount: Double { usdValue ?? 0 }
    var avgPriceValue: Double { avgPrice ?? 0 }
    var totalCostValue: Double { totalCost ?? 0 }
    var unrealizedPnlValue: Double { unrealizedPnl ?? 0 }
    var pnlPctValue: Double { pnlPct ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case coin, balance
        case usdValue = "usd_value"
        case avgPrice = "avg_price"
        case totalCost = "total_cost"
        case unrealizedPnl = "unrealized_pnl"
        case pnlPct = "pnl_pct"
    }
}

struct SpotPerformance: Codable {
    let success: Bool?
    let totalInvested: Double?
    let totalCurrentValue: Double?
    let totalUnrealizedPnl: Double?
    let roiPct: Double?
    let holdings: [SpotHolding]?
    let holdingsCount: Int?
    
    // Safe accessors
    var isSuccess: Bool { success ?? false }
    var totalInvestedValue: Double { totalInvested ?? 0 }
    var totalCurrentValueAmount: Double { totalCurrentValue ?? 0 }
    var totalUnrealizedPnlValue: Double { totalUnrealizedPnl ?? 0 }
    var roiPctValue: Double { roiPct ?? 0 }
    var holdingsList: [SpotHolding] { holdings ?? [] }
    var holdingsCountValue: Int { holdingsCount ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case success
        case totalInvested = "total_invested"
        case totalCurrentValue = "total_current_value"
        case totalUnrealizedPnl = "total_unrealized_pnl"
        case roiPct = "roi_pct"
        case holdings
        case holdingsCount = "holdings_count"
    }
}

struct SpotBalance: Codable {
    let success: Bool
    let usdtBalance: Double?
    let holdings: [SpotBalanceItem]?
    let totalValue: Double?
    
    enum CodingKeys: String, CodingKey {
        case success
        case usdtBalance = "usdt_balance"
        case holdings
        case totalValue = "total_value"
    }
}

struct SpotBalanceItem: Codable, Identifiable {
    var id: String { coin }
    let coin: String
    let balance: Double
    let usdValue: Double
    
    enum CodingKeys: String, CodingKey {
        case coin, balance
        case usdValue = "usd_value"
    }
}

struct FearGreedIndex: Codable {
    let success: Bool
    let value: Int?
    let classification: String?
    let timestamp: String?
}

struct SpotSettings: Codable {
    let dcaEnabled: Bool?
    let dcaAmount: Double?
    let dcaFrequency: String?
    let dcaStrategy: String?
    let portfolio: String?
    let tpEnabled: Bool?
    let tpProfile: String?
    let trailingTpEnabled: Bool?
    let trailingActivationPct: Double?
    let trailingTrailPct: Double?
    let profitLockEnabled: Bool?
    let profitLockTriggerPct: Double?
    let profitLockPct: Double?
    let smartRebalanceEnabled: Bool?
    let rebalanceThresholdPct: Double?
    
    // Safe accessors
    var dcaEnabledValue: Bool { dcaEnabled ?? false }
    var dcaAmountValue: Double { dcaAmount ?? 10 }
    var dcaFrequencyValue: String { dcaFrequency ?? "daily" }
    var dcaStrategyValue: String { dcaStrategy ?? "fixed" }
    var portfolioValue: String { portfolio ?? "custom" }
    var tpEnabledValue: Bool { tpEnabled ?? false }
    var tpProfileValue: String { tpProfile ?? "balanced" }
    var trailingTpEnabledValue: Bool { trailingTpEnabled ?? false }
    var trailingActivationPctValue: Double { trailingActivationPct ?? 15 }
    var trailingTrailPctValue: Double { trailingTrailPct ?? 5 }
    var profitLockEnabledValue: Bool { profitLockEnabled ?? false }
    var profitLockTriggerPctValue: Double { profitLockTriggerPct ?? 30 }
    var profitLockPctValue: Double { profitLockPct ?? 50 }
    var smartRebalanceEnabledValue: Bool { smartRebalanceEnabled ?? false }
    var rebalanceThresholdPctValue: Double { rebalanceThresholdPct ?? 10 }
    
    enum CodingKeys: String, CodingKey {
        case dcaEnabled = "dca_enabled"
        case dcaAmount = "dca_amount"
        case dcaFrequency = "dca_frequency"
        case dcaStrategy = "dca_strategy"
        case portfolio
        case tpEnabled = "tp_enabled"
        case tpProfile = "tp_profile"
        case trailingTpEnabled = "trailing_tp_enabled"
        case trailingActivationPct = "trailing_activation_pct"
        case trailingTrailPct = "trailing_trail_pct"
        case profitLockEnabled = "profit_lock_enabled"
        case profitLockTriggerPct = "profit_lock_trigger_pct"
        case profitLockPct = "profit_lock_pct"
        case smartRebalanceEnabled = "smart_rebalance_enabled"
        case rebalanceThresholdPct = "rebalance_threshold_pct"
    }
    
    static var `default`: SpotSettings {
        SpotSettings(
            dcaEnabled: false,
            dcaAmount: 10,
            dcaFrequency: "daily",
            dcaStrategy: "fixed",
            portfolio: "custom",
            tpEnabled: false,
            tpProfile: "balanced",
            trailingTpEnabled: false,
            trailingActivationPct: 15,
            trailingTrailPct: 5,
            profitLockEnabled: false,
            profitLockTriggerPct: 30,
            profitLockPct: 50,
            smartRebalanceEnabled: false,
            rebalanceThresholdPct: 10
        )
    }
}

// MARK: - Service

@MainActor
class SpotService: ObservableObject {
    static let shared = SpotService()
    
    @Published var portfolios: [String: SpotPortfolio] = [:]
    @Published var strategies: [String: DCAStrategy] = [:]
    @Published var tpProfiles: [String: TPProfile] = [:]
    @Published var performance: SpotPerformance?
    @Published var balance: SpotBalance?
    @Published var fearGreed: FearGreedIndex?
    @Published var settings: SpotSettings = .default
    @Published var isLoading = false
    @Published var error: String?
    
    private let network = NetworkService.shared
    
    // MARK: - Fetch Portfolios
    
    func fetchPortfolios() async {
        await MainActor.run { isLoading = true }
        
        do {
            let response: PortfoliosResponse = try await network.get("/spot/portfolios")
            await MainActor.run {
                if response.success {
                    self.portfolios = response.portfolios.mapValues { dict in
                        SpotPortfolio(
                            id: dict["id"] as? String ?? "",
                            name: dict["name"] as? String ?? "",
                            emoji: dict["emoji"] as? String ?? "📊",
                            coins: dict["coins"] as? [String: Int] ?? [:],
                            riskLevel: dict["risk_level"] as? String ?? "medium"
                        )
                    }
                }
                isLoading = false
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
                isLoading = false
            }
        }
    }
    
    // MARK: - Fetch Strategies
    
    func fetchStrategies() async {
        do {
            let response: StrategiesResponse = try await network.get("/spot/strategies")
            await MainActor.run {
                if response.success {
                    self.strategies = response.strategies.mapValues { dict in
                        DCAStrategy(
                            id: dict["id"] as? String ?? "",
                            name: dict["name"] as? String ?? "",
                            emoji: dict["emoji"] as? String ?? "📊",
                            description: dict["description"] as? String ?? ""
                        )
                    }
                }
            }
        } catch {
            AppLogger.shared.error("Failed to fetch strategies: \(error)", category: .network)
        }
    }
    
    // MARK: - Fetch TP Profiles
    
    func fetchTPProfiles() async {
        do {
            let response: TPProfilesResponse = try await network.get("/spot/tp-profiles")
            await MainActor.run {
                if response.success {
                    self.tpProfiles = response.profiles.mapValues { dict in
                        let levelsArray = dict["levels"] as? [[String: Any]] ?? []
                        let levels = levelsArray.compactMap { level -> TPLevel? in
                            guard let gain = level["gain_pct"] as? Double,
                                  let sell = level["sell_pct"] as? Double else { return nil }
                            return TPLevel(gainPct: gain, sellPct: sell)
                        }
                        return TPProfile(
                            id: dict["id"] as? String ?? "",
                            name: dict["name"] as? String ?? "",
                            emoji: dict["emoji"] as? String ?? "🎯",
                            levels: levels
                        )
                    }
                }
            }
        } catch {
            AppLogger.shared.error("Failed to fetch TP profiles: \(error)", category: .network)
        }
    }
    
    // MARK: - Fetch Performance
    
    func fetchPerformance(accountType: String = "demo") async {
        await MainActor.run { isLoading = true }
        
        do {
            let response: SpotPerformance = try await network.get("/spot/performance?account_type=\(accountType)")
            await MainActor.run {
                self.performance = response
                isLoading = false
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
                isLoading = false
            }
        }
    }
    
    // MARK: - Fetch Balance
    
    func fetchBalance(accountType: String = "demo") async {
        do {
            let response: SpotBalance = try await network.get("/spot/balance?account_type=\(accountType)")
            await MainActor.run {
                self.balance = response
            }
        } catch {
            AppLogger.shared.error("Failed to fetch spot balance: \(error)", category: .network)
        }
    }
    
    // MARK: - Fetch Fear & Greed
    
    func fetchFearGreed() async {
        do {
            let response: FearGreedIndex = try await network.get("/spot/fear-greed")
            await MainActor.run {
                self.fearGreed = response
            }
        } catch {
            AppLogger.shared.error("Failed to fetch Fear & Greed: \(error)", category: .network)
        }
    }
    
    // MARK: - Execute DCA
    
    func executeDCA(coin: String, amount: Double, strategy: String, accountType: String = "demo") async -> Bool {
        do {
            let body = DCAExecuteRequest(coin: coin, amount: amount, strategy: strategy)
            let _: GenericResponse = try await network.post("/spot/execute-dca?account_type=\(accountType)", body: body)
            await fetchPerformance(accountType: accountType)
            return true
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
            return false
        }
    }
    
    // MARK: - Rebalance Portfolio
    
    func rebalancePortfolio(portfolio: String, investment: Double, accountType: String = "demo") async -> Bool {
        do {
            let body = RebalanceRequest(portfolio: portfolio, totalInvestment: investment)
            let _: GenericResponse = try await network.post("/spot/rebalance?account_type=\(accountType)", body: body)
            await fetchPerformance(accountType: accountType)
            return true
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
            return false
        }
    }
    
    // MARK: - Update Settings
    
    func updateSettings(_ settings: SpotSettings, accountType: String = "demo") async -> Bool {
        do {
            let body = SpotSettingsUpdateRequest(
                dcaEnabled: settings.dcaEnabledValue,
                dcaAmount: settings.dcaAmountValue,
                dcaFrequency: settings.dcaFrequencyValue,
                dcaStrategy: settings.dcaStrategyValue,
                portfolio: settings.portfolioValue,
                tpEnabled: settings.tpEnabledValue,
                tpProfile: settings.tpProfileValue,
                trailingTpEnabled: settings.trailingTpEnabledValue,
                trailingActivationPct: settings.trailingActivationPctValue,
                trailingTrailPct: settings.trailingTrailPctValue,
                profitLockEnabled: settings.profitLockEnabledValue,
                profitLockTriggerPct: settings.profitLockTriggerPctValue,
                profitLockPct: settings.profitLockPctValue,
                smartRebalanceEnabled: settings.smartRebalanceEnabledValue,
                rebalanceThresholdPct: settings.rebalanceThresholdPctValue
            )
            let _: GenericResponse = try await network.post("/spot/settings?account_type=\(accountType)", body: body)
            await MainActor.run {
                self.settings = settings
            }
            return true
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
            return false
        }
    }
    
    // MARK: - Buy Spot
    
    func buySpot(coin: String, amount: Double, accountType: String = "demo") async -> Bool {
        do {
            let body = SpotBuyRequest(coin: coin, amount: amount)
            let _: GenericResponse = try await network.post("/spot/buy?account_type=\(accountType)", body: body)
            HapticManager.shared.perform(.success)
            await fetchBalance(accountType: accountType)
            return true
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
            HapticManager.shared.perform(.error)
            return false
        }
    }
    
    // MARK: - Sell Spot
    
    func sellSpot(coin: String, percentage: Double, accountType: String = "demo") async -> Bool {
        do {
            let body = SpotSellRequest(coin: coin, percentage: percentage)
            let _: GenericResponse = try await network.post("/spot/sell?account_type=\(accountType)", body: body)
            HapticManager.shared.perform(.success)
            await fetchBalance(accountType: accountType)
            return true
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
            HapticManager.shared.perform(.error)
            return false
        }
    }
}

// MARK: - Response Types

private struct PortfoliosResponse: Codable {
    let success: Bool
    let portfolios: [String: [String: Any]]
    let count: Int
    
    enum CodingKeys: String, CodingKey {
        case success, portfolios, count
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        success = try container.decode(Bool.self, forKey: .success)
        count = try container.decode(Int.self, forKey: .count)
        
        // Decode portfolios as dynamic dictionary
        let portfoliosContainer = try container.decode([String: PortfolioDict].self, forKey: .portfolios)
        portfolios = portfoliosContainer.mapValues { $0.asDictionary }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(success, forKey: .success)
        try container.encode(count, forKey: .count)
    }
}

private struct PortfolioDict: Codable {
    let name: String
    let emoji: String?
    let coins: [String: Int]
    let risk_level: String?
    
    var asDictionary: [String: Any] {
        var dict: [String: Any] = [
            "name": name,
            "coins": coins
        ]
        if let emoji = emoji { dict["emoji"] = emoji }
        if let risk = risk_level { dict["risk_level"] = risk }
        return dict
    }
}

private struct StrategiesResponse: Codable {
    let success: Bool
    let strategies: [String: [String: Any]]
    let count: Int
    
    enum CodingKeys: String, CodingKey {
        case success, strategies, count
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        success = try container.decode(Bool.self, forKey: .success)
        count = try container.decode(Int.self, forKey: .count)
        
        let strategiesContainer = try container.decode([String: StrategyDict].self, forKey: .strategies)
        strategies = strategiesContainer.mapValues { $0.asDictionary }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(success, forKey: .success)
        try container.encode(count, forKey: .count)
    }
}

private struct StrategyDict: Codable {
    let name: String
    let emoji: String?
    let description: String?
    
    var asDictionary: [String: Any] {
        var dict: [String: Any] = ["name": name]
        if let emoji = emoji { dict["emoji"] = emoji }
        if let desc = description { dict["description"] = desc }
        return dict
    }
}

private struct TPProfilesResponse: Codable {
    let success: Bool
    let profiles: [String: [String: Any]]
    let count: Int
    
    enum CodingKeys: String, CodingKey {
        case success, profiles, count
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        success = try container.decode(Bool.self, forKey: .success)
        count = try container.decode(Int.self, forKey: .count)
        
        let profilesContainer = try container.decode([String: TPProfileDict].self, forKey: .profiles)
        profiles = profilesContainer.mapValues { $0.asDictionary }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(success, forKey: .success)
        try container.encode(count, forKey: .count)
    }
}

private struct TPProfileDict: Codable {
    let name: String
    let emoji: String?
    let levels: [TPLevel]?
    
    var asDictionary: [String: Any] {
        var dict: [String: Any] = ["name": name]
        if let emoji = emoji { dict["emoji"] = emoji }
        if let levels = levels {
            dict["levels"] = levels.map { ["gain_pct": $0.gainPct, "sell_pct": $0.sellPct] }
        }
        return dict
    }
}

private struct GenericResponse: Codable {
    let success: Bool
    let error: String?
}

// MARK: - Request Types

private struct DCAExecuteRequest: Codable {
    let coin: String
    let amount: Double
    let strategy: String
}

private struct RebalanceRequest: Codable {
    let portfolio: String
    let totalInvestment: Double
    
    enum CodingKeys: String, CodingKey {
        case portfolio
        case totalInvestment = "total_investment"
    }
}

private struct SpotBuyRequest: Codable {
    let coin: String
    let amount: Double
}

private struct SpotSellRequest: Codable {
    let coin: String
    let percentage: Double
}

private struct SpotSettingsUpdateRequest: Codable {
    let dcaEnabled: Bool
    let dcaAmount: Double
    let dcaFrequency: String
    let dcaStrategy: String
    let portfolio: String
    let tpEnabled: Bool
    let tpProfile: String
    let trailingTpEnabled: Bool
    let trailingActivationPct: Double
    let trailingTrailPct: Double
    let profitLockEnabled: Bool
    let profitLockTriggerPct: Double
    let profitLockPct: Double
    let smartRebalanceEnabled: Bool
    let rebalanceThresholdPct: Double
    
    enum CodingKeys: String, CodingKey {
        case dcaEnabled = "dca_enabled"
        case dcaAmount = "dca_amount"
        case dcaFrequency = "dca_frequency"
        case dcaStrategy = "dca_strategy"
        case portfolio
        case tpEnabled = "tp_enabled"
        case tpProfile = "tp_profile"
        case trailingTpEnabled = "trailing_tp_enabled"
        case trailingActivationPct = "trailing_activation_pct"
        case trailingTrailPct = "trailing_trail_pct"
        case profitLockEnabled = "profit_lock_enabled"
        case profitLockTriggerPct = "profit_lock_trigger_pct"
        case profitLockPct = "profit_lock_pct"
        case smartRebalanceEnabled = "smart_rebalance_enabled"
        case rebalanceThresholdPct = "rebalance_threshold_pct"
    }
}
