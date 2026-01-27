package io.enliko.trading.ui.screens.portfolio

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.models.Balance
import io.enliko.trading.data.models.Position
import io.enliko.trading.data.models.TradeStats
import io.enliko.trading.data.repository.PreferencesRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PortfolioUiState(
    val isLoading: Boolean = true,
    val balance: Balance? = null,
    val positions: List<Position> = emptyList(),
    val stats: TradeStats? = null,
    val error: String? = null,
    val accountType: String = "demo",
    val exchange: String = "bybit"
)

@HiltViewModel
class PortfolioViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(PortfolioUiState())
    val uiState: StateFlow<PortfolioUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(
                preferencesRepository.accountType,
                preferencesRepository.exchange
            ) { accountType, exchange ->
                Pair(accountType, exchange)
            }.collect { (accountType, exchange) ->
                _uiState.update { it.copy(accountType = accountType, exchange = exchange) }
                refresh()
            }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val accountType = _uiState.value.accountType
                
                // Fetch all data in parallel
                val balanceResult = api.getBalance(accountType)
                val positionsResult = api.getPositions(accountType)
                val statsResult = api.getTradeStats(accountType)
                
                _uiState.update { state ->
                    state.copy(
                        isLoading = false,
                        balance = balanceResult.body(),
                        positions = positionsResult.body() ?: emptyList(),
                        stats = statsResult.body()
                    )
                }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(isLoading = false, error = e.message) 
                }
            }
        }
    }

    fun switchAccountType(accountType: String) {
        viewModelScope.launch {
            preferencesRepository.saveAccountType(accountType)
            try {
                api.switchAccountType(mapOf("account_type" to accountType))
            } catch (e: Exception) {
                // Local save already done
            }
        }
    }

    fun closePosition(symbol: String, side: String) {
        viewModelScope.launch {
            try {
                val request = io.enliko.trading.data.api.ClosePositionRequest(
                    symbol = symbol,
                    side = side,
                    accountType = _uiState.value.accountType
                )
                api.closePosition(request)
                refresh()
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message) }
            }
        }
    }

    fun closeAllPositions() {
        viewModelScope.launch {
            try {
                api.closeAllPositions(_uiState.value.accountType)
                refresh()
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message) }
            }
        }
    }
}
