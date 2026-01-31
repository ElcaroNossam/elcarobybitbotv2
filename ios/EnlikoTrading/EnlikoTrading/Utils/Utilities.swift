//
//  Utilities.swift
//  EnlikoTrading
//
//  Utility functions and helpers
//

import Foundation
import SwiftUI

// MARK: - Haptic Feedback
enum HapticFeedback {
    static func light() {
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
    }
    
    static func medium() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
    }
    
    static func heavy() {
        let generator = UIImpactFeedbackGenerator(style: .heavy)
        generator.impactOccurred()
    }
    
    static func success() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
    }
    
    static func warning() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.warning)
    }
    
    static func error() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.error)
    }
    
    static func selection() {
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }
}

// MARK: - Date Utilities
extension Date {
    static func fromISO8601(_ string: String) -> Date? {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = formatter.date(from: string) {
            return date
        }
        
        // Try without fractional seconds
        formatter.formatOptions = [.withInternetDateTime]
        return formatter.date(from: string)
    }
    
    var relativeString: String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: self, relativeTo: Date())
    }
    
    var shortString: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter.string(from: self)
    }
    
    var timeString: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: self)
    }
}

// MARK: - Number Utilities
extension Int {
    var abbreviated: String {
        if self >= 1_000_000_000 {
            return String(format: "%.1fB", Double(self) / 1_000_000_000)
        }
        if self >= 1_000_000 {
            return String(format: "%.1fM", Double(self) / 1_000_000)
        }
        if self >= 1_000 {
            return String(format: "%.1fK", Double(self) / 1_000)
        }
        return String(self)
    }
    
    var formattedWithSeparator: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = ","
        return formatter.string(from: NSNumber(value: self)) ?? String(self)
    }
}

extension Double {
    var formattedWithSeparator: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = ","
        formatter.maximumFractionDigits = 2
        return formatter.string(from: NSNumber(value: self)) ?? String(format: "%.2f", self)
    }
    
    func formatted(decimals: Int) -> String {
        return String(format: "%.\(decimals)f", self)
    }
    
    var percentFormatted: String {
        let sign = self >= 0 ? "+" : ""
        return "\(sign)\(String(format: "%.2f", self))%"
    }
    
    var priceFormatted: String {
        if abs(self) >= 1000 {
            return formattedWithSeparator
        } else if abs(self) >= 1 {
            return String(format: "%.2f", self)
        } else if abs(self) >= 0.0001 {
            return String(format: "%.4f", self)
        } else {
            return String(format: "%.8f", self)
        }
    }
}

// MARK: - String Utilities
extension String {
    var isValidEmail: Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let predicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
        return predicate.evaluate(with: self)
    }
    
    var masked: String {
        guard count > 8 else { return String(repeating: "*", count: count) }
        let prefix = String(self.prefix(4))
        let suffix = String(self.suffix(4))
        let middle = String(repeating: "*", count: count - 8)
        return prefix + middle + suffix
    }
    
    func truncated(to length: Int, trailing: String = "...") -> String {
        if count <= length {
            return self
        }
        return String(prefix(length)) + trailing
    }
}

// MARK: - Debouncer
class Debouncer {
    private var workItem: DispatchWorkItem?
    private let queue: DispatchQueue
    private let delay: TimeInterval
    
    init(delay: TimeInterval, queue: DispatchQueue = .main) {
        self.delay = delay
        self.queue = queue
    }
    
    func debounce(action: @escaping () -> Void) {
        workItem?.cancel()
        workItem = DispatchWorkItem(block: action)
        queue.asyncAfter(deadline: .now() + delay, execute: workItem!)
    }
}

// MARK: - Throttler
class Throttler {
    private var lastExecutedAt: Date?
    private let interval: TimeInterval
    
    init(interval: TimeInterval) {
        self.interval = interval
    }
    
    func throttle(action: () -> Void) {
        let now = Date()
        if let lastExecutedAt = lastExecutedAt,
           now.timeIntervalSince(lastExecutedAt) < interval {
            return
        }
        lastExecutedAt = now
        action()
    }
}

// MARK: - Logging
enum Logger {
    static func debug(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        #if DEBUG
        let filename = (file as NSString).lastPathComponent
        print("🔍 [\(filename):\(line)] \(function) - \(message)")
        #endif
    }
    
    static func info(_ message: String) {
        #if DEBUG
        print("ℹ️ \(message)")
        #endif
    }
    
    static func warning(_ message: String) {
        print("⚠️ \(message)")
    }
    
    static func error(_ message: String, error: Error? = nil) {
        var output = "❌ \(message)"
        if let error = error {
            output += " - \(error.localizedDescription)"
        }
        print(output)
    }
    
    static func network(_ method: String, _ url: String, status: Int? = nil) {
        #if DEBUG
        if let status = status {
            let emoji = status < 400 ? "✅" : "❌"
            print("\(emoji) [\(status)] \(method) \(url)")
        } else {
            print("🌐 \(method) \(url)")
        }
        #endif
    }
}

// MARK: - UserDefaults Keys
enum UserDefaultsKeys {
    static let hasCompletedOnboarding = "hasCompletedOnboarding"
    static let defaultExchange = "defaultExchange"
    static let defaultAccountType = "defaultAccountType"
    static let defaultLeverage = "defaultLeverage"
    static let defaultTP = "defaultTP"
    static let defaultSL = "defaultSL"
    static let maxPositions = "maxPositions"
    static let tradeNotifications = "tradeNotifications"
    static let signalNotifications = "signalNotifications"
    static let lastSyncDate = "lastSyncDate"
}

// MARK: - Validation
enum ValidationError: LocalizedError {
    case emptyField(String)
    case invalidEmail
    case passwordTooShort
    case invalidAPIKey
    case invalidPrivateKey
    
    var errorDescription: String? {
        switch self {
        case .emptyField(let field):
            return "\(field) cannot be empty"
        case .invalidEmail:
            return "Please enter a valid email address"
        case .passwordTooShort:
            return "Password must be at least 8 characters"
        case .invalidAPIKey:
            return "Invalid API key format"
        case .invalidPrivateKey:
            return "Invalid private key format"
        }
    }
}

struct Validator {
    static func validateEmail(_ email: String) throws {
        guard !email.isEmpty else {
            throw ValidationError.emptyField("Email")
        }
        guard email.isValidEmail else {
            throw ValidationError.invalidEmail
        }
    }
    
    static func validatePassword(_ password: String) throws {
        guard !password.isEmpty else {
            throw ValidationError.emptyField("Password")
        }
        guard password.count >= 8 else {
            throw ValidationError.passwordTooShort
        }
    }
    
    static func validateAPIKey(_ key: String) throws {
        guard !key.isEmpty else {
            throw ValidationError.emptyField("API Key")
        }
        guard key.count >= 18 else {
            throw ValidationError.invalidAPIKey
        }
    }
    
    static func validatePrivateKey(_ key: String) throws {
        guard !key.isEmpty else {
            throw ValidationError.emptyField("Private Key")
        }
        guard key.hasPrefix("0x") || key.count == 64 || key.count == 66 else {
            throw ValidationError.invalidPrivateKey
        }
    }
}
