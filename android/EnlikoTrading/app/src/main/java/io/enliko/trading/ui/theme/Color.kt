package io.enliko.trading.ui.theme

import androidx.compose.ui.graphics.Color

// ═══════════════════════════════════════════════════════════════
// ENLIKO BRAND COLORS - VIBRANT EDITION 2026
// Brighter, more saturated colors for modern trading experience
// ═══════════════════════════════════════════════════════════════

// Primary Brand Colors (More Vibrant!)
val EnlikoPrimary = Color(0xFFFF3333)      // Bright Red - main accent
val EnlikoPrimaryLight = Color(0xFFFF6666) // Light red
val EnlikoPrimaryDark = Color(0xFFCC0000)  // Dark red
val EnlikoSecondary = Color(0xFFFFD700)    // Bright Gold - secondary accent
val EnlikoAccent = Color(0xFF00E5FF)       // Vivid Cyan - utility accent

// Status Colors (More Saturated!)
val SuccessGreen = Color(0xFF00FF88)      // Bright neon green
val ErrorRed = Color(0xFFFF4444)          // Bright red
val WarningOrange = Color(0xFFFFAA00)     // Bright orange
val InfoBlue = Color(0xFF4DA6FF)          // Bright blue

// Trading Colors (Highly Visible)
val LongGreen = Color(0xFF00FF88)         // Bright neon green for longs
val ShortRed = Color(0xFFFF4466)          // Bright coral red for shorts
val NeutralGray = Color(0xFF888899)       // Lighter gray

// ═══════════════════════════════════════════════════════════════
// DARK THEME - LESS DARK, MORE CONTRAST
// ═══════════════════════════════════════════════════════════════
val DarkBackground = Color(0xFF0F0F14)    // Slightly blue-tinted black
val DarkSurface = Color(0xFF16161E)       // Card background - lighter
val DarkSurfaceVariant = Color(0xFF1E1E28) // Elevated cards - even lighter
val DarkSurfaceHighlight = Color(0xFF252532) // Hover/active states
val DarkOnBackground = Color(0xFFFFFFFF)  // Pure white text
val DarkOnSurface = Color(0xFFB8B8CC)     // Lighter secondary text
val DarkOnSurfaceVariant = Color(0xFF8888AA) // Muted but visible

// ═══════════════════════════════════════════════════════════════
// LIGHT THEME
// ═══════════════════════════════════════════════════════════════
val LightBackground = Color(0xFFF8F9FC)
val LightSurface = Color(0xFFFFFFFF)
val LightSurfaceVariant = Color(0xFFF0F1F5)
val LightOnBackground = Color(0xFF0F0F14)
val LightOnSurface = Color(0xFF2D2D40)
val LightOnSurfaceVariant = Color(0xFF6E6E88)

// ═══════════════════════════════════════════════════════════════
// GRADIENT COLORS (For premium feel)
// ═══════════════════════════════════════════════════════════════
val GradientStart = Color(0xFFFF3366)     // Pink-red
val GradientMiddle = Color(0xFFFF6633)    // Orange
val GradientEnd = Color(0xFFFFCC00)       // Gold

val PremiumGradientStart = Color(0xFFFFD700)  // Gold
val PremiumGradientEnd = Color(0xFFFF8C00)    // Dark orange

// ═══════════════════════════════════════════════════════════════
// CONVENIENCE ALIASES
// ═══════════════════════════════════════════════════════════════
val EnlikoBackground = DarkBackground
val EnlikoSurface = DarkSurface
val EnlikoCard = DarkSurfaceVariant
val EnlikoCardElevated = DarkSurfaceHighlight
val EnlikoTextPrimary = DarkOnBackground
val EnlikoTextSecondary = DarkOnSurface
val EnlikoTextMuted = DarkOnSurfaceVariant
val EnlikoBorder = Color(0xFF2E2E3E)      // More visible border
val EnlikoGreen = LongGreen
val EnlikoRed = ShortRed
val EnlikoYellow = WarningOrange
val EnlikoCyan = EnlikoAccent
val EnlikoBybit = Color(0xFFFF9500)       // Bright orange for Bybit
val EnlikoHL = Color(0xFF00E5FF)          // Bright cyan for HyperLiquid
val EnlikoGold = EnlikoSecondary          // Gold for premium
val EnlikoWarning = WarningOrange
val EnlikoPink = Color(0xFFFF66AA)        // For special highlights
val EnlikoPurple = Color(0xFFAA66FF)      // For strategies

// ═══════════════════════════════════════════════════════════════
// CHART COLORS (For data visualization)
// ═══════════════════════════════════════════════════════════════
val ChartLine1 = Color(0xFF00E5FF)        // Cyan
val ChartLine2 = Color(0xFFFF3366)        // Pink
val ChartLine3 = Color(0xFF00FF88)        // Green
val ChartLine4 = Color(0xFFFFAA00)        // Orange
val ChartLine5 = Color(0xFFAA66FF)        // Purple
val ChartLine6 = Color(0xFFFF66AA)        // Pink

val ChartGridLine = Color(0xFF2A2A3A)     // Subtle grid
val ChartCandleGreen = Color(0xFF00FF88)  // Green candle
val ChartCandleRed = Color(0xFFFF4466)    // Red candle

