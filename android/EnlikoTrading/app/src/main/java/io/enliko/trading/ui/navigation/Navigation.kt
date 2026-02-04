package io.enliko.trading.ui.navigation

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import io.enliko.trading.ui.screens.auth.DisclaimerScreen
import io.enliko.trading.ui.screens.auth.LoginScreen
import io.enliko.trading.ui.screens.auth.hasAcceptedDisclaimer
import io.enliko.trading.ui.screens.charts.AdvancedChartsScreen
import io.enliko.trading.ui.screens.main.MainScreen
import io.enliko.trading.ui.screens.settings.TradingSettingsScreen
import io.enliko.trading.ui.screens.auth.LinkEmailScreen
import io.enliko.trading.ui.screens.settings.ApiKeysScreen
import io.enliko.trading.ui.screens.settings.LeverageSettingsScreen
import io.enliko.trading.ui.screens.settings.RiskSettingsScreen
import io.enliko.trading.ui.screens.settings.ExchangeSettingsScreen
import io.enliko.trading.ui.screens.portfolio.PositionsScreen
import io.enliko.trading.ui.screens.screener.ScreenerScreen
import io.enliko.trading.ui.screens.admin.AdminScreen
import io.enliko.trading.util.AppLanguage
import io.enliko.trading.util.ProvideStrings

sealed class Screen(val route: String) {
    object Disclaimer : Screen("disclaimer")
    object Login : Screen("login")
    object Register : Screen("register")
    object Main : Screen("main")
    object Charts : Screen("charts/{symbol}") {
        fun createRoute(symbol: String) = "charts/$symbol"
    }
    object TradingSettings : Screen("trading_settings")
    object LinkEmail : Screen("link_email")
    object ApiKeys : Screen("api_keys")
    object Leverage : Screen("leverage")
    object RiskSettings : Screen("risk_settings")
    object ExchangeSettings : Screen("exchange_settings")
    object Positions : Screen("positions")
    object Screener : Screen("screener")
    object Admin : Screen("admin")
}

fun isLoggedIn(context: Context): Boolean {
    val prefs = context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
    return prefs.getString("auth_token", null) != null
}

@Composable
fun EnlikoNavHost(
    isLoggedIn: Boolean = false,
    currentLanguage: String = "en"
) {
    val navController = rememberNavController()
    val context = LocalContext.current
    
    // Get language preference
    val language = AppLanguage.fromCode(currentLanguage)
    
    ProvideStrings(language = language) {
        // Determine start destination
        val hasDisclaimer = hasAcceptedDisclaimer(context)
        
        val startDestination = when {
            !hasDisclaimer -> Screen.Disclaimer.route
            !isLoggedIn -> Screen.Login.route
            else -> Screen.Main.route
        }
        
        NavHost(
            navController = navController,
            startDestination = startDestination
        ) {
            // Auth Flow
            composable(Screen.Disclaimer.route) {
                DisclaimerScreen(
                    onAccept = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(Screen.Disclaimer.route) { inclusive = true }
                        }
                    },
                    onDecline = {
                        // User declined - close app
                        android.os.Process.killProcess(android.os.Process.myPid())
                    }
                )
            }
            
            composable(Screen.Login.route) {
                LoginScreen(
                    onLoginSuccess = {
                        navController.navigate(Screen.Main.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    },
                    onNavigateToRegister = {
                        navController.navigate(Screen.Register.route)
                    }
                )
            }
            
            composable(Screen.Register.route) {
                LoginScreen(
                    isRegisterMode = true,
                    onLoginSuccess = {
                        navController.navigate(Screen.Main.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    },
                    onNavigateToRegister = { navController.popBackStack() }
                )
            }
            
            // Main App
            composable(Screen.Main.route) {
                MainScreen(
                    onLogout = {
                        // Clear token and navigate to login
                        val prefs = context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
                        prefs.edit().remove("auth_token").apply()
                        navController.navigate(Screen.Login.route) {
                            popUpTo(Screen.Main.route) { inclusive = true }
                        }
                    }
                )
            }
            
            // Charts
            composable(Screen.Charts.route) { backStackEntry ->
                val symbol = backStackEntry.arguments?.getString("symbol") ?: "BTCUSDT"
                AdvancedChartsScreen(
                    symbol = symbol,
                    onBack = { navController.popBackStack() }
                )
            }
            
            // Settings Screens
            composable(Screen.TradingSettings.route) {
                TradingSettingsScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.LinkEmail.route) {
                LinkEmailScreen(
                    onBack = { navController.popBackStack() },
                    onSuccess = { navController.popBackStack() }
                )
            }
            
            composable(Screen.ApiKeys.route) {
                ApiKeysScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Leverage.route) {
                LeverageSettingsScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.RiskSettings.route) {
                RiskSettingsScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.ExchangeSettings.route) {
                ExchangeSettingsScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Positions.route) {
                PositionsScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Screener.route) {
                ScreenerScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Admin.route) {
                AdminScreen(
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
