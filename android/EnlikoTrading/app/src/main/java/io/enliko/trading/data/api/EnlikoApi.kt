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

    // 2FA (Telegram Login)
    @POST("/api/auth/telegram/request-2fa")
    suspend fun request2FA(@Body body: Request2FABody): Response<Request2FAResponse>

    @GET("/api/auth/telegram/check-2fa/{requestId}")
    suspend fun check2FA(@Path("requestId") requestId: String): Response<Check2FAResponse>

    // ==================== TRADING ====================
    @GET("/api/trading/balance")
    suspend fun getBalance(
        @Query("exchange") exchange: String? = null,
        @Query("account_type") accountType: String? = null
    ): Response<BalanceResponse>

    @GET("/api/trading/positions")
    suspend fun getPositions(
        @Query("exchange") exchange: String? = null,
        @Query("account_type") accountType: String? = null
    ): Response<PositionsResponse>

    @GET("/api/trading/orders")
    suspend fun getOrders(
        @Query("exchange") exchange: String? = null,
        @Query("account_type") accountType: String? = null
    ): Response<OrdersResponse>

    @POST("/api/trading/close")
    suspend fun closePosition(
        @Body request: ClosePositionRequest
    ): Response<ClosePositionResponse>

    @POST("/api/trading/close-all")
    suspend fun closeAllPositions(
        @Query("exchange") exchange: String? = null,
        @Query("account_type") accountType: String? = null
    ): Response<CloseAllResponse>

    @GET("/api/trading/stats")
    suspend fun getTradeStats(
        @Query("exchange") exchange: String? = null,
        @Query("account_type") accountType: String? = null,
        @Query("days") days: Int? = null
    ): Response<TradeStatsResponse>

    @GET("/api/trading/trades")
    suspend fun getTrades(
        @Query("exchange") exchange: String? = null,
        @Query("account_type") accountType: String? = null,
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): Response<TradesResponse>

    // Manual Trading
    @POST("/api/trading/place-order")
    suspend fun placeOrder(
        @Query("exchange") exchange: String? = null,
        @Query("account_type") accountType: String? = null,
        @Body request: PlaceOrderRequest
    ): Response<PlaceOrderResponse>

    @POST("/api/trading/set-leverage")
    suspend fun setLeverage(
        @Query("exchange") exchange: String? = null,
        @Query("account_type") accountType: String? = null,
        @Body request: SetLeverageRequest
    ): Response<SetLeverageResponse>

    @POST("/api/trading/cancel-order")
    suspend fun cancelOrder(
        @Body request: CancelOrderRequest
    ): Response<CancelOrderResponse>

    @POST("/api/trading/modify-tpsl")
    suspend fun modifyTpSl(
        @Body request: ModifyTpSlRequest
    ): Response<ModifyTpSlResponse>

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

    // ==================== API KEYS ====================
    @GET("/api/users/api-keys")
    suspend fun getApiKeys(): Response<ApiKeysResponse>

    @GET("/api/users/api-keys/status")
    suspend fun getApiKeysStatus(): Response<ApiKeysStatusResponse>

    @POST("/api/users/api-keys/bybit")
    suspend fun saveBybitApiKeys(
        @Body request: SaveBybitApiKeysRequest
    ): Response<ApiKeysSaveResponse>

    @GET("/api/users/api-keys/bybit/test")
    suspend fun testBybitApiKeys(
        @Query("account_type") accountType: String
    ): Response<ApiTestResponse>

    @POST("/api/users/api-keys/hyperliquid")
    suspend fun saveHyperLiquidApiKeys(
        @Body request: SaveHyperLiquidApiKeysRequest
    ): Response<ApiKeysSaveResponse>

    @GET("/api/users/api-keys/hyperliquid/test")
    suspend fun testHyperLiquidApiKeys(): Response<ApiTestResponse>

    @POST("/api/users/api-keys/hyperliquid/test")
    suspend fun testHyperLiquidApiKeysWithKey(
        @Body request: TestHyperLiquidKeyRequest
    ): Response<HyperLiquidTestResponse>

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

// ==================== API RESPONSE WRAPPERS ====================

@kotlinx.serialization.Serializable
data class BalanceResponse(
    val success: Boolean = true,
    val data: BalanceData? = null,
    val error: String? = null
)

@kotlinx.serialization.Serializable
data class BalanceData(
    @kotlinx.serialization.SerialName("total_equity") val totalEquity: Double? = 0.0,
    @kotlinx.serialization.SerialName("available_balance") val availableBalance: Double? = 0.0,
    @kotlinx.serialization.SerialName("used_margin") val usedMargin: Double? = 0.0,
    @kotlinx.serialization.SerialName("unrealized_pnl") val unrealizedPnl: Double? = 0.0,
    @kotlinx.serialization.SerialName("today_pnl") val todayPnl: Double? = 0.0,
    @kotlinx.serialization.SerialName("week_pnl") val weekPnl: Double? = 0.0,
    val currency: String? = "USDT"
)

@kotlinx.serialization.Serializable
data class PositionsResponse(
    val success: Boolean = true,
    val data: List<PositionData>? = null,
    val error: String? = null
)

@kotlinx.serialization.Serializable
data class PositionData(
    val symbol: String,
    val side: String,
    val size: Double,
    @kotlinx.serialization.SerialName("entry_price") val entryPrice: Double,
    @kotlinx.serialization.SerialName("mark_price") val markPrice: Double? = null,
    @kotlinx.serialization.SerialName("unrealized_pnl") val unrealizedPnl: Double? = null,
    val leverage: Int = 1,
    val strategy: String? = null,
    @kotlinx.serialization.SerialName("sl_price") val slPrice: Double? = null,
    @kotlinx.serialization.SerialName("tp_price") val tpPrice: Double? = null
)

@kotlinx.serialization.Serializable
data class OrdersResponse(
    val success: Boolean = true,
    val data: List<OrderData>? = null,
    val error: String? = null
)

@kotlinx.serialization.Serializable
data class OrderData(
    @kotlinx.serialization.SerialName("order_id") val orderId: String,
    val symbol: String,
    val side: String,
    @kotlinx.serialization.SerialName("order_type") val orderType: String,
    val price: Double,
    val qty: Double,
    @kotlinx.serialization.SerialName("filled_qty") val filledQty: Double? = 0.0,
    val status: String,
    @kotlinx.serialization.SerialName("created_at") val createdAt: Long? = null
)

@kotlinx.serialization.Serializable
data class TradeStatsResponse(
    val success: Boolean = true,
    val data: TradeStatsData? = null,
    val error: String? = null
)

@kotlinx.serialization.Serializable
data class TradeStatsData(
    val total: Int = 0,
    val wins: Int = 0,
    val losses: Int = 0,
    val winrate: Double = 0.0,
    @kotlinx.serialization.SerialName("total_pnl") val totalPnl: Double = 0.0,
    @kotlinx.serialization.SerialName("avg_pnl") val avgPnl: Double = 0.0,
    @kotlinx.serialization.SerialName("best_trade") val bestTrade: Double = 0.0,
    @kotlinx.serialization.SerialName("worst_trade") val worstTrade: Double = 0.0,
    @kotlinx.serialization.SerialName("profit_factor") val profitFactor: Double = 0.0
)

@kotlinx.serialization.Serializable
data class TradesResponse(
    val success: Boolean = true,
    val data: List<TradeData>? = null,
    val trades: List<TradeData>? = null,  // iOS/WebApp format
    val error: String? = null
) {
    val allTrades: List<TradeData>
        get() = data ?: trades ?: emptyList()
}

@kotlinx.serialization.Serializable
data class TradeData(
    val id: String? = null,
    val symbol: String,
    val side: String,
    @kotlinx.serialization.SerialName("entry_price") val entryPrice: Double = 0.0,
    @kotlinx.serialization.SerialName("exit_price") val exitPrice: Double? = null,
    val size: Double? = null,
    val pnl: Double? = null,
    @kotlinx.serialization.SerialName("pnl_pct") val pnlPct: Double? = null,  // iOS format
    @kotlinx.serialization.SerialName("pnl_percent") val pnlPercent: Double? = null,  // WebApp format
    val strategy: String? = null,
    @kotlinx.serialization.SerialName("exit_reason") val exitReason: String? = null,
    val timestamp: String? = null,  // Server returns string, not Long
    val ts: String? = null,  // iOS format
    @kotlinx.serialization.SerialName("account_type") val accountType: String? = null
) {
    val pnlValue: Double get() = pnl ?: 0.0
    val pnlPercentValue: Double get() = pnlPct ?: pnlPercent ?: 0.0
    val timestampStr: String get() = timestamp ?: ts ?: ""
}

// ==================== MANUAL TRADING REQUESTS/RESPONSES ====================

@kotlinx.serialization.Serializable
data class PlaceOrderRequest(
    val symbol: String,
    val side: String,
    @kotlinx.serialization.SerialName("order_type") val orderType: String = "market",
    val qty: Double? = null,
    @kotlinx.serialization.SerialName("amount_usdt") val amountUsdt: Double? = null,
    val price: Double? = null,
    val leverage: Int? = null,
    @kotlinx.serialization.SerialName("take_profit") val takeProfit: Double? = null,
    @kotlinx.serialization.SerialName("stop_loss") val stopLoss: Double? = null,
    @kotlinx.serialization.SerialName("account_type") val accountType: String? = null,
    val exchange: String? = null
)

@kotlinx.serialization.Serializable
data class PlaceOrderResponse(
    val success: Boolean,
    @kotlinx.serialization.SerialName("order_id") val orderId: String? = null,
    val message: String? = null,
    @kotlinx.serialization.SerialName("executed_qty") val executedQty: Double? = null,
    @kotlinx.serialization.SerialName("executed_price") val executedPrice: Double? = null
)

@kotlinx.serialization.Serializable
data class SetLeverageRequest(
    val symbol: String,
    val leverage: Int
)

@kotlinx.serialization.Serializable
data class SetLeverageResponse(
    val success: Boolean,
    val message: String? = null
)

@kotlinx.serialization.Serializable
data class CancelOrderRequest(
    @kotlinx.serialization.SerialName("order_id") val orderId: String,
    val symbol: String,
    @kotlinx.serialization.SerialName("account_type") val accountType: String? = null,
    val exchange: String? = null
)

@kotlinx.serialization.Serializable
data class CancelOrderResponse(
    val success: Boolean,
    val message: String? = null
)

@kotlinx.serialization.Serializable
data class ModifyTpSlRequest(
    val symbol: String,
    val side: String,
    @kotlinx.serialization.SerialName("take_profit") val takeProfit: Double? = null,
    @kotlinx.serialization.SerialName("stop_loss") val stopLoss: Double? = null,
    @kotlinx.serialization.SerialName("account_type") val accountType: String? = null,
    val exchange: String? = null
)

@kotlinx.serialization.Serializable
data class ModifyTpSlResponse(
    val success: Boolean,
    val message: String? = null
)
// ==================== API KEYS MODELS ====================

@kotlinx.serialization.Serializable
data class ApiKeysResponse(
    val bybit: BybitApiKeysInfo? = null,
    val hyperliquid: HyperLiquidApiKeysInfo? = null
)

@kotlinx.serialization.Serializable
data class BybitApiKeysInfo(
    @kotlinx.serialization.SerialName("demo_configured") val demoConfigured: Boolean = false,
    @kotlinx.serialization.SerialName("real_configured") val realConfigured: Boolean = false,
    @kotlinx.serialization.SerialName("demo_api_key") val demoApiKeyMasked: String? = null,
    @kotlinx.serialization.SerialName("real_api_key") val realApiKeyMasked: String? = null
)

@kotlinx.serialization.Serializable
data class HyperLiquidApiKeysInfo(
    @kotlinx.serialization.SerialName("testnet_configured") val testnetConfigured: Boolean = false,
    @kotlinx.serialization.SerialName("mainnet_configured") val mainnetConfigured: Boolean = false,
    @kotlinx.serialization.SerialName("testnet_wallet") val testnetWalletMasked: String? = null,
    @kotlinx.serialization.SerialName("mainnet_wallet") val mainnetWalletMasked: String? = null
)

@kotlinx.serialization.Serializable
data class ApiKeysStatusResponse(
    @kotlinx.serialization.SerialName("bybit_demo") val bybitDemo: Boolean = false,
    @kotlinx.serialization.SerialName("bybit_real") val bybitReal: Boolean = false,
    @kotlinx.serialization.SerialName("hl_testnet") val hlTestnet: Boolean = false,
    @kotlinx.serialization.SerialName("hl_mainnet") val hlMainnet: Boolean = false
)

@kotlinx.serialization.Serializable
data class SaveBybitApiKeysRequest(
    @kotlinx.serialization.SerialName("account_type") val accountType: String,
    @kotlinx.serialization.SerialName("api_key") val apiKey: String,
    @kotlinx.serialization.SerialName("api_secret") val apiSecret: String
)

@kotlinx.serialization.Serializable
data class SaveHyperLiquidApiKeysRequest(
    @kotlinx.serialization.SerialName("account_type") val accountType: String,
    @kotlinx.serialization.SerialName("private_key") val privateKey: String,
    @kotlinx.serialization.SerialName("wallet_address") val walletAddress: String
)

@kotlinx.serialization.Serializable
data class TestHyperLiquidKeyRequest(
    @kotlinx.serialization.SerialName("private_key") val privateKey: String,
    @kotlinx.serialization.SerialName("is_testnet") val isTestnet: Boolean
)

@kotlinx.serialization.Serializable
data class HyperLiquidTestResponse(
    val valid: Boolean,
    @kotlinx.serialization.SerialName("api_wallet") val apiWallet: String? = null,
    @kotlinx.serialization.SerialName("main_wallet") val mainWallet: String? = null,
    val balance: Double? = null,
    val error: String? = null
)

@kotlinx.serialization.Serializable
data class ApiKeysSaveResponse(
    val success: Boolean,
    val message: String? = null
)

@kotlinx.serialization.Serializable
data class ApiTestResponse(
    val success: Boolean,
    val message: String? = null,
    val balance: Double? = null
)