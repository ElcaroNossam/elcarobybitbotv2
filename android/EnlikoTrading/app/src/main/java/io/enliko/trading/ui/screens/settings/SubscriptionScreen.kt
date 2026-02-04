package io.enliko.trading.ui.screens.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.Localization

/**
 * SubscriptionScreen - Matching iOS SubscriptionView.swift
 * Features: Plan selection, ELC balance, payment with ELC tokens
 */

data class SubscriptionPlan(
    val id: String,
    val name: String,
    val description: String,
    val monthlyPrice: Int,
    val features: List<String>,
    val color: Color,
    val isFeatured: Boolean = false
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SubscriptionScreen(
    onBack: () -> Unit,
    viewModel: SubscriptionViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedPlan by remember { mutableStateOf("premium") }
    var selectedDuration by remember { mutableStateOf("1m") }
    var showBuySheet by remember { mutableStateOf(false) }
    var showConfirmDialog by remember { mutableStateOf(false) }
    
    val plans = listOf(
        SubscriptionPlan(
            id = "basic",
            name = "Basic",
            description = "Bybit only, OI + RSI/BB",
            monthlyPrice = 50,
            features = listOf(
                "Demo + Real trading",
                "Strategies: OI, RSI+BB",
                "Bybit only",
                "ATR risk management"
            ),
            color = Color(0xFF2196F3)
        ),
        SubscriptionPlan(
            id = "premium",
            name = "Premium",
            description = "All exchanges, all strategies",
            monthlyPrice = 100,
            features = listOf(
                "All 6 strategies",
                "Bybit + HyperLiquid",
                "DCA automation",
                "Partial Take Profit",
                "Break-Even protection",
                "Priority support"
            ),
            color = EnlikoPrimary,
            isFeatured = true
        ),
        SubscriptionPlan(
            id = "enterprise",
            name = "Enterprise",
            description = "Custom solutions",
            monthlyPrice = 500,
            features = listOf(
                "Everything in Premium",
                "Custom strategies",
                "Dedicated support",
                "API access",
                "White-label options",
                "Multiple accounts"
            ),
            color = Color(0xFFFFD700)
        )
    )
    
    val durations = listOf(
        "1m" to "1 Month" to 1.0,
        "3m" to "3 Months" to 0.9,  // 10% discount
        "6m" to "6 Months" to 0.8,  // 20% discount
        "1y" to "1 Year" to 0.7     // 30% discount
    )
    
    val selectedPlanData = plans.find { it.id == selectedPlan } ?: plans[1]
    val durationMultiplier = when (selectedDuration) {
        "1m" -> 1.0
        "3m" -> 2.7
        "6m" -> 4.8
        "1y" -> 8.4
        else -> 1.0
    }
    val totalPrice = (selectedPlanData.monthlyPrice * durationMultiplier).toInt()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Subscription") },
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
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // ELC Balance Card
            item {
                ELCBalanceCard(
                    balance = uiState.elcBalance,
                    onBuyClick = { showBuySheet = true }
                )
            }
            
            // Current Plan Card
            item {
                CurrentPlanCard(
                    currentPlan = uiState.currentPlan,
                    expiryDate = uiState.expiryDate
                )
            }
            
            // Plan Selection
            item {
                Text(
                    text = "Select Plan",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = EnlikoTextPrimary
                )
            }
            
            // Plan Cards
            items(plans.size) { index ->
                PlanCard(
                    plan = plans[index],
                    isSelected = selectedPlan == plans[index].id,
                    onClick = { selectedPlan = plans[index].id }
                )
            }
            
            // Duration Selection
            item {
                Text(
                    text = "Select Duration",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = EnlikoTextPrimary,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
            
            item {
                DurationSelector(
                    selectedDuration = selectedDuration,
                    onDurationSelect = { selectedDuration = it }
                )
            }
            
            // Price Summary
            item {
                PriceSummaryCard(
                    plan = selectedPlanData.name,
                    duration = selectedDuration,
                    totalPrice = totalPrice,
                    hasEnough = uiState.elcBalance >= totalPrice
                )
            }
            
            // Pay Button
            item {
                Button(
                    onClick = {
                        if (uiState.elcBalance >= totalPrice) {
                            showConfirmDialog = true
                        } else {
                            showBuySheet = true
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (uiState.elcBalance >= totalPrice) EnlikoPrimary else EnlikoSecondary
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    if (uiState.elcBalance >= totalPrice) {
                        Icon(Icons.Default.Payment, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Pay $totalPrice ELC", fontWeight = FontWeight.SemiBold)
                    } else {
                        Icon(Icons.Default.Add, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Buy ${totalPrice - uiState.elcBalance.toInt()} ELC", fontWeight = FontWeight.SemiBold)
                    }
                }
            }
            
            item { Spacer(modifier = Modifier.height(32.dp)) }
        }
    }
    
    // Confirm Payment Dialog
    if (showConfirmDialog) {
        AlertDialog(
            onDismissRequest = { showConfirmDialog = false },
            title = { Text("Confirm Payment") },
            text = {
                Column {
                    Text("Pay $totalPrice ELC for ${selectedPlanData.name} ($selectedDuration)?")
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "⚠️ Payments are non-refundable",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoWarning
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.payWithELC(selectedPlan, selectedDuration, totalPrice)
                        showConfirmDialog = false
                    }
                ) {
                    Text("Pay", color = EnlikoPrimary)
                }
            },
            dismissButton = {
                TextButton(onClick = { showConfirmDialog = false }) {
                    Text("Cancel")
                }
            },
            containerColor = EnlikoCard
        )
    }
    
    // Buy ELC Bottom Sheet
    if (showBuySheet) {
        ModalBottomSheet(
            onDismissRequest = { showBuySheet = false },
            containerColor = EnlikoCard
        ) {
            BuyELCSheet(
                neededAmount = (totalPrice - uiState.elcBalance.toInt()).coerceAtLeast(0),
                onDismiss = { showBuySheet = false }
            )
        }
    }
}

@Composable
private fun ELCBalanceCard(
    balance: Double,
    onBuyClick: () -> Unit
) {
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
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Token,
                        contentDescription = null,
                        tint = EnlikoPrimary,
                        modifier = Modifier.size(24.dp)
                    )
                    Text(
                        text = "ELC Balance",
                        style = MaterialTheme.typography.titleSmall,
                        color = EnlikoTextSecondary
                    )
                }
                
                TextButton(onClick = onBuyClick) {
                    Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Buy")
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "${balance.toInt()} ELC",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = EnlikoTextPrimary
            )
            
            Text(
                text = "≈ $${balance.toInt()}",
                style = MaterialTheme.typography.bodyMedium,
                color = EnlikoTextSecondary
            )
        }
    }
}

@Composable
private fun CurrentPlanCard(
    currentPlan: String?,
    expiryDate: String?
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = null,
                    tint = EnlikoSecondary,
                    modifier = Modifier.size(24.dp)
                )
                Column {
                    Text(
                        text = "Current Plan",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                    Text(
                        text = currentPlan?.replaceFirstChar { it.uppercase() } ?: "Free",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = EnlikoPrimary
                    )
                }
            }
            
            if (expiryDate != null) {
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "Expires",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                    Text(
                        text = expiryDate,
                        style = MaterialTheme.typography.bodyMedium,
                        color = EnlikoTextPrimary
                    )
                }
            }
        }
    }
}

@Composable
private fun PlanCard(
    plan: SubscriptionPlan,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .then(
                if (isSelected) Modifier.border(2.dp, plan.color, RoundedCornerShape(16.dp))
                else Modifier
            ),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) plan.color.copy(alpha = 0.1f) else EnlikoCard
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(plan.color.copy(alpha = 0.2f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = when (plan.id) {
                                "basic" -> Icons.Default.Star
                                "premium" -> Icons.Default.Workspace_Premium
                                "enterprise" -> Icons.Default.Diamond
                                else -> Icons.Default.Star
                            },
                            contentDescription = null,
                            tint = plan.color,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                    
                    Column {
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = plan.name,
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = EnlikoTextPrimary
                            )
                            if (plan.isFeatured) {
                                Surface(
                                    shape = RoundedCornerShape(4.dp),
                                    color = plan.color
                                ) {
                                    Text(
                                        text = "POPULAR",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = Color.White,
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                    )
                                }
                            }
                        }
                        Text(
                            text = plan.description,
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "$${plan.monthlyPrice}",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = plan.color
                    )
                    Text(
                        text = "/month",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            HorizontalDivider(color = EnlikoBorder)
            Spacer(modifier = Modifier.height(12.dp))
            
            // Features
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                plan.features.forEach { feature ->
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Check,
                            contentDescription = null,
                            tint = EnlikoGreen,
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = feature,
                            style = MaterialTheme.typography.bodySmall,
                            color = EnlikoTextSecondary
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun DurationSelector(
    selectedDuration: String,
    onDurationSelect: (String) -> Unit
) {
    val durations = listOf(
        "1m" to "1 Month" to null,
        "3m" to "3 Months" to "-10%",
        "6m" to "6 Months" to "-20%",
        "1y" to "1 Year" to "-30%"
    )
    
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        durations.forEach { (id, label, discount) ->
            val (durationId, durationLabel) = id to label
            Surface(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(8.dp))
                    .clickable { onDurationSelect(durationId) }
                    .then(
                        if (selectedDuration == durationId) {
                            Modifier.border(2.dp, EnlikoPrimary, RoundedCornerShape(8.dp))
                        } else Modifier
                    ),
                color = if (selectedDuration == durationId) EnlikoPrimary.copy(alpha = 0.15f) else EnlikoCard
            ) {
                Column(
                    modifier = Modifier.padding(vertical = 12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = durationId.uppercase(),
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (selectedDuration == durationId) EnlikoPrimary else EnlikoTextPrimary
                    )
                    if (discount != null) {
                        Text(
                            text = discount,
                            style = MaterialTheme.typography.labelSmall,
                            color = EnlikoGreen
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun PriceSummaryCard(
    plan: String,
    duration: String,
    totalPrice: Int,
    hasEnough: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Plan",
                    style = MaterialTheme.typography.bodyMedium,
                    color = EnlikoTextSecondary
                )
                Text(
                    text = plan,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = EnlikoTextPrimary
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Duration",
                    style = MaterialTheme.typography.bodyMedium,
                    color = EnlikoTextSecondary
                )
                Text(
                    text = duration.uppercase(),
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = EnlikoTextPrimary
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            HorizontalDivider(color = EnlikoBorder)
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Total",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = EnlikoTextPrimary
                )
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "$totalPrice ELC",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = if (hasEnough) EnlikoPrimary else EnlikoRed
                    )
                    Text(
                        text = "≈ $$totalPrice",
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                }
            }
        }
    }
}

@Composable
private fun BuyELCSheet(
    neededAmount: Int,
    onDismiss: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = Icons.Default.Token,
            contentDescription = null,
            tint = EnlikoPrimary,
            modifier = Modifier.size(64.dp)
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Buy ELC Tokens",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = EnlikoTextPrimary
        )
        
        if (neededAmount > 0) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "You need $neededAmount more ELC",
                style = MaterialTheme.typography.bodyMedium,
                color = EnlikoTextSecondary
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            text = "Purchase ELC tokens with USDT via OxaPay\n1 ELC = 1 USD",
            style = MaterialTheme.typography.bodyMedium,
            color = EnlikoTextSecondary,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = { /* Open OxaPay payment */ },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary)
        ) {
            Text("Buy with USDT", fontWeight = FontWeight.SemiBold)
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        OutlinedButton(
            onClick = onDismiss,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Cancel")
        }
        
        Spacer(modifier = Modifier.height(32.dp))
    }
}
