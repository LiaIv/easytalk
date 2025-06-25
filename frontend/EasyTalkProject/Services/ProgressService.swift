import Foundation

/// Service responsible for user progress API calls.
struct ProgressService {
    static func saveProgress(_ request: SaveProgressRequest) async throws -> SaveProgressResponse {
        try await APIClient.shared.send(Endpoints.SaveProgress(request))
    }

    static func getProgress(days: Int = 7) async throws -> ProgressResponse {
        try await APIClient.shared.send(Endpoints.GetProgress(days: days))
    }

    static func getWeeklySummary() async throws -> WeeklySummaryResponse {
        try await APIClient.shared.send(Endpoints.GetWeeklySummary())
    }
}
