package io.enliko.trading.ui.screens.history

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.pulltorefresh.PullToRefreshContainer
import androidx.compose.material3.pulltorefresh.rememberPullToRefreshState
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

/**
 * TradeHistoryScreen - Matching iOS TradeHistoryView.swift
 * Full trade history list with filters and search
 */

data class Trade(
    val id: String,
    val symbol: String,
    val side: String,
    val entryPrice: Double,
    val exitPrice: Double?,
    val pnl: Double?,
    val pnlPct: Double?,
    val strategy: String?,
    val size: Double?,
    val leverage: Int?,
    val closedAt: Long?
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TradeHistoryScreen(
    onBack: () -> Unit
) {
    var searchText by remember { mutableStateOf("") }
    var selectedStrategy by remember { mutableStateOf<String?>(null) }
    var showFilters by remember { mutableStateOf(false) }
    var trades by remember { mutableStateOf(listOf<Trade>()) }
    var isLoading by remember { mutableStateOf(false) }
    
    val pullToRefreshState = rememberPullToRefreshState()
    
    val strategies = trades.mapNotNull { it.strategy }.distinct().sorted()
    
    val filteredTrades = trades.filter { trade ->
        val matchesSearch = searchText.isEmpty() || 
            trade.symbol.contains(searchText, ignoreCase = true)
        val matchesStrategy = selectedStrategy == null || 
            trade.strategy == selectedStrategy
        matchesSearch && matchesStrategy
    }
    
    // Handle pull to refresh
    LaunchedEffect(pullToRefreshState.isRefreshing) {
        if (pullToRefreshState.isRefreshing) {
            // TODO: Refresh trades from API
            kotlinx.coroutines.delay(1000)
            pullToRefreshState.endRefresh()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Trade History") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showFilters = !showFilters }) {
                        Icon(
                            Icons.Default.FilterList,
                            contentDescription = "Filters",
                            tint = if (showFilters) EnlikoPrimary else EnlikoTextSecondary
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = EnlikoBackground
                )
            )
        },
        containerColor = EnlikoBackground
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .nestedScroll(pullToRefreshState.nestedScrollConnection)
        ) {
            Column(modifier = Modifier.fillMaxSize()) {
                // Search Bar
                SearchBar(
                    query = searchText,
                    onQueryChange = { searchText = it },
                    onSearch = { },
                    active = false,
                    onActiveChange = { },
                    placeholder = { Text("Search symbol...") },
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                    trailingIcon = {
                        if (searchText.isNotEmpty()) {
                            IconButton(onClick = { searchText = "" }) {
                                Icon(Icons.Default.Clear, contentDescription = "Clear")
                            }
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    colors = SearchBarDefaults.colors(
                        containerColor = EnlikoCard
                    )
                ) { }
                
                // Filters Section
                AnimatedVisibility(
                    visible = showFilters,
                    enter = expandVertically(),
                    exit = shrinkVertically()
                ) {
                    FiltersSection(
                        strategies = strategies,
                        selectedStrategy = selectedStrategy,
                        onStrategySelected = { selectedStrategy = it }
                    )
                }
                
                // Content
                if (filteredTrades.isEmpty()) {
                    EmptyTradesState()
                } else {
                    TradesList(
                        trades = filteredTrades,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            PullToRefreshContainer(
                state = pullToRefreshState,
                modifier = Modifier.align(Alignment.TopCenter),
                containerColor = EnlikoCard,
                contentColor = EnlikoPrimary
            )
        }
    }
}

@Composable
private fun FiltersSection(
    strategies: List<String>,
    selectedStrategy: String?,
    onStrategySelected: (String?) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(EnlikoSurface)
            .horizontalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        FilterChip(
            title = "All",
            isSelected = selectedStrategy == null,
            onClick = { onStrategySelected(null) }
        )
        
        strategies.forEach { strategy ->
            FilterChip(
                title = strategy.replaceFirstChar { it.uppercase() },
                isSelected = selectedStrategy == strategy,
                onClick = { onStrategySelected(strategy) }
            )
        }
    }
}

@Composable
private fun FilterChip(
    title: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(16.dp),
        color = if (isSelected) EnlikoPrimary else EnlikoCard
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Medium,
            color = if (isSelected) Color.White else EnlikoTextSecondary,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
        )
    }
}

@Composable
private fun EmptyTradesState() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Search,
                contentDescription = null,
                tint = EnlikoTextMuted,
                modifier = Modifier.size(60.dp)
            )
            
            Text(
                text = "No trades found",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium,
                color = EnlikoTextPrimary
            )
            
            Text(
                text = "Your trading history will appear here",
                style = MaterialTheme.typography.bodyMedium,
                color = EnlikoTextSecondary
            )
        }
    }
}

@Composable
private fun TradesList(
    trades: List<Trade>,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier,
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(trades, key = { it.id }) { trade ->
            TradeDetailCard(trade = trade)
        }
    }
}

@Composable
private fun TradeDetailCard(trade: Trade) {
    var isExpanded by remember { mutableStateOf(false) }
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { isExpanded = !isExpanded },
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Main Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Side & Symbol
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Side Badge
                    val isLong = trade.side.lowercase() == "buy"
                    Surface(
                        color = if (isLong) EnlikoGreen else EnlikoRed,
                        shape = RoundedCornerShape(4.dp)
                    ) {
                        Text(
                            text = trade.side.uppercase(),
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                    
                    Text(
                        text = trade.symbol,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = EnlikoTextPrimary
                    )
                }
                
                // PnL
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = trade.pnl?.let { formatCurrency(it) } ?: "--",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = if ((trade.pnl ?: 0.0) >= 0) EnlikoGreen else EnlikoRed
                    )
                    
                    trade.pnlPct?.let { pct ->
                        Text(
                            text = "${if (pct >= 0) "+" else ""}${String.format("%.2f", pct)}%",
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                }
            }
            
            // Expanded Details
            AnimatedVisibility(
                visible = isExpanded,
                enter = expandVertically(),
                exit = shrinkVertically()
            ) {
                Column(modifier = Modifier.padding(top = 12.dp)) {
                    HorizontalDivider(color = EnlikoBorder)
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        DetailItem(label = "Entry", value = "$${formatPrice(trade.entryPrice)}")
                        trade.exitPrice?.let { 
                            DetailItem(label = "Exit", value = "$${formatPrice(it)}") 
                        }
                        trade.strategy?.let { 
                            DetailItem(label = "Strategy", value = it.replaceFirstChar { c -> c.uppercase() }) 
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        trade.size?.let { 
                            DetailItem(label = "Size", value = formatNumber(it)) 
                        }
                        trade.leverage?.let { 
                            DetailItem(label = "Leverage", value = "${it}x") 
                        }
                        trade.closedAt?.let { 
                            DetailItem(label = "Closed", value = formatDate(it)) 
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun DetailItem(
    label: String,
    value: String
) {
    Column {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = EnlikoTextMuted
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = EnlikoTextPrimary
        )
    }
}

private fun formatCurrency(value: Double): String {
    val sign = if (value >= 0) "+" else ""
    return "$sign$${String.format("%.2f", value)}"
}

private fun formatPrice(value: Double): String {
    return if (value < 1) String.format("%.6f", value)
           else if (value < 100) String.format("%.4f", value)
           else String.format("%.2f", value)
}

private fun formatNumber(value: Double): String {
    return if (value < 0.001) String.format("%.6f", value)
           else if (value < 1) String.format("%.4f", value)
           else String.format("%.2f", value)
}

private fun formatDate(timestamp: Long): String {
    val sdf = SimpleDateFormat("MMM dd, HH:mm", Locale.US)
    return sdf.format(Date(timestamp))
}
