import Foundation

/// Service layer for achievements.
struct AchievementService {
    /// Fetch achievement catalogue with unlocked flags. Set `since` to fetch only new/unlocked since the given timestamp (server-side support required).
    static func getAchievements(since: Date? = nil) async throws -> [AchievementModel] {
        try await APIClient.shared.send(Endpoints.GetAchievements(since: since))
    }
}
