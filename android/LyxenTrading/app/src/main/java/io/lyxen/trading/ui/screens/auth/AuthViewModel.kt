package io.lyxen.trading.ui.screens.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.lyxen.trading.data.api.LyxenApi
import io.lyxen.trading.data.models.LoginRequest
import io.lyxen.trading.data.models.RegisterRequest
import io.lyxen.trading.data.repository.PreferencesRepository
import io.lyxen.trading.data.repository.SecurePreferencesRepository
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
    val isSuccess: Boolean = false
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val api: LyxenApi,
    private val preferencesRepository: PreferencesRepository,
    private val securePreferencesRepository: SecurePreferencesRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

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
                        // Store sensitive data in encrypted storage
                        securePreferencesRepository.saveAuthToken(authResponse.token)
                        securePreferencesRepository.saveUserId(authResponse.user.userId.toString())
                        // Store non-sensitive data in regular preferences
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

    fun register(email: String, password: String, username: String? = null) {
        viewModelScope.launch {
            _uiState.value = AuthUiState(isLoading = true)
            try {
                val response = api.register(RegisterRequest(email, password, username))
                if (response.isSuccessful) {
                    response.body()?.let { authResponse ->
                        // Store sensitive data in encrypted storage
                        securePreferencesRepository.saveAuthToken(authResponse.token)
                        securePreferencesRepository.saveUserId(authResponse.user.userId.toString())
                        _uiState.value = AuthUiState(isSuccess = true)
                    } ?: run {
                        _uiState.value = AuthUiState(error = "Invalid response")
                    }
                } else {
                    _uiState.value = AuthUiState(error = "Registration failed: ${response.code()}")
                }
            } catch (e: Exception) {
                _uiState.value = AuthUiState(error = e.message ?: "Unknown error")
            }
        }
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
}
