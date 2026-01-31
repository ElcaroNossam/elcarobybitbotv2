//
//  Color+Extensions.swift
//  EnlikoTrading
//
//  Brand colors and theme
//

import SwiftUI

extension Color {
    // MARK: - Brand Colors (Synced with WebApp - Stark Theme)
    static let enlikoPrimary = Color(hex: "#DC2626")      // Red - primary accent
    static let enlikoSecondary = Color(hex: "#D4A017")    // Gold - secondary accent
    static let enlikoAccent = Color(hex: "#00D4FF")       // Cyan - utility accent
    
    // MARK: - Background Colors
    static let enlikoBackground = Color(hex: "#0A0A0A")   // Primary background
    static let enlikoSurface = Color(hex: "#111111")      // Secondary background
    static let enlikoCard = Color(hex: "#141414")         // Card background
    static let enlikoCardHover = Color(hex: "#1F1F1F")    // Card hover
    static let enlikoBorder = Color(hex: "#2A2A2A")       // Border color
    
    // MARK: - Text Colors
    static let enlikoText = Color(hex: "#F5F5F5")         // Primary text
    static let enlikoTextSecondary = Color(hex: "#A1A1A1") // Secondary text
    static let enlikoTextMuted = Color(hex: "#6B6B6B")    // Muted text
    
    // MARK: - Status Colors
    static let enlikoGreen = Color(hex: "#22C55E")        // Success green
    static let enlikoRed = Color(hex: "#EF4444")          // Error/danger red
    static let enlikoYellow = Color(hex: "#EAB308")       // Warning yellow
    static let enlikoOrange = Color(hex: "#F59E0B")       // Orange
    static let enlikoBlue = Color(hex: "#2196F3")         // Info blue
    static let enlikoPurple = Color(hex: "#DC2626")       // Brand (same as primary)
    
    // MARK: - Gradient
    static let enlikoGradient = LinearGradient(
        colors: [enlikoPrimary, enlikoAccent],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    // MARK: - Hex Initializer
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - View Extensions
extension View {
    func enlikoCard() -> some View {
        self
            .background(Color.enlikoCard)
            .cornerRadius(12)
    }
    
    func enlikoShadow() -> some View {
        self.shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)
    }
    
    func hideKeyboard() {
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
    }
}

// MARK: - Number Formatting
extension Double {
    var formattedPrice: String {
        if abs(self) >= 1000 {
            return String(format: "%.2f", self)
        } else if abs(self) >= 1 {
            return String(format: "%.4f", self)
        } else {
            return String(format: "%.6f", self)
        }
    }
    
    var formattedPercent: String {
        let sign = self >= 0 ? "+" : ""
        return String(format: "%@%.2f%%", sign, self)
    }
    
    var formattedCurrency: String {
        let sign = self >= 0 ? "+" : ""
        return String(format: "%@$%.2f", sign, self)
    }
    
    var compactFormatted: String {
        if abs(self) >= 1_000_000 {
            return String(format: "%.2fM", self / 1_000_000)
        } else if abs(self) >= 1_000 {
            return String(format: "%.2fK", self / 1_000)
        } else {
            return String(format: "%.2f", self)
        }
    }
}

// MARK: - Date Formatting
extension String {
    var formattedDate: String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        
        if let date = formatter.date(from: self) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateStyle = .short
            displayFormatter.timeStyle = .short
            return displayFormatter.string(from: date)
        }
        
        return self
    }
}
