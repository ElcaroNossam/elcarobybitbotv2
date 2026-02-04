package io.enliko.trading.ui.screens.notifications

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.Localization
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.abs

/**
 * NotificationsScreen - Matching iOS NotificationsView.swift
 * Features: Notification list, banner, preferences, read/unread state
 */

// Data class matching iOS AppNotification
data class AppNotification(
    val id: String,
    val type: NotificationType,
    val title: String,
    val message: String,
    val data: Map<String, Any>? = null,
    val isRead: Boolean = false,
    val createdAt: Date = Date()
) {
    val icon: ImageVector get() = type.icon
    val color: Color get() = type.color
}

enum class NotificationType(val icon: ImageVector, val color: Color) {
    TRADE(Icons.Default.TrendingUp, EnlikoGreen),
    SIGNAL(Icons.Default.Notifications, EnlikoPrimary),
    PRICE_ALERT(Icons.Default.PriceChange, EnlikoYellow),
    SYSTEM(Icons.Default.Info, EnlikoBlue),
    WARNING(Icons.Default.Warning, EnlikoYellow),
    ERROR(Icons.Default.Error, EnlikoRed)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationsScreen(
    onBack: () -> Unit,
    viewModel: NotificationsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val pullRefreshState = rememberPullToRefreshState()
    
    LaunchedEffect(pullRefreshState.isRefreshing) {
        if (pullRefreshState.isRefreshing) {
            viewModel.loadNotifications()
            pullRefreshState.endRefresh()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(Localization.get("notifications")) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    if (uiState.unreadCount > 0) {
                        TextButton(onClick = { viewModel.markAllAsRead() }) {
                            Text(
                                Localization.get("mark_all_read"),
                                color = EnlikoPrimary,
                                fontSize = 12.sp
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = EnlikoBackground
                )
            )
        },
        containerColor = EnlikoBackground
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .pullToRefresh(
                    state = pullRefreshState,
                    isRefreshing = uiState.isLoading
                )
        ) {
            when {
                uiState.isLoading && uiState.notifications.isEmpty() -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = EnlikoPrimary)
                    }
                }
                uiState.notifications.isEmpty() -> {
                    EmptyNotificationsState()
                }
                else -> {
                    NotificationsList(
                        notifications = uiState.notifications,
                        onNotificationClick = { notification ->
                            if (!notification.isRead) {
                                viewModel.markAsRead(notification.id)
                            }
                        }
                    )
                }
            }
            
            // Pull to refresh indicator
            PullToRefreshContainer(
                state = pullRefreshState,
                modifier = Modifier.align(Alignment.TopCenter),
                containerColor = EnlikoCard,
                contentColor = EnlikoPrimary
            )
        }
    }
}

@Composable
private fun EmptyNotificationsState() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.NotificationsOff,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = EnlikoTextMuted
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = Localization.get("no_notifications"),
            style = MaterialTheme.typography.titleMedium,
            color = EnlikoTextSecondary
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = Localization.get("no_notifications_desc"),
            style = MaterialTheme.typography.bodySmall,
            color = EnlikoTextMuted,
            modifier = Modifier.padding(horizontal = 40.dp)
        )
    }
}

@Composable
private fun NotificationsList(
    notifications: List<AppNotification>,
    onNotificationClick: (AppNotification) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(notifications, key = { it.id }) { notification ->
            NotificationCard(
                notification = notification,
                onClick = { onNotificationClick(notification) }
            )
        }
    }
}

@Composable
private fun NotificationCard(
    notification: AppNotification,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(
                if (notification.isRead) EnlikoCard 
                else EnlikoCard.copy(alpha = 0.9f)
            )
            .then(
                if (!notification.isRead) {
                    Modifier.background(
                        color = notification.color.copy(alpha = 0.05f),
                        shape = RoundedCornerShape(12.dp)
                    )
                } else Modifier
            )
            .clickable(onClick = onClick)
            .padding(12.dp),
        verticalAlignment = Alignment.Top
    ) {
        // Unread indicator
        Box(
            modifier = Modifier
                .size(8.dp)
                .clip(CircleShape)
                .background(
                    if (notification.isRead) Color.Transparent 
                    else EnlikoPrimary
                )
                .align(Alignment.CenterVertically)
        )
        
        Spacer(modifier = Modifier.width(12.dp))
        
        // Icon
        Box(
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
                .background(notification.color.copy(alpha = 0.15f)),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = notification.icon,
                contentDescription = null,
                modifier = Modifier.size(20.dp),
                tint = notification.color
            )
        }
        
        Spacer(modifier = Modifier.width(12.dp))
        
        // Content
        Column(modifier = Modifier.weight(1f)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Text(
                    text = notification.title,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = EnlikoTextPrimary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )
                
                Text(
                    text = timeAgo(notification.createdAt),
                    style = MaterialTheme.typography.labelSmall,
                    color = EnlikoTextMuted,
                    modifier = Modifier.padding(start = 8.dp)
                )
            }
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = notification.message,
                style = MaterialTheme.typography.bodySmall,
                color = EnlikoTextSecondary,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
            
            // Extra data (symbol, PnL)
            notification.data?.let { data ->
                val symbol = data["symbol"] as? String
                val pnl = data["pnl"] as? Double
                
                if (symbol != null) {
                    Spacer(modifier = Modifier.height(6.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = symbol,
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Medium,
                            color = EnlikoPrimary
                        )
                        
                        pnl?.let {
                            Text(
                                text = String.format("%+.2f%%", it),
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.SemiBold,
                                color = if (it >= 0) EnlikoGreen else EnlikoRed
                            )
                        }
                    }
                }
            }
        }
    }
}

// MARK: - Notification Banner (In-App)

@Composable
fun NotificationBanner(
    notification: AppNotification?,
    onDismiss: () -> Unit,
    onTap: () -> Unit
) {
    AnimatedVisibility(
        visible = notification != null,
        enter = slideInVertically(initialOffsetY = { -it }) + fadeIn(),
        exit = slideOutVertically(targetOffsetY = { -it }) + fadeOut()
    ) {
        notification?.let { notif ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
                    .clickable(onClick = onTap),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = EnlikoCard),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Icon
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .clip(CircleShape)
                            .background(notif.color.copy(alpha = 0.2f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = notif.icon,
                            contentDescription = null,
                            modifier = Modifier.size(22.dp),
                            tint = notif.color
                        )
                    }
                    
                    Spacer(modifier = Modifier.width(12.dp))
                    
                    // Content
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = notif.title,
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.SemiBold,
                            color = EnlikoTextPrimary,
                            maxLines = 1
                        )
                        
                        Spacer(modifier = Modifier.height(2.dp))
                        
                        Text(
                            text = notif.message,
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary,
                            maxLines = 2
                        )
                    }
                    
                    // Dismiss
                    IconButton(
                        onClick = onDismiss,
                        modifier = Modifier.size(32.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Dismiss",
                            modifier = Modifier.size(16.dp),
                            tint = EnlikoTextMuted
                        )
                    }
                }
            }
        }
    }
}

// MARK: - Notification Preferences Screen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationPreferencesScreen(
    onBack: () -> Unit,
    viewModel: NotificationsViewModel = hiltViewModel()
) {
    val preferences by viewModel.preferences.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(Localization.get("notification_preferences")) },
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
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Permission status
            item {
                PermissionCard(
                    isAuthorized = viewModel.isAuthorized,
                    onRequestPermission = { viewModel.requestPermission() }
                )
            }
            
            // Categories
            item {
                PreferencesCard(
                    title = Localization.get("notification_categories"),
                    preferences = listOf(
                        SwitchPreference(
                            title = Localization.get("notification_trades"),
                            isChecked = preferences.tradesEnabled,
                            onCheckedChange = { viewModel.updatePreference { it.copy(tradesEnabled = !it.tradesEnabled) } }
                        ),
                        SwitchPreference(
                            title = Localization.get("notification_signals"),
                            isChecked = preferences.signalsEnabled,
                            onCheckedChange = { viewModel.updatePreference { it.copy(signalsEnabled = !it.signalsEnabled) } }
                        ),
                        SwitchPreference(
                            title = Localization.get("notification_price_alerts"),
                            isChecked = preferences.priceAlertsEnabled,
                            onCheckedChange = { viewModel.updatePreference { it.copy(priceAlertsEnabled = !it.priceAlertsEnabled) } }
                        ),
                        SwitchPreference(
                            title = Localization.get("notification_daily_summary"),
                            isChecked = preferences.dailyReportEnabled,
                            onCheckedChange = { viewModel.updatePreference { it.copy(dailyReportEnabled = !it.dailyReportEnabled) } }
                        )
                    )
                )
            }
            
            // Specific notifications
            item {
                PreferencesCard(
                    title = Localization.get("specific_notifications"),
                    preferences = listOf(
                        SwitchPreference(
                            title = Localization.get("trade_opened"),
                            isChecked = preferences.tradeOpened,
                            onCheckedChange = { viewModel.updatePreference { it.copy(tradeOpened = !it.tradeOpened) } }
                        ),
                        SwitchPreference(
                            title = Localization.get("trade_closed"),
                            isChecked = preferences.tradeClosed,
                            onCheckedChange = { viewModel.updatePreference { it.copy(tradeClosed = !it.tradeClosed) } }
                        ),
                        SwitchPreference(
                            title = Localization.get("break_even"),
                            isChecked = preferences.breakEven,
                            onCheckedChange = { viewModel.updatePreference { it.copy(breakEven = !it.breakEven) } }
                        ),
                        SwitchPreference(
                            title = Localization.get("partial_tp"),
                            isChecked = preferences.partialTp,
                            onCheckedChange = { viewModel.updatePreference { it.copy(partialTp = !it.partialTp) } }
                        ),
                        SwitchPreference(
                            title = Localization.get("margin_warning"),
                            isChecked = preferences.marginWarning,
                            onCheckedChange = { viewModel.updatePreference { it.copy(marginWarning = !it.marginWarning) } }
                        )
                    )
                )
            }
            
            // Sound & Vibration
            item {
                PreferencesCard(
                    title = Localization.get("sound_vibration"),
                    preferences = listOf(
                        SwitchPreference(
                            title = Localization.get("notification_sound"),
                            isChecked = preferences.soundEnabled,
                            onCheckedChange = { viewModel.updatePreference { it.copy(soundEnabled = !it.soundEnabled) } }
                        ),
                        SwitchPreference(
                            title = Localization.get("notification_vibration"),
                            isChecked = preferences.vibrationEnabled,
                            onCheckedChange = { viewModel.updatePreference { it.copy(vibrationEnabled = !it.vibrationEnabled) } }
                        )
                    )
                )
            }
        }
    }
}

@Composable
private fun PermissionCard(
    isAuthorized: Boolean,
    onRequestPermission: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(16.dp)
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
                    text = Localization.get("push_notifications"),
                    style = MaterialTheme.typography.titleMedium,
                    color = EnlikoTextPrimary
                )
                Text(
                    text = if (isAuthorized) Localization.get("enabled") else Localization.get("disabled"),
                    style = MaterialTheme.typography.bodySmall,
                    color = if (isAuthorized) EnlikoGreen else EnlikoRed
                )
            }
            
            if (!isAuthorized) {
                Button(
                    onClick = onRequestPermission,
                    colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary)
                ) {
                    Text(Localization.get("enable"))
                }
            } else {
                Icon(
                    imageVector = Icons.Default.CheckCircle,
                    contentDescription = null,
                    tint = EnlikoGreen,
                    modifier = Modifier.size(28.dp)
                )
            }
        }
    }
}

data class SwitchPreference(
    val title: String,
    val isChecked: Boolean,
    val onCheckedChange: () -> Unit
)

@Composable
private fun PreferencesCard(
    title: String,
    preferences: List<SwitchPreference>
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            preferences.forEachIndexed { index, pref ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = pref.title,
                        style = MaterialTheme.typography.bodyMedium,
                        color = EnlikoTextPrimary
                    )
                    
                    Switch(
                        checked = pref.isChecked,
                        onCheckedChange = { pref.onCheckedChange() },
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = EnlikoPrimary,
                            checkedTrackColor = EnlikoPrimary.copy(alpha = 0.5f)
                        )
                    )
                }
                
                if (index < preferences.lastIndex) {
                    HorizontalDivider(color = EnlikoBorder)
                }
            }
        }
    }
}

// Helper function
private fun timeAgo(date: Date): String {
    val now = System.currentTimeMillis()
    val diff = now - date.time
    
    val seconds = diff / 1000
    val minutes = seconds / 60
    val hours = minutes / 60
    val days = hours / 24
    
    return when {
        seconds < 60 -> "now"
        minutes < 60 -> "${minutes}m"
        hours < 24 -> "${hours}h"
        days < 7 -> "${days}d"
        else -> {
            val sdf = SimpleDateFormat("MMM d", Locale.getDefault())
            sdf.format(date)
        }
    }
}
