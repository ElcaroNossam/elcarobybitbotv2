//
//  AuthModels.swift
//  EnlikoTrading
//

import Foundation

// MARK: - Auth Request Models
struct TelegramAuthRequest: Codable {
    let initData: String
    
    enum CodingKeys: String, CodingKey {
        case initData = "init_data"
    }
}

struct EmailLoginRequest: Codable {
    let email: String
    let password: String
}

struct EmailRegisterRequest: Codable {
    let email: String
    let password: String
    let firstName: String?
    let lastName: String?
    let telegramUsername: String?  // Optional: user can enter their Telegram @username
    
    enum CodingKeys: String, CodingKey {
        case email
        case password
        case firstName = "first_name"
        case lastName = "last_name"
        case telegramUsername = "telegram_username"
    }
}

struct EmailVerifyRequest: Codable {
    let email: String
    let code: String
}

struct RefreshTokenRequest: Codable {
    let refreshToken: String
    
    enum CodingKeys: String, CodingKey {
        case refreshToken = "refresh_token"
    }
}

// MARK: - Auth Response Models
struct AuthResponse: Codable {
    let success: Bool
    let token: String?
    let refreshToken: String?
    let userId: Int?
    let user: User?
    let error: String?
    let message: String?
    
    enum CodingKeys: String, CodingKey {
        case success
        case token
        case refreshToken = "refresh_token"
        case userId = "user_id"
        case user
        case error
        case message
    }
}

struct TokenPayload: Codable {
    let userId: Int
    let exp: Int
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case exp
    }
}

// MARK: - User Response Wrapper
// Server returns {"user": {...}} not just User object
struct UserResponse: Codable {
    let user: User
}
