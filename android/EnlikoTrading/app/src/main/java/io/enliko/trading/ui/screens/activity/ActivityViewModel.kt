package io.enliko.trading.ui.screens.activity

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.ActivityItemApi
import io.enliko.trading.data.api.ActivityStatsApi
import io.enliko.trading.services.ActivityService
import io.enliko.trading.util.AppLogger
import io.enliko.trading.util.LogCategory
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ActivityUiState(
    val activities: List<ActivityItemApi> = emptyList(),
    val stats: ActivityStatsApi? = null,
    val isLoading: Boolean = false,
    val selectedSource: String? = null,
    val selectedCategory: String? = null,
    val error: String? = null
)

@HiltViewModel
class ActivityViewModel @Inject constructor(
    private val activityService: ActivityService
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(ActivityUiState())
    val uiState: StateFlow<ActivityUiState> = _uiState.asStateFlow()
    
    init {
        loadData()
    }
    
    private fun loadData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            try {
                // Load stats
                activityService.fetchStats()
                    .onSuccess { stats ->
                        _uiState.update { it.copy(stats = stats) }
                    }
                    .onFailure { e ->
                        AppLogger.warning(LogCategory.GENERAL, "Failed to load activity stats: ${e.message}")
                    }
                
                // Load history
                val source = _uiState.value.selectedSource
                val category = _uiState.value.selectedCategory
                
                activityService.fetchHistory(source = source, category = category, limit = 50)
                    .onSuccess { activities ->
                        _uiState.update { it.copy(
                            activities = activities,
                            isLoading = false
                        )}
                    }
                    .onFailure { e ->
                        _uiState.update { it.copy(
                            isLoading = false,
                            error = e.message
                        )}
                        AppLogger.error(LogCategory.GENERAL, "Failed to load activity history: ${e.message}")
                    }
            } catch (e: Exception) {
                _uiState.update { it.copy(
                    isLoading = false,
                    error = e.message
                )}
                AppLogger.error(LogCategory.GENERAL, "Activity load error: ${e.message}")
            }
        }
    }
    
    fun setSourceFilter(source: String?) {
        _uiState.update { it.copy(selectedSource = source) }
        loadData()
    }
    
    fun setCategoryFilter(category: String?) {
        _uiState.update { it.copy(selectedCategory = category) }
        loadData()
    }
    
    fun refresh() {
        loadData()
    }
    
    fun triggerSync() {
        viewModelScope.launch {
            activityService.triggerSync()
                .onSuccess {
                    AppLogger.info(LogCategory.GENERAL, "Manual sync triggered")
                    refresh()
                }
                .onFailure { e ->
                    AppLogger.error(LogCategory.GENERAL, "Sync trigger failed: ${e.message}")
                }
        }
    }
}
