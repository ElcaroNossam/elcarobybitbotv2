package io.enliko.trading.data.repository

import io.enliko.trading.data.api.*
import io.enliko.trading.data.local.dao.*
import io.enliko.trading.data.local.entities.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Trading Repository - Offline-first data layer
 * Caches API responses in Room database for offline access
 */
@Singleton
class TradingRepository @Inject constructor(
    private val api: EnlikoApi,
    private val positionDao: PositionDao,
    private val tradeDao: TradeDao,
    private val balanceCacheDao: BalanceCacheDao,
    private val orderDao: OrderDao,
    private val strategySettingsDao: StrategySettingsDao,
    private val syncMetadataDao: SyncMetadataDao
) {
    
    companion object {
        private const val CACHE_VALIDITY_MS = 5 * 60 * 1000L // 5 minutes
    }
    
    // ==================== POSITIONS ====================
    
    /**
     * Get positions with offline-first strategy
     * Returns cached data immediately, then refreshes from server
     */
    suspend fun getPositions(
        userId: Long,
        exchange: String,
        accountType: String,
        forceRefresh: Boolean = false
    ): Result<List<PositionData>> {
        // Try to return cached data first
        val cached = positionDao.getPositions(userId, exchange, accountType)
        
        if (cached.isNotEmpty() && !forceRefresh && isCacheValid("positions_$userId")) {
            return Result.success(cached.map { it.toPositionData() })
        }
        
        // Fetch from server
        return try {
            val response = api.getPositions(exchange, accountType)
            if (response.isSuccessful && response.body() != null) {
                val positions = response.body() ?: emptyList()
                
                // Cache in database
                val entities = positions.map { it.toEntity(userId, exchange, accountType) }
                positionDao.replaceAll(userId, exchange, accountType, entities)
                updateSyncTimestamp("positions_$userId")
                
                Result.success(positions)
            } else {
                // Return cached on error
                if (cached.isNotEmpty()) {
                    Result.success(cached.map { it.toPositionData() })
                } else {
                    Result.failure(Exception("Failed to load positions"))
                }
            }
        } catch (e: Exception) {
            // Return cached on network error
            if (cached.isNotEmpty()) {
                Result.success(cached.map { it.toPositionData() })
            } else {
                Result.failure(e)
            }
        }
    }
    
    /**
     * Observable positions flow - updates automatically
     */
    fun getPositionsFlow(userId: Long, exchange: String, accountType: String): Flow<List<PositionEntity>> {
        return positionDao.getPositionsFlow(userId, exchange, accountType)
    }
    
    // ==================== BALANCE ====================
    
    suspend fun getBalance(
        userId: Long,
        exchange: String,
        accountType: String,
        forceRefresh: Boolean = false
    ): Result<BalanceData> {
        val cached = balanceCacheDao.getBalance(userId, exchange, accountType)
        
        if (cached != null && !forceRefresh && isCacheValid("balance_$userId")) {
            return Result.success(cached.toBalanceData())
        }
        
        return try {
            val response = api.getBalance(exchange, accountType)
            if (response.isSuccessful && response.body() != null) {
                val balance = response.body()!!
                
                // Cache
                balanceCacheDao.insert(balance.toEntity(userId, exchange, accountType))
                updateSyncTimestamp("balance_$userId")
                
                Result.success(balance)
            } else {
                cached?.let { Result.success(it.toBalanceData()) }
                    ?: Result.failure(Exception("Failed to load balance"))
            }
        } catch (e: Exception) {
            cached?.let { Result.success(it.toBalanceData()) }
                ?: Result.failure(e)
        }
    }
    
    fun getBalanceFlow(userId: Long, exchange: String, accountType: String): Flow<BalanceCacheEntity?> {
        return balanceCacheDao.getBalanceFlow(userId, exchange, accountType)
    }
    
    // ==================== ORDERS ====================
    
    suspend fun getOrders(
        userId: Long,
        exchange: String,
        accountType: String,
        forceRefresh: Boolean = false
    ): Result<List<OrderData>> {
        val cached = orderDao.getAllOrders(userId, exchange, accountType)
        
        if (cached.isNotEmpty() && !forceRefresh && isCacheValid("orders_$userId")) {
            return Result.success(cached.map { it.toOrderData() })
        }
        
        return try {
            val response = api.getOrders(exchange, accountType)
            if (response.isSuccessful && response.body() != null) {
                val orders = response.body()!!
                
                val entities = orders.map { it.toEntity(userId, exchange, accountType) }
                orderDao.replaceAll(userId, exchange, accountType, entities)
                updateSyncTimestamp("orders_$userId")
                
                Result.success(orders)
            } else {
                if (cached.isNotEmpty()) Result.success(cached.map { it.toOrderData() })
                else Result.failure(Exception("Failed to load orders"))
            }
        } catch (e: Exception) {
            if (cached.isNotEmpty()) Result.success(cached.map { it.toOrderData() })
            else Result.failure(e)
        }
    }
    
    fun getOrdersFlow(userId: Long, exchange: String, accountType: String): Flow<List<OrderEntity>> {
        return orderDao.getActiveOrdersFlow(userId, exchange, accountType)
    }
    
    // ==================== TRADES HISTORY ====================
    
    suspend fun getTrades(
        userId: Long,
        exchange: String,
        accountType: String,
        limit: Int = 50,
        forceRefresh: Boolean = false
    ): Result<List<TradeData>> {
        val cached = tradeDao.getRecentTrades(userId, exchange, accountType, limit)
        
        if (cached.isNotEmpty() && !forceRefresh && isCacheValid("trades_$userId")) {
            return Result.success(cached.map { it.toTradeData() })
        }
        
        return try {
            val response = api.getTrades(exchange, accountType, limit)
            if (response.isSuccessful && response.body()?.data != null) {
                val trades = response.body()!!.data!!
                
                val entities = trades.map { it.toEntity(userId, exchange, accountType) }
                tradeDao.insertIgnore(entities)  // Don't replace - keep history
                updateSyncTimestamp("trades_$userId")
                
                Result.success(trades)
            } else {
                if (cached.isNotEmpty()) Result.success(cached.map { it.toTradeData() })
                else Result.failure(Exception("Failed to load trades"))
            }
        } catch (e: Exception) {
            if (cached.isNotEmpty()) Result.success(cached.map { it.toTradeData() })
            else Result.failure(e)
        }
    }
    
    // ==================== CACHE UTILS ====================
    
    private suspend fun isCacheValid(key: String): Boolean {
        val lastSync = syncMetadataDao.getTimestamp(key) ?: return false
        return System.currentTimeMillis() - lastSync < CACHE_VALIDITY_MS
    }
    
    private suspend fun updateSyncTimestamp(key: String) {
        syncMetadataDao.set(SyncMetadataEntity(key, "synced"))
    }
    
    /**
     * Clear all cached data for user
     */
    suspend fun clearCache(userId: Long) {
        positionDao.deleteAll(userId, "", "")  // Will need actual exchange/accountType
        balanceCacheDao.deleteAllForUser(userId)
        orderDao.deleteAll(userId, "", "")
    }
}

// ==================== ENTITY MAPPERS ====================

// PositionData -> PositionEntity
private fun PositionData.toEntity(userId: Long, exchange: String, accountType: String) = PositionEntity(
    id = "${userId}_${symbol}_${exchange}_${accountType}",
    userId = userId,
    symbol = symbol,
    side = side,
    size = size,
    entryPrice = entryPrice,
    markPrice = markPrice ?: entryPrice,
    leverage = leverage,
    unrealizedPnl = unrealizedPnl ?: 0.0,
    unrealizedPnlPercent = 0.0, // Calculate from markPrice/entryPrice
    liquidationPrice = null,
    takeProfitPrice = tpPrice,
    stopLossPrice = slPrice,
    strategy = strategy,
    exchange = exchange,
    accountType = accountType,
    positionValue = size * entryPrice,
    margin = null,
    createdAt = System.currentTimeMillis()
)

// PositionEntity -> PositionData
private fun PositionEntity.toPositionData() = PositionData(
    symbol = symbol,
    side = side,
    size = size,
    entryPrice = entryPrice,
    markPrice = markPrice,
    unrealizedPnl = unrealizedPnl,
    leverage = leverage,
    strategy = strategy,
    slPrice = stopLossPrice,
    tpPrice = takeProfitPrice
)

// BalanceData -> BalanceCacheEntity
private fun BalanceData.toEntity(userId: Long, exchange: String, accountType: String) = BalanceCacheEntity(
    userId = userId,
    exchange = exchange,
    accountType = accountType,
    equity = totalEquity ?: 0.0,
    availableBalance = availableBalance ?: 0.0,
    walletBalance = totalEquity ?: 0.0, // Use equity as wallet balance
    unrealizedPnl = unrealizedPnl ?: 0.0,
    marginUsed = usedMargin ?: 0.0,
    todayPnl = todayPnl,
    weekPnl = weekPnl
)

// BalanceCacheEntity -> BalanceData
private fun BalanceCacheEntity.toBalanceData() = BalanceData(
    totalEquity = equity,
    availableBalance = availableBalance,
    usedMargin = marginUsed,
    unrealizedPnl = unrealizedPnl,
    todayPnl = todayPnl,
    weekPnl = weekPnl,
    currency = "USDT"
)

// OrderData -> OrderEntity
private fun OrderData.toEntity(userId: Long, exchange: String, accountType: String) = OrderEntity(
    orderId = orderId,
    userId = userId,
    symbol = symbol,
    side = side,
    orderType = orderType,
    price = price,
    qty = qty,
    filledQty = filledQty ?: 0.0,
    status = status,
    exchange = exchange,
    accountType = accountType,
    createdAt = createdAt ?: System.currentTimeMillis()
)

// OrderEntity -> OrderData
private fun OrderEntity.toOrderData() = OrderData(
    orderId = orderId,
    symbol = symbol,
    side = side,
    orderType = orderType,
    price = price ?: 0.0,
    qty = qty,
    filledQty = filledQty,
    status = status,
    createdAt = createdAt
)

// TradeData -> TradeEntity
private fun TradeData.toEntity(userId: Long, exchange: String, accountType: String) = TradeEntity(
    id = id ?: "${userId}_${symbol}_$timestampStr",
    userId = userId,
    symbol = symbol,
    side = side,
    entryPrice = entryPrice,
    exitPrice = exitPrice ?: 0.0,
    size = size ?: 0.0,
    pnl = pnlValue,
    pnlPercent = pnlPercentValue,
    strategy = strategy ?: "manual",
    exitReason = exitReason,
    leverage = null,
    exchange = exchange,
    accountType = accountType,
    timestamp = try { timestampStr.toLong() } catch (e: Exception) { System.currentTimeMillis() }
)

// TradeEntity -> TradeData
private fun TradeEntity.toTradeData() = TradeData(
    id = id,
    symbol = symbol,
    side = side,
    entryPrice = entryPrice,
    exitPrice = exitPrice,
    size = size,
    pnl = pnl,
    pnlPct = pnlPercent,
    pnlPercent = pnlPercent,
    strategy = strategy,
    exitReason = exitReason,
    timestamp = timestamp.toString(),
    ts = timestamp.toString(),
    accountType = accountType
)
