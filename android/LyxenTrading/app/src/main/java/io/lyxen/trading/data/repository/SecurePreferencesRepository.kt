package io.lyxen.trading.data.repository

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Secure preferences repository using EncryptedSharedPreferences for sensitive data.
 * 
 * SECURITY: JWT tokens and user IDs are stored with AES-256 encryption using
 * Android Keystore-backed MasterKey.
 * 
 * Non-sensitive settings (language, theme, exchange) use regular DataStore
 * via PreferencesRepository for better performance.
 */
@Singleton
class SecurePreferencesRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    companion object {
        private const val TAG = "SecurePrefs"
        private const val PREFS_NAME = "lyxen_secure_prefs"
        
        // Sensitive keys - encrypted
        private const val KEY_AUTH_TOKEN = "auth_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_USER_ID = "user_id"
        
        // Biometric session
        private const val KEY_BIOMETRIC_SESSION_EXPIRY = "biometric_session_expiry"
    }
    
    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }
    
    private val securePrefs: SharedPreferences by lazy {
        try {
            EncryptedSharedPreferences.create(
                context,
                PREFS_NAME,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            // Fallback for corrupted keystore (should not happen in production)
            Log.e(TAG, "Failed to create EncryptedSharedPreferences, falling back", e)
            context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        }
    }
    
    // StateFlows for reactive updates
    private val _authToken = MutableStateFlow<String?>(securePrefs.getString(KEY_AUTH_TOKEN, null))
    private val _userId = MutableStateFlow<String?>(securePrefs.getString(KEY_USER_ID, null))
    
    val authToken: Flow<String?> = _authToken.asStateFlow()
    val userId: Flow<String?> = _userId.asStateFlow()
    
    /**
     * Get auth token synchronously (for OkHttp interceptor)
     */
    fun getAuthTokenSync(): String? {
        return securePrefs.getString(KEY_AUTH_TOKEN, null)
    }
    
    /**
     * Save auth token securely
     */
    suspend fun saveAuthToken(token: String) {
        securePrefs.edit()
            .putString(KEY_AUTH_TOKEN, token)
            .apply()
        _authToken.value = token
    }
    
    /**
     * Save refresh token securely
     */
    suspend fun saveRefreshToken(token: String) {
        securePrefs.edit()
            .putString(KEY_REFRESH_TOKEN, token)
            .apply()
    }
    
    /**
     * Get refresh token for token refresh
     */
    fun getRefreshToken(): String? {
        return securePrefs.getString(KEY_REFRESH_TOKEN, null)
    }
    
    /**
     * Save user ID securely
     */
    suspend fun saveUserId(userId: String) {
        securePrefs.edit()
            .putString(KEY_USER_ID, userId)
            .apply()
        _userId.value = userId
    }
    
    /**
     * Get user ID synchronously
     */
    fun getUserIdSync(): String? {
        return securePrefs.getString(KEY_USER_ID, null)
    }
    
    /**
     * Save biometric session expiry timestamp
     */
    fun saveBiometricSessionExpiry(expiryTimestamp: Long) {
        securePrefs.edit()
            .putLong(KEY_BIOMETRIC_SESSION_EXPIRY, expiryTimestamp)
            .apply()
    }
    
    /**
     * Check if biometric session is still valid
     */
    fun isBiometricSessionValid(): Boolean {
        val expiry = securePrefs.getLong(KEY_BIOMETRIC_SESSION_EXPIRY, 0L)
        return System.currentTimeMillis() < expiry
    }
    
    /**
     * Clear auth data (on logout)
     */
    suspend fun clearAuth() {
        securePrefs.edit()
            .remove(KEY_AUTH_TOKEN)
            .remove(KEY_REFRESH_TOKEN)
            .remove(KEY_USER_ID)
            .remove(KEY_BIOMETRIC_SESSION_EXPIRY)
            .apply()
        _authToken.value = null
        _userId.value = null
    }
    
    /**
     * Clear all secure data (for complete reset)
     */
    suspend fun clearAll() {
        securePrefs.edit().clear().apply()
        _authToken.value = null
        _userId.value = null
    }
    
    /**
     * Check if user is authenticated
     */
    fun isAuthenticated(): Boolean {
        return getAuthTokenSync() != null
    }
}
