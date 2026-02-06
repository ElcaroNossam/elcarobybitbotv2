package io.enliko.trading.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.LocalStrings

// ═══════════════════════════════════════════════════════════════════════════════
// COMMON COMPONENTS - 2026 Design System
// ═══════════════════════════════════════════════════════════════════════════════

@Composable
fun AccountTypeSelector(
    exchange: String,
    selectedAccountType: String,
    onAccountTypeSelected: (String) -> Unit
) {
    val strings = LocalStrings.current
    
    val options = if (exchange == "hyperliquid") {
        listOf("testnet" to strings.testnet, "mainnet" to strings.mainnet)
    } else {
        listOf("demo" to strings.demo, "real" to strings.real)
    }
    
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        options.forEach { (type, label) ->
            val isSelected = selectedAccountType == type
            val color = if (exchange == "hyperliquid") EnlikoHL else EnlikoBybit
            
            FilterChip(
                selected = isSelected,
                onClick = { onAccountTypeSelected(type) },
                label = { 
                    Text(
                        text = label,
                        fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
                    )
                },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(10.dp),
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = color,
                    selectedLabelColor = DarkOnBackground,
                    containerColor = DarkSurfaceVariant,
                    labelColor = EnlikoTextMuted
                ),
                border = FilterChipDefaults.filterChipBorder(
                    enabled = true,
                    selected = isSelected,
                    borderColor = EnlikoBorder,
                    selectedBorderColor = color
                )
            )
        }
    }
}

@Composable
fun LoadingIndicator(
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator(
            color = EnlikoPrimary,
            strokeWidth = 3.dp
        )
    }
}

@Composable
fun ErrorMessage(
    message: String,
    onRetry: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    val strings = LocalStrings.current
    
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = message,
            color = EnlikoRed,
            style = MaterialTheme.typography.bodyMedium
        )
        
        onRetry?.let {
            Spacer(modifier = Modifier.height(12.dp))
            TextButton(
                onClick = it,
                colors = ButtonDefaults.textButtonColors(
                    contentColor = EnlikoPrimary
                )
            ) {
                Text(
                    text = strings.retry,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
    }
}

@Composable
fun SectionHeader(
    title: String,
    action: (@Composable () -> Unit)? = null
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = EnlikoTextPrimary
        )
        action?.invoke()
    }
}

@Composable
fun PnLText(
    value: Double,
    showSign: Boolean = true,
    style: androidx.compose.ui.text.TextStyle = MaterialTheme.typography.bodyMedium
) {
    val color = when {
        value > 0 -> EnlikoGreen
        value < 0 -> EnlikoRed
        else -> EnlikoTextMuted
    }
    val prefix = if (showSign && value >= 0) "+" else ""
    
    Text(
        text = "$prefix${String.format("%.2f", value)}",
        style = style,
        color = color,
        fontWeight = FontWeight.SemiBold
    )
}

/**
 * Divider with subtle styling
 */
@Composable
fun EnlikoDivider(
    modifier: Modifier = Modifier
) {
    HorizontalDivider(
        modifier = modifier,
        thickness = 1.dp,
        color = EnlikoBorder
    )
}

/**
 * Section Card wrapper
 */
@Composable
fun SectionCard(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit
) {
    Surface(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp)),
        color = DarkSurfaceVariant,
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            content = content
        )
    }
}
