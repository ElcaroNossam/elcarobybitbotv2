package io.enliko.trading.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*

// ═══════════════════════════════════════════════════════════════════════════════
// MODERN COMPONENTS LIBRARY - 2026 Design System
// Premium glassmorphism, neon accents, smooth animations
// Synced with iOS ModernComponents.swift
// ═══════════════════════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════════════════════
// GLASS MORPHISM CARDS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Glass Card - Premium glassmorphism effect
 */
@Composable
fun GlassCard(
    modifier: Modifier = Modifier,
    cornerRadius: Dp = 20.dp,
    glowColor: Color = EnlikoPrimary,
    content: @Composable ColumnScope.() -> Unit
) {
    Surface(
        modifier = modifier
            .shadow(
                elevation = 16.dp,
                shape = RoundedCornerShape(cornerRadius),
                ambientColor = glowColor.copy(alpha = 0.15f),
                spotColor = glowColor.copy(alpha = 0.25f)
            )
            .border(
                width = 1.dp,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        GlassHighlight,
                        GlassBorder
                    )
                ),
                shape = RoundedCornerShape(cornerRadius)
            ),
        shape = RoundedCornerShape(cornerRadius),
        color = DarkSurfaceVariant.copy(alpha = 0.9f)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            content = content
        )
    }
}

/**
 * Glow Card - Card with colored glow effect
 */
@Composable
fun GlowCard(
    modifier: Modifier = Modifier,
    glowColor: Color = EnlikoPrimary,
    cornerRadius: Dp = 20.dp,
    content: @Composable ColumnScope.() -> Unit
) {
    Box(
        modifier = modifier
            .drawBehind {
                drawCircle(
                    color = glowColor.copy(alpha = 0.15f),
                    radius = size.maxDimension * 0.6f,
                    center = center
                )
            }
    ) {
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            cornerRadius = cornerRadius,
            glowColor = glowColor,
            content = content
        )
    }
}

/**
 * Position Card - With side-based gradient accent
 */
@Composable
fun PositionGlassCard(
    modifier: Modifier = Modifier,
    isLong: Boolean,
    isProfitable: Boolean = true,
    content: @Composable ColumnScope.() -> Unit
) {
    val sideColor = if (isLong) EnlikoGreen else EnlikoRed
    val pnlColors = if (isProfitable) GradientProfitColors else GradientLossColors
    
    Surface(
        modifier = modifier
            .shadow(
                elevation = 12.dp,
                shape = RoundedCornerShape(16.dp),
                ambientColor = sideColor.copy(alpha = 0.1f),
                spotColor = sideColor.copy(alpha = 0.2f)
            )
            .border(
                width = 1.dp,
                brush = Brush.linearGradient(pnlColors.map { it.copy(alpha = 0.3f) }),
                shape = RoundedCornerShape(16.dp)
            ),
        shape = RoundedCornerShape(16.dp),
        color = DarkSurfaceVariant.copy(alpha = 0.95f)
    ) {
        Row {
            // Side accent bar
            Box(
                modifier = Modifier
                    .width(4.dp)
                    .fillMaxHeight()
                    .background(
                        brush = Brush.verticalGradient(
                            colors = if (isLong) GradientProfitColors else GradientLossColors
                        )
                    )
            )
            Column(
                modifier = Modifier
                    .weight(1f)
                    .padding(16.dp),
                content = content
            )
        }
    }
}

/**
 * Order Card - With orange gradient accent
 */
@Composable
fun OrderGlassCard(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit
) {
    Surface(
        modifier = modifier
            .shadow(
                elevation = 10.dp,
                shape = RoundedCornerShape(16.dp),
                ambientColor = EnlikoOrange.copy(alpha = 0.1f)
            )
            .border(
                width = 1.dp,
                brush = Brush.linearGradient(
                    colors = listOf(EnlikoOrange.copy(alpha = 0.3f), GlassBorder)
                ),
                shape = RoundedCornerShape(16.dp)
            ),
        shape = RoundedCornerShape(16.dp),
        color = DarkSurfaceVariant.copy(alpha = 0.95f)
    ) {
        Row {
            // Orange accent bar
            Box(
                modifier = Modifier
                    .width(4.dp)
                    .fillMaxHeight()
                    .background(
                        brush = Brush.verticalGradient(GradientPrimaryColors)
                    )
            )
            Column(
                modifier = Modifier
                    .weight(1f)
                    .padding(16.dp),
                content = content
            )
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ANIMATED BACKGROUNDS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Animated Gradient Background - Premium feel
 */
@Composable
fun AnimatedGradientBackground(
    colors: List<Color> = listOf(
        EnlikoPrimary,
        EnlikoOrange,
        EnlikoPrimary
    ),
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "gradient")
    val animatedOffset by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(5000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "offset"
    )
    
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(
                brush = Brush.linearGradient(
                    colors = colors,
                    start = Offset(animatedOffset * 1000, 0f),
                    end = Offset(0f, animatedOffset * 1000)
                )
            )
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// PREMIUM BUTTONS
// ═══════════════════════════════════════════════════════════════════════════════

enum class NeuButtonStyle {
    PRIMARY, SECONDARY, SUCCESS, DANGER, PREMIUM
}

@Composable
fun NeuButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    isLoading: Boolean = false,
    style: NeuButtonStyle = NeuButtonStyle.PRIMARY,
    enabled: Boolean = true
) {
    val containerColor = when (style) {
        NeuButtonStyle.PRIMARY -> EnlikoPrimary
        NeuButtonStyle.SECONDARY -> DarkSurfaceVariant
        NeuButtonStyle.SUCCESS -> EnlikoGreen
        NeuButtonStyle.DANGER -> EnlikoRed
        NeuButtonStyle.PREMIUM -> EnlikoViolet
    }
    
    val contentColor = when (style) {
        NeuButtonStyle.SECONDARY -> EnlikoTextSecondary
        else -> Color.White
    }
    
    Button(
        onClick = onClick,
        modifier = modifier
            .height(52.dp)
            .shadow(
                elevation = 12.dp,
                shape = RoundedCornerShape(14.dp),
                ambientColor = containerColor.copy(alpha = 0.3f),
                spotColor = containerColor.copy(alpha = 0.4f)
            ),
        enabled = enabled && !isLoading,
        colors = ButtonDefaults.buttonColors(
            containerColor = containerColor,
            contentColor = contentColor,
            disabledContainerColor = containerColor.copy(alpha = 0.5f)
        ),
        shape = RoundedCornerShape(14.dp)
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp),
                color = contentColor,
                strokeWidth = 2.dp
            )
        } else {
            icon?.let {
                Icon(
                    imageVector = it,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(Modifier.width(8.dp))
            }
            Text(
                text = text,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}

/**
 * Gradient Button - Premium gradient style
 */
@Composable
fun GradientButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    gradientColors: List<Color> = GradientPrimaryColors,
    icon: ImageVector? = null,
    isLoading: Boolean = false,
    enabled: Boolean = true
) {
    Button(
        onClick = onClick,
        modifier = modifier
            .height(52.dp)
            .shadow(
                elevation = 16.dp,
                shape = RoundedCornerShape(14.dp),
                ambientColor = gradientColors.first().copy(alpha = 0.3f)
            ),
        enabled = enabled && !isLoading,
        colors = ButtonDefaults.buttonColors(
            containerColor = Color.Transparent,
            disabledContainerColor = Color.Transparent
        ),
        contentPadding = PaddingValues(0.dp),
        shape = RoundedCornerShape(14.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.linearGradient(gradientColors),
                    shape = RoundedCornerShape(14.dp)
                ),
            contentAlignment = Alignment.Center
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = Color.White,
                    strokeWidth = 2.dp
                )
            } else {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    icon?.let {
                        Icon(
                            imageVector = it,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(Modifier.width(8.dp))
                    }
                    Text(
                        text = text,
                        color = Color.White,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SHIMMER & SKELETON LOADING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Shimmer Loading Effect - Premium animation
 */
fun Modifier.shimmerEffect(): Modifier = composed {
    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer"
    )
    
    background(
        brush = Brush.linearGradient(
            colors = listOf(
                DarkSurfaceHighlight.copy(alpha = 0.6f),
                DarkSurfaceHighlight.copy(alpha = 0.2f),
                DarkSurfaceHighlight.copy(alpha = 0.6f)
            ),
            start = Offset(translateAnim - 500, 0f),
            end = Offset(translateAnim, 0f)
        )
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// SKELETON LOADERS
// ═══════════════════════════════════════════════════════════════════════════════

@Composable
fun SkeletonBox(
    modifier: Modifier = Modifier,
    cornerRadius: Dp = 8.dp
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(cornerRadius))
            .shimmerEffect()
    )
}

@Composable
fun SkeletonText(
    modifier: Modifier = Modifier,
    width: Dp = 100.dp,
    height: Dp = 16.dp
) {
    SkeletonBox(
        modifier = modifier
            .width(width)
            .height(height),
        cornerRadius = 4.dp
    )
}

@Composable
fun PositionCardSkeleton() {
    GlassCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SkeletonText(width = 80.dp)
                SkeletonText(width = 60.dp)
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SkeletonText(width = 100.dp, height = 24.dp)
                SkeletonText(width = 80.dp, height = 24.dp)
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SkeletonText(width = 120.dp)
                SkeletonText(width = 70.dp)
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ANIMATED COUNTERS
// ═══════════════════════════════════════════════════════════════════════════════

@Composable
fun AnimatedCounter(
    count: Double,
    modifier: Modifier = Modifier,
    style: androidx.compose.ui.text.TextStyle = MaterialTheme.typography.headlineMedium,
    prefix: String = "",
    suffix: String = "",
    color: Color = EnlikoTextPrimary
) {
    var oldCount by remember { mutableDoubleStateOf(count) }
    val animatedCount by animateFloatAsState(
        targetValue = count.toFloat(),
        animationSpec = tween(durationMillis = 500, easing = FastOutSlowInEasing),
        label = "counter"
    )
    
    LaunchedEffect(count) {
        oldCount = count
    }
    
    Text(
        text = "$prefix${String.format("%,.2f", animatedCount)}$suffix",
        style = style,
        fontWeight = FontWeight.Bold,
        color = color,
        modifier = modifier
    )
}

/**
 * PnL Counter with color change
 */
@Composable
fun PnLCounter(
    value: Double,
    modifier: Modifier = Modifier,
    style: androidx.compose.ui.text.TextStyle = MaterialTheme.typography.headlineMedium,
    prefix: String = "$"
) {
    val color = when {
        value > 0 -> EnlikoGreen
        value < 0 -> EnlikoRed
        else -> EnlikoTextMuted
    }
    val sign = if (value > 0) "+" else ""
    
    AnimatedCounter(
        count = value,
        modifier = modifier,
        style = style,
        prefix = "$sign$prefix",
        color = color
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// INDICATORS & BADGES
// ═══════════════════════════════════════════════════════════════════════════════

@Composable
fun PulsatingDot(
    modifier: Modifier = Modifier,
    color: Color = EnlikoGreen,
    size: Dp = 8.dp
) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.5f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )
    
    Box(
        modifier = modifier
            .size(size * scale)
            .clip(CircleShape)
            .background(color.copy(alpha = alpha))
    )
}

@Composable
fun PriceChangeIndicator(
    changePercent: Double,
    modifier: Modifier = Modifier
) {
    val isPositive = changePercent >= 0
    val color = if (isPositive) EnlikoGreen else EnlikoRed
    val icon = if (isPositive) Icons.Default.TrendingUp else Icons.Default.TrendingDown
    
    Surface(
        modifier = modifier,
        color = color.copy(alpha = 0.1f),
        shape = RoundedCornerShape(6.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(14.dp)
            )
            Text(
                text = "${if (isPositive) "+" else ""}${String.format("%.2f", changePercent)}%",
                color = color,
                fontWeight = FontWeight.Medium,
                style = MaterialTheme.typography.labelMedium
            )
        }
    }
}

@Composable
fun StatusBadge(
    text: String,
    modifier: Modifier = Modifier,
    isActive: Boolean = true
) {
    val color = if (isActive) EnlikoGreen else EnlikoRed
    
    Surface(
        modifier = modifier,
        color = color.copy(alpha = 0.1f),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            PulsatingDot(color = color)
            Text(
                text = text,
                color = color,
                fontWeight = FontWeight.Medium,
                style = MaterialTheme.typography.labelMedium
            )
        }
    }
}

/**
 * Side Badge - Long/Short indicator
 */
@Composable
fun SideBadge(
    isLong: Boolean,
    modifier: Modifier = Modifier
) {
    val color = if (isLong) EnlikoGreen else EnlikoRed
    val text = if (isLong) "LONG" else "SHORT"
    
    Surface(
        modifier = modifier,
        color = color.copy(alpha = 0.15f),
        shape = RoundedCornerShape(6.dp)
    ) {
        Text(
            text = text,
            color = color,
            fontWeight = FontWeight.Bold,
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

/**
 * Exchange Badge - Bybit/HyperLiquid indicator
 */
@Composable
fun ExchangeBadge(
    exchange: String,
    modifier: Modifier = Modifier
) {
    val color = if (exchange.lowercase() == "bybit") EnlikoBybit else EnlikoHL
    
    Surface(
        modifier = modifier,
        color = color.copy(alpha = 0.15f),
        shape = RoundedCornerShape(6.dp)
    ) {
        Text(
            text = exchange.uppercase(),
            color = color,
            fontWeight = FontWeight.Medium,
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EMPTY & LOADING STATES
// ═══════════════════════════════════════════════════════════════════════════════

@Composable
fun EmptyStateView(
    icon: ImageVector,
    title: String,
    subtitle: String,
    modifier: Modifier = Modifier,
    actionText: String? = null,
    onAction: (() -> Unit)? = null
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(80.dp)
                .clip(CircleShape)
                .background(DarkSurfaceVariant),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(40.dp),
                tint = EnlikoTextMuted
            )
        }
        Spacer(Modifier.height(20.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Medium,
            color = EnlikoTextPrimary
        )
        Spacer(Modifier.height(8.dp))
        Text(
            text = subtitle,
            style = MaterialTheme.typography.bodyMedium,
            color = EnlikoTextMuted
        )
        if (actionText != null && onAction != null) {
            Spacer(Modifier.height(24.dp))
            GradientButton(
                text = actionText,
                onClick = onAction
            )
        }
    }
}

@Composable
fun LoadingOverlay(
    isLoading: Boolean,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Box(modifier = modifier) {
        content()
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(GlassOverlay),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(
                    color = EnlikoPrimary,
                    strokeWidth = 3.dp
                )
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// STAT CARDS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Dashboard Stat Card with icon
 */
@Composable
fun DashboardStatCard(
    title: String,
    value: String,
    icon: ImageVector,
    iconColor: Color = EnlikoPrimary,
    modifier: Modifier = Modifier
) {
    GlassCard(
        modifier = modifier,
        glowColor = iconColor
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(CircleShape)
                    .background(iconColor.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = iconColor,
                    modifier = Modifier.size(22.dp)
                )
            }
            Column {
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelMedium,
                    color = EnlikoTextMuted
                )
                Text(
                    text = value,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = EnlikoTextPrimary
                )
            }
        }
    }
}

/**
 * Balance Card with gradient and glass
 */
@Composable
fun BalanceCard(
    title: String,
    balance: Double,
    pnl: Double? = null,
    modifier: Modifier = Modifier
) {
    GlowCard(
        modifier = modifier,
        glowColor = if ((pnl ?: 0.0) >= 0) EnlikoGreen else EnlikoRed
    ) {
        Column(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.labelMedium,
                color = EnlikoTextMuted
            )
            AnimatedCounter(
                count = balance,
                prefix = "$",
                style = MaterialTheme.typography.headlineMedium
            )
            pnl?.let {
                PriceChangeIndicator(changePercent = it)
            }
        }
    }
}
