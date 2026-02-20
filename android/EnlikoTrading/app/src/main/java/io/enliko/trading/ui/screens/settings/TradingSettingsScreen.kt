package io.enliko.trading.ui.screens.settings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.LocalStrings

/**
 * TradingSettingsScreen - Matching iOS TradingSettingsView.swift
 * Global trading settings: DCA, Order Type, Spot, ATR, Exchanges
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TradingSettingsScreen(
    onBack: () -> Unit
) {
    val strings = LocalStrings.current
    // Order Settings
    var orderType by remember { mutableStateOf("market") }
    var limitOffsetPct by remember { mutableFloatStateOf(0.1f) }
    
    // DCA Settings
    var dcaEnabled by remember { mutableStateOf(false) }
    var dcaPct1 by remember { mutableFloatStateOf(10f) }
    var dcaPct2 by remember { mutableFloatStateOf(25f) }
    
    // Spot Trading
    var spotEnabled by remember { mutableStateOf(false) }
    var spotDcaEnabled by remember { mutableStateOf(false) }
    var spotDcaPct by remember { mutableFloatStateOf(5f) }
    
    // ATR Settings
    var useAtr by remember { mutableStateOf(false) }
    var atrPeriods by remember { mutableIntStateOf(14) }
    var atrTriggerPct by remember { mutableFloatStateOf(0.5f) }
    var atrStepPct by remember { mutableFloatStateOf(0.25f) }
    
    // Exchanges
    var bybitEnabled by remember { mutableStateOf(true) }
    var hyperliquidEnabled by remember { mutableStateOf(false) }
    val bybitConfigured = true // TODO: Get from API
    val hyperliquidConfigured = false // TODO: Get from API
    
    var isSaving by remember { mutableStateOf(false) }
    var showSaveSuccess by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(strings.tradingSettingsTitle) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = strings.back)
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
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Order Type Section
            SettingsSection(title = "Order Settings") {
                // Order Type Selector
                Column {
                    Text(
                        text = strings.orderType,
                        style = MaterialTheme.typography.labelMedium,
                        color = EnlikoTextSecondary,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf("market" to "Market", "limit" to "Limit").forEach { (value, label) ->
                            FilterChip(
                                selected = orderType == value,
                                onClick = { orderType = value },
                                label = { Text(label) },
                                modifier = Modifier.weight(1f),
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = EnlikoPrimary,
                                    selectedLabelColor = Color.White
                                )
                            )
                        }
                    }
                }
                
                // Limit Offset (shown only for limit orders)
                if (orderType == "limit") {
                    Spacer(modifier = Modifier.height(8.dp))
                    SettingsSlider(
                        label = "Limit Offset",
                        value = limitOffsetPct,
                        onValueChange = { limitOffsetPct = it },
                        valueRange = 0.05f..1f,
                        steps = 18,
                        suffix = "%"
                    )
                }
                
                Text(
                    text = strings.marketOrdersDesc,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextMuted,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
            
            // DCA Section
            SettingsSection(title = "DCA Settings") {
                SettingsToggle(
                    title = "Enable DCA",
                    subtitle = "Dollar Cost Averaging for position building",
                    checked = dcaEnabled,
                    onCheckedChange = { dcaEnabled = it }
                )
                
                if (dcaEnabled) {
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    SettingsSlider(
                        label = "DCA Level 1",
                        value = dcaPct1,
                        onValueChange = { dcaPct1 = it },
                        valueRange = 5f..50f,
                        steps = 8,
                        suffix = "%"
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    SettingsSlider(
                        label = "DCA Level 2",
                        value = dcaPct2,
                        onValueChange = { dcaPct2 = it },
                        valueRange = 10f..100f,
                        steps = 17,
                        suffix = "%"
                    )
                }
                
                Text(
                    text = strings.dcaAddsDesc,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextMuted,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
            
            // Spot Trading Section
            SettingsSection(title = "Spot Trading") {
                SettingsToggle(
                    title = "Enable Spot Trading",
                    subtitle = "Trade spot markets alongside futures",
                    checked = spotEnabled,
                    onCheckedChange = { spotEnabled = it }
                )
                
                if (spotEnabled) {
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    SettingsToggle(
                        title = "Spot Auto DCA",
                        subtitle = "Automatically DCA spot positions",
                        checked = spotDcaEnabled,
                        onCheckedChange = { spotDcaEnabled = it }
                    )
                    
                    if (spotDcaEnabled) {
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        SettingsSlider(
                            label = "Spot DCA Percentage",
                            value = spotDcaPct,
                            onValueChange = { spotDcaPct = it },
                            valueRange = 1f..20f,
                            steps = 18,
                            suffix = "%"
                        )
                    }
                }
            }
            
            // ATR Section
            SettingsSection(title = "ATR Trailing Stop") {
                SettingsToggle(
                    title = "Use ATR",
                    subtitle = "Dynamic stop-loss based on volatility",
                    checked = useAtr,
                    onCheckedChange = { useAtr = it }
                )
                
                if (useAtr) {
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // ATR Periods
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "ATR Periods: $atrPeriods",
                            style = MaterialTheme.typography.bodyMedium,
                            color = EnlikoTextPrimary
                        )
                        
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            FilledIconButton(
                                onClick = { if (atrPeriods > 5) atrPeriods-- },
                                enabled = atrPeriods > 5,
                                colors = IconButtonDefaults.filledIconButtonColors(
                                    containerColor = EnlikoCard
                                ),
                                modifier = Modifier.size(36.dp)
                            ) {
                                Icon(Icons.Default.Remove, contentDescription = "Decrease")
                            }
                            
                            FilledIconButton(
                                onClick = { if (atrPeriods < 50) atrPeriods++ },
                                enabled = atrPeriods < 50,
                                colors = IconButtonDefaults.filledIconButtonColors(
                                    containerColor = EnlikoCard
                                ),
                                modifier = Modifier.size(36.dp)
                            ) {
                                Icon(Icons.Default.Add, contentDescription = "Increase")
                            }
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    SettingsSlider(
                        label = "ATR Trigger",
                        value = atrTriggerPct,
                        onValueChange = { atrTriggerPct = it },
                        valueRange = 0.1f..2f,
                        steps = 18,
                        suffix = "%"
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    SettingsSlider(
                        label = "ATR Step",
                        value = atrStepPct,
                        onValueChange = { atrStepPct = it },
                        valueRange = 0.1f..1f,
                        steps = 8,
                        suffix = "%"
                    )
                }
                
                Text(
                    text = strings.atrTrailingDesc,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextMuted,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
            
            // Exchanges Section
            SettingsSection(title = "Exchanges") {
                ExchangeToggleRow(
                    name = "Bybit",
                    color = EnlikoBybit,
                    isConfigured = bybitConfigured,
                    isEnabled = bybitEnabled,
                    onEnabledChange = { bybitEnabled = it }
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                ExchangeToggleRow(
                    name = "HyperLiquid",
                    color = EnlikoHL,
                    isConfigured = hyperliquidConfigured,
                    isEnabled = hyperliquidEnabled,
                    onEnabledChange = { hyperliquidEnabled = it }
                )
                
                Text(
                    text = strings.exchangeEnableDesc,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextMuted,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
            
            // Save Button
            Button(
                onClick = {
                    isSaving = true
                    // TODO: Save settings to API
                    showSaveSuccess = true
                    isSaving = false
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                enabled = !isSaving,
                colors = ButtonDefaults.buttonColors(
                    containerColor = EnlikoPrimary
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                if (isSaving) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White,
                        strokeWidth = 2.dp
                    )
                } else {
                    Text("Save Settings", fontWeight = FontWeight.SemiBold)
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
    
    // Success Snackbar
    if (showSaveSuccess) {
        LaunchedEffect(Unit) {
            kotlinx.coroutines.delay(2000)
            showSaveSuccess = false
        }
    }
}

@Composable
private fun SettingsSection(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = EnlikoTextPrimary,
                modifier = Modifier.padding(bottom = 12.dp)
            )
            content()
        }
    }
}

@Composable
private fun SettingsToggle(
    title: String,
    subtitle: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium,
                color = EnlikoTextPrimary
            )
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodySmall,
                color = EnlikoTextSecondary
            )
        }
        
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = Color.White,
                checkedTrackColor = EnlikoPrimary,
                uncheckedThumbColor = EnlikoTextMuted,
                uncheckedTrackColor = EnlikoSurface
            )
        )
    }
}

@Composable
private fun SettingsSlider(
    label: String,
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float>,
    steps: Int = 0,
    suffix: String = ""
) {
    Column {
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
                text = "${String.format("%.2f", value)}$suffix",
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
                activeTrackColor = EnlikoPrimary,
                inactiveTrackColor = EnlikoSurface
            )
        )
    }
}

@Composable
private fun ExchangeToggleRow(
    name: String,
    color: Color,
    isConfigured: Boolean,
    isEnabled: Boolean,
    onEnabledChange: (Boolean) -> Unit
) {
    val strings = LocalStrings.current
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Circle,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(12.dp)
            )
            Text(
                text = name,
                style = MaterialTheme.typography.bodyLarge,
                color = EnlikoTextPrimary
            )
        }
        
        if (isConfigured) {
            Switch(
                checked = isEnabled,
                onCheckedChange = onEnabledChange,
                colors = SwitchDefaults.colors(
                    checkedThumbColor = Color.White,
                    checkedTrackColor = EnlikoPrimary,
                    uncheckedThumbColor = EnlikoTextMuted,
                    uncheckedTrackColor = EnlikoSurface
                )
            )
        } else {
            Text(
                text = strings.notConfigured,
                style = MaterialTheme.typography.bodySmall,
                color = EnlikoTextMuted
            )
        }
    }
}
