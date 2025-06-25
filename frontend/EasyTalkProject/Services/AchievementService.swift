import Foundation

/// Service layer for achievements.
struct AchievementService {
    static func getAchievements() async throws -> [AchievementModel] {
        try await APIClient.shared.send(Endpoints.GetAchievements())
    }
}
