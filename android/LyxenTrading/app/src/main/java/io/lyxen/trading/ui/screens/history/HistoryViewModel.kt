package io.lyxen.trading.ui.screens.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.lyxen.trading.data.api.LyxenApi
import io.lyxen.trading.data.models.Trade
import io.lyxen.trading.data.repository.PreferencesRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HistoryUiState(
    val trades: List<Trade> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class HistoryViewModel @Inject constructor(
    private val api: LyxenApi,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(HistoryUiState())
    val uiState: StateFlow<HistoryUiState> = _uiState.asStateFlow()
    
    init {
        loadTrades()
    }
    
    fun refresh() {
        loadTrades()
    }
    
    private fun loadTrades() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            try {
                val accountType = preferencesRepository.accountType.first()
                
                val response = api.getTrades(
                    accountType = accountType,
                    limit = 100
                )
                
                if (response.isSuccessful) {
                    val trades = response.body() ?: emptyList()
                    _uiState.value = _uiState.value.copy(
                        trades = trades,
                        isLoading = false
                    )
                } else {
                    loadMockTrades()
                }
            } catch (e: Exception) {
                loadMockTrades()
            }
        }
    }
    
    private fun loadMockTrades() {
        val mockTrades = listOf(
            Trade(
                id = 1,
                symbol = "BTCUSDT",
                side = "LONG",
                entryPrice = 96500.0,
                exitPrice = 98200.0,
                pnl = 127.50,
                pnlPercent = 1.76,
                strategy = "OI",
                exitReason = "TP",
                timestamp = "2026-01-27T09:30:00"
            ),
            Trade(
                id = 2,
                symbol = "ETHUSDT",
                side = "SHORT",
                entryPrice = 3180.0,
                exitPrice = 3220.0,
                pnl = -35.20,
                pnlPercent = -1.26,
                strategy = "Scryptomera",
                exitReason = "SL",
                timestamp = "2026-01-27T08:15:00"
            ),
            Trade(
                id = 3,
                symbol = "SOLUSDT",
                side = "LONG",
                entryPrice = 235.0,
                exitPrice = 248.50,
                pnl = 89.30,
                pnlPercent = 5.74,
                strategy = "Fibonacci",
                exitReason = "TP",
                timestamp = "2026-01-26T22:45:00"
            ),
            Trade(
                id = 4,
                symbol = "XRPUSDT",
                side = "LONG",
                entryPrice = 3.05,
                exitPrice = 3.18,
                pnl = 42.60,
                pnlPercent = 4.26,
                strategy = "RSI_BB",
                exitReason = "TP",
                timestamp = "2026-01-26T18:20:00"
            ),
            Trade(
                id = 5,
                symbol = "DOGEUSDT",
                side = "SHORT",
                entryPrice = 0.395,
                exitPrice = 0.378,
                pnl = 28.50,
                pnlPercent = 4.30,
                strategy = "Scalper",
                exitReason = "TP",
                timestamp = "2026-01-26T14:10:00"
            ),
            Trade(
                id = 6,
                symbol = "AVAXUSDT",
                side = "LONG",
                entryPrice = 38.50,
                exitPrice = 37.20,
                pnl = -21.30,
                pnlPercent = -3.38,
                strategy = "OI",
                exitReason = "SL",
                timestamp = "2026-01-26T10:05:00"
            )
        )
        
        _uiState.value = _uiState.value.copy(
            trades = mockTrades,
            isLoading = false
        )
    }
}
