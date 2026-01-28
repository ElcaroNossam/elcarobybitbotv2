package io.enliko.trading.ui.screens.auth

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.EnlikoPrimary
import io.enliko.trading.ui.theme.EnlikoSecondary
import io.enliko.trading.util.LocalStrings
import kotlinx.coroutines.launch

/**
 * Legal Disclaimer Screen - REQUIRED for compliance
 * Must be shown on first launch before accessing any features
 */
@Composable
fun DisclaimerScreen(
    onAccept: () -> Unit,
    onDecline: () -> Unit
) {
    val strings = LocalStrings.current
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var isLoading by remember { mutableStateOf(false) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.background,
                        MaterialTheme.colorScheme.surface
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(40.dp))
            
            // Warning Icon
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = null,
                modifier = Modifier.size(60.dp),
                tint = Color(0xFFFFA500) // Orange
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Title
            Text(
                text = strings["disclaimer_title"] ?: "⚠️ Important Disclaimer",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Intro
            Text(
                text = strings["disclaimer_intro"] 
                    ?: "Enliko is an educational and analytical tool for cryptocurrency markets.",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Bullet Points Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    DisclaimerBullet(
                        icon = Icons.Default.Close,
                        color = Color.Red,
                        text = strings["disclaimer_not_financial_advice"] 
                            ?: "This is NOT financial advice"
                    )
                    
                    DisclaimerBullet(
                        icon = Icons.Default.TrendingDown,
                        color = Color(0xFFFFA500),
                        text = strings["disclaimer_risk_of_loss"] 
                            ?: "Trading involves substantial risk of loss"
                    )
                    
                    DisclaimerBullet(
                        icon = Icons.Default.History,
                        color = Color.Yellow,
                        text = strings["disclaimer_past_performance"] 
                            ?: "Past performance does not guarantee future results"
                    )
                    
                    DisclaimerBullet(
                        icon = Icons.Default.Person,
                        color = EnlikoPrimary,
                        text = strings["disclaimer_user_responsibility"] 
                            ?: "You are solely responsible for your decisions"
                    )
                    
                    DisclaimerBullet(
                        icon = Icons.Default.School,
                        color = Color(0xFF9C27B0),
                        text = strings["disclaimer_educational_only"] 
                            ?: "For educational purposes only"
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Risk Warning Box
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.Red.copy(alpha = 0.1f)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "⚠️ ${strings["disclaimer_risk_warning_title"] ?: "RISK WARNING"}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color.Red
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = strings["disclaimer_risk_warning_text"] 
                            ?: "Trading cryptocurrencies is highly speculative. You may lose some or all of your investment. Only trade with funds you can afford to lose.",
                        style = MaterialTheme.typography.bodySmall,
                        textAlign = TextAlign.Center,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Spacer(modifier = Modifier.weight(1f))
            
            // Accept Button
            Button(
                onClick = {
                    isLoading = true
                    scope.launch {
                        saveDisclaimerAcceptance(context)
                        onAccept()
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4CAF50) // Green
                ),
                enabled = !isLoading
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White
                    )
                } else {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = null,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = strings["disclaimer_accept_btn"] ?: "✅ I Understand & Accept",
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Decline Button
            TextButton(
                onClick = onDecline,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = strings["disclaimer_decline_btn"] ?: "❌ I Decline",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Legal Footer
            Text(
                text = strings["disclaimer_terms_agreement"] 
                    ?: "By accepting, you agree to our Terms of Service and Privacy Policy.",
                style = MaterialTheme.typography.bodySmall,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
private fun DisclaimerBullet(
    icon: ImageVector,
    color: Color,
    text: String
) {
    Row(
        verticalAlignment = Alignment.Top,
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(24.dp),
            tint = color
        )
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.weight(1f)
        )
    }
}

private fun saveDisclaimerAcceptance(context: Context) {
    val prefs = context.getSharedPreferences("enliko_prefs", Context.MODE_PRIVATE)
    prefs.edit()
        .putBoolean("disclaimer_accepted", true)
        .putLong("disclaimer_accepted_date", System.currentTimeMillis())
        .apply()
}

fun hasAcceptedDisclaimer(context: Context): Boolean {
    val prefs = context.getSharedPreferences("enliko_prefs", Context.MODE_PRIVATE)
    return prefs.getBoolean("disclaimer_accepted", false)
}
