package io.enliko.trading.ui.screens.trading

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManualTradingScreen(
    symbol: String? = null,
    onBack: () -> Unit,
    viewModel: ManualTradingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    // Initialize symbol if provided
    LaunchedEffect(symbol) {
        symbol?.let { viewModel.selectSymbol(it) }
    }
    
    // Show success/error messages
    LaunchedEffect(uiState.successMessage) {
        uiState.successMessage?.let {
            // Auto-dismiss after 3 seconds
            kotlinx.coroutines.delay(3000)
            viewModel.clearMessages()
        }
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
    ) {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(bottom = 100.dp)
        ) {
            // Header
            item {
                ManualTradingHeader(
                    symbol = uiState.symbol,
                    currentPrice = uiState.currentPrice,
                    onBack = onBack
                )
            }
            
            // Symbol Selector
            item {
                SymbolSelector(
                    currentSymbol = uiState.symbol,
                    searchQuery = uiState.searchQuery,
                    filteredSymbols = uiState.filteredSymbols,
                    onSearchChange = viewModel::updateSearchQuery,
                    onSymbolSelect = viewModel::selectSymbol
                )
            }
            
            // Side Selector (Long/Short)
            item {
                SideSelector(
                    currentSide = uiState.side,
                    onSideChange = viewModel::setSide
                )
            }
            
            // Order Type Selector
            item {
                OrderTypeSelector(
                    currentType = uiState.orderType,
                    onTypeChange = viewModel::setOrderType
                )
            }
            
            // Amount Input
            item {
                AmountInputSection(
                    amountUsdt = uiState.amountUsdt,
                    qty = uiState.qty,
                    currentPrice = uiState.currentPrice,
                    availableBalance = uiState.availableBalance,
                    onAmountChange = viewModel::setAmountUsdt,
                    onQtyChange = viewModel::setQty
                )
            }
            
            // Limit Price (if limit order)
            if (uiState.orderType == "Limit") {
                item {
                    LimitPriceInput(
                        limitPrice = uiState.limitPrice,
                        currentPrice = uiState.currentPrice,
                        onLimitPriceChange = viewModel::setLimitPrice
                    )
                }
            }
            
            // Leverage Slider
            item {
                LeverageSection(
                    leverage = uiState.leverage,
                    onLeverageChange = viewModel::setLeverage,
                    onApplyLeverage = viewModel::applyLeverage
                )
            }
            
            // TP/SL Section
            item {
                TpSlSection(
                    useTpSlPercent = uiState.useTpSlPercent,
                    tpPercent = uiState.tpPercent,
                    slPercent = uiState.slPercent,
                    takeProfit = uiState.takeProfit,
                    stopLoss = uiState.stopLoss,
                    onToggleTpSlMode = viewModel::toggleTpSlMode,
                    onTpPercentChange = viewModel::setTpPercent,
                    onSlPercentChange = viewModel::setSlPercent,
                    onTpChange = viewModel::setTakeProfit,
                    onSlChange = viewModel::setStopLoss
                )
            }
            
            // Order Summary
            item {
                OrderSummary(
                    symbol = uiState.symbol,
                    side = uiState.side,
                    orderType = uiState.orderType,
                    amountUsdt = uiState.amountUsdt,
                    qty = uiState.qty,
                    leverage = uiState.leverage,
                    tpPercent = uiState.tpPercent,
                    slPercent = uiState.slPercent,
                    accountType = uiState.accountType,
                    exchange = uiState.exchange
                )
            }
        }
        
        // Place Order Button (fixed at bottom)
        PlaceOrderButton(
            isLoading = uiState.isLoading,
            side = uiState.side,
            isEnabled = uiState.amountUsdt > 0,
            onPlaceOrder = viewModel::placeOrder,
            modifier = Modifier.align(Alignment.BottomCenter)
        )
        
        // Success/Error Overlay
        AnimatedVisibility(
            visible = uiState.successMessage != null || uiState.error != null,
            enter = fadeIn() + slideInVertically(),
            exit = fadeOut() + slideOutVertically(),
            modifier = Modifier.align(Alignment.TopCenter)
        ) {
            MessageBanner(
                message = uiState.successMessage ?: uiState.error ?: "",
                isSuccess = uiState.successMessage != null
            )
        }
    }
}

@Composable
private fun ManualTradingHeader(
    symbol: String,
    currentPrice: Double,
    onBack: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(onClick = onBack) {
            Icon(
                Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = "Back",
                tint = Color.White
            )
        }
        
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = symbol,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            if (currentPrice > 0) {
                Text(
                    text = "$${String.format("%,.2f", currentPrice)}",
                    fontSize = 14.sp,
                    color = EnlikoCyan
                )
            }
        }
        
        IconButton(onClick = { /* Refresh price */ }) {
            Icon(
                Icons.Default.Refresh,
                contentDescription = "Refresh",
                tint = Color.White.copy(alpha = 0.7f)
            )
        }
    }
}

@Composable
private fun SymbolSelector(
    currentSymbol: String,
    searchQuery: String,
    filteredSymbols: List<String>,
    onSearchChange: (String) -> Unit,
    onSymbolSelect: (String) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        // Current Symbol Card
        GlassCard(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { expanded = !expanded }
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Symbol",
                    color = Color.White.copy(alpha = 0.7f),
                    fontSize = 14.sp
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = currentSymbol,
                        color = EnlikoCyan,
                        fontWeight = FontWeight.Bold
                    )
                    Icon(
                        if (expanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                        contentDescription = null,
                        tint = Color.White.copy(alpha = 0.5f)
                    )
                }
            }
        }
        
        // Symbol List (expandable)
        AnimatedVisibility(visible = expanded) {
            GlassCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            ) {
                Column(modifier = Modifier.padding(8.dp)) {
                    // Search Field
                    OutlinedTextField(
                        value = searchQuery,
                        onValueChange = onSearchChange,
                        placeholder = { Text("Search symbol...", color = Color.White.copy(alpha = 0.5f)) },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White,
                            focusedBorderColor = EnlikoCyan,
                            unfocusedBorderColor = GlassBorder
                        ),
                        singleLine = true,
                        leadingIcon = {
                            Icon(Icons.Default.Search, null, tint = Color.White.copy(alpha = 0.5f))
                        }
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // Symbol Grid
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        contentPadding = PaddingValues(4.dp)
                    ) {
                        items(filteredSymbols.take(10)) { sym ->
                            SymbolChip(
                                symbol = sym,
                                isSelected = sym == currentSymbol,
                                onClick = {
                                    onSymbolSelect(sym)
                                    expanded = false
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SymbolChip(
    symbol: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    val bgColor = if (isSelected) EnlikoCyan.copy(alpha = 0.3f) else GlassBackground
    val borderColor = if (isSelected) EnlikoCyan else GlassBorder
    
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(bgColor)
            .border(1.dp, borderColor, RoundedCornerShape(8.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 12.dp, vertical = 8.dp)
    ) {
        Text(
            text = symbol.replace("USDT", ""),
            color = if (isSelected) EnlikoCyan else Color.White,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
            fontSize = 13.sp
        )
    }
}

@Composable
private fun SideSelector(
    currentSide: String,
    onSideChange: (String) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Long Button
        Box(
            modifier = Modifier
                .weight(1f)
                .clip(RoundedCornerShape(12.dp))
                .background(
                    if (currentSide == "Buy") 
                        Brush.linearGradient(GradientProfitColors)
                    else 
                        Brush.linearGradient(listOf(GlassBackground, GlassBackground))
                )
                .border(
                    width = 1.dp,
                    color = if (currentSide == "Buy") PositionLong else GlassBorder,
                    shape = RoundedCornerShape(12.dp)
                )
                .clickable { onSideChange("Buy") }
                .padding(vertical = 16.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    Icons.Default.TrendingUp,
                    contentDescription = null,
                    tint = if (currentSide == "Buy") Color.White else PositionLong
                )
                Text(
                    text = "LONG",
                    color = if (currentSide == "Buy") Color.White else PositionLong,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
            }
        }
        
        // Short Button
        Box(
            modifier = Modifier
                .weight(1f)
                .clip(RoundedCornerShape(12.dp))
                .background(
                    if (currentSide == "Sell") 
                        Brush.linearGradient(GradientLossColors)
                    else 
                        Brush.linearGradient(listOf(GlassBackground, GlassBackground))
                )
                .border(
                    width = 1.dp,
                    color = if (currentSide == "Sell") PositionShort else GlassBorder,
                    shape = RoundedCornerShape(12.dp)
                )
                .clickable { onSideChange("Sell") }
                .padding(vertical = 16.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    Icons.Default.TrendingDown,
                    contentDescription = null,
                    tint = if (currentSide == "Sell") Color.White else PositionShort
                )
                Text(
                    text = "SHORT",
                    color = if (currentSide == "Sell") Color.White else PositionShort,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
            }
        }
    }
}

@Composable
private fun OrderTypeSelector(
    currentType: String,
    onTypeChange: (String) -> Unit
) {
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("Market", "Limit").forEach { type ->
                val isSelected = currentType == type
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(8.dp))
                        .background(if (isSelected) EnlikoCyan.copy(alpha = 0.2f) else Color.Transparent)
                        .border(
                            width = 1.dp,
                            color = if (isSelected) EnlikoCyan else Color.Transparent,
                            shape = RoundedCornerShape(8.dp)
                        )
                        .clickable { onTypeChange(type) }
                        .padding(vertical = 12.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = type,
                        color = if (isSelected) EnlikoCyan else Color.White.copy(alpha = 0.7f),
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                    )
                }
            }
        }
    }
}

@Composable
private fun AmountInputSection(
    amountUsdt: Double,
    qty: Double,
    currentPrice: Double,
    availableBalance: Double,
    onAmountChange: (Double) -> Unit,
    onQtyChange: (Double) -> Unit
) {
    var amountText by remember { mutableStateOf(if (amountUsdt > 0) amountUsdt.toString() else "") }
    var qtyText by remember { mutableStateOf(if (qty > 0) qty.toString() else "") }
    
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Amount",
                    color = Color.White,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = "Available: $${String.format("%,.2f", availableBalance)}",
                    color = Color.White.copy(alpha = 0.6f),
                    fontSize = 12.sp
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // USDT Amount Input
            OutlinedTextField(
                value = amountText,
                onValueChange = { 
                    amountText = it
                    it.toDoubleOrNull()?.let(onAmountChange)
                },
                label = { Text("Amount (USDT)", color = Color.White.copy(alpha = 0.5f)) },
                modifier = Modifier.fillMaxWidth(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    focusedBorderColor = EnlikoCyan,
                    unfocusedBorderColor = GlassBorder
                ),
                singleLine = true,
                trailingIcon = {
                    Text("USDT", color = EnlikoCyan, fontSize = 12.sp)
                }
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Quick Amount Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(0.25, 0.5, 0.75, 1.0).forEach { percent ->
                    TextButton(
                        onClick = {
                            val amount = availableBalance * percent
                            amountText = String.format("%.2f", amount)
                            onAmountChange(amount)
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(
                            "${(percent * 100).toInt()}%",
                            color = EnlikoCyan,
                            fontSize = 12.sp
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Quantity Input
            OutlinedTextField(
                value = qtyText,
                onValueChange = {
                    qtyText = it
                    it.toDoubleOrNull()?.let(onQtyChange)
                },
                label = { Text("Quantity (Coins)", color = Color.White.copy(alpha = 0.5f)) },
                modifier = Modifier.fillMaxWidth(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    focusedBorderColor = EnlikoCyan,
                    unfocusedBorderColor = GlassBorder
                ),
                singleLine = true
            )
        }
    }
}

@Composable
private fun LimitPriceInput(
    limitPrice: Double?,
    currentPrice: Double,
    onLimitPriceChange: (Double) -> Unit
) {
    var priceText by remember { mutableStateOf(limitPrice?.toString() ?: "") }
    
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Limit Price",
                color = Color.White,
                fontWeight = FontWeight.SemiBold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            OutlinedTextField(
                value = priceText,
                onValueChange = {
                    priceText = it
                    it.toDoubleOrNull()?.let(onLimitPriceChange)
                },
                placeholder = { 
                    Text("Current: $${String.format("%,.2f", currentPrice)}", 
                         color = Color.White.copy(alpha = 0.5f)) 
                },
                modifier = Modifier.fillMaxWidth(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    focusedBorderColor = EnlikoCyan,
                    unfocusedBorderColor = GlassBorder
                ),
                singleLine = true,
                trailingIcon = {
                    Text("USDT", color = EnlikoCyan, fontSize = 12.sp)
                }
            )
        }
    }
}

@Composable
private fun LeverageSection(
    leverage: Int,
    onLeverageChange: (Int) -> Unit,
    onApplyLeverage: () -> Unit
) {
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Leverage",
                    color = Color.White,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = "${leverage}x",
                    color = EnlikoOrange,
                    fontWeight = FontWeight.Bold,
                    fontSize = 20.sp
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Slider(
                value = leverage.toFloat(),
                onValueChange = { onLeverageChange(it.toInt()) },
                valueRange = 1f..100f,
                steps = 98,
                modifier = Modifier.fillMaxWidth(),
                colors = SliderDefaults.colors(
                    thumbColor = EnlikoOrange,
                    activeTrackColor = EnlikoOrange,
                    inactiveTrackColor = GlassBorder
                )
            )
            
            // Quick leverage buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                listOf(1, 5, 10, 25, 50, 100).forEach { lev ->
                    TextButton(
                        onClick = { onLeverageChange(lev) },
                        contentPadding = PaddingValues(4.dp)
                    ) {
                        Text(
                            "${lev}x",
                            color = if (leverage == lev) EnlikoOrange else Color.White.copy(alpha = 0.6f),
                            fontSize = 12.sp,
                            fontWeight = if (leverage == lev) FontWeight.Bold else FontWeight.Normal
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Button(
                onClick = onApplyLeverage,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = EnlikoOrange.copy(alpha = 0.2f)
                ),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Apply Leverage to Symbol", color = EnlikoOrange)
            }
        }
    }
}

@Composable
private fun TpSlSection(
    useTpSlPercent: Boolean,
    tpPercent: Double?,
    slPercent: Double?,
    takeProfit: Double?,
    stopLoss: Double?,
    onToggleTpSlMode: () -> Unit,
    onTpPercentChange: (Double) -> Unit,
    onSlPercentChange: (Double) -> Unit,
    onTpChange: (Double) -> Unit,
    onSlChange: (Double) -> Unit
) {
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Take Profit / Stop Loss",
                    color = Color.White,
                    fontWeight = FontWeight.SemiBold
                )
                
                // Toggle percent/absolute
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(GlassBackground)
                        .border(1.dp, GlassBorder, RoundedCornerShape(8.dp))
                        .clickable(onClick = onToggleTpSlMode)
                        .padding(horizontal = 12.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = if (useTpSlPercent) "%" else "$",
                        color = EnlikoCyan,
                        fontWeight = FontWeight.Bold
                    )
                    Icon(
                        Icons.Default.SwapHoriz,
                        contentDescription = null,
                        tint = Color.White.copy(alpha = 0.5f),
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Take Profit
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Take Profit",
                        color = PositionLong,
                        fontSize = 12.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    if (useTpSlPercent) {
                        TpSlPercentInput(
                            value = tpPercent,
                            onValueChange = onTpPercentChange,
                            color = PositionLong
                        )
                    } else {
                        TpSlPriceInput(
                            value = takeProfit,
                            onValueChange = onTpChange,
                            color = PositionLong
                        )
                    }
                }
                
                // Stop Loss
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Stop Loss",
                        color = PositionShort,
                        fontSize = 12.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    if (useTpSlPercent) {
                        TpSlPercentInput(
                            value = slPercent,
                            onValueChange = onSlPercentChange,
                            color = PositionShort
                        )
                    } else {
                        TpSlPriceInput(
                            value = stopLoss,
                            onValueChange = onSlChange,
                            color = PositionShort
                        )
                    }
                }
            }
            
            // Quick TP/SL presets
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "Quick presets",
                color = Color.White.copy(alpha = 0.5f),
                fontSize = 11.sp
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf("1%/0.5%", "3%/1%", "5%/2%", "10%/3%").forEach { preset ->
                    val parts = preset.replace("%", "").split("/")
                    val tp = parts[0].toDouble()
                    val sl = parts[1].toDouble()
                    
                    TextButton(
                        onClick = {
                            onTpPercentChange(tp)
                            onSlPercentChange(sl)
                        },
                        contentPadding = PaddingValues(4.dp)
                    ) {
                        Text(preset, color = EnlikoCyan, fontSize = 11.sp)
                    }
                }
            }
        }
    }
}

@Composable
private fun TpSlPercentInput(
    value: Double?,
    onValueChange: (Double) -> Unit,
    color: Color
) {
    var text by remember { mutableStateOf(value?.toString() ?: "") }
    
    OutlinedTextField(
        value = text,
        onValueChange = {
            text = it
            it.toDoubleOrNull()?.let(onValueChange)
        },
        placeholder = { Text("0.0%", color = Color.White.copy(alpha = 0.3f)) },
        modifier = Modifier.fillMaxWidth(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = Color.White,
            unfocusedTextColor = Color.White,
            focusedBorderColor = color,
            unfocusedBorderColor = GlassBorder
        ),
        singleLine = true,
        trailingIcon = {
            Text("%", color = color, fontSize = 12.sp)
        }
    )
}

@Composable
private fun TpSlPriceInput(
    value: Double?,
    onValueChange: (Double) -> Unit,
    color: Color
) {
    var text by remember { mutableStateOf(value?.toString() ?: "") }
    
    OutlinedTextField(
        value = text,
        onValueChange = {
            text = it
            it.toDoubleOrNull()?.let(onValueChange)
        },
        placeholder = { Text("Price", color = Color.White.copy(alpha = 0.3f)) },
        modifier = Modifier.fillMaxWidth(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = Color.White,
            unfocusedTextColor = Color.White,
            focusedBorderColor = color,
            unfocusedBorderColor = GlassBorder
        ),
        singleLine = true,
        trailingIcon = {
            Text("$", color = color, fontSize = 12.sp)
        }
    )
}

@Composable
private fun OrderSummary(
    symbol: String,
    side: String,
    orderType: String,
    amountUsdt: Double,
    qty: Double,
    leverage: Int,
    tpPercent: Double?,
    slPercent: Double?,
    accountType: String,
    exchange: String
) {
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Order Summary",
                color = Color.White,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            SummaryRow("Symbol", symbol)
            SummaryRow("Direction", if (side == "Buy") "🟢 LONG" else "🔴 SHORT")
            SummaryRow("Type", orderType)
            SummaryRow("Amount", "$${String.format("%,.2f", amountUsdt)}")
            SummaryRow("Quantity", String.format("%.6f", qty))
            SummaryRow("Leverage", "${leverage}x")
            tpPercent?.let { SummaryRow("Take Profit", "+${it}%", PositionLong) }
            slPercent?.let { SummaryRow("Stop Loss", "-${it}%", PositionShort) }
            
            Divider(
                modifier = Modifier.padding(vertical = 8.dp),
                color = GlassBorder
            )
            
            SummaryRow("Exchange", exchange.replaceFirstChar { it.uppercase() })
            SummaryRow("Account", accountType.replaceFirstChar { it.uppercase() })
        }
    }
}

@Composable
private fun SummaryRow(
    label: String,
    value: String,
    valueColor: Color = Color.White
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            color = Color.White.copy(alpha = 0.6f),
            fontSize = 13.sp
        )
        Text(
            text = value,
            color = valueColor,
            fontWeight = FontWeight.SemiBold,
            fontSize = 13.sp
        )
    }
}

@Composable
private fun PlaceOrderButton(
    isLoading: Boolean,
    side: String,
    isEnabled: Boolean,
    onPlaceOrder: () -> Unit,
    modifier: Modifier = Modifier
) {
    val gradient = if (side == "Buy") GradientProfitColors else GradientLossColors
    val text = if (side == "Buy") "Place Long Order" else "Place Short Order"
    
    Box(
        modifier = modifier
            .fillMaxWidth()
            .background(
                Brush.verticalGradient(
                    colors = listOf(Color.Transparent, DarkBackground)
                )
            )
            .padding(16.dp)
    ) {
        Button(
            onClick = onPlaceOrder,
            enabled = isEnabled && !isLoading,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.Transparent,
                disabledContainerColor = GlassBackground
            ),
            contentPadding = PaddingValues(0.dp)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        brush = Brush.linearGradient(if (isEnabled) gradient else listOf(GlassBorder, GlassBorder)),
                        shape = RoundedCornerShape(16.dp)
                    ),
                contentAlignment = Alignment.Center
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White,
                        strokeWidth = 2.dp
                    )
                } else {
                    Text(
                        text = text,
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp
                    )
                }
            }
        }
    }
}

@Composable
private fun MessageBanner(
    message: String,
    isSuccess: Boolean
) {
    val backgroundColor = if (isSuccess) PositionLong.copy(alpha = 0.9f) else PositionShort.copy(alpha = 0.9f)
    val icon = if (isSuccess) Icons.Default.CheckCircle else Icons.Default.Error
    
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(backgroundColor)
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Icon(icon, contentDescription = null, tint = Color.White)
        Text(
            text = message,
            color = Color.White,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun GlassCard(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(GlassBackground)
            .border(1.dp, GlassBorder, RoundedCornerShape(16.dp))
    ) {
        content()
    }
}
