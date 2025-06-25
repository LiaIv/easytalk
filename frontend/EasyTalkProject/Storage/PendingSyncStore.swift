import Foundation

/// Offline queue for game-related write operations (finish session, save progress, etc.).
/// When device is offline, tasks are persisted locally. When network becomes available, call `flush()`.
@MainActor
final class PendingSyncStore {
    static let shared = PendingSyncStore()
    private init() { load() }

    // Task types
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

    struct SaveProgressTask: Codable, Identifiable {
        let id: UUID
        let request: SaveProgressRequest
        init(request: SaveProgressRequest) {
            self.id = UUID()
            self.request = request
        }
    }

    @Published private(set) var pendingFinish: [FinishSessionTask] = []
    @Published private(set) var pendingProgress: [SaveProgressTask] = []

    // MARK: - Public API
    func enqueueFinishSession(sessionId: String, details: [RoundDetail], score: Int) {
        pendingFinish.append(FinishSessionTask(sessionId: sessionId, details: details, score: score))
        save()
    }

    func enqueueSaveProgress(_ request: SaveProgressRequest) {
        pendingProgress.append(SaveProgressTask(request: request))
        save()
    }

    /// Attempt to send all queued tasks. Should be called on app launch and when connectivity restored.
    func flush() {
        guard !(pendingFinish.isEmpty && pendingProgress.isEmpty) else { return }
        Task {
            var remaining: [FinishSessionTask] = []
            // Finish sessions first
            for task in pendingFinish {
                do {
                    _ = try await GameService.finishSession(sessionId: task.sessionId, details: task.details, score: task.score)
                } catch {
                    remaining.append(task)
                }
            }
            pendingFinish = remaining

            // Save progress tasks
            var remainingProgress: [SaveProgressTask] = []
            for task in pendingProgress {
                do {
                    _ = try await ProgressService.saveProgress(task.request)
                } catch {
                    remainingProgress.append(task)
                }
            }
            pendingProgress = remainingProgress
            save()
        }
    }

    // MARK: - Persistence
    private struct Cache: Codable {
        let finish: [FinishSessionTask]
        let progress: [SaveProgressTask]
    }

    private var fileURL: URL {
        let dir = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first!
        return dir.appendingPathComponent("pending_sync_tasks.json")
    }

    private func load() {
        guard let data = try? Data(contentsOf: fileURL) else { return }
        // Attempt decode new format
        if let cache = try? JSONDecoder().decode(Cache.self, from: data) {
            pendingFinish = cache.finish
            pendingProgress = cache.progress
            return
        }
        // Fallback to old format (only finish tasks)
        struct OldCache: Codable { let tasks: [FinishSessionTask] }
        if let old = try? JSONDecoder().decode(OldCache.self, from: data) {
            pendingFinish = old.tasks
            pendingProgress = []
        }
    }

    private func save() {
        Task.detached {
            let cache = Cache(finish: self.pendingFinish, progress: self.pendingProgress)
            if let data = try? JSONEncoder().encode(cache) {
                try? data.write(to: self.fileURL, options: [.atomic])
            }
        }
    }
}
