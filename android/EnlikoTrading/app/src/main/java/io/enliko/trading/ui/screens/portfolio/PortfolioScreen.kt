package io.enliko.trading.ui.screens.portfolio

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.data.models.*
import io.enliko.trading.ui.components.AccountTypeSelector
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import io.enliko.trading.util.LocalStrings
import java.text.NumberFormat
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PortfolioScreen(
    viewModel: PortfolioViewModel = hiltViewModel()
) {
    val strings = LocalStrings.current
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(strings.portfolio) },
                actions = {
                    IconButton(onClick = { viewModel.refresh() }) {
                        Icon(Icons.Default.Refresh, contentDescription = strings.refresh)
                    }
                }
            )
        }
    ) { padding ->
        if (uiState.isLoading && uiState.balance == null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                // Account Type Selector
                Box(modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)) {
                    AccountTypeSelector(
                        exchange = uiState.exchange,
                        selectedAccountType = uiState.accountType,
                        onAccountTypeSelected = { viewModel.switchAccountType(it) }
                    )
                }
                
                // Tab Selector
                PortfolioTabSelector(
                    selectedTab = uiState.selectedTab,
                    onTabSelected = { viewModel.selectTab(it) }
                )
                
                // Period Filter
                PeriodFilterRow(
                    selectedPeriod = uiState.selectedPeriod,
                    onPeriodSelected = { viewModel.selectPeriod(it) }
                )
                
                // Content based on tab
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    when (uiState.selectedTab) {
                        PortfolioTab.OVERVIEW -> {
                            // Total Balance Card
                            item {
                                TotalBalanceCard(
                                    summary = uiState.portfolioSummary,
                                    balance = uiState.balance,
                                    strings = strings
                                )
                            }
                            
                            // PnL Chart
                            item {
                                PnLChartCard(
                                    candles = uiState.candles,
                                    period = uiState.selectedPeriod,
                                    onCandleClick = { viewModel.selectCandle(it) }
                                )
                            }
                            
                            // Stats Card
                            item {
                                uiState.stats?.let { stats ->
                                    StatsCard(stats = stats, strings = strings)
                                }
                            }
                            
                            // Positions Header
                            item {
                                PositionsHeader(
                                    positionCount = uiState.positions.size,
                                    strings = strings,
                                    onCloseAll = { viewModel.closeAllPositions() }
                                )
                            }
                            
                            // Positions
                            if (uiState.positions.isEmpty()) {
                                item {
                                    EmptyPositionsCard(strings)
                                }
                            } else {
                                items(uiState.positions, key = { "${it.symbol}_${it.side}" }) { position ->
                                    PositionCard(
                                        position = position,
                                        strings = strings,
                                        onClose = { viewModel.closePosition(position.symbol, position.side) }
                                    )
                                }
                            }
                        }
                        
                        PortfolioTab.SPOT -> {
                            item {
                                SpotBalanceCard(
                                    spotPortfolio = uiState.spotPortfolio,
                                    strings = strings
                                )
                            }
                            
                            // Spot Assets
                            uiState.spotPortfolio?.assets?.let { assets ->
                                if (assets.isEmpty()) {
                                    item {
                                        EmptyCard(text = strings.noSpotAssets)
                                    }
                                } else {
                                    items(assets, key = { it.asset }) { asset ->
                                        AssetCard(asset = asset)
                                    }
                                }
                            }
                        }
                        
                        PortfolioTab.FUTURES -> {
                            item {
                                FuturesBalanceCard(
                                    futuresPortfolio = uiState.futuresPortfolio,
                                    balance = uiState.balance,
                                    strings = strings
                                )
                            }
                            
                            // Positions in futures tab
                            item {
                                PositionsHeader(
                                    positionCount = uiState.positions.size,
                                    strings = strings,
                                    onCloseAll = { viewModel.closeAllPositions() }
                                )
                            }
                            
                            if (uiState.positions.isEmpty()) {
                                item {
                                    EmptyPositionsCard(strings)
                                }
                            } else {
                                items(uiState.positions, key = { "${it.symbol}_${it.side}" }) { position ->
                                    PositionCard(
                                        position = position,
                                        strings = strings,
                                        onClose = { viewModel.closePosition(position.symbol, position.side) }
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Candle Detail Sheet
        if (uiState.showCandleDetail && uiState.selectedCandle != null) {
            CandleClusterSheet(
                candle = uiState.selectedCandle!!,
                onDismiss = { viewModel.dismissCandleDetail() }
            )
        }
        
        // Date Picker Dialog
        if (uiState.showDatePicker) {
            DateRangePickerDialog(
                initialStart = uiState.customStartDate ?: LocalDate.now().minusDays(7),
                initialEnd = uiState.customEndDate ?: LocalDate.now(),
                onConfirm = { start, end -> viewModel.setCustomDateRange(start, end) },
                onDismiss = { viewModel.dismissDatePicker() }
            )
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════
// TAB SELECTOR
// ═══════════════════════════════════════════════════════════════════════

@Composable
private fun PortfolioTabSelector(
    selectedTab: PortfolioTab,
    onTabSelected: (PortfolioTab) -> Unit
) {
    val strings = LocalStrings.current
    
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        PortfolioTab.entries.forEach { tab ->
            val isSelected = tab == selectedTab
            FilterChip(
                selected = isSelected,
                onClick = { onTabSelected(tab) },
                label = {
                    Text(
                        when (tab) {
                            PortfolioTab.OVERVIEW -> strings.portfolioOverview
                            PortfolioTab.SPOT -> strings.portfolioSpot
                            PortfolioTab.FUTURES -> strings.portfolioFutures
                        }
                    )
                },
                modifier = Modifier.weight(1f)
            )
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════
// PERIOD FILTER
// ═══════════════════════════════════════════════════════════════════════

@Composable
private fun PeriodFilterRow(
    selectedPeriod: PeriodFilter,
    onPeriodSelected: (PeriodFilter) -> Unit
) {
    LazyRow(
        modifier = Modifier.fillMaxWidth(),
        contentPadding = PaddingValues(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(PeriodFilter.entries) { period ->
            val isSelected = period == selectedPeriod
            FilterChip(
                selected = isSelected,
                onClick = { onPeriodSelected(period) },
                label = { Text(period.label) },
                leadingIcon = if (period == PeriodFilter.CUSTOM) {
                    { Icon(Icons.Default.DateRange, contentDescription = null, modifier = Modifier.size(18.dp)) }
                } else null
            )
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════
// BALANCE CARDS
// ═══════════════════════════════════════════════════════════════════════

@Composable
private fun TotalBalanceCard(
    summary: PortfolioSummary?,
    balance: Balance?,
    strings: io.enliko.trading.util.Strings
) {
    val formatter = remember { 
        NumberFormat.getCurrencyInstance(Locale.US).apply {
            minimumFractionDigits = 2
            maximumFractionDigits = 2
        }
    }
    
    val totalUsd = summary?.totalUsd ?: balance?.totalEquity ?: 0.0
    val pnlPeriod = summary?.pnlPeriod ?: 0.0
    val pnlPeriodPct = summary?.pnlPeriodPct ?: 0.0
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = strings.totalBalance,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Text(
                text = formatter.format(totalUsd),
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Period PnL
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                val pnlColor = when {
                    pnlPeriod > 0 -> LongGreen
                    pnlPeriod < 0 -> ShortRed
                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                }
                
                Text(
                    text = "${strings.pnl}: ",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Text(
                    text = "${if (pnlPeriod >= 0) "+" else ""}${formatter.format(pnlPeriod)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = pnlColor
                )
                
                Spacer(modifier = Modifier.width(8.dp))
                
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(4.dp))
                        .background(pnlColor.copy(alpha = 0.15f))
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                ) {
                    Text(
                        text = "${if (pnlPeriodPct >= 0) "+" else ""}${String.format("%.2f", pnlPeriodPct)}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = pnlColor,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
            
            // Spot/Futures breakdown
            summary?.let { sum ->
                Spacer(modifier = Modifier.height(16.dp))
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text(
                            text = strings.portfolioSpot,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = formatter.format(sum.spot?.totalUsd ?: 0.0),
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                    
                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = strings.portfolioFutures,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = formatter.format(sum.futures?.totalEquity ?: 0.0),
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SpotBalanceCard(
    spotPortfolio: SpotPortfolio?,
    strings: io.enliko.trading.util.Strings
) {
    val formatter = remember { 
        NumberFormat.getCurrencyInstance(Locale.US).apply {
            minimumFractionDigits = 2
            maximumFractionDigits = 2
        }
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF2196F3).copy(alpha = 0.1f)
        )
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Text(
                text = "💎 ${strings.portfolioSpot}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                text = formatter.format(spotPortfolio?.totalUsd ?: 0.0),
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold
            )
            
            spotPortfolio?.let { spot ->
                val pnlColor = if (spot.pnl >= 0) LongGreen else ShortRed
                Row(
                    modifier = Modifier.padding(top = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "${if (spot.pnl >= 0) "+" else ""}${formatter.format(spot.pnl)}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = pnlColor
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "(${String.format("%.2f", spot.pnlPct)}%)",
                        style = MaterialTheme.typography.bodySmall,
                        color = pnlColor
                    )
                }
                
                Text(
                    text = "${spot.assets.size} ${strings.assets}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
private fun FuturesBalanceCard(
    futuresPortfolio: FuturesPortfolio?,
    balance: Balance?,
    strings: io.enliko.trading.util.Strings
) {
    val formatter = remember { 
        NumberFormat.getCurrencyInstance(Locale.US).apply {
            minimumFractionDigits = 2
            maximumFractionDigits = 2
        }
    }
    
    val equity = futuresPortfolio?.totalEquity ?: balance?.totalEquity ?: 0.0
    val available = futuresPortfolio?.available ?: balance?.availableBalance ?: 0.0
    val margin = futuresPortfolio?.positionMargin ?: balance?.marginUsed ?: 0.0
    val unrealized = futuresPortfolio?.unrealizedPnl ?: balance?.unrealizedPnl ?: 0.0
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFFF9800).copy(alpha = 0.1f)
        )
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Text(
                text = "📈 ${strings.portfolioFutures}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                text = formatter.format(equity),
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(strings.availableBalance, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(formatter.format(available), style = MaterialTheme.typography.bodyMedium)
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(strings.margin, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(formatter.format(margin), style = MaterialTheme.typography.bodyMedium)
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text(strings.unrealizedPnl, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    val pnlColor = if (unrealized >= 0) LongGreen else ShortRed
                    Text(
                        text = "${if (unrealized >= 0) "+" else ""}${formatter.format(unrealized)}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = pnlColor
                    )
                }
            }
            
            futuresPortfolio?.let {
                Text(
                    text = "${it.positionCount} ${strings.openPositions}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = 12.dp)
                )
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════
// PNL CHART
// ═══════════════════════════════════════════════════════════════════════

@Composable
private fun PnLChartCard(
    candles: List<CandleCluster>,
    period: PeriodFilter,
    onCandleClick: (CandleCluster) -> Unit
) {
    val strings = LocalStrings.current
    
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "📊 ${strings.pnlChart}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            if (candles.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = strings.noData,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            } else {
                // Custom candlestick chart
                CandlestickChart(
                    candles = candles,
                    onCandleClick = onCandleClick,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = strings.tapCandleHint,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}

@Composable
private fun CandlestickChart(
    candles: List<CandleCluster>,
    onCandleClick: (CandleCluster) -> Unit,
    modifier: Modifier = Modifier
) {
    if (candles.isEmpty()) return
    
    val maxPnl = candles.maxOfOrNull { maxOf(it.highPnl, it.openPnl, it.closePnl) } ?: 0.0
    val minPnl = candles.minOfOrNull { minOf(it.lowPnl, it.openPnl, it.closePnl) } ?: 0.0
    val range = if (maxPnl == minPnl) 1.0 else maxPnl - minPnl
    
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.Bottom
    ) {
        candles.forEach { candle ->
            val isGreen = candle.closePnl >= candle.openPnl
            val candleColor = if (isGreen) LongGreen else ShortRed
            
            val bodyTop = ((maxPnl - maxOf(candle.openPnl, candle.closePnl)) / range).toFloat()
            val bodyBottom = ((maxPnl - minOf(candle.openPnl, candle.closePnl)) / range).toFloat()
            val wickTop = ((maxPnl - candle.highPnl) / range).toFloat()
            val wickBottom = ((maxPnl - candle.lowPnl) / range).toFloat()
            
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxHeight()
                    .clickable { onCandleClick(candle) }
                    .padding(horizontal = 2.dp),
                contentAlignment = Alignment.TopCenter
            ) {
                // Wick
                Box(
                    modifier = Modifier
                        .fillMaxHeight(wickBottom - wickTop)
                        .offset(y = (wickTop * 200).dp)
                        .width(2.dp)
                        .background(candleColor.copy(alpha = 0.6f))
                )
                
                // Body
                Box(
                    modifier = Modifier
                        .fillMaxHeight(maxOf(bodyBottom - bodyTop, 0.02f))
                        .offset(y = (bodyTop * 200).dp)
                        .fillMaxWidth(0.7f)
                        .clip(RoundedCornerShape(2.dp))
                        .background(candleColor)
                )
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════
// CANDLE CLUSTER DETAIL SHEET
// ═══════════════════════════════════════════════════════════════════════

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun CandleClusterSheet(
    candle: CandleCluster,
    onDismiss: () -> Unit
) {
    val strings = LocalStrings.current
    val formatter = remember { 
        NumberFormat.getCurrencyInstance(Locale.US).apply {
            minimumFractionDigits = 2
            maximumFractionDigits = 2
        }
    }
    
    val dateFormatter = remember { DateTimeFormatter.ofPattern("MMM dd, HH:mm") }
    val candleDate = try {
        Instant.parse(candle.timestamp).atZone(ZoneId.systemDefault()).format(dateFormatter)
    } catch (e: Exception) { candle.timestamp }
    
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    ) {
        LazyColumn(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp),
            contentPadding = PaddingValues(bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "📊 ${strings.clusterAnalysis}",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = candleDate,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            // Summary Card
            item {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                    )
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = strings.clusterSummary,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            ClusterStatItem(
                                label = strings.trades,
                                value = candle.tradeCount.toString()
                            )
                            ClusterStatItem(
                                label = strings.pnl,
                                value = formatter.format(candle.closePnl),
                                color = if (candle.closePnl >= 0) LongGreen else ShortRed
                            )
                            ClusterStatItem(
                                label = strings.winRate,
                                value = "${String.format("%.0f", if (candle.tradeCount > 0) candle.winCount * 100.0 / candle.tradeCount else 0.0)}%"
                            )
                            ClusterStatItem(
                                label = strings.volume,
                                value = formatter.format(candle.volume)
                            )
                        }
                    }
                }
            }
            
            // Direction Breakdown
            item {
                Card {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "📈 ${strings.direction}",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "LONG",
                                    style = MaterialTheme.typography.labelMedium,
                                    color = LongGreen,
                                    fontWeight = FontWeight.Bold
                                )
                                Text("${candle.longCount} trades", style = MaterialTheme.typography.bodySmall)
                                Text(
                                    text = formatter.format(candle.longPnl),
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = if (candle.longPnl >= 0) LongGreen else ShortRed
                                )
                            }
                            
                            HorizontalDivider(modifier = Modifier.width(1.dp).height(60.dp))
                            
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "SHORT",
                                    style = MaterialTheme.typography.labelMedium,
                                    color = ShortRed,
                                    fontWeight = FontWeight.Bold
                                )
                                Text("${candle.shortCount} trades", style = MaterialTheme.typography.bodySmall)
                                Text(
                                    text = formatter.format(candle.shortPnl),
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = if (candle.shortPnl >= 0) LongGreen else ShortRed
                                )
                            }
                        }
                    }
                }
            }
            
            // Strategy Breakdown
            if (candle.strategies.isNotEmpty()) {
                item {
                    Card {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(
                                text = "🎯 ${strings.strategies}",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            
                            Spacer(modifier = Modifier.height(12.dp))
                            
                            candle.strategies.forEach { (strategy, cluster) ->
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 4.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(strategy.uppercase(), style = MaterialTheme.typography.bodyMedium)
                                    Row {
                                        Text("${cluster.count}", style = MaterialTheme.typography.bodySmall)
                                        Spacer(modifier = Modifier.width(12.dp))
                                        Text(
                                            text = formatter.format(cluster.pnl),
                                            style = MaterialTheme.typography.bodyMedium,
                                            color = if (cluster.pnl >= 0) LongGreen else ShortRed
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Symbol Breakdown
            if (candle.symbols.isNotEmpty()) {
                item {
                    Card {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(
                                text = "💰 ${strings.symbols}",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            
                            Spacer(modifier = Modifier.height(12.dp))
                            
                            candle.symbols.entries.take(10).forEach { (symbol, cluster) ->
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 4.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(symbol.removeSuffix("USDT"), style = MaterialTheme.typography.bodyMedium)
                                    Row {
                                        Text("${cluster.count}", style = MaterialTheme.typography.bodySmall)
                                        Spacer(modifier = Modifier.width(12.dp))
                                        Text(
                                            text = formatter.format(cluster.pnl),
                                            style = MaterialTheme.typography.bodyMedium,
                                            color = if (cluster.pnl >= 0) LongGreen else ShortRed
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Trades List
            if (candle.trades.isNotEmpty()) {
                item {
                    Text(
                        text = "📋 ${strings.allTrades} (${candle.trades.size})",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                }
                
                items(candle.trades.take(20)) { trade ->
                    TradeRow(trade = trade, formatter = formatter)
                }
            }
        }
    }
}

@Composable
private fun ClusterStatItem(
    label: String,
    value: String,
    color: Color? = null
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = color ?: MaterialTheme.colorScheme.onSurface
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun TradeRow(
    trade: ClusterTrade,
    formatter: NumberFormat
) {
    val isLong = trade.side.equals("Buy", ignoreCase = true) || trade.side.equals("Long", ignoreCase = true)
    val sideColor = if (isLong) LongGreen else ShortRed
    
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(4.dp))
                    .background(sideColor.copy(alpha = 0.15f))
                    .padding(horizontal = 6.dp, vertical = 2.dp)
            ) {
                Text(
                    text = if (isLong) "L" else "S",
                    style = MaterialTheme.typography.labelSmall,
                    color = sideColor,
                    fontWeight = FontWeight.Bold
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = trade.symbol.removeSuffix("USDT"),
                style = MaterialTheme.typography.bodyMedium
            )
        }
        
        Text(
            text = "${if (trade.pnl >= 0) "+" else ""}${formatter.format(trade.pnl)} (${String.format("%.2f", trade.pnlPct)}%)",
            style = MaterialTheme.typography.bodyMedium,
            color = if (trade.pnl >= 0) LongGreen else ShortRed
        )
    }
}

// ═══════════════════════════════════════════════════════════════════════
// EXISTING COMPONENTS (Updated)
// ═══════════════════════════════════════════════════════════════════════

@Composable
private fun StatsCard(stats: TradeStats, strings: io.enliko.trading.util.Strings) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            StatItem(strings.totalTrades, stats.total.toString())
            StatItem(strings.winRate, "${String.format("%.1f", stats.winrate)}%")
            StatItem(strings.wins, stats.wins.toString(), LongGreen)
            StatItem(strings.losses, stats.losses.toString(), ShortRed)
        }
    }
}

@Composable
private fun StatItem(label: String, value: String, color: Color? = null) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = color ?: MaterialTheme.colorScheme.onSurface
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun PositionsHeader(
    positionCount: Int,
    strings: io.enliko.trading.util.Strings,
    onCloseAll: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "${strings.openPositions} ($positionCount)",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        
        if (positionCount > 0) {
            TextButton(onClick = onCloseAll) {
                Text(strings.closeAll, color = ShortRed)
            }
        }
    }
}

@Composable
private fun EmptyPositionsCard(strings: io.enliko.trading.util.Strings) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = strings.noPositions,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun EmptyCard(text: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(text = text, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun AssetCard(asset: AssetBalance) {
    val formatter = remember { 
        NumberFormat.getCurrencyInstance(Locale.US).apply {
            minimumFractionDigits = 2
            maximumFractionDigits = 2
        }
    }
    
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = asset.asset,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = String.format("%.8f", asset.total),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = formatter.format(asset.usdValue),
                    style = MaterialTheme.typography.titleMedium
                )
                if (asset.pnl24h != 0.0) {
                    val pnlColor = if (asset.pnl24h >= 0) LongGreen else ShortRed
                    Text(
                        text = "${if (asset.pnl24h >= 0) "+" else ""}${String.format("%.2f", asset.pnl24hPct)}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = pnlColor
                    )
                }
            }
        }
    }
}

@Composable
private fun PositionCard(
    position: Position,
    strings: io.enliko.trading.util.Strings,
    onClose: () -> Unit
) {
    val isLong = position.side.equals("Buy", ignoreCase = true) || 
                 position.side.equals("Long", ignoreCase = true)
    val sideColor by animateColorAsState(if (isLong) LongGreen else ShortRed, label = "sideColor")
    
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(4.dp))
                            .background(sideColor.copy(alpha = 0.2f))
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = if (isLong) strings.long else strings.short,
                            style = MaterialTheme.typography.labelMedium,
                            color = sideColor,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    
                    Spacer(modifier = Modifier.width(12.dp))
                    
                    Text(
                        text = position.symbol.removeSuffix("USDT"),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    position.leverage?.let { leverage ->
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "${leverage.toInt()}x",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                IconButton(
                    onClick = onClose,
                    colors = IconButtonDefaults.iconButtonColors(contentColor = ShortRed)
                ) {
                    Icon(Icons.Default.Close, contentDescription = strings.close)
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(strings.entry, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(String.format("%.4f", position.entryPrice), style = MaterialTheme.typography.bodyMedium)
                }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(strings.size, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(String.format("%.4f", position.size), style = MaterialTheme.typography.bodyMedium)
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(strings.pnl, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    val pnl = position.unrealizedPnl ?: 0.0
                    val pnlPct = position.pnlPercent ?: 0.0
                    val pnlColor = when {
                        pnl > 0 -> LongGreen
                        pnl < 0 -> ShortRed
                        else -> MaterialTheme.colorScheme.onSurface
                    }
                    Text(
                        text = "${if (pnl >= 0) "+" else ""}${String.format("%.2f", pnl)} (${String.format("%.2f", pnlPct)}%)",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium,
                        color = pnlColor
                    )
                }
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════
// DATE RANGE PICKER
// ═══════════════════════════════════════════════════════════════════════

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DateRangePickerDialog(
    initialStart: LocalDate,
    initialEnd: LocalDate,
    onConfirm: (LocalDate, LocalDate) -> Unit,
    onDismiss: () -> Unit
) {
    var startDate by remember { mutableStateOf(initialStart) }
    var endDate by remember { mutableStateOf(initialEnd) }
    val strings = LocalStrings.current
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(strings.customPeriod) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text("${strings.from}: ${startDate}")
                Text("${strings.to}: ${endDate}")
                // Note: In production, use proper date pickers
            }
        },
        confirmButton = {
            TextButton(onClick = { onConfirm(startDate, endDate) }) {
                Text(strings.apply)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(strings.cancel)
            }
        }
    )
}
