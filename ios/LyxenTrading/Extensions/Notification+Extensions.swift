//
//  Notification+Extensions.swift
//  LyxenTrading
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
}
