package io.lyxen.trading.ui.screens.portfolio

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import io.lyxen.trading.data.models.Balance
import io.lyxen.trading.data.models.Position
import io.lyxen.trading.ui.components.AccountTypeSelector
import io.lyxen.trading.ui.theme.LongGreen
import io.lyxen.trading.ui.theme.ShortRed
import io.lyxen.trading.util.LocalStrings
import java.text.NumberFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PortfolioScreen(
    viewModel: PortfolioViewModel = hiltViewModel()
) {
    val strings = LocalStrings.current
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(strings.portfolio) },
                actions = {
                    IconButton(onClick = { viewModel.refresh() }) {
                        Icon(Icons.Default.Refresh, contentDescription = strings.refresh)
                    }
                }
            )
        }
    ) { padding ->
        if (uiState.isLoading && uiState.balance == null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Account Type Selector
                item {
                    AccountTypeSelector(
                        exchange = uiState.exchange,
                        selectedAccountType = uiState.accountType,
                        onAccountTypeSelected = { viewModel.switchAccountType(it) }
                    )
                }
                
                // Balance Card
                item {
                    uiState.balance?.let { balance ->
                        BalanceCard(balance = balance, strings = strings)
                    }
                }
                
                // Stats Card
                item {
                    uiState.stats?.let { stats ->
                        StatsCard(stats = stats, strings = strings)
                    }
                }
                
                // Positions Header
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "${strings.openPositions} (${uiState.positions.size})",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        
                        if (uiState.positions.isNotEmpty()) {
                            TextButton(onClick = { viewModel.closeAllPositions() }) {
                                Text(strings.closeAll, color = ShortRed)
                            }
                        }
                    }
                }
                
                // Positions
                if (uiState.positions.isEmpty()) {
                    item {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surfaceVariant
                            )
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(32.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = strings.noPositions,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }
                } else {
                    items(uiState.positions, key = { "${it.symbol}_${it.side}" }) { position ->
                        PositionCard(
                            position = position,
                            strings = strings,
                            onClose = { viewModel.closePosition(position.symbol, position.side) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun BalanceCard(balance: Balance, strings: io.lyxen.trading.util.Strings) {
    val formatter = remember { 
        NumberFormat.getCurrencyInstance(Locale.US).apply {
            minimumFractionDigits = 2
            maximumFractionDigits = 2
        }
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = strings.totalEquity,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Text(
                text = formatter.format(balance.totalEquity),
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = strings.availableBalance,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = formatter.format(balance.availableBalance),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Medium
                    )
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = strings.unrealizedPnl,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    val pnlColor = when {
                        balance.unrealizedPnl > 0 -> LongGreen
                        balance.unrealizedPnl < 0 -> ShortRed
                        else -> MaterialTheme.colorScheme.onSurface
                    }
                    Text(
                        text = "${if (balance.unrealizedPnl >= 0) "+" else ""}${formatter.format(balance.unrealizedPnl)}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Medium,
                        color = pnlColor
                    )
                }
            }
        }
    }
}

@Composable
private fun StatsCard(stats: io.lyxen.trading.data.models.TradeStats, strings: io.lyxen.trading.util.Strings) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            StatItem(strings.totalTrades, stats.total.toString())
            StatItem(strings.winRate, "${String.format("%.1f", stats.winrate)}%")
            StatItem(strings.wins, stats.wins.toString(), LongGreen)
            StatItem(strings.losses, stats.losses.toString(), ShortRed)
        }
    }
}

@Composable
private fun StatItem(label: String, value: String, color: Color? = null) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = color ?: MaterialTheme.colorScheme.onSurface
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun PositionCard(
    position: Position,
    strings: io.lyxen.trading.util.Strings,
    onClose: () -> Unit
) {
    val isLong = position.side.equals("Buy", ignoreCase = true) || 
                 position.side.equals("Long", ignoreCase = true)
    val sideColor by animateColorAsState(if (isLong) LongGreen else ShortRed, label = "sideColor")
    
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(4.dp))
                            .background(sideColor.copy(alpha = 0.2f))
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = if (isLong) strings.long else strings.short,
                            style = MaterialTheme.typography.labelMedium,
                            color = sideColor,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    
                    Spacer(modifier = Modifier.width(12.dp))
                    
                    Text(
                        text = position.symbol.removeSuffix("USDT"),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    position.leverage?.let { leverage ->
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "${leverage.toInt()}x",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                IconButton(
                    onClick = onClose,
                    colors = IconButtonDefaults.iconButtonColors(
                        contentColor = ShortRed
                    )
                ) {
                    Icon(Icons.Default.Close, contentDescription = strings.close)
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = strings.entry,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = String.format("%.4f", position.entryPrice),
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = strings.size,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = String.format("%.4f", position.size),
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = strings.pnl,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    val pnl = position.unrealizedPnl ?: 0.0
                    val pnlPct = position.pnlPercent ?: 0.0
                    val pnlColor = when {
                        pnl > 0 -> LongGreen
                        pnl < 0 -> ShortRed
                        else -> MaterialTheme.colorScheme.onSurface
                    }
                    Text(
                        text = "${if (pnl >= 0) "+" else ""}${String.format("%.2f", pnl)} (${String.format("%.2f", pnlPct)}%)",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium,
                        color = pnlColor
                    )
                }
            }
        }
    }
}
