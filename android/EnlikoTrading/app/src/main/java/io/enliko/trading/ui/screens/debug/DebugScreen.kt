package io.enliko.trading.ui.screens.debug

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.AppLogger
import io.enliko.trading.util.LogEntry
import io.enliko.trading.util.LogLevel
import java.text.SimpleDateFormat
import java.util.*

/**
 * DebugScreen - Matching iOS DebugView.swift
 * Debug console for viewing app logs and diagnostics
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DebugScreen(
    onBack: () -> Unit = {}
) {
    var selectedLevel by remember { mutableStateOf<LogLevel?>(null) }
    var showClearDialog by remember { mutableStateOf(false) }
    var searchQuery by remember { mutableStateOf("") }
    val clipboardManager = LocalClipboardManager.current
    
    val logs = remember {
        mutableStateListOf<LogEntry>().apply {
            addAll(AppLogger.getLogHistory())
        }
    }
    
    val filteredLogs = remember(logs.toList(), selectedLevel, searchQuery) {
        logs.filter { log ->
            (selectedLevel == null || log.level == selectedLevel) &&
            (searchQuery.isEmpty() || 
             log.message.contains(searchQuery, ignoreCase = true) ||
             log.category.contains(searchQuery, ignoreCase = true))
        }.sortedByDescending { it.timestamp }
    }
    
    // Clear dialog
    if (showClearDialog) {
        AlertDialog(
            onDismissRequest = { showClearDialog = false },
            title = { Text("Clear Logs") },
            text = { Text("Are you sure you want to clear all logs?") },
            confirmButton = {
                TextButton(
                    onClick = {
                        AppLogger.clearLogs()
                        logs.clear()
                        showClearDialog = false
                    }
                ) {
                    Text("Clear", color = EnlikoRed)
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearDialog = false }) {
                    Text("Cancel")
                }
            },
            containerColor = EnlikoCard
        )
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Column {
                        Text("Debug Console")
                        Text(
                            "${filteredLogs.size} logs",
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(
                        onClick = {
                            val allLogs = filteredLogs.joinToString("\n") { log ->
                                "[${log.level}] ${log.category}: ${log.message}"
                            }
                            clipboardManager.setText(AnnotatedString(allLogs))
                        }
                    ) {
                        Icon(Icons.Default.ContentCopy, contentDescription = "Copy all")
                    }
                    IconButton(onClick = { showClearDialog = true }) {
                        Icon(Icons.Default.Delete, contentDescription = "Clear logs")
                    }
                    IconButton(
                        onClick = {
                            logs.clear()
                            logs.addAll(AppLogger.getLogHistory())
                        }
                    ) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
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
            // Search bar
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                placeholder = { Text("Search logs...") },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { searchQuery = "" }) {
                            Icon(Icons.Default.Close, contentDescription = "Clear")
                        }
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = EnlikoPrimary,
                    unfocusedBorderColor = EnlikoBorder,
                    focusedContainerColor = EnlikoCard,
                    unfocusedContainerColor = EnlikoCard
                )
            )
            
            // Filter chips
            Row(
                modifier = Modifier
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = selectedLevel == null,
                    onClick = { selectedLevel = null },
                    label = { Text("All") },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = EnlikoPrimary,
                        selectedLabelColor = Color.White
                    )
                )
                
                LogLevel.entries.forEach { level ->
                    FilterChip(
                        selected = selectedLevel == level,
                        onClick = { 
                            selectedLevel = if (selectedLevel == level) null else level
                        },
                        label = { Text(level.name) },
                        leadingIcon = {
                            Icon(
                                imageVector = when (level) {
                                    LogLevel.DEBUG -> Icons.Default.Code
                                    LogLevel.INFO -> Icons.Default.Info
                                    LogLevel.WARNING -> Icons.Default.Warning
                                    LogLevel.ERROR -> Icons.Default.Error
                                    LogLevel.CRITICAL -> Icons.Default.Report
                                },
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                        },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = level.toColor(),
                            selectedLabelColor = Color.White,
                            labelColor = level.toColor()
                        )
                    )
                }
            }
            
            // System info card
            SystemInfoCard()
            
            // Logs list
            LazyColumn(
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (filteredLogs.isEmpty()) {
                    item {
                        EmptyLogsState()
                    }
                } else {
                    items(filteredLogs, key = { "${it.timestamp}_${it.message.hashCode()}" }) { log ->
                        LogEntryCard(log = log, clipboardManager = clipboardManager)
                    }
                }
            }
        }
    }
}

@Composable
private fun SystemInfoCard() {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = "System Info",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                color = EnlikoTextPrimary
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SystemInfoItem("App Version", "1.0.0")
                SystemInfoItem("Build", "1")
                SystemInfoItem("Android", android.os.Build.VERSION.RELEASE)
                SystemInfoItem("Device", android.os.Build.MODEL)
            }
        }
    }
}

@Composable
private fun SystemInfoItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = EnlikoTextPrimary
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = EnlikoTextSecondary
        )
    }
}

@Composable
private fun LogEntryCard(
    log: LogEntry,
    clipboardManager: androidx.compose.ui.platform.ClipboardManager
) {
    val dateFormatter = remember { SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault()) }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(8.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            // Header row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Level badge
                    Surface(
                        color = log.level.toColor().copy(alpha = 0.2f),
                        shape = RoundedCornerShape(4.dp)
                    ) {
                        Text(
                            text = log.level.name,
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = log.level.toColor(),
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                    
                    // Category badge
                    Surface(
                        color = EnlikoPrimary.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(4.dp)
                    ) {
                        Text(
                            text = log.category,
                            style = MaterialTheme.typography.labelSmall,
                            color = EnlikoPrimary,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = dateFormatter.format(Date(log.timestamp)),
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                    
                    IconButton(
                        onClick = {
                            clipboardManager.setText(AnnotatedString(log.message))
                        },
                        modifier = Modifier.size(24.dp)
                    ) {
                        Icon(
                            Icons.Default.ContentCopy,
                            contentDescription = "Copy",
                            modifier = Modifier.size(14.dp),
                            tint = EnlikoTextSecondary
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Message
            Text(
                text = log.message,
                style = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace,
                fontSize = 12.sp,
                color = EnlikoTextPrimary,
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
            )
        }
    }
}

@Composable
private fun EmptyLogsState() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            Icons.Default.Code,
            contentDescription = null,
            modifier = Modifier.size(48.dp),
            tint = EnlikoTextSecondary
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "No logs found",
            style = MaterialTheme.typography.titleMedium,
            color = EnlikoTextPrimary
        )
        Text(
            text = "Logs will appear here as the app runs",
            style = MaterialTheme.typography.bodyMedium,
            color = EnlikoTextSecondary
        )
    }
}

private fun LogLevel.toColor(): Color = when (this) {
    LogLevel.DEBUG -> Color(0xFF64B5F6)     // Light blue
    LogLevel.INFO -> EnlikoGreen             // Green
    LogLevel.WARNING -> EnlikoYellow         // Yellow/Orange
    LogLevel.ERROR -> EnlikoRed              // Red
    LogLevel.CRITICAL -> Color(0xFFAD1457)   // Dark magenta
}
