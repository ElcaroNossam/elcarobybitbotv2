//
//  AuthManager.swift
//  EnlikoTrading
//
//  Authentication management with Telegram and Email support
//

import Foundation
import Combine
import SwiftUI

class AuthManager: ObservableObject {
    static let shared = AuthManager()
    
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let network = NetworkService.shared
    private let logger = AppLogger.shared
    
    private init() {
        logger.info("AuthManager initialized", category: .auth)
    }
    
    // MARK: - Check Auth Status
    func checkAuthStatus() {
        logger.debug("Checking auth status, isAuthenticated: \(network.isAuthenticated)", category: .auth)
        if network.isAuthenticated {
            Task {
                await fetchCurrentUser()
            }
        }
    }
    
    // MARK: - Email Authentication
    func loginWithEmail(email: String, password: String) async -> Bool {
        logger.logAuthAttempt("email: \(email)")
        await MainActor.run { isLoading = true }
        defer { Task { @MainActor in isLoading = false } }
        
        do {
            let request = EmailLoginRequest(email: email, password: password)
            let response: AuthResponse = try await network.request(
                endpoint: Config.Endpoints.loginEmail,
                method: .post,
                body: request,
                authenticated: false
            )
            
            if response.success, let token = response.token, let refresh = response.refreshToken {
                network.setTokens(auth: token, refresh: refresh)
                
                if let userId = response.userId {
                    KeychainHelper.shared.save(key: Config.userIdKey, value: String(userId))
                    logger.debug("Saved userId: \(userId)", category: .auth)
                }
                
                logger.logAuthSuccess("email", userId: response.userId)
                await fetchCurrentUser()
                return true
            } else {
                let error = response.error ?? "Login failed"
                logger.logAuthFailure("email", reason: error)
                await MainActor.run {
                    errorMessage = error
                }
                return false
            }
        } catch {
            logger.logAuthFailure("email", reason: error.localizedDescription)
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    func registerWithEmail(email: String, password: String, firstName: String?, lastName: String?, telegramUsername: String? = nil) async -> Bool {
        logger.info("Registering with email: \(email)", category: .auth)
        await MainActor.run { isLoading = true }
        defer { Task { @MainActor in isLoading = false } }
        
        do {
            let request = EmailRegisterRequest(
                email: email,
                password: password,
                firstName: firstName,
                lastName: lastName,
                telegramUsername: telegramUsername
            )
            
            let response: AuthResponse = try await network.request(
                endpoint: Config.Endpoints.register,
                method: .post,
                body: request,
                authenticated: false
            )
            
            if response.success {
                logger.info("Registration successful for: \(email)", category: .auth)
                return true
            } else {
                let error = response.error ?? "Registration failed"
                logger.warning("Registration failed: \(error)", category: .auth)
                await MainActor.run {
                    errorMessage = error
                }
                return false
            }
        } catch {
            logger.error("Registration error: \(error)", category: .auth)
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    func verifyEmail(email: String, code: String) async -> Bool {
        logger.info("Verifying email: \(email) with code", category: .auth)
        await MainActor.run { isLoading = true }
        defer { Task { @MainActor in isLoading = false } }
        
        do {
            let request = EmailVerifyRequest(email: email, code: code)
            let response: AuthResponse = try await network.request(
                endpoint: Config.Endpoints.verify,
                method: .post,
                body: request,
                authenticated: false
            )
            
            if response.success, let token = response.token, let refresh = response.refreshToken {
                network.setTokens(auth: token, refresh: refresh)
                logger.info("Email verified successfully", category: .auth)
                await fetchCurrentUser()
                return true
            } else {
                let error = response.error ?? "Verification failed"
                logger.warning("Verification failed: \(error)", category: .auth)
                await MainActor.run {
                    errorMessage = error
                }
                return false
            }
        } catch {
            logger.error("Verification error: \(error)", category: .auth)
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    // MARK: - Telegram Authentication
    func loginWithTelegram(initData: String) async -> Bool {
        logger.logAuthAttempt("telegram")
        await MainActor.run { isLoading = true }
        defer { Task { @MainActor in isLoading = false } }
        
        do {
            let request = TelegramAuthRequest(initData: initData)
            let response: AuthResponse = try await network.request(
                endpoint: Config.Endpoints.login,
                method: .post,
                body: request,
                authenticated: false
            )
            
            if response.success, let token = response.token, let refresh = response.refreshToken {
                network.setTokens(auth: token, refresh: refresh)
                
                if let userId = response.userId {
                    KeychainHelper.shared.save(key: Config.userIdKey, value: String(userId))
                }
                
                logger.logAuthSuccess("telegram", userId: response.userId)
                await fetchCurrentUser()
                return true
            } else {
                let error = response.error ?? "Telegram login failed"
                logger.logAuthFailure("telegram", reason: error)
                await MainActor.run {
                    errorMessage = error
                }
                return false
            }
        } catch {
            logger.logAuthFailure("telegram", reason: error.localizedDescription)
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    // MARK: - Telegram Deep Link Login
    /// Login via deep link from Telegram bot (/app_login command)
    /// URL format: enliko://login?token=XXX&tid=12345
    func loginWithDeepLink(token: String, telegramId: Int) async -> Bool {
        logger.logAuthAttempt("deep_link: tid:\(telegramId)")
        await MainActor.run { isLoading = true }
        defer { Task { @MainActor in isLoading = false } }
        
        do {
            struct DeepLinkRequest: Encodable {
                let token: String
                let telegram_id: Int
            }
            
            let request = DeepLinkRequest(token: token, telegram_id: telegramId)
            let response: AuthResponse = try await network.request(
                endpoint: "/auth/telegram/deep-link",
                method: .post,
                body: request,
                authenticated: false
            )
            
            if response.success, let authToken = response.token, let refresh = response.refreshToken {
                network.setTokens(auth: authToken, refresh: refresh)
                
                if let userId = response.userId {
                    KeychainHelper.shared.save(key: Config.userIdKey, value: String(userId))
                }
                
                logger.logAuthSuccess("deep_link", userId: response.userId)
                await fetchCurrentUser()
                return true
            } else {
                let error = response.error ?? "Deep link login failed"
                logger.logAuthFailure("deep_link", reason: error)
                await MainActor.run {
                    errorMessage = error
                }
                return false
            }
        } catch {
            logger.logAuthFailure("deep_link", reason: error.localizedDescription)
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    // MARK: - Handle URL (for deep links)
    /// Call from App's onOpenURL handler
    func handleURL(_ url: URL) {
        logger.info("Handling deep link URL: \(url)", category: .auth)
        
        // Handle enliko://login?token=XXX&tid=12345
        guard url.scheme == "enliko",
              url.host == "login",
              let components = URLComponents(url: url, resolvingAgainstBaseURL: true),
              let token = components.queryItems?.first(where: { $0.name == "token" })?.value,
              let tidString = components.queryItems?.first(where: { $0.name == "tid" })?.value,
              let tid = Int(tidString)
        else {
            logger.warning("Invalid deep link URL: \(url)", category: .auth)
            return
        }
        
        logger.debug("Deep link parsed: tid=\(tid)", category: .auth)
        
        // Perform login
        Task {
            let success = await loginWithDeepLink(token: token, telegramId: tid)
            if !success {
                logger.error("Deep link login failed for tid=\(tid)", category: .auth)
            }
        }
    }
    
    // MARK: - Demo Login (for testing)
    func loginAsDemo(userId: Int) async -> Bool {
        logger.logAuthAttempt("demo: userId:\(userId)")
        await MainActor.run { isLoading = true }
        defer { Task { @MainActor in isLoading = false } }
        
        // In production, this should go through proper auth
        KeychainHelper.shared.save(key: Config.userIdKey, value: String(userId))
        
        // Try to fetch user - this will work if server allows demo access
        await fetchCurrentUser()
        
        if isAuthenticated {
            logger.logAuthSuccess("demo", userId: userId)
        } else {
            logger.logAuthFailure("demo", reason: "Demo login not allowed")
        }
        return isAuthenticated
    }
    
    // MARK: - Fetch Current User
    @MainActor
    func fetchCurrentUser() async {
        logger.debug("Fetching current user", category: .auth)
        
        do {
            // Server returns {"user": {...}} so we use UserResponse wrapper
            let response: UserResponse = try await network.get(Config.Endpoints.me)
            currentUser = response.user
            isAuthenticated = true
            
            logger.info("User fetched: \(response.user.email ?? "unknown")", category: .auth)
            
            // Update app state from user data
            if let exchangeRaw = response.user.exchangeType, let exchange = Exchange(rawValue: exchangeRaw) {
                AppState.shared.currentExchange = exchange
                logger.debug("Exchange set to: \(exchangeRaw)", category: .auth)
            }
            
            // Sync full settings from server (trading mode, account type, etc.)
            await AppState.shared.syncFromServer()
            
            // Connect to WebSockets (market data + settings sync)
            WebSocketService.shared.connectAll()
            
            // Initialize push notifications
            Task {
                // Request permission and register device
                let granted = await PushNotificationService.shared.requestPermission()
                if granted {
                    logger.info("Push notifications enabled", category: .auth)
                }
                
                // Connect WebSocket for real-time notifications
                await PushNotificationService.shared.connectWebSocket()
                
                // Load notification preferences
                await PushNotificationService.shared.loadPreferences()
                
                // Load initial notifications
                await PushNotificationService.shared.loadNotifications()
            }
            
        } catch {
            logger.error("Failed to fetch user: \(error)", category: .auth)
            // Don't logout on network errors - only on 401
            if case NetworkError.unauthorized = error {
                logger.warning("Unauthorized - logging out", category: .auth)
                logout()
            }
        }
    }
    
    // MARK: - Logout
    func logout() {
        logger.info("Logging out user", category: .auth)
        network.clearTokens()
        
        // Disconnect WebSockets
        WebSocketService.shared.disconnectAll()
        
        // Disconnect push notification WebSocket and unregister device
        Task {
            await PushNotificationService.shared.unregisterDevice()
            PushNotificationService.shared.disconnectWebSocket()
        }
        
        DispatchQueue.main.async {
            self.isAuthenticated = false
            self.currentUser = nil
        }
        logger.debug("Logout complete", category: .auth)
    }
    
    // MARK: - Clear Error
    func clearError() {
        errorMessage = nil
    }
    
    // MARK: - Handle Successful 2FA Login
    /// Called when 2FA polling returns approved status
    func handleSuccessfulLogin(token: String, refreshToken: String?, user: User) {
        logger.logAuthSuccess("2fa_telegram", userId: user.userId)
        
        // Save tokens (use empty string if no refresh token)
        network.setTokens(auth: token, refresh: refreshToken ?? "")
        
        // Save userId
        if let userId = user.userId {
            KeychainHelper.shared.save(key: Config.userIdKey, value: String(userId))
        }
        
        // Update state
        currentUser = user
        isAuthenticated = true
        
        // Update app state from user data
        if let exchangeRaw = user.exchangeType, let exchange = Exchange(rawValue: exchangeRaw) {
            AppState.shared.currentExchange = exchange
            logger.debug("Exchange set to: \(exchangeRaw)", category: .auth)
        }
        
        // Sync full settings from server
        Task {
            await AppState.shared.syncFromServer()
        }
        
        // Connect to WebSockets
        WebSocketService.shared.connectAll()
        
        logger.info("2FA login successful for: \(user.email ?? user.username ?? "unknown")", category: .auth)
    }
}
