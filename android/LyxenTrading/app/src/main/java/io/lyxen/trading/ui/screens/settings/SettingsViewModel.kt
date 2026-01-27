package io.lyxen.trading.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.lyxen.trading.data.api.LyxenApi
import io.lyxen.trading.data.repository.PreferencesRepository
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
    private val api: LyxenApi,
    private val preferencesRepository: PreferencesRepository
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
            preferencesRepository.saveLanguage(language)
            // Sync with server
            try {
                api.setLanguage(mapOf("language" to language))
            } catch (e: Exception) {
                // Ignore server sync errors
            }
        }
    }
    
    fun setExchange(exchange: String) {
        viewModelScope.launch {
            preferencesRepository.saveExchange(exchange)
            // Sync with server
            try {
                api.setExchange(mapOf("exchange" to exchange))
            } catch (e: Exception) {
                // Ignore server sync errors
            }
        }
    }
    
    fun setAccountType(accountType: String) {
        viewModelScope.launch {
            preferencesRepository.saveAccountType(accountType)
            try {
                api.switchAccountType(mapOf("account_type" to accountType))
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
        }
    }
}
