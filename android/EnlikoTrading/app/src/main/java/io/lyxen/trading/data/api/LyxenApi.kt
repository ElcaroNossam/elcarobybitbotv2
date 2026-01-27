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
    suspend fun getCurrentUser(): Response<User>

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
    @GET("/api/activity/recent")
    suspend fun getRecentActivity(
        @Query("limit") limit: Int? = null
    ): Response<List<ActivityItem>>
}

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

@kotlinx.serialization.Serializable
data class ActivityItem(
    val id: Long,
    @kotlinx.serialization.SerialName("action_type") val actionType: String,
    @kotlinx.serialization.SerialName("action_category") val actionCategory: String,
    val source: String,
    @kotlinx.serialization.SerialName("created_at") val createdAt: String
)
