package io.enliko.trading.data.local.dao

import androidx.paging.PagingSource
import androidx.room.*
import io.enliko.trading.data.local.entities.*
import kotlinx.coroutines.flow.Flow

/**
 * Room DAOs for Enliko Trading Platform
 * Offline-first with reactive updates via Flow
 */

// ==================== POSITIONS DAO ====================

@Dao
interface PositionDao {
    
    @Query("SELECT * FROM positions WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType ORDER BY unrealizedPnl DESC")
    fun getPositionsFlow(userId: Long, exchange: String, accountType: String): Flow<List<PositionEntity>>
    
    @Query("SELECT * FROM positions WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType")
    suspend fun getPositions(userId: Long, exchange: String, accountType: String): List<PositionEntity>
    
    @Query("SELECT * FROM positions WHERE userId = :userId AND symbol = :symbol AND exchange = :exchange AND accountType = :accountType LIMIT 1")
    suspend fun getPosition(userId: Long, symbol: String, exchange: String, accountType: String): PositionEntity?
    
    @Query("SELECT COUNT(*) FROM positions WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType")
    fun getPositionCountFlow(userId: Long, exchange: String, accountType: String): Flow<Int>
    
    @Query("SELECT SUM(unrealizedPnl) FROM positions WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType")
    fun getTotalUnrealizedPnlFlow(userId: Long, exchange: String, accountType: String): Flow<Double?>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(positions: List<PositionEntity>)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(position: PositionEntity)
    
    @Delete
    suspend fun delete(position: PositionEntity)
    
    @Query("DELETE FROM positions WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType")
    suspend fun deleteAll(userId: Long, exchange: String, accountType: String)
    
    @Query("DELETE FROM positions WHERE id = :id")
    suspend fun deleteById(id: String)
    
    @Transaction
    suspend fun replaceAll(userId: Long, exchange: String, accountType: String, positions: List<PositionEntity>) {
        deleteAll(userId, exchange, accountType)
        insertAll(positions)
    }
}

// ==================== TRADES DAO ====================

@Dao
interface TradeDao {
    
    @Query("SELECT * FROM trades WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType ORDER BY timestamp DESC")
    fun getTradesFlow(userId: Long, exchange: String, accountType: String): Flow<List<TradeEntity>>
    
    @Query("SELECT * FROM trades WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType ORDER BY timestamp DESC")
    fun getTradesPaging(userId: Long, exchange: String, accountType: String): PagingSource<Int, TradeEntity>
    
    @Query("SELECT * FROM trades WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType AND strategy = :strategy ORDER BY timestamp DESC")
    fun getTradesByStrategyPaging(userId: Long, exchange: String, accountType: String, strategy: String): PagingSource<Int, TradeEntity>
    
    @Query("SELECT * FROM trades WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getRecentTrades(userId: Long, exchange: String, accountType: String, limit: Int = 50): List<TradeEntity>
    
    @Query("SELECT * FROM trades WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType AND timestamp >= :since ORDER BY timestamp DESC")
    suspend fun getTradesSince(userId: Long, exchange: String, accountType: String, since: Long): List<TradeEntity>
    
    @Query("SELECT SUM(pnl) FROM trades WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType AND timestamp >= :since")
    suspend fun getPnlSince(userId: Long, exchange: String, accountType: String, since: Long): Double?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(trades: List<TradeEntity>)
    
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertIgnore(trades: List<TradeEntity>)
    
    @Query("DELETE FROM trades WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType")
    suspend fun deleteAll(userId: Long, exchange: String, accountType: String)
    
    @Query("DELETE FROM trades WHERE timestamp < :before")
    suspend fun deleteOlderThan(before: Long)
}

// ==================== SIGNALS DAO ====================

@Dao
interface SignalDao {
    
    @Query("SELECT * FROM signals WHERE status = 'active' ORDER BY timestamp DESC")
    fun getActiveSignalsFlow(): Flow<List<SignalEntity>>
    
    @Query("SELECT * FROM signals WHERE strategy = :strategy ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getSignalsByStrategy(strategy: String, limit: Int = 50): List<SignalEntity>
    
    @Query("SELECT * FROM signals WHERE direction = :direction AND status = 'active' ORDER BY timestamp DESC")
    fun getSignalsByDirection(direction: String): Flow<List<SignalEntity>>
    
    @Query("SELECT * FROM signals ORDER BY timestamp DESC")
    fun getAllSignalsPaging(): PagingSource<Int, SignalEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(signals: List<SignalEntity>)
    
    @Query("UPDATE signals SET status = :status WHERE id = :id")
    suspend fun updateStatus(id: String, status: String)
    
    @Query("DELETE FROM signals WHERE timestamp < :before")
    suspend fun deleteOlderThan(before: Long)
    
    @Query("DELETE FROM signals")
    suspend fun deleteAll()
}

// ==================== ORDERS DAO ====================

@Dao
interface OrderDao {
    
    @Query("SELECT * FROM orders WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType AND status NOT IN ('Filled', 'Cancelled') ORDER BY createdAt DESC")
    fun getActiveOrdersFlow(userId: Long, exchange: String, accountType: String): Flow<List<OrderEntity>>
    
    @Query("SELECT * FROM orders WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType ORDER BY createdAt DESC")
    suspend fun getAllOrders(userId: Long, exchange: String, accountType: String): List<OrderEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(orders: List<OrderEntity>)
    
    @Query("DELETE FROM orders WHERE orderId = :orderId")
    suspend fun deleteById(orderId: String)
    
    @Query("DELETE FROM orders WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType")
    suspend fun deleteAll(userId: Long, exchange: String, accountType: String)
    
    @Transaction
    suspend fun replaceAll(userId: Long, exchange: String, accountType: String, orders: List<OrderEntity>) {
        deleteAll(userId, exchange, accountType)
        insertAll(orders)
    }
}

// ==================== STRATEGY SETTINGS DAO ====================

@Dao
interface StrategySettingsDao {
    
    @Query("SELECT * FROM strategy_settings WHERE userId = :userId AND strategy = :strategy AND exchange = :exchange")
    fun getSettingsFlow(userId: Long, strategy: String, exchange: String): Flow<List<StrategySettingsEntity>>
    
    @Query("SELECT * FROM strategy_settings WHERE userId = :userId AND strategy = :strategy AND side = :side AND exchange = :exchange LIMIT 1")
    suspend fun getSettings(userId: Long, strategy: String, side: String, exchange: String): StrategySettingsEntity?
    
    @Query("SELECT * FROM strategy_settings WHERE userId = :userId AND exchange = :exchange")
    suspend fun getAllSettings(userId: Long, exchange: String): List<StrategySettingsEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(settings: StrategySettingsEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(settings: List<StrategySettingsEntity>)
    
    @Query("DELETE FROM strategy_settings WHERE userId = :userId")
    suspend fun deleteAllForUser(userId: Long)
    
    @Query("UPDATE strategy_settings SET enabled = :enabled, updatedAt = :now WHERE userId = :userId AND strategy = :strategy AND side = :side AND exchange = :exchange")
    suspend fun updateEnabled(userId: Long, strategy: String, side: String, exchange: String, enabled: Boolean, now: Long = System.currentTimeMillis())
}

// ==================== USER SETTINGS DAO ====================

@Dao
interface UserSettingsDao {
    
    @Query("SELECT * FROM user_settings WHERE userId = :userId LIMIT 1")
    fun getUserSettingsFlow(userId: Long): Flow<UserSettingsEntity?>
    
    @Query("SELECT * FROM user_settings WHERE userId = :userId LIMIT 1")
    suspend fun getUserSettings(userId: Long): UserSettingsEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(settings: UserSettingsEntity)
    
    @Query("UPDATE user_settings SET exchangeType = :exchange, updatedAt = :now WHERE userId = :userId")
    suspend fun updateExchange(userId: Long, exchange: String, now: Long = System.currentTimeMillis())
    
    @Query("UPDATE user_settings SET tradingMode = :mode, updatedAt = :now WHERE userId = :userId")
    suspend fun updateTradingMode(userId: Long, mode: String, now: Long = System.currentTimeMillis())
    
    @Query("UPDATE user_settings SET language = :lang, updatedAt = :now WHERE userId = :userId")
    suspend fun updateLanguage(userId: Long, lang: String, now: Long = System.currentTimeMillis())
    
    @Query("DELETE FROM user_settings WHERE userId = :userId")
    suspend fun delete(userId: Long)
}

// ==================== API KEYS DAO ====================

@Dao
interface ApiKeyDao {
    
    @Query("SELECT * FROM api_keys WHERE userId = :userId")
    suspend fun getAllKeys(userId: Long): List<ApiKeyEntity>
    
    @Query("SELECT * FROM api_keys WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType LIMIT 1")
    suspend fun getKey(userId: Long, exchange: String, accountType: String): ApiKeyEntity?
    
    @Query("SELECT EXISTS(SELECT 1 FROM api_keys WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType AND isConfigured = 1)")
    suspend fun isConfigured(userId: Long, exchange: String, accountType: String): Boolean
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(key: ApiKeyEntity)
    
    @Query("DELETE FROM api_keys WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType")
    suspend fun delete(userId: Long, exchange: String, accountType: String)
    
    @Query("DELETE FROM api_keys WHERE userId = :userId")
    suspend fun deleteAllForUser(userId: Long)
}

// ==================== BALANCE CACHE DAO ====================

@Dao
interface BalanceCacheDao {
    
    @Query("SELECT * FROM balance_cache WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType LIMIT 1")
    fun getBalanceFlow(userId: Long, exchange: String, accountType: String): Flow<BalanceCacheEntity?>
    
    @Query("SELECT * FROM balance_cache WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType LIMIT 1")
    suspend fun getBalance(userId: Long, exchange: String, accountType: String): BalanceCacheEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(balance: BalanceCacheEntity)
    
    @Query("DELETE FROM balance_cache WHERE userId = :userId")
    suspend fun deleteAllForUser(userId: Long)
}

// ==================== TRADE STATS CACHE DAO ====================

@Dao
interface TradeStatsCacheDao {
    
    @Query("SELECT * FROM trade_stats_cache WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType AND period = :period LIMIT 1")
    fun getStatsFlow(userId: Long, exchange: String, accountType: String, period: String): Flow<TradeStatsCacheEntity?>
    
    @Query("SELECT * FROM trade_stats_cache WHERE userId = :userId AND exchange = :exchange AND accountType = :accountType AND period = :period LIMIT 1")
    suspend fun getStats(userId: Long, exchange: String, accountType: String, period: String): TradeStatsCacheEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(stats: TradeStatsCacheEntity)
    
    @Query("DELETE FROM trade_stats_cache WHERE userId = :userId")
    suspend fun deleteAllForUser(userId: Long)
}

// ==================== SCREENER CACHE DAO ====================

@Dao
interface ScreenerCoinDao {
    
    @Query("SELECT * FROM screener_coins ORDER BY volume24h DESC")
    fun getAllCoinsFlow(): Flow<List<ScreenerCoinEntity>>
    
    @Query("SELECT * FROM screener_coins ORDER BY changePercent24h DESC LIMIT :limit")
    fun getTopGainersFlow(limit: Int = 10): Flow<List<ScreenerCoinEntity>>
    
    @Query("SELECT * FROM screener_coins ORDER BY changePercent24h ASC LIMIT :limit")
    fun getTopLosersFlow(limit: Int = 10): Flow<List<ScreenerCoinEntity>>
    
    @Query("SELECT * FROM screener_coins WHERE symbol LIKE '%' || :query || '%' ORDER BY volume24h DESC")
    suspend fun search(query: String): List<ScreenerCoinEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(coins: List<ScreenerCoinEntity>)
    
    @Query("DELETE FROM screener_coins")
    suspend fun deleteAll()
    
    @Transaction
    suspend fun replaceAll(coins: List<ScreenerCoinEntity>) {
        deleteAll()
        insertAll(coins)
    }
}

// ==================== SYNC METADATA DAO ====================

@Dao
interface SyncMetadataDao {
    
    @Query("SELECT * FROM sync_metadata WHERE `key` = :key LIMIT 1")
    suspend fun get(key: String): SyncMetadataEntity?
    
    @Query("SELECT timestamp FROM sync_metadata WHERE `key` = :key")
    suspend fun getTimestamp(key: String): Long?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun set(metadata: SyncMetadataEntity)
    
    @Query("DELETE FROM sync_metadata WHERE `key` = :key")
    suspend fun delete(key: String)
}

// ==================== ACTIVITY LOG DAO ====================

@Dao
interface ActivityLogDao {
    
    @Query("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentActivityFlow(limit: Int = 50): Flow<List<ActivityLogEntity>>
    
    @Query("SELECT * FROM activity_log WHERE actionCategory = :category ORDER BY timestamp DESC")
    fun getByCategory(category: String): PagingSource<Int, ActivityLogEntity>
    
    @Insert
    suspend fun insert(log: ActivityLogEntity)
    
    @Query("DELETE FROM activity_log WHERE timestamp < :before")
    suspend fun deleteOlderThan(before: Long)
    
    @Query("SELECT * FROM activity_log WHERE synced = 0 ORDER BY timestamp ASC LIMIT 50")
    suspend fun getUnsyncedActivities(): List<ActivityLogEntity>
    
    @Query("UPDATE activity_log SET synced = 1 WHERE id = :id")
    suspend fun markAsSynced(id: Long)
}
