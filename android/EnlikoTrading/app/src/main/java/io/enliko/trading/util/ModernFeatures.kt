package io.enliko.trading.util

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.delay

/**
 * Modern Features Module for Enliko Trading Android App
 * =====================================================
 * 
 * Топовые фичи современной мобильной разработки 2024-2026:
 * 
 * 1. Haptic Feedback - тактильная обратная связь
 * 2. Advanced Animations - продвинутые анимации
 * 3. Skeleton Loading - скелетонная загрузка
 * 4. Pull-to-Refresh - обновление свайпом
 * 5. Shimmer Effect - эффект мерцания
 * 6. Gesture Handlers - обработка жестов
 * 7. Offline-First - работа без интернета
 * 8. Adaptive Layout - адаптивная верстка
 * 9. Dynamic Color - динамические цвета Material You
 * 10. Predictive Back - предиктивный возврат
 */

// =============================================================================
// 1. HAPTIC FEEDBACK - Тактильная обратная связь
// =============================================================================

/**
 * Типы тактильной обратной связи
 */
enum class HapticType {
    LIGHT,          // Лёгкий тап
    MEDIUM,         // Средний тап
    HEAVY,          // Сильный тап
    SUCCESS,        // Успешное действие (tick)
    ERROR,          // Ошибка (double vibration)
    WARNING,        // Предупреждение
    SELECTION,      // Выбор элемента
    BUTTON_PRESS    // Нажатие кнопки
}

/**
 * Управление хаптикой
 */
class HapticManager(private val context: Context) {
    
    private val vibrator: Vibrator by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val manager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            manager.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }
    }
    
    /**
     * Выполнить тактильную обратную связь
     */
    fun performHaptic(type: HapticType) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val effect = when (type) {
                HapticType.LIGHT -> VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK)
                HapticType.MEDIUM -> VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK)
                HapticType.HEAVY -> VibrationEffect.createPredefined(VibrationEffect.EFFECT_HEAVY_CLICK)
                HapticType.SUCCESS -> VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK)
                HapticType.ERROR -> VibrationEffect.createWaveform(longArrayOf(0, 50, 50, 50), -1)
                HapticType.WARNING -> VibrationEffect.createWaveform(longArrayOf(0, 100), -1)
                HapticType.SELECTION -> VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK)
                HapticType.BUTTON_PRESS -> VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK)
            }
            vibrator.vibrate(effect)
        } else {
            // Fallback для старых версий
            @Suppress("DEPRECATION")
            vibrator.vibrate(
                when (type) {
                    HapticType.LIGHT -> 10L
                    HapticType.MEDIUM -> 25L
                    HapticType.HEAVY -> 50L
                    HapticType.SUCCESS -> 15L
                    HapticType.ERROR -> 75L
                    HapticType.WARNING -> 40L
                    HapticType.SELECTION -> 10L
                    HapticType.BUTTON_PRESS -> 20L
                }
            )
        }
    }
    
    /**
     * Хаптика для успешной сделки
     */
    fun tradeSuccess() = performHaptic(HapticType.SUCCESS)
    
    /**
     * Хаптика для ошибки
     */
    fun tradeError() = performHaptic(HapticType.ERROR)
    
    /**
     * Хаптика для нового сигнала
     */
    fun newSignal() = performHaptic(HapticType.MEDIUM)
    
    /**
     * Хаптика для изменения цены
     */
    fun priceChange() = performHaptic(HapticType.LIGHT)
}

/**
 * Composable remember для HapticManager
 */
@Composable
fun rememberHapticManager(): HapticManager {
    val context = LocalContext.current
    return remember { HapticManager(context) }
}

// =============================================================================
// 2. ADVANCED ANIMATIONS - Продвинутые анимации
// =============================================================================

/**
 * Пульсирующая анимация для важных элементов
 */
@Composable
fun PulsingAnimation(
    modifier: Modifier = Modifier,
    pulseFraction: Float = 1.2f,
    content: @Composable () -> Unit
) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = pulseFraction,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )
    
    Box(modifier = modifier.scale(scale)) {
        content()
    }
}

/**
 * Анимация появления снизу (для модальных окон)
 */
@Composable
fun SlideInFromBottom(
    visible: Boolean,
    content: @Composable AnimatedVisibilityScope.() -> Unit
) {
    AnimatedVisibility(
        visible = visible,
        enter = slideInVertically(
            initialOffsetY = { it },
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessLow
            )
        ) + fadeIn(),
        exit = slideOutVertically(
            targetOffsetY = { it },
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioNoBouncy,
                stiffness = Spring.StiffnessMedium
            )
        ) + fadeOut(),
        content = content
    )
}

/**
 * Анимация для карточек позиций
 */
@Composable
fun AnimatedPositionCard(
    modifier: Modifier = Modifier,
    isProfit: Boolean,
    content: @Composable () -> Unit
) {
    var animationTriggered by remember { mutableStateOf(false) }
    
    val backgroundColor by animateColorAsState(
        targetValue = if (isProfit) {
            androidx.compose.ui.graphics.Color(0xFF1B5E20) // Green
        } else {
            androidx.compose.ui.graphics.Color(0xFFB71C1C) // Red
        },
        animationSpec = tween(500),
        label = "bgColor"
    )
    
    LaunchedEffect(Unit) {
        animationTriggered = true
    }
    
    val offsetX by animateFloatAsState(
        targetValue = if (animationTriggered) 0f else 100f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "offsetX"
    )
    
    Box(
        modifier = modifier.graphicsLayer {
            translationX = offsetX
            alpha = 1f - (offsetX / 100f)
        }
    ) {
        content()
    }
}

/**
 * Shake анимация для ошибок
 */
@Composable
fun ShakeAnimation(
    shake: Boolean,
    content: @Composable () -> Unit
) {
    val shakeOffset by animateFloatAsState(
        targetValue = if (shake) 10f else 0f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioHighBouncy,
            stiffness = Spring.StiffnessHigh
        ),
        label = "shake"
    )
    
    Box(
        modifier = Modifier.graphicsLayer {
            translationX = if (shake) {
                kotlin.math.sin(shakeOffset * 10) * 10
            } else 0f
        }
    ) {
        content()
    }
}

/**
 * Анимация счётчика (для PnL)
 */
@Composable
fun AnimatedCounter(
    count: Float,
    durationMillis: Int = 1000
): Float {
    var oldCount by remember { mutableFloatStateOf(count) }
    val animatedCount by animateFloatAsState(
        targetValue = count,
        animationSpec = tween(durationMillis),
        label = "counter"
    )
    
    LaunchedEffect(count) {
        oldCount = count
    }
    
    return animatedCount
}

// =============================================================================
// 3. SHIMMER EFFECT - Эффект мерцания для загрузки
// =============================================================================

/**
 * Shimmer эффект для скелетной загрузки
 */
@Composable
fun ShimmerEffect(
    modifier: Modifier = Modifier,
    widthOfShadowBrush: Int = 500,
    angleOfAxisY: Float = 270f,
    durationMillis: Int = 1000
): Modifier {
    val infiniteTransition = rememberInfiniteTransition(label = "shimmer")
    
    val shimmerProgress by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmerProgress"
    )
    
    return modifier.graphicsLayer {
        alpha = 0.3f + (shimmerProgress * 0.7f)
    }
}

// =============================================================================
// 4. PULL-TO-REFRESH HELPER
// =============================================================================

/**
 * Состояние для pull-to-refresh
 */
data class PullRefreshState(
    val isRefreshing: Boolean = false,
    val pullProgress: Float = 0f
)

/**
 * Контроллер pull-to-refresh
 */
class PullRefreshController {
    var state by mutableStateOf(PullRefreshState())
        private set
    
    fun startRefresh() {
        state = state.copy(isRefreshing = true)
    }
    
    fun endRefresh() {
        state = state.copy(isRefreshing = false, pullProgress = 0f)
    }
    
    fun updateProgress(progress: Float) {
        if (!state.isRefreshing) {
            state = state.copy(pullProgress = progress.coerceIn(0f, 1f))
        }
    }
}

@Composable
fun rememberPullRefreshController(): PullRefreshController {
    return remember { PullRefreshController() }
}

// =============================================================================
// 5. OFFLINE-FIRST HELPERS
// =============================================================================

/**
 * Состояние подключения
 */
enum class ConnectionState {
    CONNECTED,
    DISCONNECTED,
    RECONNECTING
}

/**
 * Кеш данных для offline режима
 */
data class OfflineCache<T>(
    val data: T?,
    val timestamp: Long,
    val isStale: Boolean
)

/**
 * Проверка актуальности кеша
 */
fun <T> OfflineCache<T>.isValid(maxAgeMs: Long = 5 * 60 * 1000): Boolean {
    return data != null && !isStale && (System.currentTimeMillis() - timestamp) < maxAgeMs
}

// =============================================================================
// 6. GESTURE UTILITIES
// =============================================================================

/**
 * Направление свайпа
 */
enum class SwipeDirection {
    LEFT,
    RIGHT,
    UP,
    DOWN
}

/**
 * Действия для свайпа на карточке позиции
 */
data class SwipeActions(
    val onSwipeLeft: (() -> Unit)? = null,   // Закрыть позицию
    val onSwipeRight: (() -> Unit)? = null,  // Добавить к позиции
    val leftLabel: String = "Close",
    val rightLabel: String = "Add"
)

// =============================================================================
// 7. ADAPTIVE LAYOUT
// =============================================================================

/**
 * Типы устройств по размеру экрана
 */
enum class DeviceType {
    PHONE_COMPACT,    // < 360dp
    PHONE_MEDIUM,     // 360dp - 400dp
    PHONE_EXPANDED,   // 400dp - 600dp
    TABLET,           // 600dp - 840dp
    DESKTOP           // > 840dp
}

/**
 * Определение типа устройства
 */
@Composable
fun rememberDeviceType(): DeviceType {
    val configuration = LocalContext.current.resources.configuration
    val widthDp = configuration.screenWidthDp
    
    return remember(widthDp) {
        when {
            widthDp < 360 -> DeviceType.PHONE_COMPACT
            widthDp < 400 -> DeviceType.PHONE_MEDIUM
            widthDp < 600 -> DeviceType.PHONE_EXPANDED
            widthDp < 840 -> DeviceType.TABLET
            else -> DeviceType.DESKTOP
        }
    }
}

// =============================================================================
// 8. PRICE CHANGE ANIMATION
// =============================================================================

/**
 * Анимированный текст изменения цены
 */
@Composable
fun AnimatedPriceChange(
    price: Double,
    previousPrice: Double,
    modifier: Modifier = Modifier,
    content: @Composable (color: androidx.compose.ui.graphics.Color, formattedPrice: String) -> Unit
) {
    val color by animateColorAsState(
        targetValue = when {
            price > previousPrice -> androidx.compose.ui.graphics.Color(0xFF4CAF50) // Green
            price < previousPrice -> androidx.compose.ui.graphics.Color(0xFFF44336) // Red
            else -> androidx.compose.ui.graphics.Color.White
        },
        animationSpec = tween(300),
        label = "priceColor"
    )
    
    val formattedPrice = "%.2f".format(price)
    
    Box(modifier = modifier) {
        content(color, formattedPrice)
    }
}

// =============================================================================
// 9. TRADING SUCCESS CELEBRATION
// =============================================================================

/**
 * Эффект конфетти для успешной сделки
 */
@Composable
fun TradeCelebration(
    show: Boolean,
    onComplete: () -> Unit
) {
    if (show) {
        val haptic = rememberHapticManager()
        
        LaunchedEffect(Unit) {
            haptic.tradeSuccess()
            delay(2000)
            onComplete()
        }
        
        // Анимация празднования (упрощённая версия)
        val alpha by animateFloatAsState(
            targetValue = if (show) 1f else 0f,
            animationSpec = tween(500),
            label = "celebrationAlpha"
        )
        
        Box(
            modifier = Modifier.graphicsLayer { this.alpha = alpha }
        ) {
            // Здесь можно добавить Canvas с конфетти
        }
    }
}

// =============================================================================
// 10. LOADING STATES
// =============================================================================

/**
 * Состояние загрузки с прогрессом
 */
sealed class LoadingState<out T> {
    object Idle : LoadingState<Nothing>()
    object Loading : LoadingState<Nothing>()
    data class Success<T>(val data: T) : LoadingState<T>()
    data class Error(val message: String, val retry: (() -> Unit)? = null) : LoadingState<Nothing>()
    data class Progress(val percent: Int) : LoadingState<Nothing>()
}

/**
 * Extension для удобства работы с LoadingState
 */
fun <T> LoadingState<T>.isLoading() = this is LoadingState.Loading || this is LoadingState.Progress
fun <T> LoadingState<T>.isSuccess() = this is LoadingState.Success
fun <T> LoadingState<T>.isError() = this is LoadingState.Error
fun <T> LoadingState<T>.getDataOrNull() = (this as? LoadingState.Success)?.data
