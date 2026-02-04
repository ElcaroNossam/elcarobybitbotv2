package io.enliko.trading.util

import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.CopyOnWriteArrayList

/**
 * Centralized logging system with levels and categories
 * Matches iOS AppLogger pattern for consistency
 */

// MARK: - Log Level
enum class LogLevel(val value: Int, val prefix: String) {
    DEBUG(0, "🔍 DEBUG"),
    INFO(1, "ℹ️ INFO"),
    WARNING(2, "⚠️ WARNING"),
    ERROR(3, "❌ ERROR"),
    CRITICAL(4, "🔴 CRITICAL");
    
    fun toAndroidLogLevel(): Int = when (this) {
        DEBUG -> Log.DEBUG
        INFO -> Log.INFO
        WARNING -> Log.WARN
        ERROR -> Log.ERROR
        CRITICAL -> Log.ERROR
    }
}

// MARK: - Log Category
enum class LogCategory(val displayName: String, val emoji: String) {
    NETWORK("Network", "🌐"),
    AUTH("Auth", "🔐"),
    TRADING("Trading", "📊"),
    WEBSOCKET("WebSocket", "🔌"),
    STORAGE("Storage", "💾"),
    UI("UI", "📱"),
    SYNC("Sync", "🔄"),
    LOCALIZATION("Localization", "🌍"),
    SECURITY("Security", "🛡️"),
    GENERAL("General", "📝"),
    BIOMETRIC("Biometric", "👆"),
    PUSH("Push", "🔔");
    
    val tag: String get() = "Enliko.$displayName"
}

// MARK: - Log Entry
data class LogEntry(
    val timestamp: Date,
    val level: LogLevel,
    val category: LogCategory,
    val message: String,
    val file: String? = null,
    val function: String? = null,
    val line: Int? = null,
    val error: Throwable? = null
) {
    val formattedTimestamp: String
        get() = SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(timestamp)
    
    val formattedMessage: String
        get() = buildString {
            append(formattedTimestamp)
            append(" ")
            append(level.prefix)
            append(" ")
            append(category.emoji)
            append(" [${category.displayName}] ")
            append(message)
            error?.let {
                append("\n  Error: ${it.message}")
                append("\n  ${it.stackTraceToString().take(500)}")
            }
        }
}

// MARK: - AppLogger
object AppLogger {
    
    // Configuration
    private var minimumLevel: LogLevel = LogLevel.DEBUG
    private var remoteLoggingEnabled = true
    private var remoteLoggingMinLevel: LogLevel = LogLevel.WARNING
    private var enabledCategories: MutableSet<LogCategory> = LogCategory.entries.toMutableSet()
    
    // Log history for debugging (max 1000)
    private val logHistory = CopyOnWriteArrayList<LogEntry>()
    private const val MAX_HISTORY_COUNT = 1000
    private val historyMutex = Mutex()
    
    // Remote logging
    private val logScope = CoroutineScope(Dispatchers.IO)
    private var remoteLogEndpoint: String? = null
    private var authToken: String? = null
    
    // MARK: - Configuration
    
    fun setMinimumLevel(level: LogLevel) {
        minimumLevel = level
    }
    
    fun setRemoteLogging(enabled: Boolean, endpoint: String? = null, token: String? = null) {
        remoteLoggingEnabled = enabled
        remoteLogEndpoint = endpoint
        authToken = token
    }
    
    fun enableCategory(category: LogCategory) {
        enabledCategories.add(category)
    }
    
    fun disableCategory(category: LogCategory) {
        enabledCategories.remove(category)
    }
    
    // MARK: - Logging Methods
    
    fun debug(
        message: String,
        category: LogCategory = LogCategory.GENERAL,
        error: Throwable? = null
    ) = log(LogLevel.DEBUG, message, category, error)
    
    fun info(
        message: String,
        category: LogCategory = LogCategory.GENERAL,
        error: Throwable? = null
    ) = log(LogLevel.INFO, message, category, error)
    
    fun warning(
        message: String,
        category: LogCategory = LogCategory.GENERAL,
        error: Throwable? = null
    ) = log(LogLevel.WARNING, message, category, error)
    
    fun error(
        message: String,
        category: LogCategory = LogCategory.GENERAL,
        error: Throwable? = null
    ) = log(LogLevel.ERROR, message, category, error)
    
    fun critical(
        message: String,
        category: LogCategory = LogCategory.GENERAL,
        error: Throwable? = null
    ) = log(LogLevel.CRITICAL, message, category, error)
    
    // MARK: - Specialized Logging
    
    // Network
    fun logRequest(url: String, method: String, headers: Map<String, String>? = null) {
        val headerStr = headers?.entries?.joinToString(", ") { "${it.key}: ${it.value}" } ?: "none"
        debug("→ $method $url | Headers: $headerStr", LogCategory.NETWORK)
    }
    
    fun logResponse(url: String, statusCode: Int, duration: Long, bodySize: Int? = null) {
        val sizeStr = bodySize?.let { " | Size: $it bytes" } ?: ""
        val level = if (statusCode in 200..299) LogLevel.INFO else LogLevel.WARNING
        log(level, "← $statusCode $url | ${duration}ms$sizeStr", LogCategory.NETWORK)
    }
    
    // Auth
    fun logAuthAttempt(method: String) {
        info("Auth attempt: $method", LogCategory.AUTH)
    }
    
    fun logAuthSuccess(userId: Long) {
        info("Auth success for user: $userId", LogCategory.AUTH)
    }
    
    fun logAuthFailure(reason: String, error: Throwable? = null) {
        warning("Auth failed: $reason", LogCategory.AUTH, error)
    }
    
    fun logLogout(reason: String = "user_initiated") {
        info("Logout: $reason", LogCategory.AUTH)
    }
    
    // Trading
    fun logOrderPlaced(symbol: String, side: String, quantity: Double, price: Double?) {
        val priceStr = price?.let { " @ $it" } ?: " (market)"
        info("Order placed: $side $quantity $symbol$priceStr", LogCategory.TRADING)
    }
    
    fun logOrderFailed(symbol: String, reason: String, error: Throwable? = null) {
        error("Order failed for $symbol: $reason", LogCategory.TRADING, error)
    }
    
    fun logPositionClosed(symbol: String, pnl: Double, pnlPercent: Double) {
        val emoji = if (pnl >= 0) "✅" else "❌"
        info("$emoji Position closed: $symbol | PnL: $pnl (${pnlPercent}%)", LogCategory.TRADING)
    }
    
    // WebSocket
    fun logWSConnected(url: String) {
        info("Connected to $url", LogCategory.WEBSOCKET)
    }
    
    fun logWSDisconnected(url: String, reason: String) {
        warning("Disconnected from $url: $reason", LogCategory.WEBSOCKET)
    }
    
    fun logWSMessage(type: String, preview: String? = null) {
        val msg = preview?.let { " - ${it.take(100)}" } ?: ""
        debug("Message: $type$msg", LogCategory.WEBSOCKET)
    }
    
    fun logWSError(url: String, error: Throwable) {
        this.error("WebSocket error for $url", LogCategory.WEBSOCKET, error)
    }
    
    // Biometric
    fun logBiometricAttempt(type: String) {
        info("Biometric auth attempt: $type", LogCategory.BIOMETRIC)
    }
    
    fun logBiometricSuccess() {
        info("Biometric auth success", LogCategory.BIOMETRIC)
    }
    
    fun logBiometricFailure(reason: String) {
        warning("Biometric auth failed: $reason", LogCategory.BIOMETRIC)
    }
    
    // Push Notifications
    fun logPushReceived(type: String, payload: String? = null) {
        info("Push received: $type${payload?.let { " - ${it.take(100)}" } ?: ""}", LogCategory.PUSH)
    }
    
    fun logPushTokenUpdated(token: String) {
        debug("Push token updated: ${token.take(20)}...", LogCategory.PUSH)
    }
    
    // Storage
    fun logStorageSave(key: String, success: Boolean) {
        val level = if (success) LogLevel.DEBUG else LogLevel.WARNING
        log(level, "${if (success) "Saved" else "Failed to save"}: $key", LogCategory.STORAGE)
    }
    
    fun logStorageLoad(key: String, found: Boolean) {
        debug("${if (found) "Loaded" else "Not found"}: $key", LogCategory.STORAGE)
    }
    
    // MARK: - Core Log Method
    
    private fun log(
        level: LogLevel,
        message: String,
        category: LogCategory,
        error: Throwable? = null
    ) {
        // Check if this log should be shown
        if (level.value < minimumLevel.value) return
        if (category !in enabledCategories) return
        
        // Create log entry
        val entry = LogEntry(
            timestamp = Date(),
            level = level,
            category = category,
            message = message,
            error = error
        )
        
        // Add to history
        logScope.launch {
            historyMutex.withLock {
                logHistory.add(entry)
                while (logHistory.size > MAX_HISTORY_COUNT) {
                    logHistory.removeAt(0)
                }
            }
        }
        
        // Log to Android system
        when (level) {
            LogLevel.DEBUG -> Log.d(category.tag, entry.formattedMessage, error)
            LogLevel.INFO -> Log.i(category.tag, entry.formattedMessage, error)
            LogLevel.WARNING -> Log.w(category.tag, entry.formattedMessage, error)
            LogLevel.ERROR, LogLevel.CRITICAL -> Log.e(category.tag, entry.formattedMessage, error)
        }
        
        // Send to remote if configured
        if (remoteLoggingEnabled && level.value >= remoteLoggingMinLevel.value) {
            sendToRemote(entry)
        }
    }
    
    // MARK: - History Access
    
    fun getLogHistory(): List<LogEntry> = logHistory.toList()
    
    fun getLogHistory(category: LogCategory): List<LogEntry> =
        logHistory.filter { it.category == category }
    
    fun getLogHistory(level: LogLevel): List<LogEntry> =
        logHistory.filter { it.level.value >= level.value }
    
    fun clearHistory() {
        logHistory.clear()
    }
    
    fun getFormattedLogs(): String =
        logHistory.joinToString("\n") { it.formattedMessage }
    
    // MARK: - Remote Logging
    
    private fun sendToRemote(entry: LogEntry) {
        val endpoint = remoteLogEndpoint ?: return
        
        logScope.launch {
            try {
                // In production, this would send to server
                // For now, just log that we would send
                Log.v("AppLogger", "Would send to remote: ${entry.formattedMessage}")
                
                // Future: Use Retrofit or OkHttp to send to endpoint
                // api.sendLog(LogRequest(
                //     level = entry.level.name,
                //     category = entry.category.name,
                //     message = entry.message,
                //     timestamp = entry.timestamp.time,
                //     error = entry.error?.message
                // ))
            } catch (e: Exception) {
                Log.e("AppLogger", "Failed to send log to remote", e)
            }
        }
    }
}

// MARK: - Extension Functions for Easy Access

fun logDebug(message: String, category: LogCategory = LogCategory.GENERAL) =
    AppLogger.debug(message, category)

fun logInfo(message: String, category: LogCategory = LogCategory.GENERAL) =
    AppLogger.info(message, category)

fun logWarning(message: String, category: LogCategory = LogCategory.GENERAL, error: Throwable? = null) =
    AppLogger.warning(message, category, error)

fun logError(message: String, category: LogCategory = LogCategory.GENERAL, error: Throwable? = null) =
    AppLogger.error(message, category, error)

fun logCritical(message: String, category: LogCategory = LogCategory.GENERAL, error: Throwable? = null) =
    AppLogger.critical(message, category, error)
