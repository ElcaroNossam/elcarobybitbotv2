package io.enliko.trading.ui.screens.social

import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.util.LocalStrings
import java.text.DecimalFormat

// Models
data class TopTrader(
    val id: String,
    val username: String,
    val avatar: String? = null,
    val rank: Int,
    val roi30d: Double,
    val winRate: Double,
    val totalTrades: Int,
    val followers: Int,
    val maxDrawdown: Double,
    val strategies: List<String>,
    val isVerified: Boolean
) {
    val displayName: String get() = username.ifEmpty { "Trader #$rank" }
}

data class CopySettings(
    val traderId: String,
    val copyPercentage: Double,
    val maxPositionSize: Double,
    val copyType: CopyType,
    val isActive: Boolean
)

enum class CopyType { PROPORTIONAL, FIXED }

enum class SocialTimeframe(val label: String) {
    WEEK("7D"),
    MONTH("30D"),
    QUARTER("90D"),
    ALL("All")
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SocialTradingScreen(
    viewModel: SocialTradingViewModel = hiltViewModel(),
    onBack: () -> Unit = {},
    onTraderClick: (String) -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsState()
    val strings = LocalStrings.current
    var selectedTab by remember { mutableIntStateOf(0) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Social Trading") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.refresh() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Tabs
            TabRow(selectedTabIndex = selectedTab) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text("Leaderboard") },
                    icon = { Icon(Icons.Outlined.Leaderboard, null) }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Following") },
                    icon = { Icon(Icons.Outlined.Favorite, null) }
                )
            }
            
            // Timeframe Filter
            LazyRow(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(SocialTimeframe.entries) { timeframe ->
                    FilterChip(
                        selected = uiState.selectedTimeframe == timeframe,
                        onClick = { viewModel.setTimeframe(timeframe) },
                        label = { Text(timeframe.label) }
                    )
                }
            }
            
            when {
                uiState.isLoading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                selectedTab == 0 -> {
                    // Leaderboard
                    LeaderboardContent(
                        traders = uiState.topTraders,
                        onTraderClick = onTraderClick,
                        onFollow = { viewModel.followTrader(it) }
                    )
                }
                else -> {
                    // Following
                    FollowingContent(
                        traders = uiState.followedTraders,
                        onTraderClick = onTraderClick,
                        onUnfollow = { viewModel.unfollowTrader(it) },
                        onConfigureCopy = { viewModel.configureCopy(it) }
                    )
                }
            }
        }
    }
}

@Composable
private fun LeaderboardContent(
    traders: List<TopTrader>,
    onTraderClick: (String) -> Unit,
    onFollow: (String) -> Unit
) {
    if (traders.isEmpty()) {
        EmptyState(
            icon = Icons.Outlined.Leaderboard,
            title = "No traders found",
            subtitle = "Check back later for top performers"
        )
    } else {
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(traders) { trader ->
                TraderCard(
                    trader = trader,
                    onClick = { onTraderClick(trader.id) },
                    onFollow = { onFollow(trader.id) },
                    showFollowButton = true
                )
            }
        }
    }
}

@Composable
private fun FollowingContent(
    traders: List<TopTrader>,
    onTraderClick: (String) -> Unit,
    onUnfollow: (String) -> Unit,
    onConfigureCopy: (String) -> Unit
) {
    if (traders.isEmpty()) {
        EmptyState(
            icon = Icons.Outlined.Favorite,
            title = "No traders followed",
            subtitle = "Follow top traders to start copy trading"
        )
    } else {
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(traders) { trader ->
                FollowedTraderCard(
                    trader = trader,
                    onClick = { onTraderClick(trader.id) },
                    onUnfollow = { onUnfollow(trader.id) },
                    onConfigure = { onConfigureCopy(trader.id) }
                )
            }
        }
    }
}

@Composable
private fun TraderCard(
    trader: TopTrader,
    onClick: () -> Unit,
    onFollow: () -> Unit,
    showFollowButton: Boolean
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Rank Badge
                RankBadge(rank = trader.rank)
                
                // Avatar
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primaryContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = trader.displayName.take(2).uppercase(),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                
                // Name & Stats
                Column(modifier = Modifier.weight(1f)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Text(
                            text = trader.displayName,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        if (trader.isVerified) {
                            Icon(
                                imageVector = Icons.Filled.Verified,
                                contentDescription = "Verified",
                                tint = Color(0xFF1DA1F2),
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                    Text(
                        text = "${trader.followers.formatNumber()} followers • ${trader.totalTrades} trades",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // Follow button
                if (showFollowButton) {
                    FilledTonalButton(onClick = onFollow) {
                        Text("Follow")
                    }
                }
            }
            
            HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp))
            
            // Performance metrics
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MetricItem(
                    label = "ROI (30d)",
                    value = "${trader.roi30d.formatPercent()}%",
                    isPositive = trader.roi30d >= 0
                )
                MetricItem(
                    label = "Win Rate",
                    value = "${trader.winRate.formatPercent()}%",
                    isPositive = trader.winRate >= 50
                )
                MetricItem(
                    label = "Max DD",
                    value = "${trader.maxDrawdown.formatPercent()}%",
                    isPositive = false
                )
            }
            
            // Strategies
            LazyRow(
                modifier = Modifier.padding(top = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                items(trader.strategies) { strategy ->
                    SuggestionChip(
                        onClick = {},
                        label = { Text(strategy, style = MaterialTheme.typography.labelSmall) }
                    )
                }
            }
        }
    }
}

@Composable
private fun FollowedTraderCard(
    trader: TopTrader,
    onClick: () -> Unit,
    onUnfollow: () -> Unit,
    onConfigure: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primaryContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = trader.displayName.take(2).uppercase(),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = trader.displayName,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    Text(
                        text = "+${trader.roi30d.formatPercent()}% ROI (30d)",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF4CAF50)
                    )
                }
            }
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = onConfigure,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Default.Settings, null, Modifier.size(18.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Configure")
                }
                OutlinedButton(
                    onClick = onUnfollow,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Icon(Icons.Default.Close, null, Modifier.size(18.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Unfollow")
                }
            }
        }
    }
}

@Composable
private fun RankBadge(rank: Int) {
    val (color, icon) = when (rank) {
        1 -> Color(0xFFFFD700) to "🥇"
        2 -> Color(0xFFC0C0C0) to "🥈"
        3 -> Color(0xFFCD7F32) to "🥉"
        else -> MaterialTheme.colorScheme.surfaceVariant to "#$rank"
    }
    
    Box(
        modifier = Modifier
            .size(32.dp)
            .clip(CircleShape)
            .background(color.copy(alpha = 0.2f)),
        contentAlignment = Alignment.Center
    ) {
        if (rank <= 3) {
            Text(text = icon, style = MaterialTheme.typography.titleMedium)
        } else {
            Text(
                text = "#$rank",
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
private fun MetricItem(
    label: String,
    value: String,
    isPositive: Boolean
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = if (isPositive) Color(0xFF4CAF50) else Color(0xFFF44336)
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun EmptyState(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    subtitle: String
) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium
            )
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

// Extensions
private fun Int.formatNumber(): String {
    return when {
        this >= 1_000_000 -> "${(this / 1_000_000.0).formatPercent()}M"
        this >= 1_000 -> "${(this / 1_000.0).formatPercent()}K"
        else -> this.toString()
    }
}

private fun Double.formatPercent(): String {
    return DecimalFormat("#,##0.0").format(this)
}
