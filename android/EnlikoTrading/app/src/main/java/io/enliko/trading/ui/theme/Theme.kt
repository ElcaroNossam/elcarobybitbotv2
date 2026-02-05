package io.enliko.trading.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// ═══════════════════════════════════════════════════════════════
// DARK COLOR SCHEME - VIBRANT EDITION
// Brighter colors, better contrast, premium feel
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
    
    // Brighter outline for better visibility
    outline = EnlikoBorder,
    outlineVariant = Color(0xFF3A3A4A),
    
    error = ErrorRed,
    onError = Color.White,
    errorContainer = ErrorRed.copy(alpha = 0.2f),
    onErrorContainer = ErrorRed,
    
    // Inverse colors for special surfaces
    inverseSurface = Color.White,
    inverseOnSurface = DarkBackground,
    inversePrimary = EnlikoPrimaryDark
)

// ═══════════════════════════════════════════════════════════════
// LIGHT COLOR SCHEME
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
    
    error = ErrorRed,
    onError = Color.White,
    errorContainer = ErrorRed.copy(alpha = 0.1f),
    onErrorContainer = ErrorRed
)

@Composable
fun EnlikoTradingTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false, // Keep false for brand consistency
    content: @Composable () -> Unit
) {
    // Always use dark theme for trading app (better for traders)
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            // Use darker status bar for immersive feel
            window.statusBarColor = DarkBackground.toArgb()
            window.navigationBarColor = DarkBackground.toArgb()
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = !darkTheme
                isAppearanceLightNavigationBars = !darkTheme
            }
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
