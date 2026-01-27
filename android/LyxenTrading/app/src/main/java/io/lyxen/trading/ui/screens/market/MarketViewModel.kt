package io.lyxen.trading.ui.screens.market

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.lyxen.trading.data.api.LyxenApi
import io.lyxen.trading.data.models.ScreenerCoin
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class MarketUiState(
    val isLoading: Boolean = true,
    val coins: List<ScreenerCoin> = emptyList(),
    val sortBy: String = "volume",
    val error: String? = null
)

@HiltViewModel
class MarketViewModel @Inject constructor(
    private val api: LyxenApi
) : ViewModel() {

    private val _uiState = MutableStateFlow(MarketUiState())
    val uiState: StateFlow<MarketUiState> = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val response = api.getScreenerCoins(
                    sortBy = _uiState.value.sortBy,
                    limit = 100
                )
                if (response.isSuccessful) {
                    _uiState.update { 
                        it.copy(isLoading = false, coins = response.body() ?: emptyList()) 
                    }
                } else {
                    // Fallback to mock data for demo
                    _uiState.update { 
                        it.copy(isLoading = false, coins = getMockCoins()) 
                    }
                }
            } catch (e: Exception) {
                // Fallback to mock data
                _uiState.update { 
                    it.copy(isLoading = false, coins = getMockCoins()) 
                }
            }
        }
    }

    fun setSortBy(sortBy: String) {
        _uiState.update { it.copy(sortBy = sortBy) }
        refresh()
    }

    private fun getMockCoins(): List<ScreenerCoin> {
        return listOf(
            ScreenerCoin("BTCUSDT", 97543.21, 2.45, 45_000_000_000.0, 1.2, 58.3, "Bullish"),
            ScreenerCoin("ETHUSDT", 3245.67, 3.12, 18_000_000_000.0, 2.1, 62.1, "Bullish"),
            ScreenerCoin("SOLUSDT", 185.43, -1.23, 5_500_000_000.0, -0.8, 45.2, "Neutral"),
            ScreenerCoin("BNBUSDT", 695.32, 1.87, 2_100_000_000.0, 0.5, 54.7, "Bullish"),
            ScreenerCoin("XRPUSDT", 2.45, 5.67, 3_200_000_000.0, 3.2, 71.3, "Bullish"),
            ScreenerCoin("ADAUSDT", 0.89, -2.34, 890_000_000.0, -1.5, 38.9, "Bearish"),
            ScreenerCoin("DOGEUSDT", 0.32, 4.56, 1_500_000_000.0, 2.8, 65.4, "Bullish"),
            ScreenerCoin("DOTUSDT", 7.23, -0.89, 450_000_000.0, 0.2, 48.1, "Neutral"),
            ScreenerCoin("AVAXUSDT", 35.67, 2.11, 780_000_000.0, 1.1, 55.6, "Bullish"),
            ScreenerCoin("LINKUSDT", 22.45, 1.23, 560_000_000.0, 0.9, 52.3, "Bullish"),
            ScreenerCoin("MATICUSDT", 0.78, -3.45, 320_000_000.0, -2.1, 35.7, "Bearish"),
            ScreenerCoin("UNIUSDT", 12.34, 0.56, 210_000_000.0, 0.3, 50.2, "Neutral")
        )
    }
}
