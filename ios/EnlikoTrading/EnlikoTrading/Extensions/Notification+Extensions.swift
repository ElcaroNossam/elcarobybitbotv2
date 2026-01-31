//
//  Notification+Extensions.swift
//  EnlikoTrading
//
//  Notification names for cross-platform sync
//

import Foundation

extension Notification.Name {
    // MARK: - Sync Events
    
    /// Exchange was switched from another platform (webapp/telegram)
    static let exchangeSwitched = Notification.Name("exchangeSwitched")
    
    /// Account type was switched from another platform
    static let accountTypeSwitched = Notification.Name("accountTypeSwitched")
    
    /// Settings were changed from another platform
    static let settingsChanged = Notification.Name("settingsChanged")
    
    /// Server requested a full sync
    static let syncRequested = Notification.Name("syncRequested")
    
    // MARK: - Local Events
    
    /// User logged in successfully
    static let userLoggedIn = Notification.Name("userLoggedIn")
    
    /// User logged out
    static let userLoggedOut = Notification.Name("userLoggedOut")
    
    /// Position was opened
    static let positionOpened = Notification.Name("positionOpened")
    
    /// Position was closed
    static let positionClosed = Notification.Name("positionClosed")
    
    /// Order was placed
    static let orderPlaced = Notification.Name("orderPlaced")
    
    /// Order was cancelled
    static let orderCancelled = Notification.Name("orderCancelled")
    
    // MARK: - Super Features Events 🔥
    
    /// User reached a profit milestone - triggers celebration
    static let profitMilestoneReached = Notification.Name("profitMilestoneReached")
    
    /// Price alert triggered
    static let priceAlertTriggered = Notification.Name("priceAlertTriggered")
    
    /// Achievement unlocked
    static let achievementUnlocked = Notification.Name("achievementUnlocked")
    
    /// Trade signal received
    static let tradeSignalReceived = Notification.Name("tradeSignalReceived")
    
    /// Live activity update
    static let liveActivityUpdate = Notification.Name("liveActivityUpdate")
    
    /// Widget data needs refresh
    static let widgetRefreshNeeded = Notification.Name("widgetRefreshNeeded")
}

// MARK: - Notification Helper

class NotificationHelper {
    static let shared = NotificationHelper()
    
    /// Post a profit milestone notification to trigger celebration
    func postProfitMilestone(profit: Double, symbol: String) {
        NotificationCenter.default.post(
            name: .profitMilestoneReached,
            object: nil,
            userInfo: ["profit": profit, "symbol": symbol]
        )
    }
    
    /// Post an achievement unlocked notification
    func postAchievementUnlocked(title: String, description: String, icon: String) {
        NotificationCenter.default.post(
            name: .achievementUnlocked,
            object: nil,
            userInfo: ["title": title, "description": description, "icon": icon]
        )
    }
    
    /// Post a trade signal notification
    func postTradeSignal(symbol: String, side: String, strategy: String) {
        NotificationCenter.default.post(
            name: .tradeSignalReceived,
            object: nil,
            userInfo: ["symbol": symbol, "side": side, "strategy": strategy]
        )
    }
}
