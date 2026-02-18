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
 * RiskSettingsScreen - Matching iOS SubSettingsViews.swift RiskSettingsView
 * Configure Entry%, TP%, SL%, ATR and DCA settings
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RiskSettingsScreen(
    onBack: () -> Unit
) {
    val strings = LocalStrings.current
    var entryPercent by remember { mutableFloatStateOf(1f) }
    var tpPercent by remember { mutableFloatStateOf(8f) }
    var slPercent by remember { mutableFloatStateOf(3f) }
    var useATR by remember { mutableStateOf(false) }
    var atrPeriods by remember { mutableFloatStateOf(14f) }
    var atrMultiplier by remember { mutableFloatStateOf(1.5f) }
    var useDCA by remember { mutableStateOf(false) }
    var dcaLevel1 by remember { mutableFloatStateOf(10f) }
    var dcaLevel2 by remember { mutableFloatStateOf(25f) }
    var isSaving by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Risk Settings") },
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
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Position Sizing Section
            SettingsSectionCard(title = "Position Sizing") {
                // Entry %
                PercentageSlider(
                    label = "Entry %",
                    description = "Percentage of equity to use per trade",
                    value = entryPercent,
                    onValueChange = { entryPercent = it },
                    valueRange = 0.5f..10f,
                    icon = Icons.Default.AccountBalanceWallet
                )
            }
            
            // Take Profit & Stop Loss Section
            SettingsSectionCard(title = "TP / SL Settings") {
                // Take Profit %
                PercentageSlider(
                    label = "Take Profit %",
                    description = "Close position when profit reaches this %",
                    value = tpPercent,
                    onValueChange = { tpPercent = it },
                    valueRange = 1f..50f,
                    icon = Icons.Default.TrendingUp,
                    color = EnlikoGreen
                )
                
                Divider(color = EnlikoBorder, modifier = Modifier.padding(vertical = 8.dp))
                
                // Stop Loss %
                PercentageSlider(
                    label = "Stop Loss %",
                    description = "Close position when loss reaches this %",
                    value = slPercent,
                    onValueChange = { slPercent = it },
                    valueRange = 0.5f..20f,
                    icon = Icons.Default.TrendingDown,
                    color = EnlikoRed
                )
            }
            
            // ATR Section
            SettingsSectionCard(title = "ATR Settings") {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = strings.useAtrForSlTp,
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Medium,
                            color = EnlikoTextPrimary
                        )
                        Text(
                            text = strings.dynamicLevelsVolatility,
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                    Switch(
                        checked = useATR,
                        onCheckedChange = { useATR = it },
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = EnlikoPrimary,
                            checkedTrackColor = EnlikoPrimary.copy(alpha = 0.5f)
                        )
                    )
                }
                
                if (useATR) {
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // ATR Periods
                    Column {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = strings.atrPeriods,
                                style = MaterialTheme.typography.bodyMedium,
                                color = EnlikoTextSecondary
                            )
                            Text(
                                text = "${atrPeriods.toInt()}",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = EnlikoPrimary
                            )
                        }
                        Slider(
                            value = atrPeriods,
                            onValueChange = { atrPeriods = it },
                            valueRange = 7f..50f,
                            steps = 43,
                            colors = SliderDefaults.colors(
                                thumbColor = EnlikoPrimary,
                                activeTrackColor = EnlikoPrimary,
                                inactiveTrackColor = EnlikoSurface
                            )
                        )
                    }
                    
                    // ATR Multiplier
                    Column {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = strings.atrMultiplier,
                                style = MaterialTheme.typography.bodyMedium,
                                color = EnlikoTextSecondary
                            )
                            Text(
                                text = String.format("%.1fx", atrMultiplier),
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = EnlikoPrimary
                            )
                        }
                        Slider(
                            value = atrMultiplier,
                            onValueChange = { atrMultiplier = it },
                            valueRange = 0.5f..5f,
                            colors = SliderDefaults.colors(
                                thumbColor = EnlikoPrimary,
                                activeTrackColor = EnlikoPrimary,
                                inactiveTrackColor = EnlikoSurface
                            )
                        )
                    }
                }
            }
            
            // DCA Section
            SettingsSectionCard(title = "DCA Settings") {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = strings.enableDca,
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Medium,
                            color = EnlikoTextPrimary
                        )
                        Text(
                            text = strings.dcaDollarCostAvg,
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                    Switch(
                        checked = useDCA,
                        onCheckedChange = { useDCA = it },
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = EnlikoPrimary,
                            checkedTrackColor = EnlikoPrimary.copy(alpha = 0.5f)
                        )
                    )
                }
                
                if (useDCA) {
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // DCA Level 1
                    Column {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = strings.dcaLevel1Trigger,
                                style = MaterialTheme.typography.bodyMedium,
                                color = EnlikoTextSecondary
                            )
                            Text(
                                text = "-${dcaLevel1.toInt()}%",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = EnlikoYellow
                            )
                        }
                        Slider(
                            value = dcaLevel1,
                            onValueChange = { dcaLevel1 = it },
                            valueRange = 5f..30f,
                            colors = SliderDefaults.colors(
                                thumbColor = EnlikoYellow,
                                activeTrackColor = EnlikoYellow,
                                inactiveTrackColor = EnlikoSurface
                            )
                        )
                        Text(
                            text = "Add to position when unrealized loss reaches ${dcaLevel1.toInt()}%",
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // DCA Level 2
                    Column {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = strings.dcaLevel2Trigger,
                                style = MaterialTheme.typography.bodyMedium,
                                color = EnlikoTextSecondary
                            )
                            Text(
                                text = "-${dcaLevel2.toInt()}%",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = EnlikoRed
                            )
                        }
                        Slider(
                            value = dcaLevel2,
                            onValueChange = { dcaLevel2 = it },
                            valueRange = 15f..50f,
                            colors = SliderDefaults.colors(
                                thumbColor = EnlikoRed,
                                activeTrackColor = EnlikoRed,
                                inactiveTrackColor = EnlikoSurface
                            )
                        )
                        Text(
                            text = "Add to position when unrealized loss reaches ${dcaLevel2.toInt()}%",
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                }
            }
            
            // Risk/Reward Display
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = EnlikoPrimary.copy(alpha = 0.1f)),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = strings.riskRewardAnalysis,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold,
                        color = EnlikoPrimary
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                text = String.format("%.1f:1", tpPercent / slPercent),
                                style = MaterialTheme.typography.headlineSmall,
                                fontWeight = FontWeight.Bold,
                                color = EnlikoPrimary
                            )
                            Text(
                                text = strings.rrRatio,
                                style = MaterialTheme.typography.bodySmall,
                                color = EnlikoTextSecondary
                            )
                        }
                        
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                text = String.format("%.0f%%", 100 / (1 + tpPercent / slPercent)),
                                style = MaterialTheme.typography.headlineSmall,
                                fontWeight = FontWeight.Bold,
                                color = EnlikoTextPrimary
                            )
                            Text(
                                text = strings.minWinRate,
                                style = MaterialTheme.typography.bodySmall,
                                color = EnlikoTextSecondary
                            )
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Save Button
            Button(
                onClick = {
                    isSaving = true
                    // TODO: Save settings to server
                    isSaving = false
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                enabled = !isSaving,
                colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary),
                shape = RoundedCornerShape(12.dp)
            ) {
                if (isSaving) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White,
                        strokeWidth = 2.dp
                    )
                } else {
                    Text("Save Risk Settings", fontWeight = FontWeight.SemiBold)
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
private fun SettingsSectionCard(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = EnlikoTextPrimary
            )
            content()
        }
    }
}

@Composable
private fun PercentageSlider(
    label: String,
    description: String,
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float>,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color = EnlikoPrimary
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
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
                    icon,
                    contentDescription = null,
                    tint = color,
                    modifier = Modifier.size(20.dp)
                )
                Text(
                    text = label,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Medium,
                    color = EnlikoTextPrimary
                )
            }
            Text(
                text = String.format("%.1f%%", value),
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.SemiBold,
                color = color
            )
        }
        
        Slider(
            value = value,
            onValueChange = onValueChange,
            valueRange = valueRange,
            colors = SliderDefaults.colors(
                thumbColor = color,
                activeTrackColor = color,
                inactiveTrackColor = EnlikoSurface
            )
        )
        
        Text(
            text = description,
            style = MaterialTheme.typography.bodySmall,
            color = EnlikoTextSecondary
        )
    }
}
