package io.enliko.trading.ui.screens.admin

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*

/**
 * AdminScreen - Matching iOS AdminView.swift
 * Admin panel for managing users, system settings, and monitoring
 */

data class AdminUser(
    val id: Long,
    val username: String,
    val email: String?,
    val isAllowed: Boolean,
    val isBanned: Boolean,
    val exchange: String,
    val lastActive: String,
    val totalTrades: Int,
    val totalPnl: Double
)

data class SystemMetric(
    val name: String,
    val value: String,
    val icon: ImageVector,
    val color: Color
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdminScreen(
    onBack: () -> Unit = {}
) {
    var selectedTab by remember { mutableStateOf(0) }
    val tabs = listOf("Overview", "Users", "System", "Logs")
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.AdminPanelSettings,
                            contentDescription = null,
                            tint = EnlikoPrimary
                        )
                        Text("Admin Panel")
                    }
                },
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Tabs
            TabRow(
                selectedTabIndex = selectedTab,
                containerColor = EnlikoCard,
                contentColor = EnlikoPrimary
            ) {
                tabs.forEachIndexed { index, title ->
                    Tab(
                        selected = selectedTab == index,
                        onClick = { selectedTab = index },
                        text = { 
                            Text(
                                title,
                                fontWeight = if (selectedTab == index) FontWeight.Bold else FontWeight.Normal
                            )
                        }
                    )
                }
            }
            
            when (selectedTab) {
                0 -> OverviewTab()
                1 -> UsersTab()
                2 -> SystemTab()
                3 -> LogsTab()
            }
        }
    }
}

@Composable
private fun OverviewTab() {
    val metrics = remember {
        listOf(
            SystemMetric("Active Users", "1,247", Icons.Default.People, EnlikoGreen),
            SystemMetric("Total Trades", "45,892", Icons.Default.SwapVert, EnlikoPrimary),
            SystemMetric("Server Load", "34%", Icons.Default.Memory, EnlikoYellow),
            SystemMetric("API Latency", "45ms", Icons.Default.Speed, EnlikoGreen)
        )
    }
    
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Quick stats
        item {
            Text(
                text = "Quick Stats",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = EnlikoTextPrimary
            )
        }
        
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                metrics.take(2).forEach { metric ->
                    MetricCard(metric = metric, modifier = Modifier.weight(1f))
                }
            }
        }
        
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                metrics.drop(2).forEach { metric ->
                    MetricCard(metric = metric, modifier = Modifier.weight(1f))
                }
            }
        }
        
        // Recent activity
        item {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Recent Activity",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = EnlikoTextPrimary
            )
        }
        
        items(5) { index ->
            ActivityItem(
                action = when (index) {
                    0 -> "New user registered"
                    1 -> "Trade executed (BTC Long)"
                    2 -> "API key updated"
                    3 -> "Subscription activated"
                    else -> "Settings changed"
                },
                user = "user${1000 + index}",
                time = "${index + 1}m ago"
            )
        }
        
        // Quick actions
        item {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Quick Actions",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = EnlikoTextPrimary
            )
        }
        
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                QuickActionButton(
                    icon = Icons.Default.PersonAdd,
                    label = "Add User",
                    modifier = Modifier.weight(1f)
                )
                QuickActionButton(
                    icon = Icons.Default.Send,
                    label = "Broadcast",
                    modifier = Modifier.weight(1f)
                )
                QuickActionButton(
                    icon = Icons.Default.Refresh,
                    label = "Sync All",
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun UsersTab() {
    val users = remember {
        listOf(
            AdminUser(511692487, "ElcaroNossam", "admin@enliko.com", true, false, "bybit", "2m ago", 1523, 12500.50),
            AdminUser(1240338409, "User2", "user2@test.com", true, false, "hyperliquid", "15m ago", 856, 3200.25),
            AdminUser(995144364, "User3", null, true, false, "bybit", "1h ago", 432, -150.00),
            AdminUser(123456789, "NewUser", "new@test.com", false, false, "bybit", "5h ago", 0, 0.0),
            AdminUser(987654321, "BannedUser", null, false, true, "bybit", "2d ago", 12, -500.00)
        )
    }
    
    var searchQuery by remember { mutableStateOf("") }
    var showOnlyActive by remember { mutableStateOf(false) }
    
    Column {
        // Search and filter
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                placeholder = { Text("Search users...") },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                modifier = Modifier.weight(1f),
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = EnlikoPrimary,
                    unfocusedBorderColor = EnlikoBorder,
                    focusedContainerColor = EnlikoCard,
                    unfocusedContainerColor = EnlikoCard
                )
            )
            
            FilterChip(
                selected = showOnlyActive,
                onClick = { showOnlyActive = !showOnlyActive },
                label = { Text("Active") },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = EnlikoPrimary,
                    selectedLabelColor = Color.White
                )
            )
        }
        
        LazyColumn(
            contentPadding = PaddingValues(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val filteredUsers = users.filter { user ->
                (searchQuery.isEmpty() || 
                 user.username.contains(searchQuery, ignoreCase = true) ||
                 user.email?.contains(searchQuery, ignoreCase = true) == true) &&
                (!showOnlyActive || user.isAllowed)
            }
            
            items(filteredUsers, key = { it.id }) { user ->
                UserCard(user = user)
            }
        }
    }
}

@Composable
private fun SystemTab() {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            SystemSettingCard(
                title = "Database",
                items = listOf(
                    "Connection Pool" to "50/50 active",
                    "Queries/sec" to "127",
                    "Cache Hit Rate" to "94.5%"
                )
            )
        }
        
        item {
            SystemSettingCard(
                title = "API Status",
                items = listOf(
                    "Bybit API" to "✅ Connected",
                    "HyperLiquid API" to "✅ Connected",
                    "WebSocket" to "✅ Active"
                )
            )
        }
        
        item {
            SystemSettingCard(
                title = "Services",
                items = listOf(
                    "Bot Service" to "Running",
                    "WebApp Service" to "Running",
                    "Monitor Loop" to "Active"
                )
            )
        }
        
        item {
            SystemSettingCard(
                title = "Resources",
                items = listOf(
                    "Memory Usage" to "1.2 GB / 4 GB",
                    "CPU Usage" to "23%",
                    "Disk Space" to "45 GB free"
                )
            )
        }
    }
}

@Composable
private fun LogsTab() {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(20) { index ->
            ServerLogItem(
                level = when (index % 4) {
                    0 -> "INFO"
                    1 -> "WARN"
                    2 -> "ERROR"
                    else -> "DEBUG"
                },
                message = when (index % 4) {
                    0 -> "User 511692487 opened BTCUSDT long position"
                    1 -> "Rate limit approaching for API endpoint"
                    2 -> "Failed to fetch HyperLiquid balance"
                    else -> "WebSocket reconnection successful"
                },
                time = "${index + 1}s ago"
            )
        }
    }
}

@Composable
private fun MetricCard(
    metric: SystemMetric,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.Start
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(CircleShape)
                        .background(metric.color.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        metric.icon,
                        contentDescription = null,
                        tint = metric.color,
                        modifier = Modifier.size(18.dp)
                    )
                }
                Text(
                    text = metric.name,
                    style = MaterialTheme.typography.bodyMedium,
                    color = EnlikoTextSecondary
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = metric.value,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
        }
    }
}

@Composable
private fun ActivityItem(
    action: String,
    user: String,
    time: String
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = action,
                    style = MaterialTheme.typography.bodyMedium,
                    color = EnlikoTextPrimary
                )
                Text(
                    text = user,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextSecondary
                )
            }
            Text(
                text = time,
                style = MaterialTheme.typography.bodySmall,
                color = EnlikoTextSecondary
            )
        }
    }
}

@Composable
private fun QuickActionButton(
    icon: ImageVector,
    label: String,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = { },
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                icon,
                contentDescription = null,
                tint = EnlikoPrimary,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = EnlikoTextPrimary
            )
        }
    }
}

@Composable
private fun UserCard(user: AdminUser) {
    Card(
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
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
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Status indicator
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(
                            when {
                                user.isBanned -> EnlikoRed.copy(alpha = 0.2f)
                                user.isAllowed -> EnlikoGreen.copy(alpha = 0.2f)
                                else -> EnlikoYellow.copy(alpha = 0.2f)
                            }
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        when {
                            user.isBanned -> Icons.Default.Block
                            user.isAllowed -> Icons.Default.CheckCircle
                            else -> Icons.Default.HourglassEmpty
                        },
                        contentDescription = null,
                        tint = when {
                            user.isBanned -> EnlikoRed
                            user.isAllowed -> EnlikoGreen
                            else -> EnlikoYellow
                        },
                        modifier = Modifier.size(20.dp)
                    )
                }
                
                Column {
                    Text(
                        text = user.username,
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium,
                        color = EnlikoTextPrimary
                    )
                    Text(
                        text = user.email ?: "No email",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = user.exchange.uppercase(),
                            style = MaterialTheme.typography.labelSmall,
                            color = EnlikoPrimary
                        )
                        Text(
                            text = "•",
                            color = EnlikoTextSecondary
                        )
                        Text(
                            text = "${user.totalTrades} trades",
                            style = MaterialTheme.typography.labelSmall,
                            color = EnlikoTextSecondary
                        )
                    }
                }
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = if (user.totalPnl >= 0) "+$${String.format("%.2f", user.totalPnl)}" 
                           else "-$${String.format("%.2f", -user.totalPnl)}",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = if (user.totalPnl >= 0) EnlikoGreen else EnlikoRed
                )
                Text(
                    text = user.lastActive,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextSecondary
                )
            }
        }
    }
}

@Composable
private fun SystemSettingCard(
    title: String,
    items: List<Pair<String, String>>
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                color = EnlikoTextPrimary
            )
            Spacer(modifier = Modifier.height(12.dp))
            items.forEach { (key, value) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = key,
                        style = MaterialTheme.typography.bodyMedium,
                        color = EnlikoTextSecondary
                    )
                    Text(
                        text = value,
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium,
                        color = EnlikoTextPrimary
                    )
                }
            }
        }
    }
}

@Composable
private fun ServerLogItem(
    level: String,
    message: String,
    time: String
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.Top
        ) {
            Surface(
                color = when (level) {
                    "ERROR" -> EnlikoRed
                    "WARN" -> EnlikoYellow
                    "INFO" -> EnlikoGreen
                    else -> EnlikoTextSecondary
                }.copy(alpha = 0.2f),
                shape = RoundedCornerShape(4.dp)
            ) {
                Text(
                    text = level,
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                    color = when (level) {
                        "ERROR" -> EnlikoRed
                        "WARN" -> EnlikoYellow
                        "INFO" -> EnlikoGreen
                        else -> EnlikoTextSecondary
                    },
                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                )
            }
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextPrimary
                )
            }
            
            Text(
                text = time,
                style = MaterialTheme.typography.labelSmall,
                color = EnlikoTextSecondary
            )
        }
    }
}
