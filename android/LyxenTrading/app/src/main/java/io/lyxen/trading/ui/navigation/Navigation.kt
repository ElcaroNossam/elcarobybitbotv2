package io.lyxen.trading.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import io.lyxen.trading.ui.screens.auth.LoginScreen
import io.lyxen.trading.ui.screens.main.MainScreen
import io.lyxen.trading.util.AppLanguage
import io.lyxen.trading.util.ProvideStrings

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Register : Screen("register")
    object Main : Screen("main")
    object StrategySettings : Screen("strategy_settings/{strategy}") {
        fun createRoute(strategy: String) = "strategy_settings/$strategy"
    }
}

@Composable
fun LyxenNavHost(
    isLoggedIn: Boolean,
    currentLanguage: String
) {
    val navController = rememberNavController()
    val language = AppLanguage.fromCode(currentLanguage)
    
    ProvideStrings(language = language) {
        NavHost(
            navController = navController,
            startDestination = if (isLoggedIn) Screen.Main.route else Screen.Login.route
        ) {
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
                    }
                )
            }
        }
    }
}
