package io.enliko.trading.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * StrategySettingsViewModel - Manages strategy settings state
 * Matching iOS StrategySettingsView state management
 */
@HiltViewModel
class StrategySettingsViewModel @Inject constructor() : ViewModel() {
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _saveSuccess = MutableStateFlow(false)
    val saveSuccess: StateFlow<Boolean> = _saveSuccess.asStateFlow()
    
    // Long side settings
    private val _longSettings = MutableStateFlow(SideSettings())
    val longSettings: StateFlow<SideSettings> = _longSettings.asStateFlow()
    
    // Short side settings
    private val _shortSettings = MutableStateFlow(SideSettings())
    val shortSettings: StateFlow<SideSettings> = _shortSettings.asStateFlow()
    
    fun loadSettings(strategyCode: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            try {
                // TODO: Load from API
                // For now, use defaults
                kotlinx.coroutines.delay(500)
                
                // Mock data - in production, fetch from /api/strategy-settings/{strategy}
                _longSettings.value = SideSettings(
                    enabled = true,
                    percent = 1.0,
                    tpPercent = 8.0,
                    slPercent = 3.0,
                    leverage = 10
                )
                
                _shortSettings.value = SideSettings(
                    enabled = true,
                    percent = 1.0,
                    tpPercent = 8.0,
                    slPercent = 3.0,
                    leverage = 10
                )
                
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load settings"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun updateLongSettings(settings: SideSettings) {
        _longSettings.value = settings
    }
    
    fun updateShortSettings(settings: SideSettings) {
        _shortSettings.value = settings
    }
    
    fun saveSettings(strategyCode: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            try {
                // TODO: Save to API
                // POST /api/strategy-settings/{strategy}
                kotlinx.coroutines.delay(800)
                
                _saveSuccess.value = true
                
                // Reset after delay
                kotlinx.coroutines.delay(2000)
                _saveSuccess.value = false
                
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to save settings"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun clearError() {
        _error.value = null
    }
}
