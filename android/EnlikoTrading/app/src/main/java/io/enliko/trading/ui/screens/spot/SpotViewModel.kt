package io.enliko.trading.ui.screens.spot

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.SpotAsset
import io.enliko.trading.data.api.SpotBalance
import io.enliko.trading.services.SpotService
import io.enliko.trading.util.AppLogger
import io.enliko.trading.util.LogCategory
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SpotUiState(
    val balance: SpotBalance? = null,
    val assets: List<SpotAsset> = emptyList(),
    val dcaEnabled: Boolean = false,
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class SpotViewModel @Inject constructor(
    private val spotService: SpotService
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SpotUiState())
    val uiState: StateFlow<SpotUiState> = _uiState.asStateFlow()
    
    init {
        loadData()
    }
    
    private fun loadData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            try {
                // Load balance
                spotService.getBalance()
                    .onSuccess { balance ->
                        _uiState.update { it.copy(balance = balance) }
                    }
                    .onFailure { e ->
                        AppLogger.warning(LogCategory.TRADING, "Failed to load spot balance: ${e.message}")
                    }
                
                // Load assets
                spotService.getAssets()
                    .onSuccess { assets ->
                        _uiState.update { it.copy(
                            assets = assets,
                            isLoading = false
                        )}
                    }
                    .onFailure { e ->
                        _uiState.update { it.copy(
                            isLoading = false,
                            error = e.message
                        )}
                        AppLogger.error(LogCategory.TRADING, "Failed to load spot assets: ${e.message}")
                    }
                
                // Load DCA settings
                spotService.getDcaSettings()
                    .onSuccess { settings ->
                        _uiState.update { it.copy(dcaEnabled = settings.enabled) }
                    }
            } catch (e: Exception) {
                _uiState.update { it.copy(
                    isLoading = false,
                    error = e.message
                )}
                AppLogger.error(LogCategory.TRADING, "Spot load error: ${e.message}")
            }
        }
    }
    
    fun refresh() {
        loadData()
    }
    
    fun toggleDca(enabled: Boolean) {
        viewModelScope.launch {
            spotService.updateDcaSettings(enabled = enabled)
                .onSuccess {
                    _uiState.update { it.copy(dcaEnabled = enabled) }
                    AppLogger.info(LogCategory.TRADING, "Spot DCA ${if (enabled) "enabled" else "disabled"}")
                }
                .onFailure { e ->
                    AppLogger.error(LogCategory.TRADING, "Failed to update DCA: ${e.message}")
                }
        }
    }
    
    fun buySpot(symbol: String, amount: Double, usdtAmount: Double) {
        viewModelScope.launch {
            val finalAmount = if (usdtAmount > 0) null else amount
            val finalUsdt = if (usdtAmount > 0) usdtAmount else null
            
            spotService.buy(symbol, finalAmount, finalUsdt)
                .onSuccess { order ->
                    AppLogger.info(LogCategory.TRADING, "Spot buy order placed: ${order.orderId}")
                    refresh()
                }
                .onFailure { e ->
                    _uiState.update { it.copy(error = "Buy failed: ${e.message}") }
                    AppLogger.error(LogCategory.TRADING, "Spot buy error: ${e.message}")
                }
        }
    }
    
    fun sellSpot(symbol: String, amount: Double) {
        viewModelScope.launch {
            spotService.sell(symbol, amount)
                .onSuccess { order ->
                    AppLogger.info(LogCategory.TRADING, "Spot sell order placed: ${order.orderId}")
                    refresh()
                }
                .onFailure { e ->
                    _uiState.update { it.copy(error = "Sell failed: ${e.message}") }
                    AppLogger.error(LogCategory.TRADING, "Spot sell error: ${e.message}")
                }
        }
    }
}
