import Foundation

// MARK: - Concrete endpoints

public enum Endpoints {
    // Profile
    public struct GetProfile: APIEndpoint {
        public let path = "/api/profile"
        public let method: HTTPMethod = .GET
        public let queryItems: [URLQueryItem]? = nil
        public let body: Data? = nil
        public init() {}
    }

    public struct UpdateProfile: APIEndpoint {
        private let request: UpdateProfileRequest
        public init(_ request: UpdateProfileRequest) {
            self.request = request
        }
        public var path: String { "/api/profile" }
        public var method: HTTPMethod { .PUT }
        public var queryItems: [URLQueryItem]? { nil }
        public var body: Data? {
            try? JSONEncoder().encode(request)
        }
    }

    // Session
    public struct StartSession: APIEndpoint {
        private let request: StartSessionRequest
        public init(_ request: StartSessionRequest) { self.request = request }
        public var path: String { "/api/session/start" }
        public var method: HTTPMethod { .POST }
        public var queryItems: [URLQueryItem]? { nil }
        public var body: Data? { try? JSONEncoder().encode(request) }
    }

    public struct FinishSession: APIEndpoint {
        private let sessionId: String
        private let request: FinishSessionRequest
        public init(sessionId: String, request: FinishSessionRequest) {
            self.sessionId = sessionId
            self.request = request
        }
        public var path: String { "/api/session/finish" }
        public var method: HTTPMethod { .PATCH }
        public var queryItems: [URLQueryItem]? { [URLQueryItem(name: "session_id", value: sessionId)] }
        public var body: Data? { try? JSONEncoder().encode(request) }
    }

    public struct GetAnimals: APIEndpoint {
        private let difficulty: Int?
        private let limit: Int?
        private let since: Int?
        public init(difficulty: Int? = nil, limit: Int? = nil, since: Int? = nil) {
            self.difficulty = difficulty
            self.limit = limit
            self.since = since
        }
        public var path: String { "/api/content/animals" }
        public var method: HTTPMethod { .GET }
        public var queryItems: [URLQueryItem]? {
            var items: [URLQueryItem] = []
            if let difficulty = difficulty { items.append(URLQueryItem(name: "difficulty", value: String(difficulty))) }
            if let limit = limit { items.append(URLQueryItem(name: "limit", value: String(limit))) }
            return items.isEmpty ? nil : items
        }
        public let body: Data? = nil
    }

    public struct GetSentences: APIEndpoint {
        private let difficulty: Int?
        private let limit: Int?
        private let since: Int?
        public init(difficulty: Int? = nil, limit: Int? = nil, since: Int? = nil) {
            self.difficulty = difficulty
            self.limit = limit
            self.since = since
        }
        public var path: String { "/api/content/sentences" }
        public var method: HTTPMethod { .GET }
        public var queryItems: [URLQueryItem]? {
            var items: [URLQueryItem] = []
            if let difficulty = difficulty { items.append(URLQueryItem(name: "difficulty", value: String(difficulty))) }
            if let limit = limit { items.append(URLQueryItem(name: "limit", value: String(limit))) }
            return items.isEmpty ? nil : items
        }
        public let body: Data? = nil
    }
}
