package io.enliko.trading.ui.screens.market

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import java.text.NumberFormat
import java.util.*
import kotlin.math.abs

// MARK: - Data Models
data class MarketOverview(
    val totalMarketCap: Double,
    val totalVolume24h: Double,
    val btcDominance: Double,
    val fearGreedIndex: Int,
    val activeCoins: Int,
    val exchanges: Int
)

data class TrendingCoin(
    val symbol: String,
    val name: String,
    val price: Double,
    val change24h: Double,
    val volume24h: Double,
    val rank: Int
)

data class MarketSector(
    val name: String,
    val change24h: Double,
    val coins: Int,
    val marketCap: Double
)

enum class MarketHubTab { OVERVIEW, TRENDING, SECTORS, HEATMAP, NEWS }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MarketHubScreen(
    onNavigateBack: () -> Unit = {},
    onCoinSelected: (String) -> Unit = {}
) {
    var selectedTab by remember { mutableStateOf(MarketHubTab.OVERVIEW) }
    var isLoading by remember { mutableStateOf(true) }
    
    var overview by remember { mutableStateOf<MarketOverview?>(null) }
    var topGainers by remember { mutableStateOf<List<TrendingCoin>>(emptyList()) }
    var topLosers by remember { mutableStateOf<List<TrendingCoin>>(emptyList()) }
    var trending by remember { mutableStateOf<List<TrendingCoin>>(emptyList()) }
    var sectors by remember { mutableStateOf<List<MarketSector>>(emptyList()) }
    var heatmapData by remember { mutableStateOf<List<TrendingCoin>>(emptyList()) }
    
    // Mock data
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(500)
        
        overview = MarketOverview(
            totalMarketCap = 3_450_000_000_000.0,
            totalVolume24h = 125_000_000_000.0,
            btcDominance = 52.3,
            fearGreedIndex = 65,
            activeCoins = 12500,
            exchanges = 750
        )
        
        topGainers = listOf(
            TrendingCoin("PEPE", "Pepe", 0.0000125, 45.5, 1_500_000_000.0, 23),
            TrendingCoin("WIF", "dogwifhat", 3.25, 32.8, 800_000_000.0, 35),
            TrendingCoin("BONK", "Bonk", 0.000028, 28.5, 600_000_000.0, 52),
            TrendingCoin("FET", "Fetch.ai", 2.45, 22.3, 450_000_000.0, 28),
            TrendingCoin("RNDR", "Render", 8.75, 18.9, 350_000_000.0, 32)
        )
        
        topLosers = listOf(
            TrendingCoin("GMT", "STEPN", 0.18, -15.5, 150_000_000.0, 85),
            TrendingCoin("APE", "ApeCoin", 1.45, -12.8, 180_000_000.0, 68),
            TrendingCoin("GALA", "Gala", 0.045, -10.5, 120_000_000.0, 75),
            TrendingCoin("SAND", "Sandbox", 0.55, -8.9, 200_000_000.0, 62),
            TrendingCoin("MANA", "Decentraland", 0.48, -7.5, 180_000_000.0, 65)
        )
        
        trending = listOf(
            TrendingCoin("BTC", "Bitcoin", 98500.0, 2.5, 45_000_000_000.0, 1),
            TrendingCoin("ETH", "Ethereum", 3200.0, 1.8, 18_000_000_000.0, 2),
            TrendingCoin("SOL", "Solana", 180.0, 5.2, 8_000_000_000.0, 5),
            TrendingCoin("XRP", "Ripple", 2.35, 3.8, 6_000_000_000.0, 4),
            TrendingCoin("DOGE", "Dogecoin", 0.38, 8.5, 4_500_000_000.0, 8),
            TrendingCoin("ADA", "Cardano", 1.05, 2.1, 2_500_000_000.0, 9),
            TrendingCoin("AVAX", "Avalanche", 42.5, 4.2, 1_800_000_000.0, 12),
            TrendingCoin("LINK", "Chainlink", 18.5, 3.5, 1_200_000_000.0, 14)
        )
        
        sectors = listOf(
            MarketSector("Layer 1", 3.5, 45, 850_000_000_000.0),
            MarketSector("DeFi", 2.8, 120, 120_000_000_000.0),
            MarketSector("Memes", 15.2, 85, 65_000_000_000.0),
            MarketSector("AI", 8.5, 35, 45_000_000_000.0),
            MarketSector("Gaming", -2.5, 60, 25_000_000_000.0),
            MarketSector("Layer 2", 4.2, 25, 35_000_000_000.0),
            MarketSector("Exchange Tokens", 1.5, 20, 80_000_000_000.0),
            MarketSector("NFT", -5.2, 40, 8_000_000_000.0)
        )
        
        heatmapData = trending + topGainers.take(10) + topLosers.take(10)
        
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Market Hub") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { /* Search */ }) {
                        Icon(Icons.Default.Search, contentDescription = "Search")
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
                edgePadding = 16.dp
            ) {
                MarketHubTab.entries.forEach { tab ->
                    Tab(
                        selected = selectedTab == tab,
                        onClick = { selectedTab = tab },
                        text = {
                            Text(
                                text = tab.name.lowercase().replaceFirstChar { it.uppercase() },
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
                    transitionSpec = { fadeIn() togetherWith fadeOut() },
                    label = "market_tab"
                ) { tab ->
                    when (tab) {
                        MarketHubTab.OVERVIEW -> OverviewTab(
                            overview = overview,
                            topGainers = topGainers,
                            topLosers = topLosers,
                            onCoinSelected = onCoinSelected
                        )
                        MarketHubTab.TRENDING -> TrendingTab(
                            trending = trending,
                            onCoinSelected = onCoinSelected
                        )
                        MarketHubTab.SECTORS -> SectorsTab(sectors = sectors)
                        MarketHubTab.HEATMAP -> HeatmapTab(
                            coins = heatmapData,
                            onCoinSelected = onCoinSelected
                        )
                        MarketHubTab.NEWS -> NewsTab()
                    }
                }
            }
        }
    }
}

@Composable
private fun OverviewTab(
    overview: MarketOverview?,
    topGainers: List<TrendingCoin>,
    topLosers: List<TrendingCoin>,
    onCoinSelected: (String) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        overview?.let { ov ->
            // Market Stats Grid
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    StatCard(
                        title = "Market Cap",
                        value = formatCompactCurrency(ov.totalMarketCap),
                        modifier = Modifier.weight(1f)
                    )
                    StatCard(
                        title = "24h Volume",
                        value = formatCompactCurrency(ov.totalVolume24h),
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    StatCard(
                        title = "BTC Dominance",
                        value = "${String.format("%.1f", ov.btcDominance)}%",
                        modifier = Modifier.weight(1f)
                    )
                    FearGreedCard(
                        index = ov.fearGreedIndex,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
        
        // Top Gainers
        item {
            SectionHeader(title = "🚀 Top Gainers", subtitle = "24h")
        }
        
        item {
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(topGainers) { coin ->
                    CoinMiniCard(
                        coin = coin,
                        onClick = { onCoinSelected(coin.symbol) }
                    )
                }
            }
        }
        
        // Top Losers
        item {
            SectionHeader(title = "📉 Top Losers", subtitle = "24h")
        }
        
        item {
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(topLosers) { coin ->
                    CoinMiniCard(
                        coin = coin,
                        onClick = { onCoinSelected(coin.symbol) }
                    )
                }
            }
        }
    }
}

@Composable
private fun StatCard(
    title: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
private fun FearGreedCard(
    index: Int,
    modifier: Modifier = Modifier
) {
    val (color, label) = when {
        index < 25 -> ShortRed to "Extreme Fear"
        index < 45 -> Color(0xFFFF9800) to "Fear"
        index < 55 -> Color.Gray to "Neutral"
        index < 75 -> LongGreen.copy(alpha = 0.7f) to "Greed"
        else -> LongGreen to "Extreme Greed"
    }
    
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.2f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Fear & Greed",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = index.toString(),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = color
                )
                Text(
                    text = label,
                    style = MaterialTheme.typography.bodyMedium,
                    color = color
                )
            }
        }
    }
}

@Composable
private fun SectionHeader(title: String, subtitle: String = "") {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        if (subtitle.isNotEmpty()) {
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun CoinMiniCard(
    coin: TrendingCoin,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .width(140.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = coin.symbol.take(1),
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                }
                Column {
                    Text(
                        text = coin.symbol,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = coin.name,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = formatPrice(coin.price),
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            
            Text(
                text = "${if (coin.change24h >= 0) "+" else ""}${String.format("%.2f", coin.change24h)}%",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = if (coin.change24h >= 0) LongGreen else ShortRed
            )
        }
    }
}

@Composable
private fun TrendingTab(
    trending: List<TrendingCoin>,
    onCoinSelected: (String) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(trending) { coin ->
            CoinListRow(coin = coin, onClick = { onCoinSelected(coin.symbol) })
        }
    }
}

@Composable
private fun CoinListRow(
    coin: TrendingCoin,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
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
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "#${coin.rank}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.width(32.dp)
                )
                
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = coin.symbol.take(1),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                }
                
                Column {
                    Text(
                        text = coin.symbol,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = coin.name,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = formatPrice(coin.price),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${if (coin.change24h >= 0) "+" else ""}${String.format("%.2f", coin.change24h)}%",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (coin.change24h >= 0) LongGreen else ShortRed
                )
            }
        }
    }
}

@Composable
private fun SectorsTab(sectors: List<MarketSector>) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(sectors) { sector ->
            SectorCard(sector = sector)
        }
    }
}

@Composable
private fun SectorCard(sector: MarketSector) {
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
                    text = sector.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${sector.coins} coins • ${formatCompactCurrency(sector.marketCap)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Text(
                text = "${if (sector.change24h >= 0) "+" else ""}${String.format("%.2f", sector.change24h)}%",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = if (sector.change24h >= 0) LongGreen else ShortRed
            )
        }
    }
}

@Composable
private fun HeatmapTab(
    coins: List<TrendingCoin>,
    onCoinSelected: (String) -> Unit
) {
    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = 80.dp),
        contentPadding = PaddingValues(8.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        items(coins, key = { it.symbol }) { coin ->
            HeatmapCell(coin = coin, onClick = { onCoinSelected(coin.symbol) })
        }
    }
}

@Composable
private fun HeatmapCell(
    coin: TrendingCoin,
    onClick: () -> Unit
) {
    val intensity = (abs(coin.change24h) / 20).coerceIn(0.0, 1.0)
    val backgroundColor = if (coin.change24h >= 0) {
        LongGreen.copy(alpha = (0.3 + intensity * 0.7).toFloat())
    } else {
        ShortRed.copy(alpha = (0.3 + intensity * 0.7).toFloat())
    }
    
    Card(
        modifier = Modifier
            .aspectRatio(1f)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = coin.symbol,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                textAlign = TextAlign.Center
            )
            Text(
                text = "${if (coin.change24h >= 0) "+" else ""}${String.format("%.1f", coin.change24h)}%",
                style = MaterialTheme.typography.bodySmall,
                color = Color.White.copy(alpha = 0.9f),
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
private fun NewsTab() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Newspaper,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "News Coming Soon",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

private fun formatPrice(value: Double): String {
    return when {
        value >= 1000 -> String.format("$%.0f", value)
        value >= 1 -> String.format("$%.2f", value)
        value >= 0.01 -> String.format("$%.4f", value)
        else -> String.format("$%.8f", value)
    }
}

private fun formatCompactCurrency(value: Double): String {
    return when {
        value >= 1_000_000_000_000 -> String.format("$%.2fT", value / 1_000_000_000_000)
        value >= 1_000_000_000 -> String.format("$%.2fB", value / 1_000_000_000)
        value >= 1_000_000 -> String.format("$%.2fM", value / 1_000_000)
        value >= 1_000 -> String.format("$%.2fK", value / 1_000)
        else -> String.format("$%.2f", value)
    }
}
