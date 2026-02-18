package io.enliko.trading.ui.screens.settings

import androidx.compose.foundation.BorderStroke
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
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.LocalStrings

/**
 * ApiKeysScreen - Configure Bybit and HyperLiquid API keys
 * Uses ViewModel for real API integration with offline-first approach
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ApiKeysScreen(
    onBack: () -> Unit,
    viewModel: ApiKeysViewModel = hiltViewModel()
) {
    val strings = LocalStrings.current
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    
    // Show messages
    LaunchedEffect(uiState.successMessage) {
        uiState.successMessage?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.clearMessages()
        }
    }
    
    LaunchedEffect(uiState.errorMessage) {
        uiState.errorMessage?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.clearMessages()
        }
    }
    
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
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = EnlikoBackground
    ) { padding ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = EnlikoPrimary)
            }
        } else {
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
                    text = strings.selectExchange,
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
                        isSelected = uiState.selectedExchange == "bybit",
                        isConfigured = uiState.bybitDemoConfigured || uiState.bybitRealConfigured,
                        onClick = { viewModel.selectExchange("bybit") },
                        modifier = Modifier.weight(1f)
                    )
                    ExchangeChip(
                        name = "HyperLiquid",
                        icon = "🔷",
                        isSelected = uiState.selectedExchange == "hyperliquid",
                        isConfigured = uiState.hlTestnetConfigured || uiState.hlMainnetConfigured,
                        onClick = { viewModel.selectExchange("hyperliquid") },
                        modifier = Modifier.weight(1f)
                    )
                }
                
                // Account Type Selector
                Text(
                    text = strings.accountType,
                    style = MaterialTheme.typography.titleSmall,
                    color = EnlikoTextSecondary
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    if (uiState.selectedExchange == "bybit") {
                        AccountChip(
                            name = "Demo",
                            isSelected = uiState.selectedAccount == "demo",
                            isConfigured = uiState.bybitDemoConfigured,
                            onClick = { viewModel.selectAccount("demo") },
                            modifier = Modifier.weight(1f)
                        )
                        AccountChip(
                            name = "Real",
                            isSelected = uiState.selectedAccount == "real",
                            isConfigured = uiState.bybitRealConfigured,
                            onClick = { viewModel.selectAccount("real") },
                            modifier = Modifier.weight(1f)
                        )
                    } else {
                        AccountChip(
                            name = "Testnet",
                            isSelected = uiState.selectedAccount == "testnet",
                            isConfigured = uiState.hlTestnetConfigured,
                            onClick = { viewModel.selectAccount("testnet") },
                            modifier = Modifier.weight(1f)
                        )
                        AccountChip(
                            name = "Mainnet",
                            isSelected = uiState.selectedAccount == "mainnet",
                            isConfigured = uiState.hlMainnetConfigured,
                            onClick = { viewModel.selectAccount("mainnet") },
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
                            uiState.selectedExchange == "bybit" && uiState.selectedAccount == "demo" -> {
                                BybitApiFields(
                                    apiKey = uiState.bybitDemoApiKey,
                                    onApiKeyChange = viewModel::updateBybitDemoApiKey,
                                    apiSecret = uiState.bybitDemoApiSecret,
                                    onApiSecretChange = viewModel::updateBybitDemoApiSecret,
                                    label = "Bybit Demo"
                                )
                            }
                            uiState.selectedExchange == "bybit" && uiState.selectedAccount == "real" -> {
                                BybitApiFields(
                                    apiKey = uiState.bybitRealApiKey,
                                    onApiKeyChange = viewModel::updateBybitRealApiKey,
                                    apiSecret = uiState.bybitRealApiSecret,
                                    onApiSecretChange = viewModel::updateBybitRealApiSecret,
                                    label = "Bybit Real"
                                )
                            }
                            uiState.selectedExchange == "hyperliquid" && uiState.selectedAccount == "testnet" -> {
                                HyperLiquidApiFields(
                                    privateKey = uiState.hlTestnetPrivateKey,
                                    onPrivateKeyChange = viewModel::updateHlTestnetPrivateKey,
                                    walletAddress = uiState.hlTestnetWalletAddress,
                                    onWalletAddressChange = viewModel::updateHlTestnetWalletAddress,
                                    label = "HyperLiquid Testnet"
                                )
                            }
                            uiState.selectedExchange == "hyperliquid" && uiState.selectedAccount == "mainnet" -> {
                                HyperLiquidApiFields(
                                    privateKey = uiState.hlMainnetPrivateKey,
                                    onPrivateKeyChange = viewModel::updateHlMainnetPrivateKey,
                                    walletAddress = uiState.hlMainnetWalletAddress,
                                    onWalletAddressChange = viewModel::updateHlMainnetWalletAddress,
                                    label = "HyperLiquid Mainnet"
                                )
                            }
                        }
                    }
                }
                
                // Test Result
                uiState.testResult?.let { result ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = if (result.startsWith("✅")) {
                                LongGreen.copy(alpha = 0.1f)
                            } else {
                                ShortRed.copy(alpha = 0.1f)
                            }
                        ),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = result,
                                style = MaterialTheme.typography.bodyMedium,
                                color = if (result.startsWith("✅")) LongGreen else ShortRed
                            )
                        }
                    }
                }
                
                // HyperLiquid Wallet Info (auto-discovered)
                if (uiState.selectedExchange == "hyperliquid") {
                    val apiWallet = if (uiState.selectedAccount == "testnet") uiState.hlTestnetApiWallet else uiState.hlMainnetApiWallet
                    val mainWallet = if (uiState.selectedAccount == "testnet") uiState.hlTestnetMainWallet else uiState.hlMainnetMainWallet
                    val balance = if (uiState.selectedAccount == "testnet") uiState.hlTestnetBalance else uiState.hlMainnetBalance
                    
                    if (apiWallet != null || mainWallet != null) {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = EnlikoPrimary.copy(alpha = 0.1f)
                            ),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Text(
                                    text = strings.walletInfoAutoDiscovered,
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.SemiBold,
                                    color = EnlikoPrimary
                                )
                                
                                apiWallet?.let {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Icon(
                                            Icons.Default.Key,
                                            contentDescription = null,
                                            modifier = Modifier.size(16.dp),
                                            tint = EnlikoTextMuted
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            text = "API: ${it.take(6)}...${it.takeLast(4)}",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = EnlikoTextSecondary
                                        )
                                    }
                                }
                                
                                mainWallet?.let {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Icon(
                                            Icons.Default.AccountBalanceWallet,
                                            contentDescription = null,
                                            modifier = Modifier.size(16.dp),
                                            tint = LongGreen
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            text = "Main: ${it.take(6)}...${it.takeLast(4)}",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = LongGreen
                                        )
                                    }
                                }
                                
                                balance?.let {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Icon(
                                            Icons.Default.AttachMoney,
                                            contentDescription = null,
                                            modifier = Modifier.size(16.dp),
                                            tint = EnlikoYellow
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            text = "Balance: $${String.format("%.2f", it)} USDC",
                                            style = MaterialTheme.typography.bodySmall,
                                            fontWeight = FontWeight.SemiBold,
                                            color = EnlikoYellow
                                        )
                                    }
                                }
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
                            text = strings.securityWarning,
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                }
                
                // Save Button
                Button(
                    onClick = viewModel::saveCurrentKeys,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp),
                    enabled = !uiState.isSaving,
                    colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    if (uiState.isSaving) {
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
                    onClick = viewModel::testConnection,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp),
                    enabled = !uiState.isTesting,
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = EnlikoPrimary
                    )
                ) {
                    if (uiState.isTesting) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = EnlikoPrimary,
                            strokeWidth = 2.dp
                        )
                    } else {
                        Icon(
                            Icons.Default.Wifi,
                            contentDescription = null,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Test Connection")
                    }
                }
                
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
private fun ExchangeChip(
    name: String,
    icon: String,
    isSelected: Boolean,
    isConfigured: Boolean,
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
            if (isConfigured) {
                Spacer(modifier = Modifier.width(4.dp))
                Icon(
                    Icons.Default.CheckCircle,
                    contentDescription = "Configured",
                    modifier = Modifier.size(16.dp),
                    tint = if (isSelected) Color.White else LongGreen
                )
            }
        }
    }
}

@Composable
private fun AccountChip(
    name: String,
    isSelected: Boolean,
    isConfigured: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        onClick = onClick,
        color = if (isSelected) EnlikoPrimary.copy(alpha = 0.2f) else EnlikoSurface,
        shape = RoundedCornerShape(8.dp),
        modifier = modifier,
        border = if (isSelected) BorderStroke(2.dp, EnlikoPrimary) else null
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
                color = if (isSelected) EnlikoPrimary else EnlikoTextSecondary
            )
            if (isConfigured) {
                Spacer(modifier = Modifier.width(4.dp))
                Icon(
                    Icons.Default.Check,
                    contentDescription = "Configured",
                    modifier = Modifier.size(14.dp),
                    tint = LongGreen
                )
            }
        }
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
