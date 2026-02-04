package io.enliko.trading.ui.screens.strategies

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.EnlikoApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * StrategiesViewModel - Matching iOS StrategiesView state management
 */

data class StrategiesUiState(
    val myStrategies: List<TradingStrategy> = emptyList(),
    val marketplaceStrategies: List<MarketplaceStrategy> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class StrategiesViewModel @Inject constructor(
    private val api: EnlikoApi
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(StrategiesUiState())
    val uiState: StateFlow<StrategiesUiState> = _uiState.asStateFlow()
    
    init {
        loadMyStrategies()
        loadMarketplaceStrategies()
    }
    
    private fun loadMyStrategies() {
        // Load predefined strategies matching iOS
        val defaultStrategies = listOf(
            TradingStrategy(
                name = "OI",
                description = "Open Interest based signals - tracks large position changes",
                isEnabled = true
            ),
            TradingStrategy(
                name = "Scryptomera",
                description = "Volume delta analysis with trend confirmation",
                isEnabled = true
            ),
            TradingStrategy(
                name = "Scalper",
                description = "Quick scalping strategy for high frequency trading",
                isEnabled = false
            ),
            TradingStrategy(
                name = "Elcaro",
                description = "AI-powered multi-indicator strategy",
                isEnabled = true
            ),
            TradingStrategy(
                name = "Fibonacci",
                description = "Fibonacci retracement levels with trend analysis",
                isEnabled = false
            ),
            TradingStrategy(
                name = "RSI_BB",
                description = "RSI with Bollinger Bands for reversal detection",
                isEnabled = true
            )
        )
        
        _uiState.update { it.copy(myStrategies = defaultStrategies) }
    }
    
    private fun loadMarketplaceStrategies() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                // TODO: Load from API
                // val strategies = api.getMarketplaceStrategies()
                
                // For now, empty list (marketplace coming soon)
                _uiState.update { 
                    it.copy(
                        marketplaceStrategies = emptyList(),
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        error = e.message
                    )
                }
            }
        }
    }
    
    fun toggleStrategy(strategyName: String, enabled: Boolean) {
        _uiState.update { state ->
            state.copy(
                myStrategies = state.myStrategies.map { strategy ->
                    if (strategy.name == strategyName) {
                        strategy.copy(isEnabled = enabled)
                    } else {
                        strategy
                    }
                }
            )
        }
        
        // TODO: Sync with server
        viewModelScope.launch {
            try {
                // api.updateStrategySettings(strategyName, mapOf("enabled" to enabled))
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
    
    fun refreshMarketplace() {
        loadMarketplaceStrategies()
    }
}
