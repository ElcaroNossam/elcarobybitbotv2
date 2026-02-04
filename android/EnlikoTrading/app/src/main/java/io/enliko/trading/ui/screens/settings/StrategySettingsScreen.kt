package io.enliko.trading.ui.screens.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
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
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.Localization

/**
 * StrategySettingsScreen - Matching iOS StrategySettingsView.swift
 * Features: Long/Short side settings, ATR, DCA, Break-Even, Partial TP
 */

// Data classes matching iOS
data class StrategyInfo(
    val code: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color,
    val supportsAtr: Boolean = true,
    val supportsDca: Boolean = true,
    val supportsBE: Boolean = true,
    val supportsPartialTP: Boolean = true
) {
    companion object {
        val all = listOf(
            StrategyInfo("oi", "Open Interest", "OI divergence signals", Icons.Default.BarChart, Color(0xFF2196F3)),
            StrategyInfo("scryptomera", "Scryptomera", "Volume delta analysis", Icons.Default.GraphicEq, Color(0xFF9C27B0)),
            StrategyInfo("scalper", "Scalper", "Momentum breakouts", Icons.Default.FlashOn, Color(0xFFFF9800)),
            StrategyInfo("elcaro", "ENLIKO AI", "AI-powered signals", Icons.Default.Psychology, Color(0xFF4CAF50), supportsAtr = false, supportsDca = false),
            StrategyInfo("fibonacci", "Fibonacci", "Fib retracement levels", Icons.Default.Functions, Color(0xFF00BCD4)),
            StrategyInfo("rsi_bb", "RSI + BB", "RSI & Bollinger Bands", Icons.Default.ShowChart, Color(0xFFE91E63))
        )
    }
}

data class SideSettings(
    var enabled: Boolean = true,
    var percent: Double = 1.0,
    var tpPercent: Double = 8.0,
    var slPercent: Double = 3.0,
    var leverage: Int = 10,
    var useAtr: Boolean = false,
    var atrTriggerPct: Double = 0.5,
    var atrStepPct: Double = 0.25,
    var dcaEnabled: Boolean = false,
    var dcaPct1: Double = 10.0,
    var dcaPct2: Double = 25.0,
    var orderType: String = "market",
    var maxPositions: Int = 0,
    var coinsGroup: String = "ALL",
    // Break-Even
    var beEnabled: Boolean = false,
    var beTriggerPct: Double = 1.0,
    // Partial Take Profit
    var partialTpEnabled: Boolean = false,
    var partialTp1TriggerPct: Double = 2.0,
    var partialTp1ClosePct: Double = 30.0,
    var partialTp2TriggerPct: Double = 5.0,
    var partialTp2ClosePct: Double = 50.0
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StrategySettingsScreen(
    strategyCode: String,
    onBack: () -> Unit,
    viewModel: StrategySettingsViewModel = hiltViewModel()
) {
    val strategy = remember(strategyCode) {
        StrategyInfo.all.find { it.code == strategyCode } ?: StrategyInfo.all[0]
    }
    
    var selectedSide by remember { mutableStateOf("long") }
    var longSettings by remember { mutableStateOf(SideSettings()) }
    var shortSettings by remember { mutableStateOf(SideSettings()) }
    var isLoading by remember { mutableStateOf(false) }
    var showSaveSuccess by remember { mutableStateOf(false) }
    
    val currentSettings = if (selectedSide == "long") longSettings else shortSettings
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("${strategy.name} Settings") },
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
            // Strategy Info Header
            item {
                StrategyHeader(strategy = strategy)
            }
            
            // Side Selector (Long/Short)
            item {
                SideSelector(
                    selectedSide = selectedSide,
                    onSideChange = { selectedSide = it },
                    longEnabled = longSettings.enabled,
                    shortEnabled = shortSettings.enabled
                )
            }
            
            // Enable/Disable Toggle
            item {
                EnableToggleCard(
                    side = selectedSide,
                    isEnabled = currentSettings.enabled,
                    onToggle = {
                        if (selectedSide == "long") {
                            longSettings = longSettings.copy(enabled = !longSettings.enabled)
                        } else {
                            shortSettings = shortSettings.copy(enabled = !shortSettings.enabled)
                        }
                    }
                )
            }
            
            // Core Settings
            item {
                CoreSettingsCard(
                    settings = currentSettings,
                    onSettingsChange = { newSettings ->
                        if (selectedSide == "long") {
                            longSettings = newSettings
                        } else {
                            shortSettings = newSettings
                        }
                    }
                )
            }
            
            // ATR Settings (if supported)
            if (strategy.supportsAtr) {
                item {
                    AtrSettingsCard(
                        useAtr = currentSettings.useAtr,
                        atrTriggerPct = currentSettings.atrTriggerPct,
                        atrStepPct = currentSettings.atrStepPct,
                        onUseAtrChange = { useAtr ->
                            if (selectedSide == "long") {
                                longSettings = longSettings.copy(useAtr = useAtr)
                            } else {
                                shortSettings = shortSettings.copy(useAtr = useAtr)
                            }
                        },
                        onTriggerChange = { trigger ->
                            if (selectedSide == "long") {
                                longSettings = longSettings.copy(atrTriggerPct = trigger)
                            } else {
                                shortSettings = shortSettings.copy(atrTriggerPct = trigger)
                            }
                        },
                        onStepChange = { step ->
                            if (selectedSide == "long") {
                                longSettings = longSettings.copy(atrStepPct = step)
                            } else {
                                shortSettings = shortSettings.copy(atrStepPct = step)
                            }
                        }
                    )
                }
            }
            
            // Break-Even Settings (if supported)
            if (strategy.supportsBE) {
                item {
                    BreakEvenCard(
                        beEnabled = currentSettings.beEnabled,
                        beTriggerPct = currentSettings.beTriggerPct,
                        onEnabledChange = { enabled ->
                            if (selectedSide == "long") {
                                longSettings = longSettings.copy(beEnabled = enabled)
                            } else {
                                shortSettings = shortSettings.copy(beEnabled = enabled)
                            }
                        },
                        onTriggerChange = { trigger ->
                            if (selectedSide == "long") {
                                longSettings = longSettings.copy(beTriggerPct = trigger)
                            } else {
                                shortSettings = shortSettings.copy(beTriggerPct = trigger)
                            }
                        }
                    )
                }
            }
            
            // Partial TP Settings (if supported)
            if (strategy.supportsPartialTP) {
                item {
                    PartialTpCard(
                        settings = currentSettings,
                        onSettingsChange = { newSettings ->
                            if (selectedSide == "long") {
                                longSettings = newSettings
                            } else {
                                shortSettings = newSettings
                            }
                        }
                    )
                }
            }
            
            // DCA Settings (if supported)
            if (strategy.supportsDca) {
                item {
                    DcaSettingsCard(
                        dcaEnabled = currentSettings.dcaEnabled,
                        dcaPct1 = currentSettings.dcaPct1,
                        dcaPct2 = currentSettings.dcaPct2,
                        onEnabledChange = { enabled ->
                            if (selectedSide == "long") {
                                longSettings = longSettings.copy(dcaEnabled = enabled)
                            } else {
                                shortSettings = shortSettings.copy(dcaEnabled = enabled)
                            }
                        },
                        onPct1Change = { pct ->
                            if (selectedSide == "long") {
                                longSettings = longSettings.copy(dcaPct1 = pct)
                            } else {
                                shortSettings = shortSettings.copy(dcaPct1 = pct)
                            }
                        },
                        onPct2Change = { pct ->
                            if (selectedSide == "long") {
                                longSettings = longSettings.copy(dcaPct2 = pct)
                            } else {
                                shortSettings = shortSettings.copy(dcaPct2 = pct)
                            }
                        }
                    )
                }
            }
            
            // Save Button
            item {
                Button(
                    onClick = {
                        // TODO: Save to API
                        showSaveSuccess = true
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Default.Save, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(Localization.get("save"), fontWeight = FontWeight.SemiBold)
                }
            }
            
            item { Spacer(modifier = Modifier.height(32.dp)) }
        }
    }
    
    // Save success snackbar
    if (showSaveSuccess) {
        LaunchedEffect(Unit) {
            kotlinx.coroutines.delay(2000)
            showSaveSuccess = false
        }
    }
}

@Composable
private fun StrategyHeader(strategy: StrategyInfo) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(strategy.color.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = strategy.icon,
                    contentDescription = null,
                    tint = strategy.color,
                    modifier = Modifier.size(24.dp)
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column {
                Text(
                    text = strategy.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = EnlikoTextPrimary
                )
                Text(
                    text = strategy.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextSecondary
                )
            }
        }
    }
}

@Composable
private fun SideSelector(
    selectedSide: String,
    onSideChange: (String) -> Unit,
    longEnabled: Boolean,
    shortEnabled: Boolean
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Long Button
        SideSelectorButton(
            title = "LONG",
            isSelected = selectedSide == "long",
            isEnabled = longEnabled,
            color = EnlikoGreen,
            onClick = { onSideChange("long") },
            modifier = Modifier.weight(1f)
        )
        
        // Short Button
        SideSelectorButton(
            title = "SHORT",
            isSelected = selectedSide == "short",
            isEnabled = shortEnabled,
            color = EnlikoRed,
            onClick = { onSideChange("short") },
            modifier = Modifier.weight(1f)
        )
    }
}

@Composable
private fun SideSelectorButton(
    title: String,
    isSelected: Boolean,
    isEnabled: Boolean,
    color: Color,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .then(
                if (isSelected) Modifier.border(2.dp, color, RoundedCornerShape(12.dp))
                else Modifier
            ),
        color = if (isSelected) color.copy(alpha = 0.15f) else EnlikoCard
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(if (isEnabled) color else EnlikoTextMuted)
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = if (isSelected) color else EnlikoTextSecondary
            )
        }
    }
}

@Composable
private fun EnableToggleCard(
    side: String,
    isEnabled: Boolean,
    onToggle: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
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
                    text = "${side.uppercase()} Trading",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium,
                    color = EnlikoTextPrimary
                )
                Text(
                    text = if (isEnabled) "Active" else "Disabled",
                    style = MaterialTheme.typography.bodySmall,
                    color = if (isEnabled) EnlikoGreen else EnlikoTextMuted
                )
            }
            
            Switch(
                checked = isEnabled,
                onCheckedChange = { onToggle() },
                colors = SwitchDefaults.colors(
                    checkedThumbColor = if (side == "long") EnlikoGreen else EnlikoRed,
                    checkedTrackColor = (if (side == "long") EnlikoGreen else EnlikoRed).copy(alpha = 0.5f)
                )
            )
        }
    }
}

@Composable
private fun CoreSettingsCard(
    settings: SideSettings,
    onSettingsChange: (SideSettings) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = Localization.get("core_settings"),
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Entry %
            SettingSlider(
                label = Localization.get("entry_pct"),
                value = settings.percent.toFloat(),
                onValueChange = { onSettingsChange(settings.copy(percent = it.toDouble())) },
                valueRange = 0.1f..10f,
                suffix = "%"
            )
            
            // Take Profit %
            SettingSlider(
                label = Localization.get("take_profit_pct"),
                value = settings.tpPercent.toFloat(),
                onValueChange = { onSettingsChange(settings.copy(tpPercent = it.toDouble())) },
                valueRange = 0.5f..50f,
                suffix = "%"
            )
            
            // Stop Loss %
            SettingSlider(
                label = Localization.get("stop_loss_pct"),
                value = settings.slPercent.toFloat(),
                onValueChange = { onSettingsChange(settings.copy(slPercent = it.toDouble())) },
                valueRange = 0.5f..20f,
                suffix = "%"
            )
            
            // Leverage
            SettingSlider(
                label = Localization.get("leverage"),
                value = settings.leverage.toFloat(),
                onValueChange = { onSettingsChange(settings.copy(leverage = it.toInt())) },
                valueRange = 1f..50f,
                suffix = "x",
                steps = 49
            )
        }
    }
}

@Composable
private fun SettingSlider(
    label: String,
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float>,
    suffix: String,
    steps: Int = 0
) {
    Column(modifier = Modifier.padding(vertical = 8.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = EnlikoTextSecondary
            )
            Text(
                text = "${String.format("%.1f", value)}$suffix",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = EnlikoPrimary
            )
        }
        
        Slider(
            value = value,
            onValueChange = onValueChange,
            valueRange = valueRange,
            steps = steps,
            colors = SliderDefaults.colors(
                thumbColor = EnlikoPrimary,
                activeTrackColor = EnlikoPrimary
            )
        )
    }
}

@Composable
private fun AtrSettingsCard(
    useAtr: Boolean,
    atrTriggerPct: Double,
    atrStepPct: Double,
    onUseAtrChange: (Boolean) -> Unit,
    onTriggerChange: (Double) -> Unit,
    onStepChange: (Double) -> Unit
) {
    ExpandableSettingsCard(
        title = "ATR Trailing Stop",
        isEnabled = useAtr,
        onToggle = { onUseAtrChange(!useAtr) }
    ) {
        SettingSlider(
            label = "Trigger %",
            value = atrTriggerPct.toFloat(),
            onValueChange = { onTriggerChange(it.toDouble()) },
            valueRange = 0.1f..5f,
            suffix = "%"
        )
        
        SettingSlider(
            label = "Step %",
            value = atrStepPct.toFloat(),
            onValueChange = { onStepChange(it.toDouble()) },
            valueRange = 0.05f..2f,
            suffix = "%"
        )
    }
}

@Composable
private fun BreakEvenCard(
    beEnabled: Boolean,
    beTriggerPct: Double,
    onEnabledChange: (Boolean) -> Unit,
    onTriggerChange: (Double) -> Unit
) {
    ExpandableSettingsCard(
        title = "Break-Even",
        isEnabled = beEnabled,
        onToggle = { onEnabledChange(!beEnabled) }
    ) {
        SettingSlider(
            label = "Trigger %",
            value = beTriggerPct.toFloat(),
            onValueChange = { onTriggerChange(it.toDouble()) },
            valueRange = 0.1f..10f,
            suffix = "%"
        )
        
        Text(
            text = "Move SL to entry when profit reaches trigger",
            style = MaterialTheme.typography.bodySmall,
            color = EnlikoTextMuted
        )
    }
}

@Composable
private fun PartialTpCard(
    settings: SideSettings,
    onSettingsChange: (SideSettings) -> Unit
) {
    ExpandableSettingsCard(
        title = "Partial Take Profit",
        isEnabled = settings.partialTpEnabled,
        onToggle = { onSettingsChange(settings.copy(partialTpEnabled = !settings.partialTpEnabled)) }
    ) {
        Text(
            text = "Step 1",
            style = MaterialTheme.typography.labelMedium,
            color = EnlikoPrimary
        )
        
        SettingSlider(
            label = "Trigger %",
            value = settings.partialTp1TriggerPct.toFloat(),
            onValueChange = { onSettingsChange(settings.copy(partialTp1TriggerPct = it.toDouble())) },
            valueRange = 0.5f..20f,
            suffix = "%"
        )
        
        SettingSlider(
            label = "Close %",
            value = settings.partialTp1ClosePct.toFloat(),
            onValueChange = { onSettingsChange(settings.copy(partialTp1ClosePct = it.toDouble())) },
            valueRange = 10f..50f,
            suffix = "%"
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "Step 2",
            style = MaterialTheme.typography.labelMedium,
            color = EnlikoPrimary
        )
        
        SettingSlider(
            label = "Trigger %",
            value = settings.partialTp2TriggerPct.toFloat(),
            onValueChange = { onSettingsChange(settings.copy(partialTp2TriggerPct = it.toDouble())) },
            valueRange = 1f..30f,
            suffix = "%"
        )
        
        SettingSlider(
            label = "Close %",
            value = settings.partialTp2ClosePct.toFloat(),
            onValueChange = { onSettingsChange(settings.copy(partialTp2ClosePct = it.toDouble())) },
            valueRange = 10f..70f,
            suffix = "%"
        )
    }
}

@Composable
private fun DcaSettingsCard(
    dcaEnabled: Boolean,
    dcaPct1: Double,
    dcaPct2: Double,
    onEnabledChange: (Boolean) -> Unit,
    onPct1Change: (Double) -> Unit,
    onPct2Change: (Double) -> Unit
) {
    ExpandableSettingsCard(
        title = "DCA (Dollar Cost Averaging)",
        isEnabled = dcaEnabled,
        onToggle = { onEnabledChange(!dcaEnabled) }
    ) {
        SettingSlider(
            label = "DCA 1 trigger",
            value = dcaPct1.toFloat(),
            onValueChange = { onPct1Change(it.toDouble()) },
            valueRange = 5f..30f,
            suffix = "%"
        )
        
        SettingSlider(
            label = "DCA 2 trigger",
            value = dcaPct2.toFloat(),
            onValueChange = { onPct2Change(it.toDouble()) },
            valueRange = 10f..50f,
            suffix = "%"
        )
        
        Text(
            text = "Add to position when loss reaches trigger %",
            style = MaterialTheme.typography.bodySmall,
            color = EnlikoTextMuted
        )
    }
}

@Composable
private fun ExpandableSettingsCard(
    title: String,
    isEnabled: Boolean,
    onToggle: () -> Unit,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = EnlikoTextPrimary
                )
                
                Switch(
                    checked = isEnabled,
                    onCheckedChange = { onToggle() },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = EnlikoPrimary,
                        checkedTrackColor = EnlikoPrimary.copy(alpha = 0.5f)
                    )
                )
            }
            
            if (isEnabled) {
                Spacer(modifier = Modifier.height(16.dp))
                HorizontalDivider(color = EnlikoBorder)
                Spacer(modifier = Modifier.height(16.dp))
                content()
            }
        }
    }
}
