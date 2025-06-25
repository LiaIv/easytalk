import Foundation

/// Persisted cache for game content (animals & sentences) to support offline mode.
/// Usage: `LocalContentStore.shared`.
@MainActor
final class LocalContentStore {
    static let shared = LocalContentStore()
    private init() {
        load() // attempt to load from disk on first access
    }

    // MARK: - Public data
    @Published private(set) var animals: [AnimalContent] = []
    @Published private(set) var sentences: [SentenceContent] = []

    // Simple content version for incremental updates (could be a timestamp or int)
    private(set) var contentVersion: Int = 0

    // MARK: - Public helpers
    func updateAnimals(_ new: [AnimalContent], newVersion: Int? = nil) {
        var dict = Dictionary(uniqueKeysWithValues: animals.map { ($0.id, $0) })
        for item in new {
            dict[item.id] = item
        }
        animals = Array(dict.values)
        if let v = newVersion { contentVersion = max(contentVersion, v) }
        save()
    }

    func updateSentences(_ new: [SentenceContent], newVersion: Int? = nil) {
        var dict = Dictionary(uniqueKeysWithValues: sentences.map { ($0.id, $0) })
        for item in new {
            dict[item.id] = item
        }
        sentences = Array(dict.values)
        if let v = newVersion { contentVersion = max(contentVersion, v) }
        save()
    }

    // MARK: - Disk persistence
    private struct Cache: Codable {
        let animals: [AnimalContent]
        let sentences: [SentenceContent]
        let version: Int
    }

    private var fileURL: URL {
        let fm = FileManager.default
        let dir = fm.urls(for: .cachesDirectory, in: .userDomainMask).first!
        return dir.appendingPathComponent("game_content_cache.json")
    }

    private func load() {
        guard let data = try? Data(contentsOf: fileURL) else { return }
        if let cache = try? JSONDecoder().decode(Cache.self, from: data) {
            animals = cache.animals
            sentences = cache.sentences
            contentVersion = cache.version
        }
    }

    private func save() {
        Task.detached {
            let cache = Cache(animals: self.animals, sentences: self.sentences, version: self.contentVersion)
            if let data = try? JSONEncoder().encode(cache) {
                try? data.write(to: self.fileURL, options: [.atomic])
            }
        }
    }
}
