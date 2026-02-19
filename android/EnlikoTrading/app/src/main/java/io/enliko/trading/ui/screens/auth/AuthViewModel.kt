package io.enliko.trading.ui.screens.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.models.LoginRequest
import io.enliko.trading.data.models.RegisterRequest
import io.enliko.trading.data.models.Request2FABody
import io.enliko.trading.data.models.VerifyRequest
import io.enliko.trading.data.repository.PreferencesRepository
import io.enliko.trading.data.repository.SecurePreferencesRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val isSuccess: Boolean = false,
    // Email verification state
    val isWaitingForEmailVerification: Boolean = false,
    val pendingEmail: String? = null,
    // 2FA state
    val isWaitingFor2FA: Boolean = false,
    val twoFARequestId: String? = null,
    val twoFACountdown: Int = 300,
    val twoFAStatus: String? = null, // "pending", "approved", "denied", "expired"
    val twoFAMessage: String? = null
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val preferencesRepository: PreferencesRepository,
    private val securePreferencesRepository: SecurePreferencesRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    private var pollingJob: Job? = null
    private var countdownJob: Job? = null

    val isLoggedIn: StateFlow<Boolean> = securePreferencesRepository.authToken
        .map { it != null }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), false)

    val currentLanguage: StateFlow<String> = preferencesRepository.language
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), "en")

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _uiState.value = AuthUiState(isLoading = true)
            try {
                val response = api.login(LoginRequest(email, password))
                if (response.isSuccessful) {
                    response.body()?.let { authResponse ->
                        securePreferencesRepository.saveAuthToken(authResponse.token)
                        securePreferencesRepository.saveUserId(authResponse.user.userId.toString())
                        preferencesRepository.saveLanguage(authResponse.user.lang)
                        _uiState.value = AuthUiState(isSuccess = true)
                    } ?: run {
                        _uiState.value = AuthUiState(error = "Invalid response")
                    }
                } else {
                    _uiState.value = AuthUiState(error = "Login failed: ${response.code()}")
                }
            } catch (e: Exception) {
                _uiState.value = AuthUiState(error = e.message ?: "Unknown error")
            }
        }
    }

    fun register(email: String, password: String, name: String? = null) {
        viewModelScope.launch {
            _uiState.value = AuthUiState(isLoading = true)
            try {
                val response = api.register(RegisterRequest(email, password, name))
                if (response.isSuccessful) {
                    response.body()?.let { registerResponse ->
                        if (registerResponse.success) {
                            // Show verification code input
                            _uiState.value = AuthUiState(
                                isWaitingForEmailVerification = true,
                                pendingEmail = email
                            )
                        } else {
                            _uiState.value = AuthUiState(error = registerResponse.message ?: "Registration failed")
                        }
                    } ?: run {
                        _uiState.value = AuthUiState(error = "Invalid response")
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMsg = when {
                        response.code() == 400 && errorBody?.contains("already registered") == true -> 
                            "This email is already registered"
                        response.code() == 422 -> "Password must be at least 8 characters with letters and numbers"
                        else -> "Registration failed: ${response.code()}"
                    }
                    _uiState.value = AuthUiState(error = errorMsg)
                }
            } catch (e: Exception) {
                _uiState.value = AuthUiState(error = e.message ?: "Unknown error")
            }
        }
    }

    fun verifyEmail(code: String) {
        val email = _uiState.value.pendingEmail
        if (email.isNullOrBlank()) {
            _uiState.value = _uiState.value.copy(error = "No email to verify. Please register again.")
            return
        }
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            try {
                val response = api.verify(VerifyRequest(email, code))
                if (response.isSuccessful) {
                    response.body()?.let { authResponse ->
                        securePreferencesRepository.saveAuthToken(authResponse.token)
                        securePreferencesRepository.saveUserId(authResponse.user.userId.toString())
                        preferencesRepository.saveLanguage(authResponse.user.lang)
                        _uiState.value = AuthUiState(isSuccess = true)
                    } ?: run {
                        _uiState.value = _uiState.value.copy(isLoading = false, error = "Empty response from server")
                    }
                } else {
                    val errorBody = response.errorBody()?.string() ?: ""
                    val errorMsg = when (response.code()) {
                        400 -> if (errorBody.contains("expired")) "Code expired. Please register again." 
                               else "Invalid verification code"
                        404 -> "No pending registration. Please register again."
                        else -> "Server error: ${response.code()}"
                    }
                    _uiState.value = _uiState.value.copy(isLoading = false, error = errorMsg)
                }
            } catch (e: Exception) {
                val errorDetail = when {
                    e.message?.contains("JsonDecodingException") == true -> "Server response format error"
                    e.message?.contains("Unable to resolve") == true -> "No internet connection"
                    e.message?.contains("timeout") == true -> "Connection timeout"
                    else -> e.message ?: "Unknown error"
                }
                _uiState.value = _uiState.value.copy(isLoading = false, error = errorDetail)
            }
        }
    }

    fun cancelEmailVerification() {
        _uiState.value = AuthUiState()
    }

    // ==================== 2FA (Telegram Login) ====================

    fun request2FALogin(username: String) {
        val cleaned = username.trim().removePrefix("@")
        if (cleaned.isBlank()) {
            _uiState.value = _uiState.value.copy(error = "Enter your Telegram username")
            return
        }

        viewModelScope.launch {
            _uiState.value = AuthUiState(isLoading = true)
            try {
                val response = api.request2FA(Request2FABody(cleaned))
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body?.success == true && body.requestId != null) {
                        _uiState.value = AuthUiState(
                            isWaitingFor2FA = true,
                            twoFARequestId = body.requestId,
                            twoFACountdown = 300,
                            twoFAStatus = "pending",
                            twoFAMessage = body.message
                        )
                        startPolling(body.requestId)
                        startCountdown()
                    } else {
                        _uiState.value = AuthUiState(
                            error = body?.message ?: "User not found. Make sure you use @enliko_bot first."
                        )
                    }
                } else {
                    val errorMsg = when (response.code()) {
                        404 -> "User not found. Start @enliko_bot in Telegram first."
                        429 -> "Too many requests. Please wait."
                        else -> "Request failed: ${response.code()}"
                    }
                    _uiState.value = AuthUiState(error = errorMsg)
                }
            } catch (e: Exception) {
                _uiState.value = AuthUiState(error = e.message ?: "Connection error")
            }
        }
    }

    private fun startPolling(requestId: String) {
        pollingJob?.cancel()
        pollingJob = viewModelScope.launch {
            while (true) {
                delay(2500)
                try {
                    val response = api.check2FA(requestId)
                    if (response.isSuccessful) {
                        val body = response.body() ?: continue
                        when (body.status) {
                            "approved" -> {
                                stopPolling()
                                val token = body.token
                                val user = body.user
                                if (token != null && user != null) {
                                    securePreferencesRepository.saveAuthToken(token)
                                    securePreferencesRepository.saveUserId(user.userId.toString())
                                    body.refreshToken?.let {
                                        securePreferencesRepository.saveRefreshToken(it)
                                    }
                                    preferencesRepository.saveLanguage(user.lang)
                                    _uiState.value = AuthUiState(
                                        isSuccess = true,
                                        twoFAStatus = "approved"
                                    )
                                } else {
                                    _uiState.value = AuthUiState(error = "Approved but no token received")
                                }
                                return@launch
                            }
                            "denied" -> {
                                stopPolling()
                                _uiState.value = AuthUiState(
                                    twoFAStatus = "denied",
                                    error = "Login denied in Telegram"
                                )
                                return@launch
                            }
                            "expired" -> {
                                stopPolling()
                                _uiState.value = AuthUiState(
                                    twoFAStatus = "expired",
                                    error = "Request expired. Try again."
                                )
                                return@launch
                            }
                            // "pending" → continue polling
                        }
                    }
                } catch (_: Exception) {
                    // Network error during poll — continue trying
                }
            }
        }
    }

    private fun startCountdown() {
        countdownJob?.cancel()
        countdownJob = viewModelScope.launch {
            var remaining = 300
            while (remaining > 0) {
                delay(1000)
                remaining--
                if (_uiState.value.isWaitingFor2FA) {
                    _uiState.value = _uiState.value.copy(twoFACountdown = remaining)
                } else {
                    return@launch
                }
            }
            // Expired
            stopPolling()
            _uiState.value = AuthUiState(
                twoFAStatus = "expired",
                error = "Request expired. Try again."
            )
        }
    }

    fun cancel2FA() {
        stopPolling()
        _uiState.value = AuthUiState()
    }

    private fun stopPolling() {
        pollingJob?.cancel()
        pollingJob = null
        countdownJob?.cancel()
        countdownJob = null
    }

    fun logout() {
        viewModelScope.launch {
            securePreferencesRepository.clearAuth()
            preferencesRepository.clearAuth()
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }

    override fun onCleared() {
        super.onCleared()
        stopPolling()
    }
}
