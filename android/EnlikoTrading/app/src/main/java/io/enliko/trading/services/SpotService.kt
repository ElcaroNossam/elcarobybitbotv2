package io.enliko.trading.services

import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.api.SpotAsset
import io.enliko.trading.data.api.SpotBalance
import io.enliko.trading.data.api.SpotDcaSettings
import io.enliko.trading.data.api.SpotOrderRequest
import io.enliko.trading.data.api.SpotOrderResponse
import io.enliko.trading.util.AppLogger
import io.enliko.trading.util.LogCategory
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Spot trading service for Android.
 * Matches iOS SpotService for feature parity.
 * 
 * Features:
 * - Spot balance viewing
 * - Spot asset management
 * - DCA (Dollar Cost Averaging) automation
 * - Spot buy/sell orders
 */

@Singleton
class SpotService @Inject constructor(
    private val api: EnlikoApi
) {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private val _balance = MutableStateFlow<SpotBalance?>(null)
    val balance: StateFlow<SpotBalance?> = _balance.asStateFlow()
    
    private val _assets = MutableStateFlow<List<SpotAsset>>(emptyList())
    val assets: StateFlow<List<SpotAsset>> = _assets.asStateFlow()
    
    private val _dcaSettings = MutableStateFlow<SpotDcaSettings?>(null)
    val dcaSettings: StateFlow<SpotDcaSettings?> = _dcaSettings.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _lastOrderResult = MutableStateFlow<SpotOrderResponse?>(null)
    val lastOrderResult: StateFlow<SpotOrderResponse?> = _lastOrderResult.asStateFlow()
    
    // MARK: - Fetch Data
    
    /**
     * Fetch spot balance
     */
    fun fetchBalance() {
        scope.launch {
            _isLoading.value = true
            try {
                val response = api.getSpotBalance()
                if (response.isSuccessful) {
                    _balance.value = response.body()
                    AppLogger.info("Fetched spot balance: ${response.body()?.totalUsdt} USDT", LogCategory.TRADING)
                } else {
                    AppLogger.warning("Failed to fetch spot balance: ${response.code()}", LogCategory.TRADING)
                }
            } catch (e: Exception) {
                AppLogger.error("Error fetching spot balance", LogCategory.TRADING, e)
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    /**
     * Fetch spot assets (holdings)
     */
    fun fetchAssets() {
        scope.launch {
            _isLoading.value = true
            try {
                val response = api.getSpotAssets()
                if (response.isSuccessful) {
                    _assets.value = response.body() ?: emptyList()
                    AppLogger.info("Fetched ${_assets.value.size} spot assets", LogCategory.TRADING)
                } else {
                    AppLogger.warning("Failed to fetch spot assets: ${response.code()}", LogCategory.TRADING)
                }
            } catch (e: Exception) {
                AppLogger.error("Error fetching spot assets", LogCategory.TRADING, e)
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    /**
     * Fetch all spot data (balance + assets)
     */
    fun refreshAll() {
        fetchBalance()
        fetchAssets()
        fetchDcaSettings()
    }
    
    // MARK: - Trading
    
    /**
     * Buy spot asset
     */
    suspend fun buySpot(
        symbol: String,
        amountUsdt: Double? = null,
        amountCoin: Double? = null
    ): SpotOrderResponse? {
        return try {
            val request = SpotOrderRequest(
                symbol = symbol,
                side = "buy",
                amountUsdt = amountUsdt,
                amountCoin = amountCoin
            )
            
            val response = api.buySpot(request)
            if (response.isSuccessful) {
                val result = response.body()
                _lastOrderResult.value = result
                
                AppLogger.logOrderPlaced(symbol, "BUY", amountUsdt ?: amountCoin ?: 0.0, null)
                
                // Refresh data after order
                fetchBalance()
                fetchAssets()
                
                result
            } else {
                val errorMsg = "Buy failed: ${response.code()}"
                AppLogger.logOrderFailed(symbol, errorMsg)
                SpotOrderResponse(success = false, message = errorMsg)
            }
        } catch (e: Exception) {
            AppLogger.logOrderFailed(symbol, e.message ?: "Unknown error", e)
            SpotOrderResponse(success = false, message = e.message)
        }
    }
    
    /**
     * Sell spot asset
     */
    suspend fun sellSpot(
        symbol: String,
        amountUsdt: Double? = null,
        amountCoin: Double? = null
    ): SpotOrderResponse? {
        return try {
            val request = SpotOrderRequest(
                symbol = symbol,
                side = "sell",
                amountUsdt = amountUsdt,
                amountCoin = amountCoin
            )
            
            val response = api.sellSpot(request)
            if (response.isSuccessful) {
                val result = response.body()
                _lastOrderResult.value = result
                
                AppLogger.logOrderPlaced(symbol, "SELL", amountUsdt ?: amountCoin ?: 0.0, null)
                
                // Refresh data after order
                fetchBalance()
                fetchAssets()
                
                result
            } else {
                val errorMsg = "Sell failed: ${response.code()}"
                AppLogger.logOrderFailed(symbol, errorMsg)
                SpotOrderResponse(success = false, message = errorMsg)
            }
        } catch (e: Exception) {
            AppLogger.logOrderFailed(symbol, e.message ?: "Unknown error", e)
            SpotOrderResponse(success = false, message = e.message)
        }
    }
    
    // MARK: - DCA Settings
    
    /**
     * Fetch DCA settings
     */
    fun fetchDcaSettings() {
        scope.launch {
            try {
                val response = api.getSpotDcaSettings()
                if (response.isSuccessful) {
                    _dcaSettings.value = response.body()
                    AppLogger.info("Fetched DCA settings", LogCategory.TRADING)
                }
            } catch (e: Exception) {
                AppLogger.error("Error fetching DCA settings", LogCategory.TRADING, e)
            }
        }
    }
    
    /**
     * Update DCA settings
     */
    suspend fun updateDcaSettings(settings: SpotDcaSettings): Boolean {
        return try {
            val response = api.updateSpotDcaSettings(settings)
            if (response.isSuccessful) {
                _dcaSettings.value = settings
                AppLogger.info("Updated DCA settings", LogCategory.TRADING)
                true
            } else {
                AppLogger.warning("Failed to update DCA settings: ${response.code()}", LogCategory.TRADING)
                false
            }
        } catch (e: Exception) {
            AppLogger.error("Error updating DCA settings", LogCategory.TRADING, e)
            false
        }
    }
    
    // MARK: - Helpers
    
    /**
     * Get total portfolio value in USD
     */
    fun getTotalPortfolioValue(): Double {
        return _balance.value?.totalValueUsd ?: 0.0
    }
    
    /**
     * Get asset by symbol
     */
    fun getAsset(symbol: String): SpotAsset? {
        return _assets.value.find { it.symbol == symbol || it.coin == symbol }
    }
    
    /**
     * Get profitable assets
     */
    fun getProfitableAssets(): List<SpotAsset> {
        return _assets.value.filter { (it.pnl ?: 0.0) > 0 }
    }
    
    /**
     * Get losing assets
     */
    fun getLosingAssets(): List<SpotAsset> {
        return _assets.value.filter { (it.pnl ?: 0.0) < 0 }
    }
    
    /**
     * Clear last order result
     */
    fun clearLastOrderResult() {
        _lastOrderResult.value = null
    }
}
