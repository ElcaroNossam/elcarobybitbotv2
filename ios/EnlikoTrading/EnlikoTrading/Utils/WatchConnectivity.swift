//
//  WatchConnectivity.swift
//  EnlikoTrading
//
//  ⌚ iOS-Side Watch Connectivity Manager
//  ======================================
//
//  This file provides iOS-side support for Apple Watch communication.
//  Syncs balance, positions, and alerts with paired Apple Watch.
//
//  Note: The actual WatchKit app requires a separate Watch Extension target.
//

import Foundation
import WatchConnectivity
import Combine

// MARK: - Watch Data Models

struct WatchBalanceData: Codable {
    let totalEquity: Double
    let unrealizedPnL: Double
    let todayPnL: Double
    let availableBalance: Double
    let timestamp: Date
}

struct WatchPositionData: Codable, Identifiable {
    let id: String
    let symbol: String
    let side: String
    let entryPrice: Double
    let currentPrice: Double
    let pnl: Double
    let pnlPercent: Double
    let size: Double
}

struct WatchAlertData: Codable, Identifiable {
    let id: String
    let type: String // priceAlert, orderFilled, signalTriggered, tpHit, slHit
    let symbol: String
    let message: String
    let timestamp: Date
}

// MARK: - Watch Session Manager

/// Manages communication between iOS app and Apple Watch
/// Provides real-time syncing of trading data
class WatchSessionManager: NSObject, ObservableObject {
    static let shared = WatchSessionManager()
    
    @Published var isWatchAppInstalled = false
    @Published var isReachable = false
    @Published var lastSyncTime: Date?
    
    private var session: WCSession?
    private let userDefaults = UserDefaults.standard
    
    override init() {
        super.init()
        setupSession()
    }
    
    // MARK: - Setup
    
    private func setupSession() {
        if WCSession.isSupported() {
            session = WCSession.default
            session?.delegate = self
            session?.activate()
        }
    }
    
    // MARK: - Send Data to Watch
    
    /// Send current balance to Watch
    func sendBalance(_ balance: WatchBalanceData) {
        guard let session = session, session.isReachable else {
            // Cache for later
            if let encoded = try? JSONEncoder().encode(balance) {
                userDefaults.set(encoded, forKey: "pending_watch_balance")
            }
            return
        }
        
        do {
            let data = try JSONEncoder().encode(balance)
            let message = ["type": "balance", "data": data] as [String: Any]
            
            session.sendMessage(message, replyHandler: nil) { error in
                print("⌚ Watch balance send error: \(error)")
            }
            
            lastSyncTime = Date()
        } catch {
            print("⌚ Balance encoding error: \(error)")
        }
    }
    
    /// Send positions to Watch
    func sendPositions(_ positions: [WatchPositionData]) {
        guard let session = session, session.isReachable else {
            if let encoded = try? JSONEncoder().encode(positions) {
                userDefaults.set(encoded, forKey: "pending_watch_positions")
            }
            return
        }
        
        do {
            let data = try JSONEncoder().encode(positions)
            let message = ["type": "positions", "data": data] as [String: Any]
            
            session.sendMessage(message, replyHandler: nil) { error in
                print("⌚ Watch positions send error: \(error)")
            }
        } catch {
            print("⌚ Positions encoding error: \(error)")
        }
    }
    
    /// Send alert to Watch (will trigger haptic on Watch)
    func sendAlert(_ alert: WatchAlertData) {
        guard let session = session else { return }
        
        do {
            let data = try JSONEncoder().encode(alert)
            let message = ["type": "alert", "data": data] as [String: Any]
            
            if session.isReachable {
                session.sendMessage(message, replyHandler: nil, errorHandler: nil)
            } else {
                // Use transferUserInfo for background delivery
                session.transferUserInfo(message)
            }
        } catch {
            print("⌚ Alert encoding error: \(error)")
        }
    }
    
    /// Send complication update
    func updateComplication(symbol: String, price: Double, change: Double) {
        guard let session = session, session.isReachable else { return }
        
        let message: [String: Any] = [
            "type": "complication",
            "symbol": symbol,
            "price": price,
            "change": change
        ]
        
        session.transferCurrentComplicationUserInfo(message)
    }
    
    // MARK: - Sync Helpers
    
    /// Sync all current data to Watch
    func syncAllData() {
        // This would be called when Watch becomes reachable
        // or when user manually requests sync
        
        // Send any pending data
        if let balanceData = userDefaults.data(forKey: "pending_watch_balance"),
           let balance = try? JSONDecoder().decode(WatchBalanceData.self, from: balanceData) {
            sendBalance(balance)
            userDefaults.removeObject(forKey: "pending_watch_balance")
        }
        
        if let positionsData = userDefaults.data(forKey: "pending_watch_positions"),
           let positions = try? JSONDecoder().decode([WatchPositionData].self, from: positionsData) {
            sendPositions(positions)
            userDefaults.removeObject(forKey: "pending_watch_positions")
        }
    }
    
    /// Request data from Watch (for debugging)
    func requestWatchStatus(completion: @escaping (Bool, String) -> Void) {
        guard let session = session, session.isReachable else {
            completion(false, "Watch not reachable")
            return
        }
        
        session.sendMessage(["type": "status"], replyHandler: { reply in
            if let status = reply["status"] as? String {
                completion(true, status)
            } else {
                completion(true, "Unknown")
            }
        }, errorHandler: { error in
            completion(false, error.localizedDescription)
        })
    }
}

// MARK: - WCSessionDelegate

extension WatchSessionManager: WCSessionDelegate {
    
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        DispatchQueue.main.async {
            self.isWatchAppInstalled = session.isWatchAppInstalled
            self.isReachable = session.isReachable
        }
        
        if activationState == .activated {
            syncAllData()
        }
    }
    
    func sessionDidBecomeInactive(_ session: WCSession) {
        // Handle session becoming inactive
    }
    
    func sessionDidDeactivate(_ session: WCSession) {
        // Reactivate session for watch switching
        session.activate()
    }
    
    func sessionReachabilityDidChange(_ session: WCSession) {
        DispatchQueue.main.async {
            self.isReachable = session.isReachable
        }
        
        if session.isReachable {
            syncAllData()
        }
    }
    
    // Handle messages from Watch
    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
        guard let type = message["type"] as? String else { return }
        
        DispatchQueue.main.async {
            switch type {
            case "closePosition":
                if let positionId = message["positionId"] as? String {
                    self.handleClosePositionRequest(positionId)
                }
                
            case "closeAll":
                self.handleCloseAllRequest()
                
            case "refresh":
                self.handleRefreshRequest()
                
            default:
                break
            }
        }
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any], replyHandler: @escaping ([String : Any]) -> Void) {
        guard let type = message["type"] as? String else {
            replyHandler(["error": "Unknown message type"])
            return
        }
        
        switch type {
        case "getBalance":
            // Return current balance
            if let balance = TradingService.shared.balance {
                replyHandler(["equity": balance.totalEquity])
            } else {
                replyHandler(["error": "No balance data"])
            }
            
        default:
            replyHandler(["error": "Unhandled type: \(type)"])
        }
    }
    
    // MARK: - Handle Watch Commands
    
    private func handleClosePositionRequest(_ positionId: String) {
        // Notify app to close position
        NotificationCenter.default.post(
            name: .watchClosePositionRequested,
            object: nil,
            userInfo: ["positionId": positionId]
        )
    }
    
    private func handleCloseAllRequest() {
        NotificationCenter.default.post(
            name: .watchCloseAllRequested,
            object: nil
        )
    }
    
    private func handleRefreshRequest() {
        NotificationCenter.default.post(
            name: .watchRefreshRequested,
            object: nil
        )
    }
}

// MARK: - Notification Extensions

extension Notification.Name {
    static let watchClosePositionRequested = Notification.Name("watchClosePositionRequested")
    static let watchCloseAllRequested = Notification.Name("watchCloseAllRequested")
    static let watchRefreshRequested = Notification.Name("watchRefreshRequested")
}

// MARK: - Watch Status View (for Settings)

import SwiftUI

/// Shows Watch connection status in Settings
struct WatchStatusView: View {
    @ObservedObject private var manager = WatchSessionManager.shared
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "applewatch")
                    .font(.title2)
                    .foregroundColor(manager.isReachable ? .green : .secondary)
                
                VStack(alignment: .leading) {
                    Text("Apple Watch")
                        .font(.headline)
                    
                    Text(statusText)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if manager.isReachable {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                }
            }
            
            if manager.isWatchAppInstalled {
                if let lastSync = manager.lastSyncTime {
                    Text("Last sync: \(lastSync.formatted(.relative(presentation: .named)))")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
                Button("Sync Now") {
                    manager.syncAllData()
                }
                .font(.caption)
                .buttonStyle(.bordered)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
    
    private var statusText: String {
        if !WCSession.isSupported() {
            return "Not supported on this device"
        }
        if !manager.isWatchAppInstalled {
            return "Watch app not installed"
        }
        if manager.isReachable {
            return "Connected"
        }
        return "Not reachable"
    }
}

// MARK: - Preview

#Preview {
    WatchStatusView()
        .padding()
}
