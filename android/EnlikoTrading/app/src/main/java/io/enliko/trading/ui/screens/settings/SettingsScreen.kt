package io.enliko.trading.ui.screens.settings

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.ui.theme.ShortRed
import io.enliko.trading.util.AppLanguage
import io.enliko.trading.util.LocalStrings

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onLogout: () -> Unit,
    onNavigateToNotifications: () -> Unit = {},
    onNavigateToActivity: () -> Unit = {},
    onNavigateToSpot: () -> Unit = {},
    onNavigateToStrategies: () -> Unit = {},
    onNavigateToCharts: (String) -> Unit = {},
    onNavigateToSocialTrading: () -> Unit = {},
    onNavigateToLanguage: () -> Unit = {},
    onNavigateToSubscription: () -> Unit = {},
    onNavigateToTradeHistory: () -> Unit = {},
    onNavigateToTradingSettings: () -> Unit = {},
    onNavigateToLinkEmail: () -> Unit = {},
    onNavigateToApiKeys: () -> Unit = {},
    onNavigateToLeverageSettings: () -> Unit = {},
    onNavigateToRiskSettings: () -> Unit = {},
    onNavigateToExchangeSettings: () -> Unit = {},
    onNavigateToMarketHeatmap: () -> Unit = {},
    onNavigateToStats: () -> Unit = {},
    onNavigateToPositions: () -> Unit = {},
    onNavigateToScreener: () -> Unit = {},
    onNavigateToAICopilot: () -> Unit = {},
    onNavigateToAdmin: () -> Unit = {},
    onNavigateToDebug: () -> Unit = {},
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val strings = LocalStrings.current
    val uiState by viewModel.uiState.collectAsState()
    var showLanguageDialog by remember { mutableStateOf(false) }
    var showExchangeDialog by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(strings.settings) }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Account Section
            item {
                Text(
                    text = strings.account,
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Language,
                    title = strings.language,
                    subtitle = AppLanguage.fromCode(uiState.language).let { "${it.flag} ${it.displayName}" },
                    onClick = { showLanguageDialog = true }
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.AccountBalance,
                    title = strings.exchange,
                    subtitle = uiState.exchange.replaceFirstChar { it.uppercase() },
                    onClick = { showExchangeDialog = true }
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Key,
                    title = strings.apiKeys,
                    subtitle = "Configure exchange API keys",
                    onClick = onNavigateToApiKeys
                )
            }
            
            // Linked Accounts Section (Unified Auth)
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = strings.linkedAccounts,
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
            
            // Telegram link status
            item {
                LinkedAccountItem(
                    icon = Icons.Default.Send,
                    platform = "Telegram",
                    isLinked = uiState.hasTelegramLinked,
                    linkedInfo = uiState.telegramUsername?.let { "@$it" } 
                        ?: uiState.telegramId?.let { "ID: $it" },
                    onLink = { viewModel.openTelegramToLink() }
                )
            }
            
            // Email link status
            item {
                LinkedAccountItem(
                    icon = Icons.Default.Email,
                    platform = "Email",
                    isLinked = uiState.hasEmailLinked,
                    linkedInfo = uiState.email,
                    isVerified = uiState.emailVerified,
                    onLink = onNavigateToLinkEmail
                )
            }
            
            // Trading Section
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = strings.trading,
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.TrendingUp,
                    title = strings.strategies,
                    subtitle = "Configure trading strategies",
                    onClick = onNavigateToStrategies
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Tune,
                    title = "Trading Settings",
                    subtitle = "DCA, ATR, Order types",
                    onClick = onNavigateToTradingSettings
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Speed,
                    title = "Leverage",
                    subtitle = "Adjust trading leverage",
                    onClick = onNavigateToLeverageSettings
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Shield,
                    title = "Risk Settings",
                    subtitle = "Entry%, TP%, SL%",
                    onClick = onNavigateToRiskSettings
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.SwapHoriz,
                    title = "Exchange Settings",
                    subtitle = "Configure exchanges",
                    onClick = onNavigateToExchangeSettings
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.History,
                    title = "Trade History",
                    subtitle = "View past trades",
                    onClick = onNavigateToTradeHistory
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Analytics,
                    title = "Statistics",
                    subtitle = "Trading performance",
                    onClick = onNavigateToStats
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.GridView,
                    title = "Market Heatmap",
                    subtitle = "Visual market overview",
                    onClick = onNavigateToMarketHeatmap
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.ShowChart,
                    title = "Charts",
                    subtitle = "Advanced TradingView charts",
                    onClick = { onNavigateToCharts("BTCUSDT") }
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.People,
                    title = "Social Trading",
                    subtitle = "Copy top traders",
                    onClick = onNavigateToSocialTrading
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Notifications,
                    title = strings.notifications,
                    subtitle = "Trade alerts and signals",
                    onClick = onNavigateToNotifications
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Timeline,
                    title = "Activity",
                    subtitle = "Cross-platform sync history",
                    onClick = onNavigateToActivity
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Wallet,
                    title = "Spot Trading",
                    subtitle = "Buy and sell crypto",
                    onClick = onNavigateToSpot
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.AccountBalanceWallet,
                    title = "Positions",
                    subtitle = "View open positions",
                    onClick = onNavigateToPositions
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Search,
                    title = "Screener",
                    subtitle = "Crypto screener with filters",
                    onClick = onNavigateToScreener
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Psychology,
                    title = "AI Copilot",
                    subtitle = "AI trading assistant",
                    onClick = onNavigateToAICopilot
                )
            }
            
            // Developer Section
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = strings.developer,
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.AdminPanelSettings,
                    title = "Admin Panel",
                    subtitle = "System management",
                    onClick = onNavigateToAdmin
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.Code,
                    title = "Debug Console",
                    subtitle = "View app logs",
                    onClick = onNavigateToDebug
                )
            }
            
            // Appearance Section
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = strings.appearance,
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
            
            item {
                SettingsItem(
                    icon = Icons.Default.DarkMode,
                    title = strings.theme,
                    subtitle = strings.systemTheme,
                    onClick = { /* Theme picker */ }
                )
            }
            
            // Premium Section
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.5f)
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onNavigateToSubscription() }
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Default.Star,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Spacer(modifier = Modifier.width(16.dp))
                            Column {
                                Text(
                                    text = strings.premium,
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.SemiBold
                                )
                                Text(
                                    text = strings.unlockAllFeatures,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                        Icon(
                            Icons.Default.ChevronRight,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            // Logout
            item {
                Spacer(modifier = Modifier.height(24.dp))
                OutlinedButton(
                    onClick = {
                        viewModel.logout()
                        onLogout()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = ShortRed
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.AutoMirrored.Filled.Logout, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(strings.logout)
                }
            }
            
            // Version
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = strings.appVersion,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.fillMaxWidth()
                        .wrapContentWidth(Alignment.CenterHorizontally)
                )
            }
        }
    }
    
    // Language Dialog
    if (showLanguageDialog) {
        AlertDialog(
            onDismissRequest = { showLanguageDialog = false },
            title = { Text(strings.language) },
            text = {
                LazyColumn {
                    items(AppLanguage.entries) { language ->
                        ListItem(
                            headlineContent = { Text("${language.flag} ${language.displayName}") },
                            modifier = Modifier.clickable {
                                viewModel.setLanguage(language.code)
                                showLanguageDialog = false
                            },
                            trailingContent = {
                                if (uiState.language == language.code) {
                                    Icon(
                                        Icons.Default.Check,
                                        contentDescription = null,
                                        tint = MaterialTheme.colorScheme.primary
                                    )
                                }
                            }
                        )
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showLanguageDialog = false }) {
                    Text(strings.cancel)
                }
            }
        )
    }
    
    // Exchange Dialog
    if (showExchangeDialog) {
        AlertDialog(
            onDismissRequest = { showExchangeDialog = false },
            title = { Text(strings.exchange) },
            text = {
                Column {
                    listOf("bybit" to "Bybit", "hyperliquid" to "HyperLiquid").forEach { (code, name) ->
                        ListItem(
                            headlineContent = { Text(name) },
                            modifier = Modifier.clickable {
                                viewModel.setExchange(code)
                                showExchangeDialog = false
                            },
                            trailingContent = {
                                if (uiState.exchange == code) {
                                    Icon(
                                        Icons.Default.Check,
                                        contentDescription = null,
                                        tint = MaterialTheme.colorScheme.primary
                                    )
                                }
                            }
                        )
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showExchangeDialog = false }) {
                    Text(strings.cancel)
                }
            }
        )
    }
}

@Composable
private fun SettingsItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(onClick = onClick)
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Text(
                        text = subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            Icon(
                Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun LinkedAccountItem(
    icon: ImageVector,
    platform: String,
    isLinked: Boolean,
    linkedInfo: String? = null,
    isVerified: Boolean? = null,
    onLink: () -> Unit
) {
    val strings = LocalStrings.current
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .then(if (!isLinked) Modifier.clickable(onClick = onLink) else Modifier)
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    icon,
                    contentDescription = null,
                    tint = if (isLinked) MaterialTheme.colorScheme.primary 
                           else MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(
                        text = platform,
                        style = MaterialTheme.typography.bodyLarge
                    )
                    if (isLinked && linkedInfo != null) {
                        Text(
                            text = linkedInfo,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    } else if (!isLinked) {
                        Text(
                            text = strings.tapToLink,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }
            if (isLinked) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (isVerified == false) {
                        Text(
                            text = strings.notVerified,
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.error
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                    }
                    Icon(
                        Icons.Default.CheckCircle,
                        contentDescription = "Linked",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            } else {
                Icon(
                    Icons.Default.AddCircleOutline,
                    contentDescription = "Link",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}
