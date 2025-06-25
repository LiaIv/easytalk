import Foundation
import Combine

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var profile: UserModel?
    @Published var isLoading: Bool = false
    @Published var error: String?
    @Published var achievements: [AchievementModel] = []

    func load() {
        Task {
            do {
                isLoading = true
                async let profileTask = ProfileService.getProfile()
                async let achievementsTask: [AchievementModel] = AchievementService.getAchievements()
                profile = try await profileTask
                achievements = try await achievementsTask
            } catch {
                error = error.localizedDescription
            }
            isLoading = false
        }
    }

    func updateDisplayName(_ name: String) {
        Task {
            do {
                let updated = try await ProfileService.updateProfile(
                    UpdateProfileRequest(displayName: name)
                )
                profile = updated
            } catch {
                error = error.localizedDescription
            }
        }
    }

    /// Update user's English level on the server
    func updateLevel(_ level: String) {
        Task {
            do {
                let updated = try await ProfileService.updateProfile(
                    UpdateProfileRequest(level: level)
                )
                profile = updated
            } catch {
                error = error.localizedDescription
            }
        }
    }
}
