package io.enliko.trading.ui.screens.hyperliquid

import androidx.compose.animation.*
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
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import java.text.NumberFormat
import java.util.*

// MARK: - Data Models
data class HLVault(
    val name: String,
    val leader: String,
    val apy: Double,
    val tvl: Double,
    val pnl30d: Double,
    val followers: Int,
    val isFollowing: Boolean = false
)

data class HLTransfer(
    val type: String, // deposit, withdraw
    val amount: Double,
    val timestamp: Long,
    val status: String,
    val txHash: String?
)

data class HLPoints(
    val totalPoints: Long,
    val rank: Int,
    val weeklyPoints: Long,
    val referralPoints: Long,
    val tradingPoints: Long
)

enum class HLTab { VAULTS, TRANSFERS, POINTS, SETTINGS }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HyperLiquidScreen(
    onNavigateBack: () -> Unit = {}
) {
    var selectedTab by remember { mutableStateOf(HLTab.VAULTS) }
    var isLoading by remember { mutableStateOf(true) }
    
    var vaults by remember { mutableStateOf<List<HLVault>>(emptyList()) }
    var transfers by remember { mutableStateOf<List<HLTransfer>>(emptyList()) }
    var points by remember { mutableStateOf<HLPoints?>(null) }
    var isTestnet by remember { mutableStateOf(false) }
    var walletAddress by remember { mutableStateOf<String?>(null) }
    
    // Mock data
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(500)
        vaults = listOf(
            HLVault("Alpha Momentum", "0x1234...abcd", 85.5, 15_000_000.0, 12.5, 1234, true),
            HLVault("BTC Macro", "0x5678...efgh", 45.2, 8_500_000.0, 8.2, 567),
            HLVault("ETH DeFi", "0x9abc...ijkl", 120.8, 25_000_000.0, 18.7, 2345),
            HLVault("Stable Yield", "0xdef0...mnop", 15.5, 50_000_000.0, 1.2, 5678),
            HLVault("High Vol", "0x1111...2222", 250.3, 3_000_000.0, -5.2, 234)
        )
        transfers = listOf(
            HLTransfer("deposit", 5000.0, System.currentTimeMillis() - 86400000, "completed", "0xabc123..."),
            HLTransfer("withdraw", 1000.0, System.currentTimeMillis() - 172800000, "completed", "0xdef456..."),
            HLTransfer("deposit", 10000.0, System.currentTimeMillis() - 259200000, "completed", "0xghi789...")
        )
        points = HLPoints(
            totalPoints = 125_000,
            rank = 4521,
            weeklyPoints = 15_000,
            referralPoints = 25_000,
            tradingPoints = 85_000
        )
        walletAddress = "0x742d35Cc6634C0532925a3b844Bc9e7595f8F0f1"
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("HyperLiquid")
                        if (isTestnet) {
                            Badge(
                                containerColor = MaterialTheme.colorScheme.tertiary
                            ) {
                                Text("TESTNET")
                            }
                        }
                    }
                },
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Wallet Address Card
            walletAddress?.let { address ->
                WalletAddressCard(address = address)
            }
            
            // Tab Selector
            ScrollableTabRow(
                selectedTabIndex = selectedTab.ordinal,
                edgePadding = 16.dp
            ) {
                HLTab.entries.forEach { tab ->
                    Tab(
                        selected = selectedTab == tab,
                        onClick = { selectedTab = tab },
                        text = {
                            Text(
                                text = tab.name.lowercase().replaceFirstChar { it.uppercase() },
                                fontWeight = if (selectedTab == tab) FontWeight.Bold else FontWeight.Normal
                            )
                        },
                        icon = {
                            Icon(
                                imageVector = when (tab) {
                                    HLTab.VAULTS -> Icons.Default.AccountBalance
                                    HLTab.TRANSFERS -> Icons.Default.SwapHoriz
                                    HLTab.POINTS -> Icons.Default.Stars
                                    HLTab.SETTINGS -> Icons.Default.Settings
                                },
                                contentDescription = null
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
                    label = "hl_tab"
                ) { tab ->
                    when (tab) {
                        HLTab.VAULTS -> VaultsTab(vaults) { vault ->
                            vaults = vaults.map {
                                if (it.name == vault.name) it.copy(isFollowing = !it.isFollowing)
                                else it
                            }
                        }
                        HLTab.TRANSFERS -> TransfersTab(transfers)
                        HLTab.POINTS -> points?.let { PointsTab(it) }
                        HLTab.SETTINGS -> HLSettingsTab(
                            isTestnet = isTestnet,
                            onTestnetChange = { isTestnet = it },
                            walletAddress = walletAddress
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun WalletAddressCard(address: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
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
                    text = "Connected Wallet",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                )
                Text(
                    text = "${address.take(6)}...${address.takeLast(4)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            }
            
            IconButton(onClick = { /* Copy */ }) {
                Icon(Icons.Default.ContentCopy, contentDescription = "Copy")
            }
        }
    }
}

@Composable
private fun VaultsTab(
    vaults: List<HLVault>,
    onFollowToggle: (HLVault) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text(
                text = "Top Performing Vaults",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }
        
        items(vaults, key = { it.name }) { vault ->
            VaultCard(vault = vault, onFollowToggle = { onFollowToggle(vault) })
        }
    }
}

@Composable
private fun VaultCard(
    vault: HLVault,
    onFollowToggle: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = vault.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = vault.leader,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Button(
                    onClick = onFollowToggle,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (vault.isFollowing) 
                            MaterialTheme.colorScheme.secondaryContainer 
                        else 
                            MaterialTheme.colorScheme.primary
                    )
                ) {
                    Icon(
                        imageVector = if (vault.isFollowing) Icons.Default.Check else Icons.Default.Add,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(if (vault.isFollowing) "Following" else "Follow")
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                VaultStat(
                    label = "APY",
                    value = "${String.format("%.1f", vault.apy)}%",
                    color = if (vault.apy >= 0) LongGreen else ShortRed
                )
                VaultStat(
                    label = "TVL",
                    value = formatCompactNumber(vault.tvl)
                )
                VaultStat(
                    label = "30d PnL",
                    value = "${if (vault.pnl30d >= 0) "+" else ""}${String.format("%.1f", vault.pnl30d)}%",
                    color = if (vault.pnl30d >= 0) LongGreen else ShortRed
                )
                VaultStat(
                    label = "Followers",
                    value = formatCompactNumber(vault.followers.toDouble())
                )
            }
        }
    }
}

@Composable
private fun VaultStat(
    label: String,
    value: String,
    color: Color = MaterialTheme.colorScheme.onSurface
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold,
            color = color
        )
    }
}

@Composable
private fun TransfersTab(transfers: List<HLTransfer>) {
    if (transfers.isEmpty()) {
        EmptyStateView(
            icon = Icons.Default.SwapHoriz,
            title = "No Transfers",
            subtitle = "Your transfer history will appear here"
        )
    } else {
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(transfers) { transfer ->
                TransferCard(transfer)
            }
        }
    }
}

@Composable
private fun TransferCard(transfer: HLTransfer) {
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
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(
                            if (transfer.type == "deposit") 
                                LongGreen.copy(alpha = 0.2f) 
                            else 
                                ShortRed.copy(alpha = 0.2f)
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = if (transfer.type == "deposit") 
                            Icons.Default.ArrowDownward 
                        else 
                            Icons.Default.ArrowUpward,
                        contentDescription = null,
                        tint = if (transfer.type == "deposit") LongGreen else ShortRed
                    )
                }
                
                Column {
                    Text(
                        text = transfer.type.replaceFirstChar { it.uppercase() },
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = formatTimestamp(transfer.timestamp),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "${if (transfer.type == "deposit") "+" else "-"}${formatCurrency(transfer.amount)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (transfer.type == "deposit") LongGreen else ShortRed
                )
                Text(
                    text = transfer.status.uppercase(),
                    style = MaterialTheme.typography.bodySmall,
                    color = if (transfer.status == "completed") LongGreen else MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun PointsTab(points: HLPoints) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Total Points Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        imageVector = Icons.Default.Stars,
                        contentDescription = null,
                        modifier = Modifier.size(48.dp),
                        tint = Color(0xFFFFD700)
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    Text(
                        text = formatNumber(points.totalPoints),
                        style = MaterialTheme.typography.displaySmall,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Text(
                        text = "Total Points",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surface
                        )
                    ) {
                        Text(
                            text = "Rank #${points.rank}",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                        )
                    }
                }
            }
        }
        
        // Breakdown
        item {
            Text(
                text = "Points Breakdown",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }
        
        item {
            PointsBreakdownCard(
                icon = Icons.Default.ShowChart,
                title = "Trading Points",
                points = points.tradingPoints,
                description = "Earned from trading volume"
            )
        }
        
        item {
            PointsBreakdownCard(
                icon = Icons.Default.Group,
                title = "Referral Points",
                points = points.referralPoints,
                description = "Earned from referrals"
            )
        }
        
        item {
            PointsBreakdownCard(
                icon = Icons.Default.CalendarToday,
                title = "This Week",
                points = points.weeklyPoints,
                description = "Points earned this week"
            )
        }
    }
}

@Composable
private fun PointsBreakdownCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    points: Long,
    description: String
) {
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
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(24.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Column {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = description,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Text(
                text = formatNumber(points),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
private fun HLSettingsTab(
    isTestnet: Boolean,
    onTestnetChange: (Boolean) -> Unit,
    walletAddress: String?
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "Network Settings",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }
        
        item {
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
                            text = "Testnet Mode",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Use testnet for testing",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Switch(
                        checked = isTestnet,
                        onCheckedChange = onTestnetChange
                    )
                }
            }
        }
        
        item {
            Text(
                text = "Wallet",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }
        
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Connected Address",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = walletAddress ?: "Not connected",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Button(
                        onClick = { /* Disconnect */ },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = ShortRed
                        )
                    ) {
                        Icon(Icons.Default.LinkOff, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Disconnect Wallet")
                    }
                }
            }
        }
    }
}

@Composable
private fun EmptyStateView(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    subtitle: String
) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
            )
        }
    }
}

private fun formatCurrency(value: Double): String {
    return NumberFormat.getCurrencyInstance(Locale.US).format(value)
}

private fun formatNumber(value: Long): String {
    return NumberFormat.getNumberInstance(Locale.US).format(value)
}

private fun formatCompactNumber(value: Double): String {
    return when {
        value >= 1_000_000_000 -> String.format("%.1fB", value / 1_000_000_000)
        value >= 1_000_000 -> String.format("%.1fM", value / 1_000_000)
        value >= 1_000 -> String.format("%.1fK", value / 1_000)
        else -> String.format("%.0f", value)
    }
}

private fun formatTimestamp(timestamp: Long): String {
    val sdf = java.text.SimpleDateFormat("MMM d, HH:mm", Locale.getDefault())
    return sdf.format(Date(timestamp))
}
