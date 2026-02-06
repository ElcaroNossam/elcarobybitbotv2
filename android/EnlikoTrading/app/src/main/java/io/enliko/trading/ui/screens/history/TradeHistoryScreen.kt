package io.enliko.trading.ui.screens.history

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import io.enliko.trading.util.LocalStrings
import java.text.SimpleDateFormat
import java.util.*

// MARK: - Data Models
data class OrderRecord(
    val id: String,
    val symbol: String,
    val side: String,
    val type: String,
    val price: Double,
    val qty: Double,
    val filledQty: Double,
    val status: String,
    val createdAt: Long
)

data class TradeRecord(
    val id: String,
    val symbol: String,
    val side: String,
    val price: Double,
    val qty: Double,
    val fee: Double,
    val realizedPnl: Double?,
    val executedAt: Long
)

data class FundingRecord(
    val id: String,
    val symbol: String,
    val fundingRate: Double,
    val payment: Double,
    val positionSize: Double,
    val timestamp: Long
)

data class PnlRecord(
    val id: String,
    val symbol: String,
    val side: String,
    val entryPrice: Double,
    val exitPrice: Double,
    val qty: Double,
    val pnl: Double,
    val pnlPercent: Double,
    val closedAt: Long
)

enum class HistoryTab { ORDERS, TRADES, FUNDING, PNL }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TradeHistoryScreen(
    onNavigateBack: () -> Unit = {}
) {
    val strings = LocalStrings.current
    var selectedTab by remember { mutableStateOf(HistoryTab.TRADES) }
    var isLoading by remember { mutableStateOf(true) }
    
    var orders by remember { mutableStateOf<List<OrderRecord>>(emptyList()) }
    var trades by remember { mutableStateOf<List<TradeRecord>>(emptyList()) }
    var fundings by remember { mutableStateOf<List<FundingRecord>>(emptyList()) }
    var pnlRecords by remember { mutableStateOf<List<PnlRecord>>(emptyList()) }
    
    // Mock data
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(500)
        orders = listOf(
            OrderRecord("1", "BTCUSDT", "Buy", "Limit", 97500.0, 0.01, 0.01, "Filled", System.currentTimeMillis() - 3600000),
            OrderRecord("2", "ETHUSDT", "Sell", "Market", 3250.0, 0.5, 0.5, "Filled", System.currentTimeMillis() - 7200000),
            OrderRecord("3", "SOLUSDT", "Buy", "Limit", 170.0, 10.0, 0.0, "Cancelled", System.currentTimeMillis() - 10800000)
        )
        trades = listOf(
            TradeRecord("1", "BTCUSDT", "Buy", 97500.0, 0.01, 0.98, null, System.currentTimeMillis() - 3600000),
            TradeRecord("2", "ETHUSDT", "Sell", 3250.0, 0.5, 1.63, 125.50, System.currentTimeMillis() - 7200000),
            TradeRecord("3", "BTCUSDT", "Sell", 98000.0, 0.01, 0.98, 5.0, System.currentTimeMillis() - 10800000)
        )
        fundings = listOf(
            FundingRecord("1", "BTCUSDT", 0.0001, -0.98, 1.0, System.currentTimeMillis() - 28800000),
            FundingRecord("2", "ETHUSDT", 0.00015, -1.25, 0.5, System.currentTimeMillis() - 57600000),
            FundingRecord("3", "BTCUSDT", -0.0001, 0.49, 0.5, System.currentTimeMillis() - 86400000)
        )
        pnlRecords = listOf(
            PnlRecord("1", "BTCUSDT", "Long", 95000.0, 97000.0, 0.1, 200.0, 2.1, System.currentTimeMillis() - 86400000),
            PnlRecord("2", "ETHUSDT", "Short", 3300.0, 3200.0, 1.0, 100.0, 3.03, System.currentTimeMillis() - 172800000),
            PnlRecord("3", "SOLUSDT", "Long", 175.0, 170.0, 20.0, -100.0, -2.86, System.currentTimeMillis() - 259200000)
        )
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Trade History") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { /* Export */ }) {
                        Icon(Icons.Default.Download, contentDescription = "Export")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Tab Selector
            ScrollableTabRow(
                selectedTabIndex = selectedTab.ordinal,
                modifier = Modifier.fillMaxWidth(),
                edgePadding = 16.dp
            ) {
                HistoryTab.entries.forEach { tab ->
                    Tab(
                        selected = selectedTab == tab,
                        onClick = { selectedTab = tab },
                        text = {
                            Text(
                                text = tab.name,
                                fontWeight = if (selectedTab == tab) FontWeight.Bold else FontWeight.Normal
                            )
                        }
                    )
                }
            }
            
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else {
                AnimatedContent(
                    targetState = selectedTab,
                    transitionSpec = {
                        fadeIn() togetherWith fadeOut()
                    },
                    label = "history_tab"
                ) { tab ->
                    when (tab) {
                        HistoryTab.ORDERS -> OrdersTab(orders)
                        HistoryTab.TRADES -> TradesTab(trades)
                        HistoryTab.FUNDING -> FundingTab(fundings)
                        HistoryTab.PNL -> PnLTab(pnlRecords)
                    }
                }
            }
        }
    }
}

@Composable
private fun OrdersTab(orders: List<OrderRecord>) {
    if (orders.isEmpty()) {
        EmptyHistoryView("No orders found")
    } else {
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(orders, key = { it.id }) { order ->
                OrderCard(order)
            }
        }
    }
}

@Composable
private fun OrderCard(order: OrderRecord) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = order.symbol,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    SideChip(side = order.side)
                }
                StatusChip(status = order.status)
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                InfoColumn("Type", order.type)
                InfoColumn("Price", formatPrice(order.price))
                InfoColumn("Qty", "${order.filledQty}/${order.qty}")
                InfoColumn("Time", formatTime(order.createdAt))
            }
        }
    }
}

@Composable
private fun TradesTab(trades: List<TradeRecord>) {
    if (trades.isEmpty()) {
        EmptyHistoryView("No trades found")
    } else {
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(trades, key = { it.id }) { trade ->
                TradeCard(trade)
            }
        }
    }
}

@Composable
private fun TradeCard(trade: TradeRecord) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = trade.symbol,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    SideChip(side = trade.side)
                }
                
                trade.realizedPnl?.let { pnl ->
                    Text(
                        text = "${if (pnl >= 0) "+" else ""}${formatCurrency(pnl)}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (pnl >= 0) LongGreen else ShortRed
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                InfoColumn("Price", formatPrice(trade.price))
                InfoColumn("Qty", trade.qty.toString())
                InfoColumn("Fee", formatCurrency(trade.fee))
                InfoColumn("Time", formatTime(trade.executedAt))
            }
        }
    }
}

@Composable
private fun FundingTab(fundings: List<FundingRecord>) {
    if (fundings.isEmpty()) {
        EmptyHistoryView("No funding history")
    } else {
        // Summary header
        val totalFunding = fundings.sumOf { it.payment }
        
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Total Funding",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "${if (totalFunding >= 0) "+" else ""}${formatCurrency(totalFunding)}",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = if (totalFunding >= 0) LongGreen else ShortRed
                        )
                    }
                }
            }
            
            items(fundings, key = { it.id }) { funding ->
                FundingCard(funding)
            }
        }
    }
}

@Composable
private fun FundingCard(funding: FundingRecord) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = funding.symbol,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Rate: ${String.format("%.4f", funding.fundingRate * 100)}%",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = formatTime(funding.timestamp),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Text(
                text = "${if (funding.payment >= 0) "+" else ""}${formatCurrency(funding.payment)}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = if (funding.payment >= 0) LongGreen else ShortRed
            )
        }
    }
}

@Composable
private fun PnLTab(records: List<PnlRecord>) {
    if (records.isEmpty()) {
        EmptyHistoryView("No closed positions")
    } else {
        val totalPnl = records.sumOf { it.pnl }
        val winCount = records.count { it.pnl > 0 }
        val winRate = if (records.isNotEmpty()) winCount.toDouble() / records.size * 100 else 0.0
        
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Summary Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceAround
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Total PnL", style = MaterialTheme.typography.bodySmall)
                            Text(
                                text = "${if (totalPnl >= 0) "+" else ""}${formatCurrency(totalPnl)}",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                color = if (totalPnl >= 0) LongGreen else ShortRed
                            )
                        }
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Win Rate", style = MaterialTheme.typography.bodySmall)
                            Text(
                                text = "${String.format("%.1f", winRate)}%",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Trades", style = MaterialTheme.typography.bodySmall)
                            Text(
                                text = "${records.size}",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }
            
            items(records, key = { it.id }) { record ->
                PnLCard(record)
            }
        }
    }
}

@Composable
private fun PnLCard(record: PnlRecord) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = record.symbol,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    SideChip(side = record.side)
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "${if (record.pnl >= 0) "+" else ""}${formatCurrency(record.pnl)}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (record.pnl >= 0) LongGreen else ShortRed
                    )
                    Text(
                        text = "${if (record.pnlPercent >= 0) "+" else ""}${String.format("%.2f", record.pnlPercent)}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = if (record.pnlPercent >= 0) LongGreen else ShortRed
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                InfoColumn("Entry", formatPrice(record.entryPrice))
                InfoColumn("Exit", formatPrice(record.exitPrice))
                InfoColumn("Qty", record.qty.toString())
                InfoColumn("Closed", formatDate(record.closedAt))
            }
        }
    }
}

@Composable
private fun SideChip(side: String) {
    val isLong = side.equals("Buy", ignoreCase = true) || side.equals("Long", ignoreCase = true)
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(4.dp))
            .background(if (isLong) LongGreen.copy(alpha = 0.2f) else ShortRed.copy(alpha = 0.2f))
            .padding(horizontal = 8.dp, vertical = 2.dp)
    ) {
        Text(
            text = if (isLong) "LONG" else "SHORT",
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color = if (isLong) LongGreen else ShortRed
        )
    }
}

@Composable
private fun StatusChip(status: String) {
    val color = when (status.lowercase()) {
        "filled" -> LongGreen
        "cancelled", "canceled" -> ShortRed
        "partial" -> MaterialTheme.colorScheme.tertiary
        else -> MaterialTheme.colorScheme.onSurfaceVariant
    }
    
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(4.dp))
            .background(color.copy(alpha = 0.2f))
            .padding(horizontal = 8.dp, vertical = 2.dp)
    ) {
        Text(
            text = status.uppercase(),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color = color
        )
    }
}

@Composable
private fun InfoColumn(label: String, value: String) {
    Column {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun EmptyHistoryView(message: String) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.History,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

private fun formatPrice(value: Double): String {
    return if (value >= 1) String.format("$%.2f", value) else String.format("$%.6f", value)
}

private fun formatCurrency(value: Double): String {
    return String.format("$%.2f", value)
}

private fun formatTime(timestamp: Long): String {
    return SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date(timestamp))
}

private fun formatDate(timestamp: Long): String {
    return SimpleDateFormat("MMM d", Locale.getDefault()).format(Date(timestamp))
}
