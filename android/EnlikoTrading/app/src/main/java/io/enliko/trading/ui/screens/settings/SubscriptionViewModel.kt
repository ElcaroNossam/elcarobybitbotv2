package io.enliko.trading.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SubscriptionUiState(
    val elcBalance: Double = 0.0,
    val currentPlan: String? = null,
    val expiryDate: String? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val paymentSuccess: Boolean = false
)

@HiltViewModel
class SubscriptionViewModel @Inject constructor() : ViewModel() {
    
    private val _uiState = MutableStateFlow(SubscriptionUiState())
    val uiState: StateFlow<SubscriptionUiState> = _uiState.asStateFlow()
    
    init {
        loadSubscriptionData()
    }
    
    private fun loadSubscriptionData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                // TODO: Fetch from API
                kotlinx.coroutines.delay(500)
                
                // Mock data
                _uiState.update { it.copy(
                    elcBalance = 150.0,
                    currentPlan = "free",
                    expiryDate = null,
                    isLoading = false
                )}
            } catch (e: Exception) {
                _uiState.update { it.copy(
                    isLoading = false,
                    error = e.message
                )}
            }
        }
    }
    
    fun payWithELC(plan: String, duration: String, amount: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            try {
                // TODO: Call payment API
                kotlinx.coroutines.delay(1000)
                
                // Simulate successful payment
                _uiState.update { state ->
                    state.copy(
                        elcBalance = state.elcBalance - amount,
                        currentPlan = plan,
                        expiryDate = calculateExpiry(duration),
                        isLoading = false,
                        paymentSuccess = true
                    )
                }
                
                // Reset success flag after delay
                kotlinx.coroutines.delay(2000)
                _uiState.update { it.copy(paymentSuccess = false) }
                
            } catch (e: Exception) {
                _uiState.update { it.copy(
                    isLoading = false,
                    error = e.message ?: "Payment failed"
                )}
            }
        }
    }
    
    private fun calculateExpiry(duration: String): String {
        val months = when (duration) {
            "1m" -> 1
            "3m" -> 3
            "6m" -> 6
            "1y" -> 12
            else -> 1
        }
        // Simple mock calculation
        return "2026-${(2 + months).toString().padStart(2, '0')}-15"
    }
    
    fun refreshBalance() {
        viewModelScope.launch {
            try {
                // TODO: Fetch updated balance from API
                kotlinx.coroutines.delay(500)
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message) }
            }
        }
    }
    
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
