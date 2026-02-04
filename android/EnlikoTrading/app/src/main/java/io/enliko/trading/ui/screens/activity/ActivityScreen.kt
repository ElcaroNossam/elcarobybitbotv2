package io.enliko.trading.ui.screens.activity

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.data.api.ActivityItemApi
import io.enliko.trading.data.api.ActivityStatsApi
import io.enliko.trading.services.ActivityService
import io.enliko.trading.util.Localization
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ActivityScreen(
    viewModel: ActivityViewModel = hiltViewModel(),
    onBack: () -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsState()
    val scope = rememberCoroutineScope()
    
    val sources = listOf("ios", "webapp", "telegram", "api")
    val categories = listOf("settings", "trading", "auth", "exchange")
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(Localization.get("activity_title")) },
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
            // Source Filter
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = uiState.selectedSource == null,
                    onClick = { viewModel.setSourceFilter(null) },
                    label = { Text("All Sources") }
                )
                sources.forEach { source ->
                    FilterChip(
                        selected = uiState.selectedSource == source,
                        onClick = { viewModel.setSourceFilter(source) },
                        label = { Text(getSourceLabel(source)) },
                        leadingIcon = {
                            Icon(
                                imageVector = getSourceIcon(source),
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                    )
                }
            }
            
            // Category Filter
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = uiState.selectedCategory == null,
                    onClick = { viewModel.setCategoryFilter(null) },
                    label = { Text("All Types") }
                )
                categories.forEach { category ->
                    FilterChip(
                        selected = uiState.selectedCategory == category,
                        onClick = { viewModel.setCategoryFilter(category) },
                        label = { Text(category.replaceFirstChar { it.uppercase() }) }
                    )
                }
            }
            
            // Stats Summary
            uiState.stats?.let { stats ->
                ActivityStatsBar(stats = stats)
            }
            
            // Loading or Content
            when {
                uiState.isLoading && uiState.activities.isEmpty() -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                uiState.activities.isEmpty() -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.History,
                                contentDescription = null,
                                modifier = Modifier.size(48.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Text(
                                text = Localization.get("activity_title"),
                                style = MaterialTheme.typography.titleMedium
                            )
                            Text(
                                text = Localization.get("activity_no_recent"),
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
                else -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(uiState.activities) { activity ->
                            ActivityRow(activity = activity)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ActivityStatsBar(stats: ActivityStatsApi) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceAround
        ) {
            StatItem(
                label = "Total",
                value = stats.totalActivities.toString(),
                icon = Icons.Outlined.List
            )
            StatItem(
                label = "Today",
                value = stats.todayCount.toString(),
                icon = Icons.Outlined.Today
            )
            StatItem(
                label = "Sync",
                value = if (stats.syncedCount > 0) "✓" else "−",
                icon = Icons.Outlined.Sync
            )
        }
    }
}

@Composable
private fun StatItem(
    label: String,
    value: String,
    icon: ImageVector
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(20.dp)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun ActivityRow(activity: ActivityItemApi) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Icon
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(getCategoryColor(activity.actionCategory).copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = getCategoryIcon(activity.actionCategory),
                    contentDescription = null,
                    tint = getCategoryColor(activity.actionCategory),
                    modifier = Modifier.size(20.dp)
                )
            }
            
            // Content
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = activity.actionType.replace("_", " ").replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Source badge
                    SourceBadge(source = activity.source)
                    
                    // Time
                    Text(
                        text = formatActivityTime(activity.createdAt),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            // Sync indicators
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                if (activity.telegramNotified) {
                    SyncIndicator(color = Color(0xFF0088CC), label = "T")
                }
                if (activity.webappNotified) {
                    SyncIndicator(color = Color(0xFF4CAF50), label = "W")
                }
                if (activity.iosNotified) {
                    SyncIndicator(color = Color(0xFF007AFF), label = "i")
                }
            }
        }
    }
}

@Composable
private fun SourceBadge(source: String) {
    Surface(
        color = getSourceColor(source).copy(alpha = 0.1f),
        shape = RoundedCornerShape(4.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = getSourceIcon(source),
                contentDescription = null,
                tint = getSourceColor(source),
                modifier = Modifier.size(12.dp)
            )
            Text(
                text = getSourceLabel(source),
                style = MaterialTheme.typography.labelSmall,
                color = getSourceColor(source)
            )
        }
    }
}

@Composable
private fun SyncIndicator(color: Color, label: String) {
    Box(
        modifier = Modifier
            .size(16.dp)
            .clip(CircleShape)
            .background(color.copy(alpha = 0.2f)),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = color,
            fontWeight = FontWeight.Bold
        )
    }
}

// Helper functions
private fun getSourceIcon(source: String): ImageVector = when (source) {
    "ios" -> Icons.Outlined.PhoneIphone
    "webapp" -> Icons.Outlined.Language
    "telegram" -> Icons.Outlined.Send
    "api" -> Icons.Outlined.Api
    else -> Icons.Outlined.DeviceUnknown
}

private fun getSourceLabel(source: String): String = when (source) {
    "ios" -> "iOS"
    "webapp" -> "Web"
    "telegram" -> "Telegram"
    "api" -> "API"
    else -> source
}

private fun getSourceColor(source: String): Color = when (source) {
    "ios" -> Color(0xFF007AFF)
    "webapp" -> Color(0xFF4CAF50)
    "telegram" -> Color(0xFF0088CC)
    "api" -> Color(0xFFFF9800)
    else -> Color.Gray
}

private fun getCategoryIcon(category: String): ImageVector = when (category) {
    "settings" -> Icons.Outlined.Settings
    "trading" -> Icons.Outlined.TrendingUp
    "auth" -> Icons.Outlined.Lock
    "exchange" -> Icons.Outlined.SwapHoriz
    else -> Icons.Outlined.Info
}

private fun getCategoryColor(category: String): Color = when (category) {
    "settings" -> Color(0xFF9C27B0)
    "trading" -> Color(0xFF4CAF50)
    "auth" -> Color(0xFF2196F3)
    "exchange" -> Color(0xFFFF9800)
    else -> Color.Gray
}

private fun formatActivityTime(dateString: String): String {
    return try {
        val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
        val date = inputFormat.parse(dateString)
        val now = Date()
        val diff = now.time - (date?.time ?: 0)
        
        val minutes = diff / 60000
        val hours = diff / 3600000
        val days = diff / 86400000
        
        when {
            minutes < 1 -> "Just now"
            minutes < 60 -> "${minutes}m ago"
            hours < 24 -> "${hours}h ago"
            days < 7 -> "${days}d ago"
            else -> SimpleDateFormat("MMM dd", Locale.getDefault()).format(date ?: Date())
        }
    } catch (e: Exception) {
        dateString.take(10)
    }
}
