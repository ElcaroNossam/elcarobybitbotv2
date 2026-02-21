package io.enliko.trading.ui.screens.strategies

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import io.enliko.trading.data.api.RetrofitClient
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.LocalStrings
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// ═══════════════════════════════════════════════════════════════════════════════
// BACKTEST MODELS
// ═══════════════════════════════════════════════════════════════════════════════

@Serializable
data class BacktestRunRequest(
    val symbol: String,
    val strategy: String,
    @SerialName("start_date") val startDate: String,
    @SerialName("end_date") val endDate: String,
    val timeframe: String = "1h",
    @SerialName("initial_capital") val initialCapital: Double = 10000.0,
    val leverage: Int = 10,
    @SerialName("stop_loss") val stopLoss: Double = 2.0,
    @SerialName("take_profit") val takeProfit: Double = 3.0,
    @SerialName("risk_per_trade") val riskPerTrade: Double = 1.0,
    @SerialName("data_source") val dataSource: String = "binance"
)

@Serializable
data class BacktestResultResponse(
    val success: Boolean = false,
    val message: String? = null,
    val result: BacktestResultData? = null,
    @SerialName("request_id") val requestId: String? = null,
    
    // Fields that might come directly in async response
    val status: String? = null,
    @SerialName("total_trades") val totalTrades: Int? = null,
    @SerialName("winning_trades") val winningTrades: Int? = null,
    @SerialName("losing_trades") val losingTrades: Int? = null,
    @SerialName("win_rate") val winRate: Double? = null,
    @SerialName("total_pnl") val totalPnl: Double? = null,
    @SerialName("pnl_percent") val pnlPercent: Double? = null,
    @SerialName("sharpe_ratio") val sharpeRatio: Double? = null,
    @SerialName("max_drawdown") val maxDrawdown: Double? = null,
    @SerialName("profit_factor") val profitFactor: Double? = null,
    @SerialName("avg_win") val avgWin: Double? = null,
    @SerialName("avg_loss") val avgLoss: Double? = null,
    @SerialName("expectancy") val expectancy: Double? = null,
    @SerialName("final_balance") val finalBalance: Double? = null,
    val trades: List<BacktestTradeData>? = null
)

@Serializable
data class BacktestResultData(
    @SerialName("total_trades") val totalTrades: Int = 0,
    @SerialName("winning_trades") val winningTrades: Int = 0,
    @SerialName("losing_trades") val losingTrades: Int = 0,
    @SerialName("win_rate") val winRate: Double = 0.0,
    @SerialName("total_pnl") val totalPnl: Double = 0.0,
    @SerialName("pnl_percent") val pnlPercent: Double = 0.0,
    @SerialName("sharpe_ratio") val sharpeRatio: Double = 0.0,
    @SerialName("max_drawdown") val maxDrawdown: Double = 0.0,
    @SerialName("profit_factor") val profitFactor: Double = 0.0,
    @SerialName("avg_win") val avgWin: Double = 0.0,
    @SerialName("avg_loss") val avgLoss: Double = 0.0,
    @SerialName("expectancy") val expectancy: Double = 0.0,
    @SerialName("final_balance") val finalBalance: Double = 0.0,
    val trades: List<BacktestTradeData> = emptyList()
)

@Serializable
data class BacktestTradeData(
    val id: Int? = null,
    val symbol: String? = null,
    val side: String = "",
    @SerialName("entry_time") val entryTime: String? = null,
    @SerialName("exit_time") val exitTime: String? = null,
    @SerialName("entry_price") val entryPrice: Double = 0.0,
    @SerialName("exit_price") val exitPrice: Double = 0.0,
    val pnl: Double = 0.0,
    @SerialName("pnl_percent") val pnlPercent: Double = 0.0,
    val size: Double? = null,
    val leverage: Int? = null
)

@Serializable
data class StrategiesResponse(
    val available: List<String> = emptyList(),
    val strategies: List<String> = emptyList()
)

@Serializable
data class SavedBacktest(
    val id: String,
    val name: String,
    val symbol: String,
    val strategy: String,
    @SerialName("total_pnl") val totalPnl: Double = 0.0,
    @SerialName("win_rate") val winRate: Double = 0.0,
    @SerialName("created_at") val createdAt: String? = null
)

// ═══════════════════════════════════════════════════════════════════════════════
// VIEW MODEL
// ═══════════════════════════════════════════════════════════════════════════════

class BacktestViewModel : ViewModel() {
    var isLoading by mutableStateOf(false)
    var isRunning by mutableStateOf(false)
    var errorMessage by mutableStateOf<String?>(null)
    
    // Parameters
    var selectedStrategy by mutableStateOf("rsibboi")
    var selectedSymbol by mutableStateOf("BTCUSDT")
    var selectedTimeframe by mutableStateOf("1h")
    var startDate by mutableStateOf("2024-01-01")
    var endDate by mutableStateOf("2024-12-31")
    var initialCapital by mutableStateOf("10000")
    var leverage by mutableStateOf("10")
    var stopLoss by mutableStateOf("2.0")
    var takeProfit by mutableStateOf("3.0")
    var riskPerTrade by mutableStateOf("1.0")
    var selectedDataSource by mutableStateOf("binance")
    
    // Results
    var result by mutableStateOf<BacktestResultData?>(null)
    
    // Available options
    var strategies by mutableStateOf(listOf(
        "rsibboi", "wyckoff", "elcaro", "scryptomera", "scalper",
        "mean_reversion", "trend_following", "breakout", "dca", "grid",
        "momentum", "volatility_breakout"
    ))
    
    val symbols = listOf(
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT",
        "BNBUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT",
        "MATICUSDT", "LTCUSDT", "ATOMUSDT", "NEARUSDT", "APTUSDT"
    )
    
    val timeframes = listOf("1m", "5m", "15m", "1h", "4h", "1d")
    val dataSources = listOf("binance", "bybit", "hyperliquid")
    
    // Saved backtests
    var savedBacktests by mutableStateOf<List<SavedBacktest>>(emptyList())
    var showSavedBacktests by mutableStateOf(false)
    var showSaveDialog by mutableStateOf(false)
    var saveBacktestName by mutableStateOf("")
    
    init {
        loadStrategies()
    }
    
    private fun loadStrategies() {
        viewModelScope.launch {
            try {
                val response = withContext(Dispatchers.IO) {
                    RetrofitClient.api.getBacktestStrategies()
                }
                if (response.isSuccessful) {
                    response.body()?.let { data ->
                        val available = data.available.takeIf { it.isNotEmpty() } ?: data.strategies
                        if (available.isNotEmpty()) {
                            strategies = available
                            if (selectedStrategy !in available) {
                                selectedStrategy = available.first()
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                // Keep defaults
            }
        }
    }
    
    fun runBacktest() {
        if (isRunning) return
        
        viewModelScope.launch {
            isRunning = true
            errorMessage = null
            result = null
            
            try {
                val request = BacktestRunRequest(
                    symbol = selectedSymbol,
                    strategy = selectedStrategy,
                    startDate = startDate,
                    endDate = endDate,
                    timeframe = selectedTimeframe,
                    initialCapital = initialCapital.toDoubleOrNull() ?: 10000.0,
                    leverage = leverage.toIntOrNull() ?: 10,
                    stopLoss = stopLoss.toDoubleOrNull() ?: 2.0,
                    takeProfit = takeProfit.toDoubleOrNull() ?: 3.0,
                    riskPerTrade = riskPerTrade.toDoubleOrNull() ?: 1.0,
                    dataSource = selectedDataSource
                )
                
                val response = withContext(Dispatchers.IO) {
                    RetrofitClient.api.runBacktest(request)
                }
                
                if (response.isSuccessful) {
                    response.body()?.let { data ->
                        if (data.success && data.result != null) {
                            result = data.result
                        } else if (data.totalTrades != null) {
                            // Direct results (async-style response)
                            result = BacktestResultData(
                                totalTrades = data.totalTrades,
                                winningTrades = data.winningTrades ?: 0,
                                losingTrades = data.losingTrades ?: 0,
                                winRate = data.winRate ?: 0.0,
                                totalPnl = data.totalPnl ?: 0.0,
                                pnlPercent = data.pnlPercent ?: 0.0,
                                sharpeRatio = data.sharpeRatio ?: 0.0,
                                maxDrawdown = data.maxDrawdown ?: 0.0,
                                profitFactor = data.profitFactor ?: 0.0,
                                avgWin = data.avgWin ?: 0.0,
                                avgLoss = data.avgLoss ?: 0.0,
                                expectancy = data.expectancy ?: 0.0,
                                finalBalance = data.finalBalance ?: 0.0,
                                trades = data.trades ?: emptyList()
                            )
                        } else {
                            errorMessage = data.message ?: "Unknown error"
                        }
                    }
                } else {
                    errorMessage = "Error: ${response.code()} - ${response.message()}"
                }
            } catch (e: Exception) {
                errorMessage = "Network error: ${e.localizedMessage}"
            } finally {
                isRunning = false
            }
        }
    }
    
    fun saveBacktest() {
        if (result == null || saveBacktestName.isBlank()) return
        
        viewModelScope.launch {
            try {
                val body = mapOf(
                    "name" to saveBacktestName,
                    "symbol" to selectedSymbol,
                    "strategy" to selectedStrategy,
                    "result" to mapOf(
                        "total_pnl" to result!!.totalPnl,
                        "win_rate" to result!!.winRate,
                        "total_trades" to result!!.totalTrades
                    )
                )
                
                withContext(Dispatchers.IO) {
                    RetrofitClient.api.saveBacktest(body)
                }
                
                showSaveDialog = false
                saveBacktestName = ""
            } catch (e: Exception) {
                errorMessage = "Failed to save: ${e.localizedMessage}"
            }
        }
    }
    
    fun loadSavedBacktests() {
        viewModelScope.launch {
            try {
                val response = withContext(Dispatchers.IO) {
                    RetrofitClient.api.getSavedBacktests()
                }
                if (response.isSuccessful) {
                    savedBacktests = response.body() ?: emptyList()
                    showSavedBacktests = true
                }
            } catch (e: Exception) {
                errorMessage = "Failed to load saved backtests"
            }
        }
    }
    
    fun deleteSavedBacktest(id: String) {
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    RetrofitClient.api.deleteBacktest(id)
                }
                savedBacktests = savedBacktests.filter { it.id != id }
            } catch (e: Exception) {
                errorMessage = "Failed to delete"
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN SCREEN
// ═══════════════════════════════════════════════════════════════════════════════

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BacktestScreen(
    onNavigateBack: () -> Unit = {},
    viewModel: BacktestViewModel = viewModel()
) {
    val strings = LocalStrings.current
    val scrollState = rememberScrollState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        text = strings.backtest,
                        fontWeight = FontWeight.Bold
                    ) 
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    // Saved Backtests Button
                    IconButton(onClick = { viewModel.loadSavedBacktests() }) {
                        Icon(Icons.Default.History, contentDescription = "History")
                    }
                    
                    // Save Current Button
                    if (viewModel.result != null) {
                        IconButton(onClick = { viewModel.showSaveDialog = true }) {
                            Icon(Icons.Default.Save, contentDescription = "Save")
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = DarkBackground
                )
            )
        },
        containerColor = DarkBackground
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(scrollState)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Parameters Card
            ParametersCard(viewModel = viewModel)
            
            // Run Button
            RunBacktestButton(
                isRunning = viewModel.isRunning,
                onClick = { viewModel.runBacktest() }
            )
            
            // Error Message
            viewModel.errorMessage?.let { error ->
                Text(
                    text = error,
                    color = EnlikoRed,
                    modifier = Modifier.padding(8.dp)
                )
            }
            
            // Results
            viewModel.result?.let { result ->
                ResultsCard(result = result)
                TradesCard(trades = result.trades)
            }
            
            Spacer(modifier = Modifier.height(80.dp))
        }
    }
    
    // Save Dialog
    if (viewModel.showSaveDialog) {
        SaveBacktestDialog(
            name = viewModel.saveBacktestName,
            onNameChange = { viewModel.saveBacktestName = it },
            onSave = { viewModel.saveBacktest() },
            onDismiss = { viewModel.showSaveDialog = false }
        )
    }
    
    // Saved Backtests Sheet
    if (viewModel.showSavedBacktests) {
        SavedBacktestsSheet(
            backtests = viewModel.savedBacktests,
            onDelete = { viewModel.deleteSavedBacktest(it) },
            onDismiss = { viewModel.showSavedBacktests = false }
        )
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ParametersCard(viewModel: BacktestViewModel) {
    val strings = LocalStrings.current
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = DarkSurfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Parameters",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
            
            // Strategy Dropdown
            DropdownSelector(
                label = "Strategy",
                options = viewModel.strategies,
                selected = viewModel.selectedStrategy,
                onSelect = { viewModel.selectedStrategy = it }
            )
            
            // Symbol Dropdown
            DropdownSelector(
                label = "Symbol",
                options = viewModel.symbols,
                selected = viewModel.selectedSymbol,
                onSelect = { viewModel.selectedSymbol = it }
            )
            
            // Timeframe & Data Source Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                DropdownSelector(
                    label = "Timeframe",
                    options = viewModel.timeframes,
                    selected = viewModel.selectedTimeframe,
                    onSelect = { viewModel.selectedTimeframe = it },
                    modifier = Modifier.weight(1f)
                )
                
                DropdownSelector(
                    label = "Data Source",
                    options = viewModel.dataSources,
                    selected = viewModel.selectedDataSource,
                    onSelect = { viewModel.selectedDataSource = it },
                    modifier = Modifier.weight(1f)
                )
            }
            
            // Date Range
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = viewModel.startDate,
                    onValueChange = { viewModel.startDate = it },
                    label = { Text("Start Date") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = EnlikoPrimary,
                        unfocusedBorderColor = GlassBorder
                    )
                )
                
                OutlinedTextField(
                    value = viewModel.endDate,
                    onValueChange = { viewModel.endDate = it },
                    label = { Text("End Date") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = EnlikoPrimary,
                        unfocusedBorderColor = GlassBorder
                    )
                )
            }
            
            // Capital & Leverage Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = viewModel.initialCapital,
                    onValueChange = { viewModel.initialCapital = it },
                    label = { Text("Capital") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    prefix = { Text("$") },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = EnlikoPrimary,
                        unfocusedBorderColor = GlassBorder
                    )
                )
                
                OutlinedTextField(
                    value = viewModel.leverage,
                    onValueChange = { viewModel.leverage = it },
                    label = { Text("Leverage") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    suffix = { Text("x") },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = EnlikoPrimary,
                        unfocusedBorderColor = GlassBorder
                    )
                )
            }
            
            // SL & TP Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = viewModel.stopLoss,
                    onValueChange = { viewModel.stopLoss = it },
                    label = { Text("Stop Loss") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    suffix = { Text("%") },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = EnlikoRed,
                        unfocusedBorderColor = GlassBorder
                    )
                )
                
                OutlinedTextField(
                    value = viewModel.takeProfit,
                    onValueChange = { viewModel.takeProfit = it },
                    label = { Text("Take Profit") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    suffix = { Text("%") },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = EnlikoGreen,
                        unfocusedBorderColor = GlassBorder
                    )
                )
            }
            
            // Risk Per Trade
            OutlinedTextField(
                value = viewModel.riskPerTrade,
                onValueChange = { viewModel.riskPerTrade = it },
                label = { Text("Risk Per Trade") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                suffix = { Text("%") },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = EnlikoPrimary,
                    unfocusedBorderColor = GlassBorder
                )
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DropdownSelector(
    label: String,
    options: List<String>,
    selected: String,
    onSelect: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }
    
    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = it },
        modifier = modifier
    ) {
        OutlinedTextField(
            value = selected,
            onValueChange = {},
            readOnly = true,
            label = { Text(label) },
            trailingIcon = {
                ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded)
            },
            modifier = Modifier
                .menuAnchor()
                .fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = EnlikoPrimary,
                unfocusedBorderColor = GlassBorder
            )
        )
        
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            options.forEach { option ->
                DropdownMenuItem(
                    text = { Text(option) },
                    onClick = {
                        onSelect(option)
                        expanded = false
                    },
                    contentPadding = ExposedDropdownMenuDefaults.ItemContentPadding
                )
            }
        }
    }
}

@Composable
private fun RunBacktestButton(
    isRunning: Boolean,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp),
        enabled = !isRunning,
        shape = RoundedCornerShape(16.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = EnlikoPrimary,
            disabledContainerColor = EnlikoPrimary.copy(alpha = 0.5f)
        )
    ) {
        if (isRunning) {
            CircularProgressIndicator(
                color = Color.White,
                strokeWidth = 2.dp,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text("Running...", fontWeight = FontWeight.Bold)
        } else {
            Icon(Icons.Default.PlayArrow, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Run Backtest", fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun ResultsCard(result: BacktestResultData) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = DarkSurfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Results",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
            
            // Main Stats Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                ResultStatItem(
                    label = "Total PnL",
                    value = "${if (result.totalPnl >= 0) "+" else ""}$${String.format("%.2f", result.totalPnl)}",
                    valueColor = if (result.totalPnl >= 0) EnlikoGreen else EnlikoRed,
                    isLarge = true
                )
                ResultStatItem(
                    label = "Win Rate",
                    value = "${String.format("%.1f", result.winRate)}%",
                    valueColor = if (result.winRate >= 50) EnlikoGreen else EnlikoRed,
                    isLarge = true
                )
            }
            
            Divider(color = GlassBorder)
            
            // Stats Grid
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    ResultStatItem(label = "Total Trades", value = "${result.totalTrades}")
                    ResultStatItem(label = "Wins", value = "${result.winningTrades}", valueColor = EnlikoGreen)
                    ResultStatItem(label = "Losses", value = "${result.losingTrades}", valueColor = EnlikoRed)
                }
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    ResultStatItem(label = "Sharpe", value = String.format("%.2f", result.sharpeRatio))
                    ResultStatItem(label = "Max DD", value = "${String.format("%.1f", result.maxDrawdown)}%", valueColor = EnlikoRed)
                    ResultStatItem(label = "Profit Factor", value = String.format("%.2f", result.profitFactor))
                }
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    ResultStatItem(
                        label = "Avg Win",
                        value = "$${String.format("%.2f", result.avgWin)}",
                        valueColor = EnlikoGreen
                    )
                    ResultStatItem(
                        label = "Avg Loss",
                        value = "$${String.format("%.2f", kotlin.math.abs(result.avgLoss))}",
                        valueColor = EnlikoRed
                    )
                    ResultStatItem(
                        label = "Expectancy",
                        value = "$${String.format("%.2f", result.expectancy)}"
                    )
                }
                
                if (result.finalBalance > 0) {
                    Divider(color = GlassBorder)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center
                    ) {
                        ResultStatItem(
                            label = "Final Balance",
                            value = "$${String.format("%.2f", result.finalBalance)}",
                            valueColor = if (result.finalBalance > 10000) EnlikoGreen else EnlikoRed,
                            isLarge = true
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ResultStatItem(
    label: String,
    value: String,
    valueColor: Color = EnlikoTextPrimary,
    isLarge: Boolean = false
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = if (isLarge) MaterialTheme.typography.titleLarge else MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold,
            color = valueColor
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = EnlikoTextMuted
        )
    }
}

@Composable
private fun TradesCard(trades: List<BacktestTradeData>) {
    if (trades.isEmpty()) return
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = DarkSurfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Recent Trades",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
            
            trades.take(10).forEach { trade ->
                TradeRow(trade = trade)
            }
            
            if (trades.size > 10) {
                Text(
                    text = "... and ${trades.size - 10} more",
                    style = MaterialTheme.typography.labelSmall,
                    color = EnlikoTextMuted
                )
            }
        }
    }
}

@Composable
private fun TradeRow(trade: BacktestTradeData) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = if (trade.pnl >= 0) EnlikoGreen.copy(alpha = 0.1f) else EnlikoRed.copy(alpha = 0.1f),
                shape = RoundedCornerShape(8.dp)
            )
            .padding(horizontal = 12.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Side Badge
        Text(
            text = trade.side.uppercase(),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color = if (trade.side.lowercase() == "long") EnlikoGreen else EnlikoRed
        )
        
        // Entry -> Exit
        Text(
            text = "${String.format("%.2f", trade.entryPrice)} → ${String.format("%.2f", trade.exitPrice)}",
            style = MaterialTheme.typography.labelSmall,
            color = EnlikoTextSecondary
        )
        
        // PnL
        Text(
            text = "${if (trade.pnl >= 0) "+" else ""}$${String.format("%.2f", trade.pnl)}",
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color = if (trade.pnl >= 0) EnlikoGreen else EnlikoRed
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SaveBacktestDialog(
    name: String,
    onNameChange: (String) -> Unit,
    onSave: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Save Backtest") },
        text = {
            OutlinedTextField(
                value = name,
                onValueChange = onNameChange,
                label = { Text("Name") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
        },
        confirmButton = {
            TextButton(
                onClick = onSave,
                enabled = name.isNotBlank()
            ) {
                Text("Save", color = EnlikoPrimary)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SavedBacktestsSheet(
    backtests: List<SavedBacktest>,
    onDelete: (String) -> Unit,
    onDismiss: () -> Unit
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = DarkSurface
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Saved Backtests",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            if (backtests.isEmpty()) {
                Text(
                    text = "No saved backtests yet",
                    color = EnlikoTextMuted
                )
            } else {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    contentPadding = PaddingValues(bottom = 32.dp)
                ) {
                    items(backtests) { backtest ->
                        SavedBacktestCard(
                            backtest = backtest,
                            onDelete = { onDelete(backtest.id) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SavedBacktestCard(
    backtest: SavedBacktest,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = DarkSurfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = backtest.name,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${backtest.symbol} • ${backtest.strategy}",
                    style = MaterialTheme.typography.labelSmall,
                    color = EnlikoTextMuted
                )
            }
            
            Text(
                text = "${if (backtest.totalPnl >= 0) "+" else ""}$${String.format("%.0f", backtest.totalPnl)}",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = if (backtest.totalPnl >= 0) EnlikoGreen else EnlikoRed
            )
            
            IconButton(onClick = onDelete) {
                Icon(
                    Icons.Default.Delete,
                    contentDescription = "Delete",
                    tint = EnlikoRed
                )
            }
        }
    }
}
