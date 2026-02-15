package io.enliko.trading.ui.screens.trading

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import kotlinx.coroutines.delay
import kotlin.random.Random

// MARK: - Data Models
enum class OrderType(val displayName: String) {
    MARKET("Market"),
    LIMIT("Limit"),
    STOP_MARKET("Stop Market"),
    STOP_LIMIT("Stop Limit"),
    TRAILING_STOP("Trailing Stop")
}

enum class TradeSide { LONG, SHORT }

enum class MarginMode { CROSS, ISOLATED }

enum class PositionMode { ONE_WAY, HEDGE }

data class OrderFormState(
    val symbol: String = "BTCUSDT",
    val side: TradeSide = TradeSide.LONG,
    val orderType: OrderType = OrderType.MARKET,
    val quantity: String = "",
    val price: String = "",
    val stopPrice: String = "",
    val leverage: Int = 10,
    val marginMode: MarginMode = MarginMode.CROSS,
    val reduceOnly: Boolean = false,
    val postOnly: Boolean = false,
    val tpEnabled: Boolean = true,
    val tpPercent: String = "25.0",
    val tpPrice: String = "",
    val slEnabled: Boolean = true,
    val slPercent: String = "30.0",
    val slPrice: String = "",
    val trailingPercent: String = "1.0"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdvancedTradingScreen(
    symbol: String = "BTCUSDT",
    onNavigateBack: () -> Unit = {},
    onOpenOrderbook: () -> Unit = {},
    onOpenChart: () -> Unit = {}
) {
    var orderForm by remember { mutableStateOf(OrderFormState(symbol = symbol)) }
    var showConfirmDialog by remember { mutableStateOf(false) }
    var showLeverageSheet by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(true) }
    
    var lastPrice by remember { mutableDoubleStateOf(0.0) }
    var markPrice by remember { mutableDoubleStateOf(0.0) }
    var change24h by remember { mutableDoubleStateOf(0.0) }
    var high24h by remember { mutableDoubleStateOf(0.0) }
    var low24h by remember { mutableDoubleStateOf(0.0) }
    var volume24h by remember { mutableDoubleStateOf(0.0) }
    var availableBalance by remember { mutableDoubleStateOf(0.0) }
    
    // Load initial data (no infinite loop - one-time load)
    LaunchedEffect(symbol) {
        lastPrice = 98500.0
        markPrice = 98485.0
        change24h = 2.45
        high24h = 99200.0
        low24h = 96800.0
        volume24h = 45_000_000_000.0
        availableBalance = 10000.0
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = symbol,
                            fontWeight = FontWeight.Bold
                        )
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = String.format("$%.2f", lastPrice),
                                style = MaterialTheme.typography.bodyMedium,
                                color = if (change24h >= 0) LongGreen else ShortRed
                            )
                            Text(
                                text = "${if (change24h >= 0) "+" else ""}${String.format("%.2f", change24h)}%",
                                style = MaterialTheme.typography.bodySmall,
                                color = if (change24h >= 0) LongGreen else ShortRed
                            )
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = onOpenChart) {
                        Icon(Icons.Default.ShowChart, contentDescription = "Chart")
                    }
                    IconButton(onClick = onOpenOrderbook) {
                        Icon(Icons.Default.ViewList, contentDescription = "Orderbook")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
        ) {
            // Market Stats Bar
            MarketStatsBar(
                high24h = high24h,
                low24h = low24h,
                volume24h = volume24h,
                markPrice = markPrice
            )
            
            // Side Selector
            SideSelector(
                selectedSide = orderForm.side,
                onSideChange = { orderForm = orderForm.copy(side = it) }
            )
            
            // Order Type Selector
            OrderTypeSelector(
                selectedType = orderForm.orderType,
                onTypeChange = { orderForm = orderForm.copy(orderType = it) }
            )
            
            // Margin & Leverage
            MarginLeverageRow(
                marginMode = orderForm.marginMode,
                leverage = orderForm.leverage,
                onMarginModeChange = { orderForm = orderForm.copy(marginMode = it) },
                onLeverageClick = { showLeverageSheet = true }
            )
            
            // Order Form
            OrderForm(
                state = orderForm,
                onStateChange = { orderForm = it },
                lastPrice = lastPrice,
                availableBalance = availableBalance
            )
            
            // TP/SL Settings
            TPSLSettings(
                state = orderForm,
                onStateChange = { orderForm = it },
                lastPrice = lastPrice
            )
            
            // Order Options
            OrderOptions(
                reduceOnly = orderForm.reduceOnly,
                postOnly = orderForm.postOnly,
                onReduceOnlyChange = { orderForm = orderForm.copy(reduceOnly = it) },
                onPostOnlyChange = { orderForm = orderForm.copy(postOnly = it) }
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Submit Button
            SubmitOrderButton(
                side = orderForm.side,
                orderType = orderForm.orderType,
                symbol = symbol,
                isValid = orderForm.quantity.toDoubleOrNull() != null && orderForm.quantity.toDoubleOrNull()!! > 0,
                onClick = { showConfirmDialog = true }
            )
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
    
    // Leverage Bottom Sheet
    if (showLeverageSheet) {
        LeverageBottomSheet(
            currentLeverage = orderForm.leverage,
            maxLeverage = 100,
            onLeverageChange = { 
                orderForm = orderForm.copy(leverage = it)
            },
            onDismiss = { showLeverageSheet = false }
        )
    }
    
    // Confirmation Dialog
    if (showConfirmDialog) {
        OrderConfirmationDialog(
            state = orderForm,
            lastPrice = lastPrice,
            onConfirm = {
                // TODO: Submit order
                showConfirmDialog = false
            },
            onDismiss = { showConfirmDialog = false }
        )
    }
}

@Composable
private fun MarketStatsBar(
    high24h: Double,
    low24h: Double,
    volume24h: Double,
    markPrice: Double
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        StatItem("24h High", String.format("%.2f", high24h))
        StatItem("24h Low", String.format("%.2f", low24h))
        StatItem("24h Vol", formatCompact(volume24h))
        StatItem("Mark", String.format("%.2f", markPrice))
    }
}

@Composable
private fun StatItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun SideSelector(
    selectedSide: TradeSide,
    onSideChange: (TradeSide) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        TradeSide.entries.forEach { side ->
            val isSelected = side == selectedSide
            val color = if (side == TradeSide.LONG) LongGreen else ShortRed
            
            Button(
                onClick = { onSideChange(side) },
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isSelected) color else color.copy(alpha = 0.2f),
                    contentColor = if (isSelected) Color.White else color
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(
                    text = if (side == TradeSide.LONG) "Long / Buy" else "Short / Sell",
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
private fun OrderTypeSelector(
    selectedType: OrderType,
    onTypeChange: (OrderType) -> Unit
) {
    LazyRow(
        modifier = Modifier.fillMaxWidth(),
        contentPadding = PaddingValues(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(OrderType.entries) { type ->
            FilterChip(
                selected = type == selectedType,
                onClick = { onTypeChange(type) },
                label = { Text(type.displayName) }
            )
        }
    }
}

@Composable
private fun MarginLeverageRow(
    marginMode: MarginMode,
    leverage: Int,
    onMarginModeChange: (MarginMode) -> Unit,
    onLeverageClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Margin Mode
        Row(
            modifier = Modifier
                .weight(1f)
                .clip(RoundedCornerShape(8.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant)
        ) {
            MarginMode.entries.forEach { mode ->
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .background(
                            if (mode == marginMode) MaterialTheme.colorScheme.primary
                            else Color.Transparent
                        )
                        .clickable { onMarginModeChange(mode) }
                        .padding(vertical = 12.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = mode.name,
                        style = MaterialTheme.typography.labelMedium,
                        color = if (mode == marginMode) 
                            MaterialTheme.colorScheme.onPrimary 
                        else 
                            MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
        
        // Leverage
        OutlinedButton(
            onClick = onLeverageClick,
            modifier = Modifier.weight(1f)
        ) {
            Text(
                text = "${leverage}x",
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.width(4.dp))
            Icon(
                Icons.Default.KeyboardArrowDown,
                contentDescription = null,
                modifier = Modifier.size(16.dp)
            )
        }
    }
}

@Composable
private fun OrderForm(
    state: OrderFormState,
    onStateChange: (OrderFormState) -> Unit,
    lastPrice: Double,
    availableBalance: Double
) {
    Column(
        modifier = Modifier.padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Price field (for limit orders)
        if (state.orderType != OrderType.MARKET) {
            OutlinedTextField(
                value = state.price,
                onValueChange = { onStateChange(state.copy(price = it)) },
                label = { Text("Price (USDT)") },
                placeholder = { Text(String.format("%.2f", lastPrice)) },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                modifier = Modifier.fillMaxWidth(),
                trailingIcon = {
                    TextButton(onClick = { 
                        onStateChange(state.copy(price = String.format("%.2f", lastPrice))) 
                    }) {
                        Text("Last")
                    }
                }
            )
        }
        
        // Stop Price (for stop orders)
        if (state.orderType == OrderType.STOP_MARKET || 
            state.orderType == OrderType.STOP_LIMIT) {
            OutlinedTextField(
                value = state.stopPrice,
                onValueChange = { onStateChange(state.copy(stopPrice = it)) },
                label = { Text("Trigger Price (USDT)") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                modifier = Modifier.fillMaxWidth()
            )
        }
        
        // Trailing Percent (for trailing stop)
        if (state.orderType == OrderType.TRAILING_STOP) {
            OutlinedTextField(
                value = state.trailingPercent,
                onValueChange = { onStateChange(state.copy(trailingPercent = it)) },
                label = { Text("Trailing Distance (%)") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                modifier = Modifier.fillMaxWidth()
            )
        }
        
        // Quantity
        OutlinedTextField(
            value = state.quantity,
            onValueChange = { onStateChange(state.copy(quantity = it)) },
            label = { Text("Quantity (${state.symbol.replace("USDT", "")})") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            modifier = Modifier.fillMaxWidth(),
            supportingText = {
                Text("Available: ${String.format("%.2f", availableBalance)} USDT")
            }
        )
        
        // Quick Amount Buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("25%", "50%", "75%", "100%").forEach { pct ->
                OutlinedButton(
                    onClick = {
                        val percent = pct.removeSuffix("%").toInt()
                        val amount = availableBalance * percent / 100 / lastPrice * state.leverage
                        onStateChange(state.copy(quantity = String.format("%.4f", amount)))
                    },
                    modifier = Modifier.weight(1f),
                    contentPadding = PaddingValues(4.dp)
                ) {
                    Text(pct, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
private fun TPSLSettings(
    state: OrderFormState,
    onStateChange: (OrderFormState) -> Unit,
    lastPrice: Double
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Take Profit / Stop Loss",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )
            
            // Take Profit
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Checkbox(
                    checked = state.tpEnabled,
                    onCheckedChange = { onStateChange(state.copy(tpEnabled = it)) }
                )
                Text("TP", modifier = Modifier.width(28.dp))
                OutlinedTextField(
                    value = state.tpPercent,
                    onValueChange = { onStateChange(state.copy(tpPercent = it)) },
                    modifier = Modifier.weight(1f),
                    suffix = { Text("%") },
                    enabled = state.tpEnabled,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    singleLine = true
                )
                OutlinedTextField(
                    value = state.tpPrice.ifEmpty { 
                        state.tpPercent.toDoubleOrNull()?.let { pct ->
                            val mult = if (state.side == TradeSide.LONG) 1 + pct/100 else 1 - pct/100
                            String.format("%.2f", lastPrice * mult)
                        } ?: ""
                    },
                    onValueChange = { onStateChange(state.copy(tpPrice = it)) },
                    modifier = Modifier.weight(1.2f),
                    prefix = { Text("$") },
                    enabled = state.tpEnabled,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    singleLine = true
                )
            }
            
            // Stop Loss
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Checkbox(
                    checked = state.slEnabled,
                    onCheckedChange = { onStateChange(state.copy(slEnabled = it)) }
                )
                Text("SL", modifier = Modifier.width(28.dp))
                OutlinedTextField(
                    value = state.slPercent,
                    onValueChange = { onStateChange(state.copy(slPercent = it)) },
                    modifier = Modifier.weight(1f),
                    suffix = { Text("%") },
                    enabled = state.slEnabled,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    singleLine = true
                )
                OutlinedTextField(
                    value = state.slPrice.ifEmpty {
                        state.slPercent.toDoubleOrNull()?.let { pct ->
                            val mult = if (state.side == TradeSide.LONG) 1 - pct/100 else 1 + pct/100
                            String.format("%.2f", lastPrice * mult)
                        } ?: ""
                    },
                    onValueChange = { onStateChange(state.copy(slPrice = it)) },
                    modifier = Modifier.weight(1.2f),
                    prefix = { Text("$") },
                    enabled = state.slEnabled,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    singleLine = true
                )
            }
        }
    }
}

@Composable
private fun OrderOptions(
    reduceOnly: Boolean,
    postOnly: Boolean,
    onReduceOnlyChange: (Boolean) -> Unit,
    onPostOnlyChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(checked = reduceOnly, onCheckedChange = onReduceOnlyChange)
            Text("Reduce Only", style = MaterialTheme.typography.bodyMedium)
        }
        
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(checked = postOnly, onCheckedChange = onPostOnlyChange)
            Text("Post Only", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun SubmitOrderButton(
    side: TradeSide,
    orderType: OrderType,
    symbol: String,
    isValid: Boolean,
    onClick: () -> Unit
) {
    val color = if (side == TradeSide.LONG) LongGreen else ShortRed
    val text = "${if (side == TradeSide.LONG) "Buy/Long" else "Sell/Short"} ${symbol.replace("USDT", "")}"
    
    Button(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
            .height(56.dp),
        enabled = isValid,
        colors = ButtonDefaults.buttonColors(
            containerColor = color,
            disabledContainerColor = color.copy(alpha = 0.3f)
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun LeverageBottomSheet(
    currentLeverage: Int,
    maxLeverage: Int,
    onLeverageChange: (Int) -> Unit,
    onDismiss: () -> Unit
) {
    var tempLeverage by remember { mutableIntStateOf(currentLeverage) }
    
    ModalBottomSheet(
        onDismissRequest = onDismiss
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Adjust Leverage",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Text(
                text = "${tempLeverage}x",
                style = MaterialTheme.typography.displayMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Slider(
                value = tempLeverage.toFloat(),
                onValueChange = { tempLeverage = it.toInt() },
                valueRange = 1f..maxLeverage.toFloat(),
                steps = maxLeverage - 2
            )
            
            // Quick leverage buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                listOf(1, 5, 10, 25, 50, 100).filter { it <= maxLeverage }.forEach { lev ->
                    OutlinedButton(
                        onClick = { tempLeverage = lev },
                        modifier = Modifier.width(56.dp),
                        contentPadding = PaddingValues(4.dp)
                    ) {
                        Text("${lev}x", fontSize = 12.sp)
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Button(
                onClick = {
                    onLeverageChange(tempLeverage)
                    onDismiss()
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Confirm")
            }
            
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun OrderConfirmationDialog(
    state: OrderFormState,
    lastPrice: Double,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    val sideColor = if (state.side == TradeSide.LONG) LongGreen else ShortRed
    val quantity = state.quantity.toDoubleOrNull() ?: 0.0
    val price = state.price.toDoubleOrNull() ?: lastPrice
    val notional = quantity * price
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = "Confirm Order",
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(state.symbol, fontWeight = FontWeight.Bold)
                    Text(
                        text = if (state.side == TradeSide.LONG) "LONG" else "SHORT",
                        color = sideColor,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                HorizontalDivider()
                
                ConfirmRow("Order Type", state.orderType.displayName)
                ConfirmRow("Price", if (state.orderType == OrderType.MARKET) "Market" else "$${String.format("%.2f", price)}")
                ConfirmRow("Quantity", String.format("%.4f", quantity))
                ConfirmRow("Notional", "$${String.format("%.2f", notional)}")
                ConfirmRow("Leverage", "${state.leverage}x")
                
                if (state.tpEnabled) {
                    ConfirmRow("Take Profit", "${state.tpPercent}%", LongGreen)
                }
                if (state.slEnabled) {
                    ConfirmRow("Stop Loss", "${state.slPercent}%", ShortRed)
                }
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirm,
                colors = ButtonDefaults.buttonColors(containerColor = sideColor)
            ) {
                Text("Confirm ${if (state.side == TradeSide.LONG) "Buy" else "Sell"}")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

@Composable
private fun ConfirmRow(
    label: String,
    value: String,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            fontWeight = FontWeight.Medium,
            color = valueColor
        )
    }
}

private fun formatCompact(value: Double): String {
    return when {
        value >= 1_000_000_000 -> String.format("%.1fB", value / 1_000_000_000)
        value >= 1_000_000 -> String.format("%.1fM", value / 1_000_000)
        value >= 1_000 -> String.format("%.1fK", value / 1_000)
        else -> String.format("%.0f", value)
    }
}
