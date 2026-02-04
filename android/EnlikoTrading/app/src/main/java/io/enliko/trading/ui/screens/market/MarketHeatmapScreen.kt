package io.enliko.trading.ui.screens.market

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.*
import kotlin.math.abs

/**
 * MarketHeatmapScreen - Matching iOS MarketHeatmapView.swift
 * Visual crypto market overview with treemap-style heatmap
 */

data class HeatmapCoin(
    val symbol: String,
    val name: String,
    val price: Double,
    val change24h: Double,
    val marketCap: Double,
    val volume24h: Double
) {
    val shortSymbol: String
        get() = symbol.replace("USDT", "")
    
    val changeColor: Color
        get() = when {
            change24h > 5 -> Color(0xFF00C853)
            change24h > 2 -> Color(0xFF66BB6A)
            change24h > 0 -> Color(0xFF4D804D)
            change24h > -2 -> Color(0xFF804D4D)
            change24h > -5 -> Color(0xFFCC4D4D)
            else -> Color(0xFFE53935)
        }
}

enum class Timeframe(val label: String) {
    HOUR("1H"),
    DAY("24H"),
    WEEK("7D")
}

enum class SortOption(val label: String) {
    MARKET_CAP("Market Cap"),
    VOLUME("Volume"),
    CHANGE("% Change")
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MarketHeatmapScreen(
    onBack: () -> Unit,
    onCoinClick: (String) -> Unit = {}
) {
    var selectedTimeframe by remember { mutableStateOf(Timeframe.DAY) }
    var selectedSort by remember { mutableStateOf(SortOption.MARKET_CAP) }
    var selectedCoin by remember { mutableStateOf<HeatmapCoin?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    
    val pullToRefreshState = rememberPullToRefreshState()
    
    // Mock data - in real app fetch from API
    val coins = remember {
        mutableStateListOf(
            HeatmapCoin("BTCUSDT", "Bitcoin", 95234.50, 2.34, 890_000_000_000.0, 25_000_000_000.0),
            HeatmapCoin("ETHUSDT", "Ethereum", 3456.78, 4.12, 295_000_000_000.0, 12_000_000_000.0),
            HeatmapCoin("BNBUSDT", "BNB", 612.45, -1.23, 48_000_000_000.0, 800_000_000.0),
            HeatmapCoin("SOLUSDT", "Solana", 148.76, 8.45, 42_000_000_000.0, 2_500_000_000.0),
            HeatmapCoin("XRPUSDT", "XRP", 2.34, -0.45, 28_000_000_000.0, 1_200_000_000.0),
            HeatmapCoin("ADAUSDT", "Cardano", 0.95, 3.21, 16_000_000_000.0, 450_000_000.0),
            HeatmapCoin("AVAXUSDT", "Avalanche", 35.67, 5.67, 13_000_000_000.0, 520_000_000.0),
            HeatmapCoin("DOTUSDT", "Polkadot", 7.89, -2.34, 10_000_000_000.0, 380_000_000.0),
            HeatmapCoin("LINKUSDT", "Chainlink", 18.56, 6.78, 8_500_000_000.0, 650_000_000.0),
            HeatmapCoin("MATICUSDT", "Polygon", 0.8765, 1.23, 8_100_000_000.0, 420_000_000.0),
            HeatmapCoin("UNIUSDT", "Uniswap", 12.78, -3.45, 5_100_000_000.0, 180_000_000.0),
            HeatmapCoin("ATOMUSDT", "Cosmos", 9.12, 2.89, 3_500_000_000.0, 210_000_000.0),
            HeatmapCoin("LTCUSDT", "Litecoin", 95.34, -0.98, 5_400_000_000.0, 340_000_000.0),
            HeatmapCoin("NEARUSDT", "NEAR", 5.67, 7.89, 5_800_000_000.0, 380_000_000.0),
            HeatmapCoin("APTUSDT", "Aptos", 12.90, -4.56, 3_900_000_000.0, 290_000_000.0),
            HeatmapCoin("ARBUSDT", "Arbitrum", 1.23, 9.12, 3_100_000_000.0, 520_000_000.0)
        )
    }
    
    val sortedCoins = remember(selectedSort, coins.toList()) {
        when (selectedSort) {
            SortOption.MARKET_CAP -> coins.sortedByDescending { it.marketCap }
            SortOption.VOLUME -> coins.sortedByDescending { it.volume24h }
            SortOption.CHANGE -> coins.sortedByDescending { abs(it.change24h) }
        }
    }
    
    // Handle refresh
    LaunchedEffect(pullToRefreshState.isRefreshing) {
        if (pullToRefreshState.isRefreshing) {
            isLoading = true
            kotlinx.coroutines.delay(1000)
            isLoading = false
            pullToRefreshState.endRefresh()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Market Heatmap") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
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
                // Filters Row
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Timeframe Selector
                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .background(EnlikoCard),
                        horizontalArrangement = Arrangement.spacedBy(0.dp)
                    ) {
                        Timeframe.entries.forEach { timeframe ->
                            Surface(
                                onClick = { selectedTimeframe = timeframe },
                                color = if (selectedTimeframe == timeframe) EnlikoPrimary else Color.Transparent,
                                shape = RoundedCornerShape(8.dp)
                            ) {
                                Text(
                                    text = timeframe.label,
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Medium,
                                    color = if (selectedTimeframe == timeframe) Color.White else EnlikoTextSecondary,
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                                )
                            }
                        }
                    }
                    
                    Spacer(modifier = Modifier.weight(1f))
                    
                    // Sort Dropdown
                    var showSortMenu by remember { mutableStateOf(false) }
                    Box {
                        Surface(
                            onClick = { showSortMenu = true },
                            color = EnlikoCard,
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Text(
                                    text = selectedSort.label,
                                    style = MaterialTheme.typography.labelMedium,
                                    color = EnlikoTextPrimary
                                )
                                Icon(
                                    Icons.Default.ArrowDropDown,
                                    contentDescription = null,
                                    tint = EnlikoTextSecondary
                                )
                            }
                        }
                        
                        DropdownMenu(
                            expanded = showSortMenu,
                            onDismissRequest = { showSortMenu = false }
                        ) {
                            SortOption.entries.forEach { option ->
                                DropdownMenuItem(
                                    text = { Text(option.label) },
                                    onClick = {
                                        selectedSort = option
                                        showSortMenu = false
                                    },
                                    trailingIcon = if (selectedSort == option) {
                                        { Icon(Icons.Default.Check, contentDescription = null) }
                                    } else null
                                )
                            }
                        }
                    }
                }
                
                // Heatmap Grid
                LazyVerticalGrid(
                    columns = GridCells.Adaptive(minSize = 100.dp),
                    contentPadding = PaddingValues(8.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp),
                    modifier = Modifier.weight(1f)
                ) {
                    items(sortedCoins, key = { it.symbol }) { coin ->
                        HeatmapTile(
                            coin = coin,
                            onClick = {
                                selectedCoin = coin
                            }
                        )
                    }
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
    
    // Coin Detail Sheet
    if (selectedCoin != null) {
        CoinDetailSheet(
            coin = selectedCoin!!,
            onDismiss = { selectedCoin = null },
            onTrade = {
                onCoinClick(selectedCoin!!.symbol)
                selectedCoin = null
            }
        )
    }
}

@Composable
private fun HeatmapTile(
    coin: HeatmapCoin,
    onClick: () -> Unit
) {
    // Determine tile size based on market cap rank
    val height = 80.dp
    
    Surface(
        onClick = onClick,
        color = coin.changeColor,
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier
            .fillMaxWidth()
            .height(height)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Symbol
            Text(
                text = coin.shortSymbol,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            
            // Change %
            Text(
                text = "${if (coin.change24h >= 0) "+" else ""}${String.format("%.2f", coin.change24h)}%",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                color = Color.White.copy(alpha = 0.9f)
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun CoinDetailSheet(
    coin: HeatmapCoin,
    onDismiss: () -> Unit,
    onTrade: () -> Unit
) {
    val sheetState = rememberModalBottomSheetState()
    
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = EnlikoBackground
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = coin.name,
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = EnlikoTextPrimary
                    )
                    Text(
                        text = coin.symbol,
                        style = MaterialTheme.typography.bodyMedium,
                        color = EnlikoTextSecondary
                    )
                }
                
                Text(
                    text = "$${formatLargeNumber(coin.price)}",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = EnlikoTextPrimary
                )
            }
            
            // Change Badge
            Surface(
                color = coin.changeColor.copy(alpha = 0.2f),
                shape = RoundedCornerShape(8.dp)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        if (coin.change24h >= 0) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                        contentDescription = null,
                        tint = coin.changeColor,
                        modifier = Modifier.size(20.dp)
                    )
                    Text(
                        text = "${if (coin.change24h >= 0) "+" else ""}${String.format("%.2f", coin.change24h)}% (24h)",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium,
                        color = coin.changeColor
                    )
                }
            }
            
            HorizontalDivider(color = EnlikoBorder)
            
            // Stats Grid
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StatItem(label = "Market Cap", value = "$${formatLargeNumber(coin.marketCap)}")
                StatItem(label = "24h Volume", value = "$${formatLargeNumber(coin.volume24h)}")
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Trade Button
            Button(
                onClick = onTrade,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(
                    Icons.Default.TrendingUp,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Trade ${coin.shortSymbol}", fontWeight = FontWeight.SemiBold)
            }
            
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun StatItem(
    label: String,
    value: String
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = EnlikoTextMuted
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = EnlikoTextPrimary
        )
    }
}

private fun formatLargeNumber(value: Double): String {
    return when {
        value >= 1_000_000_000_000 -> String.format("%.2fT", value / 1_000_000_000_000)
        value >= 1_000_000_000 -> String.format("%.2fB", value / 1_000_000_000)
        value >= 1_000_000 -> String.format("%.2fM", value / 1_000_000)
        value >= 1_000 -> String.format("%.2fK", value / 1_000)
        value >= 100 -> String.format("%.0f", value)
        value >= 1 -> String.format("%.2f", value)
        else -> String.format("%.6f", value)
    }
}
