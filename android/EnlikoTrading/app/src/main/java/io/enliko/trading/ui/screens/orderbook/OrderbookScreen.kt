package io.enliko.trading.ui.screens.orderbook

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import kotlinx.coroutines.delay
import kotlin.random.Random
import io.enliko.trading.util.LocalStrings

// MARK: - Data Models
data class OrderBookLevel(
    val price: Double,
    val quantity: Double,
    val total: Double,
    val percentage: Double // For depth visualization
)

data class RecentTrade(
    val price: Double,
    val quantity: Double,
    val isBuy: Boolean,
    val timestamp: Long
)

enum class OrderBookMode { BOTH, BIDS, ASKS }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrderbookScreen(
    symbol: String = "BTCUSDT",
    onNavigateBack: () -> Unit = {},
    onPriceSelected: (Double) -> Unit = {}
) {
    val strings = LocalStrings.current
    var mode by remember { mutableStateOf(OrderBookMode.BOTH) }
    var precision by remember { mutableIntStateOf(2) }
    var isLoading by remember { mutableStateOf(true) }
    
    var asks by remember { mutableStateOf<List<OrderBookLevel>>(emptyList()) }
    var bids by remember { mutableStateOf<List<OrderBookLevel>>(emptyList()) }
    var recentTrades by remember { mutableStateOf<List<RecentTrade>>(emptyList()) }
    var lastPrice by remember { mutableDoubleStateOf(0.0) }
    var markPrice by remember { mutableDoubleStateOf(0.0) }
    var spread by remember { mutableDoubleStateOf(0.0) }
    
    // Simulate real-time data
    LaunchedEffect(Unit) {
        // Initial load
        val basePrice = 98500.0
        lastPrice = basePrice
        markPrice = basePrice + Random.nextDouble(-10.0, 10.0)
        
        asks = (0..14).map { i ->
            val price = basePrice + (i + 1) * 5.0
            val qty = Random.nextDouble(0.1, 5.0)
            OrderBookLevel(price, qty, 0.0, 0.0)
        }.reversed().let { list ->
            val totalQty = list.sumOf { it.quantity }
            var cumulative = 0.0
            list.map { level ->
                cumulative += level.quantity
                level.copy(total = cumulative, percentage = cumulative / totalQty)
            }
        }
        
        bids = (0..14).map { i ->
            val price = basePrice - (i + 1) * 5.0
            val qty = Random.nextDouble(0.1, 5.0)
            OrderBookLevel(price, qty, 0.0, 0.0)
        }.let { list ->
            val totalQty = list.sumOf { it.quantity }
            var cumulative = 0.0
            list.map { level ->
                cumulative += level.quantity
                level.copy(total = cumulative, percentage = cumulative / totalQty)
            }
        }
        
        spread = asks.lastOrNull()?.price?.minus(bids.firstOrNull()?.price ?: 0.0) ?: 0.0
        
        recentTrades = (0..19).map {
            RecentTrade(
                price = basePrice + Random.nextDouble(-50.0, 50.0),
                quantity = Random.nextDouble(0.001, 1.0),
                isBuy = Random.nextBoolean(),
                timestamp = System.currentTimeMillis() - it * 5000
            )
        }
        
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(symbol, fontWeight = FontWeight.Bold)
                        Text(
                            text = strings.orderBook,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    // Precision selector
                    TextButton(onClick = { precision = (precision % 4) + 1 }) {
                        Text("${precision}dp")
                    }
                }
            )
        }
    ) { padding ->
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Row(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                // Order Book (70%)
                Column(
                    modifier = Modifier
                        .weight(0.7f)
                        .fillMaxHeight()
                ) {
                    // Mode selector
                    OrderBookModeSelector(
                        mode = mode,
                        onModeChange = { mode = it }
                    )
                    
                    // Header
                    OrderBookHeader()
                    
                    // Order book content
                    Box(modifier = Modifier.weight(1f)) {
                        when (mode) {
                            OrderBookMode.BOTH -> BothSidesView(
                                asks = asks,
                                bids = bids,
                                onPriceSelected = onPriceSelected,
                                precision = precision
                            )
                            OrderBookMode.ASKS -> AsksOnlyView(
                                asks = asks,
                                onPriceSelected = onPriceSelected,
                                precision = precision
                            )
                            OrderBookMode.BIDS -> BidsOnlyView(
                                bids = bids,
                                onPriceSelected = onPriceSelected,
                                precision = precision
                            )
                        }
                    }
                    
                    // Spread & Last Price
                    SpreadBar(
                        lastPrice = lastPrice,
                        markPrice = markPrice,
                        spread = spread,
                        precision = precision
                    )
                }
                
                // Recent Trades (30%)
                Column(
                    modifier = Modifier
                        .weight(0.3f)
                        .fillMaxHeight()
                        .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f))
                ) {
                    Text(
                        text = strings.recentTrades,
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(8.dp)
                    )
                    
                    LazyColumn {
                        itemsIndexed(recentTrades) { _, trade ->
                            RecentTradeRow(trade = trade, precision = precision)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun OrderBookModeSelector(
    mode: OrderBookMode,
    onModeChange: (OrderBookMode) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        OrderBookMode.entries.forEach { m ->
            FilterChip(
                selected = mode == m,
                onClick = { onModeChange(m) },
                label = {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        when (m) {
                            OrderBookMode.BOTH -> {
                                Box(
                                    modifier = Modifier
                                        .size(12.dp)
                                        .clip(RoundedCornerShape(2.dp))
                                ) {
                                    Row {
                                        Box(Modifier.weight(1f).fillMaxHeight().background(ShortRed))
                                        Box(Modifier.weight(1f).fillMaxHeight().background(LongGreen))
                                    }
                                }
                            }
                            OrderBookMode.BIDS -> {
                                Box(
                                    modifier = Modifier
                                        .size(12.dp)
                                        .clip(RoundedCornerShape(2.dp))
                                        .background(LongGreen)
                                )
                            }
                            OrderBookMode.ASKS -> {
                                Box(
                                    modifier = Modifier
                                        .size(12.dp)
                                        .clip(RoundedCornerShape(2.dp))
                                        .background(ShortRed)
                                )
                            }
                        }
                        Text(m.name)
                    }
                },
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun OrderBookHeader() {
    val strings = LocalStrings.current
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = strings.price,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.weight(1f)
        )
        Text(
            text = strings.qty,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.weight(1f),
            textAlign = TextAlign.End
        )
        Text(
            text = strings.total,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.weight(1f),
            textAlign = TextAlign.End
        )
    }
}

@Composable
private fun BothSidesView(
    asks: List<OrderBookLevel>,
    bids: List<OrderBookLevel>,
    onPriceSelected: (Double) -> Unit,
    precision: Int
) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Asks (top half, reversed so lowest ask is at bottom)
        LazyColumn(
            modifier = Modifier.weight(1f),
            reverseLayout = true
        ) {
            itemsIndexed(asks.take(10)) { _, level ->
                OrderBookRow(
                    level = level,
                    isAsk = true,
                    onPriceSelected = onPriceSelected,
                    precision = precision
                )
            }
        }
        
        // Bids (bottom half)
        LazyColumn(
            modifier = Modifier.weight(1f)
        ) {
            itemsIndexed(bids.take(10)) { _, level ->
                OrderBookRow(
                    level = level,
                    isAsk = false,
                    onPriceSelected = onPriceSelected,
                    precision = precision
                )
            }
        }
    }
}

@Composable
private fun AsksOnlyView(
    asks: List<OrderBookLevel>,
    onPriceSelected: (Double) -> Unit,
    precision: Int
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        reverseLayout = true
    ) {
        itemsIndexed(asks) { _, level ->
            OrderBookRow(
                level = level,
                isAsk = true,
                onPriceSelected = onPriceSelected,
                precision = precision
            )
        }
    }
}

@Composable
private fun BidsOnlyView(
    bids: List<OrderBookLevel>,
    onPriceSelected: (Double) -> Unit,
    precision: Int
) {
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        itemsIndexed(bids) { _, level ->
            OrderBookRow(
                level = level,
                isAsk = false,
                onPriceSelected = onPriceSelected,
                precision = precision
            )
        }
    }
}

@Composable
private fun OrderBookRow(
    level: OrderBookLevel,
    isAsk: Boolean,
    onPriceSelected: (Double) -> Unit,
    precision: Int
) {
    val backgroundColor = if (isAsk) ShortRed else LongGreen
    val textColor = if (isAsk) ShortRed else LongGreen
    
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(24.dp)
    ) {
        // Depth bar
        Box(
            modifier = Modifier
                .fillMaxHeight()
                .fillMaxWidth(level.percentage.toFloat().coerceIn(0f, 1f))
                .align(Alignment.CenterEnd)
                .background(backgroundColor.copy(alpha = 0.15f))
        )
        
        // Content
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = formatPrice(level.price, precision),
                style = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace,
                color = textColor,
                modifier = Modifier
                    .weight(1f)
                    .clickable { onPriceSelected(level.price) }
            )
            Text(
                text = formatQuantity(level.quantity),
                style = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.End
            )
            Text(
                text = formatQuantity(level.total),
                style = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.End
            )
        }
    }
}

@Composable
private fun SpreadBar(
    lastPrice: Double,
    markPrice: Double,
    spread: Double,
    precision: Int
) {
    val strings = LocalStrings.current
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = strings.lastPrice,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = formatPrice(lastPrice, precision),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            }
            
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = strings.spread,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = formatPrice(spread, precision),
                    style = MaterialTheme.typography.bodyMedium,
                    fontFamily = FontFamily.Monospace
                )
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = strings.markPrice,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = formatPrice(markPrice, precision),
                    style = MaterialTheme.typography.bodyMedium,
                    fontFamily = FontFamily.Monospace
                )
            }
        }
    }
}

@Composable
private fun RecentTradeRow(
    trade: RecentTrade,
    precision: Int
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 2.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = formatPrice(trade.price, precision),
            style = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace,
            fontSize = 11.sp,
            color = if (trade.isBuy) LongGreen else ShortRed
        )
        Text(
            text = formatQuantity(trade.quantity),
            style = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace,
            fontSize = 11.sp
        )
    }
}

private fun formatPrice(value: Double, precision: Int): String {
    return String.format("%.${precision}f", value)
}

private fun formatQuantity(value: Double): String {
    return when {
        value >= 1000 -> String.format("%.0f", value)
        value >= 1 -> String.format("%.2f", value)
        else -> String.format("%.4f", value)
    }
}

private fun Modifier.clickable(onClick: () -> Unit): Modifier = this.then(
    Modifier.clickable(onClick = onClick)
)
