//
//  AuthManager.swift
//  LyxenTrading
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
    
    private init() {}
    
    // MARK: - Check Auth Status
    func checkAuthStatus() {
        if network.isAuthenticated {
            Task {
                await fetchCurrentUser()
            }
        }
    }
    
    // MARK: - Email Authentication
    func loginWithEmail(email: String, password: String) async -> Bool {
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
                }
                
                await fetchCurrentUser()
                return true
            } else {
                await MainActor.run {
                    errorMessage = response.error ?? "Login failed"
                }
                return false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    func registerWithEmail(email: String, password: String, firstName: String?, lastName: String?) async -> Bool {
        await MainActor.run { isLoading = true }
        defer { Task { @MainActor in isLoading = false } }
        
        do {
            let request = EmailRegisterRequest(
                email: email,
                password: password,
                firstName: firstName,
                lastName: lastName
            )
            
            let response: AuthResponse = try await network.request(
                endpoint: Config.Endpoints.register,
                method: .post,
                body: request,
                authenticated: false
            )
            
            if response.success {
                return true
            } else {
                await MainActor.run {
                    errorMessage = response.error ?? "Registration failed"
                }
                return false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    func verifyEmail(email: String, code: String) async -> Bool {
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
                await fetchCurrentUser()
                return true
            } else {
                await MainActor.run {
                    errorMessage = response.error ?? "Verification failed"
                }
                return false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    // MARK: - Telegram Authentication
    func loginWithTelegram(initData: String) async -> Bool {
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
                
                await fetchCurrentUser()
                return true
            } else {
                await MainActor.run {
                    errorMessage = response.error ?? "Telegram login failed"
                }
                return false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
            }
            return false
        }
    }
    
    // MARK: - Demo Login (for testing)
    func loginAsDemo(userId: Int) async -> Bool {
        // For development/testing - simulate login
        await MainActor.run { isLoading = true }
        defer { Task { @MainActor in isLoading = false } }
        
        // In production, this should go through proper auth
        // For now, we'll try to get user data with the userId
        KeychainHelper.shared.save(key: Config.userIdKey, value: String(userId))
        
        // Try to fetch user - this will work if server allows demo access
        await fetchCurrentUser()
        return isAuthenticated
    }
    
    // MARK: - Fetch Current User
    @MainActor
    func fetchCurrentUser() async {
        do {
            let user: User = try await network.get(Config.Endpoints.me)
            currentUser = user
            isAuthenticated = true
            
            // Update app state from user data
            if let exchangeRaw = user.exchangeType, let exchange = Exchange(rawValue: exchangeRaw) {
                AppState.shared.currentExchange = exchange
            }
            
            // Sync full settings from server (trading mode, account type, etc.)
            await AppState.shared.syncFromServer()
            
            // Connect to WebSockets (market data + settings sync)
            WebSocketService.shared.connectAll()
            
        } catch {
            print("Failed to fetch user: \(error)")
            // Don't logout on network errors - only on 401
            if case NetworkError.unauthorized = error {
                logout()
            }
        }
    }
    
    // MARK: - Logout
    func logout() {
        network.clearTokens()
        
        // Disconnect WebSockets
        WebSocketService.shared.disconnectAll()
        
        DispatchQueue.main.async {
            self.isAuthenticated = false
            self.currentUser = nil
        }
    }
    
    // MARK: - Clear Error
    func clearError() {
        errorMessage = nil
    }
}
