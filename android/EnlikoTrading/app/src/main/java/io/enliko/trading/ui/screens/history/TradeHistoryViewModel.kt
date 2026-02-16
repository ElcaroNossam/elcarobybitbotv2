package io.enliko.trading.ui.screens.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.local.dao.OrderDao
import io.enliko.trading.data.local.dao.TradeDao
import io.enliko.trading.data.local.entities.OrderEntity
import io.enliko.trading.data.local.entities.TradeEntity
import io.enliko.trading.data.repository.PreferencesRepository
import io.enliko.trading.util.AppLogger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for Trade History with offline-first approach
 * Loads cached data first, then updates from server
 */
@HiltViewModel
class TradeHistoryViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val tradeDao: TradeDao,
    private val orderDao: OrderDao,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    data class UiState(
        val isLoading: Boolean = true,
        val isRefreshing: Boolean = false,
        val selectedTab: HistoryTab = HistoryTab.TRADES,
        
        // Data
        val orders: List<OrderRecord> = emptyList(),
        val trades: List<TradeRecord> = emptyList(),
        val fundings: List<FundingRecord> = emptyList(),
        val pnlRecords: List<PnlRecord> = emptyList(),
        
        // Stats
        val totalTrades: Int = 0,
        val totalPnl: Double = 0.0,
        val winRate: Double = 0.0,
        
        val errorMessage: String? = null
    )
    
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    init {
        loadData()
    }
    
    fun selectTab(tab: HistoryTab) {
        _uiState.update { it.copy(selectedTab = tab) }
    }
    
    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isRefreshing = true) }
            fetchFromServer()
            _uiState.update { it.copy(isRefreshing = false) }
        }
    }
    
    private fun loadData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            // Load from cache first
            loadCachedData()
            
            // Then fetch from server
            fetchFromServer()
            
            _uiState.update { it.copy(isLoading = false) }
        }
    }
    
    private suspend fun loadCachedData() {
        try {
            val userId = preferencesRepository.userId.first()?.toLongOrNull() ?: return
            val exchange = preferencesRepository.exchange.first()
            val accountType = preferencesRepository.accountType.first()
            
            // Load cached trades (closed positions with PnL) - collect first value from Flow
            val cachedTrades = tradeDao.getTradesFlow(userId, exchange, accountType).first()
            val pnlRecords = cachedTrades.map { trade ->
                PnlRecord(
                    id = trade.id,
                    symbol = trade.symbol,
                    side = trade.side,
                    entryPrice = trade.entryPrice,
                    exitPrice = trade.exitPrice,
                    qty = trade.size,
                    pnl = trade.pnl,
                    pnlPercent = trade.pnlPercent,
                    closedAt = trade.timestamp.toString()  // Convert Long to String
                )
            }
            
            // Load cached orders
            val cachedOrders = orderDao.getAllOrders(userId, exchange, accountType)
            val orderRecords = cachedOrders.map { order ->
                OrderRecord(
                    id = order.orderId,
                    symbol = order.symbol,
                    side = order.side,
                    type = order.orderType,
                    price = order.price ?: 0.0,
                    qty = order.qty,
                    filledQty = order.filledQty,
                    status = order.status,
                    createdAt = order.createdAt
                )
            }
            
            // Calculate stats from cache
            val totalPnl = cachedTrades.sumOf { it.pnl }
            val winCount = cachedTrades.count { it.pnl > 0 }
            val winRate = if (cachedTrades.isNotEmpty()) winCount.toDouble() / cachedTrades.size * 100 else 0.0
            
            _uiState.update { 
                it.copy(
                    pnlRecords = pnlRecords,
                    orders = orderRecords,
                    totalTrades = cachedTrades.size,
                    totalPnl = totalPnl,
                    winRate = winRate
                )
            }
        } catch (e: Exception) {
            AppLogger.error("Failed to load cached data: ${e.message}")
        }
    }
    
    private suspend fun fetchFromServer() {
        try {
            val accountType = preferencesRepository.accountType.first()
            val exchange = preferencesRepository.exchange.first()
            val userId = preferencesRepository.userId.first()?.toLongOrNull() ?: 0L
            
            // Fetch orders using existing API method
            val ordersResponse = api.getOrders(exchange, accountType)
            if (ordersResponse.isSuccessful) {
                val ordersData = ordersResponse.body() ?: emptyList()
                val orderRecords = ordersData.map { order ->
                    OrderRecord(
                        id = order.orderId,
                        symbol = order.symbol,
                        side = order.side,
                        type = order.orderType,
                        price = order.price,
                        qty = order.qty,
                        filledQty = order.filledQty ?: 0.0,
                        status = order.status,
                        createdAt = order.createdAt ?: System.currentTimeMillis()
                    )
                }
                
                // Cache orders
                val orderEntities = orderRecords.map { record ->
                    OrderEntity(
                        orderId = record.id,
                        userId = userId,
                        symbol = record.symbol,
                        side = record.side,
                        orderType = record.type,
                        price = record.price,
                        qty = record.qty,
                        filledQty = record.filledQty,
                        status = record.status,
                        exchange = exchange,
                        accountType = accountType,
                        createdAt = record.createdAt
                    )
                }
                
                if (orderEntities.isNotEmpty()) {
                    orderDao.replaceAll(userId, exchange, accountType, orderEntities)
                }
                
                _uiState.update { it.copy(orders = orderRecords) }
            }
            
            // Fetch trade stats
            val statsResponse = api.getTradeStats(exchange, accountType)
            if (statsResponse.isSuccessful) {
                val stats = statsResponse.body()
                _uiState.update { 
                    it.copy(
                        totalTrades = stats?.total ?: 0,
                        totalPnl = stats?.totalPnl ?: 0.0,
                        winRate = stats?.winrate ?: 0.0
                    )
                }
            }
            
            // Fetch closed PnL records (trade_logs) using getTrades
            val tradesResponse = api.getTrades(exchange, accountType, limit = 50)
            if (tradesResponse.isSuccessful) {
                val tradesData = tradesResponse.body()?.allTrades ?: emptyList()
                val pnlRecords = tradesData.map { trade ->
                    PnlRecord(
                        id = trade.id ?: "${trade.symbol}_${trade.timestampStr}",
                        symbol = trade.symbol,
                        side = trade.side,
                        entryPrice = trade.entryPrice,
                        exitPrice = trade.exitPrice,
                        qty = trade.size,
                        pnl = trade.pnlValue,
                        pnlPercent = trade.pnlPercentValue,
                        closedAt = trade.timestampStr
                    )
                }
                
                // Convert to TradeRecord format for Trades tab (execution-like view)
                val tradeRecords = tradesData.map { trade ->
                    TradeRecord(
                        id = trade.id ?: "${trade.symbol}_${trade.timestampStr}",
                        symbol = trade.symbol,
                        side = trade.side,
                        price = trade.exitPrice, // Show exit price
                        qty = trade.size,
                        fee = 0.0, // Not available in trade_logs
                        realizedPnl = trade.pnlValue,
                        executedAt = trade.timestampStr
                    )
                }
                
                // Cache as TradeEntity for offline access
                val tradeEntities = pnlRecords.map { record ->
                    TradeEntity(
                        id = record.id,
                        userId = userId,
                        symbol = record.symbol,
                        side = record.side,
                        entryPrice = record.entryPrice,
                        exitPrice = record.exitPrice ?: 0.0,
                        size = record.qty ?: 0.0,
                        pnl = record.pnl ?: 0.0,
                        pnlPercent = record.pnlPercent ?: 0.0,
                        strategy = "unknown",
                        exitReason = null,
                        leverage = null,
                        exchange = exchange,
                        accountType = accountType,
                        timestamp = try { record.closedAt.toLong() } catch (e: Exception) { System.currentTimeMillis() }
                    )
                }
                
                if (tradeEntities.isNotEmpty()) {
                    tradeDao.insertAll(tradeEntities)
                }
                
                _uiState.update { 
                    it.copy(
                        pnlRecords = pnlRecords,
                        trades = tradeRecords
                    )
                }
            }
            
        } catch (e: Exception) {
            AppLogger.error("Failed to fetch from server: ${e.message}")
            _uiState.update { it.copy(errorMessage = "Failed to load: ${e.message}") }
        }
    }
    
    fun clearError() {
        _uiState.update { it.copy(errorMessage = null) }
    }
}
