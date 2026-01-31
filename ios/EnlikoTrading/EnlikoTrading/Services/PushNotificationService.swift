//
//  PushNotificationService.swift
//  EnlikoTrading
//
//  Push notification service for iOS
//  Handles APNs registration, notification display, and WebSocket notifications
//

import SwiftUI
import UIKit
import UserNotifications
import Combine

// MARK: - Notification Models

enum NotificationType: String, Codable {
    case tradeOpened = "trade_opened"
    case tradeClosed = "trade_closed"
    case positionUpdate = "position_update"
    case orderFilled = "order_filled"
    case orderCancelled = "order_cancelled"
    case signalNew = "signal_new"
    case signalEntry = "signal_entry"
    case signalExit = "signal_exit"
    case balanceUpdate = "balance_update"
    case marginWarning = "margin_warning"
    case liquidationWarning = "liquidation_warning"
    case settingsChanged = "settings_changed"
    case systemMessage = "system_message"
    case dailyReport = "daily_report"
    case breakEvenTriggered = "break_even_triggered"
    case partialTpTriggered = "partial_tp_triggered"
    case unknown = "unknown"
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        self = NotificationType(rawValue: rawValue) ?? .unknown
    }
}

struct AppNotification: Identifiable, Codable {
    var id: Int
    var type: NotificationType
    var title: String
    var message: String
    var data: [String: AnyCodable]?
    var isRead: Bool
    var createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, type, title, message, data
        case isRead = "is_read"
        case createdAt = "created_at"
    }
    
    var icon: String {
        switch type {
        case .tradeOpened:
            return "arrow.up.right.circle.fill"
        case .tradeClosed:
            return "checkmark.circle.fill"
        case .signalNew, .signalEntry:
            return "bell.badge.fill"
        case .marginWarning, .liquidationWarning:
            return "exclamationmark.triangle.fill"
        case .breakEvenTriggered:
            return "equal.circle.fill"
        case .partialTpTriggered:
            return "chart.pie.fill"
        case .dailyReport:
            return "doc.text.fill"
        default:
            return "bell.fill"
        }
    }
    
    var color: Color {
        switch type {
        case .tradeOpened, .signalNew, .signalEntry:
            return .green
        case .tradeClosed:
            if let pnl = data?["pnl"]?.value as? Double {
                return pnl >= 0 ? .green : .red
            }
            return .blue
        case .marginWarning, .liquidationWarning:
            return .red
        case .breakEvenTriggered:
            return .yellow
        case .partialTpTriggered:
            return .cyan
        default:
            return .blue
        }
    }
}

struct NotificationPreferences: Codable, Equatable {
    var tradesEnabled: Bool = true
    var signalsEnabled: Bool = true
    var priceAlertsEnabled: Bool = true
    var dailyReportEnabled: Bool = true
    var soundEnabled: Bool = true
    var vibrationEnabled: Bool = true
    var tradeOpened: Bool = true
    var tradeClosed: Bool = true
    var breakEven: Bool = true
    var partialTp: Bool = true
    var marginWarning: Bool = true
    
    enum CodingKeys: String, CodingKey {
        case tradesEnabled = "trades_enabled"
        case signalsEnabled = "signals_enabled"
        case priceAlertsEnabled = "price_alerts_enabled"
        case dailyReportEnabled = "daily_report_enabled"
        case soundEnabled = "sound_enabled"
        case vibrationEnabled = "vibration_enabled"
        case tradeOpened = "trade_opened"
        case tradeClosed = "trade_closed"
        case breakEven = "break_even"
        case partialTp = "partial_tp"
        case marginWarning = "margin_warning"
    }
}

// MARK: - Push Notification Service

// Request body for device registration
struct DeviceRegistrationRequest: Encodable {
    let deviceToken: String
    let platform: String
    let deviceName: String?
    let appVersion: String?
    let osVersion: String?
    
    enum CodingKeys: String, CodingKey {
        case deviceToken = "device_token"
        case platform
        case deviceName = "device_name"
        case appVersion = "app_version"
        case osVersion = "os_version"
    }
}

class PushNotificationService: NSObject, ObservableObject {
    static let shared = PushNotificationService()
    
    @Published var notifications: [AppNotification] = []
    @Published var unreadCount: Int = 0
    @Published var preferences: NotificationPreferences = NotificationPreferences()
    @Published var isAuthorized: Bool = false
    @Published var showBanner: Bool = false
    @Published var currentBannerNotification: AppNotification?
    
    private var deviceToken: String?
    private var cancellables = Set<AnyCancellable>()
    
    // WebSocket for real-time notifications
    private var notificationWebSocket: URLSessionWebSocketTask?
    private var webSocketSession: URLSession?
    private var reconnectTimer: Timer?
    private var reconnectAttempts = 0
    private let maxReconnectAttempts = 5
    
    override private init() {
        super.init()
        setupNotificationDelegate()
        setupNotificationCategories()
    }
    
    // MARK: - Setup
    
    private func setupNotificationDelegate() {
        UNUserNotificationCenter.current().delegate = self
    }
    
    /// Setup notification categories with action buttons
    private func setupNotificationCategories() {
        // Trade Opened Category - View Details button
        let viewPositionAction = UNNotificationAction(
            identifier: "VIEW_POSITION",
            title: "📊 View Position",
            options: [.foreground]
        )
        let tradeOpenedCategory = UNNotificationCategory(
            identifier: "TRADE_OPENED",
            actions: [viewPositionAction],
            intentIdentifiers: [],
            options: [.hiddenPreviewsShowTitle, .hiddenPreviewsShowSubtitle]
        )
        
        // Trade Closed Category - View History button
        let viewHistoryAction = UNNotificationAction(
            identifier: "VIEW_HISTORY",
            title: "📈 View History",
            options: [.foreground]
        )
        let shareAction = UNNotificationAction(
            identifier: "SHARE_TRADE",
            title: "📤 Share",
            options: [.foreground]
        )
        let tradeClosedCategory = UNNotificationCategory(
            identifier: "TRADE_CLOSED",
            actions: [viewHistoryAction, shareAction],
            intentIdentifiers: [],
            options: [.hiddenPreviewsShowTitle, .hiddenPreviewsShowSubtitle]
        )
        
        // Daily Digest Category
        let viewStatsAction = UNNotificationAction(
            identifier: "VIEW_STATS",
            title: "📊 Full Report",
            options: [.foreground]
        )
        let dailyDigestCategory = UNNotificationCategory(
            identifier: "DAILY_DIGEST",
            actions: [viewStatsAction],
            intentIdentifiers: [],
            options: [.hiddenPreviewsShowTitle, .hiddenPreviewsShowSubtitle]
        )
        
        // Signal Category - Open/Ignore
        let openSignalAction = UNNotificationAction(
            identifier: "OPEN_SIGNAL",
            title: "🎯 View Signal",
            options: [.foreground]
        )
        let ignoreSignalAction = UNNotificationAction(
            identifier: "IGNORE_SIGNAL",
            title: "Skip",
            options: [.destructive]
        )
        let signalCategory = UNNotificationCategory(
            identifier: "SIGNAL",
            actions: [openSignalAction, ignoreSignalAction],
            intentIdentifiers: [],
            options: [.hiddenPreviewsShowTitle]
        )
        
        // Break-Even Category
        let breakEvenCategory = UNNotificationCategory(
            identifier: "BREAK_EVEN",
            actions: [viewPositionAction],
            intentIdentifiers: [],
            options: [.hiddenPreviewsShowTitle]
        )
        
        // Partial TP Category
        let partialTpCategory = UNNotificationCategory(
            identifier: "PARTIAL_TP",
            actions: [viewPositionAction],
            intentIdentifiers: [],
            options: [.hiddenPreviewsShowTitle]
        )
        
        // Margin Warning Category
        let viewAccountAction = UNNotificationAction(
            identifier: "VIEW_ACCOUNT",
            title: "⚠️ Check Account",
            options: [.foreground]
        )
        let marginWarningCategory = UNNotificationCategory(
            identifier: "MARGIN_WARNING",
            actions: [viewAccountAction],
            intentIdentifiers: [],
            options: [.hiddenPreviewsShowTitle]
        )
        
        // Register all categories
        UNUserNotificationCenter.current().setNotificationCategories([
            tradeOpenedCategory,
            tradeClosedCategory,
            dailyDigestCategory,
            signalCategory,
            breakEvenCategory,
            partialTpCategory,
            marginWarningCategory
        ])
        
        AppLogger.shared.info("Notification categories registered", category: .general)
    }
    
    // MARK: - Permission & Registration
    
    func requestPermission() async -> Bool {
        let center = UNUserNotificationCenter.current()
        
        do {
            let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge])
            
            await MainActor.run {
                self.isAuthorized = granted
            }
            
            if granted {
                await MainActor.run {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
            
            return granted
        } catch {
            AppLogger.shared.error("Failed to request notification permission: \(error)", category: .general)
            return false
        }
    }
    
    func checkAuthorizationStatus() async {
        let settings = await UNUserNotificationCenter.current().notificationSettings()
        
        await MainActor.run {
            self.isAuthorized = settings.authorizationStatus == .authorized
        }
    }
    
    func registerDeviceToken(_ token: Data) {
        let tokenString = token.map { String(format: "%02.2hhx", $0) }.joined()
        self.deviceToken = tokenString
        
        AppLogger.shared.info("Device token: \(tokenString.prefix(20))...", category: .general)
        
        // Register with server
        Task {
            await registerTokenWithServer(tokenString)
        }
    }
    
    private func registerTokenWithServer(_ token: String) async {
        guard AuthManager.shared.isAuthenticated else { return }
        
        let deviceName = UIDevice.current.name
        let appVersion = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0"
        let osVersion = UIDevice.current.systemVersion
        
        let body = DeviceRegistrationRequest(
            deviceToken: token,
            platform: "ios",
            deviceName: deviceName,
            appVersion: appVersion,
            osVersion: osVersion
        )
        
        do {
            let _: EmptyResponse = try await NetworkService.shared.post("/notifications/devices/register", body: body)
            AppLogger.shared.info("Device token registered with server", category: .network)
        } catch {
            AppLogger.shared.error("Failed to register device token: \(error)", category: .network)
        }
    }
    
    // Unregister device on logout
    func unregisterDevice() async {
        guard let token = deviceToken else { return }
        
        do {
            try await NetworkService.shared.delete("/notifications/devices/\(token)")
            AppLogger.shared.info("Device unregistered", category: .network)
        } catch {
            AppLogger.shared.error("Failed to unregister device: \(error)", category: .network)
        }
        
        deviceToken = nil
    }
    
    // MARK: - WebSocket Connection
    
    func connectWebSocket() async {
        guard AuthManager.shared.isAuthenticated,
              let token = NetworkService.shared.currentAuthToken else { return }
        
        let wsURL = URL(string: "\(Config.wsURL)/api/notifications/ws/\(token)")!
        
        let configuration = URLSessionConfiguration.default
        configuration.waitsForConnectivity = true
        
        webSocketSession = URLSession(configuration: configuration, delegate: nil, delegateQueue: nil)
        notificationWebSocket = webSocketSession?.webSocketTask(with: wsURL)
        notificationWebSocket?.resume()
        
        receiveMessage()
        
        AppLogger.shared.logWSConnected("notifications")
    }
    
    func disconnectWebSocket() {
        notificationWebSocket?.cancel(with: .goingAway, reason: nil)
        notificationWebSocket = nil
        reconnectTimer?.invalidate()
        reconnectTimer = nil
        
        AppLogger.shared.logWSDisconnected("notifications")
    }
    
    private func receiveMessage() {
        notificationWebSocket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                self?.handleWebSocketMessage(message)
                self?.receiveMessage() // Continue receiving
                
            case .failure(let error):
                AppLogger.shared.error("WebSocket receive error: \(error)", category: .websocket)
                self?.scheduleReconnect()
            }
        }
    }
    
    private func handleWebSocketMessage(_ message: URLSessionWebSocketTask.Message) {
        switch message {
        case .string(let text):
            guard let data = text.data(using: .utf8),
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let type = json["type"] as? String else { return }
            
            switch type {
            case "notification":
                if let payload = json["payload"] as? [String: Any],
                   let payloadData = try? JSONSerialization.data(withJSONObject: payload),
                   let notification = try? JSONDecoder().decode(AppNotification.self, from: payloadData) {
                    
                    DispatchQueue.main.async {
                        self.handleNewNotification(notification)
                    }
                }
                
            case "connected":
                if let count = json["unread_count"] as? Int {
                    DispatchQueue.main.async {
                        self.unreadCount = count
                    }
                }
                
            case "ping":
                sendPong()
                
            default:
                break
            }
            
        case .data:
            break
            
        @unknown default:
            break
        }
    }
    
    private func sendPong() {
        let message = URLSessionWebSocketTask.Message.string(#"{"type":"pong"}"#)
        notificationWebSocket?.send(message) { _ in }
    }
    
    private func scheduleReconnect() {
        guard reconnectAttempts < maxReconnectAttempts else {
            AppLogger.shared.error("Max reconnect attempts reached", category: .websocket)
            return
        }
        
        let delay = Double(min(30, pow(2.0, Double(reconnectAttempts))))
        reconnectAttempts += 1
        
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            Task {
                await self?.connectWebSocket()
            }
        }
    }
    
    // MARK: - Notification Handling
    
    private func handleNewNotification(_ notification: AppNotification) {
        // Add to list
        notifications.insert(notification, at: 0)
        unreadCount += 1
        
        // Show banner
        showNotificationBanner(notification)
        
        // Haptic feedback
        if preferences.vibrationEnabled {
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(.success)
        }
        
        // Post notification for other parts of app
        NotificationCenter.default.post(
            name: .newNotificationReceived,
            object: nil,
            userInfo: ["notification": notification]
        )
    }
    
    private func showNotificationBanner(_ notification: AppNotification) {
        withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
            currentBannerNotification = notification
            showBanner = true
        }
        
        // Auto-hide after 4 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 4) { [weak self] in
            withAnimation(.easeOut(duration: 0.3)) {
                self?.showBanner = false
            }
        }
    }
    
    func dismissBanner() {
        withAnimation(.easeOut(duration: 0.3)) {
            showBanner = false
        }
    }
    
    // MARK: - API Methods
    
    func loadNotifications() async {
        do {
            struct NotificationHistoryResponse: Codable {
                let notifications: [AppNotification]
                let unreadCount: Int
                
                enum CodingKeys: String, CodingKey {
                    case notifications
                    case unreadCount = "unread_count"
                }
            }
            
            let response: NotificationHistoryResponse = try await NetworkService.shared.get(
                "/notifications/history",
                params: ["limit": "50"]
            )
            
            await MainActor.run {
                self.notifications = response.notifications
                self.unreadCount = response.unreadCount
            }
        } catch {
            AppLogger.shared.error("Failed to load notifications: \(error)", category: .network)
        }
    }
    
    func markAsRead(_ notificationId: Int) async {
        struct MarkReadRequest: Encodable {
            let notificationIds: [Int]
            
            enum CodingKeys: String, CodingKey {
                case notificationIds = "notification_ids"
            }
        }
        
        do {
            let body = MarkReadRequest(notificationIds: [notificationId])
            let _: EmptyResponse = try await NetworkService.shared.post(
                "/notifications/mark-read",
                body: body
            )
            
            await MainActor.run {
                if let index = self.notifications.firstIndex(where: { $0.id == notificationId }) {
                    self.notifications[index].isRead = true
                }
                self.unreadCount = max(0, self.unreadCount - 1)
            }
        } catch {
            AppLogger.shared.error("Failed to mark notification as read: \(error)", category: .network)
        }
    }
    
    func markAllAsRead() async {
        do {
            try await NetworkService.shared.postIgnoreResponse("/notifications/mark-all-read")
            
            await MainActor.run {
                for i in self.notifications.indices {
                    self.notifications[i].isRead = true
                }
                self.unreadCount = 0
            }
        } catch {
            AppLogger.shared.error("Failed to mark all as read: \(error)", category: .network)
        }
    }
    
    func loadPreferences() async {
        do {
            let prefs: NotificationPreferences = try await NetworkService.shared.get("/notifications/preferences")
            
            await MainActor.run {
                self.preferences = prefs
            }
        } catch {
            AppLogger.shared.error("Failed to load notification preferences: \(error)", category: .network)
        }
    }
    
    func savePreferences() async {
        do {
            let _: EmptyResponse = try await NetworkService.shared.put("/notifications/preferences", body: preferences)
        } catch {
            AppLogger.shared.error("Failed to save notification preferences: \(error)", category: .network)
        }
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension PushNotificationService: UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification
    ) async -> UNNotificationPresentationOptions {
        // Show banner and sound even when app is in foreground
        return [.banner, .sound, .badge]
    }
    
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        let userInfo = response.notification.request.content.userInfo
        let actionIdentifier = response.actionIdentifier
        
        AppLogger.shared.info("Notification action: \(actionIdentifier)", category: .general)
        
        // Handle notification tap or action button
        if let notificationId = userInfo["notification_id"] as? Int {
            await markAsRead(notificationId)
        }
        
        // Handle specific action buttons
        switch actionIdentifier {
        case "VIEW_POSITION", "VIEW_ACCOUNT":
            // Navigate to positions/portfolio
            DispatchQueue.main.async {
                NotificationCenter.default.post(name: .navigateToPositions, object: nil)
            }
            
        case "VIEW_HISTORY":
            // Navigate to trade history
            DispatchQueue.main.async {
                NotificationCenter.default.post(name: .navigateToHistory, object: nil)
            }
            
        case "VIEW_STATS":
            // Navigate to stats
            DispatchQueue.main.async {
                NotificationCenter.default.post(name: .navigateToStats, object: nil)
            }
            
        case "OPEN_SIGNAL":
            // Navigate to signals
            DispatchQueue.main.async {
                NotificationCenter.default.post(name: .navigateToSignals, object: nil)
            }
            
        case "SHARE_TRADE":
            // Share trade result
            if let symbol = userInfo["symbol"] as? String,
               let pnl = userInfo["pnl"] as? Double,
               let pnlPercent = userInfo["pnl_percent"] as? Double {
                DispatchQueue.main.async {
                    let shareText = "🎉 Just closed \(symbol) trade on Enliko!\n💰 PnL: $\(String(format: "%+.2f", pnl)) (\(String(format: "%+.1f", pnlPercent))%)\n\n📱 Download Enliko: https://enliko.com"
                    NotificationCenter.default.post(
                        name: .shareContent,
                        object: shareText
                    )
                }
            }
            
        case "IGNORE_SIGNAL":
            // Just dismiss, nothing to do
            break
            
        case UNNotificationDefaultActionIdentifier:
            // Default tap on notification
            if let type = userInfo["type"] as? String {
                DispatchQueue.main.async {
                    switch type {
                    case "trade_opened", "trade_closed", "position_update", "break_even_triggered", "partial_tp_triggered":
                        NotificationCenter.default.post(name: .navigateToPositions, object: nil)
                        
                    case "signal_new", "signal_entry":
                        NotificationCenter.default.post(name: .navigateToSignals, object: nil)
                        
                    case "daily_report":
                        NotificationCenter.default.post(name: .navigateToStats, object: nil)
                        
                    case "margin_warning", "liquidation_warning":
                        NotificationCenter.default.post(name: .navigateToPositions, object: nil)
                        
                    default:
                        break
                    }
                }
            }
            
        default:
            break
        }
    }
}

// MARK: - Notification Names

extension Notification.Name {
    static let newNotificationReceived = Notification.Name("newNotificationReceived")
    static let navigateToPositions = Notification.Name("navigateToPositions")
    static let navigateToSignals = Notification.Name("navigateToSignals")
    static let navigateToHistory = Notification.Name("navigateToHistory")
    static let navigateToStats = Notification.Name("navigateToStats")
    static let shareContent = Notification.Name("shareContent")
