package io.enliko.trading.ui.screens.portfolio

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*
import java.text.NumberFormat
import java.util.Locale

/**
 * PositionsScreen - Matching iOS PositionsView.swift
 * Display open positions with detailed information
 */

// Local model for this screen (different from API Position)
data class PositionDisplay(
    val id: String,
    val symbol: String,
    val side: String, // "long" or "short"
    val entryPrice: Double,
    val markPrice: Double,
    val size: Double,
    val leverage: Int,
    val unrealizedPnl: Double,
    val unrealizedPnlPercent: Double,
    val margin: Double,
    val liquidationPrice: Double?,
    val strategy: String?,
    val tpPrice: Double?,
    val slPrice: Double?,
    val exchange: String // "bybit" or "hyperliquid"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PositionsScreen(
    onBack: () -> Unit = {},
    showBackButton: Boolean = true
) {
    var isRefreshing by remember { mutableStateOf(false) }
    var selectedFilter by remember { mutableStateOf("all") } // all, long, short
    var selectedExchange by remember { mutableStateOf("all") } // all, bybit, hyperliquid
    
    // Sample positions data
    val positions = remember {
        listOf(
            PositionDisplay(
                id = "1",
                symbol = "BTCUSDT",
                side = "long",
                entryPrice = 96500.0,
                markPrice = 97250.0,
                size = 0.1,
                leverage = 10,
                unrealizedPnl = 75.0,
                unrealizedPnlPercent = 0.78,
                margin = 965.0,
                liquidationPrice = 87000.0,
                strategy = "OI Strategy",
                tpPrice = 100000.0,
                slPrice = 94000.0,
                exchange = "bybit"
            ),
            PositionDisplay(
                id = "2",
                symbol = "ETHUSDT",
                side = "long",
                entryPrice = 3450.0,
                markPrice = 3480.0,
                size = 1.5,
                leverage = 15,
                unrealizedPnl = 45.0,
                unrealizedPnlPercent = 0.87,
                margin = 345.0,
                liquidationPrice = 3100.0,
                strategy = "Scryptomera",
                tpPrice = 3600.0,
                slPrice = 3350.0,
                exchange = "bybit"
            ),
            PositionDisplay(
                id = "3",
                symbol = "SOLUSDT",
                side = "short",
                entryPrice = 195.0,
                markPrice = 193.50,
                size = 20.0,
                leverage = 5,
                unrealizedPnl = 30.0,
                unrealizedPnlPercent = 0.77,
                margin = 780.0,
                liquidationPrice = 215.0,
                strategy = "Manual",
                tpPrice = 180.0,
                slPrice = 205.0,
                exchange = "hyperliquid"
            )
        )
    }
    
    val filteredPositions = positions.filter { position ->
        val matchesFilter = when (selectedFilter) {
            "long" -> position.side == "long"
            "short" -> position.side == "short"
            else -> true
        }
        val matchesExchange = when (selectedExchange) {
            "bybit" -> position.exchange == "bybit"
            "hyperliquid" -> position.exchange == "hyperliquid"
            else -> true
        }
        matchesFilter && matchesExchange
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Positions") },
                navigationIcon = {
                    if (showBackButton) {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = EnlikoBackground
                ),
                actions = {
                    // Close All button
                    if (positions.isNotEmpty()) {
                        TextButton(onClick = { /* Close all positions */ }) {
                            Text("Close All", color = EnlikoRed)
                        }
                    }
                }
            )
        },
        containerColor = EnlikoBackground
    ) { padding ->
        PullToRefreshBox(
            isRefreshing = isRefreshing,
            onRefresh = {
                isRefreshing = true
                // Simulate refresh
                isRefreshing = false
            },
            modifier = Modifier.fillMaxSize()
        ) {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Summary Card
                item {
                    PositionsSummaryCard(positions = positions)
                }
                
                // Filters
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        FilterChip(
                            selected = selectedFilter == "all",
                            onClick = { selectedFilter = "all" },
                            label = { Text("All") },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = EnlikoPrimary,
                                selectedLabelColor = Color.White
                            )
                        )
                        FilterChip(
                            selected = selectedFilter == "long",
                            onClick = { selectedFilter = "long" },
                            label = { Text("Long") },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = EnlikoGreen,
                                selectedLabelColor = Color.White
                            )
                        )
                        FilterChip(
                            selected = selectedFilter == "short",
                            onClick = { selectedFilter = "short" },
                            label = { Text("Short") },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = EnlikoRed,
                                selectedLabelColor = Color.White
                            )
                        )
                    }
                }
                
                // Exchange Filter
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        FilterChip(
                            selected = selectedExchange == "all",
                            onClick = { selectedExchange = "all" },
                            label = { Text("All Exchanges") }
                        )
                        FilterChip(
                            selected = selectedExchange == "bybit",
                            onClick = { selectedExchange = "bybit" },
                            label = { Text("🟠 Bybit") }
                        )
                        FilterChip(
                            selected = selectedExchange == "hyperliquid",
                            onClick = { selectedExchange = "hyperliquid" },
                            label = { Text("🔷 HL") }
                        )
                    }
                }
                
                if (filteredPositions.isEmpty()) {
                    item {
                        EmptyPositionsState()
                    }
                } else {
                    items(filteredPositions, key = { it.id }) { position ->
                        PositionCard(
                            position = position,
                            onClose = { /* Close position */ },
                            onModifyTpSl = { /* Modify TP/SL */ }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun PositionsSummaryCard(positions: List<PositionDisplay>) {
    val totalUnrealizedPnl = positions.sumOf { it.unrealizedPnl }
    val totalMargin = positions.sumOf { it.margin }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            SummaryItem(
                label = "Positions",
                value = "${positions.size}",
                color = EnlikoTextPrimary
            )
            SummaryItem(
                label = "Unrealized PnL",
                value = formatCurrency(totalUnrealizedPnl),
                color = if (totalUnrealizedPnl >= 0) EnlikoGreen else EnlikoRed
            )
            SummaryItem(
                label = "Margin Used",
                value = formatCurrency(totalMargin),
                color = EnlikoTextPrimary
            )
        }
    }
}

@Composable
private fun SummaryItem(
    label: String,
    value: String,
    color: Color
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = EnlikoTextSecondary
        )
    }
}

@Composable
private fun PositionCard(
    position: PositionDisplay,
    onClose: () -> Unit,
    onModifyTpSl: () -> Unit
) {
    val isLong = position.side == "long"
    val sideColor = if (isLong) EnlikoGreen else EnlikoRed
    val pnlColor = if (position.unrealizedPnl >= 0) EnlikoGreen else EnlikoRed
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Side badge
                    Surface(
                        color = sideColor.copy(alpha = 0.15f),
                        shape = RoundedCornerShape(4.dp)
                    ) {
                        Text(
                            text = if (isLong) "LONG" else "SHORT",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = sideColor,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                    
                    Text(
                        text = position.symbol,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = EnlikoTextPrimary
                    )
                    
                    Text(
                        text = "${position.leverage}x",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                }
                
                // PnL
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = formatCurrency(position.unrealizedPnl),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = pnlColor
                    )
                    Text(
                        text = "${if (position.unrealizedPnlPercent >= 0) "+" else ""}${String.format("%.2f", position.unrealizedPnlPercent)}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = pnlColor
                    )
                }
            }
            
            // Price Info
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                PriceInfoColumn("Entry", formatPrice(position.entryPrice))
                PriceInfoColumn("Mark", formatPrice(position.markPrice))
                PriceInfoColumn("Size", position.size.toString())
            }
            
            // TP/SL
            if (position.tpPrice != null || position.slPrice != null) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    if (position.tpPrice != null) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "TP: ",
                                style = MaterialTheme.typography.bodySmall,
                                color = EnlikoTextSecondary
                            )
                            Text(
                                text = formatPrice(position.tpPrice),
                                style = MaterialTheme.typography.bodySmall,
                                fontWeight = FontWeight.Medium,
                                color = EnlikoGreen
                            )
                        }
                    }
                    if (position.slPrice != null) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "SL: ",
                                style = MaterialTheme.typography.bodySmall,
                                color = EnlikoTextSecondary
                            )
                            Text(
                                text = formatPrice(position.slPrice),
                                style = MaterialTheme.typography.bodySmall,
                                fontWeight = FontWeight.Medium,
                                color = EnlikoRed
                            )
                        }
                    }
                }
            }
            
            // Strategy & Exchange
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                position.strategy?.let {
                    Text(
                        text = "📊 $it",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                }
                Text(
                    text = if (position.exchange == "bybit") "🟠 Bybit" else "🔷 HyperLiquid",
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextSecondary
                )
            }
            
            // Action Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = onModifyTpSl,
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("Modify TP/SL")
                }
                
                Button(
                    onClick = onClose,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = EnlikoRed),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("Close")
                }
            }
        }
    }
}

@Composable
private fun PriceInfoColumn(label: String, value: String) {
    Column {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = EnlikoTextSecondary
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = EnlikoTextPrimary
        )
    }
}

@Composable
private fun EmptyPositionsState() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Icon(
                Icons.Default.Inbox,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = EnlikoTextSecondary
            )
            Text(
                text = "No Open Positions",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = EnlikoTextPrimary
            )
            Text(
                text = "Your open positions will appear here",
                style = MaterialTheme.typography.bodyMedium,
                color = EnlikoTextSecondary,
                textAlign = TextAlign.Center
            )
        }
    }
}

private fun formatCurrency(value: Double): String {
    val format = NumberFormat.getCurrencyInstance(Locale.US)
    return if (value >= 0) format.format(value) else format.format(value)
}

private fun formatPrice(value: Double): String {
    return if (value >= 1000) {
        String.format("%.2f", value)
    } else if (value >= 1) {
        String.format("%.4f", value)
    } else {
        String.format("%.6f", value)
    }
}
