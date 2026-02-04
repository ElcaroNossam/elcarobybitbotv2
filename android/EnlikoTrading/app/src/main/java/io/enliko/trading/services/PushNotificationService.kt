package io.enliko.trading.services

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import dagger.hilt.android.AndroidEntryPoint
import io.enliko.trading.MainActivity
import io.enliko.trading.R
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
 * Firebase Cloud Messaging service for push notifications.
 * Handles trade updates, signals, price alerts, and system messages.
 * 
 * SETUP REQUIRED:
 * 1. Add google-services.json to app/ folder
 * 2. Enable FCM in Firebase Console
 * 3. Register device token with backend
 */

// MARK: - Notification Types
enum class NotificationType(val value: String) {
    TRADE_OPENED("trade_opened"),
    TRADE_CLOSED("trade_closed"),
    POSITION_UPDATE("position_update"),
    ORDER_FILLED("order_filled"),
    ORDER_CANCELLED("order_cancelled"),
    SIGNAL_NEW("signal_new"),
    SIGNAL_ENTRY("signal_entry"),
    SIGNAL_EXIT("signal_exit"),
    BALANCE_UPDATE("balance_update"),
    MARGIN_WARNING("margin_warning"),
    LIQUIDATION_WARNING("liquidation_warning"),
    SETTINGS_CHANGED("settings_changed"),
    SYSTEM_MESSAGE("system_message"),
    DAILY_REPORT("daily_report"),
    BREAK_EVEN_TRIGGERED("break_even_triggered"),
    PARTIAL_TP_TRIGGERED("partial_tp_triggered"),
    UNKNOWN("unknown");
    
    companion object {
        fun fromString(value: String): NotificationType {
            return entries.find { it.value == value } ?: UNKNOWN
        }
    }
}

// MARK: - App Notification Model
data class AppNotification(
    val id: Int,
    val type: NotificationType,
    val title: String,
    val message: String,
    val data: Map<String, String>? = null,
    val isRead: Boolean = false,
    val createdAt: Long = System.currentTimeMillis()
) {
    val icon: Int
        get() = when (type) {
            NotificationType.TRADE_OPENED -> R.drawable.ic_arrow_up
            NotificationType.TRADE_CLOSED -> R.drawable.ic_checkmark
            NotificationType.SIGNAL_NEW, NotificationType.SIGNAL_ENTRY -> R.drawable.ic_bell
            NotificationType.MARGIN_WARNING, NotificationType.LIQUIDATION_WARNING -> R.drawable.ic_warning
            NotificationType.BREAK_EVEN_TRIGGERED -> R.drawable.ic_equals
            NotificationType.PARTIAL_TP_TRIGGERED -> R.drawable.ic_chart
            NotificationType.DAILY_REPORT -> R.drawable.ic_document
            else -> R.drawable.ic_notification
        }
    
    val colorHex: Int
        get() = when (type) {
            NotificationType.TRADE_OPENED, NotificationType.SIGNAL_NEW, NotificationType.SIGNAL_ENTRY -> Color.GREEN
            NotificationType.TRADE_CLOSED -> {
                val pnl = data?.get("pnl")?.toDoubleOrNull() ?: 0.0
                if (pnl >= 0) Color.GREEN else Color.RED
            }
            NotificationType.MARGIN_WARNING, NotificationType.LIQUIDATION_WARNING -> Color.RED
            NotificationType.BREAK_EVEN_TRIGGERED -> Color.YELLOW
            NotificationType.PARTIAL_TP_TRIGGERED -> Color.CYAN
            else -> Color.BLUE
        }
}

// MARK: - Notification Preferences
data class NotificationPreferences(
    val tradesEnabled: Boolean = true,
    val signalsEnabled: Boolean = true,
    val priceAlertsEnabled: Boolean = true,
    val dailyReportEnabled: Boolean = true,
    val soundEnabled: Boolean = true,
    val vibrationEnabled: Boolean = true,
    val tradeOpened: Boolean = true,
    val tradeClosed: Boolean = true,
    val breakEven: Boolean = true,
    val partialTp: Boolean = true,
    val marginWarning: Boolean = true
)

// MARK: - Notification Manager Singleton
@Singleton
class PushNotificationManager @Inject constructor(
    private val context: Context
) {
    companion object {
        // Notification Channels
        const val CHANNEL_TRADES = "trades_channel"
        const val CHANNEL_SIGNALS = "signals_channel"
        const val CHANNEL_ALERTS = "alerts_channel"
        const val CHANNEL_SYSTEM = "system_channel"
        
        // For notification IDs
        private var notificationIdCounter = 1000
    }
    
    private val _notifications = MutableStateFlow<List<AppNotification>>(emptyList())
    val notifications: StateFlow<List<AppNotification>> = _notifications.asStateFlow()
    
    private val _unreadCount = MutableStateFlow(0)
    val unreadCount: StateFlow<Int> = _unreadCount.asStateFlow()
    
    private val _preferences = MutableStateFlow(NotificationPreferences())
    val preferences: StateFlow<NotificationPreferences> = _preferences.asStateFlow()
    
    private val _deviceToken = MutableStateFlow<String?>(null)
    val deviceToken: StateFlow<String?> = _deviceToken.asStateFlow()
    
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    init {
        createNotificationChannels()
    }
    
    // MARK: - Notification Channels
    
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = context.getSystemService(NotificationManager::class.java)
            
            // Trades Channel - High importance
            val tradesChannel = NotificationChannel(
                CHANNEL_TRADES,
                "Trade Updates",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notifications for trade opens, closes, and updates"
                enableLights(true)
                lightColor = Color.GREEN
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 250, 100, 250)
            }
            
            // Signals Channel - High importance
            val signalsChannel = NotificationChannel(
                CHANNEL_SIGNALS,
                "Trading Signals",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "New trading signal alerts"
                enableLights(true)
                lightColor = Color.BLUE
                enableVibration(true)
            }
            
            // Alerts Channel - Max importance for warnings
            val alertsChannel = NotificationChannel(
                CHANNEL_ALERTS,
                "Margin & Liquidation Alerts",
                NotificationManager.IMPORTANCE_MAX
            ).apply {
                description = "Critical margin and liquidation warnings"
                enableLights(true)
                lightColor = Color.RED
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 500, 200, 500, 200, 500)
            }
            
            // System Channel - Default importance
            val systemChannel = NotificationChannel(
                CHANNEL_SYSTEM,
                "System Messages",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "System updates and daily reports"
            }
            
            notificationManager.createNotificationChannels(
                listOf(tradesChannel, signalsChannel, alertsChannel, systemChannel)
            )
            
            AppLogger.info("Notification channels created", LogCategory.PUSH)
        }
    }
    
    // MARK: - Token Management
    
    fun updateDeviceToken(token: String) {
        _deviceToken.value = token
        AppLogger.logPushTokenUpdated(token)
        
        // Register with backend
        scope.launch {
            try {
                // TODO: Call API to register token
                // api.registerDevice(DeviceRegistrationRequest(token, "android", ...))
            } catch (e: Exception) {
                AppLogger.error("Failed to register device token", LogCategory.PUSH, e)
            }
        }
    }
    
    // MARK: - Show Notification
    
    fun showNotification(notification: AppNotification) {
        if (!shouldShowNotification(notification)) return
        
        val channelId = getChannelForType(notification.type)
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("notification_type", notification.type.value)
            putExtra("notification_id", notification.id)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context,
            notification.id,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val builder = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(notification.title)
            .setContentText(notification.message)
            .setPriority(getPriorityForType(notification.type))
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setColor(notification.colorHex)
        
        // Add vibration pattern for warnings
        if (notification.type in listOf(
                NotificationType.MARGIN_WARNING,
                NotificationType.LIQUIDATION_WARNING
            )) {
            builder.setVibrate(longArrayOf(0, 500, 200, 500, 200, 500))
        }
        
        // Add actions based on type
        addActionsForType(builder, notification)
        
        try {
            NotificationManagerCompat.from(context).notify(
                notification.id.takeIf { it > 0 } ?: notificationIdCounter++,
                builder.build()
            )
            
            // Add to in-app list
            addNotificationToList(notification)
            
            AppLogger.logPushReceived(notification.type.value, notification.message)
        } catch (e: SecurityException) {
            AppLogger.error("Notification permission denied", LogCategory.PUSH, e)
        }
    }
    
    private fun getChannelForType(type: NotificationType): String {
        return when (type) {
            NotificationType.TRADE_OPENED,
            NotificationType.TRADE_CLOSED,
            NotificationType.POSITION_UPDATE,
            NotificationType.ORDER_FILLED,
            NotificationType.ORDER_CANCELLED,
            NotificationType.BREAK_EVEN_TRIGGERED,
            NotificationType.PARTIAL_TP_TRIGGERED -> CHANNEL_TRADES
            
            NotificationType.SIGNAL_NEW,
            NotificationType.SIGNAL_ENTRY,
            NotificationType.SIGNAL_EXIT -> CHANNEL_SIGNALS
            
            NotificationType.MARGIN_WARNING,
            NotificationType.LIQUIDATION_WARNING -> CHANNEL_ALERTS
            
            else -> CHANNEL_SYSTEM
        }
    }
    
    private fun getPriorityForType(type: NotificationType): Int {
        return when (type) {
            NotificationType.MARGIN_WARNING,
            NotificationType.LIQUIDATION_WARNING -> NotificationCompat.PRIORITY_MAX
            
            NotificationType.TRADE_OPENED,
            NotificationType.TRADE_CLOSED,
            NotificationType.SIGNAL_NEW -> NotificationCompat.PRIORITY_HIGH
            
            else -> NotificationCompat.PRIORITY_DEFAULT
        }
    }
    
    private fun shouldShowNotification(notification: AppNotification): Boolean {
        val prefs = _preferences.value
        
        return when (notification.type) {
            NotificationType.TRADE_OPENED -> prefs.tradesEnabled && prefs.tradeOpened
            NotificationType.TRADE_CLOSED -> prefs.tradesEnabled && prefs.tradeClosed
            NotificationType.SIGNAL_NEW, 
            NotificationType.SIGNAL_ENTRY,
            NotificationType.SIGNAL_EXIT -> prefs.signalsEnabled
            NotificationType.BREAK_EVEN_TRIGGERED -> prefs.breakEven
            NotificationType.PARTIAL_TP_TRIGGERED -> prefs.partialTp
            NotificationType.MARGIN_WARNING,
            NotificationType.LIQUIDATION_WARNING -> prefs.marginWarning
            NotificationType.DAILY_REPORT -> prefs.dailyReportEnabled
            else -> true
        }
    }
    
    private fun addActionsForType(builder: NotificationCompat.Builder, notification: AppNotification) {
        when (notification.type) {
            NotificationType.TRADE_OPENED -> {
                val viewIntent = Intent(context, MainActivity::class.java).apply {
                    putExtra("action", "view_position")
                    putExtra("symbol", notification.data?.get("symbol"))
                }
                val pendingIntent = PendingIntent.getActivity(
                    context, 
                    notification.id + 1000,
                    viewIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                builder.addAction(R.drawable.ic_chart, "View Position", pendingIntent)
            }
            
            NotificationType.TRADE_CLOSED -> {
                val shareIntent = Intent(Intent.ACTION_SEND).apply {
                    type = "text/plain"
                    putExtra(Intent.EXTRA_TEXT, buildTradeShareText(notification))
                }
                val pendingIntent = PendingIntent.getActivity(
                    context,
                    notification.id + 2000,
                    Intent.createChooser(shareIntent, "Share Trade"),
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                builder.addAction(R.drawable.ic_share, "Share", pendingIntent)
            }
            
            else -> { /* No actions */ }
        }
    }
    
    private fun buildTradeShareText(notification: AppNotification): String {
        val symbol = notification.data?.get("symbol") ?: "Unknown"
        val pnl = notification.data?.get("pnl") ?: "0"
        val pnlPercent = notification.data?.get("pnl_percent") ?: "0"
        
        return """
            🚀 Trade Closed on Enliko Trading!
            
            📊 Symbol: $symbol
            💰 PnL: $pnl USDT ($pnlPercent%)
            
            Start trading: https://enliko.com
        """.trimIndent()
    }
    
    private fun addNotificationToList(notification: AppNotification) {
        val current = _notifications.value.toMutableList()
        current.add(0, notification)
        
        // Keep only last 100 notifications
        if (current.size > 100) {
            current.removeAt(current.lastIndex)
        }
        
        _notifications.value = current
        _unreadCount.value = current.count { !it.isRead }
    }
    
    // MARK: - Notification List Management
    
    fun markAsRead(notificationId: Int) {
        val current = _notifications.value.toMutableList()
        val index = current.indexOfFirst { it.id == notificationId }
        if (index >= 0) {
            current[index] = current[index].copy(isRead = true)
            _notifications.value = current
            _unreadCount.value = current.count { !it.isRead }
        }
    }
    
    fun markAllAsRead() {
        _notifications.value = _notifications.value.map { it.copy(isRead = true) }
        _unreadCount.value = 0
    }
    
    fun clearNotifications() {
        _notifications.value = emptyList()
        _unreadCount.value = 0
    }
    
    fun updatePreferences(preferences: NotificationPreferences) {
        _preferences.value = preferences
        
        // TODO: Sync with backend
        scope.launch {
            try {
                // api.updateNotificationPreferences(preferences)
            } catch (e: Exception) {
                AppLogger.error("Failed to update preferences", LogCategory.PUSH, e)
            }
        }
    }
}

// MARK: - Firebase Messaging Service

@AndroidEntryPoint
class EnlikoFirebaseMessagingService : FirebaseMessagingService() {
    
    @Inject
    lateinit var notificationManager: PushNotificationManager
    
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        AppLogger.logPushTokenUpdated(token)
        notificationManager.updateDeviceToken(token)
    }
    
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)
        
        AppLogger.logPushReceived(
            remoteMessage.data["type"] ?: "unknown",
            remoteMessage.notification?.body
        )
        
        // Parse notification type
        val type = NotificationType.fromString(remoteMessage.data["type"] ?: "")
        
        // Build notification
        val notification = AppNotification(
            id = remoteMessage.data["notification_id"]?.toIntOrNull() ?: System.currentTimeMillis().toInt(),
            type = type,
            title = remoteMessage.notification?.title ?: remoteMessage.data["title"] ?: "Enliko Trading",
            message = remoteMessage.notification?.body ?: remoteMessage.data["message"] ?: "",
            data = remoteMessage.data.filterKeys { it !in listOf("type", "title", "message") },
            isRead = false,
            createdAt = System.currentTimeMillis()
        )
        
        // Show notification
        notificationManager.showNotification(notification)
    }
}
