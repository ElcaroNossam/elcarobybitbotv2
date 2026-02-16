package io.enliko.trading.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.models.MobileStrategySettings
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * StrategySettingsViewModel - Manages strategy settings state.
 * Uses /api/users/strategy-settings/mobile which returns per-side flat objects.
 * Each side (long/short) is a separate MobileStrategySettings object.
 */
@HiltViewModel
class StrategySettingsViewModel @Inject constructor(
    private val api: EnlikoApi
) : ViewModel() {
    
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
    
    /**
     * Load strategy settings from mobile API.
     * The endpoint returns per-side objects: [{strategy, side:"long", ...}, {strategy, side:"short", ...}]
     */
    fun loadSettings(strategyCode: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            try {
                val response = api.getStrategySettingsMobile(strategy = strategyCode)
                if (response.isSuccessful) {
                    val settingsList = response.body() ?: emptyList()
                    
                    // Find long and short side objects
                    val longData = settingsList.find { it.side == "long" }
                    val shortData = settingsList.find { it.side == "short" }
                    
                    if (longData != null) {
                        _longSettings.value = mapToSideSettings(longData)
                    }
                    if (shortData != null) {
                        _shortSettings.value = mapToSideSettings(shortData)
                    }
                } else {
                    _error.value = "Failed to load: ${response.code()}"
                }
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load settings"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    /** Map per-side MobileStrategySettings to SideSettings UI model. */
    private fun mapToSideSettings(data: MobileStrategySettings): SideSettings {
        return SideSettings(
            enabled = data.enabled ?: true,
            percent = data.percent ?: 1.0,
            tpPercent = data.tpPercent ?: 25.0,
            slPercent = data.slPercent ?: 30.0,
            leverage = data.leverage ?: 10,
            useAtr = data.useAtr ?: true,
            atrPeriods = data.atrPeriods ?: 7,
            atrMultiplierSl = data.atrMultiplierSl ?: 0.5,
            atrTriggerPct = data.atrTriggerPct ?: 3.0,
            atrStepPct = data.atrStepPct ?: 0.5,
            dcaEnabled = data.dcaEnabled ?: false,
            dcaPct1 = data.dcaPct1 ?: 10.0,
            dcaPct2 = data.dcaPct2 ?: 25.0,
            orderType = data.orderType ?: "market",
            limitOffsetPct = data.limitOffsetPct ?: 0.1,
            direction = data.direction ?: "all",
            maxPositions = data.maxPositions ?: 0,
            coinsGroup = data.coinsGroup ?: "ALL",
            beEnabled = data.beEnabled ?: false,
            beTriggerPct = data.beTriggerPct ?: 1.0,
            partialTpEnabled = data.partialTpEnabled ?: false,
            partialTp1TriggerPct = data.partialTp1TriggerPct ?: 2.0,
            partialTp1ClosePct = data.partialTp1ClosePct ?: 30.0,
            partialTp2TriggerPct = data.partialTp2TriggerPct ?: 5.0,
            partialTp2ClosePct = data.partialTp2ClosePct ?: 30.0
        )
    }
    
    fun updateLongSettings(settings: SideSettings) {
        _longSettings.value = settings
    }
    
    fun updateShortSettings(settings: SideSettings) {
        _shortSettings.value = settings
    }
    
    /**
     * Save strategy settings via mobile API.
     * Sends TWO separate PUT requests — one for long, one for short.
     * The mobile PUT endpoint expects per-side flat format with "side" field.
     */
    fun saveSettings(strategyCode: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            try {
                // Save long side
                val longBody = buildSideBody("long", _longSettings.value)
                val longResponse = api.updateStrategySettingsMobile(strategyCode, longBody)
                
                // Save short side
                val shortBody = buildSideBody("short", _shortSettings.value)
                val shortResponse = api.updateStrategySettingsMobile(strategyCode, shortBody)
                
                if (longResponse.isSuccessful && shortResponse.isSuccessful) {
                    _saveSuccess.value = true
                    kotlinx.coroutines.delay(2000)
                    _saveSuccess.value = false
                } else {
                    val longErr = if (!longResponse.isSuccessful) "Long: ${longResponse.code()}" else ""
                    val shortErr = if (!shortResponse.isSuccessful) "Short: ${shortResponse.code()}" else ""
                    _error.value = "Save failed. $longErr $shortErr".trim()
                }
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to save settings"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    /** Build per-side body for PUT /api/users/strategy-settings/mobile/{strategy}. */
    private fun buildSideBody(side: String, s: SideSettings): Map<String, Any> {
        return mapOf(
            "side" to side,
            "source" to "android",
            "enabled" to s.enabled,
            "percent" to s.percent,
            "tp_percent" to s.tpPercent,
            "sl_percent" to s.slPercent,
            "leverage" to s.leverage,
            "use_atr" to s.useAtr,
            "atr_periods" to s.atrPeriods,
            "atr_multiplier_sl" to s.atrMultiplierSl,
            "atr_trigger_pct" to s.atrTriggerPct,
            "atr_step_pct" to s.atrStepPct,
            "dca_enabled" to s.dcaEnabled,
            "dca_pct_1" to s.dcaPct1,
            "dca_pct_2" to s.dcaPct2,
            "order_type" to s.orderType,
            "limit_offset_pct" to s.limitOffsetPct,
            "direction" to s.direction,
            "max_positions" to s.maxPositions,
            "coins_group" to s.coinsGroup,
            "be_enabled" to s.beEnabled,
            "be_trigger_pct" to s.beTriggerPct,
            "partial_tp_enabled" to s.partialTpEnabled,
            "partial_tp_1_trigger_pct" to s.partialTp1TriggerPct,
            "partial_tp_1_close_pct" to s.partialTp1ClosePct,
            "partial_tp_2_trigger_pct" to s.partialTp2TriggerPct,
            "partial_tp_2_close_pct" to s.partialTp2ClosePct
        )
    }
    
    fun clearError() {
        _error.value = null
    }
}
