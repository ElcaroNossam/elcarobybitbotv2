package io.enliko.trading.ui.screens.spot

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.data.api.SpotAsset
import io.enliko.trading.data.api.SpotBalance
import io.enliko.trading.util.Localization
import java.text.DecimalFormat

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpotScreen(
    viewModel: SpotViewModel = hiltViewModel(),
    onBack: () -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsState()
    var showBuyDialog by remember { mutableStateOf(false) }
    var showSellDialog by remember { mutableStateOf(false) }
    var selectedSymbol by remember { mutableStateOf("") }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(Localization.get("spot_title")) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.refresh() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                    IconButton(onClick = { /* Settings */ }) {
                        Icon(Icons.Default.Settings, contentDescription = "DCA Settings")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { 
                    selectedSymbol = "BTC"
                    showBuyDialog = true 
                }
            ) {
                Icon(Icons.Default.Add, contentDescription = "Buy")
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Balance Card
            uiState.balance?.let { balance ->
                SpotBalanceCard(balance = balance)
            }
            
            // DCA Status
            if (uiState.dcaEnabled) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.Loop,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Text(
                                text = Localization.get("spot_dca_enabled"),
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        }
                        Switch(
                            checked = uiState.dcaEnabled,
                            onCheckedChange = { viewModel.toggleDca(it) }
                        )
                    }
                }
            }
            
            // Assets List
            when {
                uiState.isLoading && uiState.assets.isEmpty() -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                uiState.assets.isEmpty() -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.Wallet,
                                contentDescription = null,
                                modifier = Modifier.size(48.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Text(
                                text = "No spot assets",
                                style = MaterialTheme.typography.titleMedium
                            )
                            Text(
                                text = "Start buying crypto to see your portfolio",
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
                        items(uiState.assets) { asset ->
                            SpotAssetCard(
                                asset = asset,
                                onBuy = {
                                    selectedSymbol = asset.symbol
                                    showBuyDialog = true
                                },
                                onSell = {
                                    selectedSymbol = asset.symbol
                                    showSellDialog = true
                                }
                            )
                        }
                    }
                }
            }
        }
        
        // Buy Dialog
        if (showBuyDialog) {
            SpotOrderDialog(
                symbol = selectedSymbol,
                isBuy = true,
                onDismiss = { showBuyDialog = false },
                onConfirm = { symbol, amount, usdt ->
                    viewModel.buySpot(symbol, amount, usdt)
                    showBuyDialog = false
                }
            )
        }
        
        // Sell Dialog
        if (showSellDialog) {
            SpotOrderDialog(
                symbol = selectedSymbol,
                isBuy = false,
                onDismiss = { showSellDialog = false },
                onConfirm = { symbol, amount, _ ->
                    viewModel.sellSpot(symbol, amount)
                    showSellDialog = false
                }
            )
        }
    }
}

@Composable
private fun SpotBalanceCard(balance: SpotBalance) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Spot Portfolio",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
            )
            Text(
                text = "$${formatCurrency(balance.totalValueUsdt)}",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = "Available",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                    )
                    Text(
                        text = "$${formatCurrency(balance.availableUsdt)}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "In Orders",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                    )
                    Text(
                        text = "$${formatCurrency(balance.totalValueUsdt - balance.availableUsdt)}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
        }
    }
}

@Composable
private fun SpotAssetCard(
    asset: SpotAsset,
    onBuy: () -> Unit,
    onSell: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Coin Icon
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = asset.symbol.take(2),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            
            // Info
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = asset.symbol,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "${formatAmount(asset.available)} ${asset.symbol}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            // Value
            Column(
                horizontalAlignment = Alignment.End,
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "$${formatCurrency(asset.valueUsdt)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
                val pnlColor = if (asset.pnlPercent >= 0) Color(0xFF4CAF50) else Color(0xFFF44336)
                Text(
                    text = "${if (asset.pnlPercent >= 0) "+" else ""}${formatPercent(asset.pnlPercent)}%",
                    style = MaterialTheme.typography.bodySmall,
                    color = pnlColor
                )
            }
            
            // Actions
            Column(
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                IconButton(
                    onClick = onBuy,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = "Buy",
                        tint = Color(0xFF4CAF50)
                    )
                }
                IconButton(
                    onClick = onSell,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Remove,
                        contentDescription = "Sell",
                        tint = Color(0xFFF44336)
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SpotOrderDialog(
    symbol: String,
    isBuy: Boolean,
    onDismiss: () -> Unit,
    onConfirm: (String, Double, Double) -> Unit
) {
    var amount by remember { mutableStateOf("") }
    var usdtAmount by remember { mutableStateOf("") }
    var useUsdt by remember { mutableStateOf(true) }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = if (isBuy) "Buy $symbol" else "Sell $symbol",
                style = MaterialTheme.typography.titleLarge
            )
        },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                if (isBuy) {
                    // Toggle for USDT or Amount
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        FilterChip(
                            selected = useUsdt,
                            onClick = { useUsdt = true },
                            label = { Text("By USDT") }
                        )
                        FilterChip(
                            selected = !useUsdt,
                            onClick = { useUsdt = false },
                            label = { Text("By Amount") }
                        )
                    }
                }
                
                if (useUsdt && isBuy) {
                    OutlinedTextField(
                        value = usdtAmount,
                        onValueChange = { usdtAmount = it },
                        label = { Text("USDT Amount") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                } else {
                    OutlinedTextField(
                        value = amount,
                        onValueChange = { amount = it },
                        label = { Text("$symbol Amount") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    val qty = amount.toDoubleOrNull() ?: 0.0
                    val usdt = usdtAmount.toDoubleOrNull() ?: 0.0
                    onConfirm(symbol, qty, usdt)
                },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isBuy) Color(0xFF4CAF50) else Color(0xFFF44336)
                )
            ) {
                Text(if (isBuy) "Buy" else "Sell")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

// Helpers
private fun formatCurrency(value: Double): String {
    return DecimalFormat("#,##0.00").format(value)
}

private fun formatAmount(value: Double): String {
    return if (value >= 1) DecimalFormat("#,##0.####").format(value)
    else DecimalFormat("0.########").format(value)
}

private fun formatPercent(value: Double): String {
    return DecimalFormat("0.00").format(value)
}
