//
//  Color+Extensions.swift
//  LyxenTrading
//
//  Brand colors and theme
//

import SwiftUI

extension Color {
    // MARK: - Brand Colors
    static let lyxenPrimary = Color(hex: "#6C5CE7")
    static let lyxenSecondary = Color(hex: "#A29BFE")
    static let lyxenAccent = Color(hex: "#00D9FF")
    
    // MARK: - Background Colors
    static let lyxenBackground = Color(hex: "#0D1117")
    static let lyxenSurface = Color(hex: "#161B22")
    static let lyxenCard = Color(hex: "#21262D")
    static let lyxenCardHover = Color(hex: "#30363D")
    
    // MARK: - Text Colors
    static let lyxenText = Color(hex: "#E6EDF3")
    static let lyxenTextSecondary = Color(hex: "#8B949E")
    static let lyxenTextMuted = Color(hex: "#6E7681")
    
    // MARK: - Status Colors
    static let lyxenGreen = Color(hex: "#00C853")
    static let lyxenRed = Color(hex: "#FF5252")
    static let lyxenYellow = Color(hex: "#FFD600")
    static let lyxenOrange = Color(hex: "#FF9100")
    static let lyxenBlue = Color(hex: "#2196F3")
    
    // MARK: - Gradient
    static let lyxenGradient = LinearGradient(
        colors: [lyxenPrimary, lyxenAccent],
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
    func lyxenCard() -> some View {
        self
            .background(Color.lyxenCard)
            .cornerRadius(12)
    }
    
    func lyxenShadow() -> some View {
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
