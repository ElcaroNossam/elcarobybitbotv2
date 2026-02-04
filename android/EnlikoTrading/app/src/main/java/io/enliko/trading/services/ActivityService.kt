package io.enliko.trading.services

import io.enliko.trading.data.api.ActivityHistoryResponse
import io.enliko.trading.data.api.ActivityItemApi
import io.enliko.trading.data.api.ActivityLogRequestApi
import io.enliko.trading.data.api.ActivityStatsApi
import io.enliko.trading.data.api.ActivityStatsResponse
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.api.SyncStatusApi
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
 * Cross-platform activity sync service for Android.
 * Matches iOS ActivityService for feature parity.
 * 
 * Tracks:
 * - Settings changes across iOS, WebApp, Telegram, Android
 * - Exchange switches
 * - Authentication events
 * - Trading activities
 */

// MARK: - Activity Service

@Singleton
class ActivityService @Inject constructor(
    private val api: EnlikoApi
) {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private val _activities = MutableStateFlow<List<ActivityItemApi>>(emptyList())
    val activities: StateFlow<List<ActivityItemApi>> = _activities.asStateFlow()
    
    private val _recentActivities = MutableStateFlow<List<ActivityItemApi>>(emptyList())
    val recentActivities: StateFlow<List<ActivityItemApi>> = _recentActivities.asStateFlow()
    
    private val _stats = MutableStateFlow<ActivityStatsApi?>(null)
    val stats: StateFlow<ActivityStatsApi?> = _stats.asStateFlow()
    
    private val _syncStatus = MutableStateFlow<SyncStatusApi?>(null)
    val syncStatus: StateFlow<SyncStatusApi?> = _syncStatus.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    // MARK: - Fetch History
    
    /**
     * Fetch activity history with optional filters
     */
    fun fetchHistory(
        limit: Int = 50,
        source: String? = null,
        category: String? = null
    ) {
        scope.launch {
            _isLoading.value = true
            try {
                val response = api.getActivityHistory(
                    limit = limit,
                    source = source,
                    category = category
                )
                _activities.value = response.activities
                
                AppLogger.info("Fetched ${response.activities.size} activities", LogCategory.SYNC)
            } catch (e: Exception) {
                AppLogger.error("Failed to fetch activity history", LogCategory.SYNC, e)
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    /**
     * Fetch recent activities (last 10)
     */
    fun fetchRecentActivities() {
        scope.launch {
            try {
                val response = api.getActivityHistory(limit = 10)
                _recentActivities.value = response.activities
            } catch (e: Exception) {
                AppLogger.error("Failed to fetch recent activities", LogCategory.SYNC, e)
            }
        }
    }
    
    // MARK: - Fetch Stats
    
    /**
     * Fetch activity statistics
     */
    fun fetchStats() {
        scope.launch {
            try {
                val response = api.getActivityStats()
                _stats.value = response.stats
                _syncStatus.value = response.status
                
                AppLogger.info("Fetched activity stats: ${response.stats?.totalActivities} total", LogCategory.SYNC)
            } catch (e: Exception) {
                AppLogger.error("Failed to fetch activity stats", LogCategory.SYNC, e)
            }
        }
    }
    
    // MARK: - Log Activity
    
    /**
     * Log a settings change activity
     */
    fun logSettingsChange(
        settingName: String,
        oldValue: String?,
        newValue: String
    ) {
        logActivity(ActivityLogRequestApi(
            actionType = "settings_change",
            actionCategory = "settings",
            entityType = settingName,
            oldValue = oldValue,
            newValue = newValue
        ))
    }
    
    /**
     * Log an exchange switch activity
     */
    fun logExchangeSwitch(
        oldExchange: String,
        newExchange: String
    ) {
        logActivity(ActivityLogRequestApi(
            actionType = "exchange_switch",
            actionCategory = "exchange",
            oldValue = oldExchange,
            newValue = newExchange
        ))
    }
    
    /**
     * Log a login activity
     */
    fun logLogin(method: String) {
        logActivity(ActivityLogRequestApi(
            actionType = "login",
            actionCategory = "auth",
            entityType = method
        ))
    }
    
    /**
     * Log a logout activity
     */
    fun logLogout() {
        logActivity(ActivityLogRequestApi(
            actionType = "logout",
            actionCategory = "auth"
        ))
    }
    
    /**
     * Generic activity logging
     */
    fun logActivity(request: ActivityLogRequestApi) {
        scope.launch {
            try {
                api.logActivity(request)
                AppLogger.info("Logged activity: ${request.actionType}", LogCategory.SYNC)
                
                // Refresh recent activities
                fetchRecentActivities()
            } catch (e: Exception) {
                AppLogger.error("Failed to log activity: ${request.actionType}", LogCategory.SYNC, e)
            }
        }
    }
    
    // MARK: - Trigger Sync
    
    /**
     * Manually trigger cross-platform sync
     */
    fun triggerSync() {
        scope.launch {
            try {
                api.triggerSync()
                AppLogger.info("Sync triggered successfully", LogCategory.SYNC)
                
                // Refresh status
                fetchStats()
            } catch (e: Exception) {
                AppLogger.error("Failed to trigger sync", LogCategory.SYNC, e)
            }
        }
    }
    
    // MARK: - Filter Helpers
    
    /**
     * Get activities filtered by source
     */
    fun getActivitiesBySource(source: String): List<ActivityItemApi> {
        return _activities.value.filter { it.source == source }
    }
    
    /**
     * Get activities filtered by category
     */
    fun getActivitiesByCategory(category: String): List<ActivityItemApi> {
        return _activities.value.filter { it.actionCategory == category }
    }
    
    /**
     * Get settings changes only
     */
    fun getSettingsChanges(): List<ActivityItemApi> {
        return _activities.value.filter { it.actionCategory == "settings" }
    }
}
