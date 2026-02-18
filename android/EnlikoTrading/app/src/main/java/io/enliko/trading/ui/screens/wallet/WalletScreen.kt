package io.enliko.trading.ui.screens.wallet

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import io.enliko.trading.util.LocalStrings
import java.text.NumberFormat
import java.util.Locale

// MARK: - Data Models
data class WalletAsset(
    val coin: String,
    val balance: Double,
    val availableBalance: Double,
    val lockedBalance: Double,
    val usdValue: Double,
    val change24h: Double
)

enum class WalletTab { SPOT, FUTURES, MARGIN }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WalletScreen(
    onNavigateBack: () -> Unit = {},
    onTransfer: () -> Unit = {},
    onDeposit: () -> Unit = {},
    onWithdraw: () -> Unit = {}
) {
    val strings = LocalStrings.current
    var selectedTab by remember { mutableStateOf(WalletTab.FUTURES) }
    var hideSmallBalances by remember { mutableStateOf(true) }
    var isLoading by remember { mutableStateOf(true) }
    var totalEquity by remember { mutableDoubleStateOf(0.0) }
    var totalPnL24h by remember { mutableDoubleStateOf(0.0) }
    var assets by remember { mutableStateOf<List<WalletAsset>>(emptyList()) }
    
    // Mock data loading
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(500)
        totalEquity = 15234.56
        totalPnL24h = 523.45
        assets = listOf(
            WalletAsset("USDT", 10000.0, 7000.0, 3000.0, 10000.0, 0.0),
            WalletAsset("BTC", 0.05, 0.05, 0.0, 4925.0, 2.5),
            WalletAsset("ETH", 1.2, 1.2, 0.0, 3840.0, 1.8),
            WalletAsset("SOL", 25.0, 20.0, 5.0, 4500.0, 5.2)
        )
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(strings.wallet) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { /* Refresh */ }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        }
    ) { padding ->
        if (isLoading) {
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
                // Balance Header Card
                item {
                    WalletBalanceHeader(
                        totalEquity = totalEquity,
                        totalPnL24h = totalPnL24h,
                        onDeposit = onDeposit,
                        onWithdraw = onWithdraw,
                        onTransfer = onTransfer
                    )
                }
                
                // Tab Selector
                item {
                    WalletTabSelector(
                        selectedTab = selectedTab,
                        onTabSelected = { selectedTab = it }
                    )
                }
                
                // Options Bar
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = strings.assets,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(
                                text = strings.hideSmall,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Switch(
                                checked = hideSmallBalances,
                                onCheckedChange = { hideSmallBalances = it },
                                modifier = Modifier.height(24.dp)
                            )
                        }
                    }
                }
                
                // Assets List
                val filteredAssets = if (hideSmallBalances) {
                    assets.filter { it.usdValue >= 1.0 }
                } else {
                    assets
                }
                
                items(filteredAssets, key = { it.coin }) { asset ->
                    AssetRow(asset = asset)
                }
            }
        }
    }
}

@Composable
private fun WalletBalanceHeader(
    totalEquity: Double,
    totalPnL24h: Double,
    onDeposit: () -> Unit,
    onWithdraw: () -> Unit,
    onTransfer: () -> Unit
) {
    val strings = LocalStrings.current
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = strings.totalBalance,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = formatCurrency(totalEquity),
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = if (totalPnL24h >= 0) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                    contentDescription = null,
                    tint = if (totalPnL24h >= 0) LongGreen else ShortRed,
                    modifier = Modifier.size(16.dp)
                )
                Text(
                    text = "${if (totalPnL24h >= 0) "+" else ""}${formatCurrency(totalPnL24h)} (24h)",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (totalPnL24h >= 0) LongGreen else ShortRed
                )
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            
            // Quick Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                QuickActionButton(
                    icon = Icons.Default.Add,
                    label = "Deposit",
                    onClick = onDeposit
                )
                QuickActionButton(
                    icon = Icons.Default.Remove,
                    label = "Withdraw",
                    onClick = onWithdraw
                )
                QuickActionButton(
                    icon = Icons.Default.SwapHoriz,
                    label = "Transfer",
                    onClick = onTransfer
                )
            }
        }
    }
}

@Composable
private fun QuickActionButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    onClick: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.clickable(onClick = onClick)
    ) {
        Box(
            modifier = Modifier
                .size(48.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.primary),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = label,
                tint = MaterialTheme.colorScheme.onPrimary
            )
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onPrimaryContainer
        )
    }
}

@Composable
private fun WalletTabSelector(
    selectedTab: WalletTab,
    onTabSelected: (WalletTab) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        WalletTab.entries.forEach { tab ->
            val isSelected = tab == selectedTab
            val backgroundColor by animateColorAsState(
                if (isSelected) MaterialTheme.colorScheme.primary else Color.Transparent,
                label = "tab_bg"
            )
            val contentColor by animateColorAsState(
                if (isSelected) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant,
                label = "tab_content"
            )
            
            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(12.dp))
                    .background(backgroundColor)
                    .clickable { onTabSelected(tab) }
                    .padding(vertical = 12.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = tab.name,
                    style = MaterialTheme.typography.labelLarge,
                    color = contentColor,
                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                )
            }
        }
    }
}

@Composable
private fun AssetRow(asset: WalletAsset) {
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
            // Coin Info
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Coin Icon Placeholder
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = asset.coin.take(1),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                }
                
                Column {
                    Text(
                        text = asset.coin,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Available: ${formatNumber(asset.availableBalance)}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            // Value
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = formatCurrency(asset.usdValue),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                if (asset.change24h != 0.0) {
                    Text(
                        text = "${if (asset.change24h >= 0) "+" else ""}${String.format("%.2f", asset.change24h)}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = if (asset.change24h >= 0) LongGreen else ShortRed
                    )
                }
            }
        }
    }
}

private fun formatCurrency(value: Double): String {
    return NumberFormat.getCurrencyInstance(Locale.US).format(value)
}

private fun formatNumber(value: Double): String {
    return if (value >= 1000) {
        String.format("%.2f", value)
    } else if (value >= 1) {
        String.format("%.4f", value)
    } else {
        String.format("%.8f", value)
    }
}
