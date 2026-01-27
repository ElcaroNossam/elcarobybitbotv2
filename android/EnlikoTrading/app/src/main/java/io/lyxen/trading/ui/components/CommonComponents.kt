package io.enliko.trading.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import io.enliko.trading.util.LocalStrings

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
            FilterChip(
                selected = isSelected,
                onClick = { onAccountTypeSelected(type) },
                label = { Text(label) },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(8.dp),
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = MaterialTheme.colorScheme.primary,
                    selectedLabelColor = MaterialTheme.colorScheme.onPrimary
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
        contentAlignment = androidx.compose.ui.Alignment.Center
    ) {
        CircularProgressIndicator()
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
        horizontalAlignment = androidx.compose.ui.Alignment.CenterHorizontally
    ) {
        Text(
            text = message,
            color = MaterialTheme.colorScheme.error,
            style = MaterialTheme.typography.bodyMedium
        )
        
        onRetry?.let {
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = it) {
                Text(strings.retry)
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
            .padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = androidx.compose.ui.Alignment.CenterVertically
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold
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
        value > 0 -> io.enliko.trading.ui.theme.LongGreen
        value < 0 -> io.enliko.trading.ui.theme.ShortRed
        else -> MaterialTheme.colorScheme.onSurface
    }
    val prefix = if (showSign && value >= 0) "+" else ""
    
    Text(
        text = "$prefix${String.format("%.2f", value)}",
        style = style,
        color = color
    )
}
