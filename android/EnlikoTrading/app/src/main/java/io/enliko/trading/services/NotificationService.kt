package io.enliko.trading.services

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import dagger.hilt.android.qualifiers.ApplicationContext
import io.enliko.trading.MainActivity
import io.enliko.trading.R
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Notification Service - Handles all app notifications
 * - Trade execution notifications
 * - Signal alerts
 * - Position updates
 * - Strategy triggers
 */
@Singleton
class NotificationService @Inject constructor(
    @ApplicationContext private val context: Context
) {
    companion object {
        const val CHANNEL_TRADES = "trades_channel"
        const val CHANNEL_SIGNALS = "signals_channel"
        const val CHANNEL_ALERTS = "alerts_channel"
        
        private const val NOTIFICATION_ID_TRADE = 1001
        private const val NOTIFICATION_ID_SIGNAL = 2001
        private const val NOTIFICATION_ID_ALERT = 3001
    }
    
    init {
        createNotificationChannels()
    }
    
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = context.getSystemService(NotificationManager::class.java)
            
            // Trades channel (high priority)
            val tradesChannel = NotificationChannel(
                CHANNEL_TRADES,
                "Trade Notifications",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notifications about trade executions and position changes"
                enableVibration(true)
            }
            
            // Signals channel (default priority)
            val signalsChannel = NotificationChannel(
                CHANNEL_SIGNALS,
                "Signal Alerts",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Trading signal alerts from strategies"
            }
            
            // General alerts channel (low priority)
            val alertsChannel = NotificationChannel(
                CHANNEL_ALERTS,
                "General Alerts",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "General app notifications and updates"
            }
            
            notificationManager?.createNotificationChannels(
                listOf(tradesChannel, signalsChannel, alertsChannel)
            )
        }
    }
    
    /**
     * Show trade execution notification
     */
    fun showTradeNotification(
        title: String,
        message: String,
        symbol: String? = null,
        isProfitable: Boolean? = null
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("navigate_to", "portfolio")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent, 
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val iconRes = when {
            isProfitable == true -> android.R.drawable.ic_menu_add
            isProfitable == false -> android.R.drawable.ic_delete
            else -> android.R.drawable.ic_dialog_info
        }
        
        val notification = NotificationCompat.Builder(context, CHANNEL_TRADES)
            .setSmallIcon(iconRes)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_EVENT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()
        
        try {
            NotificationManagerCompat.from(context)
                .notify(NOTIFICATION_ID_TRADE + (symbol?.hashCode() ?: 0), notification)
        } catch (e: SecurityException) {
            // Permission not granted
        }
    }
    
    /**
     * Show signal alert notification
     */
    fun showSignalNotification(
        strategy: String,
        symbol: String,
        direction: String,
        price: Double?
    ) {
        val directionEmoji = if (direction.equals("long", ignoreCase = true)) "🟢" else "🔴"
        val priceText = price?.let { " @ $${String.format("%.2f", it)}" } ?: ""
        
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("navigate_to", "signals")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent, 
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(context, CHANNEL_SIGNALS)
            .setSmallIcon(android.R.drawable.ic_menu_compass)
            .setContentTitle("$directionEmoji Signal: $symbol")
            .setContentText("$strategy ${direction.uppercase()}$priceText")
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()
        
        try {
            NotificationManagerCompat.from(context)
                .notify(NOTIFICATION_ID_SIGNAL + symbol.hashCode(), notification)
        } catch (e: SecurityException) {
            // Permission not granted
        }
    }
    
    /**
     * Show position closed notification with PnL
     */
    fun showPositionClosedNotification(
        symbol: String,
        side: String,
        pnl: Double,
        pnlPercent: Double,
        exitReason: String
    ) {
        val isProfitable = pnl >= 0
        val emoji = if (isProfitable) "✅" else "❌"
        val pnlText = if (pnl >= 0) "+$${String.format("%.2f", pnl)}" else "-$${String.format("%.2f", -pnl)}"
        
        showTradeNotification(
            title = "$emoji Position Closed: $symbol",
            message = "$side closed by $exitReason: $pnlText (${String.format("%.2f", pnlPercent)}%)",
            symbol = symbol,
            isProfitable = isProfitable
        )
    }
    
    /**
     * Show position opened notification
     */
    fun showPositionOpenedNotification(
        symbol: String,
        side: String,
        size: Double,
        entryPrice: Double,
        strategy: String?
    ) {
        val sideEmoji = if (side.equals("Buy", ignoreCase = true)) "🟢" else "🔴"
        val strategyText = strategy?.let { " via $it" } ?: ""
        
        showTradeNotification(
            title = "$sideEmoji Position Opened: $symbol",
            message = "$side ${String.format("%.4f", size)} @ $${String.format("%.2f", entryPrice)}$strategyText",
            symbol = symbol
        )
    }
    
    /**
     * Show TP/SL triggered notification
     */
    fun showTpSlTriggeredNotification(
        symbol: String,
        type: String, // "TP" or "SL"
        triggerPrice: Double,
        pnl: Double
    ) {
        val title = if (type == "TP") "✅ Take Profit Hit" else "🛑 Stop Loss Hit"
        val pnlText = if (pnl >= 0) "+$${String.format("%.2f", pnl)}" else "-$${String.format("%.2f", -pnl)}"
        
        showTradeNotification(
            title = "$title: $symbol",
            message = "$type @ $${String.format("%.2f", triggerPrice)}, PnL: $pnlText",
            symbol = symbol,
            isProfitable = pnl >= 0
        )
    }
    
    /**
     * Show general alert notification
     */
    fun showAlertNotification(title: String, message: String) {
        val notification = NotificationCompat.Builder(context, CHANNEL_ALERTS)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setAutoCancel(true)
            .build()
        
        try {
            NotificationManagerCompat.from(context)
                .notify(NOTIFICATION_ID_ALERT, notification)
        } catch (e: SecurityException) {
            // Permission not granted
        }
    }
    
    /**
     * Cancel all notifications
     */
    fun cancelAll() {
        NotificationManagerCompat.from(context).cancelAll()
    }
}
