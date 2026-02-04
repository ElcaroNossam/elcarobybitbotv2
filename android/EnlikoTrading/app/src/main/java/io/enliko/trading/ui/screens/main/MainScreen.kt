package io.enliko.trading.ui.screens.main

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import io.enliko.trading.ui.screens.portfolio.PortfolioScreen
import io.enliko.trading.ui.screens.trading.TradingScreen
import io.enliko.trading.ui.screens.market.MarketScreen
import io.enliko.trading.ui.screens.settings.SettingsScreen
import io.enliko.trading.ui.screens.settings.NotificationSettingsScreen
import io.enliko.trading.ui.screens.signals.SignalsScreen
import io.enliko.trading.util.LocalStrings

enum class MainTab(
    val route: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector,
    val labelKey: String
) {
    PORTFOLIO("portfolio", Icons.Filled.AccountBalance, Icons.Outlined.AccountBalance, "portfolio"),
    TRADING("trading", Icons.Filled.TrendingUp, Icons.Outlined.TrendingUp, "trading"),
    SIGNALS("signals", Icons.Filled.Notifications, Icons.Outlined.Notifications, "signals"),
    MARKET("market", Icons.Filled.ShowChart, Icons.Outlined.ShowChart, "market"),
    SETTINGS("settings", Icons.Filled.Settings, Icons.Outlined.Settings, "settings")
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    onLogout: () -> Unit,
    onNavigateToActivity: () -> Unit = {},
    onNavigateToSpot: () -> Unit = {}
) {
    val strings = LocalStrings.current
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination
    
    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
                contentColor = MaterialTheme.colorScheme.onSurface
            ) {
                MainTab.entries.forEach { tab ->
                    val selected = currentDestination?.hierarchy?.any { it.route == tab.route } == true
                    val label = when (tab.labelKey) {
                        "portfolio" -> strings.portfolio
                        "trading" -> strings.trading
                        "signals" -> strings.signals
                        "market" -> strings.market
                        "settings" -> strings.settings
                        else -> tab.labelKey
                    }
                    
                    NavigationBarItem(
                        icon = {
                            Icon(
                                imageVector = if (selected) tab.selectedIcon else tab.unselectedIcon,
                                contentDescription = label
                            )
                        },
                        label = { Text(label, maxLines = 1) },
                        selected = selected,
                        onClick = {
                            navController.navigate(tab.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = MaterialTheme.colorScheme.primary,
                            selectedTextColor = MaterialTheme.colorScheme.primary,
                            indicatorColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f),
                            unselectedIconColor = MaterialTheme.colorScheme.onSurfaceVariant,
                            unselectedTextColor = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = MainTab.PORTFOLIO.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(MainTab.PORTFOLIO.route) {
                PortfolioScreen()
            }
            composable(MainTab.TRADING.route) {
                TradingScreen()
            }
            composable(MainTab.SIGNALS.route) {
                SignalsScreen()
            }
            composable(MainTab.MARKET.route) {
                MarketScreen()
            }
            composable(MainTab.SETTINGS.route) {
                SettingsScreen(
                    onLogout = onLogout,
                    onNavigateToNotifications = {
                        navController.navigate("notifications")
                    },
                    onNavigateToActivity = onNavigateToActivity,
                    onNavigateToSpot = onNavigateToSpot
                )
            }
            composable("notifications") {
                NotificationSettingsScreen(
                    strings = strings,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
