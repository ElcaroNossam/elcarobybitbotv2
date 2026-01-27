package io.enliko.trading.data.websocket

import android.util.Log
import io.enliko.trading.data.models.Position
import io.enliko.trading.data.models.ScreenerCoin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.json.*
import okhttp3.*
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

sealed class WebSocketMessage {
    data class PositionUpdate(val positions: List<Position>) : WebSocketMessage()
    data class BalanceUpdate(val balance: Double, val equity: Double) : WebSocketMessage()
    data class PriceUpdate(val symbol: String, val price: Double, val change24h: Double) : WebSocketMessage()
    data class SignalReceived(val symbol: String, val side: String, val strategy: String) : WebSocketMessage()
    data class SettingsSync(val settingName: String, val value: String, val source: String) : WebSocketMessage()
    data class ExchangeSwitch(val exchange: String, val source: String) : WebSocketMessage()
    data object Connected : WebSocketMessage()
    data object Disconnected : WebSocketMessage()
    data class Error(val message: String) : WebSocketMessage()
}

@Singleton
class WebSocketService @Inject constructor(
    private val okHttpClient: OkHttpClient
) {
    companion object {
        private const val TAG = "WebSocketService"
        private const val WS_URL = "wss://enliko.com/ws"
        private const val RECONNECT_DELAY_MS = 5000L
        private const val PING_INTERVAL_MS = 30000L
    }
    
    private var webSocket: WebSocket? = null
    private var isConnected = false
    private var shouldReconnect = true
    private var userId: Long? = null
    private var authToken: String? = null
    
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var reconnectJob: Job? = null
    private var pingJob: Job? = null
    
    private val _messages = MutableSharedFlow<WebSocketMessage>(replay = 0)
    val messages: SharedFlow<WebSocketMessage> = _messages.asSharedFlow()
    
    private val _connectionState = MutableStateFlow(false)
    val connectionState: StateFlow<Boolean> = _connectionState.asStateFlow()
    
    private val json = Json { 
        ignoreUnknownKeys = true 
        isLenient = true
    }
    
    fun connect(userId: Long, token: String) {
        this.userId = userId
        this.authToken = token
        shouldReconnect = true
        doConnect()
    }
    
    private fun doConnect() {
        if (isConnected) return
        
        val request = Request.Builder()
            .url("$WS_URL?user_id=$userId&token=$authToken")
            .build()
        
        webSocket = okHttpClient.newBuilder()
            .pingInterval(PING_INTERVAL_MS, TimeUnit.MILLISECONDS)
            .build()
            .newWebSocket(request, object : WebSocketListener() {
                override fun onOpen(webSocket: WebSocket, response: Response) {
                    Log.d(TAG, "WebSocket connected")
                    isConnected = true
                    _connectionState.value = true
                    scope.launch { _messages.emit(WebSocketMessage.Connected) }
                    startPingLoop()
                    
                    // Subscribe to updates
                    sendMessage(buildJsonObject {
                        put("type", "subscribe")
                        put("channels", buildJsonArray {
                            add("positions")
                            add("balance")
                            add("prices")
                            add("signals")
                            add("sync")
                        })
                    }.toString())
                }
                
                override fun onMessage(webSocket: WebSocket, text: String) {
                    scope.launch {
                        handleMessage(text)
                    }
                }
                
                override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                    Log.d(TAG, "WebSocket closing: $code - $reason")
                }
                
                override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                    Log.d(TAG, "WebSocket closed: $code - $reason")
                    handleDisconnect()
                }
                
                override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                    Log.e(TAG, "WebSocket error: ${t.message}")
                    scope.launch { 
                        _messages.emit(WebSocketMessage.Error(t.message ?: "Unknown error")) 
                    }
                    handleDisconnect()
                }
            })
    }
    
    private fun handleDisconnect() {
        isConnected = false
        _connectionState.value = false
        pingJob?.cancel()
        scope.launch { _messages.emit(WebSocketMessage.Disconnected) }
        
        if (shouldReconnect) {
            scheduleReconnect()
        }
    }
    
    private fun scheduleReconnect() {
        reconnectJob?.cancel()
        reconnectJob = scope.launch {
            delay(RECONNECT_DELAY_MS)
            if (shouldReconnect && !isConnected) {
                Log.d(TAG, "Attempting to reconnect...")
                doConnect()
            }
        }
    }
    
    private fun startPingLoop() {
        pingJob?.cancel()
        pingJob = scope.launch {
            while (isActive && isConnected) {
                delay(PING_INTERVAL_MS)
                sendMessage("""{"type":"ping"}""")
            }
        }
    }
    
    private suspend fun handleMessage(text: String) {
        try {
            val jsonObj = json.parseToJsonElement(text).jsonObject
            val type = jsonObj["type"]?.jsonPrimitive?.contentOrNull ?: return
            
            when (type) {
                "positions_update" -> {
                    // Handle positions update
                    val data = jsonObj["data"]?.jsonArray
                    // Parse positions and emit
                }
                
                "balance_update" -> {
                    val data = jsonObj["data"]?.jsonObject
                    val balance = data?.get("balance")?.jsonPrimitive?.doubleOrNull ?: 0.0
                    val equity = data?.get("equity")?.jsonPrimitive?.doubleOrNull ?: 0.0
                    _messages.emit(WebSocketMessage.BalanceUpdate(balance, equity))
                }
                
                "price_update" -> {
                    val data = jsonObj["data"]?.jsonObject
                    val symbol = data?.get("symbol")?.jsonPrimitive?.contentOrNull ?: ""
                    val price = data?.get("price")?.jsonPrimitive?.doubleOrNull ?: 0.0
                    val change = data?.get("change_24h")?.jsonPrimitive?.doubleOrNull ?: 0.0
                    _messages.emit(WebSocketMessage.PriceUpdate(symbol, price, change))
                }
                
                "signal" -> {
                    val data = jsonObj["data"]?.jsonObject
                    val symbol = data?.get("symbol")?.jsonPrimitive?.contentOrNull ?: ""
                    val side = data?.get("side")?.jsonPrimitive?.contentOrNull ?: ""
                    val strategy = data?.get("strategy")?.jsonPrimitive?.contentOrNull ?: ""
                    _messages.emit(WebSocketMessage.SignalReceived(symbol, side, strategy))
                }
                
                "settings_changed" -> {
                    val data = jsonObj["data"]?.jsonObject
                    val settingName = data?.get("setting")?.jsonPrimitive?.contentOrNull ?: ""
                    val value = data?.get("new_value")?.jsonPrimitive?.contentOrNull ?: ""
                    val source = data?.get("source")?.jsonPrimitive?.contentOrNull ?: ""
                    _messages.emit(WebSocketMessage.SettingsSync(settingName, value, source))
                }
                
                "exchange_switched" -> {
                    val data = jsonObj["data"]?.jsonObject
                    val exchange = data?.get("exchange")?.jsonPrimitive?.contentOrNull ?: ""
                    val source = data?.get("source")?.jsonPrimitive?.contentOrNull ?: ""
                    _messages.emit(WebSocketMessage.ExchangeSwitch(exchange, source))
                }
                
                "pong" -> {
                    // Heartbeat response, do nothing
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing message: ${e.message}")
        }
    }
    
    fun sendMessage(message: String): Boolean {
        return webSocket?.send(message) ?: false
    }
    
    fun sendExchangeSwitch(exchange: String) {
        sendMessage(buildJsonObject {
            put("type", "exchange_switched")
            put("source", "android")
            put("data", buildJsonObject {
                put("exchange", exchange)
                put("timestamp", System.currentTimeMillis())
            })
        }.toString())
    }
    
    fun sendSettingsChange(settingName: String, oldValue: String?, newValue: String) {
        sendMessage(buildJsonObject {
            put("type", "settings_changed")
            put("source", "android")
            put("data", buildJsonObject {
                put("setting", settingName)
                put("old_value", oldValue)
                put("new_value", newValue)
            })
        }.toString())
    }
    
    fun disconnect() {
        shouldReconnect = false
        reconnectJob?.cancel()
        pingJob?.cancel()
        webSocket?.close(1000, "User disconnect")
        webSocket = null
        isConnected = false
        _connectionState.value = false
    }
}
