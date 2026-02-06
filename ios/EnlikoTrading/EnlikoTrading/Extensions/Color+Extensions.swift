//
//  Color+Extensions.swift
//  EnlikoTrading
//
//  Brand colors and theme - 2026 Modern Design System
//

import SwiftUI

extension Color {
    // MARK: - Brand Colors (Synced with WebApp - Stark Theme 2026)
    static let enlikoPrimary = Color(hex: "#DC2626")      // Red - primary accent
    static let enlikoSecondary = Color(hex: "#D4A017")    // Gold - secondary accent
    static let enlikoAccent = Color(hex: "#00D4FF")       // Cyan - utility accent
    static let enlikoPink = Color(hex: "#EC4899")         // Pink - for highlights
    static let enlikoViolet = Color(hex: "#8B5CF6")       // Violet - for premium
    
    // MARK: - Background Colors (Refined Dark Theme)
    static let enlikoBackground = Color(hex: "#050505")   // Deeper black
    static let enlikoSurface = Color(hex: "#0D0D0D")      // Elevated surface
    static let enlikoCard = Color(hex: "#121212")         // Card background
    static let enlikoCardHover = Color(hex: "#1A1A1A")    // Card hover
    static let enlikoCardElevated = Color(hex: "#1E1E1E") // Elevated card
    static let enlikoBorder = Color(hex: "#262626")       // Border color
    static let enlikoBorderLight = Color(hex: "#333333")  // Lighter border
    
    // MARK: - Glass Effect Colors
    static let enlikoGlass = Color.white.opacity(0.05)    // Glassmorphism base
    static let enlikoGlassBorder = Color.white.opacity(0.1) // Glass border
    
    // MARK: - Text Colors
    static let enlikoText = Color(hex: "#FAFAFA")         // Primary text (brighter)
    static let enlikoTextSecondary = Color(hex: "#9CA3AF") // Secondary text
    static let enlikoTextMuted = Color(hex: "#6B7280")    // Muted text
    static let enlikoTextTertiary = Color(hex: "#4B5563") // Tertiary text
    
    // MARK: - Status Colors (Vibrant)
    static let enlikoGreen = Color(hex: "#10B981")        // Success green (emerald)
    static let enlikoGreenLight = Color(hex: "#34D399")   // Light green
    static let enlikoRed = Color(hex: "#EF4444")          // Error/danger red
    static let enlikoRedLight = Color(hex: "#F87171")     // Light red
    static let enlikoYellow = Color(hex: "#F59E0B")       // Warning yellow
    static let enlikoOrange = Color(hex: "#F97316")       // Orange
    static let enlikoBlue = Color(hex: "#3B82F6")         // Info blue
    static let enlikoPurple = Color(hex: "#A855F7")       // Purple accent
    
    // MARK: - Gradients
    static let enlikoGradient = LinearGradient(
        colors: [enlikoPrimary, enlikoOrange],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    static let enlikoProfitGradient = LinearGradient(
        colors: [enlikoGreen, enlikoGreenLight],
        startPoint: .leading,
        endPoint: .trailing
    )
    
    static let enlikoLossGradient = LinearGradient(
        colors: [enlikoRed, enlikoRedLight],
        startPoint: .leading,
        endPoint: .trailing
    )
    
    static let enlikoPremiumGradient = LinearGradient(
        colors: [enlikoViolet, enlikoPink],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    static let enlikoGlassGradient = LinearGradient(
        colors: [Color.white.opacity(0.1), Color.white.opacity(0.05)],
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

// MARK: - View Extensions (2026 Modern Design)
extension View {
    // Standard card style
    func enlikoCard() -> some View {
        self
            .background(Color.enlikoCard)
            .cornerRadius(16)
    }
    
    // Elevated card with subtle glow
    func enlikoCardElevated() -> some View {
        self
            .background(Color.enlikoCardElevated)
            .cornerRadius(20)
            .shadow(color: Color.black.opacity(0.4), radius: 20, x: 0, y: 10)
    }
    
    // Glassmorphism card style
    func enlikoGlassCard() -> some View {
        self
            .background(
                RoundedRectangle(cornerRadius: 20)
                    .fill(Color.enlikoGlass)
                    .background(
                        RoundedRectangle(cornerRadius: 20)
                            .fill(.ultraThinMaterial)
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(Color.enlikoGlassBorder, lineWidth: 1)
            )
    }
    
    // Glowing card for important elements
    func enlikoGlowCard(color: Color = .enlikoPrimary) -> some View {
        self
            .background(Color.enlikoCard)
            .cornerRadius(16)
            .shadow(color: color.opacity(0.3), radius: 15, x: 0, y: 5)
    }
    
    // Neon border effect
    func enlikoNeonBorder(color: Color = .enlikoPrimary) -> some View {
        self
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(color.opacity(0.6), lineWidth: 1)
            )
            .shadow(color: color.opacity(0.4), radius: 8, x: 0, y: 0)
    }
    
    // Standard shadow
    func enlikoShadow() -> some View {
        self.shadow(color: Color.black.opacity(0.4), radius: 15, x: 0, y: 8)
    }
    
    // Subtle shadow for cards
    func enlikoSubtleShadow() -> some View {
        self.shadow(color: Color.black.opacity(0.25), radius: 8, x: 0, y: 4)
    }
    
    // Hide keyboard
    func hideKeyboard() {
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
    }
    
    // Shimmer loading effect
    @ViewBuilder
    func shimmer(isActive: Bool = true) -> some View {
        if isActive {
            self.modifier(ShimmerModifier())
        } else {
            self
        }
    }
}

// MARK: - Shimmer Effect Modifier
struct ShimmerModifier: ViewModifier {
    @State private var phase: CGFloat = 0
    
    func body(content: Content) -> some View {
        content
            .overlay(
                GeometryReader { geo in
                    LinearGradient(
                        colors: [
                            Color.clear,
                            Color.white.opacity(0.2),
                            Color.clear
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                    .frame(width: geo.size.width * 2)
                    .offset(x: -geo.size.width + phase * geo.size.width * 2)
                }
            )
            .mask(content)
            .onAppear {
                withAnimation(.linear(duration: 1.5).repeatForever(autoreverses: false)) {
                    phase = 1
                }
            }
    }
}

// NOTE: AnimatedGradientBackground is defined in ModernComponents.swift

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
