package io.enliko.trading.ui.screens.alerts

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
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
import io.enliko.trading.util.LocalStrings
import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.*

// MARK: - Data Models
data class PriceAlert(
    val id: String = UUID.randomUUID().toString(),
    val symbol: String,
    val targetPrice: Double,
    val condition: AlertCondition,
    val currentPrice: Double = 0.0,
    val isTriggered: Boolean = false,
    val isEnabled: Boolean = true,
    val createdAt: Long = System.currentTimeMillis(),
    val triggeredAt: Long? = null,
    val note: String = ""
)

enum class AlertCondition(val displayName: String, val icon: androidx.compose.ui.graphics.vector.ImageVector) {
    ABOVE("Price Above", Icons.Default.TrendingUp),
    BELOW("Price Below", Icons.Default.TrendingDown),
    CROSSES("Price Crosses", Icons.Default.SwapVert)
}

enum class AlertTab { ACTIVE, TRIGGERED, ALL }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AlertsScreen(
    onNavigateBack: () -> Unit = {}
) {
    val strings = LocalStrings.current
    var selectedTab by remember { mutableStateOf(AlertTab.ACTIVE) }
    var showCreateDialog by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(true) }
    var alerts by remember { mutableStateOf<List<PriceAlert>>(emptyList()) }
    
    // Mock data
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(500)
        alerts = listOf(
            PriceAlert(
                symbol = "BTCUSDT",
                targetPrice = 100000.0,
                condition = AlertCondition.ABOVE,
                currentPrice = 98500.0,
                isEnabled = true
            ),
            PriceAlert(
                symbol = "ETHUSDT",
                targetPrice = 3500.0,
                condition = AlertCondition.BELOW,
                currentPrice = 3200.0,
                isEnabled = true
            ),
            PriceAlert(
                symbol = "SOLUSDT",
                targetPrice = 180.0,
                condition = AlertCondition.CROSSES,
                currentPrice = 175.0,
                isTriggered = true,
                triggeredAt = System.currentTimeMillis() - 3600000
            ),
            PriceAlert(
                symbol = "XRPUSDT",
                targetPrice = 2.5,
                condition = AlertCondition.ABOVE,
                currentPrice = 2.35,
                isEnabled = false
            )
        )
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Price Alerts") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showCreateDialog = true }) {
                        Icon(Icons.Default.Add, contentDescription = "Add Alert")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showCreateDialog = true },
                containerColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add Alert")
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Tab Selector
            AlertTabSelector(
                selectedTab = selectedTab,
                onTabSelected = { selectedTab = it },
                alertCounts = mapOf(
                    AlertTab.ACTIVE to alerts.count { it.isEnabled && !it.isTriggered },
                    AlertTab.TRIGGERED to alerts.count { it.isTriggered },
                    AlertTab.ALL to alerts.size
                )
            )
            
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else {
                val filteredAlerts = when (selectedTab) {
                    AlertTab.ACTIVE -> alerts.filter { it.isEnabled && !it.isTriggered }
                    AlertTab.TRIGGERED -> alerts.filter { it.isTriggered }
                    AlertTab.ALL -> alerts
                }
                
                if (filteredAlerts.isEmpty()) {
                    EmptyAlertsView(
                        tab = selectedTab,
                        onCreateAlert = { showCreateDialog = true }
                    )
                } else {
                    LazyColumn(
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(filteredAlerts, key = { it.id }) { alert ->
                            AlertCard(
                                alert = alert,
                                onToggle = { 
                                    alerts = alerts.map { 
                                        if (it.id == alert.id) it.copy(isEnabled = !it.isEnabled) 
                                        else it 
                                    }
                                },
                                onDelete = {
                                    alerts = alerts.filter { it.id != alert.id }
                                }
                            )
                        }
                    }
                }
            }
        }
    }
    
    // Create Alert Dialog
    if (showCreateDialog) {
        CreateAlertDialog(
            onDismiss = { showCreateDialog = false },
            onCreate = { newAlert ->
                alerts = alerts + newAlert
                showCreateDialog = false
            }
        )
    }
}

@Composable
private fun AlertTabSelector(
    selectedTab: AlertTab,
    onTabSelected: (AlertTab) -> Unit,
    alertCounts: Map<AlertTab, Int>
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        AlertTab.entries.forEach { tab ->
            val isSelected = tab == selectedTab
            val count = alertCounts[tab] ?: 0
            
            FilterChip(
                selected = isSelected,
                onClick = { onTabSelected(tab) },
                label = {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(tab.name.lowercase().replaceFirstChar { it.uppercase() })
                        if (count > 0) {
                            Badge(
                                containerColor = if (isSelected) 
                                    MaterialTheme.colorScheme.onPrimary 
                                else 
                                    MaterialTheme.colorScheme.primary
                            ) {
                                Text(
                                    text = count.toString(),
                                    color = if (isSelected)
                                        MaterialTheme.colorScheme.primary
                                    else
                                        MaterialTheme.colorScheme.onPrimary
                                )
                            }
                        }
                    }
                },
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun AlertCard(
    alert: PriceAlert,
    onToggle: () -> Unit,
    onDelete: () -> Unit
) {
    val strings = LocalStrings.current
    val priceDistance = ((alert.targetPrice - alert.currentPrice) / alert.currentPrice * 100)
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (alert.isTriggered) 
                MaterialTheme.colorScheme.secondaryContainer 
            else 
                MaterialTheme.colorScheme.surfaceVariant
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
                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Condition Icon
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(
                                when (alert.condition) {
                                    AlertCondition.ABOVE -> LongGreen.copy(alpha = 0.2f)
                                    AlertCondition.BELOW -> ShortRed.copy(alpha = 0.2f)
                                    AlertCondition.CROSSES -> MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)
                                }
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = alert.condition.icon,
                            contentDescription = null,
                            tint = when (alert.condition) {
                                AlertCondition.ABOVE -> LongGreen
                                AlertCondition.BELOW -> ShortRed
                                AlertCondition.CROSSES -> MaterialTheme.colorScheme.primary
                            }
                        )
                    }
                    
                    Column {
                        Text(
                            text = alert.symbol,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = alert.condition.displayName,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                if (!alert.isTriggered) {
                    Switch(
                        checked = alert.isEnabled,
                        onCheckedChange = { onToggle() }
                    )
                } else {
                    IconButton(onClick = onDelete) {
                        Icon(
                            Icons.Default.Delete,
                            contentDescription = "Delete",
                            tint = ShortRed
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Price Info
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = strings.targetPrice,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = formatPrice(alert.targetPrice),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = strings.currentPrice,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = formatPrice(alert.currentPrice),
                        style = MaterialTheme.typography.titleMedium
                    )
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = strings.distance,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "${if (priceDistance >= 0) "+" else ""}${String.format("%.2f", priceDistance)}%",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (priceDistance >= 0) LongGreen else ShortRed
                    )
                }
            }
            
            if (alert.isTriggered && alert.triggeredAt != null) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Triggered: ${formatDate(alert.triggeredAt)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun EmptyAlertsView(
    tab: AlertTab,
    onCreateAlert: () -> Unit
) {
    val strings = LocalStrings.current
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.NotificationsNone,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = when (tab) {
                AlertTab.ACTIVE -> "No Active Alerts"
                AlertTab.TRIGGERED -> "No Triggered Alerts"
                AlertTab.ALL -> "No Alerts Created"
            },
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = strings.alertCreateDesc,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(onClick = onCreateAlert) {
            Icon(Icons.Default.Add, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Create Alert")
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun CreateAlertDialog(
    onDismiss: () -> Unit,
    onCreate: (PriceAlert) -> Unit
) {
    val strings = LocalStrings.current
    var symbol by remember { mutableStateOf("BTCUSDT") }
    var targetPrice by remember { mutableStateOf("") }
    var condition by remember { mutableStateOf(AlertCondition.ABOVE) }
    var note by remember { mutableStateOf("") }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Create Price Alert") },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                OutlinedTextField(
                    value = symbol,
                    onValueChange = { symbol = it.uppercase() },
                    label = { Text("Symbol") },
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = targetPrice,
                    onValueChange = { targetPrice = it },
                    label = { Text("Target Price") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.fillMaxWidth()
                )
                
                Text(
                    text = strings.condition,
                    style = MaterialTheme.typography.labelLarge
                )
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    AlertCondition.entries.forEach { cond ->
                        FilterChip(
                            selected = condition == cond,
                            onClick = { condition = cond },
                            label = { Text(cond.displayName) },
                            leadingIcon = {
                                Icon(cond.icon, contentDescription = null, modifier = Modifier.size(16.dp))
                            }
                        )
                    }
                }
                
                OutlinedTextField(
                    value = note,
                    onValueChange = { note = it },
                    label = { Text("Note (optional)") },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    val price = targetPrice.toDoubleOrNull() ?: return@Button
                    onCreate(
                        PriceAlert(
                            symbol = symbol,
                            targetPrice = price,
                            condition = condition,
                            note = note
                        )
                    )
                },
                enabled = symbol.isNotBlank() && targetPrice.toDoubleOrNull() != null
            ) {
                Text("Create")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

private fun formatPrice(value: Double): String {
    return if (value >= 1) {
        String.format("$%.2f", value)
    } else {
        String.format("$%.6f", value)
    }
}

private fun formatDate(timestamp: Long): String {
    return SimpleDateFormat("MMM d, HH:mm", Locale.getDefault()).format(Date(timestamp))
}
