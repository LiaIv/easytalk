import Foundation

/// Generic wrapper for incremental content updates from backend.
/// `items` – newly added or changed items since the provided version.
/// `version` – latest content version on backend. Save it in `LocalContentStore`.
public struct ContentUpdate<T: Decodable>: Decodable {
    public let items: [T]
    public let version: Int

    enum CodingKeys: String, CodingKey {
        case items = "data" // backend returns `data` array
        case version
    }
}
