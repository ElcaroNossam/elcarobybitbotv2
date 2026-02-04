package io.enliko.trading.ui.screens.notifications

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.repository.PreferencesRepository
import io.enliko.trading.services.PushNotificationService
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.*
import javax.inject.Inject

/**
 * NotificationsViewModel - Matching iOS NotificationsView state management
 */

data class NotificationsUiState(
    val notifications: List<AppNotification> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
) {
    val unreadCount: Int get() = notifications.count { !it.isRead }
}

data class NotificationPreferences(
    // Categories
    val tradesEnabled: Boolean = true,
    val signalsEnabled: Boolean = true,
    val priceAlertsEnabled: Boolean = true,
    val dailyReportEnabled: Boolean = true,
    
    // Specific
    val tradeOpened: Boolean = true,
    val tradeClosed: Boolean = true,
    val breakEven: Boolean = true,
    val partialTp: Boolean = true,
    val marginWarning: Boolean = true,
    
    // Sound & Vibration
    val soundEnabled: Boolean = true,
    val vibrationEnabled: Boolean = true
)

@HiltViewModel
class NotificationsViewModel @Inject constructor(
    private val pushNotificationService: PushNotificationService,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(NotificationsUiState())
    val uiState: StateFlow<NotificationsUiState> = _uiState.asStateFlow()
    
    private val _preferences = MutableStateFlow(NotificationPreferences())
    val preferences: StateFlow<NotificationPreferences> = _preferences.asStateFlow()
    
    // Banner state for in-app notifications
    private val _currentBanner = MutableStateFlow<AppNotification?>(null)
    val currentBanner: StateFlow<AppNotification?> = _currentBanner.asStateFlow()
    
    val isAuthorized: Boolean
        get() = pushNotificationService.areNotificationsEnabled()
    
    init {
        loadNotifications()
        loadPreferences()
    }
    
    fun loadNotifications() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            try {
                // TODO: Load from API
                // For now, use mock data
                val mockNotifications = generateMockNotifications()
                
                _uiState.update { 
                    it.copy(
                        notifications = mockNotifications,
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
    
    fun markAsRead(notificationId: String) {
        viewModelScope.launch {
            _uiState.update { state ->
                state.copy(
                    notifications = state.notifications.map { notif ->
                        if (notif.id == notificationId) notif.copy(isRead = true)
                        else notif
                    }
                )
            }
            
            // TODO: Call API to mark as read
            // api.markNotificationAsRead(notificationId)
        }
    }
    
    fun markAllAsRead() {
        viewModelScope.launch {
            _uiState.update { state ->
                state.copy(
                    notifications = state.notifications.map { it.copy(isRead = true) }
                )
            }
            
            // TODO: Call API to mark all as read
            // api.markAllNotificationsAsRead()
        }
    }
    
    fun showBanner(notification: AppNotification) {
        _currentBanner.value = notification
    }
    
    fun dismissBanner() {
        val currentId = _currentBanner.value?.id
        _currentBanner.value = null
        
        // Mark as read when dismissed
        currentId?.let { markAsRead(it) }
    }
    
    fun loadPreferences() {
        viewModelScope.launch {
            // TODO: Load from DataStore
            // For now, use defaults
        }
    }
    
    fun updatePreference(update: (NotificationPreferences) -> NotificationPreferences) {
        _preferences.update { update(it) }
        savePreferences()
    }
    
    private fun savePreferences() {
        viewModelScope.launch {
            // TODO: Save to DataStore and sync with server
            // preferencesRepository.saveNotificationPreferences(_preferences.value)
            // api.syncNotificationPreferences(_preferences.value)
        }
    }
    
    fun requestPermission() {
        // Note: On Android 13+, this needs to be called from an Activity
        // The actual permission request is handled by PushNotificationService
    }
    
    // Mock data generator
    private fun generateMockNotifications(): List<AppNotification> {
        val calendar = Calendar.getInstance()
        
        return listOf(
            AppNotification(
                id = "1",
                type = NotificationType.TRADE,
                title = "Trade Opened",
                message = "Long position opened on BTCUSDT at $96,500",
                data = mapOf("symbol" to "BTCUSDT", "side" to "long", "price" to 96500.0),
                isRead = false,
                createdAt = calendar.time
            ),
            AppNotification(
                id = "2",
                type = NotificationType.TRADE,
                title = "Take Profit Hit",
                message = "ETHUSDT position closed with profit",
                data = mapOf("symbol" to "ETHUSDT", "pnl" to 5.23),
                isRead = false,
                createdAt = calendar.apply { add(Calendar.HOUR, -1) }.time
            ),
            AppNotification(
                id = "3",
                type = NotificationType.SIGNAL,
                title = "New Signal",
                message = "OI Strategy detected bullish signal on SOLUSDT",
                data = mapOf("symbol" to "SOLUSDT", "strategy" to "oi"),
                isRead = true,
                createdAt = calendar.apply { add(Calendar.HOUR, -2) }.time
            ),
            AppNotification(
                id = "4",
                type = NotificationType.PRICE_ALERT,
                title = "Price Alert",
                message = "BTC crossed above $100,000",
                data = mapOf("symbol" to "BTCUSDT", "price" to 100500.0),
                isRead = true,
                createdAt = calendar.apply { add(Calendar.DAY_OF_YEAR, -1) }.time
            ),
            AppNotification(
                id = "5",
                type = NotificationType.WARNING,
                title = "Margin Warning",
                message = "Your margin level is below 50%. Consider reducing positions.",
                isRead = false,
                createdAt = calendar.apply { add(Calendar.DAY_OF_YEAR, -1) }.time
            ),
            AppNotification(
                id = "6",
                type = NotificationType.SYSTEM,
                title = "Daily Summary",
                message = "You made 3 trades today with +$125.50 total PnL",
                data = mapOf("trades" to 3, "pnl" to 125.50),
                isRead = true,
                createdAt = calendar.apply { add(Calendar.DAY_OF_YEAR, -1) }.time
            )
        )
    }
}
