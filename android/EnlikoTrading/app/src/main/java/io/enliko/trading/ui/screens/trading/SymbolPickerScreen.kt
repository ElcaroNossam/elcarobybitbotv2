package io.enliko.trading.ui.screens.trading

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*

/**
 * SymbolPickerScreen - Matching iOS SymbolPickerView.swift
 * Symbol selection bottom sheet with search and popular symbols
 */

data class SymbolInfo(
    val symbol: String,
    val base: String,
    val quote: String = "USDT",
    val price: Double = 0.0,
    val change24h: Double = 0.0
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SymbolPickerBottomSheet(
    selectedSymbol: String,
    onSymbolSelected: (String) -> Unit,
    onDismiss: () -> Unit
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = EnlikoBackground,
        dragHandle = { BottomSheetDefaults.DragHandle(color = EnlikoTextMuted) }
    ) {
        SymbolPickerContent(
            selectedSymbol = selectedSymbol,
            onSymbolSelected = { symbol ->
                onSymbolSelected(symbol)
                onDismiss()
            },
            onDone = onDismiss
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SymbolPickerContent(
    selectedSymbol: String,
    onSymbolSelected: (String) -> Unit,
    onDone: () -> Unit
) {
    var searchText by remember { mutableStateOf("") }
    
    // Sample symbols - in real app, get from API
    val allSymbols = remember {
        listOf(
            SymbolInfo("BTCUSDT", "BTC", price = 95000.0, change24h = 2.5),
            SymbolInfo("ETHUSDT", "ETH", price = 3400.0, change24h = -1.2),
            SymbolInfo("SOLUSDT", "SOL", price = 145.0, change24h = 5.3),
            SymbolInfo("XRPUSDT", "XRP", price = 2.1, change24h = 0.8),
            SymbolInfo("DOGEUSDT", "DOGE", price = 0.12, change24h = -0.5),
            SymbolInfo("BNBUSDT", "BNB", price = 650.0, change24h = 1.1),
            SymbolInfo("ADAUSDT", "ADA", price = 0.95, change24h = 3.2),
            SymbolInfo("AVAXUSDT", "AVAX", price = 38.0, change24h = -2.1),
            SymbolInfo("DOTUSDT", "DOT", price = 7.5, change24h = 1.5),
            SymbolInfo("MATICUSDT", "MATIC", price = 0.85, change24h = 0.3),
            SymbolInfo("LINKUSDT", "LINK", price = 18.0, change24h = 4.2),
            SymbolInfo("ATOMUSDT", "ATOM", price = 9.5, change24h = -0.8),
            SymbolInfo("LTCUSDT", "LTC", price = 95.0, change24h = 1.0),
            SymbolInfo("NEARUSDT", "NEAR", price = 5.2, change24h = 2.8),
            SymbolInfo("APTUSDT", "APT", price = 12.0, change24h = -1.5)
        )
    }
    
    val popularSymbols = listOf("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT")
    
    val filteredSymbols = if (searchText.isEmpty()) {
        allSymbols
    } else {
        allSymbols.filter { it.symbol.contains(searchText, ignoreCase = true) }
    }
    
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(max = 600.dp)
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Select Symbol",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
            
            TextButton(onClick = onDone) {
                Text("Done", color = EnlikoPrimary)
            }
        }
        
        // Search Bar
        OutlinedTextField(
            value = searchText,
            onValueChange = { searchText = it },
            placeholder = { Text("Search symbols...") },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
            trailingIcon = {
                if (searchText.isNotEmpty()) {
                    IconButton(onClick = { searchText = "" }) {
                        Icon(Icons.Default.Clear, contentDescription = "Clear")
                    }
                }
            },
            singleLine = true,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = EnlikoPrimary,
                unfocusedBorderColor = EnlikoBorder,
                focusedTextColor = EnlikoTextPrimary,
                unfocusedTextColor = EnlikoTextPrimary,
                cursorColor = EnlikoPrimary
            ),
            shape = RoundedCornerShape(12.dp)
        )
        
        // Popular Section (only when not searching)
        if (searchText.isEmpty()) {
            PopularSymbolsSection(
                popularSymbols = popularSymbols,
                selectedSymbol = selectedSymbol,
                onSymbolSelected = onSymbolSelected
            )
            
            HorizontalDivider(
                color = EnlikoBorder,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }
        
        // Symbols List
        LazyColumn(
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(filteredSymbols, key = { it.symbol }) { symbolInfo ->
                SymbolRow(
                    symbolInfo = symbolInfo,
                    isSelected = selectedSymbol == symbolInfo.symbol,
                    onClick = { onSymbolSelected(symbolInfo.symbol) }
                )
            }
        }
    }
}

@Composable
private fun PopularSymbolsSection(
    popularSymbols: List<String>,
    selectedSymbol: String,
    onSymbolSelected: (String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        Text(
            text = "Popular",
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Medium,
            color = EnlikoTextSecondary,
            modifier = Modifier.padding(horizontal = 16.dp, bottom = 8.dp)
        )
        
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState())
                .padding(horizontal = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            popularSymbols.forEach { symbol ->
                val displayName = symbol.replace("USDT", "")
                val isSelected = selectedSymbol == symbol
                
                Surface(
                    onClick = { onSymbolSelected(symbol) },
                    color = if (isSelected) EnlikoPrimary else EnlikoCard,
                    shape = RoundedCornerShape(20.dp)
                ) {
                    Text(
                        text = displayName,
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Medium,
                        color = if (isSelected) Color.White else EnlikoTextPrimary,
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun SymbolRow(
    symbolInfo: SymbolInfo,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        color = EnlikoCard,
        shape = RoundedCornerShape(12.dp)
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
                // Symbol Icon
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(EnlikoSurface),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = symbolInfo.base.take(1),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = EnlikoPrimary
                    )
                }
                
                // Symbol Name
                Column {
                    Text(
                        text = symbolInfo.base,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = EnlikoTextPrimary
                    )
                    
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            text = "/ USDT",
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                        
                        if (symbolInfo.price > 0) {
                            Text(
                                text = "$${formatSymbolPrice(symbolInfo.price)}",
                                style = MaterialTheme.typography.bodySmall,
                                color = EnlikoTextSecondary
                            )
                        }
                    }
                }
            }
            
            // Price Change & Selection
            Column(horizontalAlignment = Alignment.End) {
                if (symbolInfo.change24h != 0.0) {
                    val changeColor = if (symbolInfo.change24h >= 0) EnlikoGreen else EnlikoRed
                    Text(
                        text = "${if (symbolInfo.change24h >= 0) "+" else ""}${String.format("%.2f", symbolInfo.change24h)}%",
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Medium,
                        color = changeColor
                    )
                }
                
                if (isSelected) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = "Selected",
                        tint = EnlikoPrimary,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }
    }
}

private fun formatSymbolPrice(price: Double): String {
    return when {
        price < 0.01 -> String.format("%.6f", price)
        price < 1 -> String.format("%.4f", price)
        price < 100 -> String.format("%.2f", price)
        else -> String.format("%.0f", price)
    }
}
