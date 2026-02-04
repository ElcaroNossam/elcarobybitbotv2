package io.enliko.trading.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*

/**
 * LoadingScreen - Matching iOS LoadingView.swift
 * Full-screen loading indicator with optional message
 */
@Composable
fun LoadingScreen(
    message: String = "Loading...",
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(EnlikoBackground),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Animated loading indicator
            PulsingLoadingIndicator()
            
            Text(
                text = message,
                style = MaterialTheme.typography.bodyLarge,
                color = EnlikoTextSecondary
            )
        }
    }
}

/**
 * PulsingLoadingIndicator - Animated pulsing circles
 */
@Composable
fun PulsingLoadingIndicator(
    modifier: Modifier = Modifier,
    color: Color = EnlikoPrimary
) {
    val infiniteTransition = rememberInfiniteTransition(label = "loading")
    
    // Pulsing animation
    val scale by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )
    
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )
    
    Box(
        modifier = modifier,
        contentAlignment = Alignment.Center
    ) {
        // Outer pulsing circle
        Box(
            modifier = Modifier
                .size(80.dp)
                .scale(scale)
                .clip(CircleShape)
                .background(color.copy(alpha = alpha * 0.3f))
        )
        
        // Inner circle
        Box(
            modifier = Modifier
                .size(60.dp)
                .clip(CircleShape)
                .background(color.copy(alpha = 0.5f))
        )
        
        // Center dot
        Box(
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
                .background(color)
        )
    }
}

/**
 * LoadingOverlay - Semi-transparent overlay with loading indicator
 */
@Composable
fun LoadingOverlay(
    isLoading: Boolean,
    message: String = "Loading...",
    content: @Composable () -> Unit
) {
    Box(modifier = Modifier.fillMaxSize()) {
        content()
        
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.6f)),
                contentAlignment = Alignment.Center
            ) {
                Card(
                    colors = CardDefaults.cardColors(containerColor = EnlikoCard),
                    elevation = CardDefaults.cardElevation(8.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        CircularProgressIndicator(color = EnlikoPrimary)
                        
                        Text(
                            text = message,
                            style = MaterialTheme.typography.bodyMedium,
                            color = EnlikoTextPrimary
                        )
                    }
                }
            }
        }
    }
}

/**
 * InlineLoadingIndicator - Small loading indicator for inline use
 */
@Composable
fun InlineLoadingIndicator(
    modifier: Modifier = Modifier,
    size: Int = 24,
    strokeWidth: Float = 2f,
    color: Color = EnlikoPrimary
) {
    CircularProgressIndicator(
        modifier = modifier.size(size.dp),
        strokeWidth = strokeWidth.dp,
        color = color
    )
}

/**
 * LoadingButton - Button with loading state
 */
@Composable
fun LoadingButton(
    text: String,
    isLoading: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    Button(
        onClick = onClick,
        modifier = modifier,
        enabled = enabled && !isLoading,
        colors = ButtonDefaults.buttonColors(containerColor = EnlikoPrimary)
    ) {
        if (isLoading) {
            InlineLoadingIndicator(
                size = 20,
                strokeWidth = 2f,
                color = Color.White
            )
            Spacer(modifier = Modifier.width(8.dp))
        }
        Text(
            text = if (isLoading) "Loading..." else text,
            fontWeight = FontWeight.SemiBold
        )
    }
}
