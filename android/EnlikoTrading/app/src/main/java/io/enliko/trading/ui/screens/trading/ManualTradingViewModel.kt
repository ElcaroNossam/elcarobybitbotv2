package io.enliko.trading.ui.screens.trading

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.*
import io.enliko.trading.data.repository.PreferencesRepository
import io.enliko.trading.services.NotificationService
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Manual Trading State
 */
data class ManualTradingUiState(
    val isLoading: Boolean = false,
    val symbol: String = "BTCUSDT",
    val currentPrice: Double = 0.0,
    val side: String = "Buy", // "Buy" or "Sell"
    val orderType: String = "Market", // "Market" or "Limit"
    val amountUsdt: Double = 0.0,
    val qty: Double = 0.0,
    val limitPrice: Double? = null,
    val leverage: Int = 10,
    val takeProfit: Double? = null,
    val stopLoss: Double? = null,
    val tpPercent: Double? = null,
    val slPercent: Double? = null,
    val useTpSlPercent: Boolean = true, // Toggle between absolute and percent
    val availableBalance: Double = 0.0,
    val accountType: String = "demo",
    val exchange: String = "bybit",
    val error: String? = null,
    val successMessage: String? = null,
    val isOrderPlaced: Boolean = false,
    // Symbol search
    val availableSymbols: List<String> = defaultSymbols,
    val searchQuery: String = "",
    val filteredSymbols: List<String> = defaultSymbols
) {
    companion object {
        val defaultSymbols = listOf(
            "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT",
            "MATICUSDT", "UNIUSDT", "LTCUSDT", "ATOMUSDT", "NEARUSDT",
            "APTUSDT", "ARBUSDT", "OPUSDT", "SUIUSDT", "WLDUSDT"
        )
    }
}

@HiltViewModel
class ManualTradingViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val preferencesRepository: PreferencesRepository,
    private val notificationService: NotificationService
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(ManualTradingUiState())
    val uiState: StateFlow<ManualTradingUiState> = _uiState.asStateFlow()
    
    init {
        viewModelScope.launch {
            combine(
                preferencesRepository.accountType,
                preferencesRepository.exchange
            ) { accountType, exchange ->
                Pair(accountType, exchange)
            }.collect { (accountType, exchange) ->
                _uiState.update { 
                    it.copy(accountType = accountType, exchange = exchange)
                }
                loadBalance()
            }
        }
    }
    
    private fun loadBalance() {
        viewModelScope.launch {
            try {
                val response = api.getBalance(
                    exchange = _uiState.value.exchange,
                    accountType = _uiState.value.accountType
                )
                if (response.isSuccessful) {
                    val balance = response.body()?.data
                    _uiState.update {
                        it.copy(availableBalance = balance?.availableBalance ?: 0.0)
                    }
                }
            } catch (_: Exception) {
                // Silent fail
            }
        }
    }
    
    // ==================== SYMBOL SELECTION ====================
    
    fun selectSymbol(symbol: String) {
        _uiState.update { 
            it.copy(symbol = symbol, searchQuery = "", filteredSymbols = ManualTradingUiState.defaultSymbols)
        }
        fetchCurrentPrice()
    }
    
    fun updateSearchQuery(query: String) {
        val filtered = if (query.isBlank()) {
            ManualTradingUiState.defaultSymbols
        } else {
            ManualTradingUiState.defaultSymbols.filter { 
                it.contains(query.uppercase()) 
            }
        }
        _uiState.update { it.copy(searchQuery = query, filteredSymbols = filtered) }
    }
    
    private fun fetchCurrentPrice() {
        viewModelScope.launch {
            try {
                val response = api.getScreenerCoins(limit = 100)
                if (response.isSuccessful) {
                    val coin = response.body()?.find { it.symbol == _uiState.value.symbol }
                    coin?.let {
                        _uiState.update { state ->
                            state.copy(currentPrice = coin.price)
                        }
                    }
                }
            } catch (_: Exception) {
                // Silent fail
            }
        }
    }
    
    // ==================== ORDER PARAMETERS ====================
    
    fun setSide(side: String) {
        _uiState.update { it.copy(side = side) }
        recalculateTpSl()
    }
    
    fun setOrderType(orderType: String) {
        _uiState.update { it.copy(orderType = orderType) }
    }
    
    fun setAmountUsdt(amount: Double) {
        val qty = if (_uiState.value.currentPrice > 0) {
            amount / _uiState.value.currentPrice
        } else 0.0
        _uiState.update { it.copy(amountUsdt = amount, qty = qty) }
    }
    
    fun setQty(qty: Double) {
        val amount = qty * _uiState.value.currentPrice
        _uiState.update { it.copy(qty = qty, amountUsdt = amount) }
    }
    
    fun setLimitPrice(price: Double?) {
        _uiState.update { it.copy(limitPrice = price) }
    }
    
    fun setLeverage(leverage: Int) {
        _uiState.update { it.copy(leverage = leverage.coerceIn(1, 100)) }
    }
    
    fun setTpPercent(percent: Double?) {
        _uiState.update { it.copy(tpPercent = percent) }
        recalculateTpSl()
    }
    
    fun setSlPercent(percent: Double?) {
        _uiState.update { it.copy(slPercent = percent) }
        recalculateTpSl()
    }
    
    fun setTakeProfit(price: Double?) {
        _uiState.update { it.copy(takeProfit = price) }
    }
    
    fun setStopLoss(price: Double?) {
        _uiState.update { it.copy(stopLoss = price) }
    }
    
    fun toggleTpSlMode() {
        _uiState.update { it.copy(useTpSlPercent = !it.useTpSlPercent) }
    }
    
    private fun recalculateTpSl() {
        val state = _uiState.value
        val price = if (state.orderType == "Limit" && state.limitPrice != null) {
            state.limitPrice
        } else {
            state.currentPrice
        }
        
        if (price <= 0) return
        
        val isLong = state.side == "Buy"
        
        state.tpPercent?.let { tpPct ->
            val tp = if (isLong) {
                price * (1 + tpPct / 100)
            } else {
                price * (1 - tpPct / 100)
            }
            _uiState.update { it.copy(takeProfit = tp) }
        }
        
        state.slPercent?.let { slPct ->
            val sl = if (isLong) {
                price * (1 - slPct / 100)
            } else {
                price * (1 + slPct / 100)
            }
            _uiState.update { it.copy(stopLoss = sl) }
        }
    }
    
    // ==================== QUICK AMOUNT BUTTONS ====================
    
    fun setAmountPercent(percent: Int) {
        val amount = _uiState.value.availableBalance * percent / 100
        setAmountUsdt(amount)
    }
    
    // ==================== PLACE ORDER ====================
    
    fun placeOrder() {
        viewModelScope.launch {
            val state = _uiState.value
            
            // Validation
            if (state.amountUsdt <= 0 && state.qty <= 0) {
                _uiState.update { it.copy(error = "Please enter amount") }
                return@launch
            }
            
            if (state.orderType == "Limit" && state.limitPrice == null) {
                _uiState.update { it.copy(error = "Please set limit price") }
                return@launch
            }
            
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            try {
                val request = PlaceOrderRequest(
                    symbol = state.symbol,
                    side = state.side,
                    orderType = state.orderType.lowercase(),
                    qty = if (state.qty > 0) state.qty else null,
                    amountUsdt = if (state.amountUsdt > 0 && state.qty <= 0) state.amountUsdt else null,
                    price = state.limitPrice,
                    leverage = state.leverage,
                    takeProfit = state.takeProfit,
                    stopLoss = state.stopLoss,
                    accountType = state.accountType,
                    exchange = state.exchange
                )
                
                val response = api.placeOrder(
                    exchange = state.exchange,
                    accountType = state.accountType,
                    request = request
                )
                
                if (response.isSuccessful && response.body()?.success == true) {
                    val result = response.body()!!
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            successMessage = "Order placed successfully! ${result.orderId ?: ""}",
                            isOrderPlaced = true
                        )
                    }
                    
                    // Show notification
                    notificationService.showPositionOpenedNotification(
                        symbol = state.symbol,
                        side = state.side,
                        size = result.executedQty ?: state.qty,
                        entryPrice = result.executedPrice ?: state.currentPrice,
                        strategy = "Manual"
                    )
                    
                    // Reload balance
                    loadBalance()
                } else {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = response.body()?.message ?: "Failed to place order"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Network error"
                    )
                }
            }
        }
    }
    
    // ==================== SET LEVERAGE ====================
    
    fun applyLeverage() {
        viewModelScope.launch {
            val state = _uiState.value
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            try {
                val request = SetLeverageRequest(
                    symbol = state.symbol,
                    leverage = state.leverage
                )
                
                val response = api.setLeverage(
                    exchange = state.exchange,
                    accountType = state.accountType,
                    request = request
                )
                
                if (response.isSuccessful && response.body()?.success == true) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            successMessage = "Leverage set to ${state.leverage}x"
                        )
                    }
                } else {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = response.body()?.message ?: "Failed to set leverage"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Network error"
                    )
                }
            }
        }
    }
    
    // ==================== CLEAR MESSAGES ====================
    
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
    
    fun clearSuccess() {
        _uiState.update { it.copy(successMessage = null, isOrderPlaced = false) }
    }
    
    fun clearMessages() {
        _uiState.update { it.copy(error = null, successMessage = null) }
    }
    
    fun resetForm() {
        _uiState.update { 
            it.copy(
                amountUsdt = 0.0,
                qty = 0.0,
                limitPrice = null,
                takeProfit = null,
                stopLoss = null,
                tpPercent = null,
                slPercent = null,
                error = null,
                successMessage = null,
                isOrderPlaced = false
            )
        }
    }
}
