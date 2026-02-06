package io.enliko.trading.data.local.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * Room Entities for offline-first architecture
 * Enliko Trading Platform - Android App
 */

// ==================== POSITIONS ====================

@Entity(
    tableName = "positions",
    indices = [
        Index(value = ["userId"]),
        Index(value = ["symbol"]),
        Index(value = ["exchange", "accountType"])
    ]
)
data class PositionEntity(
    @PrimaryKey
    val id: String, // Composite: "{userId}_{symbol}_{exchange}_{accountType}"
    val userId: Long,
    val symbol: String,
    val side: String, // "Buy" or "Sell"
    val size: Double,
    val entryPrice: Double,
    val markPrice: Double,
    val leverage: Int,
    val unrealizedPnl: Double,
    val unrealizedPnlPercent: Double,
    val liquidationPrice: Double?,
    val takeProfitPrice: Double?,
    val stopLossPrice: Double?,
    val strategy: String?,
    val exchange: String, // "bybit" or "hyperliquid"
    val accountType: String, // "demo", "real", "testnet", "mainnet"
    val positionValue: Double,
    val margin: Double?,
    val createdAt: Long,
    val updatedAt: Long = System.currentTimeMillis()
)

// ==================== TRADES (HISTORY) ====================

@Entity(
    tableName = "trades",
    indices = [
        Index(value = ["userId"]),
        Index(value = ["symbol"]),
        Index(value = ["strategy"]),
        Index(value = ["timestamp"])
    ]
)
data class TradeEntity(
    @PrimaryKey
    val id: String, // Server trade ID or generated
    val userId: Long,
    val symbol: String,
    val side: String,
    val entryPrice: Double,
    val exitPrice: Double,
    val size: Double,
    val pnl: Double,
    val pnlPercent: Double,
    val strategy: String,
    val exitReason: String?, // "TP", "SL", "MANUAL", "ATR"
    val leverage: Int?,
    val exchange: String,
    val accountType: String,
    val timestamp: Long,
    val syncedAt: Long = System.currentTimeMillis()
)

// ==================== SIGNALS ====================

@Entity(
    tableName = "signals",
    indices = [
        Index(value = ["strategy"]),
        Index(value = ["symbol"]),
        Index(value = ["timestamp"])
    ]
)
data class SignalEntity(
    @PrimaryKey
    val id: String,
    val strategy: String,
    val symbol: String,
    val direction: String, // "long" or "short"
    val entryPrice: Double?,
    val takeProfit: Double?,
    val stopLoss: Double?,
    val confidence: Double?, // 0.0 - 1.0
    val timeframe: String?,
    val message: String?,
    val status: String, // "active", "triggered", "expired"
    val timestamp: Long,
    val syncedAt: Long = System.currentTimeMillis()
)

// ==================== ORDERS ====================

@Entity(
    tableName = "orders",
    indices = [
        Index(value = ["userId"]),
        Index(value = ["symbol"]),
        Index(value = ["status"])
    ]
)
data class OrderEntity(
    @PrimaryKey
    val orderId: String,
    val userId: Long,
    val symbol: String,
    val side: String,
    val orderType: String, // "Market", "Limit"
    val price: Double?,
    val qty: Double,
    val filledQty: Double,
    val status: String, // "New", "Filled", "PartiallyFilled", "Cancelled"
    val exchange: String,
    val accountType: String,
    val createdAt: Long,
    val updatedAt: Long = System.currentTimeMillis()
)

// ==================== STRATEGY SETTINGS ====================

@Entity(
    tableName = "strategy_settings",
    primaryKeys = ["userId", "strategy", "side", "exchange"]
)
data class StrategySettingsEntity(
    val userId: Long,
    val strategy: String, // "oi", "scryptomera", "scalper", "elcaro", "fibonacci", "rsi_bb"
    val side: String, // "long" or "short"
    val exchange: String, // "bybit" or "hyperliquid"
    val enabled: Boolean = true,
    val percent: Double = 1.0,
    val tpPercent: Double = 8.0,
    val slPercent: Double = 3.0,
    val leverage: Int = 10,
    val useAtr: Boolean = false,
    val atrPeriods: Int = 14,
    val atrMultiplierSl: Double = 1.5,
    val atrTriggerPct: Double = 0.5,
    val atrStepPct: Double = 0.3,
    val orderType: String = "market",
    val limitOffsetPct: Double = 0.1,
    val direction: String = "all", // "all", "long", "short"
    val dcaEnabled: Boolean = false,
    val dcaPct1: Double = 10.0,
    val dcaPct2: Double = 25.0,
    val maxPositions: Int = 0,
    val coinsGroup: String = "ALL",
    val beEnabled: Boolean = false,
    val beTriggerPct: Double = 1.0,
    val partialTpEnabled: Boolean = false,
    val partialTp1TriggerPct: Double = 2.0,
    val partialTp1ClosePct: Double = 30.0,
    val partialTp2TriggerPct: Double = 5.0,
    val partialTp2ClosePct: Double = 50.0,
    val updatedAt: Long = System.currentTimeMillis()
)

// ==================== USER SETTINGS ====================

@Entity(tableName = "user_settings")
data class UserSettingsEntity(
    @PrimaryKey
    val userId: Long,
    val email: String?,
    val firstName: String?,
    val lastName: String?,
    val telegramUsername: String?,
    val language: String = "en",
    val exchangeType: String = "bybit", // Current active exchange
    val tradingMode: String = "demo", // "demo", "real", "both"
    val hlTestnet: Boolean = true, // For HyperLiquid
    val bybitDemoConfigured: Boolean = false,
    val bybitRealConfigured: Boolean = false,
    val hlTestnetConfigured: Boolean = false,
    val hlMainnetConfigured: Boolean = false,
    val isAllowed: Boolean = false,
    val isPremium: Boolean = false,
    val premiumUntil: Long? = null,
    val updatedAt: Long = System.currentTimeMillis()
)

// ==================== API KEYS (Encrypted) ====================

@Entity(
    tableName = "api_keys",
    primaryKeys = ["userId", "exchange", "accountType"]
)
data class ApiKeyEntity(
    val userId: Long,
    val exchange: String, // "bybit" or "hyperliquid"
    val accountType: String, // "demo", "real", "testnet", "mainnet"
    val apiKey: String, // Encrypted
    val apiSecret: String, // Encrypted (or privateKey for HL)
    val walletAddress: String?, // For HyperLiquid
    val isConfigured: Boolean = true,
    val updatedAt: Long = System.currentTimeMillis()
)

// ==================== BALANCE CACHE ====================

@Entity(
    tableName = "balance_cache",
    primaryKeys = ["userId", "exchange", "accountType"]
)
data class BalanceCacheEntity(
    val userId: Long,
    val exchange: String,
    val accountType: String,
    val equity: Double,
    val availableBalance: Double,
    val walletBalance: Double,
    val unrealizedPnl: Double,
    val marginUsed: Double,
    val todayPnl: Double?,
    val weekPnl: Double?,
    val updatedAt: Long = System.currentTimeMillis()
)

// ==================== TRADE STATS CACHE ====================

@Entity(
    tableName = "trade_stats_cache",
    primaryKeys = ["userId", "exchange", "accountType", "period"]
)
data class TradeStatsCacheEntity(
    val userId: Long,
    val exchange: String,
    val accountType: String,
    val period: String, // "7d", "30d", "all"
    val totalTrades: Int,
    val winningTrades: Int,
    val losingTrades: Int,
    val winRate: Double,
    val totalPnl: Double,
    val avgWin: Double,
    val avgLoss: Double,
    val bestTrade: Double,
    val worstTrade: Double,
    val profitFactor: Double,
    val updatedAt: Long = System.currentTimeMillis()
)

// ==================== SCREENER CACHE ====================

@Entity(
    tableName = "screener_coins",
    indices = [Index(value = ["changePercent24h"])]
)
data class ScreenerCoinEntity(
    @PrimaryKey
    val symbol: String,
    val price: Double,
    val changePercent24h: Double,
    val volume24h: Double,
    val high24h: Double,
    val low24h: Double,
    val openInterest: Double?,
    val fundingRate: Double?,
    val rsi: Double?,
    val trend: String?, // "bullish", "bearish", "neutral"
    val updatedAt: Long = System.currentTimeMillis()
)

// ==================== SYNC METADATA ====================

@Entity(tableName = "sync_metadata")
data class SyncMetadataEntity(
    @PrimaryKey
    val key: String, // e.g., "positions_last_sync", "trades_last_sync"
    val value: String,
    val timestamp: Long = System.currentTimeMillis()
)

// ==================== ACTIVITY LOG ====================

@Entity(
    tableName = "activity_log",
    indices = [
        Index(value = ["timestamp"]),
        Index(value = ["userId"]),
        Index(value = ["synced"])
    ]
)
data class ActivityLogEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val userId: Long,
    val actionType: String, // "trade_opened", "trade_closed", "settings_changed", etc.
    val actionCategory: String, // "trading", "settings", "auth"
    val source: String, // "android", "ios", "webapp", "telegram"
    val entityType: String?,
    val oldValue: String?, // JSON
    val newValue: String?, // JSON
    val message: String? = null,
    val timestamp: Long = System.currentTimeMillis(),
    val synced: Boolean = false
)
