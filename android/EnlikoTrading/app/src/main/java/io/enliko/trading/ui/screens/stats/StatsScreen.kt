package io.enliko.trading.ui.screens.stats

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.TrendingUp
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.pulltorefresh.PullToRefreshContainer
import androidx.compose.material3.pulltorefresh.rememberPullToRefreshState
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*

/**
 * StatsScreen - Matching iOS StatsView.swift
 * Trading statistics dashboard with PnL, win rate, and performance metrics
 */

data class DashboardStats(
    val totalPnl: Double = 0.0,
    val todayPnl: Double = 0.0,
    val weekPnl: Double = 0.0,
    val monthPnl: Double = 0.0,
    val totalTrades: Int = 0,
    val winRate: Double = 0.0,
    val avgProfit: Double = 0.0,
    val avgLoss: Double = 0.0,
    val bestTrade: Double = 0.0,
    val worstTrade: Double = 0.0,
    val profitFactor: Double = 0.0,
    val avgHoldingTime: String = "0h"
)

enum class StatsPeriod(val label: String) {
    TODAY("Today"),
    WEEK("Week"),
    MONTH("Month"),
    THREE_MONTHS("3M"),
    YEAR("Year"),
    ALL("All Time")
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatsScreen(
    onBack: () -> Unit
) {
    var selectedPeriod by remember { mutableStateOf(StatsPeriod.WEEK) }
    var isLoading by remember { mutableStateOf(false) }
    
    val pullToRefreshState = rememberPullToRefreshState()
    
    // Mock dashboard data - in real app fetch from API
    val dashboard by remember {
        mutableStateOf(
            DashboardStats(
                totalPnl = 12543.67,
                todayPnl = 234.56,
                weekPnl = 1234.56,
                monthPnl = 4567.89,
                totalTrades = 156,
                winRate = 62.5,
                avgProfit = 145.32,
                avgLoss = -87.45,
                bestTrade = 2345.67,
                worstTrade = -567.89,
                profitFactor = 2.34,
                avgHoldingTime = "4h 23m"
            )
        )
    }
    
    // Handle refresh
    LaunchedEffect(pullToRefreshState.isRefreshing) {
        if (pullToRefreshState.isRefreshing) {
            isLoading = true
            kotlinx.coroutines.delay(1000)
            isLoading = false
            pullToRefreshState.endRefresh()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Trading Statistics") },
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
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .nestedScroll(pullToRefreshState.nestedScrollConnection)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Period Picker
                PeriodPicker(
                    selectedPeriod = selectedPeriod,
                    onPeriodSelected = { selectedPeriod = it }
                )
                
                // Loading indicator
                if (isLoading) {
                    LinearProgressIndicator(
                        modifier = Modifier.fillMaxWidth(),
                        color = EnlikoPrimary
                    )
                }
                
                // PnL Summary Cards
                PnlSummarySection(dashboard = dashboard)
                
                // Trading Stats
                TradingStatsSection(dashboard = dashboard)
                
                // Best/Worst Trades
                BestWorstTradesSection(dashboard = dashboard)
                
                // Additional Metrics
                AdditionalMetricsSection(dashboard = dashboard)
                
                Spacer(modifier = Modifier.height(32.dp))
            }
            
            PullToRefreshContainer(
                state = pullToRefreshState,
                modifier = Modifier.align(Alignment.TopCenter),
                containerColor = EnlikoCard,
                contentColor = EnlikoPrimary
            )
        }
    }
}

@Composable
private fun PeriodPicker(
    selectedPeriod: StatsPeriod,
    onPeriodSelected: (StatsPeriod) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        StatsPeriod.entries.forEach { period ->
            FilterChip(
                selected = selectedPeriod == period,
                onClick = { onPeriodSelected(period) },
                label = { 
                    Text(
                        period.label,
                        fontWeight = if (selectedPeriod == period) FontWeight.SemiBold else FontWeight.Normal
                    )
                },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = EnlikoPrimary,
                    selectedLabelColor = Color.White
                )
            )
        }
    }
}

@Composable
private fun PnlSummarySection(dashboard: DashboardStats) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = "PnL Summary",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = EnlikoTextPrimary
        )
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            StatCard(
                title = "Total PnL",
                value = formatCurrency(dashboard.totalPnl),
                valueColor = if (dashboard.totalPnl >= 0) EnlikoGreen else EnlikoRed,
                modifier = Modifier.weight(1f)
            )
            StatCard(
                title = "Today",
                value = formatCurrency(dashboard.todayPnl),
                valueColor = if (dashboard.todayPnl >= 0) EnlikoGreen else EnlikoRed,
                modifier = Modifier.weight(1f)
            )
        }
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            StatCard(
                title = "Week",
                value = formatCurrency(dashboard.weekPnl),
                valueColor = if (dashboard.weekPnl >= 0) EnlikoGreen else EnlikoRed,
                modifier = Modifier.weight(1f)
            )
            StatCard(
                title = "Month",
                value = formatCurrency(dashboard.monthPnl),
                valueColor = if (dashboard.monthPnl >= 0) EnlikoGreen else EnlikoRed,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun TradingStatsSection(dashboard: DashboardStats) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = "Trading Stats",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = EnlikoTextPrimary
        )
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            StatCard(
                title = "Total Trades",
                value = "${dashboard.totalTrades}",
                modifier = Modifier.weight(1f)
            )
            StatCard(
                title = "Win Rate",
                value = "${String.format("%.1f", dashboard.winRate)}%",
                valueColor = if (dashboard.winRate >= 50) EnlikoGreen else EnlikoRed,
                modifier = Modifier.weight(1f)
            )
        }
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            StatCard(
                title = "Avg Profit",
                value = formatCurrency(dashboard.avgProfit),
                valueColor = EnlikoGreen,
                modifier = Modifier.weight(1f)
            )
            StatCard(
                title = "Avg Loss",
                value = formatCurrency(dashboard.avgLoss),
                valueColor = EnlikoRed,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun BestWorstTradesSection(dashboard: DashboardStats) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = "Best & Worst",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = EnlikoTextPrimary
        )
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            StatCard(
                title = "Best Trade",
                value = formatCurrency(dashboard.bestTrade),
                valueColor = EnlikoGreen,
                icon = Icons.Default.TrendingUp,
                modifier = Modifier.weight(1f)
            )
            StatCard(
                title = "Worst Trade",
                value = formatCurrency(dashboard.worstTrade),
                valueColor = EnlikoRed,
                icon = Icons.Default.TrendingDown,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun AdditionalMetricsSection(dashboard: DashboardStats) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = "Additional Metrics",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = EnlikoTextPrimary
        )
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            StatCard(
                title = "Profit Factor",
                value = String.format("%.2f", dashboard.profitFactor),
                valueColor = if (dashboard.profitFactor >= 1) EnlikoGreen else EnlikoRed,
                modifier = Modifier.weight(1f)
            )
            StatCard(
                title = "Avg Hold Time",
                value = dashboard.avgHoldingTime,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun StatCard(
    title: String,
    value: String,
    valueColor: Color = EnlikoTextPrimary,
    icon: androidx.compose.ui.graphics.vector.ImageVector? = null,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelMedium,
                    color = EnlikoTextSecondary
                )
                icon?.let {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        tint = valueColor,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
            
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = valueColor
            )
        }
    }
}

private fun formatCurrency(value: Double): String {
    val absValue = kotlin.math.abs(value)
    val sign = if (value >= 0) "+" else "-"
    return "$sign$${String.format("%.2f", absValue)}"
}
