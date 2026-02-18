package io.enliko.trading.ui.screens.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.Strings
import io.enliko.trading.util.LocalStrings

/**
 * Notification Settings Screen - synced with iOS and WebApp
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationSettingsScreen(
    strings: Strings,
    onBack: () -> Unit
) {
    val strings = LocalStrings.current
    // Notification states
    var tradesEnabled by remember { mutableStateOf(true) }
    var signalsEnabled by remember { mutableStateOf(true) }
    var priceAlertsEnabled by remember { mutableStateOf(true) }
    var dailySummaryEnabled by remember { mutableStateOf(false) }
    var soundEnabled by remember { mutableStateOf(true) }
    var vibrationEnabled by remember { mutableStateOf(true) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(strings.notifications) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = DarkSurface,
                    titleContentColor = DarkOnBackground
                )
            )
        },
        containerColor = DarkBackground
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Categories Header
            item {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = strings.notificationCategories,
                    style = MaterialTheme.typography.labelLarge,
                    color = DarkOnSurfaceVariant
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
            
            // Trade Notifications
            item {
                NotificationToggleItem(
                    icon = Icons.Default.SwapHoriz,
                    iconColor = EnlikoPrimary,
                    title = "Trade Notifications",
                    subtitle = "Get notified when trades open or close",
                    checked = tradesEnabled,
                    onCheckedChange = { tradesEnabled = it }
                )
            }
            
            // Signal Notifications
            item {
                NotificationToggleItem(
                    icon = Icons.Default.Notifications,
                    iconColor = EnlikoSecondary,
                    title = "Trading Signals",
                    subtitle = "Receive new trading signal alerts",
                    checked = signalsEnabled,
                    onCheckedChange = { signalsEnabled = it }
                )
            }
            
            // Price Alerts
            item {
                NotificationToggleItem(
                    icon = Icons.Default.TrendingUp,
                    iconColor = EnlikoAccent,
                    title = "Price Alerts",
                    subtitle = "Alert when price targets are reached",
                    checked = priceAlertsEnabled,
                    onCheckedChange = { priceAlertsEnabled = it }
                )
            }
            
            // Daily Summary
            item {
                NotificationToggleItem(
                    icon = Icons.Default.CalendarToday,
                    iconColor = SuccessGreen,
                    title = "Daily Summary",
                    subtitle = "Daily trading performance report",
                    checked = dailySummaryEnabled,
                    onCheckedChange = { dailySummaryEnabled = it }
                )
            }
            
            // Preferences Header
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = strings.preferences,
                    style = MaterialTheme.typography.labelLarge,
                    color = DarkOnSurfaceVariant
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
            
            // Sound
            item {
                NotificationToggleItem(
                    icon = Icons.Default.VolumeUp,
                    iconColor = DarkOnSurface,
                    title = "Sound",
                    subtitle = "Play sound for notifications",
                    checked = soundEnabled,
                    onCheckedChange = { soundEnabled = it }
                )
            }
            
            // Vibration
            item {
                NotificationToggleItem(
                    icon = Icons.Default.Vibration,
                    iconColor = DarkOnSurface,
                    title = "Vibration",
                    subtitle = "Vibrate for notifications",
                    checked = vibrationEnabled,
                    onCheckedChange = { vibrationEnabled = it }
                )
            }
            
            item {
                Spacer(modifier = Modifier.height(24.dp))
            }
        }
    }
}

@Composable
private fun NotificationToggleItem(
    icon: ImageVector,
    iconColor: androidx.compose.ui.graphics.Color,
    title: String,
    subtitle: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = DarkSurface
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = iconColor,
                modifier = Modifier.size(24.dp)
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyLarge,
                    color = DarkOnBackground
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = DarkOnSurfaceVariant
                )
            }
            
            Switch(
                checked = checked,
                onCheckedChange = onCheckedChange,
                colors = SwitchDefaults.colors(
                    checkedThumbColor = DarkOnBackground,
                    checkedTrackColor = EnlikoPrimary,
                    uncheckedThumbColor = DarkOnSurfaceVariant,
                    uncheckedTrackColor = DarkSurfaceVariant
                )
            )
        }
    }
}
