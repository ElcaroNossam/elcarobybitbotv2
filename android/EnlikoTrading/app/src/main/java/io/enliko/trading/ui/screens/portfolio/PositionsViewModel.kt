package io.enliko.trading.ui.screens.portfolio

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.api.PositionData
import io.enliko.trading.data.repository.PreferencesRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PositionsUiState(
    val isLoading: Boolean = true,
    val isRefreshing: Boolean = false,
    val positions: List<PositionData> = emptyList(),
    val exchange: String = "bybit",
    val accountType: String = "demo",
    val error: String? = null
)

@HiltViewModel
class PositionsViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(PositionsUiState())
    val uiState: StateFlow<PositionsUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(
                preferencesRepository.exchange,
                preferencesRepository.accountType
            ) { exchange, accountType ->
                Pair(exchange, accountType)
            }.collect { (exchange, accountType) ->
                _uiState.update { it.copy(exchange = exchange, accountType = accountType) }
                loadPositions()
            }
        }
    }

    fun loadPositions() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = it.positions.isEmpty(), error = null) }
            try {
                val response = api.getPositions(
                    exchange = _uiState.value.exchange,
                    accountType = _uiState.value.accountType
                )
                if (response.isSuccessful) {
                    val positions = response.body() ?: emptyList()
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isRefreshing = false,
                            positions = positions,
                            error = null
                        )
                    }
                } else {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isRefreshing = false,
                            error = "Server error: ${response.code()}"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        isRefreshing = false,
                        positions = emptyList(),
                        error = if (e.message?.contains("Unable to resolve host") == true)
                            "No internet connection"
                        else e.message ?: "Unknown error"
                    )
                }
            }
        }
    }

    fun refresh() {
        _uiState.update { it.copy(isRefreshing = true) }
        loadPositions()
    }

    fun closePosition(symbol: String, side: String) {
        viewModelScope.launch {
            try {
                val request = io.enliko.trading.data.api.ClosePositionRequest(
                    symbol = symbol,
                    side = side,
                    exchange = _uiState.value.exchange,
                    accountType = _uiState.value.accountType
                )
                val response = api.closePosition(request)
                if (response.isSuccessful && response.body()?.success == true) {
                    // Refresh positions after close
                    loadPositions()
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(error = "Failed to close: ${e.message}") }
            }
        }
    }

    fun closeAllPositions() {
        viewModelScope.launch {
            try {
                val response = api.closeAllPositions(
                    exchange = _uiState.value.exchange,
                    accountType = _uiState.value.accountType
                )
                if (response.isSuccessful && response.body()?.success == true) {
                    loadPositions()
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(error = "Failed to close all: ${e.message}") }
            }
        }
    }
}
