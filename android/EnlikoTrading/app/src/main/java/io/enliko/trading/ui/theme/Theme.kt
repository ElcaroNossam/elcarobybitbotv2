package io.enliko.trading.ui.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// ═══════════════════════════════════════════════════════════════
// DARK COLOR SCHEME - 2026 PREMIUM EDITION
// Deeper backgrounds, glassmorphism ready, neon accents
// ═══════════════════════════════════════════════════════════════
private val DarkColorScheme = darkColorScheme(
    primary = EnlikoPrimary,
    onPrimary = Color.White,
    primaryContainer = EnlikoPrimaryDark,
    onPrimaryContainer = Color.White,
    
    secondary = EnlikoSecondary,
    onSecondary = Color.Black,
    secondaryContainer = EnlikoSecondary.copy(alpha = 0.2f),
    onSecondaryContainer = EnlikoSecondary,
    
    tertiary = EnlikoAccent,
    onTertiary = Color.Black,
    tertiaryContainer = EnlikoAccent.copy(alpha = 0.2f),
    onTertiaryContainer = EnlikoAccent,
    
    background = DarkBackground,
    onBackground = DarkOnBackground,
    
    surface = DarkSurface,
    onSurface = DarkOnSurface,
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = DarkOnSurfaceVariant,
    
    // Subtle borders for glass effect
    outline = EnlikoBorder,
    outlineVariant = EnlikoBorderLight,
    
    error = EnlikoRed,
    onError = Color.White,
    errorContainer = EnlikoRed.copy(alpha = 0.15f),
    onErrorContainer = EnlikoRed,
    
    // Inverse colors for special surfaces
    inverseSurface = Color.White,
    inverseOnSurface = DarkBackground,
    inversePrimary = EnlikoPrimaryDark,
    
    // Scrim for overlays
    scrim = GlassOverlay
)

// ═══════════════════════════════════════════════════════════════
// LIGHT COLOR SCHEME (preserved for compatibility)
// ═══════════════════════════════════════════════════════════════
private val LightColorScheme = lightColorScheme(
    primary = EnlikoPrimary,
    onPrimary = Color.White,
    primaryContainer = EnlikoPrimary.copy(alpha = 0.1f),
    onPrimaryContainer = EnlikoPrimaryDark,
    
    secondary = EnlikoSecondary,
    onSecondary = Color.Black,
    secondaryContainer = EnlikoSecondary.copy(alpha = 0.1f),
    onSecondaryContainer = EnlikoSecondary,
    
    tertiary = EnlikoAccent,
    onTertiary = Color.Black,
    
    background = LightBackground,
    onBackground = LightOnBackground,
    surface = LightSurface,
    onSurface = LightOnSurface,
    surfaceVariant = LightSurfaceVariant,
    onSurfaceVariant = LightOnSurfaceVariant,
    
    error = EnlikoRed,
    onError = Color.White,
    errorContainer = EnlikoRed.copy(alpha = 0.1f),
    onErrorContainer = EnlikoRed
)

@Composable
fun EnlikoTradingTheme(
    darkTheme: Boolean = true, // ALWAYS dark for trading app
    dynamicColor: Boolean = false, // Keep false for brand consistency
    content: @Composable () -> Unit
) {
    // ALWAYS use dark theme for premium trading experience
    // Ignore dynamic colors and system theme - trading apps need dark mode
    val colorScheme = DarkColorScheme
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            // Deep dark status/nav bars for immersive experience
            window.statusBarColor = DarkBackground.toArgb()
            window.navigationBarColor = DarkBackground.toArgb()
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = false
                isAppearanceLightNavigationBars = false
            }
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
