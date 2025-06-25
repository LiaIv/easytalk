import Foundation
import FirebaseAuth

// MARK: - Config loader
struct AppConfig {
    let baseURL: String
    let useEmulators: Bool
    let firebaseProjectId: String

    static let shared: AppConfig = {
        guard let url = Bundle.main.url(forResource: "Config", withExtension: "plist"),
              let data = try? Data(contentsOf: url),
              let plist = try? PropertyListSerialization.propertyList(from: data, options: [], format: nil) as? [String: Any] else {
            fatalError("💥 Config.plist not found or corrupted. Ensure the file is added to the target.")
        }
        guard let baseURL = plist["baseURL"] as? String,
              let useEmulators = plist["useEmulators"] as? Bool,
              let firebaseProjectId = plist["firebaseProjectId"] as? String else {
            fatalError("💥 Config.plist is missing required keys (baseURL, useEmulators, firebaseProjectId)")
        }
        return AppConfig(baseURL: baseURL, useEmulators: useEmulators, firebaseProjectId: firebaseProjectId)
    }()
}

// MARK: - HTTP Method enum
public enum HTTPMethod: String {
    case GET, POST, PUT, PATCH, DELETE
}

// MARK: - Network Error
public enum NetworkError: Error, LocalizedError {
    case invalidBaseURL
    case invalidURL
    case unauthorised
    case http(Int)
    case decodingFailed(Error)
    case unknown(Error)

    public var errorDescription: String? {
        switch self {
        case .invalidBaseURL: return "Invalid base URL in config"
        case .invalidURL:      return "Invalid URL for endpoint"
        case .unauthorised:    return "Unauthorised (401)"
        case .http(let code):  return "HTTP error code: \(code)"
        case .decodingFailed:  return "Failed to decode response"
        case .unknown(let err):return err.localizedDescription
        }
    }
}

// MARK: - APIEndpoint protocol
public protocol APIEndpoint {
    var path: String { get }
    var method: HTTPMethod { get }
    var queryItems: [URLQueryItem]? { get }
    var body: Data? { get }
}

extension APIEndpoint {
    func urlRequest() throws -> URLRequest {
        guard var components = URLComponents(string: AppConfig.shared.baseURL) else {
            throw NetworkError.invalidBaseURL
        }
        components.path += path
        components.queryItems = queryItems
        guard let url = components.url else { throw NetworkError.invalidURL }
        var req = URLRequest(url: url)
        req.httpMethod = method.rawValue
        req.httpBody = body
        if body != nil { req.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        return req
    }
}

// MARK: - TokenProvider
actor TokenProvider {
    static let shared = TokenProvider()
    private var cachedToken: String?
    private var expiryDate: Date?

    func idToken(forceRefresh: Bool = false) async throws -> String {
        let now = Date()
        if let token = cachedToken, let expiry = expiryDate, expiry > now.addingTimeInterval(60), !forceRefresh {
            return token
        }
        let tokenResult = try await AuthService.shared.idToken(forceRefresh: forceRefresh)
        // Firebase tokens are 1h; set expiry 55m to be safe
        expiryDate = Date().addingTimeInterval(55 * 60)
        cachedToken = tokenResult
        return tokenResult
    }
}

// MARK: - APIClient
public struct APIClient {
    public static let shared = APIClient()
    private init() {}

    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return d
    }()

    public func send<T: Decodable>(_ endpoint: APIEndpoint, type: T.Type = T.self) async throws -> T {
        var request = try endpoint.urlRequest()

        // Attach bearer token
        let token = try await TokenProvider.shared.idToken()
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        // Perform request
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(for: request)
        } catch {
            throw NetworkError.unknown(error)
        }

        guard let http = response as? HTTPURLResponse else {
            throw NetworkError.invalidURL
        }

        if http.statusCode == 401 { // Token expired, retry once
            let refreshedToken = try await TokenProvider.shared.idToken(forceRefresh: true)
            request.setValue("Bearer \(refreshedToken)", forHTTPHeaderField: "Authorization")
            let (retryData, retryResp) = try await URLSession.shared.data(for: request)
            return try decode(type, from: retryData, response: retryResp)
        }

        return try decode(type, from: data, response: response)
    }

    // MARK: - Helpers
    private func decode<T: Decodable>(_ type: T.Type, from data: Data, response: URLResponse) throws -> T {
        if let http = response as? HTTPURLResponse, !(200...299).contains(http.statusCode) {
            if http.statusCode == 401 { throw NetworkError.unauthorised }
            throw NetworkError.http(http.statusCode)
        }
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw NetworkError.decodingFailed(error)
        }
    }
}
