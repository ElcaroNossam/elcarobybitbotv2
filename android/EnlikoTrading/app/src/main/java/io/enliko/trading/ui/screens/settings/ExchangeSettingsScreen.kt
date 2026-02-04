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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*

/**
 * ExchangeSettingsScreen - Matching iOS SubSettingsViews.swift ExchangeSettingsView
 * Configure exchange preferences and account types
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExchangeSettingsScreen(
    currentExchange: String = "bybit",
    currentAccountType: String = "demo",
    onExchangeChange: (String) -> Unit = {},
    onAccountTypeChange: (String) -> Unit = {},
    onBack: () -> Unit
) {
    var selectedExchange by remember { mutableStateOf(currentExchange) }
    var selectedAccountType by remember { mutableStateOf(currentAccountType) }
    var tradingMode by remember { mutableStateOf("demo") } // demo, real, both
    var isSaving by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Exchange Settings") },
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
            // Exchange Selection
            Text(
                text = "Select Exchange",
                style = MaterialTheme.typography.titleSmall,
                color = EnlikoTextSecondary
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                ExchangeCard(
                    name = "Bybit",
                    icon = "🟠",
                    description = "CEX with demo & real accounts",
                    isSelected = selectedExchange == "bybit",
                    onClick = { 
                        selectedExchange = "bybit"
                        selectedAccountType = "demo"
                        onExchangeChange("bybit")
                    },
                    modifier = Modifier.weight(1f)
                )
                
                ExchangeCard(
                    name = "HyperLiquid",
                    icon = "🔷",
                    description = "DEX perpetual trading",
                    isSelected = selectedExchange == "hyperliquid",
                    onClick = { 
                        selectedExchange = "hyperliquid"
                        selectedAccountType = "testnet"
                        onExchangeChange("hyperliquid")
                    },
                    modifier = Modifier.weight(1f)
                )
            }
            
            // Account Type Selection
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
                        text = "Account Type",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = EnlikoTextPrimary
                    )
                    
                    if (selectedExchange == "bybit") {
                        AccountTypeOption(
                            title = "Demo Account",
                            description = "Paper trading with virtual funds",
                            icon = Icons.Default.Science,
                            isSelected = selectedAccountType == "demo",
                            onClick = { 
                                selectedAccountType = "demo"
                                onAccountTypeChange("demo")
                            }
                        )
                        
                        AccountTypeOption(
                            title = "Real Account",
                            description = "Live trading with real funds",
                            icon = Icons.Default.AccountBalanceWallet,
                            isSelected = selectedAccountType == "real",
                            onClick = { 
                                selectedAccountType = "real"
                                onAccountTypeChange("real")
                            },
                            warning = "⚠️ Real money at risk"
                        )
                    } else {
                        AccountTypeOption(
                            title = "Testnet",
                            description = "Test trading on testnet",
                            icon = Icons.Default.BugReport,
                            isSelected = selectedAccountType == "testnet",
                            onClick = { 
                                selectedAccountType = "testnet"
                                onAccountTypeChange("testnet")
                            }
                        )
                        
                        AccountTypeOption(
                            title = "Mainnet",
                            description = "Production trading",
                            icon = Icons.Default.Verified,
                            isSelected = selectedAccountType == "mainnet",
                            onClick = { 
                                selectedAccountType = "mainnet"
                                onAccountTypeChange("mainnet")
                            },
                            warning = "⚠️ Real money at risk"
                        )
                    }
                }
            }
            
            // Trading Mode (Bybit only)
            if (selectedExchange == "bybit") {
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
                            text = "Trading Mode",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold,
                            color = EnlikoTextPrimary
                        )
                        
                        TradingModeOption(
                            title = "Demo Only",
                            description = "Trade only on demo account",
                            isSelected = tradingMode == "demo",
                            onClick = { tradingMode = "demo" }
                        )
                        
                        TradingModeOption(
                            title = "Real Only",
                            description = "Trade only on real account",
                            isSelected = tradingMode == "real",
                            onClick = { tradingMode = "real" }
                        )
                        
                        TradingModeOption(
                            title = "Both Accounts",
                            description = "Mirror trades on demo & real",
                            isSelected = tradingMode == "both",
                            onClick = { tradingMode = "both" },
                            badge = "PRO"
                        )
                    }
                }
            }
            
            // Exchange Info Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = EnlikoPrimary.copy(alpha = 0.1f)
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = if (selectedExchange == "bybit") "Bybit Features" else "HyperLiquid Features",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold,
                        color = EnlikoPrimary
                    )
                    
                    if (selectedExchange == "bybit") {
                        FeatureRow(icon = Icons.Default.Check, text = "Demo & Real accounts")
                        FeatureRow(icon = Icons.Default.Check, text = "Up to 100x leverage")
                        FeatureRow(icon = Icons.Default.Check, text = "Spot & Futures trading")
                        FeatureRow(icon = Icons.Default.Check, text = "Low trading fees")
                    } else {
                        FeatureRow(icon = Icons.Default.Check, text = "Decentralized trading")
                        FeatureRow(icon = Icons.Default.Check, text = "Non-custodial")
                        FeatureRow(icon = Icons.Default.Check, text = "Up to 50x leverage")
                        FeatureRow(icon = Icons.Default.Check, text = "No KYC required")
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Save Button
            Button(
                onClick = {
                    isSaving = true
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
                    Text("Save Exchange Settings", fontWeight = FontWeight.SemiBold)
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
private fun ExchangeCard(
    name: String,
    icon: String,
    description: String,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onClick,
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) EnlikoPrimary.copy(alpha = 0.15f) else EnlikoCard
        ),
        shape = RoundedCornerShape(12.dp),
        border = if (isSelected) {
            androidx.compose.foundation.BorderStroke(2.dp, EnlikoPrimary)
        } else null
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = icon,
                style = MaterialTheme.typography.headlineMedium
            )
            Text(
                text = name,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = if (isSelected) EnlikoPrimary else EnlikoTextPrimary
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = EnlikoTextSecondary,
                modifier = Modifier.padding(horizontal = 4.dp)
            )
            
            if (isSelected) {
                Icon(
                    Icons.Default.CheckCircle,
                    contentDescription = "Selected",
                    tint = EnlikoPrimary,
                    modifier = Modifier.size(24.dp)
                )
            }
        }
    }
}

@Composable
private fun AccountTypeOption(
    title: String,
    description: String,
    icon: ImageVector,
    isSelected: Boolean,
    onClick: () -> Unit,
    warning: String? = null
) {
    Surface(
        onClick = onClick,
        color = if (isSelected) EnlikoPrimary.copy(alpha = 0.1f) else Color.Transparent,
        shape = RoundedCornerShape(10.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    icon,
                    contentDescription = null,
                    tint = if (isSelected) EnlikoPrimary else EnlikoTextSecondary
                )
                Column {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium,
                        color = if (isSelected) EnlikoPrimary else EnlikoTextPrimary
                    )
                    Text(
                        text = description,
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                    if (warning != null) {
                        Text(
                            text = warning,
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoYellow
                        )
                    }
                }
            }
            
            RadioButton(
                selected = isSelected,
                onClick = onClick,
                colors = RadioButtonDefaults.colors(
                    selectedColor = EnlikoPrimary
                )
            )
        }
    }
}

@Composable
private fun TradingModeOption(
    title: String,
    description: String,
    isSelected: Boolean,
    onClick: () -> Unit,
    badge: String? = null
) {
    Surface(
        onClick = onClick,
        color = if (isSelected) EnlikoPrimary.copy(alpha = 0.1f) else Color.Transparent,
        shape = RoundedCornerShape(10.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium,
                        color = if (isSelected) EnlikoPrimary else EnlikoTextPrimary
                    )
                    if (badge != null) {
                        Surface(
                            color = EnlikoGold,
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                text = badge,
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = Color.Black,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                }
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = EnlikoTextSecondary
                )
            }
            
            RadioButton(
                selected = isSelected,
                onClick = onClick,
                colors = RadioButtonDefaults.colors(
                    selectedColor = EnlikoPrimary
                )
            )
        }
    }
}

@Composable
private fun FeatureRow(
    icon: ImageVector,
    text: String
) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            icon,
            contentDescription = null,
            tint = EnlikoGreen,
            modifier = Modifier.size(16.dp)
        )
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall,
            color = EnlikoTextSecondary
        )
    }
}
