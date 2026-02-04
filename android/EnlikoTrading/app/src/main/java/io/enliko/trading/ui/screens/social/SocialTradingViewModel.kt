package io.enliko.trading.ui.screens.social

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.util.AppLogger
import io.enliko.trading.util.LogCategory
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SocialTradingUiState(
    val topTraders: List<TopTrader> = emptyList(),
    val followedTraders: List<TopTrader> = emptyList(),
    val selectedTimeframe: SocialTimeframe = SocialTimeframe.MONTH,
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class SocialTradingViewModel @Inject constructor(
    // TODO: Add social trading service when backend is ready
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SocialTradingUiState())
    val uiState: StateFlow<SocialTradingUiState> = _uiState.asStateFlow()
    
    init {
        loadData()
    }
    
    private fun loadData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            // Simulate API call with mock data
            delay(500)
            
            val mockTraders = listOf(
                TopTrader(
                    id = "1",
                    username = "CryptoWhale",
                    rank = 1,
                    roi30d = 127.5,
                    winRate = 78.4,
                    totalTrades = 342,
                    followers = 12500,
                    maxDrawdown = -8.2,
                    strategies = listOf("OI", "Scalper"),
                    isVerified = true
                ),
                TopTrader(
                    id = "2",
                    username = "BTCMaster",
                    rank = 2,
                    roi30d = 95.3,
                    winRate = 72.1,
                    totalTrades = 189,
                    followers = 8700,
                    maxDrawdown = -12.5,
                    strategies = listOf("Fibonacci"),
                    isVerified = true
                ),
                TopTrader(
                    id = "3",
                    username = "AlphaTrader",
                    rank = 3,
                    roi30d = 82.1,
                    winRate = 68.9,
                    totalTrades = 456,
                    followers = 6200,
                    maxDrawdown = -15.3,
                    strategies = listOf("Scryptomera", "RSI"),
                    isVerified = false
                ),
                TopTrader(
                    id = "4",
                    username = "SwingKing",
                    rank = 4,
                    roi30d = 67.8,
                    winRate = 65.2,
                    totalTrades = 123,
                    followers = 4100,
                    maxDrawdown = -18.7,
                    strategies = listOf("Elcaro"),
                    isVerified = true
                ),
                TopTrader(
                    id = "5",
                    username = "DayTraderPro",
                    rank = 5,
                    roi30d = 54.2,
                    winRate = 61.8,
                    totalTrades = 678,
                    followers = 3200,
                    maxDrawdown = -22.1,
                    strategies = listOf("Scalper", "OI"),
                    isVerified = false
                )
            )
            
            _uiState.update { it.copy(
                topTraders = mockTraders,
                isLoading = false
            )}
            
            AppLogger.info(LogCategory.GENERAL, "Loaded ${mockTraders.size} top traders")
        }
    }
    
    fun setTimeframe(timeframe: SocialTimeframe) {
        _uiState.update { it.copy(selectedTimeframe = timeframe) }
        loadData()
    }
    
    fun refresh() {
        loadData()
    }
    
    fun followTrader(traderId: String) {
        viewModelScope.launch {
            val trader = _uiState.value.topTraders.find { it.id == traderId }
            trader?.let {
                _uiState.update { state ->
                    state.copy(
                        followedTraders = state.followedTraders + it
                    )
                }
                AppLogger.info(LogCategory.GENERAL, "Followed trader: ${trader.displayName}")
            }
        }
    }
    
    fun unfollowTrader(traderId: String) {
        viewModelScope.launch {
            _uiState.update { state ->
                state.copy(
                    followedTraders = state.followedTraders.filter { it.id != traderId }
                )
            }
            AppLogger.info(LogCategory.GENERAL, "Unfollowed trader: $traderId")
        }
    }
    
    fun configureCopy(traderId: String) {
        // TODO: Show copy settings dialog
        AppLogger.info(LogCategory.GENERAL, "Configure copy for: $traderId")
    }
}
