package io.enliko.trading

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.hilt.navigation.compose.hiltViewModel
import dagger.hilt.android.AndroidEntryPoint
import io.enliko.trading.ui.navigation.EnlikoNavHost
import io.enliko.trading.ui.screens.auth.AuthViewModel
import io.enliko.trading.ui.theme.EnlikoTradingTheme

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        setContent {
            val authViewModel: AuthViewModel = hiltViewModel()
            val isLoggedIn by authViewModel.isLoggedIn.collectAsState()
            val currentLanguage by authViewModel.currentLanguage.collectAsState()
            
            EnlikoTradingTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    EnlikoNavHost(
                        isLoggedIn = isLoggedIn,
                        currentLanguage = currentLanguage
                    )
                }
            }
        }
    }
}
