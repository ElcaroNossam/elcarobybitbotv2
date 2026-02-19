package io.enliko.trading.ui.theme

import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

// ═══════════════════════════════════════════════════════════════════════════════
// ENLIKO TRADING - MODERN 2026 DESIGN SYSTEM
// Premium glassmorphism, refined dark theme, neon accents
// Synced with iOS Color+Extensions.swift
// ═══════════════════════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════════════════════
// BRAND COLORS (Synced with iOS - Violet Theme 2026)
// ═══════════════════════════════════════════════════════════════════════════════
val EnlikoPrimary = Color(0xFF7C3AED)        // Violet - primary accent (synced with iOS)
val EnlikoPrimaryLight = Color(0xFFA78BFA)   // Light violet - secondary accent
val EnlikoPrimaryDark = Color(0xFF5B21B6)    // Darker violet
val EnlikoSecondary = Color(0xFFC084FC)      // Soft purple - utility accent
val EnlikoAccent = Color(0xFFD946EF)         // Fuchsia - for highlights

// Extended brand palette (Synced with iOS)
val EnlikoPink = Color(0xFFD946EF)           // Fuchsia accent
val EnlikoViolet = Color(0xFF8B5CF6)         // Violet for premium
val EnlikoOrange = Color(0xFFF97316)         // Orange accent
val EnlikoTeal = Color(0xFF14B8A6)           // Teal accent

// ═══════════════════════════════════════════════════════════════════════════════
// TRADING STATUS COLORS - VIBRANT & CLEAR
// ═══════════════════════════════════════════════════════════════════════════════
val EnlikoGreen = Color(0xFF10B981)          // Emerald - Profit/Long
val EnlikoGreenBright = Color(0xFF00FF88)    // Neon green for highlights
val EnlikoRed = Color(0xFFEF4444)            // Red - Loss/Short
val EnlikoRedBright = Color(0xFFFF4466)      // Bright red for highlights
val EnlikoYellow = Color(0xFFF59E0B)         // Amber - Warning
val EnlikoBlue = Color(0xFF3B82F6)           // Blue - Info

// Long/Short specific
val LongGreen = EnlikoGreen
val ShortRed = EnlikoRed
val NeutralGray = Color(0xFF6B7280)

// Status colors (aliases)
val SuccessGreen = EnlikoGreen
val ErrorRed = EnlikoRed
val WarningOrange = EnlikoYellow
val InfoBlue = EnlikoBlue

// ═══════════════════════════════════════════════════════════════════════════════
// DARK THEME - DEEPER, MORE PREMIUM (2026)
// ═══════════════════════════════════════════════════════════════════════════════
val DarkBackground = Color(0xFF050505)       // Near black - deeper than before
val DarkSurface = Color(0xFF0D0D0D)          // Slightly lighter
val DarkSurfaceVariant = Color(0xFF121212)   // Card background
val DarkSurfaceHighlight = Color(0xFF1A1A1A) // Hover/elevated states
val DarkOnBackground = Color(0xFFFFFFFF)     // Pure white text
val DarkOnSurface = Color(0xFFE5E5E5)        // Primary text
val DarkOnSurfaceVariant = Color(0xFF9CA3AF) // Secondary text
val DarkOnSurfaceMuted = Color(0xFF6B7280)   // Muted text

// ═══════════════════════════════════════════════════════════════════════════════
// GLASS MORPHISM COLORS (NEW 2026)
// ═══════════════════════════════════════════════════════════════════════════════
val GlassBackground = Color(0x0DFFFFFF)      // 5% white
val GlassBorder = Color(0x1AFFFFFF)          // 10% white
val GlassHighlight = Color(0x26FFFFFF)       // 15% white
val GlassOverlay = Color(0x80000000)         // 50% black overlay

// ═══════════════════════════════════════════════════════════════════════════════
// LIGHT THEME (preserved for compatibility)
// ═══════════════════════════════════════════════════════════════════════════════
val LightBackground = Color(0xFFF8F9FC)
val LightSurface = Color(0xFFFFFFFF)
val LightSurfaceVariant = Color(0xFFF0F1F5)
val LightOnBackground = Color(0xFF0F0F14)
val LightOnSurface = Color(0xFF1F2937)
val LightOnSurfaceVariant = Color(0xFF6B7280)

// ═══════════════════════════════════════════════════════════════════════════════
// GRADIENT COLORS (Synced with iOS - Violet Theme)
// ═══════════════════════════════════════════════════════════════════════════════
val GradientStart = Color(0xFF7C3AED)     // Violet (synced with iOS)
val GradientMiddle = Color(0xFFA78BFA)    // Light violet
val GradientEnd = Color(0xFFC084FC)       // Soft purple

val PremiumGradientStart = Color(0xFF7C3AED)  // Violet (synced with iOS)
val PremiumGradientMiddle = Color(0xFFD946EF) // Fuchsia
val PremiumGradientEnd = Color(0xFFA78BFA)    // Light violet

// Gradient color lists for Brush.linearGradient()
val GradientPrimaryColors = listOf(EnlikoPrimary, EnlikoSecondary)  // Violet gradient
val GradientProfitColors = listOf(EnlikoGreen, EnlikoTeal)
val GradientLossColors = listOf(EnlikoRed, EnlikoPink)
val GradientPremiumColors = listOf(EnlikoPrimary, EnlikoPink, EnlikoSecondary)
val GradientGlassColors = listOf(GlassHighlight, GlassBackground)

// ═══════════════════════════════════════════════════════════════════════════════
// CONVENIENCE ALIASES
// ═══════════════════════════════════════════════════════════════════════════════
val EnlikoBackground = DarkBackground
val EnlikoSurface = DarkSurface

// PnL colors (CRITICAL - used across screens)
val ProfitGreen = EnlikoGreen
val LossRed = EnlikoRed
val EnlikoCard = DarkSurfaceVariant
val EnlikoCardElevated = DarkSurfaceHighlight
val EnlikoTextPrimary = DarkOnBackground
val EnlikoTextSecondary = DarkOnSurface
val EnlikoTextMuted = DarkOnSurfaceVariant
val EnlikoBorder = Color(0xFF262626)         // Subtle border
val EnlikoBorderLight = Color(0xFF333333)    // Lighter border
val EnlikoCyan = EnlikoAccent
val EnlikoBybit = Color(0xFFF7931A)          // Bybit orange
val EnlikoHL = Color(0xFF00D4FF)             // HyperLiquid cyan
val EnlikoGold = EnlikoSecondary             // Premium gold
val EnlikoWarning = EnlikoYellow
val EnlikoPurple = EnlikoViolet

// Semantic colors
val EnlikoSuccess = EnlikoGreen
val EnlikoError = EnlikoRed
val EnlikoInfo = EnlikoBlue

// ═══════════════════════════════════════════════════════════════════════════════
// POSITION CARD COLORS (side-specific)
// ═══════════════════════════════════════════════════════════════════════════════
val PositionLong = EnlikoGreen  // Main long/buy color
val PositionShort = EnlikoRed   // Main short/sell color
val PositionLongBg = EnlikoGreen.copy(alpha = 0.08f)
val PositionLongBorder = EnlikoGreen.copy(alpha = 0.25f)
val PositionShortBg = EnlikoRed.copy(alpha = 0.08f)
val PositionShortBorder = EnlikoRed.copy(alpha = 0.25f)

val ProfitBg = EnlikoGreen.copy(alpha = 0.1f)
val LossBg = EnlikoRed.copy(alpha = 0.1f)

// ═══════════════════════════════════════════════════════════════════════════════
// CHART COLORS (For data visualization)
// ═══════════════════════════════════════════════════════════════════════════════
val ChartLine1 = EnlikoAccent                // Cyan
val ChartLine2 = EnlikoPink                  // Pink
val ChartLine3 = EnlikoGreen                 // Green
val ChartLine4 = EnlikoOrange                // Orange
val ChartLine5 = EnlikoViolet                // Purple
val ChartLine6 = EnlikoYellow                // Yellow

val ChartGridLine = Color(0xFF1F1F1F)        // Subtle grid
val ChartCandleGreen = EnlikoGreenBright     // Green candle
val ChartCandleRed = EnlikoRedBright         // Red candle

