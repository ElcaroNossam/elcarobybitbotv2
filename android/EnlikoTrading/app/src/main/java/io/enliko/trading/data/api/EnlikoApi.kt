package io.enliko.trading.data.api

import io.enliko.trading.data.models.*
import retrofit2.Response
import retrofit2.http.*

interface EnlikoApi {

    // ==================== AUTH ====================
    @POST("/api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>

    @POST("/api/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<AuthResponse>

    @GET("/api/users/me")
    suspend fun getCurrentUser(): Response<UserResponse>

    @POST("/api/auth/logout")
    suspend fun logout(): Response<Unit>

    // ==================== TRADING ====================
    @GET("/api/trading/balance")
    suspend fun getBalance(
        @Query("account_type") accountType: String? = null
    ): Response<Balance>

    @GET("/api/trading/positions")
    suspend fun getPositions(
        @Query("account_type") accountType: String? = null
    ): Response<List<Position>>

    @GET("/api/trading/orders")
    suspend fun getOrders(
        @Query("account_type") accountType: String? = null
    ): Response<List<Order>>

    @POST("/api/trading/close")
    suspend fun closePosition(
        @Body request: ClosePositionRequest
    ): Response<ClosePositionResponse>

    @POST("/api/trading/close-all")
    suspend fun closeAllPositions(
        @Query("account_type") accountType: String? = null
    ): Response<CloseAllResponse>

    @GET("/api/trading/stats")
    suspend fun getTradeStats(
        @Query("account_type") accountType: String? = null,
        @Query("days") days: Int? = null
    ): Response<TradeStats>

    @GET("/api/trading/trades")
    suspend fun getTrades(
        @Query("account_type") accountType: String? = null,
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): Response<List<Trade>>

    // ==================== STRATEGY SETTINGS ====================
    @GET("/api/trading/strategy-settings")
    suspend fun getStrategySettings(
        @Query("strategy") strategy: String? = null
    ): Response<List<StrategySettings>>

    @PUT("/api/trading/strategy-settings/{strategy}")
    suspend fun updateStrategySettings(
        @Path("strategy") strategy: String,
        @Body settings: Map<String, @JvmSuppressWildcards Any>
    ): Response<StrategySettings>

    // ==================== USER SETTINGS ====================
    @PUT("/api/users/exchange")
    suspend fun setExchange(
        @Body request: Map<String, String>
    ): Response<Unit>

    @PUT("/api/users/language")
    suspend fun setLanguage(
        @Body request: Map<String, String>
    ): Response<Unit>

    @PUT("/api/users/switch-account-type")
    suspend fun switchAccountType(
        @Body request: Map<String, String>
    ): Response<Unit>

    @GET("/api/users/settings")
    suspend fun getUserSettings(): Response<Map<String, @JvmSuppressWildcards Any>>

    // ==================== SIGNALS ====================
    @GET("/api/signals")
    suspend fun getSignals(
        @Query("side") side: String? = null,
        @Query("limit") limit: Int? = null
    ): Response<List<Signal>>

    // ==================== SCREENER ====================
    @GET("/api/screener/coins")
    suspend fun getScreenerCoins(
        @Query("sort_by") sortBy: String? = null,
        @Query("limit") limit: Int? = null
    ): Response<List<ScreenerCoin>>

    // ==================== AI CHAT ====================
    @POST("/api/ai/chat")
    suspend fun sendAiMessage(
        @Body request: AIChatRequest
    ): Response<AIChatResponse>

    // ==================== ACTIVITY ====================
    @GET("/api/activity/history")
    suspend fun getActivityHistory(
        @Query("limit") limit: Int? = null,
        @Query("source") source: String? = null,
        @Query("category") category: String? = null
    ): ActivityHistoryResponse

    @GET("/api/activity/recent")
    suspend fun getRecentActivity(
        @Query("limit") limit: Int? = null
    ): Response<List<ActivityItemApi>>

    @GET("/api/activity/stats")
    suspend fun getActivityStats(): ActivityStatsResponse

    @POST("/api/activity/log")
    suspend fun logActivity(
        @Body request: ActivityLogRequestApi
    ): Response<Unit>

    @POST("/api/activity/trigger-sync")
    suspend fun triggerSync(): Response<Unit>

    // ==================== PORTFOLIO ====================
    @GET("/api/portfolio/summary")
    suspend fun getPortfolioSummary(
        @Query("account_type") accountType: String? = null,
        @Query("period") period: String? = "1w",
        @Query("custom_start") customStart: String? = null,
        @Query("custom_end") customEnd: String? = null
    ): Response<io.enliko.trading.data.models.PortfolioSummary>

    @GET("/api/portfolio/spot")
    suspend fun getSpotPortfolio(
        @Query("account_type") accountType: String? = null
    ): Response<io.enliko.trading.data.models.SpotPortfolio>

    @GET("/api/portfolio/futures")
    suspend fun getFuturesPortfolio(
        @Query("account_type") accountType: String? = null
    ): Response<io.enliko.trading.data.models.FuturesPortfolio>

    @GET("/api/portfolio/chart")
    suspend fun getPortfolioChart(
        @Query("account_type") accountType: String? = null,
        @Query("period") period: String? = "1w",
        @Query("custom_start") customStart: String? = null,
        @Query("custom_end") customEnd: String? = null
    ): Response<List<io.enliko.trading.data.models.CandleCluster>>

    @GET("/api/portfolio/candle/{timestamp}")
    suspend fun getCandleCluster(
        @Path("timestamp") timestamp: String,
        @Query("account_type") accountType: String? = null
    ): Response<io.enliko.trading.data.models.CandleCluster>

    // ==================== SPOT TRADING ====================
    @GET("/api/spot/balance")
    suspend fun getSpotBalance(): Response<SpotBalance>

    @GET("/api/spot/assets")
    suspend fun getSpotAssets(): Response<List<SpotAsset>>

    @POST("/api/spot/buy")
    suspend fun buySpot(@Body request: SpotOrderRequest): Response<SpotOrderResponse>

    @POST("/api/spot/sell")
    suspend fun sellSpot(@Body request: SpotOrderRequest): Response<SpotOrderResponse>

    @GET("/api/spot/dca-settings")
    suspend fun getSpotDcaSettings(): Response<SpotDcaSettings>

    @PUT("/api/spot/dca-settings")
    suspend fun updateSpotDcaSettings(@Body settings: SpotDcaSettings): Response<Unit>
}

// ==================== REQUEST/RESPONSE MODELS ====================

@kotlinx.serialization.Serializable
data class ClosePositionRequest(
    val symbol: String,
    val side: String,
    @kotlinx.serialization.SerialName("account_type") val accountType: String? = null
)

@kotlinx.serialization.Serializable
data class ClosePositionResponse(
    val success: Boolean,
    val message: String? = null
)

@kotlinx.serialization.Serializable
data class CloseAllResponse(
    val success: Boolean,
    val closed: Int = 0,
    val message: String? = null
)

// Activity API Models
@kotlinx.serialization.Serializable
data class ActivityItemApi(
    val id: Long,
    @kotlinx.serialization.SerialName("action_type") val actionType: String,
    @kotlinx.serialization.SerialName("action_category") val actionCategory: String,
    val source: String,
    @kotlinx.serialization.SerialName("entity_type") val entityType: String? = null,
    @kotlinx.serialization.SerialName("old_value") val oldValue: String? = null,
    @kotlinx.serialization.SerialName("new_value") val newValue: String? = null,
    @kotlinx.serialization.SerialName("created_at") val createdAt: String
)

@kotlinx.serialization.Serializable
data class ActivityHistoryResponse(
    val activities: List<ActivityItemApi> = emptyList(),
    val total: Int = 0,
    val page: Int = 1
)

@kotlinx.serialization.Serializable
data class ActivityStatsResponse(
    val stats: ActivityStatsApi? = null,
    val status: SyncStatusApi? = null
)

@kotlinx.serialization.Serializable
data class ActivityStatsApi(
    @kotlinx.serialization.SerialName("total_activities") val totalActivities: Int = 0,
    @kotlinx.serialization.SerialName("by_source") val bySource: Map<String, Int> = emptyMap(),
    @kotlinx.serialization.SerialName("by_category") val byCategory: Map<String, Int> = emptyMap(),
    @kotlinx.serialization.SerialName("last_24h_count") val last24hCount: Int = 0
)

@kotlinx.serialization.Serializable
data class SyncStatusApi(
    @kotlinx.serialization.SerialName("pending_sync") val pendingSync: Int = 0,
    @kotlinx.serialization.SerialName("last_sync_at") val lastSyncAt: String? = null,
    @kotlinx.serialization.SerialName("sync_health") val syncHealth: String = "unknown"
)

@kotlinx.serialization.Serializable
data class ActivityLogRequestApi(
    @kotlinx.serialization.SerialName("action_type") val actionType: String,
    @kotlinx.serialization.SerialName("action_category") val actionCategory: String,
    val source: String = "android",
    @kotlinx.serialization.SerialName("entity_type") val entityType: String? = null,
    @kotlinx.serialization.SerialName("old_value") val oldValue: String? = null,
    @kotlinx.serialization.SerialName("new_value") val newValue: String? = null
)

// Spot Trading Models
@kotlinx.serialization.Serializable
data class SpotBalance(
    @kotlinx.serialization.SerialName("total_usdt") val totalUsdt: Double = 0.0,
    @kotlinx.serialization.SerialName("available_usdt") val availableUsdt: Double = 0.0,
    @kotlinx.serialization.SerialName("total_value_usd") val totalValueUsd: Double = 0.0,
    @kotlinx.serialization.SerialName("assets_count") val assetsCount: Int = 0
)

@kotlinx.serialization.Serializable
data class SpotAsset(
    val symbol: String,
    val coin: String,
    @kotlinx.serialization.SerialName("free") val free: Double = 0.0,
    @kotlinx.serialization.SerialName("locked") val locked: Double = 0.0,
    @kotlinx.serialization.SerialName("total") val total: Double = 0.0,
    @kotlinx.serialization.SerialName("usd_value") val usdValue: Double = 0.0,
    @kotlinx.serialization.SerialName("avg_entry_price") val avgEntryPrice: Double? = null,
    @kotlinx.serialization.SerialName("current_price") val currentPrice: Double? = null,
    @kotlinx.serialization.SerialName("pnl") val pnl: Double? = null,
    @kotlinx.serialization.SerialName("pnl_percent") val pnlPercent: Double? = null
)

@kotlinx.serialization.Serializable
data class SpotOrderRequest(
    val symbol: String,
    val side: String,
    @kotlinx.serialization.SerialName("amount_usdt") val amountUsdt: Double? = null,
    @kotlinx.serialization.SerialName("amount_coin") val amountCoin: Double? = null,
    @kotlinx.serialization.SerialName("order_type") val orderType: String = "market"
)

@kotlinx.serialization.Serializable
data class SpotOrderResponse(
    val success: Boolean,
    @kotlinx.serialization.SerialName("order_id") val orderId: String? = null,
    val message: String? = null,
    @kotlinx.serialization.SerialName("executed_qty") val executedQty: Double? = null,
    @kotlinx.serialization.SerialName("executed_price") val executedPrice: Double? = null
)

@kotlinx.serialization.Serializable
data class SpotDcaSettings(
    val enabled: Boolean = false,
    @kotlinx.serialization.SerialName("buy_amount_usdt") val buyAmountUsdt: Double = 10.0,
    @kotlinx.serialization.SerialName("frequency_hours") val frequencyHours: Int = 24,
    val coins: List<String> = listOf("BTC", "ETH"),
    @kotlinx.serialization.SerialName("auto_sell_enabled") val autoSellEnabled: Boolean = false,
    @kotlinx.serialization.SerialName("take_profit_percent") val takeProfitPercent: Double = 10.0
)
