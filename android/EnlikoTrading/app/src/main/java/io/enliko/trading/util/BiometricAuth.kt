package io.enliko.trading.util

import android.content.Context
import android.os.Build
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.suspendCancellableCoroutine
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * Biometric Authentication Manager for Enliko Trading
 * ===================================================
 * 
 * Современная биометрическая аутентификация:
 * - Fingerprint (отпечаток пальца)
 * - Face ID (распознавание лица)
 * - Fallback на PIN/Pattern
 * - Интеграция с Android Keystore
 * - Безопасное хранение токенов
 * 
 * Требования:
 * - androidx.biometric:biometric:1.1.0+
 * - minSdk 26 (Android 8.0+)
 */

/**
 * Результат биометрической аутентификации
 */
sealed class BiometricResult {
    object Success : BiometricResult()
    data class Error(val errorCode: Int, val errorMessage: String) : BiometricResult()
    object Canceled : BiometricResult()
    object NoBiometricAvailable : BiometricResult()
    object NotEnrolled : BiometricResult()
    object HardwareUnavailable : BiometricResult()
}

/**
 * Состояние биометрической аутентификации
 */
data class BiometricState(
    val isAvailable: Boolean = false,
    val isEnabled: Boolean = false,
    val biometricType: BiometricType = BiometricType.NONE,
    val lastAuthTime: Long = 0
)

/**
 * Типы биометрии
 */
enum class BiometricType {
    NONE,
    FINGERPRINT,
    FACE,
    IRIS,
    MULTIPLE // Несколько типов доступны
}

/**
 * Менеджер биометрической аутентификации
 */
class BiometricAuthManager(private val context: Context) {
    
    companion object {
        private const val KEY_NAME = "enliko_biometric_key"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        private const val BIOMETRIC_AUTH_TIMEOUT_MS = 5 * 60 * 1000L // 5 минут
    }
    
    private val biometricManager = BiometricManager.from(context)
    
    private val _state = MutableStateFlow(BiometricState())
    val state: StateFlow<BiometricState> = _state
    
    init {
        updateAvailability()
    }
    
    /**
     * Проверить доступность биометрии
     */
    fun checkBiometricAvailability(): BiometricResult {
        return when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
            BiometricManager.BIOMETRIC_SUCCESS -> BiometricResult.Success
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> BiometricResult.HardwareUnavailable
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> BiometricResult.HardwareUnavailable
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> BiometricResult.NotEnrolled
            else -> BiometricResult.NoBiometricAvailable
        }
    }
    
    /**
     * Обновить статус доступности
     */
    private fun updateAvailability() {
        val canAuthenticate = biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
            BiometricManager.Authenticators.BIOMETRIC_WEAK
        )
        
        val isAvailable = canAuthenticate == BiometricManager.BIOMETRIC_SUCCESS
        val biometricType = detectBiometricType()
        
        _state.value = _state.value.copy(
            isAvailable = isAvailable,
            biometricType = biometricType
        )
    }
    
    /**
     * Определить тип доступной биометрии
     */
    private fun detectBiometricType(): BiometricType {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            val authenticators = biometricManager.canAuthenticate(
                BiometricManager.Authenticators.BIOMETRIC_STRONG
            )
            
            return when {
                authenticators == BiometricManager.BIOMETRIC_SUCCESS -> {
                    // На Android 11+ можно определить точнее
                    BiometricType.MULTIPLE
                }
                else -> BiometricType.NONE
            }
        }
        
        // Для старых версий предполагаем fingerprint
        return if (checkBiometricAvailability() is BiometricResult.Success) {
            BiometricType.FINGERPRINT
        } else {
            BiometricType.NONE
        }
    }
    
    /**
     * Показать биометрический промпт
     */
    suspend fun authenticate(
        activity: FragmentActivity,
        title: String = "Biometric Authentication",
        subtitle: String = "Authenticate to access Enliko Trading",
        negativeButtonText: String = "Cancel"
    ): BiometricResult = suspendCancellableCoroutine { continuation ->
        
        val executor = ContextCompat.getMainExecutor(context)
        
        val callback = object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                super.onAuthenticationSucceeded(result)
                _state.value = _state.value.copy(lastAuthTime = System.currentTimeMillis())
                continuation.resume(BiometricResult.Success)
            }
            
            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                super.onAuthenticationError(errorCode, errString)
                val result = when (errorCode) {
                    BiometricPrompt.ERROR_USER_CANCELED,
                    BiometricPrompt.ERROR_NEGATIVE_BUTTON,
                    BiometricPrompt.ERROR_CANCELED -> BiometricResult.Canceled
                    BiometricPrompt.ERROR_NO_BIOMETRICS -> BiometricResult.NotEnrolled
                    BiometricPrompt.ERROR_HW_NOT_PRESENT,
                    BiometricPrompt.ERROR_HW_UNAVAILABLE -> BiometricResult.HardwareUnavailable
                    else -> BiometricResult.Error(errorCode, errString.toString())
                }
                continuation.resume(result)
            }
            
            override fun onAuthenticationFailed() {
                super.onAuthenticationFailed()
                // Не вызываем resume - пользователь может попробовать снова
            }
        }
        
        val biometricPrompt = BiometricPrompt(activity, executor, callback)
        
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setNegativeButtonText(negativeButtonText)
            .setConfirmationRequired(false)
            .build()
        
        biometricPrompt.authenticate(promptInfo)
        
        continuation.invokeOnCancellation {
            biometricPrompt.cancelAuthentication()
        }
    }
    
    /**
     * Аутентификация с криптографией (более безопасная)
     */
    suspend fun authenticateWithCrypto(
        activity: FragmentActivity,
        title: String = "Secure Authentication",
        subtitle: String = "Authenticate to decrypt your data"
    ): BiometricResult = suspendCancellableCoroutine { continuation ->
        
        try {
            val cipher = getCipher()
            val secretKey = getOrCreateSecretKey()
            cipher.init(Cipher.ENCRYPT_MODE, secretKey)
            
            val executor = ContextCompat.getMainExecutor(context)
            
            val callback = object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    // Можно использовать result.cryptoObject?.cipher для шифрования
                    _state.value = _state.value.copy(lastAuthTime = System.currentTimeMillis())
                    continuation.resume(BiometricResult.Success)
                }
                
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    continuation.resume(BiometricResult.Error(errorCode, errString.toString()))
                }
            }
            
            val biometricPrompt = BiometricPrompt(activity, executor, callback)
            
            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle(title)
                .setSubtitle(subtitle)
                .setNegativeButtonText("Use Password")
                .build()
            
            biometricPrompt.authenticate(
                promptInfo,
                BiometricPrompt.CryptoObject(cipher)
            )
            
            continuation.invokeOnCancellation {
                biometricPrompt.cancelAuthentication()
            }
            
        } catch (e: Exception) {
            continuation.resumeWithException(e)
        }
    }
    
    /**
     * Проверить нужна ли повторная аутентификация
     */
    fun needsReauthentication(): Boolean {
        val lastAuth = _state.value.lastAuthTime
        if (lastAuth == 0L) return true
        return (System.currentTimeMillis() - lastAuth) > BIOMETRIC_AUTH_TIMEOUT_MS
    }
    
    /**
     * Включить/выключить биометрию для приложения
     */
    fun setBiometricEnabled(enabled: Boolean) {
        _state.value = _state.value.copy(isEnabled = enabled)
    }
    
    // =========================================================================
    // Private Crypto Methods
    // =========================================================================
    
    private fun getCipher(): Cipher {
        return Cipher.getInstance(
            "${KeyProperties.KEY_ALGORITHM_AES}/" +
            "${KeyProperties.BLOCK_MODE_CBC}/" +
            KeyProperties.ENCRYPTION_PADDING_PKCS7
        )
    }
    
    private fun getOrCreateSecretKey(): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)
        
        keyStore.getKey(KEY_NAME, null)?.let { return it as SecretKey }
        
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            ANDROID_KEYSTORE
        )
        
        val keyGenSpec = KeyGenParameterSpec.Builder(
            KEY_NAME,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            .apply {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    setUserAuthenticationParameters(
                        0, // Требует аутентификации при каждом использовании
                        KeyProperties.AUTH_BIOMETRIC_STRONG
                    )
                } else {
                    @Suppress("DEPRECATION")
                    setUserAuthenticationValidityDurationSeconds(-1)
                }
            }
            .setInvalidatedByBiometricEnrollment(true)
            .build()
        
        keyGenerator.init(keyGenSpec)
        return keyGenerator.generateKey()
    }
}

// =============================================================================
// COMPOSABLE HELPERS
// =============================================================================

/**
 * Composable для получения BiometricAuthManager
 */
@androidx.compose.runtime.Composable
fun rememberBiometricAuthManager(): BiometricAuthManager {
    val context = androidx.compose.ui.platform.LocalContext.current
    return androidx.compose.runtime.remember { BiometricAuthManager(context) }
}

/**
 * Текстовое описание типа биометрии
 */
fun BiometricType.getDisplayName(): String = when (this) {
    BiometricType.NONE -> "Not Available"
    BiometricType.FINGERPRINT -> "Fingerprint"
    BiometricType.FACE -> "Face ID"
    BiometricType.IRIS -> "Iris"
    BiometricType.MULTIPLE -> "Biometrics"
}

/**
 * Иконка для типа биометрии (Material Icons)
 */
fun BiometricType.getIconName(): String = when (this) {
    BiometricType.NONE -> "block"
    BiometricType.FINGERPRINT -> "fingerprint"
    BiometricType.FACE -> "face"
    BiometricType.IRIS -> "visibility"
    BiometricType.MULTIPLE -> "security"
}
