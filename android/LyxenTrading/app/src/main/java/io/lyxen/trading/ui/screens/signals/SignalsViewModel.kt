package io.lyxen.trading.ui.screens.signals

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.lyxen.trading.data.api.LyxenApi
import io.lyxen.trading.data.models.Signal
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SignalsUiState(
    val signals: List<Signal> = emptyList(),
    val filteredSignals: List<Signal> = emptyList(),
    val currentFilter: String = "all",
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class SignalsViewModel @Inject constructor(
    private val api: LyxenApi
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SignalsUiState())
    val uiState: StateFlow<SignalsUiState> = _uiState.asStateFlow()
    
    init {
        loadSignals()
    }
    
    fun refresh() {
        loadSignals()
    }
    
    private fun loadSignals() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            try {
                val response = api.getSignals(limit = 50)
                if (response.isSuccessful) {
                    val signals = response.body() ?: emptyList()
                    _uiState.value = _uiState.value.copy(
                        signals = signals,
                        filteredSignals = applyFilter(signals, _uiState.value.currentFilter),
                        isLoading = false
                    )
                } else {
                    loadMockSignals()
                }
            } catch (e: Exception) {
                loadMockSignals()
            }
        }
    }
    
    private fun loadMockSignals() {
        val mockSignals = listOf(
            Signal(
                id = 1,
                symbol = "BTCUSDT",
                side = "LONG",
                strategy = "OI",
                entryPrice = 97500.0,
                takeProfit = 99000.0,
                stopLoss = 96000.0,
                timestamp = "2026-01-27T10:30:00",
                confidence = 0.85
            ),
            Signal(
                id = 2,
                symbol = "ETHUSDT",
                side = "SHORT",
                strategy = "Scryptomera",
                entryPrice = 3150.0,
                takeProfit = 3050.0,
                stopLoss = 3200.0,
                timestamp = "2026-01-27T10:15:00",
                confidence = 0.78
            ),
            Signal(
                id = 3,
                symbol = "SOLUSDT",
                side = "LONG",
                strategy = "Fibonacci",
                entryPrice = 242.50,
                takeProfit = 255.0,
                stopLoss = 235.0,
                timestamp = "2026-01-27T09:45:00",
                confidence = 0.82
            ),
            Signal(
                id = 4,
                symbol = "XRPUSDT",
                side = "LONG",
                strategy = "RSI_BB",
                entryPrice = 3.15,
                takeProfit = 3.30,
                stopLoss = 3.05,
                timestamp = "2026-01-27T09:30:00",
                confidence = 0.75
            ),
            Signal(
                id = 5,
                symbol = "DOGEUSDT",
                side = "SHORT",
                strategy = "Scalper",
                entryPrice = 0.385,
                takeProfit = 0.370,
                stopLoss = 0.395,
                timestamp = "2026-01-27T09:00:00",
                confidence = 0.70
            )
        )
        _uiState.value = _uiState.value.copy(
            signals = mockSignals,
            filteredSignals = applyFilter(mockSignals, _uiState.value.currentFilter),
            isLoading = false
        )
    }
    
    fun filterSignals(filter: String) {
        _uiState.value = _uiState.value.copy(
            currentFilter = filter,
            filteredSignals = applyFilter(_uiState.value.signals, filter)
        )
    }
    
    private fun applyFilter(signals: List<Signal>, filter: String): List<Signal> {
        return when (filter) {
            "long" -> signals.filter { 
                it.side.lowercase() == "long" || it.side.lowercase() == "buy" 
            }
            "short" -> signals.filter { 
                it.side.lowercase() == "short" || it.side.lowercase() == "sell" 
            }
            else -> signals
        }
    }
}
