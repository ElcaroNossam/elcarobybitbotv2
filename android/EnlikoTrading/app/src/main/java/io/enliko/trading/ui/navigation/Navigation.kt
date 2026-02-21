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
import io.enliko.trading.ui.screens.wallet.WalletScreen
import io.enliko.trading.ui.screens.alerts.AlertsScreen
import io.enliko.trading.ui.screens.history.TradeHistoryScreen
import io.enliko.trading.ui.screens.hyperliquid.HyperLiquidScreen
import io.enliko.trading.ui.screens.orderbook.OrderbookScreen
import io.enliko.trading.ui.screens.market.MarketHubScreen
import io.enliko.trading.ui.screens.trading.AdvancedTradingScreen
import io.enliko.trading.ui.screens.more.MoreScreen
import io.enliko.trading.ui.screens.copytrading.CopyTradingScreen
import io.enliko.trading.ui.screens.ai.AIAssistantScreen
import io.enliko.trading.ui.screens.stats.StatsScreen
import io.enliko.trading.ui.screens.spot.SpotTradingScreen
import io.enliko.trading.ui.screens.strategies.StrategiesScreen
import io.enliko.trading.ui.screens.strategies.BacktestScreen
import io.enliko.trading.ui.screens.settings.StrategySettingsScreen
import io.enliko.trading.ui.screens.trading.ManualTradingScreen
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
    
    // New screens
    object Wallet : Screen("wallet")
    object Alerts : Screen("alerts")
    object TradeHistory : Screen("trade_history")
    object HyperLiquid : Screen("hyperliquid")
    object Orderbook : Screen("orderbook/{symbol}") {
        fun createRoute(symbol: String) = "orderbook/$symbol"
    }
    object MarketHub : Screen("market_hub")
    object AdvancedTrading : Screen("advanced_trading/{symbol}") {
        fun createRoute(symbol: String) = "advanced_trading/$symbol"
    }
    
    // Additional screens
    object More : Screen("more")
    object CopyTrading : Screen("copy_trading")
    object AIAssistant : Screen("ai_assistant")
    object Stats : Screen("stats")
    object SpotTrading : Screen("spot_trading")
    object Strategies : Screen("strategies")
    object Backtest : Screen("backtest")
    object StrategySettings : Screen("strategy_settings/{strategy}") {
        fun createRoute(strategy: String) = "strategy_settings/$strategy"
    }
    object ManualTrading : Screen("manual_trading/{symbol}") {
        fun createRoute(symbol: String = "BTCUSDT") = "manual_trading/$symbol"
    }
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
                        // User declined - close app gracefully
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
                    },
                    onNavigateToManualTrading = { symbol ->
                        navController.navigate(Screen.ManualTrading.createRoute(symbol))
                    },
                    onNavigateToActivity = {
                        // Activity handled in Settings tab internal nav
                    },
                    onNavigateToSpot = {
                        navController.navigate(Screen.SpotTrading.route)
                    },
                    onNavigateToNotifications = {
                        // Handled by MainScreen internal NavHost (notifications route)
                    },
                    onNavigateToStrategies = {
                        navController.navigate(Screen.Strategies.route)
                    },
                    onNavigateToCharts = { symbol ->
                        navController.navigate(Screen.Charts.createRoute(symbol))
                    },
                    onNavigateToSocialTrading = {
                        navController.navigate(Screen.CopyTrading.route)
                    },
                    onNavigateToLanguage = {
                        // Handled by SettingsScreen language dialog
                    },
                    onNavigateToSubscription = {
                        // Subscription screen (future)
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
                        navController.navigate(Screen.Leverage.route)
                    },
                    onNavigateToRiskSettings = {
                        navController.navigate(Screen.RiskSettings.route)
                    },
                    onNavigateToExchangeSettings = {
                        navController.navigate(Screen.ExchangeSettings.route)
                    },
                    onNavigateToMarketHeatmap = {
                        navController.navigate(Screen.MarketHub.route)
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
                        navController.navigate(Screen.AIAssistant.route)
                    },
                    onNavigateToAdmin = {
                        navController.navigate(Screen.Admin.route)
                    },
                    onNavigateToDebug = {
                        // Debug console (future)
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
            
            // Wallet
            composable(Screen.Wallet.route) {
                WalletScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // Alerts
            composable(Screen.Alerts.route) {
                AlertsScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // Trade History
            composable(Screen.TradeHistory.route) {
                TradeHistoryScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // HyperLiquid
            composable(Screen.HyperLiquid.route) {
                HyperLiquidScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // Orderbook
            composable(Screen.Orderbook.route) { backStackEntry ->
                val symbol = backStackEntry.arguments?.getString("symbol") ?: "BTCUSDT"
                OrderbookScreen(
                    symbol = symbol,
                    onNavigateBack = { navController.popBackStack() },
                    onPriceSelected = { /* Handle price selection */ }
                )
            }
            
            // Market Hub
            composable(Screen.MarketHub.route) {
                MarketHubScreen(
                    onNavigateBack = { navController.popBackStack() },
                    onCoinSelected = { symbol -> 
                        navController.navigate(Screen.Charts.createRoute(symbol))
                    }
                )
            }
            
            // Advanced Trading
            composable(Screen.AdvancedTrading.route) { backStackEntry ->
                val symbol = backStackEntry.arguments?.getString("symbol") ?: "BTCUSDT"
                AdvancedTradingScreen(
                    symbol = symbol,
                    onNavigateBack = { navController.popBackStack() },
                    onOpenOrderbook = { navController.navigate(Screen.Orderbook.createRoute(symbol)) },
                    onOpenChart = { navController.navigate(Screen.Charts.createRoute(symbol)) }
                )
            }
            
            // More Menu
            composable(Screen.More.route) {
                MoreScreen(
                    onNavigateBack = { navController.popBackStack() },
                    onNavigateTo = { destination ->
                        when (destination) {
                            "wallet" -> navController.navigate(Screen.Wallet.route)
                            "alerts" -> navController.navigate(Screen.Alerts.route)
                            "history" -> navController.navigate(Screen.TradeHistory.route)
                            "hyperliquid" -> navController.navigate(Screen.HyperLiquid.route)
                            "market_hub" -> navController.navigate(Screen.MarketHub.route)
                            "orderbook" -> navController.navigate(Screen.Orderbook.createRoute("BTCUSDT"))
                            "stats" -> navController.navigate(Screen.Stats.route)
                            "ai" -> navController.navigate(Screen.AIAssistant.route)
                            "strategies" -> navController.navigate(Screen.Strategies.route)
                            "backtest" -> navController.navigate(Screen.Backtest.route)
                            "spot" -> navController.navigate(Screen.SpotTrading.route)
                            "copy_trading" -> navController.navigate(Screen.CopyTrading.route)
                        }
                    }
                )
            }
            
            // Copy Trading
            composable(Screen.CopyTrading.route) {
                CopyTradingScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // AI Assistant
            composable(Screen.AIAssistant.route) {
                AIAssistantScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // Stats
            composable(Screen.Stats.route) {
                StatsScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // Spot Trading
            composable(Screen.SpotTrading.route) {
                SpotTradingScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // Strategies
            composable(Screen.Strategies.route) {
                StrategiesScreen(
                    onNavigateBack = { navController.popBackStack() },
                    onNavigateToSettings = { strategyCode ->
                        navController.navigate(Screen.StrategySettings.createRoute(strategyCode))
                    }
                )
            }
            
            // Backtest
            composable(Screen.Backtest.route) {
                BacktestScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            // Strategy Settings (per-strategy, per-side via API)
            composable(Screen.StrategySettings.route) { backStackEntry ->
                val strategyCode = backStackEntry.arguments?.getString("strategy") ?: "oi"
                StrategySettingsScreen(
                    strategyCode = strategyCode,
                    onBack = { navController.popBackStack() }
                )
            }
            
            // Manual Trading
            composable(Screen.ManualTrading.route) { backStackEntry ->
                val symbol = backStackEntry.arguments?.getString("symbol") ?: "BTCUSDT"
                ManualTradingScreen(
                    symbol = symbol,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
