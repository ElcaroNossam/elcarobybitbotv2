package io.enliko.trading.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class User(
    @SerialName("user_id") val userId: Long,
    val email: String? = null,
    val username: String? = null,
    val lang: String = "en",
    @SerialName("exchange_type") val exchangeType: String = "bybit",
    @SerialName("trading_mode") val tradingMode: String = "demo",
    @SerialName("hl_testnet") val hlTestnet: Boolean? = null,
    @SerialName("is_allowed") val isAllowed: Boolean = false,
    @SerialName("is_premium") val isPremium: Boolean = false
)

@Serializable
data class LoginRequest(
    val email: String,
    val password: String
)

@Serializable
data class RegisterRequest(
    val email: String,
    val password: String,
    val username: String? = null
)

@Serializable
data class AuthResponse(
    val token: String,
    val user: User
)

@Serializable
data class Position(
    val symbol: String,
    val side: String,
    @SerialName("entry_price") val entryPrice: Double,
    val size: Double,
    val leverage: Double? = null,
    @SerialName("unrealized_pnl") val unrealizedPnl: Double? = null,
    @SerialName("pnl_pct") val pnlPercent: Double? = null,
    @SerialName("mark_price") val markPrice: Double? = null,
    val strategy: String? = null,
    @SerialName("sl_price") val slPrice: Double? = null,
    @SerialName("tp_price") val tpPrice: Double? = null,
    @SerialName("account_type") val accountType: String? = null,
    val exchange: String? = null
)

@Serializable
data class Balance(
    @SerialName("total_equity") val totalEquity: Double,
    @SerialName("available_balance") val availableBalance: Double,
    @SerialName("unrealized_pnl") val unrealizedPnl: Double = 0.0,
    @SerialName("margin_used") val marginUsed: Double = 0.0,
    val currency: String = "USDT"
)

@Serializable
data class Trade(
    val id: Long? = null,
    val symbol: String,
    val side: String,
    @SerialName("entry_price") val entryPrice: Double,
    @SerialName("exit_price") val exitPrice: Double? = null,
    val pnl: Double? = null,
    @SerialName("pnl_pct") val pnlPercent: Double? = null,
    val strategy: String? = null,
    @SerialName("exit_reason") val exitReason: String? = null,
    @SerialName("account_type") val accountType: String? = null,
    val timestamp: String? = null
)

@Serializable
data class TradeStats(
    val total: Int = 0,
    val wins: Int = 0,
    val losses: Int = 0,
    val winrate: Double = 0.0,
    @SerialName("total_pnl") val totalPnl: Double = 0.0,
    @SerialName("avg_pnl") val avgPnl: Double = 0.0,
    @SerialName("best_pnl") val bestPnl: Double = 0.0,
    @SerialName("worst_pnl") val worstPnl: Double = 0.0
)

@Serializable
data class Signal(
    val id: Long? = null,
    val symbol: String,
    val side: String,
    val strategy: String,
    val price: Double? = null,
    @SerialName("entry_price") val entryPrice: Double? = null,
    @SerialName("take_profit") val takeProfit: Double? = null,
    @SerialName("stop_loss") val stopLoss: Double? = null,
    @SerialName("sl_pct") val slPercent: Double? = null,
    @SerialName("tp_pct") val tpPercent: Double? = null,
    val confidence: Double? = null,
    val status: String? = null,
    val timestamp: String? = null
)

@Serializable
data class ScreenerCoin(
    val symbol: String,
    val price: Double,
    @SerialName("change_24h") val change24h: Double,
    @SerialName("volume_24h") val volume24h: Double,
    @SerialName("oi_change") val oiChange: Double? = null,
    val rsi: Double? = null,
    val trend: String? = null
)

@Serializable
data class Order(
    @SerialName("order_id") val orderId: String,
    val symbol: String,
    val side: String,
    @SerialName("order_type") val orderType: String,
    val price: Double? = null,
    val qty: Double,
    val status: String,
    @SerialName("created_at") val createdAt: String? = null
)

@Serializable
data class StrategySettings(
    val strategy: String,
    val enabled: Boolean = true,
    @SerialName("long_percent") val longPercent: Double? = null,
    @SerialName("long_tp_percent") val longTpPercent: Double? = null,
    @SerialName("long_sl_percent") val longSlPercent: Double? = null,
    @SerialName("long_leverage") val longLeverage: Int? = null,
    @SerialName("short_percent") val shortPercent: Double? = null,
    @SerialName("short_tp_percent") val shortTpPercent: Double? = null,
    @SerialName("short_sl_percent") val shortSlPercent: Double? = null,
    @SerialName("short_leverage") val shortLeverage: Int? = null,
    @SerialName("long_dca_enabled") val longDcaEnabled: Boolean = false,
    @SerialName("short_dca_enabled") val shortDcaEnabled: Boolean = false,
    @SerialName("long_be_enabled") val longBeEnabled: Boolean = false,
    @SerialName("short_be_enabled") val shortBeEnabled: Boolean = false
)

@Serializable
data class AIChatMessage(
    val role: String,
    val content: String,
    val timestamp: String? = null
)

@Serializable
data class AIChatRequest(
    val message: String,
    val context: String? = null
)

@Serializable
data class AIChatResponse(
    val response: String,
    val suggestions: List<String>? = null
)

@Serializable
data class ApiError(
    val detail: String? = null,
    val message: String? = null
)
