package io.enliko.trading.ui.screens.stats

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import kotlinx.coroutines.delay
import kotlin.random.Random

// MARK: - Data Models
data class TradingStats(
    val totalTrades: Int,
    val winningTrades: Int,
    val losingTrades: Int,
    val winRate: Double,
    val totalPnL: Double,
    val totalPnLPercent: Double,
    val avgWin: Double,
    val avgLoss: Double,
    val largestWin: Double,
    val largestLoss: Double,
    val profitFactor: Double,
    val sharpeRatio: Double,
    val maxDrawdown: Double,
    val avgHoldTime: String,
    val bestDay: Double,
    val worstDay: Double
)

data class StrategyStats(
    val name: String,
    val trades: Int,
    val pnl: Double,
    val winRate: Double
)

data class SymbolStats(
    val symbol: String,
    val trades: Int,
    val pnl: Double,
    val winRate: Double
)

data class DailyPnL(
    val date: String,
    val pnl: Double
)

enum class StatsPeriod(val label: String, val days: Int) {
    TODAY("Today", 1),
    WEEK("7D", 7),
    MONTH("30D", 30),
    THREE_MONTHS("90D", 90),
    YEAR("1Y", 365),
    ALL("All", 0)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatsScreen(
    onNavigateBack: () -> Unit = {}
) {
    var selectedPeriod by remember { mutableStateOf(StatsPeriod.MONTH) }
    var stats by remember { mutableStateOf<TradingStats?>(null) }
    var strategyStats by remember { mutableStateOf(listOf<StrategyStats>()) }
    var symbolStats by remember { mutableStateOf(listOf<SymbolStats>()) }
    var dailyPnL by remember { mutableStateOf(listOf<DailyPnL>()) }
    var isLoading by remember { mutableStateOf(true) }
    
    // Load mock data
    LaunchedEffect(selectedPeriod) {
        isLoading = true
        delay(500)
        stats = generateMockStats(selectedPeriod)
        strategyStats = generateMockStrategyStats()
        symbolStats = generateMockSymbolStats()
        dailyPnL = generateMockDailyPnL(selectedPeriod.days)
        isLoading = false
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text("Trading Statistics", fontWeight = FontWeight.Bold) 
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { /* Export stats */ }) {
                        Icon(Icons.Default.Share, contentDescription = "Export")
                    }
                }
            )
        }
    ) { padding ->
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Period Selector
                item {
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(StatsPeriod.entries) { period ->
                            FilterChip(
                                selected = period == selectedPeriod,
                                onClick = { selectedPeriod = period },
                                label = { Text(period.label) }
                            )
                        }
                    }
                }
                
                // Main Stats Cards
                stats?.let { s ->
                    item {
                        MainStatsCard(stats = s)
                    }
                    
                    // PnL Chart
                    item {
                        PnLChartCard(dailyPnL = dailyPnL)
                    }
                    
                    // Performance Metrics
                    item {
                        PerformanceMetricsCard(stats = s)
                    }
                    
                    // Win/Loss Distribution
                    item {
                        WinLossDistributionCard(stats = s)
                    }
                }
                
                // Strategy Breakdown
                item {
                    StrategyBreakdownCard(strategies = strategyStats)
                }
                
                // Top Symbols
                item {
                    TopSymbolsCard(symbols = symbolStats)
                }
            }
        }
    }
}

@Composable
private fun MainStatsCard(stats: TradingStats) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Total PnL
            Text(
                text = "Total PnL",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Row(
                verticalAlignment = Alignment.Bottom,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "${if (stats.totalPnL >= 0) "+" else ""}$${String.format("%.2f", stats.totalPnL)}",
                    style = MaterialTheme.typography.headlineLarge,
                    fontWeight = FontWeight.Bold,
                    color = if (stats.totalPnL >= 0) LongGreen else ShortRed
                )
                Text(
                    text = "${if (stats.totalPnLPercent >= 0) "+" else ""}${String.format("%.1f", stats.totalPnLPercent)}%",
                    style = MaterialTheme.typography.titleMedium,
                    color = if (stats.totalPnLPercent >= 0) LongGreen else ShortRed
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Quick Stats Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                QuickStatItem(
                    label = "Trades",
                    value = stats.totalTrades.toString(),
                    icon = Icons.Default.SwapHoriz
                )
                QuickStatItem(
                    label = "Win Rate",
                    value = "${String.format("%.1f", stats.winRate)}%",
                    icon = Icons.Default.TrendingUp,
                    valueColor = if (stats.winRate >= 50) LongGreen else ShortRed
                )
                QuickStatItem(
                    label = "Avg Win",
                    value = "$${String.format("%.0f", stats.avgWin)}",
                    icon = Icons.Default.ArrowUpward,
                    valueColor = LongGreen
                )
                QuickStatItem(
                    label = "Avg Loss",
                    value = "$${String.format("%.0f", stats.avgLoss)}",
                    icon = Icons.Default.ArrowDownward,
                    valueColor = ShortRed
                )
            }
        }
    }
}

@Composable
private fun QuickStatItem(
    label: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(
            icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = valueColor
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun PnLChartCard(dailyPnL: List<DailyPnL>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "PnL Chart",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            if (dailyPnL.isNotEmpty()) {
                PnLChart(
                    data = dailyPnL,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(150.dp)
                )
            }
        }
    }
}

@Composable
private fun PnLChart(
    data: List<DailyPnL>,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        if (data.isEmpty()) return@Canvas
        
        val width = size.width
        val height = size.height
        val maxPnL = data.maxOfOrNull { it.pnl } ?: 0.0
        val minPnL = data.minOfOrNull { it.pnl } ?: 0.0
        val range = maxOf(maxPnL - minPnL, 1.0)
        
        val zeroY = height * (maxPnL / range)
        
        // Draw zero line
        drawLine(
            color = Color.Gray.copy(alpha = 0.3f),
            start = Offset(0f, zeroY.toFloat()),
            end = Offset(width, zeroY.toFloat()),
            strokeWidth = 1f
        )
        
        // Draw cumulative PnL line
        val path = Path()
        var cumulativePnL = 0.0
        
        data.forEachIndexed { index, day ->
            cumulativePnL += day.pnl
            val x = index * width / (data.size - 1).coerceAtLeast(1)
            val y = height - ((cumulativePnL - minPnL) / range * height).toFloat()
            
            if (index == 0) {
                path.moveTo(x, y)
            } else {
                path.lineTo(x, y)
            }
        }
        
        val finalColor = if (cumulativePnL >= 0) LongGreen else ShortRed
        drawPath(
            path = path,
            color = finalColor,
            style = Stroke(width = 3f, cap = StrokeCap.Round)
        )
    }
}

@Composable
private fun PerformanceMetricsCard(stats: TradingStats) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Performance Metrics",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    MetricRow("Profit Factor", String.format("%.2f", stats.profitFactor))
                    MetricRow("Sharpe Ratio", String.format("%.2f", stats.sharpeRatio))
                    MetricRow("Max Drawdown", "${String.format("%.1f", stats.maxDrawdown)}%")
                }
                Column(modifier = Modifier.weight(1f)) {
                    MetricRow("Best Day", "+$${String.format("%.0f", stats.bestDay)}", LongGreen)
                    MetricRow("Worst Day", "-$${String.format("%.0f", kotlin.math.abs(stats.worstDay))}", ShortRed)
                    MetricRow("Avg Hold Time", stats.avgHoldTime)
                }
            }
        }
    }
}

@Composable
private fun MetricRow(
    label: String,
    value: String,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = valueColor
        )
    }
}

@Composable
private fun WinLossDistributionCard(stats: TradingStats) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Win/Loss Distribution",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Bar visualization
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(24.dp)
                    .clip(RoundedCornerShape(12.dp))
            ) {
                val winRatio = stats.winningTrades.toFloat() / stats.totalTrades.coerceAtLeast(1)
                
                Box(
                    modifier = Modifier
                        .weight(winRatio.coerceAtLeast(0.01f))
                        .fillMaxHeight()
                        .background(LongGreen)
                )
                Box(
                    modifier = Modifier
                        .weight((1f - winRatio).coerceAtLeast(0.01f))
                        .fillMaxHeight()
                        .background(ShortRed)
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .background(LongGreen, RoundedCornerShape(2.dp))
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "${stats.winningTrades} Wins",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .background(ShortRed, RoundedCornerShape(2.dp))
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "${stats.losingTrades} Losses",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("Largest Win", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("+$${String.format("%.0f", stats.largestWin)}", fontWeight = FontWeight.Bold, color = LongGreen)
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text("Largest Loss", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("-$${String.format("%.0f", kotlin.math.abs(stats.largestLoss))}", fontWeight = FontWeight.Bold, color = ShortRed)
                }
            }
        }
    }
}

@Composable
private fun StrategyBreakdownCard(strategies: List<StrategyStats>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Strategy Breakdown",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            strategies.forEach { strategy ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = strategy.name,
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "${strategy.trades} trades",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                text = "${if (strategy.pnl >= 0) "+" else ""}$${String.format("%.0f", strategy.pnl)}",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold,
                                color = if (strategy.pnl >= 0) LongGreen else ShortRed
                            )
                            Text(
                                text = "${String.format("%.0f", strategy.winRate)}% WR",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
                if (strategies.last() != strategy) {
                    HorizontalDivider()
                }
            }
        }
    }
}

@Composable
private fun TopSymbolsCard(symbols: List<SymbolStats>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Top Symbols",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            symbols.take(5).forEach { symbol ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = symbol.symbol,
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "${if (symbol.pnl >= 0) "+" else ""}$${String.format("%.0f", symbol.pnl)}",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (symbol.pnl >= 0) LongGreen else ShortRed
                    )
                }
                if (symbols.indexOf(symbol) < 4) {
                    HorizontalDivider()
                }
            }
        }
    }
}

// Mock data generators
private fun generateMockStats(period: StatsPeriod): TradingStats {
    val baseTrades = when (period) {
        StatsPeriod.TODAY -> 5
        StatsPeriod.WEEK -> 35
        StatsPeriod.MONTH -> 156
        StatsPeriod.THREE_MONTHS -> 450
        StatsPeriod.YEAR -> 1800
        StatsPeriod.ALL -> 2500
    }
    
    val winRate = Random.nextDouble(55.0, 75.0)
    val winningTrades = (baseTrades * winRate / 100).toInt()
    
    return TradingStats(
        totalTrades = baseTrades,
        winningTrades = winningTrades,
        losingTrades = baseTrades - winningTrades,
        winRate = winRate,
        totalPnL = Random.nextDouble(1000.0, 15000.0),
        totalPnLPercent = Random.nextDouble(5.0, 45.0),
        avgWin = Random.nextDouble(80.0, 250.0),
        avgLoss = Random.nextDouble(40.0, 120.0),
        largestWin = Random.nextDouble(500.0, 2500.0),
        largestLoss = Random.nextDouble(-1500.0, -300.0),
        profitFactor = Random.nextDouble(1.2, 2.8),
        sharpeRatio = Random.nextDouble(0.8, 2.5),
        maxDrawdown = Random.nextDouble(5.0, 20.0),
        avgHoldTime = "${Random.nextInt(1, 48)}h ${Random.nextInt(0, 59)}m",
        bestDay = Random.nextDouble(500.0, 2000.0),
        worstDay = Random.nextDouble(-1000.0, -200.0)
    )
}

private fun generateMockStrategyStats(): List<StrategyStats> {
    return listOf(
        StrategyStats("OI Strategy", Random.nextInt(50, 150), Random.nextDouble(1000.0, 5000.0), Random.nextDouble(55.0, 75.0)),
        StrategyStats("Scalper", Random.nextInt(100, 300), Random.nextDouble(500.0, 3000.0), Random.nextDouble(60.0, 80.0)),
        StrategyStats("Fibonacci", Random.nextInt(30, 80), Random.nextDouble(800.0, 2500.0), Random.nextDouble(50.0, 70.0)),
        StrategyStats("RSI_BB", Random.nextInt(40, 100), Random.nextDouble(-500.0, 2000.0), Random.nextDouble(45.0, 65.0)),
        StrategyStats("Manual", Random.nextInt(20, 60), Random.nextDouble(200.0, 1500.0), Random.nextDouble(50.0, 70.0))
    )
}

private fun generateMockSymbolStats(): List<SymbolStats> {
    return listOf(
        SymbolStats("BTCUSDT", Random.nextInt(50, 200), Random.nextDouble(2000.0, 8000.0), Random.nextDouble(55.0, 75.0)),
        SymbolStats("ETHUSDT", Random.nextInt(40, 150), Random.nextDouble(1000.0, 5000.0), Random.nextDouble(55.0, 70.0)),
        SymbolStats("SOLUSDT", Random.nextInt(30, 100), Random.nextDouble(500.0, 3000.0), Random.nextDouble(50.0, 70.0)),
        SymbolStats("XRPUSDT", Random.nextInt(20, 80), Random.nextDouble(-200.0, 2000.0), Random.nextDouble(45.0, 65.0)),
        SymbolStats("DOGEUSDT", Random.nextInt(10, 50), Random.nextDouble(-500.0, 1000.0), Random.nextDouble(40.0, 60.0))
    )
}

private fun generateMockDailyPnL(days: Int): List<DailyPnL> {
    val actualDays = if (days == 0) 365 else days.coerceAtMost(90)
    return (0 until actualDays).map { i ->
        DailyPnL(
            date = "Day ${actualDays - i}",
            pnl = Random.nextDouble(-200.0, 300.0)
        )
    }
}
