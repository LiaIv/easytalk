import Foundation
import Network

/// Monitors network status and triggers PendingSyncStore flush when connection becomes available.
@MainActor
final class NetworkMonitor {
    static let shared = NetworkMonitor()
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "NetworkMonitor")

    private init() {
        monitor.pathUpdateHandler = { path in
            if path.status == .satisfied {
                PendingSyncStore.shared.flush()
            }
        }
        monitor.start(queue: queue)
    }
}
