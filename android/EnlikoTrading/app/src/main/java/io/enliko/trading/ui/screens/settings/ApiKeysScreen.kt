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
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*

/**
 * ApiKeysScreen - Matching iOS SubSettingsViews.swift API Keys section
 * Configure Bybit and HyperLiquid API keys
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ApiKeysScreen(
    onBack: () -> Unit
) {
    var selectedExchange by remember { mutableStateOf("bybit") }
    var selectedAccount by remember { mutableStateOf("demo") }
    
    // Bybit Demo
    var bybitDemoApiKey by remember { mutableStateOf("") }
    var bybitDemoApiSecret by remember { mutableStateOf("") }
    
    // Bybit Real
    var bybitRealApiKey by remember { mutableStateOf("") }
    var bybitRealApiSecret by remember { mutableStateOf("") }
    
    // HyperLiquid Testnet
    var hlTestnetPrivateKey by remember { mutableStateOf("") }
    var hlTestnetWalletAddress by remember { mutableStateOf("") }
    
    // HyperLiquid Mainnet
    var hlMainnetPrivateKey by remember { mutableStateOf("") }
    var hlMainnetWalletAddress by remember { mutableStateOf("") }
    
    var isSaving by remember { mutableStateOf(false) }
    var showSuccess by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("API Keys") },
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
            // Exchange Selector
            Text(
                text = "Select Exchange",
                style = MaterialTheme.typography.titleSmall,
                color = EnlikoTextSecondary
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ExchangeChip(
                    name = "Bybit",
                    icon = "🟠",
                    isSelected = selectedExchange == "bybit",
                    onClick = { selectedExchange = "bybit"; selectedAccount = "demo" },
                    modifier = Modifier.weight(1f)
                )
                ExchangeChip(
                    name = "HyperLiquid",
                    icon = "🔷",
                    isSelected = selectedExchange == "hyperliquid",
                    onClick = { selectedExchange = "hyperliquid"; selectedAccount = "testnet" },
                    modifier = Modifier.weight(1f)
                )
            }
            
            // Account Type Selector
            Text(
                text = "Account Type",
                style = MaterialTheme.typography.titleSmall,
                color = EnlikoTextSecondary
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (selectedExchange == "bybit") {
                    AccountChip(
                        name = "Demo",
                        isSelected = selectedAccount == "demo",
                        onClick = { selectedAccount = "demo" },
                        modifier = Modifier.weight(1f)
                    )
                    AccountChip(
                        name = "Real",
                        isSelected = selectedAccount == "real",
                        onClick = { selectedAccount = "real" },
                        modifier = Modifier.weight(1f)
                    )
                } else {
                    AccountChip(
                        name = "Testnet",
                        isSelected = selectedAccount == "testnet",
                        onClick = { selectedAccount = "testnet" },
                        modifier = Modifier.weight(1f)
                    )
                    AccountChip(
                        name = "Mainnet",
                        isSelected = selectedAccount == "mainnet",
                        onClick = { selectedAccount = "mainnet" },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            // API Keys Form
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = EnlikoCard),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    when {
                        selectedExchange == "bybit" && selectedAccount == "demo" -> {
                            BybitApiFields(
                                apiKey = bybitDemoApiKey,
                                onApiKeyChange = { bybitDemoApiKey = it },
                                apiSecret = bybitDemoApiSecret,
                                onApiSecretChange = { bybitDemoApiSecret = it },
                                label = "Bybit Demo"
                            )
                        }
                        selectedExchange == "bybit" && selectedAccount == "real" -> {
                            BybitApiFields(
                                apiKey = bybitRealApiKey,
                                onApiKeyChange = { bybitRealApiKey = it },
                                apiSecret = bybitRealApiSecret,
                                onApiSecretChange = { bybitRealApiSecret = it },
                                label = "Bybit Real"
                            )
                        }
                        selectedExchange == "hyperliquid" && selectedAccount == "testnet" -> {
                            HyperLiquidApiFields(
                                privateKey = hlTestnetPrivateKey,
                                onPrivateKeyChange = { hlTestnetPrivateKey = it },
                                walletAddress = hlTestnetWalletAddress,
                                onWalletAddressChange = { hlTestnetWalletAddress = it },
                                label = "HyperLiquid Testnet"
                            )
                        }
                        selectedExchange == "hyperliquid" && selectedAccount == "mainnet" -> {
                            HyperLiquidApiFields(
                                privateKey = hlMainnetPrivateKey,
                                onPrivateKeyChange = { hlMainnetPrivateKey = it },
                                walletAddress = hlMainnetWalletAddress,
                                onWalletAddressChange = { hlMainnetWalletAddress = it },
                                label = "HyperLiquid Mainnet"
                            )
                        }
                    }
                }
            }
            
            // Warning Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = EnlikoYellow.copy(alpha = 0.1f)
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = null,
                        tint = EnlikoYellow
                    )
                    Text(
                        text = "Never share your API keys or private keys with anyone. Enable only required permissions.",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                }
            }
            
            // Save Button
            Button(
                onClick = {
                    isSaving = true
                    // TODO: Save API keys to server
                    showSuccess = true
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
                    Text("Save API Keys", fontWeight = FontWeight.SemiBold)
                }
            }
            
            // Test Connection Button
            OutlinedButton(
                onClick = { /* TODO: Test connection */ },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = EnlikoPrimary
                )
            ) {
                Icon(
                    Icons.Default.Wifi,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Test Connection")
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
    
    // Success Snackbar
    if (showSuccess) {
        LaunchedEffect(Unit) {
            kotlinx.coroutines.delay(2000)
            showSuccess = false
        }
    }
}

@Composable
private fun ExchangeChip(
    name: String,
    icon: String,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        onClick = onClick,
        color = if (isSelected) EnlikoPrimary else EnlikoCard,
        shape = RoundedCornerShape(12.dp),
        modifier = modifier
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = icon,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = name,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium,
                color = if (isSelected) Color.White else EnlikoTextPrimary
            )
        }
    }
}

@Composable
private fun AccountChip(
    name: String,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        onClick = onClick,
        color = if (isSelected) EnlikoPrimary.copy(alpha = 0.2f) else EnlikoSurface,
        shape = RoundedCornerShape(8.dp),
        modifier = modifier,
        border = if (isSelected) {
            androidx.compose.foundation.BorderStroke(2.dp, EnlikoPrimary)
        } else null
    ) {
        Text(
            text = name,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
            color = if (isSelected) EnlikoPrimary else EnlikoTextSecondary,
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)
        )
    }
}

@Composable
private fun BybitApiFields(
    apiKey: String,
    onApiKeyChange: (String) -> Unit,
    apiSecret: String,
    onApiSecretChange: (String) -> Unit,
    label: String
) {
    var showSecret by remember { mutableStateOf(false) }
    
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = EnlikoTextPrimary
        )
        
        OutlinedTextField(
            value = apiKey,
            onValueChange = onApiKeyChange,
            label = { Text("API Key") },
            placeholder = { Text("Enter your Bybit API key") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = EnlikoPrimary,
                unfocusedBorderColor = EnlikoBorder,
                focusedLabelColor = EnlikoPrimary,
                focusedTextColor = EnlikoTextPrimary,
                unfocusedTextColor = EnlikoTextPrimary,
                cursorColor = EnlikoPrimary
            )
        )
        
        OutlinedTextField(
            value = apiSecret,
            onValueChange = onApiSecretChange,
            label = { Text("API Secret") },
            placeholder = { Text("Enter your Bybit API secret") },
            singleLine = true,
            visualTransformation = if (showSecret) VisualTransformation.None else PasswordVisualTransformation(),
            trailingIcon = {
                IconButton(onClick = { showSecret = !showSecret }) {
                    Icon(
                        if (showSecret) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                        contentDescription = "Toggle visibility"
                    )
                }
            },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = EnlikoPrimary,
                unfocusedBorderColor = EnlikoBorder,
                focusedLabelColor = EnlikoPrimary,
                focusedTextColor = EnlikoTextPrimary,
                unfocusedTextColor = EnlikoTextPrimary,
                cursorColor = EnlikoPrimary
            )
        )
    }
}

@Composable
private fun HyperLiquidApiFields(
    privateKey: String,
    onPrivateKeyChange: (String) -> Unit,
    walletAddress: String,
    onWalletAddressChange: (String) -> Unit,
    label: String
) {
    var showKey by remember { mutableStateOf(false) }
    
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = EnlikoTextPrimary
        )
        
        OutlinedTextField(
            value = walletAddress,
            onValueChange = onWalletAddressChange,
            label = { Text("Wallet Address") },
            placeholder = { Text("0x...") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = EnlikoPrimary,
                unfocusedBorderColor = EnlikoBorder,
                focusedLabelColor = EnlikoPrimary,
                focusedTextColor = EnlikoTextPrimary,
                unfocusedTextColor = EnlikoTextPrimary,
                cursorColor = EnlikoPrimary
            )
        )
        
        OutlinedTextField(
            value = privateKey,
            onValueChange = onPrivateKeyChange,
            label = { Text("Private Key") },
            placeholder = { Text("Enter your private key") },
            singleLine = true,
            visualTransformation = if (showKey) VisualTransformation.None else PasswordVisualTransformation(),
            trailingIcon = {
                IconButton(onClick = { showKey = !showKey }) {
                    Icon(
                        if (showKey) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                        contentDescription = "Toggle visibility"
                    )
                }
            },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = EnlikoPrimary,
                unfocusedBorderColor = EnlikoBorder,
                focusedLabelColor = EnlikoPrimary,
                focusedTextColor = EnlikoTextPrimary,
                unfocusedTextColor = EnlikoTextPrimary,
                cursorColor = EnlikoPrimary
            )
        )
    }
}
