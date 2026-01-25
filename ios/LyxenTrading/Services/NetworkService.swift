//
//  NetworkService.swift
//  LyxenTrading
//
//  Core networking layer with JWT authentication
//

import Foundation
import Combine

// MARK: - Network Error
enum NetworkError: LocalizedError {
    case invalidURL
    case noData
    case decodingError(Error)
    case serverError(Int, String?)
    case unauthorized
    case networkError(Error)
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .noData:
            return "No data received"
        case .decodingError(let error):
            return "Decoding error: \(error.localizedDescription)"
        case .serverError(let code, let message):
            return message ?? "Server error: \(code)"
        case .unauthorized:
            return "Session expired. Please login again."
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .unknown:
            return "Unknown error occurred"
        }
    }
}

// MARK: - HTTP Method
enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
    case patch = "PATCH"
}

// MARK: - Network Service
class NetworkService {
    static let shared = NetworkService()
    
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = Config.requestTimeout
        config.timeoutIntervalForResource = Config.requestTimeout * 2
        
        self.session = URLSession(configuration: config)
        
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .useDefaultKeys
        
        self.encoder = JSONEncoder()
        self.encoder.keyEncodingStrategy = .useDefaultKeys
    }
    
    // MARK: - Token Management
    private var authToken: String? {
        get { KeychainHelper.shared.read(key: Config.tokenKey) }
        set {
            if let token = newValue {
                KeychainHelper.shared.save(key: Config.tokenKey, value: token)
            } else {
                KeychainHelper.shared.delete(key: Config.tokenKey)
            }
        }
    }
    
    private var refreshToken: String? {
        get { KeychainHelper.shared.read(key: Config.refreshTokenKey) }
        set {
            if let token = newValue {
                KeychainHelper.shared.save(key: Config.refreshTokenKey, value: token)
            } else {
                KeychainHelper.shared.delete(key: Config.refreshTokenKey)
            }
        }
    }
    
    func setTokens(auth: String, refresh: String) {
        authToken = auth
        refreshToken = refresh
    }
    
    func clearTokens() {
        authToken = nil
        refreshToken = nil
        KeychainHelper.shared.delete(key: Config.userIdKey)
    }
    
    var isAuthenticated: Bool {
        authToken != nil
    }
    
    // MARK: - Request Building
    private func buildRequest(
        endpoint: String,
        method: HTTPMethod,
        body: Encodable? = nil,
        queryParams: [String: String]? = nil,
        authenticated: Bool = true
    ) throws -> URLRequest {
        var urlString = Config.apiURL + endpoint
        
        // Add query parameters
        if let params = queryParams, !params.isEmpty {
            let queryString = params.map { "\($0.key)=\($0.value)" }.joined(separator: "&")
            urlString += "?\(queryString)"
        }
        
        guard let url = URL(string: urlString) else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("LyxenTrading-iOS/1.0", forHTTPHeaderField: "User-Agent")
        
        // Add auth header
        if authenticated, let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Add body
        if let body = body {
            request.httpBody = try encoder.encode(body)
        }
        
        return request
    }
    
    // MARK: - Generic Request
    func request<T: Codable>(
        endpoint: String,
        method: HTTPMethod = .get,
        body: Encodable? = nil,
        queryParams: [String: String]? = nil,
        authenticated: Bool = true
    ) async throws -> T {
        let request = try buildRequest(
            endpoint: endpoint,
            method: method,
            body: body,
            queryParams: queryParams,
            authenticated: authenticated
        )
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.unknown
            }
            
            // Handle 401 - try refresh token
            if httpResponse.statusCode == 401 && authenticated {
                if try await refreshAuthToken() {
                    // Retry with new token
                    return try await self.request(
                        endpoint: endpoint,
                        method: method,
                        body: body,
                        queryParams: queryParams,
                        authenticated: authenticated
                    )
                } else {
                    throw NetworkError.unauthorized
                }
            }
            
            // Check for errors
            if httpResponse.statusCode >= 400 {
                let errorMessage = try? decoder.decode(SimpleResponse.self, from: data).error
                throw NetworkError.serverError(httpResponse.statusCode, errorMessage)
            }
            
            // Decode response
            do {
                return try decoder.decode(T.self, from: data)
            } catch {
                #if DEBUG
                if let jsonString = String(data: data, encoding: .utf8) {
                    print("Failed to decode: \(jsonString)")
                }
                #endif
                throw NetworkError.decodingError(error)
            }
            
        } catch let error as NetworkError {
            throw error
        } catch {
            throw NetworkError.networkError(error)
        }
    }
    
    // MARK: - Token Refresh
    private func refreshAuthToken() async throws -> Bool {
        guard let refresh = refreshToken else {
            return false
        }
        
        let request = RefreshTokenRequest(refreshToken: refresh)
        
        do {
            let response: AuthResponse = try await self.request(
                endpoint: Config.Endpoints.refresh,
                method: .post,
                body: request,
                authenticated: false
            )
            
            if let newToken = response.token, let newRefresh = response.refreshToken {
                setTokens(auth: newToken, refresh: newRefresh)
                return true
            }
            
            return false
        } catch {
            clearTokens()
            return false
        }
    }
    
    // MARK: - Convenience Methods
    func get<T: Codable>(
        _ endpoint: String,
        params: [String: String]? = nil
    ) async throws -> T {
        try await request(endpoint: endpoint, method: .get, queryParams: params)
    }
    
    func post<T: Codable>(
        _ endpoint: String,
        body: Encodable? = nil
    ) async throws -> T {
        try await request(endpoint: endpoint, method: .post, body: body)
    }
    
    func put<T: Codable>(
        _ endpoint: String,
        body: Encodable? = nil
    ) async throws -> T {
        try await request(endpoint: endpoint, method: .put, body: body)
    }
    
    func delete<T: Codable>(
        _ endpoint: String,
        body: Encodable? = nil
    ) async throws -> T {
        try await request(endpoint: endpoint, method: .delete, body: body)
    }
}

// MARK: - Keychain Helper
class KeychainHelper {
    static let shared = KeychainHelper()
    
    private init() {}
    
    func save(key: String, value: String) {
        let data = Data(value.utf8)
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        // Delete existing
        SecItemDelete(query as CFDictionary)
        
        // Add new
        SecItemAdd(query as CFDictionary, nil)
    }
    
    func read(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        
        guard let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }
    
    func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}
