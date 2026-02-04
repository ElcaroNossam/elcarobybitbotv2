package io.enliko.trading.ui.screens.strategies

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
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
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.Localization
import kotlinx.coroutines.delay

/**
 * BacktestScreen - Matching iOS BacktestView.swift
 * Features: Parameter configuration, run backtest, show results
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BacktestScreen(
    onBack: () -> Unit
) {
    var selectedStrategy by remember { mutableStateOf("oi") }
    var selectedSymbol by remember { mutableStateOf("BTCUSDT") }
    var selectedTimeframe by remember { mutableStateOf("15m") }
    var days by remember { mutableIntStateOf(30) }
    var initialBalance by remember { mutableStateOf("10000") }
    var riskPercent by remember { mutableStateOf("1.0") }
    var stopLossPercent by remember { mutableStateOf("3.0") }
    var takeProfitPercent by remember { mutableStateOf("8.0") }
    
    var isRunning by remember { mutableStateOf(false) }
    var result by remember { mutableStateOf<BacktestResult?>(null) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    val strategies = listOf("oi", "scryptomera", "scalper", "elcaro", "fibonacci", "rsi_bb")
    val timeframes = listOf("5m", "15m", "1h", "4h", "1d")
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(Localization.get("backtest")) },
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
            // Parameters Card
            ParametersCard(
                selectedStrategy = selectedStrategy,
                onStrategyChange = { selectedStrategy = it },
                strategies = strategies,
                selectedSymbol = selectedSymbol,
                onSymbolChange = { selectedSymbol = it },
                selectedTimeframe = selectedTimeframe,
                onTimeframeChange = { selectedTimeframe = it },
                timeframes = timeframes,
                days = days,
                onDaysChange = { days = it },
                initialBalance = initialBalance,
                onInitialBalanceChange = { initialBalance = it },
                riskPercent = riskPercent,
                onRiskPercentChange = { riskPercent = it },
                stopLossPercent = stopLossPercent,
                onStopLossPercentChange = { stopLossPercent = it },
                takeProfitPercent = takeProfitPercent,
                onTakeProfitPercentChange = { takeProfitPercent = it }
            )
            
            // Run Button
            Button(
                onClick = {
                    isRunning = true
                    result = null
                    errorMessage = null
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                enabled = !isRunning,
                colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary),
                shape = RoundedCornerShape(12.dp)
            ) {
                if (isRunning) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White,
                        strokeWidth = 2.dp
                    )
                } else {
                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(Localization.get("run_backtest"), fontWeight = FontWeight.SemiBold)
                }
            }
            
            // Simulate backtest
            LaunchedEffect(isRunning) {
                if (isRunning) {
                    delay(2000) // Simulate API call
                    result = BacktestResult(
                        id = System.currentTimeMillis().toString(),
                        strategy = selectedStrategy,
                        symbol = selectedSymbol,
                        timeframe = selectedTimeframe,
                        totalTrades = 156,
                        winRate = 62.5,
                        totalPnl = 2340.50,
                        maxDrawdown = 12.3,
                        profitFactor = 1.85,
                        sharpeRatio = 1.42
                    )
                    isRunning = false
                }
            }
            
            // Results
            result?.let { backtestResult ->
                ResultsCard(result = backtestResult)
            }
            
            // Error
            errorMessage?.let { error ->
                ErrorCard(error = error)
            }
        }
    }
}

@Composable
private fun ParametersCard(
    selectedStrategy: String,
    onStrategyChange: (String) -> Unit,
    strategies: List<String>,
    selectedSymbol: String,
    onSymbolChange: (String) -> Unit,
    selectedTimeframe: String,
    onTimeframeChange: (String) -> Unit,
    timeframes: List<String>,
    days: Int,
    onDaysChange: (Int) -> Unit,
    initialBalance: String,
    onInitialBalanceChange: (String) -> Unit,
    riskPercent: String,
    onRiskPercentChange: (String) -> Unit,
    stopLossPercent: String,
    onStopLossPercentChange: (String) -> Unit,
    takeProfitPercent: String,
    onTakeProfitPercentChange: (String) -> Unit
) {
    var strategyExpanded by remember { mutableStateOf(false) }
    
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
                text = Localization.get("backtest_parameters"),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
            
            // Strategy Picker
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(Localization.get("strategy"), color = EnlikoTextSecondary)
                
                ExposedDropdownMenuBox(
                    expanded = strategyExpanded,
                    onExpandedChange = { strategyExpanded = it }
                ) {
                    TextField(
                        value = selectedStrategy.uppercase(),
                        onValueChange = {},
                        readOnly = true,
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = strategyExpanded) },
                        modifier = Modifier
                            .menuAnchor()
                            .width(140.dp),
                        colors = TextFieldDefaults.colors(
                            unfocusedContainerColor = EnlikoSurface,
                            focusedContainerColor = EnlikoSurface
                        )
                    )
                    
                    ExposedDropdownMenu(
                        expanded = strategyExpanded,
                        onDismissRequest = { strategyExpanded = false }
                    ) {
                        strategies.forEach { strategy ->
                            DropdownMenuItem(
                                text = { Text(strategy.uppercase()) },
                                onClick = {
                                    onStrategyChange(strategy)
                                    strategyExpanded = false
                                }
                            )
                        }
                    }
                }
            }
            
            // Symbol
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(Localization.get("symbol"), color = EnlikoTextSecondary)
                
                OutlinedTextField(
                    value = selectedSymbol,
                    onValueChange = { onSymbolChange(it.uppercase()) },
                    modifier = Modifier.width(140.dp),
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        unfocusedContainerColor = EnlikoSurface,
                        focusedContainerColor = EnlikoSurface
                    )
                )
            }
            
            // Timeframe
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(Localization.get("timeframe"), color = EnlikoTextSecondary)
                
                SingleChoiceSegmentedButtonRow {
                    timeframes.forEachIndexed { index, tf ->
                        SegmentedButton(
                            selected = selectedTimeframe == tf,
                            onClick = { onTimeframeChange(tf) },
                            shape = SegmentedButtonDefaults.itemShape(index, timeframes.size)
                        ) {
                            Text(tf, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
            }
            
            HorizontalDivider(color = EnlikoBorder)
            
            // Days
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(Localization.get("history_days"), color = EnlikoTextSecondary)
                
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(onClick = { if (days > 7) onDaysChange(days - 7) }) {
                        Icon(Icons.Default.Remove, contentDescription = "Decrease")
                    }
                    Text("$days", color = EnlikoTextPrimary)
                    IconButton(onClick = { if (days < 365) onDaysChange(days + 7) }) {
                        Icon(Icons.Default.Add, contentDescription = "Increase")
                    }
                }
            }
            
            // Initial Balance
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(Localization.get("initial_balance"), color = EnlikoTextSecondary)
                
                OutlinedTextField(
                    value = initialBalance,
                    onValueChange = onInitialBalanceChange,
                    modifier = Modifier.width(120.dp),
                    singleLine = true,
                    leadingIcon = { Text("$", color = EnlikoTextSecondary) },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    colors = OutlinedTextFieldDefaults.colors(
                        unfocusedContainerColor = EnlikoSurface,
                        focusedContainerColor = EnlikoSurface
                    )
                )
            }
            
            HorizontalDivider(color = EnlikoBorder)
            
            // Risk Parameters Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                RiskParameterField(
                    label = Localization.get("risk_pct"),
                    value = riskPercent,
                    onValueChange = onRiskPercentChange,
                    modifier = Modifier.weight(1f)
                )
                
                RiskParameterField(
                    label = Localization.get("sl_pct"),
                    value = stopLossPercent,
                    onValueChange = onStopLossPercentChange,
                    modifier = Modifier.weight(1f)
                )
                
                RiskParameterField(
                    label = Localization.get("tp_pct"),
                    value = takeProfitPercent,
                    onValueChange = onTakeProfitPercentChange,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun RiskParameterField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = EnlikoTextSecondary
        )
        
        Spacer(modifier = Modifier.height(4.dp))
        
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            colors = OutlinedTextFieldDefaults.colors(
                unfocusedContainerColor = EnlikoSurface,
                focusedContainerColor = EnlikoSurface
            )
        )
    }
}

@Composable
private fun ResultsCard(result: BacktestResult) {
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
                    text = Localization.get("results"),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = EnlikoTextPrimary
                )
                
                Surface(
                    color = EnlikoPrimary,
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = result.strategy.uppercase(),
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = Color.White,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Stats Grid (2 columns)
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                modifier = Modifier.height(180.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                item {
                    ResultStat(
                        title = Localization.get("total_trades"),
                        value = result.totalTrades.toString()
                    )
                }
                item {
                    ResultStat(
                        title = Localization.get("win_rate"),
                        value = String.format("%.1f%%", result.winRate),
                        color = if (result.winRate >= 50) EnlikoGreen else EnlikoRed
                    )
                }
                item {
                    ResultStat(
                        title = Localization.get("total_pnl"),
                        value = String.format("$%.2f", result.totalPnl),
                        color = if (result.totalPnl >= 0) EnlikoGreen else EnlikoRed
                    )
                }
                item {
                    ResultStat(
                        title = Localization.get("max_drawdown"),
                        value = String.format("%.1f%%", result.maxDrawdown),
                        color = EnlikoRed
                    )
                }
                item {
                    ResultStat(
                        title = Localization.get("profit_factor"),
                        value = String.format("%.2f", result.profitFactor)
                    )
                }
                item {
                    ResultStat(
                        title = Localization.get("sharpe_ratio"),
                        value = String.format("%.2f", result.sharpeRatio)
                    )
                }
            }
        }
    }
}

@Composable
private fun ResultStat(
    title: String,
    value: String,
    color: Color = EnlikoTextPrimary
) {
    Surface(
        color = EnlikoSurface,
        shape = RoundedCornerShape(8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.labelSmall,
                color = EnlikoTextSecondary
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = color
            )
        }
    }
}

@Composable
private fun ErrorCard(error: String) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = EnlikoRed.copy(alpha = 0.1f),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = null,
                tint = EnlikoRed
            )
            Text(
                text = error,
                color = EnlikoRed,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

// Data class
data class BacktestResult(
    val id: String,
    val strategy: String,
    val symbol: String,
    val timeframe: String,
    val totalTrades: Int,
    val winRate: Double,
    val totalPnl: Double,
    val maxDrawdown: Double,
    val profitFactor: Double,
    val sharpeRatio: Double
)
