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
import io.enliko.trading.ui.screens.history.TradeHistoryScreen
import io.enliko.trading.ui.screens.settings.TradingSettingsScreen
import io.enliko.trading.ui.screens.auth.LinkEmailScreen
import io.enliko.trading.ui.screens.settings.ApiKeysScreen
import io.enliko.trading.ui.screens.settings.LeverageSettingsScreen
import io.enliko.trading.ui.screens.settings.RiskSettingsScreen
import io.enliko.trading.ui.screens.settings.ExchangeSettingsScreen
import io.enliko.trading.ui.screens.market.MarketHeatmapScreen
import io.enliko.trading.ui.screens.stats.StatsScreen
import io.enliko.trading.ui.screens.portfolio.PositionsScreen
import io.enliko.trading.ui.screens.screener.ScreenerScreen
import io.enliko.trading.ui.screens.ai.AICopilotScreen
import io.enliko.trading.ui.screens.admin.AdminScreen
import io.enliko.trading.ui.screens.debug.DebugScreen
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
    object TradeHistory : Screen("trade_history")
    object TradingSettings : Screen("trading_settings")
    object LinkEmail : Screen("link_email")
    object ApiKeys : Screen("api_keys")
    object LeverageSettings : Screen("leverage_settings")
    object RiskSettings : Screen("risk_settings")
    object ExchangeSettings : Screen("exchange_settings")
    object MarketHeatmap : Screen("market_heatmap")
    object Stats : Screen("stats")
    object Positions : Screen("positions")
    object Screener : Screen("screener")
    object AICopilot : Screen("ai_copilot")
    object Admin : Screen("admin")
    object Debug : Screen("debug")
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
                    },
                    onNavigateToTradeHistory = {
                        navController.navigate(Screen.TradeHistory.route)
                    },
                    onNavigateToTradingSettings = {
                        navController.navigate(Screen.TradingSettings.route)
                    },
                    onNavigateToLinkEmail = {
                        navController.navigate(Screen.LinkEmail.route)
                    },
                    onNavigateToApiKeys = {
                        navController.navigate(Screen.ApiKeys.route)
                    },
                    onNavigateToLeverageSettings = {
                        navController.navigate(Screen.LeverageSettings.route)
                    },
                    onNavigateToRiskSettings = {
                        navController.navigate(Screen.RiskSettings.route)
                    },
                    onNavigateToExchangeSettings = {
                        navController.navigate(Screen.ExchangeSettings.route)
                    },
                    onNavigateToMarketHeatmap = {
                        navController.navigate(Screen.MarketHeatmap.route)
                    },
                    onNavigateToStats = {
                        navController.navigate(Screen.Stats.route)
                    },
                    onNavigateToPositions = {
                        navController.navigate(Screen.Positions.route)
                    },
                    onNavigateToScreener = {
                        navController.navigate(Screen.Screener.route)
                    },
                    onNavigateToAICopilot = {
                        navController.navigate(Screen.AICopilot.route)
                    },
                    onNavigateToAdmin = {
                        navController.navigate(Screen.Admin.route)
                    },
                    onNavigateToDebug = {
                        navController.navigate(Screen.Debug.route)
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
            
            composable(Screen.TradeHistory.route) {
                TradeHistoryScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
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
            
            composable(Screen.LeverageSettings.route) {
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
            
            composable(Screen.MarketHeatmap.route) {
                MarketHeatmapScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Stats.route) {
                StatsScreen(
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
            
            composable(Screen.AICopilot.route) {
                AICopilotScreen(
                    onBack = { navController.popBackStack() },
                    showBackButton = true
                )
            }
            
            composable(Screen.Admin.route) {
                AdminScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(Screen.Debug.route) {
                DebugScreen(
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
