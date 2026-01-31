//
//  NetworkService.swift
//  EnlikoTrading
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
    case timeout
    case noInternet
    case sslError
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "error_invalid_url".localized
        case .noData:
            return "error_no_data".localized
        case .decodingError(let error):
            return "Decoding error: \(error.localizedDescription)"
        case .serverError(let code, let message):
            return message ?? "Server error: \(code)"
        case .unauthorized:
            return "error_auth".localized
        case .networkError(let error):
            return "error_network".localized + ": \(error.localizedDescription)"
        case .timeout:
            return "error_timeout".localized
        case .noInternet:
            return "error_no_internet".localized
        case .sslError:
            return "error_ssl".localized
        case .unknown:
            return "error_unknown".localized
        }
    }
    
    var isRetryable: Bool {
        switch self {
        case .timeout, .noInternet, .networkError:
            return true
        case .serverError(let code, _):
            return code >= 500 // Server errors are retryable
        default:
            return false
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
    private let logger = AppLogger.shared
    
    // Retry configuration
    private let maxRetries = 3
    private let retryDelay: TimeInterval = 1.0
    
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = Config.requestTimeout
        config.timeoutIntervalForResource = Config.requestTimeout * 2
        config.waitsForConnectivity = true
        
        self.session = URLSession(configuration: config)
        
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .useDefaultKeys
        
        self.encoder = JSONEncoder()
        self.encoder.keyEncodingStrategy = .useDefaultKeys
        
        logger.info("NetworkService initialized", category: .network)
    }
    
    // MARK: - Token Management
    private var authToken: String? {
        get { 
            let token = KeychainHelper.shared.read(key: Config.tokenKey)
            logger.debug("Read auth token: \(token != nil ? "exists" : "nil")", category: .security)
            return token
        }
        set {
            if let token = newValue {
                KeychainHelper.shared.save(key: Config.tokenKey, value: token)
                logger.info("Auth token saved", category: .security)
            } else {
                KeychainHelper.shared.delete(key: Config.tokenKey)
                logger.info("Auth token deleted", category: .security)
            }
        }
    }
    
    private var refreshToken: String? {
        get { 
            let token = KeychainHelper.shared.read(key: Config.refreshTokenKey)
            logger.debug("Read refresh token: \(token != nil ? "exists" : "nil")", category: .security)
            return token
        }
        set {
            if let token = newValue {
                KeychainHelper.shared.save(key: Config.refreshTokenKey, value: token)
                logger.info("Refresh token saved", category: .security)
            } else {
                KeychainHelper.shared.delete(key: Config.refreshTokenKey)
                logger.info("Refresh token deleted", category: .security)
            }
        }
    }
    
    func setTokens(auth: String, refresh: String) {
        logger.logAuthSuccess("setTokens")
        authToken = auth
        refreshToken = refresh
    }
    
    func clearTokens() {
        logger.logLogout()
        authToken = nil
        refreshToken = nil
        KeychainHelper.shared.delete(key: Config.userIdKey)
    }
    
    var isAuthenticated: Bool {
        let hasToken = authToken != nil
        logger.debug("isAuthenticated: \(hasToken)", category: .auth)
        return hasToken
    }
    
    /// Public accessor for auth token (read-only) - used for WebSocket connections
    var currentAuthToken: String? {
        authToken
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
            logger.error("Invalid URL: \(urlString)", category: .network)
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("EnlikoTrading-iOS/1.0", forHTTPHeaderField: "User-Agent")
        
        // Add auth header
        if authenticated, let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Add body
        if let body = body {
            do {
                request.httpBody = try encoder.encode(body)
            } catch {
                logger.error("Failed to encode request body: \(error)", category: .network)
                throw error
            }
        }
        
        return request
    }
    
    // MARK: - Generic Request
    func request<T: Codable>(
        endpoint: String,
        method: HTTPMethod = .get,
        body: Encodable? = nil,
        queryParams: [String: String]? = nil,
        authenticated: Bool = true,
        retryCount: Int = 0
    ) async throws -> T {
        let startTime = Date()
        let request = try buildRequest(
            endpoint: endpoint,
            method: method,
            body: body,
            queryParams: queryParams,
            authenticated: authenticated
        )
        
        // Log request
        let bodyString = body.flatMap { try? String(data: encoder.encode($0), encoding: .utf8) }
        logger.logRequest(method.rawValue, url: endpoint, body: bodyString)
        
        do {
            let (data, response) = try await session.data(for: request)
            let duration = Date().timeIntervalSince(startTime)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                logger.error("Invalid response type", category: .network)
                throw NetworkError.unknown
            }
            
            // Log response
            logger.logResponse(method.rawValue, url: endpoint, statusCode: httpResponse.statusCode, duration: duration)
            
            // Handle 401 - try refresh token (only once to prevent infinite loop)
            if httpResponse.statusCode == 401 && authenticated && retryCount == 0 {
                logger.warning("401 Unauthorized - attempting token refresh", category: .auth)
                if try await refreshAuthToken() {
                    // Retry with new token (increment retryCount to prevent infinite loop)
                    logger.info("Token refreshed successfully, retrying request", category: .auth)
                    return try await self.request(
                        endpoint: endpoint,
                        method: method,
                        body: body,
                        queryParams: queryParams,
                        authenticated: authenticated,
                        retryCount: retryCount + 1
                    )
                } else {
                    logger.error("Token refresh failed", category: .auth)
                    throw NetworkError.unauthorized
                }
            } else if httpResponse.statusCode == 401 && authenticated && retryCount > 0 {
                // Already retried after refresh - token is truly invalid
                logger.error("401 after token refresh - clearing tokens", category: .auth)
                clearTokens()
                throw NetworkError.unauthorized
            }
            
            // Check for errors
            if httpResponse.statusCode >= 400 {
                // ALWAYS log raw response for debugging
                let rawResponse = String(data: data, encoding: .utf8) ?? "unable to decode"
                logger.error("❌ HTTP \(httpResponse.statusCode) from \(endpoint): \(rawResponse.prefix(500))", category: .network)
                
                // Try to parse validation error (422)
                if httpResponse.statusCode == 422 {
                    logger.error("Attempting to parse 422 validation error...", category: .network)
                    
                    if let validationError = try? decoder.decode(ValidationErrorResponse.self, from: data) {
                        let message = validationError.userFriendlyMessage
                        logger.error("✅ Parsed validation error: \(message)", category: .network)
                        logger.sendLogsToServer() // Send logs for analysis
                        throw NetworkError.serverError(httpResponse.statusCode, message)
                    } else {
                        logger.error("❌ Failed to decode ValidationErrorResponse", category: .network)
                    }
                }
                
                // Try standard error format
                let errorMessage = try? decoder.decode(SimpleResponse.self, from: data).error
                    ?? (try? decoder.decode(SimpleResponse.self, from: data).message)
                logger.error("Server error \(httpResponse.statusCode): \(errorMessage ?? "unknown")", category: .network)
                logger.sendLogsToServer() // Send logs for analysis
                throw NetworkError.serverError(httpResponse.statusCode, errorMessage)
            }
            
            // Decode response
            do {
                let decoded = try decoder.decode(T.self, from: data)
                logger.debug("Successfully decoded response for \(endpoint)", category: .network)
                return decoded
            } catch {
                #if DEBUG
                if let jsonString = String(data: data, encoding: .utf8) {
                    logger.error("Failed to decode response: \(jsonString.prefix(500))", category: .network)
                }
                #endif
                logger.error("Decoding error: \(error)", category: .network)
                throw NetworkError.decodingError(error)
            }
            
        } catch let error as NetworkError {
            throw error
        } catch let urlError as URLError {
            // Handle specific URL errors
            let networkError: NetworkError
            switch urlError.code {
            case .timedOut:
                networkError = .timeout
            case .notConnectedToInternet, .networkConnectionLost:
                networkError = .noInternet
            case .secureConnectionFailed, .serverCertificateUntrusted:
                networkError = .sslError
            default:
                networkError = .networkError(urlError)
            }
            
            // Retry logic for retryable errors
            if networkError.isRetryable && retryCount < maxRetries {
                logger.warning("Request failed, retrying (\(retryCount + 1)/\(maxRetries)): \(networkError.localizedDescription)", category: .network)
                try await Task.sleep(nanoseconds: UInt64(retryDelay * 1_000_000_000))
                return try await self.request(
                    endpoint: endpoint,
                    method: method,
                    body: body,
                    queryParams: queryParams,
                    authenticated: authenticated,
                    retryCount: retryCount + 1
                )
            }
            
            logger.logNetworkError(urlError, method: method.rawValue, url: endpoint)
            throw networkError
        } catch {
            logger.logNetworkError(error, method: method.rawValue, url: endpoint)
            throw NetworkError.networkError(error)
        }
    }
    
    // MARK: - Token Refresh
    private func refreshAuthToken() async throws -> Bool {
        guard let refresh = refreshToken else {
            logger.warning("No refresh token available", category: .auth)
            return false
        }
        
        logger.info("Attempting token refresh", category: .auth)
        
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
                logger.info("Token refresh successful", category: .auth)
                return true
            }
            
            logger.warning("Token refresh response missing tokens", category: .auth)
            return false
        } catch {
            logger.error("Token refresh failed: \(error)", category: .auth)
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
    
    /// Fire-and-forget POST request (no response expected)
    func postIgnoreResponse(
        _ endpoint: String,
        body: Encodable? = nil
    ) async throws {
        let _: EmptyResponse = try await request(endpoint: endpoint, method: .post, body: body)
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
    
    /// Delete request that ignores response (fire-and-forget)
    func delete(_ endpoint: String) async throws {
        let request = try buildRequest(endpoint: endpoint, method: .delete, body: nil, authenticated: true)
        let (_, response) = try await session.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse,
           !(200...299).contains(httpResponse.statusCode) {
            throw NetworkError.serverError(httpResponse.statusCode, nil)
        }
    }
}

// MARK: - Keychain Helper
class KeychainHelper {
    static let shared = KeychainHelper()
    private let logger = AppLogger.shared
    
    private init() {}
    
    func save(key: String, value: String) {
        let data = Data(value.utf8)
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock  // Security: available after first unlock
        ]
        
        // Delete existing
        let deleteStatus = SecItemDelete(query as CFDictionary)
        logger.logKeychainOperation("delete", key: key, success: deleteStatus == errSecSuccess || deleteStatus == errSecItemNotFound)
        
        // Add new
        let addStatus = SecItemAdd(query as CFDictionary, nil)
        logger.logKeychainOperation("save", key: key, success: addStatus == errSecSuccess)
        
        if addStatus != errSecSuccess {
            logger.error("Keychain save failed for key '\(key)': \(addStatus)", category: .security)
        }
    }
    
    func read(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        let success = status == errSecSuccess
        logger.logKeychainOperation("read", key: key, success: success)
        
        guard success, let data = result as? Data else { 
            if status != errSecItemNotFound {
                logger.debug("Keychain read failed for key '\(key)': \(status)", category: .security)
            }
            return nil 
        }
        return String(data: data, encoding: .utf8)
    }
    
    func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        logger.logKeychainOperation("delete", key: key, success: status == errSecSuccess || status == errSecItemNotFound)
    }
    
    /// Clear all app keychain items (use on logout or reset)
    func clearAll() {
        let secItemClasses = [
            kSecClassGenericPassword,
            kSecClassInternetPassword
        ]
        
        for itemClass in secItemClasses {
            let query: [String: Any] = [kSecClass as String: itemClass]
            let status = SecItemDelete(query as CFDictionary)
            logger.debug("Keychain clear \(itemClass): \(status)", category: .security)
        }
        
        logger.info("Keychain cleared", category: .security)
    }
}
