package io.enliko.trading.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class User(
    @SerialName("user_id") val userId: Long,
    val id: Long? = null,  // Alternative ID field
    val email: String? = null,
    val username: String? = null,
    val name: String? = null,  // Full name from server
    @SerialName("first_name") val firstName: String? = null,
    @SerialName("last_name") val lastName: String? = null,
    val lang: String = "en",
    @SerialName("exchange_type") val exchangeType: String = "bybit",
    @SerialName("trading_mode") val tradingMode: String = "demo",
    @SerialName("hl_testnet") val hlTestnet: Boolean? = null,
    @SerialName("is_allowed") val isAllowed: Boolean = false,
    @SerialName("is_premium") val isPremium: Boolean = false,
    @SerialName("is_admin") val isAdmin: Boolean = false,
    
    // Linked accounts info (Unified Auth)
    @SerialName("telegram_id") val telegramId: Long? = null,
    @SerialName("telegram_username") val telegramUsername: String? = null,
    @SerialName("email_verified") val emailVerified: Boolean? = null,
    @SerialName("auth_provider") val authProvider: String? = null  // 'telegram', 'email', 'both'
) {
    // Display name computed property
    val displayName: String
        get() = name?.takeIf { it.isNotBlank() }
            ?: firstName?.let { f -> lastName?.let { "$f $it" } ?: f }
            ?: username
            ?: email
            ?: "User $userId"
    
    // Check if Telegram is linked
    val hasTelegramLinked: Boolean
        get() = telegramId != null || userId > 0
    
    // Check if email is linked
    val hasEmailLinked: Boolean
        get() = !email.isNullOrBlank()
}

// User Response Wrapper - Server returns {"user": {...}} not just User object
@Serializable
data class UserResponse(
    val user: User
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

// ==================== 2FA (Telegram Login) ====================
@Serializable
data class Request2FABody(
    val username: String
)

@Serializable
data class Request2FAResponse(
    val success: Boolean = false,
    @SerialName("request_id") val requestId: String? = null,
    val message: String? = null
)

@Serializable
data class Check2FAResponse(
    val status: String,
    val token: String? = null,
    @SerialName("refresh_token") val refreshToken: String? = null,
    val user: User? = null,
    val message: String? = null
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
    // --- Long side ---
    @SerialName("long_enabled") val longEnabled: Boolean = true,
    @SerialName("long_percent") val longPercent: Double? = null,
    @SerialName("long_tp_percent") val longTpPercent: Double? = null,
    @SerialName("long_sl_percent") val longSlPercent: Double? = null,
    @SerialName("long_leverage") val longLeverage: Int? = null,
    @SerialName("long_use_atr") val longUseAtr: Boolean? = null,
    @SerialName("long_atr_periods") val longAtrPeriods: Int? = null,
    @SerialName("long_atr_multiplier_sl") val longAtrMultiplierSl: Double? = null,
    @SerialName("long_atr_trigger_pct") val longAtrTriggerPct: Double? = null,
    @SerialName("long_atr_step_pct") val longAtrStepPct: Double? = null,
    @SerialName("long_order_type") val longOrderType: String? = null,
    @SerialName("long_limit_offset_pct") val longLimitOffsetPct: Double? = null,
    @SerialName("long_direction") val longDirection: String? = null,
    @SerialName("long_coins_group") val longCoinsGroup: String? = null,
    @SerialName("long_max_positions") val longMaxPositions: Int? = null,
    @SerialName("long_dca_enabled") val longDcaEnabled: Boolean = false,
    @SerialName("long_dca_pct_1") val longDcaPct1: Double? = null,
    @SerialName("long_dca_pct_2") val longDcaPct2: Double? = null,
    @SerialName("long_be_enabled") val longBeEnabled: Boolean = false,
    @SerialName("long_be_trigger_pct") val longBeTriggerPct: Double? = null,
    @SerialName("long_partial_tp_enabled") val longPartialTpEnabled: Boolean = false,
    @SerialName("long_partial_tp_1_trigger_pct") val longPartialTp1TriggerPct: Double? = null,
    @SerialName("long_partial_tp_1_close_pct") val longPartialTp1ClosePct: Double? = null,
    @SerialName("long_partial_tp_2_trigger_pct") val longPartialTp2TriggerPct: Double? = null,
    @SerialName("long_partial_tp_2_close_pct") val longPartialTp2ClosePct: Double? = null,
    // --- Short side ---
    @SerialName("short_enabled") val shortEnabled: Boolean = true,
    @SerialName("short_percent") val shortPercent: Double? = null,
    @SerialName("short_tp_percent") val shortTpPercent: Double? = null,
    @SerialName("short_sl_percent") val shortSlPercent: Double? = null,
    @SerialName("short_leverage") val shortLeverage: Int? = null,
    @SerialName("short_use_atr") val shortUseAtr: Boolean? = null,
    @SerialName("short_atr_periods") val shortAtrPeriods: Int? = null,
    @SerialName("short_atr_multiplier_sl") val shortAtrMultiplierSl: Double? = null,
    @SerialName("short_atr_trigger_pct") val shortAtrTriggerPct: Double? = null,
    @SerialName("short_atr_step_pct") val shortAtrStepPct: Double? = null,
    @SerialName("short_order_type") val shortOrderType: String? = null,
    @SerialName("short_limit_offset_pct") val shortLimitOffsetPct: Double? = null,
    @SerialName("short_direction") val shortDirection: String? = null,
    @SerialName("short_coins_group") val shortCoinsGroup: String? = null,
    @SerialName("short_max_positions") val shortMaxPositions: Int? = null,
    @SerialName("short_dca_enabled") val shortDcaEnabled: Boolean = false,
    @SerialName("short_dca_pct_1") val shortDcaPct1: Double? = null,
    @SerialName("short_dca_pct_2") val shortDcaPct2: Double? = null,
    @SerialName("short_be_enabled") val shortBeEnabled: Boolean = false,
    @SerialName("short_be_trigger_pct") val shortBeTriggerPct: Double? = null,
    @SerialName("short_partial_tp_enabled") val shortPartialTpEnabled: Boolean = false,
    @SerialName("short_partial_tp_1_trigger_pct") val shortPartialTp1TriggerPct: Double? = null,
    @SerialName("short_partial_tp_1_close_pct") val shortPartialTp1ClosePct: Double? = null,
    @SerialName("short_partial_tp_2_trigger_pct") val shortPartialTp2TriggerPct: Double? = null,
    @SerialName("short_partial_tp_2_close_pct") val shortPartialTp2ClosePct: Double? = null
)

/**
 * MobileStrategySettings — per-side flat format returned by /api/users/strategy-settings/mobile.
 * Each object represents ONE side (long or short) of one strategy.
 * Fields have NO long_/short_ prefix — the "side" field indicates which side.
 */
@Serializable
data class MobileStrategySettings(
    val strategy: String? = null,
    val side: String? = null,
    val exchange: String? = null,
    @SerialName("account_type") val accountType: String? = null,
    val enabled: Boolean? = null,
    val percent: Double? = null,
    @SerialName("tp_percent") val tpPercent: Double? = null,
    @SerialName("sl_percent") val slPercent: Double? = null,
    val leverage: Int? = null,
    @SerialName("use_atr") val useAtr: Boolean? = null,
    @SerialName("atr_trigger_pct") val atrTriggerPct: Double? = null,
    @SerialName("atr_step_pct") val atrStepPct: Double? = null,
    @SerialName("atr_periods") val atrPeriods: Int? = null,
    @SerialName("atr_multiplier_sl") val atrMultiplierSl: Double? = null,
    @SerialName("dca_enabled") val dcaEnabled: Boolean? = null,
    @SerialName("dca_pct_1") val dcaPct1: Double? = null,
    @SerialName("dca_pct_2") val dcaPct2: Double? = null,
    @SerialName("max_positions") val maxPositions: Int? = null,
    @SerialName("coins_group") val coinsGroup: String? = null,
    val direction: String? = null,
    @SerialName("order_type") val orderType: String? = null,
    @SerialName("be_enabled") val beEnabled: Boolean? = null,
    @SerialName("be_trigger_pct") val beTriggerPct: Double? = null,
    @SerialName("partial_tp_enabled") val partialTpEnabled: Boolean? = null,
    @SerialName("partial_tp_1_trigger_pct") val partialTp1TriggerPct: Double? = null,
    @SerialName("partial_tp_1_close_pct") val partialTp1ClosePct: Double? = null,
    @SerialName("partial_tp_2_trigger_pct") val partialTp2TriggerPct: Double? = null,
    @SerialName("partial_tp_2_close_pct") val partialTp2ClosePct: Double? = null,
    @SerialName("limit_offset_pct") val limitOffsetPct: Double? = null
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

// ═══════════════════════════════════════════════════════════════════════
// PORTFOLIO MODELS
// ═══════════════════════════════════════════════════════════════════════

@Serializable
data class AssetBalance(
    val asset: String,
    val free: Double,
    val locked: Double,
    val total: Double,
    @SerialName("usd_value") val usdValue: Double,
    @SerialName("pnl_24h") val pnl24h: Double = 0.0,
    @SerialName("pnl_24h_pct") val pnl24hPct: Double = 0.0
)

@Serializable
data class SpotPortfolio(
    @SerialName("total_usd") val totalUsd: Double,
    val pnl: Double,
    @SerialName("pnl_pct") val pnlPct: Double,
    val assets: List<AssetBalance>
)

@Serializable
data class FuturesPortfolio(
    @SerialName("total_equity") val totalEquity: Double,
    val available: Double,
    @SerialName("position_margin") val positionMargin: Double,
    @SerialName("unrealized_pnl") val unrealizedPnl: Double,
    @SerialName("realized_pnl") val realizedPnl: Double,
    @SerialName("position_count") val positionCount: Int
)

@Serializable
data class PnLDataPoint(
    val timestamp: String,
    val pnl: Double,
    @SerialName("cumulative_pnl") val cumulativePnl: Double,
    @SerialName("trade_count") val tradeCount: Int
)

@Serializable
data class StrategyCluster(
    val count: Int,
    val pnl: Double,
    @SerialName("win_rate") val winRate: Double
)

@Serializable
data class SymbolCluster(
    val count: Int,
    val pnl: Double
)

@Serializable
data class ClusterTrade(
    val symbol: String,
    val side: String,
    val pnl: Double,
    @SerialName("pnl_pct") val pnlPct: Double,
    val strategy: String,
    val timestamp: String
)

@Serializable
data class CandleCluster(
    val timestamp: String,
    @SerialName("open_pnl") val openPnl: Double,
    @SerialName("high_pnl") val highPnl: Double,
    @SerialName("low_pnl") val lowPnl: Double,
    @SerialName("close_pnl") val closePnl: Double,
    val volume: Double,
    @SerialName("trade_count") val tradeCount: Int,
    @SerialName("long_count") val longCount: Int,
    @SerialName("short_count") val shortCount: Int,
    @SerialName("long_pnl") val longPnl: Double,
    @SerialName("short_pnl") val shortPnl: Double,
    @SerialName("win_count") val winCount: Int,
    @SerialName("loss_count") val lossCount: Int,
    @SerialName("avg_win") val avgWin: Double,
    @SerialName("avg_loss") val avgLoss: Double,
    val strategies: Map<String, StrategyCluster> = emptyMap(),
    val symbols: Map<String, SymbolCluster> = emptyMap(),
    val trades: List<ClusterTrade> = emptyList()
)

@Serializable
data class PortfolioSummary(
    val spot: SpotPortfolio? = null,
    val futures: FuturesPortfolio? = null,
    @SerialName("total_usd") val totalUsd: Double,
    @SerialName("pnl_period") val pnlPeriod: Double,
    @SerialName("pnl_period_pct") val pnlPeriodPct: Double,
    val period: String,
    @SerialName("chart_data") val chartData: List<PnLDataPoint> = emptyList(),
    val candles: List<CandleCluster> = emptyList()
)
