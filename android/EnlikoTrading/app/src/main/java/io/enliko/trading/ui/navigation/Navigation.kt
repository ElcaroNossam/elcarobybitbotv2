package io.enliko.trading.ui.navigation

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import io.enliko.trading.ui.screens.activity.ActivityScreen
import io.enliko.trading.ui.screens.auth.DisclaimerScreen
import io.enliko.trading.ui.screens.auth.LoginScreen
import io.enliko.trading.ui.screens.auth.hasAcceptedDisclaimer
import io.enliko.trading.ui.screens.charts.AdvancedChartsScreen
import io.enliko.trading.ui.screens.main.MainScreen
import io.enliko.trading.ui.screens.notifications.NotificationsScreen
import io.enliko.trading.ui.screens.notifications.NotificationPreferencesScreen
import io.enliko.trading.ui.screens.social.SocialTradingScreen
import io.enliko.trading.ui.screens.spot.SpotScreen
import io.enliko.trading.ui.screens.strategies.StrategiesScreen
import io.enliko.trading.ui.screens.strategies.BacktestScreen
import io.enliko.trading.util.AppLanguage
import io.enliko.trading.util.ProvideStrings

sealed class Screen(val route: String) {
    object Disclaimer : Screen("disclaimer")
    object Login : Screen("login")
    object Register : Screen("register")
    object Main : Screen("main")
    object Activity : Screen("activity")
    object Spot : Screen("spot")
    object Charts : Screen("charts/{symbol}") {
        fun createRoute(symbol: String) = "charts/$symbol"
    }
    object SocialTrading : Screen("social")
    object Notifications : Screen("notifications")
    object NotificationPreferences : Screen("notification_preferences")
    object Strategies : Screen("strategies")
    object Backtest : Screen("backtest")
    object StrategySettings : Screen("strategy_settings/{strategy}") {
        fun createRoute(strategy: String) = "strategy_settings/$strategy"
    }
    object LanguageSettings : Screen("language_settings")
    object Subscription : Screen("subscription")
}

@Composable
fun EnlikoNavHost(
    isLoggedIn: Boolean,
    currentLanguage: String
) {
    val navController = rememberNavController()
    val language = AppLanguage.fromCode(currentLanguage)
    val context = LocalContext.current
    val disclaimerAccepted = hasAcceptedDisclaimer(context)
    
    // Determine start destination based on disclaimer acceptance and login state
    val startDestination = when {
        !disclaimerAccepted -> Screen.Disclaimer.route
        isLoggedIn -> Screen.Main.route
        else -> Screen.Login.route
    }
    
    ProvideStrings(language = language) {
        NavHost(
            navController = navController,
            startDestination = startDestination
        ) {
            composable(Screen.Disclaimer.route) {
                DisclaimerScreen(
                    onAccept = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(Screen.Disclaimer.route) { inclusive = true }
                        }
                    },
                    onDecline = {
                        // Close the app - user declined disclaimer
                        (context as? android.app.Activity)?.finish()
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
                    onNavigateToRegister = {
                        navController.popBackStack()
                    }
                )
            }
            
            composable(Screen.Main.route) {
                MainScreen(
                    onLogout = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(Screen.Main.route) { inclusive = true }
                        }
                    },
                    onNavigateToActivity = {
                        navController.navigate(Screen.Activity.route)
                    },
                    onNavigateToSpot = {
                        navController.navigate(Screen.Spot.route)
                    },
                    onNavigateToNotifications = {
                        navController.navigate(Screen.Notifications.route)
                    },
                    onNavigateToStrategies = {
                        navController.navigate(Screen.Strategies.route)
                    },
                    onNavigateToCharts = { symbol ->
                        navController.navigate(Screen.Charts.createRoute(symbol))
                    },
                    onNavigateToSocialTrading = {
                        navController.navigate(Screen.SocialTrading.route)
                    },
                    onNavigateToLanguage = {
                        navController.navigate(Screen.LanguageSettings.route)
                    },
                    onNavigateToSubscription = {
                        navController.navigate(Screen.Subscription.route)
                    }
                )
            }
            
            composable(Screen.Activity.route) {
                ActivityScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Spot.route) {
                SpotScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Charts.route) { backStackEntry ->
                val symbol = backStackEntry.arguments?.getString("symbol") ?: "BTCUSDT"
                AdvancedChartsScreen(
                    symbol = symbol,
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.SocialTrading.route) {
                SocialTradingScreen(
                    onBack = { navController.popBackStack() },
                    onTraderClick = { traderId ->
                        // Navigate to trader profile
                    }
                )
            }
            
            composable(Screen.Notifications.route) {
                NotificationsScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.NotificationPreferences.route) {
                NotificationPreferencesScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Strategies.route) {
                StrategiesScreen(
                    onBack = { navController.popBackStack() },
                    onNavigateToStrategySettings = { strategy ->
                        navController.navigate(Screen.StrategySettings.createRoute(strategy))
                    },
                    onNavigateToBacktest = {
                        navController.navigate(Screen.Backtest.route)
                    }
                )
            }
            
            composable(Screen.Backtest.route) {
                BacktestScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.StrategySettings.route) { backStackEntry ->
                val strategy = backStackEntry.arguments?.getString("strategy") ?: "oi"
                io.enliko.trading.ui.screens.settings.StrategySettingsScreen(
                    strategyCode = strategy,
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.LanguageSettings.route) {
                io.enliko.trading.ui.screens.settings.LanguageSettingsScreen(
                    currentLanguage = language,
                    onLanguageSelect = { selectedLanguage ->
                        // TODO: Save language preference
                        navController.popBackStack()
                    },
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Subscription.route) {
                io.enliko.trading.ui.screens.settings.SubscriptionScreen(
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
