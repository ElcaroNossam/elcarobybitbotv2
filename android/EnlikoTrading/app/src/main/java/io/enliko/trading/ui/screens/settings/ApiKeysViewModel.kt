package io.enliko.trading.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.*
import io.enliko.trading.data.local.dao.ApiKeyDao
import io.enliko.trading.data.local.entities.ApiKeyEntity
import io.enliko.trading.data.repository.PreferencesRepository
import io.enliko.trading.util.AppLogger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for API Keys management
 * Handles Bybit (Demo/Real) and HyperLiquid (Testnet/Mainnet) API credentials
 */
@HiltViewModel
class ApiKeysViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val apiKeyDao: ApiKeyDao,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    data class UiState(
        val isLoading: Boolean = false,
        val isSaving: Boolean = false,
        val isTesting: Boolean = false,
        
        // Exchange and account selection
        val selectedExchange: String = "bybit",
        val selectedAccount: String = "demo",
        
        // Bybit Demo
        val bybitDemoApiKey: String = "",
        val bybitDemoApiSecret: String = "",
        val bybitDemoConfigured: Boolean = false,
        
        // Bybit Real
        val bybitRealApiKey: String = "",
        val bybitRealApiSecret: String = "",
        val bybitRealConfigured: Boolean = false,
        
        // HyperLiquid Testnet
        val hlTestnetPrivateKey: String = "",
        val hlTestnetWalletAddress: String = "",
        val hlTestnetConfigured: Boolean = false,
        
        // HyperLiquid Mainnet
        val hlMainnetPrivateKey: String = "",
        val hlMainnetWalletAddress: String = "",
        val hlMainnetConfigured: Boolean = false,
        
        // Status
        val successMessage: String? = null,
        val errorMessage: String? = null,
        val testResult: String? = null
    )
    
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    init {
        loadApiKeysStatus()
    }
    
    fun selectExchange(exchange: String) {
        _uiState.update { 
            it.copy(
                selectedExchange = exchange,
                selectedAccount = if (exchange == "bybit") "demo" else "testnet",
                successMessage = null,
                errorMessage = null,
                testResult = null
            )
        }
    }
    
    fun selectAccount(account: String) {
        _uiState.update { 
            it.copy(
                selectedAccount = account,
                successMessage = null,
                errorMessage = null,
                testResult = null
            )
        }
    }
    
    // Bybit Demo
    fun updateBybitDemoApiKey(value: String) {
        _uiState.update { it.copy(bybitDemoApiKey = value) }
    }
    
    fun updateBybitDemoApiSecret(value: String) {
        _uiState.update { it.copy(bybitDemoApiSecret = value) }
    }
    
    // Bybit Real
    fun updateBybitRealApiKey(value: String) {
        _uiState.update { it.copy(bybitRealApiKey = value) }
    }
    
    fun updateBybitRealApiSecret(value: String) {
        _uiState.update { it.copy(bybitRealApiSecret = value) }
    }
    
    // HyperLiquid Testnet
    fun updateHlTestnetPrivateKey(value: String) {
        _uiState.update { it.copy(hlTestnetPrivateKey = value) }
    }
    
    fun updateHlTestnetWalletAddress(value: String) {
        _uiState.update { it.copy(hlTestnetWalletAddress = value) }
    }
    
    // HyperLiquid Mainnet
    fun updateHlMainnetPrivateKey(value: String) {
        _uiState.update { it.copy(hlMainnetPrivateKey = value) }
    }
    
    fun updateHlMainnetWalletAddress(value: String) {
        _uiState.update { it.copy(hlMainnetWalletAddress = value) }
    }
    
    fun clearMessages() {
        _uiState.update { 
            it.copy(
                successMessage = null,
                errorMessage = null,
                testResult = null
            )
        }
    }
    
    private fun loadApiKeysStatus() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                val response = api.getApiKeysStatus()
                if (response.isSuccessful) {
                    val status = response.body()
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            bybitDemoConfigured = status?.bybitDemo ?: false,
                            bybitRealConfigured = status?.bybitReal ?: false,
                            hlTestnetConfigured = status?.hlTestnet ?: false,
                            hlMainnetConfigured = status?.hlMainnet ?: false
                        )
                    }
                } else {
                    _uiState.update { it.copy(isLoading = false) }
                }
            } catch (e: Exception) {
                AppLogger.error("Failed to load API keys status: ${e.message}")
                _uiState.update { it.copy(isLoading = false) }
            }
        }
    }
    
    fun saveCurrentKeys() {
        val state = _uiState.value
        
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true, errorMessage = null, successMessage = null) }
            
            try {
                when {
                    state.selectedExchange == "bybit" && state.selectedAccount == "demo" -> {
                        saveBybitKeys("demo", state.bybitDemoApiKey, state.bybitDemoApiSecret)
                    }
                    state.selectedExchange == "bybit" && state.selectedAccount == "real" -> {
                        saveBybitKeys("real", state.bybitRealApiKey, state.bybitRealApiSecret)
                    }
                    state.selectedExchange == "hyperliquid" && state.selectedAccount == "testnet" -> {
                        saveHyperLiquidKeys("testnet", state.hlTestnetPrivateKey, state.hlTestnetWalletAddress)
                    }
                    state.selectedExchange == "hyperliquid" && state.selectedAccount == "mainnet" -> {
                        saveHyperLiquidKeys("mainnet", state.hlMainnetPrivateKey, state.hlMainnetWalletAddress)
                    }
                }
            } catch (e: Exception) {
                AppLogger.error("Failed to save API keys: ${e.message}")
                _uiState.update { 
                    it.copy(
                        isSaving = false,
                        errorMessage = "Failed to save: ${e.message}"
                    )
                }
            }
        }
    }
    
    private suspend fun saveBybitKeys(accountType: String, apiKey: String, apiSecret: String) {
        if (apiKey.isBlank() || apiSecret.isBlank()) {
            _uiState.update { 
                it.copy(
                    isSaving = false,
                    errorMessage = "API Key and Secret are required"
                )
            }
            return
        }
        
        val response = api.saveBybitApiKeys(
            SaveBybitApiKeysRequest(
                accountType = accountType,
                apiKey = apiKey,
                apiSecret = apiSecret
            )
        )
        
        if (response.isSuccessful && response.body()?.success == true) {
            // Get userId from preferences flow (collect first value)
            val userId = preferencesRepository.userId.first()?.toLongOrNull() ?: 0L
            
            // Save locally for offline access
            apiKeyDao.insert(
                ApiKeyEntity(
                    userId = userId,
                    exchange = "bybit",
                    accountType = accountType,
                    apiKey = maskApiKey(apiKey),
                    apiSecret = "****", // Never store real secret locally
                    walletAddress = null,
                    isConfigured = true,
                    updatedAt = System.currentTimeMillis()
                )
            )
            
            _uiState.update { 
                it.copy(
                    isSaving = false,
                    successMessage = "API Keys saved successfully!",
                    bybitDemoConfigured = if (accountType == "demo") true else it.bybitDemoConfigured,
                    bybitRealConfigured = if (accountType == "real") true else it.bybitRealConfigured
                )
            }
        } else {
            _uiState.update { 
                it.copy(
                    isSaving = false,
                    errorMessage = response.body()?.message ?: "Failed to save API keys"
                )
            }
        }
    }
    
    private suspend fun saveHyperLiquidKeys(accountType: String, privateKey: String, walletAddress: String) {
        if (privateKey.isBlank() || walletAddress.isBlank()) {
            _uiState.update { 
                it.copy(
                    isSaving = false,
                    errorMessage = "Private Key and Wallet Address are required"
                )
            }
            return
        }
        
        val response = api.saveHyperLiquidApiKeys(
            SaveHyperLiquidApiKeysRequest(
                accountType = accountType,
                privateKey = privateKey,
                walletAddress = walletAddress
            )
        )
        
        if (response.isSuccessful && response.body()?.success == true) {
            val userId = preferencesRepository.userId.first()?.toLongOrNull() ?: 0L
            
            apiKeyDao.insert(
                ApiKeyEntity(
                    userId = userId,
                    exchange = "hyperliquid",
                    accountType = accountType,
                    apiKey = "****", // No API key for HL
                    apiSecret = "****", // Private key masked
                    walletAddress = maskWalletAddress(walletAddress),
                    isConfigured = true,
                    updatedAt = System.currentTimeMillis()
                )
            )
            
            _uiState.update { 
                it.copy(
                    isSaving = false,
                    successMessage = "HyperLiquid keys saved successfully!",
                    hlTestnetConfigured = if (accountType == "testnet") true else it.hlTestnetConfigured,
                    hlMainnetConfigured = if (accountType == "mainnet") true else it.hlMainnetConfigured
                )
            }
        } else {
            _uiState.update { 
                it.copy(
                    isSaving = false,
                    errorMessage = response.body()?.message ?: "Failed to save HyperLiquid keys"
                )
            }
        }
    }
    
    fun testConnection() {
        val state = _uiState.value
        
        viewModelScope.launch {
            _uiState.update { it.copy(isTesting = true, testResult = null, errorMessage = null) }
            
            try {
                val response = when {
                    state.selectedExchange == "bybit" -> {
                        api.testBybitApiKeys(state.selectedAccount)
                    }
                    else -> {
                        api.testHyperLiquidApiKeys()
                    }
                }
                
                if (response.isSuccessful && response.body()?.success == true) {
                    val balance = response.body()?.balance
                    _uiState.update { 
                        it.copy(
                            isTesting = false,
                            testResult = if (balance != null) {
                                "✅ Connection successful! Balance: $${String.format("%.2f", balance)}"
                            } else {
                                "✅ Connection successful!"
                            }
                        )
                    }
                } else {
                    _uiState.update { 
                        it.copy(
                            isTesting = false,
                            testResult = "❌ ${response.body()?.message ?: "Connection failed"}"
                        )
                    }
                }
            } catch (e: Exception) {
                AppLogger.error("API test failed: ${e.message}")
                _uiState.update { 
                    it.copy(
                        isTesting = false,
                        testResult = "❌ Error: ${e.message}"
                    )
                }
            }
        }
    }
    
    private fun maskApiKey(apiKey: String): String {
        return if (apiKey.length > 8) {
            "${apiKey.take(4)}****${apiKey.takeLast(4)}"
        } else {
            "****"
        }
    }
    
    private fun maskWalletAddress(address: String): String {
        return if (address.length > 10) {
            "${address.take(6)}...${address.takeLast(4)}"
        } else {
            "****"
        }
    }
}
