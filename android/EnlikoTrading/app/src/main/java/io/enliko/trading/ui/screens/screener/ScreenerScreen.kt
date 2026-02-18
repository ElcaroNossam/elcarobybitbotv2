package io.enliko.trading.ui.screens.screener

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Sort
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
import io.enliko.trading.data.models.ScreenerCoin
import java.text.NumberFormat
import java.util.Locale
import io.enliko.trading.util.LocalStrings

/**
 * ScreenerScreen - Matching iOS ScreenerView.swift
 * Crypto screener with filters and sorting
 */

enum class ScreenerSortBy {
    VOLUME,
    PRICE,
    CHANGE_24H,
    OI_CHANGE
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScreenerScreen(
    onBack: () -> Unit = {},
    showBackButton: Boolean = false,
    onCoinClick: (String) -> Unit = {}
) {
    var isRefreshing by remember { mutableStateOf(false) }
    var searchQuery by remember { mutableStateOf("") }
    var sortBy by remember { mutableStateOf(ScreenerSortBy.VOLUME) }
    var sortAscending by remember { mutableStateOf(false) }
    var showDerivatives by remember { mutableStateOf(false) }
    var selectedFilter by remember { mutableStateOf("all") } // all, gainers, losers
    
    // Sample data (fallback when API is unavailable)
    val coins = remember {
        listOf(
            ScreenerCoin("BTCUSDT", 97150.0, 1.25, 45_000_000_000.0, 2.5),
            ScreenerCoin("ETHUSDT", 3475.0, 2.15, 22_000_000_000.0, 3.2),
            ScreenerCoin("SOLUSDT", 193.50, -0.85, 8_500_000_000.0, -1.5),
            ScreenerCoin("BNBUSDT", 685.0, 0.75, 3_200_000_000.0, 0.8),
            ScreenerCoin("XRPUSDT", 2.35, 5.25, 12_000_000_000.0, 8.5),
            ScreenerCoin("ADAUSDT", 1.05, -2.15, 2_100_000_000.0, -3.2),
            ScreenerCoin("DOGEUSDT", 0.385, 3.85, 5_800_000_000.0, 5.5),
            ScreenerCoin("AVAXUSDT", 42.50, 1.95, 1_800_000_000.0, 4.2),
            ScreenerCoin("DOTUSDT", 7.85, -1.25, 950_000_000.0, -2.1),
            ScreenerCoin("LINKUSDT", 23.75, 2.85, 1_200_000_000.0, 3.8)
        )
    }
    
    val filteredCoins = coins
        .filter { coin ->
            val matchesSearch = searchQuery.isEmpty() || 
                coin.symbol.contains(searchQuery, ignoreCase = true)
            val matchesFilter = when (selectedFilter) {
                "gainers" -> coin.change24h > 0
                "losers" -> coin.change24h < 0
                else -> true
            }
            matchesSearch && matchesFilter
        }
        .sortedWith(
            compareBy<ScreenerCoin> { coin ->
                when (sortBy) {
                    ScreenerSortBy.VOLUME -> coin.volume24h
                    ScreenerSortBy.PRICE -> coin.price
                    ScreenerSortBy.CHANGE_24H -> coin.change24h
                    ScreenerSortBy.OI_CHANGE -> coin.oiChange ?: 0.0
                }
            }.let { if (sortAscending) it else it.reversed() }
        )
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Crypto Screener") },
                navigationIcon = {
                    if (showBackButton) {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = EnlikoBackground
                )
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
                // Search Bar
                item {
                    OutlinedTextField(
                        value = searchQuery,
                        onValueChange = { searchQuery = it },
                        placeholder = { Text("Search coins...") },
                        leadingIcon = {
                            Icon(Icons.Default.Search, contentDescription = null)
                        },
                        trailingIcon = {
                            if (searchQuery.isNotEmpty()) {
                                IconButton(onClick = { searchQuery = "" }) {
                                    Icon(Icons.Default.Clear, contentDescription = "Clear")
                                }
                            }
                        },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = EnlikoPrimary,
                            unfocusedBorderColor = EnlikoBorder,
                            focusedContainerColor = EnlikoSurface,
                            unfocusedContainerColor = EnlikoSurface
                        )
                    )
                }
                
                // Filters Row
                item {
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        item {
                            FilterChip(
                                selected = selectedFilter == "all",
                                onClick = { selectedFilter = "all" },
                                label = { Text("All") },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = EnlikoPrimary,
                                    selectedLabelColor = Color.White
                                )
                            )
                        }
                        item {
                            FilterChip(
                                selected = selectedFilter == "gainers",
                                onClick = { selectedFilter = "gainers" },
                                label = { Text("📈 Gainers") },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = EnlikoGreen,
                                    selectedLabelColor = Color.White
                                )
                            )
                        }
                        item {
                            FilterChip(
                                selected = selectedFilter == "losers",
                                onClick = { selectedFilter = "losers" },
                                label = { Text("📉 Losers") },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = EnlikoRed,
                                    selectedLabelColor = Color.White
                                )
                            )
                        }
                        item {
                            FilterChip(
                                selected = showDerivatives,
                                onClick = { showDerivatives = !showDerivatives },
                                label = { Text("🔮 Derivatives") }
                            )
                        }
                    }
                }
                
                // Sort Options
                item {
                    SortOptionsRow(
                        sortBy = sortBy,
                        sortAscending = sortAscending,
                        onSortChange = { sortBy = it },
                        onToggleOrder = { sortAscending = !sortAscending },
                        showDerivatives = showDerivatives
                    )
                }
                
                // Column Headers
                item {
                    ScreenerHeader(showDerivatives = showDerivatives)
                }
                
                // Coins List
                items(filteredCoins, key = { it.symbol }) { coin ->
                    ScreenerCoinRow(
                        coin = coin,
                        showDerivatives = showDerivatives,
                        onClick = { onCoinClick(coin.symbol) }
                    )
                }
                
                // Results count
                item {
                    Text(
                        text = "${filteredCoins.size} coins found",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary,
                        textAlign = TextAlign.Center,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 8.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun SortOptionsRow(
    sortBy: ScreenerSortBy,
    sortAscending: Boolean,
    onSortChange: (ScreenerSortBy) -> Unit,
    onToggleOrder: () -> Unit,
    showDerivatives: Boolean
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            modifier = Modifier.weight(1f)
        ) {
            item {
                SortChip("Volume", sortBy == ScreenerSortBy.VOLUME) {
                    onSortChange(ScreenerSortBy.VOLUME)
                }
            }
            item {
                SortChip("Price", sortBy == ScreenerSortBy.PRICE) {
                    onSortChange(ScreenerSortBy.PRICE)
                }
            }
            item {
                SortChip("24h%", sortBy == ScreenerSortBy.CHANGE_24H) {
                    onSortChange(ScreenerSortBy.CHANGE_24H)
                }
            }
            if (showDerivatives) {
                item {
                    SortChip("OI Δ", sortBy == ScreenerSortBy.OI_CHANGE) {
                        onSortChange(ScreenerSortBy.OI_CHANGE)
                    }
                }
            }
        }
        
        IconButton(onClick = onToggleOrder) {
            Icon(
                Icons.AutoMirrored.Filled.Sort,
                contentDescription = "Toggle sort order",
                tint = EnlikoPrimary
            )
        }
    }
}

@Composable
private fun SortChip(
    label: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        color = if (isSelected) EnlikoPrimary else EnlikoSurface,
        shape = RoundedCornerShape(8.dp)
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
            color = if (isSelected) Color.White else EnlikoTextSecondary,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
        )
    }
}

@Composable
private fun ScreenerHeader(showDerivatives: Boolean) {
    val strings = LocalStrings.current
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = strings.coin,
            style = MaterialTheme.typography.labelSmall,
            color = EnlikoTextSecondary,
            modifier = Modifier.weight(2f)
        )
        Text(
            text = strings.price,
            style = MaterialTheme.typography.labelSmall,
            color = EnlikoTextSecondary,
            textAlign = TextAlign.End,
            modifier = Modifier.weight(1.5f)
        )
        Text(
            text = "24h %",
            style = MaterialTheme.typography.labelSmall,
            color = EnlikoTextSecondary,
            textAlign = TextAlign.End,
            modifier = Modifier.weight(1f)
        )
        if (showDerivatives) {
            Text(
                text = "OI Δ",
                style = MaterialTheme.typography.labelSmall,
                color = EnlikoTextSecondary,
                textAlign = TextAlign.End,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun ScreenerCoinRow(
    coin: ScreenerCoin,
    showDerivatives: Boolean,
    onClick: () -> Unit
) {
    val changeColor = if (coin.change24h >= 0) EnlikoGreen else EnlikoRed
    
    Surface(
        onClick = onClick,
        color = EnlikoCard,
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Coin Info
            Column(modifier = Modifier.weight(2f)) {
                Text(
                    text = coin.symbol.replace("USDT", ""),
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.SemiBold,
                    color = EnlikoTextPrimary
                )
                Text(
                    text = coin.symbol,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextSecondary
                )
            }
            
            // Price
            Text(
                text = formatPrice(coin.price),
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = EnlikoTextPrimary,
                textAlign = TextAlign.End,
                modifier = Modifier.weight(1.5f)
            )
            
            // 24h Change
            Surface(
                color = changeColor.copy(alpha = 0.15f),
                shape = RoundedCornerShape(6.dp),
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = "${if (coin.change24h >= 0) "+" else ""}${String.format("%.2f", coin.change24h)}%",
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.SemiBold,
                    color = changeColor,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
            
            // OI Change (if derivatives)
            if (showDerivatives && coin.oiChange != null) {
                val oiColor = if (coin.oiChange >= 0) EnlikoGreen else EnlikoRed
                Text(
                    text = "${if (coin.oiChange >= 0) "+" else ""}${String.format("%.1f", coin.oiChange)}%",
                    style = MaterialTheme.typography.bodySmall,
                    color = oiColor,
                    textAlign = TextAlign.End,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

private fun formatPrice(value: Double): String {
    return when {
        value >= 1000 -> String.format("$%.2f", value)
        value >= 1 -> String.format("$%.3f", value)
        value >= 0.01 -> String.format("$%.4f", value)
        else -> String.format("$%.6f", value)
    }
}

private fun formatVolume(value: Double): String {
    return when {
        value >= 1_000_000_000 -> String.format("$%.1fB", value / 1_000_000_000)
        value >= 1_000_000 -> String.format("$%.1fM", value / 1_000_000)
        value >= 1_000 -> String.format("$%.1fK", value / 1_000)
        else -> String.format("$%.0f", value)
    }
}
