package io.enliko.trading.ui.screens.strategies

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.Localization
import kotlinx.coroutines.launch

/**
 * StrategiesScreen - Matching iOS StrategiesView.swift
 * Features: My Strategies, Marketplace, Backtest tabs
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StrategiesScreen(
    onBack: () -> Unit,
    onNavigateToStrategySettings: (String) -> Unit,
    onNavigateToBacktest: () -> Unit,
    viewModel: StrategiesViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val pagerState = rememberPagerState(pageCount = { 3 })
    val coroutineScope = rememberCoroutineScope()
    
    val tabs = listOf(
        Localization.get("my_strategies"),
        Localization.get("marketplace"),
        Localization.get("backtest")
    )
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(Localization.get("strategies")) },
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
        ) {
            // Tab Selector
            TabRow(
                selectedTabIndex = pagerState.currentPage,
                containerColor = EnlikoSurface,
                contentColor = EnlikoTextPrimary,
                indicator = { tabPositions ->
                    TabRowDefaults.SecondaryIndicator(
                        modifier = Modifier.tabIndicatorOffset(tabPositions[pagerState.currentPage]),
                        color = EnlikoPrimary
                    )
                }
            ) {
                tabs.forEachIndexed { index, title ->
                    Tab(
                        selected = pagerState.currentPage == index,
                        onClick = {
                            coroutineScope.launch {
                                pagerState.animateScrollToPage(index)
                            }
                        },
                        text = {
                            Text(
                                text = title,
                                fontWeight = if (pagerState.currentPage == index) FontWeight.Medium else FontWeight.Normal,
                                color = if (pagerState.currentPage == index) EnlikoTextPrimary else EnlikoTextSecondary
                            )
                        }
                    )
                }
            }
            
            // Pager Content
            HorizontalPager(
                state = pagerState,
                modifier = Modifier.fillMaxSize()
            ) { page ->
                when (page) {
                    0 -> MyStrategiesTab(
                        strategies = uiState.myStrategies,
                        onConfigure = onNavigateToStrategySettings,
                        onToggle = { strategy, enabled ->
                            viewModel.toggleStrategy(strategy, enabled)
                        }
                    )
                    1 -> MarketplaceTab(
                        strategies = uiState.marketplaceStrategies,
                        isLoading = uiState.isLoading
                    )
                    2 -> BacktestTab(
                        onNavigateToBacktest = onNavigateToBacktest
                    )
                }
            }
        }
    }
}

// MARK: - My Strategies Tab

@Composable
private fun MyStrategiesTab(
    strategies: List<TradingStrategy>,
    onConfigure: (String) -> Unit,
    onToggle: (String, Boolean) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        items(strategies) { strategy ->
            StrategyCard(
                strategy = strategy,
                onConfigure = { onConfigure(strategy.name) },
                onToggle = { enabled -> onToggle(strategy.name, enabled) }
            )
        }
    }
}

@Composable
private fun StrategyCard(
    strategy: TradingStrategy,
    onConfigure: () -> Unit,
    onToggle: (Boolean) -> Unit
) {
    var isEnabled by remember { mutableStateOf(strategy.isEnabled) }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Icon
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .clip(CircleShape)
                            .background(EnlikoPrimary.copy(alpha = 0.2f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = strategy.icon,
                            contentDescription = null,
                            tint = EnlikoPrimary,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                    
                    Column {
                        Text(
                            text = strategy.name.uppercase(),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = EnlikoTextPrimary
                        )
                        
                        Text(
                            text = strategy.description,
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
                
                Switch(
                    checked = isEnabled,
                    onCheckedChange = { 
                        isEnabled = it
                        onToggle(it)
                    },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = EnlikoPrimary,
                        checkedTrackColor = EnlikoPrimary.copy(alpha = 0.5f)
                    )
                )
            }
            
            HorizontalDivider(
                modifier = Modifier.padding(vertical = 12.dp),
                color = EnlikoBorder
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Configure button
                Row(
                    modifier = Modifier.clickable(onClick = onConfigure),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Settings,
                        contentDescription = null,
                        tint = EnlikoPrimary,
                        modifier = Modifier.size(18.dp)
                    )
                    Text(
                        text = Localization.get("configure"),
                        style = MaterialTheme.typography.bodyMedium,
                        color = EnlikoPrimary
                    )
                }
                
                // Status badge
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(6.dp)
                            .clip(CircleShape)
                            .background(if (isEnabled) EnlikoGreen else EnlikoTextMuted)
                    )
                    Text(
                        text = if (isEnabled) Localization.get("active") else Localization.get("inactive"),
                        style = MaterialTheme.typography.labelSmall,
                        color = if (isEnabled) EnlikoGreen else EnlikoTextMuted
                    )
                }
            }
        }
    }
}

// MARK: - Marketplace Tab

@Composable
private fun MarketplaceTab(
    strategies: List<MarketplaceStrategy>,
    isLoading: Boolean
) {
    if (isLoading) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator(color = EnlikoPrimary)
        }
    } else if (strategies.isEmpty()) {
        // Coming Soon placeholder
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.Storefront,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = EnlikoTextMuted
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = Localization.get("marketplace_coming_soon"),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium,
                color = EnlikoTextPrimary
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = Localization.get("marketplace_desc"),
                style = MaterialTheme.typography.bodyMedium,
                color = EnlikoTextSecondary
            )
        }
    } else {
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(strategies) { strategy ->
                MarketplaceStrategyCard(strategy = strategy)
            }
        }
    }
}

@Composable
private fun MarketplaceStrategyCard(strategy: MarketplaceStrategy) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = strategy.displayName,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = EnlikoTextPrimary
                    )
                    
                    Text(
                        text = "by ${strategy.author}",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                }
                
                // Rating
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Star,
                        contentDescription = null,
                        tint = EnlikoYellow,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = String.format("%.1f", strategy.rating),
                        style = MaterialTheme.typography.bodyMedium,
                        color = EnlikoTextSecondary
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = strategy.description ?: "No description",
                style = MaterialTheme.typography.bodySmall,
                color = EnlikoTextSecondary,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis
            )
            
            HorizontalDivider(
                modifier = Modifier.padding(vertical = 12.dp),
                color = EnlikoBorder
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom
            ) {
                // Stats
                Row(horizontalArrangement = Arrangement.spacedBy(24.dp)) {
                    Column {
                        Text(
                            text = Localization.get("win_rate"),
                            style = MaterialTheme.typography.labelSmall,
                            color = EnlikoTextMuted
                        )
                        Text(
                            text = "${(strategy.winRate * 100).toInt()}%",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold,
                            color = EnlikoGreen
                        )
                    }
                    
                    Column {
                        Text(
                            text = Localization.get("monthly_pnl"),
                            style = MaterialTheme.typography.labelSmall,
                            color = EnlikoTextMuted
                        )
                        Text(
                            text = String.format("%+.1f%%", strategy.monthlyPnl),
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold,
                            color = if (strategy.monthlyPnl >= 0) EnlikoGreen else EnlikoRed
                        )
                    }
                }
                
                // Price/Subscribe button
                Button(
                    onClick = { /* Subscribe */ },
                    colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = if (strategy.price > 0) "$${strategy.price.toInt()}/mo" else "Free"
                    )
                }
            }
        }
    }
}

// MARK: - Backtest Tab

@Composable
private fun BacktestTab(onNavigateToBacktest: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Analytics,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = EnlikoPrimary
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = Localization.get("backtest_title"),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = EnlikoTextPrimary
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = Localization.get("backtest_desc"),
            style = MaterialTheme.typography.bodyMedium,
            color = EnlikoTextSecondary,
            modifier = Modifier.padding(horizontal = 32.dp)
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = onNavigateToBacktest,
            colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary),
            shape = RoundedCornerShape(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(Icons.Default.PlayArrow, contentDescription = null)
                Text(Localization.get("start_backtest"))
            }
        }
    }
}

// MARK: - Data Models

data class TradingStrategy(
    val name: String,
    val description: String,
    val isEnabled: Boolean = true
) {
    val icon: ImageVector
        get() = when (name.lowercase()) {
            "oi" -> Icons.Default.BarChart
            "scryptomera" -> Icons.Default.GraphicEq
            "scalper" -> Icons.Default.FlashOn
            "elcaro" -> Icons.Default.Psychology
            "fibonacci" -> Icons.Default.Functions
            "rsi_bb" -> Icons.Default.ShowChart
            else -> Icons.Default.Description
        }
}

data class MarketplaceStrategy(
    val id: String,
    val displayName: String,
    val author: String,
    val description: String? = null,
    val rating: Double = 0.0,
    val winRate: Double = 0.0,
    val monthlyPnl: Double = 0.0,
    val price: Double = 0.0
)
