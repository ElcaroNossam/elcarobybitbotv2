package io.enliko.trading.ui.screens.spot

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import kotlinx.coroutines.delay
import kotlin.random.Random
import io.enliko.trading.util.LocalStrings

// MARK: - Data Models
data class SpotAsset(
    val symbol: String,
    val name: String,
    val price: Double,
    val change24h: Double,
    val volume24h: Double,
    val balance: Double = 0.0,
    val balanceUsdt: Double = 0.0,
    val isFavorite: Boolean = false
)

data class SpotOrder(
    val id: String,
    val symbol: String,
    val side: String,
    val type: String,
    val price: Double,
    val amount: Double,
    val filled: Double,
    val status: String,
    val time: String
)

enum class SpotTab(val label: String) {
    MARKET("Market"),
    ORDERS("Orders"),
    HOLDINGS("Holdings")
}

enum class SpotOrderType(val label: String) {
    MARKET("Market"),
    LIMIT("Limit")
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpotTradingScreen(
    onNavigateBack: () -> Unit = {}
) {
    var selectedTab by remember { mutableStateOf(SpotTab.MARKET) }
    var selectedAsset by remember { mutableStateOf<SpotAsset?>(null) }
    var showTradeSheet by remember { mutableStateOf(false) }
    
    var assets by remember { mutableStateOf(listOf<SpotAsset>()) }
    var orders by remember { mutableStateOf(listOf<SpotOrder>()) }
    var holdings by remember { mutableStateOf(listOf<SpotAsset>()) }
    var isLoading by remember { mutableStateOf(true) }
    var searchQuery by remember { mutableStateOf("") }
    
    // Load data
    LaunchedEffect(Unit) {
        delay(500)
        assets = generateMockAssets()
        orders = generateMockOrders()
        holdings = generateMockHoldings()
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Spot Trading", fontWeight = FontWeight.Bold) },
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
            // Tab Row
            TabRow(selectedTabIndex = selectedTab.ordinal) {
                SpotTab.entries.forEach { tab ->
                    Tab(
                        selected = selectedTab == tab,
                        onClick = { selectedTab = tab },
                        text = { Text(tab.label) }
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
                when (selectedTab) {
                    SpotTab.MARKET -> MarketContent(
                        assets = assets.filter { 
                            searchQuery.isEmpty() || 
                            it.symbol.contains(searchQuery, ignoreCase = true) ||
                            it.name.contains(searchQuery, ignoreCase = true)
                        },
                        onAssetClick = { asset ->
                            selectedAsset = asset
                            showTradeSheet = true
                        },
                        searchQuery = searchQuery,
                        onSearchChange = { searchQuery = it }
                    )
                    SpotTab.ORDERS -> OrdersContent(
                        orders = orders,
                        onCancelOrder = { /* Cancel order */ }
                    )
                    SpotTab.HOLDINGS -> HoldingsContent(
                        holdings = holdings,
                        onAssetClick = { asset ->
                            selectedAsset = asset
                            showTradeSheet = true
                        }
                    )
                }
            }
        }
    }
    
    // Trade Bottom Sheet
    if (showTradeSheet && selectedAsset != null) {
        SpotTradeBottomSheet(
            asset = selectedAsset!!,
            onDismiss = { showTradeSheet = false },
            onTrade = { side, type, amount, price ->
                // Execute trade
                showTradeSheet = false
            }
        )
    }
}

@Composable
private fun MarketContent(
    assets: List<SpotAsset>,
    onAssetClick: (SpotAsset) -> Unit,
    searchQuery: String,
    onSearchChange: (String) -> Unit
) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Search Bar
        OutlinedTextField(
            value = searchQuery,
            onValueChange = onSearchChange,
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            placeholder = { Text("Search coin...") },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { onSearchChange("") }) {
                        Icon(Icons.Default.Close, contentDescription = "Clear")
                    }
                }
            },
            singleLine = true,
            shape = RoundedCornerShape(12.dp)
        )
        
        // Category Filters
        LazyRow(
            contentPadding = PaddingValues(horizontal = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val categories = listOf("All", "⭐ Favorites", "BTC", "ETH", "Layer1", "DeFi", "Meme")
            items(categories) { category ->
                FilterChip(
                    selected = category == "All",
                    onClick = { /* Filter by category */ },
                    label = { Text(category) }
                )
            }
        }
        
        // Asset List
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(assets) { asset ->
                SpotAssetCard(
                    asset = asset,
                    onClick = { onAssetClick(asset) }
                )
            }
        }
    }
}

@Composable
private fun SpotAssetCard(
    asset: SpotAsset,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Coin Icon Placeholder
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = asset.symbol.take(1),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Column {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = asset.symbol.replace("USDT", ""),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        if (asset.isFavorite) {
                            Icon(
                                Icons.Default.Star,
                                contentDescription = null,
                                tint = Color(0xFFFFD700),
                                modifier = Modifier.size(14.dp)
                            )
                        }
                    }
                    Text(
                        text = asset.name,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "$${formatPrice(asset.price)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${if (asset.change24h >= 0) "+" else ""}${String.format("%.2f", asset.change24h)}%",
                    style = MaterialTheme.typography.bodySmall,
                    color = if (asset.change24h >= 0) LongGreen else ShortRed
                )
            }
        }
    }
}

@Composable
private fun OrdersContent(
    orders: List<SpotOrder>,
    onCancelOrder: (SpotOrder) -> Unit
) {
    val strings = LocalStrings.current
    if (orders.isEmpty()) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    Icons.Default.Receipt,
                    contentDescription = null,
                    modifier = Modifier.size(64.dp),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = strings.noOpenOrders,
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(orders) { order ->
                SpotOrderCard(
                    order = order,
                    onCancel = { onCancelOrder(order) }
                )
            }
        }
    }
}

@Composable
private fun SpotOrderCard(
    order: SpotOrder,
    onCancel: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
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
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = if (order.side == "Buy") LongGreen.copy(alpha = 0.1f) else ShortRed.copy(alpha = 0.1f)
                    ) {
                        Text(
                            text = order.side,
                            style = MaterialTheme.typography.labelSmall,
                            color = if (order.side == "Buy") LongGreen else ShortRed,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = MaterialTheme.colorScheme.surfaceVariant
                    ) {
                        Text(
                            text = order.type,
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }
                
                IconButton(onClick = onCancel) {
                    Icon(
                        Icons.Default.Close,
                        contentDescription = "Cancel",
                        tint = ShortRed
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("Price", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("$${formatPrice(order.price)}", style = MaterialTheme.typography.bodyMedium)
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("Amount", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("${order.amount}", style = MaterialTheme.typography.bodyMedium)
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text("Filled", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("${String.format("%.1f", order.filled / order.amount * 100)}%", style = MaterialTheme.typography.bodyMedium)
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Progress bar
            LinearProgressIndicator(
                progress = { (order.filled / order.amount).toFloat() },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp)),
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = order.time,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun HoldingsContent(
    holdings: List<SpotAsset>,
    onAssetClick: (SpotAsset) -> Unit
) {
    val strings = LocalStrings.current
    Column(modifier = Modifier.fillMaxSize()) {
        // Total Value Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = strings.totalSpotValue,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "$${String.format("%.2f", holdings.sumOf { it.balanceUsdt })}",
                    style = MaterialTheme.typography.headlineLarge,
                    fontWeight = FontWeight.Bold
                )
            }
        }
        
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(holdings.filter { it.balance > 0 }) { asset ->
                HoldingAssetCard(
                    asset = asset,
                    onClick = { onAssetClick(asset) }
                )
            }
        }
    }
}

@Composable
private fun HoldingAssetCard(
    asset: SpotAsset,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = asset.symbol.replace("USDT", "").take(1),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Column {
                    Text(
                        text = asset.symbol.replace("USDT", ""),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "${String.format("%.6f", asset.balance)} ${asset.symbol.replace("USDT", "")}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "$${String.format("%.2f", asset.balanceUsdt)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${if (asset.change24h >= 0) "+" else ""}${String.format("%.2f", asset.change24h)}%",
                    style = MaterialTheme.typography.bodySmall,
                    color = if (asset.change24h >= 0) LongGreen else ShortRed
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SpotTradeBottomSheet(
    asset: SpotAsset,
    onDismiss: () -> Unit,
    onTrade: (String, SpotOrderType, Double, Double?) -> Unit
) {
    val strings = LocalStrings.current
    var isBuy by remember { mutableStateOf(true) }
    var orderType by remember { mutableStateOf(SpotOrderType.MARKET) }
    var amount by remember { mutableStateOf("") }
    var price by remember { mutableStateOf(asset.price.toString()) }
    
    val availableBalance = 10000.0 // USDT balance for buy
    val assetBalance = asset.balance // Asset balance for sell
    
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = MaterialTheme.colorScheme.surface
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Trade ${asset.symbol.replace("USDT", "")}",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "$${formatPrice(asset.price)}",
                    style = MaterialTheme.typography.titleMedium,
                    color = if (asset.change24h >= 0) LongGreen else ShortRed
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Buy/Sell Toggle
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (isBuy) LongGreen else Color.Transparent)
                        .clickable { isBuy = true },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = strings.buy,
                        fontWeight = FontWeight.Bold,
                        color = if (isBuy) Color.White else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (!isBuy) ShortRed else Color.Transparent)
                        .clickable { isBuy = false },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = strings.sell,
                        fontWeight = FontWeight.Bold,
                        color = if (!isBuy) Color.White else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Order Type
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SpotOrderType.entries.forEach { type ->
                    FilterChip(
                        selected = orderType == type,
                        onClick = { orderType = type },
                        label = { Text(type.label) }
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Price (only for limit orders)
            if (orderType == SpotOrderType.LIMIT) {
                OutlinedTextField(
                    value = price,
                    onValueChange = { price = it },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Price (USDT)") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    singleLine = true,
                    shape = RoundedCornerShape(12.dp)
                )
                
                Spacer(modifier = Modifier.height(12.dp))
            }
            
            // Amount
            OutlinedTextField(
                value = amount,
                onValueChange = { amount = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Amount (${asset.symbol.replace("USDT", "")})") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
                supportingText = {
                    Text(
                        if (isBuy) "Available: $${String.format("%.2f", availableBalance)} USDT"
                        else "Available: ${String.format("%.6f", assetBalance)} ${asset.symbol.replace("USDT", "")}"
                    )
                }
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Quick Amount Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf("25%", "50%", "75%", "100%").forEach { percent ->
                    OutlinedButton(
                        onClick = {
                            val pct = percent.replace("%", "").toDouble() / 100
                            val maxAmount = if (isBuy) {
                                val effectivePrice = if (orderType == SpotOrderType.LIMIT) price.toDoubleOrNull() ?: asset.price else asset.price
                                availableBalance / effectivePrice * pct
                            } else {
                                assetBalance * pct
                            }
                            amount = String.format("%.6f", maxAmount)
                        },
                        modifier = Modifier.weight(1f),
                        contentPadding = PaddingValues(8.dp)
                    ) {
                        Text(percent, style = MaterialTheme.typography.labelSmall)
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Total
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = strings.total,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                val amountValue = amount.toDoubleOrNull() ?: 0.0
                val priceValue = if (orderType == SpotOrderType.LIMIT) price.toDoubleOrNull() ?: asset.price else asset.price
                Text(
                    text = "≈ $${String.format("%.2f", amountValue * priceValue)} USDT",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Trade Button
            Button(
                onClick = {
                    val amountValue = amount.toDoubleOrNull() ?: return@Button
                    val priceValue = if (orderType == SpotOrderType.LIMIT) price.toDoubleOrNull() else null
                    onTrade(if (isBuy) "Buy" else "Sell", orderType, amountValue, priceValue)
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isBuy) LongGreen else ShortRed
                ),
                shape = RoundedCornerShape(12.dp),
                enabled = amount.toDoubleOrNull()?.let { it > 0 } == true
            ) {
                Text(
                    text = "${if (isBuy) "Buy" else "Sell"} ${asset.symbol.replace("USDT", "")}",
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

// Helpers
private fun formatPrice(price: Double): String {
    return when {
        price >= 1000 -> String.format("%.2f", price)
        price >= 1 -> String.format("%.4f", price)
        price >= 0.01 -> String.format("%.6f", price)
        else -> String.format("%.8f", price)
    }
}

// Mock data generators
private fun generateMockAssets(): List<SpotAsset> {
    return listOf(
        SpotAsset("BTCUSDT", "Bitcoin", 97500.0, Random.nextDouble(-5.0, 8.0), 45_000_000_000.0, isFavorite = true),
        SpotAsset("ETHUSDT", "Ethereum", 3850.0, Random.nextDouble(-5.0, 8.0), 28_000_000_000.0, isFavorite = true),
        SpotAsset("BNBUSDT", "BNB", 720.0, Random.nextDouble(-5.0, 8.0), 2_500_000_000.0),
        SpotAsset("SOLUSDT", "Solana", 245.0, Random.nextDouble(-8.0, 12.0), 8_000_000_000.0),
        SpotAsset("XRPUSDT", "XRP", 2.45, Random.nextDouble(-5.0, 10.0), 5_000_000_000.0),
        SpotAsset("ADAUSDT", "Cardano", 1.05, Random.nextDouble(-5.0, 8.0), 1_200_000_000.0),
        SpotAsset("DOGEUSDT", "Dogecoin", 0.42, Random.nextDouble(-8.0, 15.0), 3_500_000_000.0),
        SpotAsset("AVAXUSDT", "Avalanche", 42.0, Random.nextDouble(-5.0, 10.0), 800_000_000.0),
        SpotAsset("DOTUSDT", "Polkadot", 8.5, Random.nextDouble(-5.0, 8.0), 450_000_000.0),
        SpotAsset("LINKUSDT", "Chainlink", 28.0, Random.nextDouble(-5.0, 10.0), 600_000_000.0),
        SpotAsset("MATICUSDT", "Polygon", 0.58, Random.nextDouble(-5.0, 8.0), 350_000_000.0),
        SpotAsset("ATOMUSDT", "Cosmos", 9.2, Random.nextDouble(-5.0, 10.0), 250_000_000.0)
    )
}

private fun generateMockOrders(): List<SpotOrder> {
    return listOf(
        SpotOrder("1", "BTCUSDT", "Buy", "Limit", 95000.0, 0.05, 0.02, "Open", "2 hours ago"),
        SpotOrder("2", "ETHUSDT", "Sell", "Limit", 4000.0, 1.5, 0.0, "Open", "1 hour ago"),
        SpotOrder("3", "SOLUSDT", "Buy", "Limit", 220.0, 10.0, 5.0, "Partially Filled", "30 min ago")
    )
}

private fun generateMockHoldings(): List<SpotAsset> {
    return listOf(
        SpotAsset("BTCUSDT", "Bitcoin", 97500.0, 2.5, 0.0, 0.25, 24375.0),
        SpotAsset("ETHUSDT", "Ethereum", 3850.0, 1.8, 0.0, 5.0, 19250.0),
        SpotAsset("SOLUSDT", "Solana", 245.0, 5.2, 0.0, 50.0, 12250.0),
        SpotAsset("BNBUSDT", "BNB", 720.0, -1.2, 0.0, 10.0, 7200.0),
        SpotAsset("USDTUSDT", "USDT", 1.0, 0.0, 0.0, 5000.0, 5000.0)
    )
}
