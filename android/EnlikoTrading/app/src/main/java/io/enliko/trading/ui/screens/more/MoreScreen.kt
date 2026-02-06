package io.enliko.trading.ui.screens.more

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed

data class MoreMenuItem(
    val id: String,
    val title: String,
    val subtitle: String,
    val icon: ImageVector,
    val color: Color,
    val badge: String? = null
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MoreScreen(
    onNavigateBack: () -> Unit = {},
    onNavigateTo: (String) -> Unit = {}
) {
    val menuItems = remember {
        listOf(
            MoreMenuItem(
                id = "wallet",
                title = "Wallet",
                subtitle = "Assets & Balances",
                icon = Icons.Filled.AccountBalanceWallet,
                color = Color(0xFF3B82F6)
            ),
            MoreMenuItem(
                id = "alerts",
                title = "Price Alerts",
                subtitle = "Set notifications",
                icon = Icons.Filled.NotificationsActive,
                color = Color(0xFFF59E0B),
                badge = "5"
            ),
            MoreMenuItem(
                id = "history",
                title = "Trade History",
                subtitle = "Orders & PnL",
                icon = Icons.Filled.History,
                color = Color(0xFF8B5CF6)
            ),
            MoreMenuItem(
                id = "hyperliquid",
                title = "HyperLiquid",
                subtitle = "DEX Trading",
                icon = Icons.Filled.Bolt,
                color = Color(0xFF06B6D4)
            ),
            MoreMenuItem(
                id = "market",
                title = "Market Hub",
                subtitle = "Overview & News",
                icon = Icons.Filled.Hub,
                color = Color(0xFF10B981)
            ),
            MoreMenuItem(
                id = "orderbook",
                title = "Orderbook",
                subtitle = "Depth Analysis",
                icon = Icons.Filled.ViewList,
                color = Color(0xFFEF4444)
            ),
            MoreMenuItem(
                id = "stats",
                title = "Statistics",
                subtitle = "Performance",
                icon = Icons.Filled.Analytics,
                color = Color(0xFF6366F1)
            ),
            MoreMenuItem(
                id = "ai",
                title = "AI Assistant",
                subtitle = "Trading Copilot",
                icon = Icons.Filled.Psychology,
                color = Color(0xFFEC4899),
                badge = "NEW"
            ),
            MoreMenuItem(
                id = "strategies",
                title = "Strategies",
                subtitle = "Auto Trading",
                icon = Icons.Filled.AutoGraph,
                color = LongGreen
            ),
            MoreMenuItem(
                id = "spot",
                title = "Spot Trading",
                subtitle = "Buy & Sell",
                icon = Icons.Filled.SwapHoriz,
                color = Color(0xFF14B8A6)
            ),
            MoreMenuItem(
                id = "copy",
                title = "Copy Trading",
                subtitle = "Follow Traders",
                icon = Icons.Filled.Groups,
                color = Color(0xFFF97316),
                badge = "SOON"
            ),
            MoreMenuItem(
                id = "staking",
                title = "Staking",
                subtitle = "Earn Rewards",
                icon = Icons.Filled.Savings,
                color = Color(0xFFA855F7),
                badge = "SOON"
            )
        )
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        "More Features",
                        fontWeight = FontWeight.Bold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(menuItems) { item ->
                MoreMenuCard(
                    item = item,
                    onClick = {
                        when (item.id) {
                            "wallet" -> onNavigateTo("wallet")
                            "alerts" -> onNavigateTo("alerts")
                            "history" -> onNavigateTo("history")
                            "hyperliquid" -> onNavigateTo("hyperliquid")
                            "market" -> onNavigateTo("market_hub")
                            "orderbook" -> onNavigateTo("orderbook")
                            "stats" -> onNavigateTo("stats")
                            "ai" -> onNavigateTo("ai")
                            "strategies" -> onNavigateTo("strategies")
                            "spot" -> onNavigateTo("spot")
                            "copy" -> onNavigateTo("copy_trading")
                            "staking" -> { /* Coming soon */ }
                        }
                    }
                )
            }
        }
    }
}

@Composable
private fun MoreMenuCard(
    item: MoreMenuItem,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(120.dp)
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            // Badge
            item.badge?.let { badge ->
                Surface(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(8.dp),
                    shape = RoundedCornerShape(4.dp),
                    color = when (badge) {
                        "NEW" -> LongGreen
                        "SOON" -> Color.Gray
                        else -> ShortRed
                    }
                ) {
                    Text(
                        text = badge,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(item.color.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = item.icon,
                        contentDescription = item.title,
                        tint = item.color,
                        modifier = Modifier.size(24.dp)
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = item.title,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center
                )
                
                Text(
                    text = item.subtitle,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}
