package io.enliko.trading.ui.screens.trading

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.api.OrderData
import io.enliko.trading.data.repository.PreferencesRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class TradingUiState(
    val isLoading: Boolean = false,
    val orders: List<OrderData> = emptyList(),
    val selectedSymbol: String = "BTCUSDT",
    val leverage: Int = 10,
    val slPercent: Double = 30.0,
    val tpPercent: Double = 25.0,
    val orderType: String = "market",
    val error: String? = null,
    val accountType: String = "demo"
)

@HiltViewModel
class TradingViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(TradingUiState())
    val uiState: StateFlow<TradingUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            preferencesRepository.accountType.collect { accountType ->
                _uiState.update { it.copy(accountType = accountType) }
                loadOrders()
            }
        }
    }

    fun loadOrders() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val response = api.getOrders(_uiState.value.accountType)
                if (response.isSuccessful && response.body()?.success == true) {
                    _uiState.update { 
                        it.copy(isLoading = false, orders = response.body()?.data ?: emptyList()) 
                    }
                } else {
                    _uiState.update { 
                        it.copy(isLoading = false, error = response.body()?.error ?: "Failed to load orders") 
                    }
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    fun setSymbol(symbol: String) {
        _uiState.update { it.copy(selectedSymbol = symbol) }
    }

    fun setLeverage(leverage: Int) {
        _uiState.update { it.copy(leverage = leverage) }
    }

    fun setSlPercent(sl: Double) {
        _uiState.update { it.copy(slPercent = sl) }
    }

    fun setTpPercent(tp: Double) {
        _uiState.update { it.copy(tpPercent = tp) }
    }

    fun setOrderType(type: String) {
        _uiState.update { it.copy(orderType = type) }
    }
}
