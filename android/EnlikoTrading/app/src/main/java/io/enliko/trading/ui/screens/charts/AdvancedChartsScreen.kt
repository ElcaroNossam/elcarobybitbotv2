package io.enliko.trading.ui.screens.charts

import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import io.enliko.trading.util.LocalStrings
import java.text.DecimalFormat

enum class ChartTimeframe(val label: String, val interval: String) {
    M1("1m", "1"),
    M5("5m", "5"),
    M15("15m", "15"),
    H1("1H", "60"),
    H4("4H", "240"),
    D1("1D", "D"),
    W1("1W", "W")
}

enum class ChartIndicator(val label: String) {
    MA7("MA 7"),
    MA25("MA 25"),
    MA99("MA 99"),
    EMA12("EMA 12"),
    EMA26("EMA 26"),
    BB("Bollinger"),
    RSI("RSI"),
    MACD("MACD"),
    VOL("Volume")
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdvancedChartsScreen(
    symbol: String = "BTCUSDT",
    onBack: () -> Unit = {}
) {
    var selectedTimeframe by remember { mutableStateOf(ChartTimeframe.H1) }
    var enabledIndicators by remember { mutableStateOf(setOf(ChartIndicator.MA7, ChartIndicator.MA25)) }
    var showIndicatorsDialog by remember { mutableStateOf(false) }
    
    // Mock data - in production this would come from WebSocket
    var currentPrice by remember { mutableDoubleStateOf(97542.50) }
    var priceChange24h by remember { mutableDoubleStateOf(2.45) }
    var high24h by remember { mutableDoubleStateOf(98500.00) }
    var low24h by remember { mutableDoubleStateOf(95200.00) }
    
    val bullishColor = Color(0xFF4CAF50)
    val bearishColor = Color(0xFFF44336)
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = symbol.replace("USDT", "/USDT"),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "$${currentPrice.formatPrice()}",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "${if (priceChange24h >= 0) "+" else ""}${priceChange24h.formatPercent()}%",
                                style = MaterialTheme.typography.bodySmall,
                                color = if (priceChange24h >= 0) bullishColor else bearishColor
                            )
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showIndicatorsDialog = true }) {
                        Icon(Icons.Outlined.Analytics, contentDescription = "Indicators")
                    }
                    IconButton(onClick = { /* Full screen */ }) {
                        Icon(Icons.Outlined.Fullscreen, contentDescription = "Full screen")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Price stats bar
            PriceStatsBar(
                high24h = high24h,
                low24h = low24h,
                bullishColor = bullishColor,
                bearishColor = bearishColor
            )
            
            // Timeframe selector
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 8.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                ChartTimeframe.entries.forEach { timeframe ->
                    TimeframeChip(
                        timeframe = timeframe,
                        isSelected = selectedTimeframe == timeframe,
                        onClick = { selectedTimeframe = timeframe }
                    )
                }
            }
            
            // Active indicators
            if (enabledIndicators.isNotEmpty()) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    enabledIndicators.forEach { indicator ->
                        AssistChip(
                            onClick = {
                                enabledIndicators = enabledIndicators - indicator
                            },
                            label = { Text(indicator.label, style = MaterialTheme.typography.labelSmall) },
                            trailingIcon = {
                                Icon(
                                    Icons.Default.Close,
                                    contentDescription = "Remove",
                                    modifier = Modifier.size(14.dp)
                                )
                            }
                        )
                    }
                }
            }
            
            // TradingView Chart WebView
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) {
                TradingViewChart(
                    symbol = symbol,
                    interval = selectedTimeframe.interval,
                    modifier = Modifier.fillMaxSize()
                )
            }
            
            // Quick trade buttons
            QuickTradeBar(
                symbol = symbol,
                onLong = { /* Open long dialog */ },
                onShort = { /* Open short dialog */ }
            )
        }
        
        // Indicators dialog
        if (showIndicatorsDialog) {
            IndicatorsDialog(
                enabledIndicators = enabledIndicators,
                onDismiss = { showIndicatorsDialog = false },
                onToggle = { indicator ->
                    enabledIndicators = if (indicator in enabledIndicators) {
                        enabledIndicators - indicator
                    } else {
                        enabledIndicators + indicator
                    }
                }
            )
        }
    }
}

@Composable
private fun PriceStatsBar(
    high24h: Double,
    low24h: Double,
    bullishColor: Color,
    bearishColor: Color
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        StatColumn(
            label = "24h High",
            value = "$${high24h.formatPrice()}",
            color = bullishColor
        )
        StatColumn(
            label = "24h Low",
            value = "$${low24h.formatPrice()}",
            color = bearishColor
        )
        StatColumn(
            label = "24h Vol",
            value = "1.2B",
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}

@Composable
private fun StatColumn(
    label: String,
    value: String,
    color: Color
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = color
        )
    }
}

@Composable
private fun TimeframeChip(
    timeframe: ChartTimeframe,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onClick),
        color = if (isSelected) {
            MaterialTheme.colorScheme.primary
        } else {
            MaterialTheme.colorScheme.surfaceVariant
        },
        contentColor = if (isSelected) {
            MaterialTheme.colorScheme.onPrimary
        } else {
            MaterialTheme.colorScheme.onSurfaceVariant
        }
    ) {
        Text(
            text = timeframe.label,
            style = MaterialTheme.typography.labelMedium,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
        )
    }
}

@Composable
private fun TradingViewChart(
    symbol: String,
    interval: String,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    
    val tradingViewHtml = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
            <style>
                body { margin: 0; padding: 0; background: #1E1E1E; }
                #chart { width: 100%; height: 100vh; }
            </style>
        </head>
        <body>
            <div id="chart"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
                new TradingView.widget({
                    "autosize": true,
                    "symbol": "BYBIT:${symbol}",
                    "interval": "$interval",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "#1E1E1E",
                    "enable_publishing": false,
                    "hide_side_toolbar": false,
                    "allow_symbol_change": true,
                    "container_id": "chart",
                    "studies": ["MASimple@tv-basicstudies", "Volume@tv-basicstudies"]
                });
            </script>
        </body>
        </html>
    """.trimIndent()
    
    AndroidView(
        factory = { ctx ->
            WebView(ctx).apply {
                webViewClient = WebViewClient()
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.loadWithOverviewMode = true
                settings.useWideViewPort = true
                loadDataWithBaseURL(
                    "https://www.tradingview.com",
                    tradingViewHtml,
                    "text/html",
                    "UTF-8",
                    null
                )
            }
        },
        modifier = modifier
    )
}

@Composable
private fun QuickTradeBar(
    symbol: String,
    onLong: () -> Unit,
    onShort: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Button(
            onClick = onLong,
            modifier = Modifier.weight(1f),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF4CAF50)
            )
        ) {
            Icon(Icons.Default.TrendingUp, null, Modifier.size(18.dp))
            Spacer(Modifier.width(8.dp))
            Text("Long")
        }
        Button(
            onClick = onShort,
            modifier = Modifier.weight(1f),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFFF44336)
            )
        ) {
            Icon(Icons.Default.TrendingDown, null, Modifier.size(18.dp))
            Spacer(Modifier.width(8.dp))
            Text("Short")
        }
    }
}

@Composable
private fun IndicatorsDialog(
    enabledIndicators: Set<ChartIndicator>,
    onDismiss: () -> Unit,
    onToggle: (ChartIndicator) -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Technical Indicators") },
        text = {
            Column {
                ChartIndicator.entries.forEach { indicator ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onToggle(indicator) }
                            .padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(indicator.label)
                        Checkbox(
                            checked = indicator in enabledIndicators,
                            onCheckedChange = { onToggle(indicator) }
                        )
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Done")
            }
        }
    )
}

// Extensions
private fun Double.formatPrice(): String = DecimalFormat("#,##0.00").format(this)
private fun Double.formatPercent(): String = DecimalFormat("0.00").format(this)
