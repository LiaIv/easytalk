import Foundation

/// Offline queue for game-related write operations (finish session, save progress, etc.).
/// When device is offline, tasks are persisted locally. When network becomes available, call `flush()`.
@MainActor
final class PendingSyncStore {
    static let shared = PendingSyncStore()
    private init() { load() }

    // Currently we queue only FinishSession tasks. Extend if needed.
    struct FinishSessionTask: Codable, Identifiable {
        let id: UUID
        let sessionId: String
        let details: [RoundDetail]
        let score: Int
        init(sessionId: String, details: [RoundDetail], score: Int) {
            self.id = UUID()
            self.sessionId = sessionId
            self.details = details
            self.score = score
        }
    }

    @Published private(set) var pendingFinish: [FinishSessionTask] = []

    // MARK: - Public API
    func enqueueFinishSession(sessionId: String, details: [RoundDetail], score: Int) {
        pendingFinish.append(FinishSessionTask(sessionId: sessionId, details: details, score: score))
        save()
    }

    /// Attempt to send all queued tasks. Should be called on app launch and when connectivity restored.
    func flush() {
        guard !pendingFinish.isEmpty else { return }
        Task {
            var remaining: [FinishSessionTask] = []
            for task in pendingFinish {
                do {
                    _ = try await GameService.finishSession(sessionId: task.sessionId, details: task.details, score: task.score)
                    // success -> not re-added
                } catch {
                    // keep task for next time
                    remaining.append(task)
                }
            }
            pendingFinish = remaining
            save()
        }
    }

    // MARK: - Persistence
    private struct Cache: Codable { let tasks: [FinishSessionTask] }

    private var fileURL: URL {
        let dir = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first!
        return dir.appendingPathComponent("pending_sync_tasks.json")
    }

    private func load() {
        guard let data = try? Data(contentsOf: fileURL) else { return }
        if let cache = try? JSONDecoder().decode(Cache.self, from: data) {
            pendingFinish = cache.tasks
        }
    }

    private func save() {
        Task.detached {
            let cache = Cache(tasks: self.pendingFinish)
            if let data = try? JSONEncoder().encode(cache) {
                try? data.write(to: self.fileURL, options: [.atomic])
            }
        }
    }
}
