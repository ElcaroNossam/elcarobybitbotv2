//
//  Logger.swift
//  EnlikoTrading
//
//  Centralized logging system with levels and categories
//

import Foundation
import os.log
import UIKit

// MARK: - Log Level
enum LogLevel: Int, Comparable {
    case debug = 0
    case info = 1
    case warning = 2
    case error = 3
    case critical = 4
    
    var prefix: String {
        switch self {
        case .debug: return "🔍 DEBUG"
        case .info: return "ℹ️ INFO"
        case .warning: return "⚠️ WARNING"
        case .error: return "❌ ERROR"
        case .critical: return "🔴 CRITICAL"
        }
    }
    
    var osLogType: OSLogType {
        switch self {
        case .debug: return .debug
        case .info: return .info
        case .warning: return .default
        case .error: return .error
        case .critical: return .fault
        }
    }
    
    static func < (lhs: LogLevel, rhs: LogLevel) -> Bool {
        lhs.rawValue < rhs.rawValue
    }
}

// MARK: - Log Category
enum LogCategory: String, CaseIterable {
    case network = "Network"
    case auth = "Auth"
    case trading = "Trading"
    case websocket = "WebSocket"
    case storage = "Storage"
    case ui = "UI"
    case sync = "Sync"
    case localization = "Localization"
    case security = "Security"
    case general = "General"
    
    var emoji: String {
        switch self {
        case .network: return "🌐"
        case .auth: return "🔐"
        case .trading: return "📊"
        case .websocket: return "🔌"
        case .storage: return "💾"
        case .ui: return "📱"
        case .sync: return "🔄"
        case .localization: return "🌍"
        case .security: return "🛡️"
        case .general: return "📝"
        }
    }
}

// MARK: - AppLogger
class AppLogger {
    static let shared = AppLogger()
    
    // Always show info+ logs (for debugging user issues)
    private var minimumLevel: LogLevel = .debug
    
    // Remote logging config
    private var remoteLoggingEnabled = true
    private var remoteLoggingMinLevel: LogLevel = .warning
    
    private var enabledCategories: Set<LogCategory> = Set(LogCategory.allCases)
    private let dateFormatter: DateFormatter
    private let queue = DispatchQueue(label: "io.enliko.logger", qos: .utility)
    
    // Store recent logs for debugging (max 1000)
    private var logHistory: [LogEntry] = []
    private let maxHistoryCount = 1000
    
    // OS Log handles
    private let osLogHandles: [LogCategory: OSLog]
    
    private init() {
        dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "HH:mm:ss.SSS"
        
        // Create OS Log handles for each category
        var handles: [LogCategory: OSLog] = [:]
        for category in LogCategory.allCases {
            handles[category] = OSLog(subsystem: "io.enliko.trading", category: category.rawValue)
        }
        osLogHandles = handles
    }
    
    // MARK: - Configuration
    
    func setMinimumLevel(_ level: LogLevel) {
        queue.async { [weak self] in
            self?.minimumLevel = level
        }
    }
    
    func enableCategory(_ category: LogCategory) {
        queue.async { [weak self] in
            self?.enabledCategories.insert(category)
        }
    }
    
    func disableCategory(_ category: LogCategory) {
        queue.async { [weak self] in
            self?.enabledCategories.remove(category)
        }
    }
    
    // MARK: - Logging Methods
    
    func debug(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .debug, category: category, file: file, function: function, line: line)
    }
    
    func info(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .info, category: category, file: file, function: function, line: line)
    }
    
    func warning(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .warning, category: category, file: file, function: function, line: line)
    }
    
    func error(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .error, category: category, file: file, function: function, line: line)
    }
    
    func error(_ error: Error, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
        log("Error: \(error.localizedDescription)", level: .error, category: category, file: file, function: function, line: line)
    }
    
    func critical(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .critical, category: category, file: file, function: function, line: line)
    }
    
    // MARK: - Network Specific
    
    func logRequest(_ method: String, url: String, body: String? = nil) {
        let bodyInfo = body.map { ", body: \($0.prefix(200))" } ?? ""
        debug("→ \(method) \(url)\(bodyInfo)", category: .network)
    }
    
    func logResponse(_ method: String, url: String, statusCode: Int, duration: TimeInterval) {
        let emoji = statusCode >= 200 && statusCode < 300 ? "✅" : "❌"
        info("← \(emoji) \(method) \(url) [\(statusCode)] (\(String(format: "%.2f", duration * 1000))ms)", category: .network)
    }
    
    func logNetworkError(_ error: Error, method: String, url: String) {
        self.error("Network failed: \(method) \(url) - \(error.localizedDescription)", category: .network)
    }
    
    // MARK: - Auth Specific
    
    func logAuthAttempt(_ method: String) {
        info("Auth attempt: \(method)", category: .auth)
    }
    
    func logAuthSuccess(_ method: String, userId: Int? = nil) {
        let userInfo = userId.map { ", user_id: \($0)" } ?? ""
        info("✅ Auth success: \(method)\(userInfo)", category: .auth)
    }
    
    func logAuthFailure(_ method: String, reason: String) {
        warning("Auth failed: \(method) - \(reason)", category: .auth)
    }
    
    func logLogout() {
        info("User logged out", category: .auth)
    }
    
    // MARK: - Trading Specific
    
    func logOrderPlaced(symbol: String, side: String, type: String, qty: Double, price: Double?) {
        let priceInfo = price.map { " @ $\($0)" } ?? " @ Market"
        info("📊 Order: \(side) \(symbol) \(qty)\(priceInfo) (\(type))", category: .trading)
    }
    
    func logPositionClosed(symbol: String, side: String, pnl: Double?) {
        let pnlInfo = pnl.map { String(format: " PnL: $%.2f", $0) } ?? ""
        info("📊 Position closed: \(symbol) \(side)\(pnlInfo)", category: .trading)
    }
    
    func logBalanceUpdate(equity: Double, available: Double) {
        debug("Balance update: equity=$\(String(format: "%.2f", equity)), available=$\(String(format: "%.2f", available))", category: .trading)
    }
    
    // MARK: - WebSocket Specific
    
    func logWSConnected(_ type: String) {
        info("🔌 WebSocket connected: \(type)", category: .websocket)
    }
    
    func logWSDisconnected(_ type: String, reason: String? = nil) {
        let reasonInfo = reason.map { " - \($0)" } ?? ""
        info("WebSocket disconnected: \(type)\(reasonInfo)", category: .websocket)
    }
    
    func logWSMessage(_ type: String, data: String) {
        debug("WS message [\(type)]: \(data.prefix(100))", category: .websocket)
    }
    
    func logWSError(_ type: String, error: Error) {
        self.error("WebSocket error [\(type)]: \(error.localizedDescription)", category: .websocket)
    }
    
    // MARK: - Security Specific
    
    func logSecurityEvent(_ event: String) {
        warning("🛡️ Security: \(event)", category: .security)
    }
    
    func logKeychainOperation(_ operation: String, key: String, success: Bool) {
        let status = success ? "✅" : "❌"
        debug("Keychain \(operation) [\(key)]: \(status)", category: .security)
    }
    
    // MARK: - Private
    
    private func log(_ message: String, level: LogLevel, category: LogCategory, file: String, function: String, line: Int) {
        // Check minimum level
        guard level >= minimumLevel else { return }
        
        // Check category enabled
        guard enabledCategories.contains(category) else { return }
        
        queue.async { [weak self] in
            guard let self = self else { return }
            
            let fileName = (file as NSString).lastPathComponent
            let timestamp = self.dateFormatter.string(from: Date())
            let logMessage = "\(timestamp) \(level.prefix) \(category.emoji)[\(category.rawValue)] \(message) (\(fileName):\(line))"
            
            // Print to console
            print(logMessage)
            
            // Log to OS Log
            if let osLog = self.osLogHandles[category] {
                os_log("%{public}@", log: osLog, type: level.osLogType, message)
            }
            
            // Store in history
            let entry = LogEntry(
                timestamp: Date(),
                level: level,
                category: category,
                message: message,
                file: fileName,
                function: function,
                line: line
            )
            self.logHistory.append(entry)
            
            // Trim history if needed
            if self.logHistory.count > self.maxHistoryCount {
                self.logHistory.removeFirst(self.logHistory.count - self.maxHistoryCount)
            }
        }
    }
    
    // MARK: - History Access
    
    func getRecentLogs(count: Int = 100, level: LogLevel? = nil, category: LogCategory? = nil) -> [LogEntry] {
        var filtered = logHistory
        
        if let level = level {
            filtered = filtered.filter { $0.level >= level }
        }
        
        if let category = category {
            filtered = filtered.filter { $0.category == category }
        }
        
        return Array(filtered.suffix(count))
    }
    
    func clearHistory() {
        queue.async { [weak self] in
            self?.logHistory.removeAll()
        }
    }
    
    func exportLogs() -> String {
        return logHistory.map { entry in
            let timestamp = dateFormatter.string(from: entry.timestamp)
            return "\(timestamp) [\(entry.level.prefix)] [\(entry.category.rawValue)] \(entry.message) (\(entry.file):\(entry.line))"
        }.joined(separator: "\n")
    }
    
    // MARK: - Remote Logging
    
    /// Send critical logs to server for monitoring
    func sendLogsToServer() {
        let errorLogs = getRecentLogs(count: 50, level: .warning)
        guard !errorLogs.isEmpty else { return }
        
        let logsData = errorLogs.map { entry -> [String: Any] in
            return [
                "level": entry.level.prefix,
                "category": entry.category.rawValue,
                "message": entry.message,
                "file": entry.file,
                "line": entry.line,
                "timestamp": ISO8601DateFormatter().string(from: entry.timestamp)
            ]
        }
        
        // Fire-and-forget log submission
        Task {
            do {
                try await submitLogsToServer(logs: logsData)
            } catch {
                print("Failed to send logs: \(error)")
            }
        }
    }
    
    private func submitLogsToServer(logs: [[String: Any]]) async throws {
        guard let url = URL(string: Config.apiURL + "/logs/ios") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: [
            "logs": logs,
            "device": UIDevice.current.name,
            "os_version": UIDevice.current.systemVersion,
            "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown"
        ])
        
        let _ = try await URLSession.shared.data(for: request)
    }
}

// MARK: - Log Entry
struct LogEntry: Identifiable {
    let id = UUID()
    let timestamp: Date
    let level: LogLevel
    let category: LogCategory
    let message: String
    let file: String
    let function: String
    let line: Int
}

// MARK: - Convenience Global Functions
func logDebug(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.debug(message, category: category, file: file, function: function, line: line)
}

func logInfo(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.info(message, category: category, file: file, function: function, line: line)
}

func logWarning(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.warning(message, category: category, file: file, function: function, line: line)
}

func logError(_ message: String, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.error(message, category: category, file: file, function: function, line: line)
}

func logError(_ error: Error, category: LogCategory = .general, file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.error(error, category: category, file: file, function: function, line: line)
}
