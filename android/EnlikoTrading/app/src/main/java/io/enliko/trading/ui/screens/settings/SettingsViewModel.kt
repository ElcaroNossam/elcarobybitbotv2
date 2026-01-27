package io.enliko.trading.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.repository.PreferencesRepository
import io.enliko.trading.data.websocket.WebSocketService
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val language: String = "en",
    val exchange: String = "bybit",
    val accountType: String = "demo",
    val theme: String = "dark",
    val notificationsEnabled: Boolean = true,
    val isLoading: Boolean = false
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val preferencesRepository: PreferencesRepository,
    private val webSocketService: WebSocketService  // CROSS-PLATFORM: Inject for sync
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()
    
    init {
        loadSettings()
    }
    
    private fun loadSettings() {
        viewModelScope.launch {
            combine(
                preferencesRepository.language,
                preferencesRepository.exchange,
                preferencesRepository.accountType,
                preferencesRepository.theme
            ) { lang, exchange, accountType, theme ->
                SettingsUiState(
                    language = lang,
                    exchange = exchange,
                    accountType = accountType,
                    theme = theme
                )
            }.collect { state ->
                _uiState.value = state
            }
        }
    }
    
    fun setLanguage(language: String) {
        viewModelScope.launch {
            val oldLang = _uiState.value.language
            preferencesRepository.saveLanguage(language)
            // Sync with server
            try {
                api.setLanguage(mapOf("language" to language))
                // CROSS-PLATFORM: Send WebSocket sync message
                webSocketService.sendSettingsChange("language", oldLang, language)
            } catch (e: Exception) {
                // Ignore server sync errors
            }
        }
    }
    
    fun setExchange(exchange: String) {
        viewModelScope.launch {
            val oldExchange = _uiState.value.exchange
            preferencesRepository.saveExchange(exchange)
            // Sync with server
            try {
                api.setExchange(mapOf("exchange" to exchange))
                // CROSS-PLATFORM: Send WebSocket sync message
                webSocketService.sendExchangeSwitch(exchange)
                webSocketService.sendSettingsChange("exchange", oldExchange, exchange)
            } catch (e: Exception) {
                // Ignore server sync errors
            }
        }
    }
    
    fun setAccountType(accountType: String) {
        viewModelScope.launch {
            val oldAccountType = _uiState.value.accountType
            preferencesRepository.saveAccountType(accountType)
            try {
                api.switchAccountType(mapOf("account_type" to accountType))
                // CROSS-PLATFORM: Send WebSocket sync message
                webSocketService.sendSettingsChange("account_type", oldAccountType, accountType)
            } catch (e: Exception) {
                // Ignore server sync errors
            }
        }
    }
    
    fun setTheme(theme: String) {
        viewModelScope.launch {
            preferencesRepository.saveTheme(theme)
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            preferencesRepository.clearAuth()
            webSocketService.disconnect()
        }
    }
}
