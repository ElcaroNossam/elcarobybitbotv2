package io.enliko.trading.ui.screens.settings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*

/**
 * LeverageSettingsScreen - Matching iOS SubSettingsViews.swift LeverageSettingsView
 * Configure leverage settings with slider and quick select buttons
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LeverageSettingsScreen(
    currentLeverage: Int = 10,
    onLeverageChange: (Int) -> Unit = {},
    onBack: () -> Unit
) {
    var leverage by remember { mutableFloatStateOf(currentLeverage.toFloat()) }
    var isSaving by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Leverage Settings") },
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
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Current Leverage Display
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = EnlikoCard),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Current Leverage",
                        style = MaterialTheme.typography.titleSmall,
                        color = EnlikoTextSecondary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "${leverage.toInt()}x",
                        style = MaterialTheme.typography.displayMedium,
                        fontWeight = FontWeight.Bold,
                        color = getLeverageColor(leverage.toInt())
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = getRiskLevel(leverage.toInt()),
                        style = MaterialTheme.typography.bodySmall,
                        color = getLeverageColor(leverage.toInt())
                    )
                }
            }
            
            // Leverage Slider
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = EnlikoCard),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Text(
                        text = "Adjust Leverage",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = EnlikoTextPrimary
                    )
                    
                    Slider(
                        value = leverage,
                        onValueChange = { leverage = it },
                        valueRange = 1f..100f,
                        steps = 99,
                        colors = SliderDefaults.colors(
                            thumbColor = getLeverageColor(leverage.toInt()),
                            activeTrackColor = getLeverageColor(leverage.toInt()),
                            inactiveTrackColor = EnlikoSurface
                        ),
                        modifier = Modifier.fillMaxWidth()
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "1x",
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                        Text(
                            text = "100x",
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                }
            }
            
            // Quick Select Buttons
            Text(
                text = "Quick Select",
                style = MaterialTheme.typography.titleSmall,
                color = EnlikoTextSecondary
            )
            
            // Row 1: 1x - 5x
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(1, 2, 3, 5).forEach { value ->
                    LeverageQuickButton(
                        leverage = value,
                        isSelected = leverage.toInt() == value,
                        onClick = { leverage = value.toFloat() },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            // Row 2: 10x - 25x
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(10, 15, 20, 25).forEach { value ->
                    LeverageQuickButton(
                        leverage = value,
                        isSelected = leverage.toInt() == value,
                        onClick = { leverage = value.toFloat() },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            // Row 3: 50x - 100x
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(50, 75, 100).forEach { value ->
                    LeverageQuickButton(
                        leverage = value,
                        isSelected = leverage.toInt() == value,
                        onClick = { leverage = value.toFloat() },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            // Risk Warning
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = when {
                        leverage.toInt() >= 50 -> EnlikoRed.copy(alpha = 0.1f)
                        leverage.toInt() >= 20 -> EnlikoYellow.copy(alpha = 0.1f)
                        else -> EnlikoGreen.copy(alpha = 0.1f)
                    }
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = when {
                            leverage.toInt() >= 50 -> "⚠️ High Risk Warning"
                            leverage.toInt() >= 20 -> "⚡ Moderate Risk"
                            else -> "✅ Conservative"
                        },
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold,
                        color = getLeverageColor(leverage.toInt())
                    )
                    
                    Text(
                        text = when {
                            leverage.toInt() >= 50 -> "High leverage significantly increases risk of liquidation. A ${100 / leverage.toInt()}% price move against you will liquidate your position."
                            leverage.toInt() >= 20 -> "Moderate leverage increases both potential gains and losses. Monitor your positions closely."
                            else -> "Lower leverage provides more margin for price fluctuations and reduces liquidation risk."
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Save Button
            Button(
                onClick = {
                    isSaving = true
                    onLeverageChange(leverage.toInt())
                    // TODO: Save to server
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
                    Text("Save Leverage Settings", fontWeight = FontWeight.SemiBold)
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
private fun LeverageQuickButton(
    leverage: Int,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        onClick = onClick,
        color = if (isSelected) getLeverageColor(leverage) else EnlikoSurface,
        shape = RoundedCornerShape(10.dp),
        modifier = modifier
    ) {
        Box(
            modifier = Modifier.padding(vertical = 14.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "${leverage}x",
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.SemiBold,
                color = if (isSelected) Color.White else EnlikoTextSecondary
            )
        }
    }
}

@Composable
private fun getLeverageColor(leverage: Int): Color {
    return when {
        leverage >= 50 -> EnlikoRed
        leverage >= 20 -> EnlikoYellow
        else -> EnlikoGreen
    }
}

private fun getRiskLevel(leverage: Int): String {
    return when {
        leverage >= 75 -> "Extreme Risk"
        leverage >= 50 -> "Very High Risk"
        leverage >= 25 -> "High Risk"
        leverage >= 10 -> "Moderate Risk"
        leverage >= 5 -> "Low Risk"
        else -> "Very Low Risk"
    }
}
