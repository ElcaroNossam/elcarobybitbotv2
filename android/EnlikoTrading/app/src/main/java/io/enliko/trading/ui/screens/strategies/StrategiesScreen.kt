package io.enliko.trading.ui.screens.strategies

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
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
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import kotlinx.coroutines.delay

// MARK: - Data Models
data class Strategy(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color,
    val isEnabled: Boolean,
    val longEnabled: Boolean,
    val shortEnabled: Boolean,
    val trades: Int,
    val pnl: Double,
    val winRate: Double,
    val settings: StrategySettings
)

data class StrategySettings(
    val entryPercent: Double = 1.0,
    val tpPercent: Double = 25.0,
    val slPercent: Double = 30.0,
    val leverage: Int = 10,
    val useAtr: Boolean = true,
    val atrPeriods: Int = 7,
    val atrMultiplierSl: Double = 0.5,
    val atrTriggerPct: Double = 3.0,
    val atrStepPct: Double = 0.5,
    val orderType: String = "market",
    val limitOffsetPct: Double = 0.1,
    val direction: String = "all",
    val coinsGroup: String = "ALL",
    val maxPositions: Int = 0,
    val dcaEnabled: Boolean = false,
    val dcaPct1: Double = 10.0,
    val dcaPct2: Double = 25.0,
    val beEnabled: Boolean = false,
    val beTriggerPct: Double = 1.0,
    val partialTpEnabled: Boolean = false,
    val partialTp1TriggerPct: Double = 2.0,
    val partialTp1ClosePct: Double = 30.0,
    val partialTp2TriggerPct: Double = 5.0,
    val partialTp2ClosePct: Double = 30.0
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StrategiesScreen(
    onNavigateBack: () -> Unit = {}
) {
    var strategies by remember { mutableStateOf(listOf<Strategy>()) }
    var isLoading by remember { mutableStateOf(true) }
    var selectedStrategy by remember { mutableStateOf<Strategy?>(null) }
    var showSettingsSheet by remember { mutableStateOf(false) }
    
    // Load strategies
    LaunchedEffect(Unit) {
        delay(500)
        strategies = generateDefaultStrategies()
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Trading Strategies", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { /* Help */ }) {
                        Icon(Icons.Default.HelpOutline, contentDescription = "Help")
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
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Overview Card
                item {
                    StrategiesOverviewCard(strategies = strategies)
                }
                
                // Strategy Cards
                items(strategies) { strategy ->
                    StrategyCard(
                        strategy = strategy,
                        onToggle = { enabled ->
                            strategies = strategies.map {
                                if (it.id == strategy.id) it.copy(isEnabled = enabled)
                                else it
                            }
                        },
                        onSettings = {
                            selectedStrategy = strategy
                            showSettingsSheet = true
                        }
                    )
                }
            }
        }
    }
    
    // Settings Bottom Sheet
    if (showSettingsSheet && selectedStrategy != null) {
        StrategySettingsSheet(
            strategy = selectedStrategy!!,
            onDismiss = { showSettingsSheet = false },
            onSave = { updatedStrategy ->
                strategies = strategies.map {
                    if (it.id == updatedStrategy.id) updatedStrategy else it
                }
                showSettingsSheet = false
            }
        )
    }
}

@Composable
private fun StrategiesOverviewCard(strategies: List<Strategy>) {
    val enabledCount = strategies.count { it.isEnabled }
    val totalPnL = strategies.sumOf { it.pnl }
    val totalTrades = strategies.sumOf { it.trades }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Strategies Overview",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                OverviewItem(
                    label = "Active",
                    value = "$enabledCount/${strategies.size}"
                )
                OverviewItem(
                    label = "Total Trades",
                    value = totalTrades.toString()
                )
                OverviewItem(
                    label = "Total PnL",
                    value = "${if (totalPnL >= 0) "+" else ""}$${String.format("%.0f", totalPnL)}",
                    valueColor = if (totalPnL >= 0) LongGreen else ShortRed
                )
            }
        }
    }
}

@Composable
private fun OverviewItem(
    label: String,
    value: String,
    valueColor: Color = MaterialTheme.colorScheme.onPrimaryContainer
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = valueColor
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
        )
    }
}

@Composable
private fun StrategyCard(
    strategy: Strategy,
    onToggle: (Boolean) -> Unit,
    onSettings: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(48.dp)
                            .clip(CircleShape)
                            .background(strategy.color.copy(alpha = 0.1f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            strategy.icon,
                            contentDescription = null,
                            tint = strategy.color,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                    
                    Column {
                        Text(
                            text = strategy.name,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = strategy.description,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                Switch(
                    checked = strategy.isEnabled,
                    onCheckedChange = onToggle,
                    colors = SwitchDefaults.colors(
                        checkedTrackColor = LongGreen
                    )
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Stats Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StatChip(
                    label = "Trades",
                    value = strategy.trades.toString()
                )
                StatChip(
                    label = "PnL",
                    value = "${if (strategy.pnl >= 0) "+" else ""}$${String.format("%.0f", strategy.pnl)}",
                    valueColor = if (strategy.pnl >= 0) LongGreen else ShortRed
                )
                StatChip(
                    label = "Win Rate",
                    value = "${String.format("%.0f", strategy.winRate)}%",
                    valueColor = if (strategy.winRate >= 50) LongGreen else ShortRed
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Direction indicators
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                DirectionChip(
                    label = "LONG",
                    enabled = strategy.longEnabled,
                    color = LongGreen
                )
                DirectionChip(
                    label = "SHORT",
                    enabled = strategy.shortEnabled,
                    color = ShortRed
                )
                
                Spacer(modifier = Modifier.weight(1f))
                
                // Settings Button
                IconButton(
                    onClick = onSettings,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        Icons.Default.Settings,
                        contentDescription = "Settings",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
private fun StatChip(
    label: String,
    value: String,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = valueColor
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun DirectionChip(
    label: String,
    enabled: Boolean,
    color: Color
) {
    Surface(
        shape = RoundedCornerShape(8.dp),
        color = if (enabled) color.copy(alpha = 0.1f) else MaterialTheme.colorScheme.surfaceVariant
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(if (enabled) color else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.3f))
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Medium,
                color = if (enabled) color else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun StrategySettingsSheet(
    strategy: Strategy,
    onDismiss: () -> Unit,
    onSave: (Strategy) -> Unit
) {
    var settings by remember { mutableStateOf(strategy.settings) }
    var longEnabled by remember { mutableStateOf(strategy.longEnabled) }
    var shortEnabled by remember { mutableStateOf(strategy.shortEnabled) }
    
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = MaterialTheme.colorScheme.surface
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "${strategy.name} Settings",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                IconButton(onClick = onDismiss) {
                    Icon(Icons.Default.Close, contentDescription = "Close")
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Direction Settings
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Direction",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Enable LONG")
                        Switch(
                            checked = longEnabled,
                            onCheckedChange = { longEnabled = it },
                            colors = SwitchDefaults.colors(checkedTrackColor = LongGreen)
                        )
                    }
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Enable SHORT")
                        Switch(
                            checked = shortEnabled,
                            onCheckedChange = { shortEnabled = it },
                            colors = SwitchDefaults.colors(checkedTrackColor = ShortRed)
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Trading Settings
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Trading Parameters",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    SettingSlider(
                        label = "Entry %",
                        value = settings.entryPercent,
                        range = 0.1f..10f,
                        format = "%.1f%%",
                        onValueChange = { settings = settings.copy(entryPercent = it.toDouble()) }
                    )
                    
                    SettingSlider(
                        label = "Take Profit %",
                        value = settings.tpPercent,
                        range = 0.5f..100f,
                        format = "%.1f%%",
                        onValueChange = { settings = settings.copy(tpPercent = it.toDouble()) }
                    )
                    
                    SettingSlider(
                        label = "Stop Loss %",
                        value = settings.slPercent,
                        range = 0.5f..100f,
                        format = "%.1f%%",
                        onValueChange = { settings = settings.copy(slPercent = it.toDouble()) }
                    )
                    
                    SettingSlider(
                        label = "Leverage",
                        value = settings.leverage.toDouble(),
                        range = 1f..100f,
                        format = "%.0fx",
                        onValueChange = { settings = settings.copy(leverage = it.toInt()) }
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // ATR Settings
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "ATR Trailing Stop",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Switch(
                            checked = settings.useAtr,
                            onCheckedChange = { settings = settings.copy(useAtr = it) }
                        )
                    }
                    
                    if (settings.useAtr) {
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        SettingSlider(
                            label = "ATR Periods",
                            value = settings.atrPeriods.toDouble(),
                            range = 3f..50f,
                            format = "%.0f",
                            onValueChange = { settings = settings.copy(atrPeriods = it.toInt()) }
                        )
                        
                        SettingSlider(
                            label = "ATR Multiplier (SL)",
                            value = settings.atrMultiplierSl,
                            range = 0.1f..5f,
                            format = "%.1f",
                            onValueChange = { settings = settings.copy(atrMultiplierSl = it.toDouble()) }
                        )
                        
                        SettingSlider(
                            label = "ATR Trigger %",
                            value = settings.atrTriggerPct,
                            range = 0.1f..10f,
                            format = "%.1f%%",
                            onValueChange = { settings = settings.copy(atrTriggerPct = it.toDouble()) }
                        )
                        
                        SettingSlider(
                            label = "ATR Step %",
                            value = settings.atrStepPct,
                            range = 0.05f..5f,
                            format = "%.2f%%",
                            onValueChange = { settings = settings.copy(atrStepPct = it.toDouble()) }
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Save Button
            Button(
                onClick = {
                    onSave(strategy.copy(
                        longEnabled = longEnabled,
                        shortEnabled = shortEnabled,
                        settings = settings
                    ))
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.Save, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Save Settings", fontWeight = FontWeight.Bold)
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
private fun SettingSlider(
    label: String,
    value: Double,
    range: ClosedFloatingPointRange<Float>,
    format: String,
    onValueChange: (Float) -> Unit
) {
    Column(modifier = Modifier.padding(vertical = 8.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = String.format(format, value),
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold
            )
        }
        
        Slider(
            value = value.toFloat().coerceIn(range),
            onValueChange = onValueChange,
            valueRange = range
        )
    }
}

// Default strategies with canonical settings from coin_params.py
private fun generateDefaultStrategies(): List<Strategy> {
    return listOf(
        Strategy(
            id = "oi",
            name = "OI Strategy",
            description = "Open Interest divergence signals",
            icon = Icons.Default.TrendingUp,
            color = Color(0xFF2196F3),
            isEnabled = true,
            longEnabled = true,
            shortEnabled = true,
            trades = 0,
            pnl = 0.0,
            winRate = 0.0,
            settings = StrategySettings()
        ),
        Strategy(
            id = "scryptomera",
            name = "Scryptomera",
            description = "Volume delta analysis",
            icon = Icons.Default.Speed,
            color = Color(0xFFE91E63),
            isEnabled = true,
            longEnabled = true,
            shortEnabled = true,
            trades = 0,
            pnl = 0.0,
            winRate = 0.0,
            settings = StrategySettings()
        ),
        Strategy(
            id = "scalper",
            name = "Scalper",
            description = "Momentum breakouts",
            icon = Icons.Default.FlashOn,
            color = Color(0xFFFF9800),
            isEnabled = true,
            longEnabled = true,
            shortEnabled = true,
            trades = 0,
            pnl = 0.0,
            winRate = 0.0,
            settings = StrategySettings()
        ),
        Strategy(
            id = "elcaro",
            name = "ENLIKO AI",
            description = "AI-powered trading signals",
            icon = Icons.Default.Psychology,
            color = Color(0xFF4CAF50),
            isEnabled = true,
            longEnabled = true,
            shortEnabled = true,
            trades = 0,
            pnl = 0.0,
            winRate = 0.0,
            settings = StrategySettings()
        ),
        Strategy(
            id = "fibonacci",
            name = "Fibonacci",
            description = "Fib retracement levels",
            icon = Icons.Default.AutoGraph,
            color = Color(0xFF9C27B0),
            isEnabled = true,
            longEnabled = true,
            shortEnabled = true,
            trades = 0,
            pnl = 0.0,
            winRate = 0.0,
            settings = StrategySettings()
        ),
        Strategy(
            id = "rsi_bb",
            name = "RSI + Bollinger",
            description = "RSI & Bollinger Bands",
            icon = Icons.Default.Assessment,
            color = Color(0xFF00BCD4),
            isEnabled = true,
            longEnabled = true,
            shortEnabled = true,
            trades = 0,
            pnl = 0.0,
            winRate = 0.0,
            settings = StrategySettings()
        )
    )
}
