package io.enliko.trading.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import io.enliko.trading.data.local.dao.*
import io.enliko.trading.data.local.entities.*

/**
 * Room Database for Enliko Trading Platform
 * 
 * Version History:
 * 1 - Initial schema with all entities
 * 2 - Added userId and synced fields to ActivityLogEntity
 */
@Database(
    entities = [
        PositionEntity::class,
        TradeEntity::class,
        SignalEntity::class,
        OrderEntity::class,
        StrategySettingsEntity::class,
        UserSettingsEntity::class,
        ApiKeyEntity::class,
        BalanceCacheEntity::class,
        TradeStatsCacheEntity::class,
        ScreenerCoinEntity::class,
        SyncMetadataEntity::class,
        ActivityLogEntity::class
    ],
    version = 2,
    exportSchema = false
)
abstract class EnlikoDatabase : RoomDatabase() {
    
    abstract fun positionDao(): PositionDao
    abstract fun tradeDao(): TradeDao
    abstract fun signalDao(): SignalDao
    abstract fun orderDao(): OrderDao
    abstract fun strategySettingsDao(): StrategySettingsDao
    abstract fun userSettingsDao(): UserSettingsDao
    abstract fun apiKeyDao(): ApiKeyDao
    abstract fun balanceCacheDao(): BalanceCacheDao
    abstract fun tradeStatsCacheDao(): TradeStatsCacheDao
    abstract fun screenerCoinDao(): ScreenerCoinDao
    abstract fun syncMetadataDao(): SyncMetadataDao
    abstract fun activityLogDao(): ActivityLogDao
    
    companion object {
        const val DATABASE_NAME = "enliko_trading.db"
    }
}
