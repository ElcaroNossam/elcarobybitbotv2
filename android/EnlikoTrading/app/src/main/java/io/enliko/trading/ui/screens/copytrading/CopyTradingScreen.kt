package io.enliko.trading.ui.screens.copytrading

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import kotlinx.coroutines.delay

// MARK: - Data Models
data class Trader(
    val id: String,
    val name: String,
    val avatar: String,
    val pnlPercent: Double,
    val pnlAmount: Double,
    val winRate: Double,
    val followers: Int,
    val trades: Int,
    val maxDrawdown: Double,
    val sharpeRatio: Double,
    val aum: Double,
    val isFollowing: Boolean = false,
    val isVerified: Boolean = false,
    val rank: Int = 0,
    val tags: List<String> = emptyList()
)

data class CopySettings(
    val maxCopyAmount: Double = 1000.0,
    val copyPercentage: Double = 10.0,
    val maxPositions: Int = 5,
    val stopCopyingOnLoss: Double = 20.0,
    val copyOnlySpecificPairs: Boolean = false,
    val allowedPairs: List<String> = emptyList()
)

enum class TraderTab { TOP, FOLLOWING, DISCOVER }
enum class TraderSortBy { PNL, WIN_RATE, FOLLOWERS, SHARPE }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CopyTradingScreen(
    onNavigateBack: () -> Unit = {},
    onViewTraderProfile: (String) -> Unit = {}
) {
    var selectedTab by remember { mutableStateOf(TraderTab.TOP) }
    var sortBy by remember { mutableStateOf(TraderSortBy.PNL) }
    var traders by remember { mutableStateOf(listOf<Trader>()) }
    var isLoading by remember { mutableStateOf(true) }
    var showCopyDialog by remember { mutableStateOf<Trader?>(null) }
    var showFilters by remember { mutableStateOf(false) }
    
    var totalCopied by remember { mutableDoubleStateOf(0.0) }
    var totalPnL by remember { mutableDoubleStateOf(0.0) }
    var followingCount by remember { mutableIntStateOf(0) }
    
    // Load mock data
    LaunchedEffect(Unit) {
        delay(500)
        traders = generateMockTraders()
        totalCopied = 5420.0
        totalPnL = 847.50
        followingCount = 3
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Column {
                        Text("Copy Trading", fontWeight = FontWeight.Bold)
                        Text(
                            "Follow top traders",
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
                    IconButton(onClick = { showFilters = true }) {
                        Icon(Icons.Default.FilterList, contentDescription = "Filter")
                    }
                    IconButton(onClick = { /* Open settings */ }) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings")
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
            // Stats Overview
            StatsOverview(
                totalCopied = totalCopied,
                totalPnL = totalPnL,
                followingCount = followingCount
            )
            
            // Tab Row
            TabRow(
                selectedTabIndex = selectedTab.ordinal,
                modifier = Modifier.padding(horizontal = 16.dp)
            ) {
                TraderTab.entries.forEach { tab ->
                    Tab(
                        selected = tab == selectedTab,
                        onClick = { selectedTab = tab },
                        text = { 
                            Text(
                                when (tab) {
                                    TraderTab.TOP -> "🏆 Top"
                                    TraderTab.FOLLOWING -> "⭐ Following"
                                    TraderTab.DISCOVER -> "🔍 Discover"
                                }
                            ) 
                        }
                    )
                }
            }
            
            // Sort Options
            LazyRow(
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(TraderSortBy.entries) { sort ->
                    FilterChip(
                        selected = sort == sortBy,
                        onClick = { sortBy = sort },
                        label = { 
                            Text(
                                when (sort) {
                                    TraderSortBy.PNL -> "PnL"
                                    TraderSortBy.WIN_RATE -> "Win Rate"
                                    TraderSortBy.FOLLOWERS -> "Followers"
                                    TraderSortBy.SHARPE -> "Sharpe"
                                }
                            )
                        }
                    )
                }
            }
            
            // Traders List
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else {
                val filteredTraders = when (selectedTab) {
                    TraderTab.TOP -> traders.sortedByDescending { 
                        when (sortBy) {
                            TraderSortBy.PNL -> it.pnlPercent
                            TraderSortBy.WIN_RATE -> it.winRate
                            TraderSortBy.FOLLOWERS -> it.followers.toDouble()
                            TraderSortBy.SHARPE -> it.sharpeRatio
                        }
                    }
                    TraderTab.FOLLOWING -> traders.filter { it.isFollowing }
                    TraderTab.DISCOVER -> traders.shuffled().take(10)
                }
                
                LazyColumn(
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(filteredTraders) { trader ->
                        TraderCard(
                            trader = trader,
                            onCopy = { showCopyDialog = trader },
                            onViewProfile = { onViewTraderProfile(trader.id) }
                        )
                    }
                }
            }
        }
    }
    
    // Copy Dialog
    showCopyDialog?.let { trader ->
        CopyTraderDialog(
            trader = trader,
            onConfirm = { settings ->
                // TODO: Start copying trader
                showCopyDialog = null
            },
            onDismiss = { showCopyDialog = null }
        )
    }
    
    // Filters Sheet
    if (showFilters) {
        FiltersBottomSheet(
            onDismiss = { showFilters = false }
        )
    }
}

@Composable
private fun StatsOverview(
    totalCopied: Double,
    totalPnL: Double,
    followingCount: Int
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        StatCard(
            title = "Copied",
            value = "$${String.format("%.0f", totalCopied)}",
            icon = Icons.Filled.MonetizationOn,
            color = Color(0xFF3B82F6)
        )
        StatCard(
            title = "Total PnL",
            value = "${if (totalPnL >= 0) "+" else ""}$${String.format("%.2f", totalPnL)}",
            icon = Icons.Filled.TrendingUp,
            color = if (totalPnL >= 0) LongGreen else ShortRed
        )
        StatCard(
            title = "Following",
            value = followingCount.toString(),
            icon = Icons.Filled.Groups,
            color = Color(0xFF8B5CF6)
        )
    }
}

@Composable
private fun StatCard(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            icon,
            contentDescription = title,
            tint = color,
            modifier = Modifier.size(28.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = title,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun TraderCard(
    trader: Trader,
    onCopy: () -> Unit,
    onViewProfile: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onViewProfile() },
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Avatar with rank badge
                Box {
                    Box(
                        modifier = Modifier
                            .size(52.dp)
                            .clip(CircleShape)
                            .background(
                                Brush.linearGradient(
                                    colors = listOf(
                                        Color(0xFF6366F1),
                                        Color(0xFF8B5CF6)
                                    )
                                )
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = trader.name.take(2).uppercase(),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                    
                    if (trader.rank in 1..3) {
                        Surface(
                            modifier = Modifier
                                .align(Alignment.BottomEnd)
                                .size(20.dp),
                            shape = CircleShape,
                            color = when (trader.rank) {
                                1 -> Color(0xFFFFD700)
                                2 -> Color(0xFFC0C0C0)
                                else -> Color(0xFFCD7F32)
                            }
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    text = "#${trader.rank}",
                                    style = MaterialTheme.typography.labelSmall,
                                    fontSize = 8.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.Black
                                )
                            }
                        }
                    }
                }
                
                Spacer(modifier = Modifier.width(12.dp))
                
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = trader.name,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        if (trader.isVerified) {
                            Spacer(modifier = Modifier.width(4.dp))
                            Icon(
                                Icons.Filled.Verified,
                                contentDescription = "Verified",
                                tint = Color(0xFF3B82F6),
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                    
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "${trader.followers} followers",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "•",
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "${trader.trades} trades",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "${if (trader.pnlPercent >= 0) "+" else ""}${String.format("%.1f", trader.pnlPercent)}%",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = if (trader.pnlPercent >= 0) LongGreen else ShortRed
                    )
                    Text(
                        text = "30D PnL",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Stats Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                TraderStatItem("Win Rate", "${String.format("%.1f", trader.winRate)}%")
                TraderStatItem("Max DD", "${String.format("%.1f", trader.maxDrawdown)}%")
                TraderStatItem("Sharpe", String.format("%.2f", trader.sharpeRatio))
                TraderStatItem("AUM", "$${formatCompact(trader.aum)}")
            }
            
            // Tags
            if (trader.tags.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    trader.tags.take(3).forEach { tag ->
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.5f)
                        ) {
                            Text(
                                text = tag,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                style = MaterialTheme.typography.labelSmall
                            )
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Action buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedButton(
                    onClick = onViewProfile,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Default.Person, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Profile")
                }
                
                Button(
                    onClick = onCopy,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (trader.isFollowing) Color.Gray else LongGreen
                    )
                ) {
                    Icon(
                        if (trader.isFollowing) Icons.Default.Check else Icons.Default.PersonAdd,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(if (trader.isFollowing) "Following" else "Copy")
                }
            }
        }
    }
}

@Composable
private fun TraderStatItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun CopyTraderDialog(
    trader: Trader,
    onConfirm: (CopySettings) -> Unit,
    onDismiss: () -> Unit
) {
    var copyAmount by remember { mutableStateOf("1000") }
    var copyPercentage by remember { mutableStateOf("10") }
    var maxPositions by remember { mutableStateOf("5") }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { 
            Text("Copy ${trader.name}", fontWeight = FontWeight.Bold) 
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                OutlinedTextField(
                    value = copyAmount,
                    onValueChange = { copyAmount = it },
                    label = { Text("Max Copy Amount (USDT)") },
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = copyPercentage,
                    onValueChange = { copyPercentage = it },
                    label = { Text("Copy Percentage (%)") },
                    modifier = Modifier.fillMaxWidth(),
                    supportingText = { Text("Percentage of trader's position size") }
                )
                
                OutlinedTextField(
                    value = maxPositions,
                    onValueChange = { maxPositions = it },
                    label = { Text("Max Positions") },
                    modifier = Modifier.fillMaxWidth()
                )
                
                Text(
                    text = "⚠️ Copy trading involves risk. Past performance doesn't guarantee future results.",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    onConfirm(CopySettings(
                        maxCopyAmount = copyAmount.toDoubleOrNull() ?: 1000.0,
                        copyPercentage = copyPercentage.toDoubleOrNull() ?: 10.0,
                        maxPositions = maxPositions.toIntOrNull() ?: 5
                    ))
                },
                colors = ButtonDefaults.buttonColors(containerColor = LongGreen)
            ) {
                Text("Start Copying")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FiltersBottomSheet(
    onDismiss: () -> Unit
) {
    var minPnl by remember { mutableStateOf("") }
    var minWinRate by remember { mutableStateOf("") }
    var minFollowers by remember { mutableStateOf("") }
    
    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp)
        ) {
            Text(
                "Filter Traders",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            OutlinedTextField(
                value = minPnl,
                onValueChange = { minPnl = it },
                label = { Text("Min PnL (%)") },
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            OutlinedTextField(
                value = minWinRate,
                onValueChange = { minWinRate = it },
                label = { Text("Min Win Rate (%)") },
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            OutlinedTextField(
                value = minFollowers,
                onValueChange = { minFollowers = it },
                label = { Text("Min Followers") },
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedButton(
                    onClick = {
                        minPnl = ""
                        minWinRate = ""
                        minFollowers = ""
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Reset")
                }
                Button(
                    onClick = onDismiss,
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Apply")
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

private fun generateMockTraders(): List<Trader> {
    return listOf(
        Trader("1", "CryptoWhale", "", 156.8, 15680.0, 72.5, 12450, 892, 12.3, 2.45, 5_400_000.0, true, true, 1, listOf("BTC", "ETH", "Scalper")),
        Trader("2", "AlphaTrader", "", 98.5, 9850.0, 68.2, 8920, 1245, 15.8, 1.89, 2_800_000.0, false, true, 2, listOf("Futures", "Swing")),
        Trader("3", "DeFiMaster", "", 87.3, 8730.0, 65.0, 6540, 678, 18.5, 1.56, 1_200_000.0, true, false, 3, listOf("DeFi", "Long-term")),
        Trader("4", "SwingKing", "", 75.2, 7520.0, 71.8, 4320, 456, 10.2, 2.12, 890_000.0, false, true, 4, listOf("Swing", "BTC")),
        Trader("5", "ScalpMaster", "", 62.4, 6240.0, 78.5, 3210, 2340, 8.5, 1.78, 450_000.0, false, false, 5, listOf("Scalper", "ETH")),
        Trader("6", "TrendFollower", "", 54.8, 5480.0, 62.3, 2890, 567, 22.1, 1.34, 320_000.0, false, true, 6, listOf("Trend", "Multi-coin")),
        Trader("7", "RiskManager", "", 45.6, 4560.0, 82.1, 1980, 234, 5.8, 2.89, 180_000.0, false, false, 7, listOf("Conservative", "Low Risk")),
        Trader("8", "MomentumPro", "", 38.2, 3820.0, 58.9, 1560, 789, 28.4, 1.12, 95_000.0, false, true, 8, listOf("Momentum", "High Risk"))
    )
}

private fun formatCompact(value: Double): String {
    return when {
        value >= 1_000_000 -> String.format("%.1fM", value / 1_000_000)
        value >= 1_000 -> String.format("%.0fK", value / 1_000)
        else -> String.format("%.0f", value)
    }
}
