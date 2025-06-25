import Foundation
import Combine

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var profile: UserModel?
    @Published var isLoading: Bool = false
    @Published var error: String?
    @Published var achievements: [AchievementModel] = []
    /// IDs of achievements unlocked during the last fetch and not yet viewed by the user.
    @Published var newAchievementIDs: Set<String> = []

    func load() {
        let lastSeenKey = "lastSeenAchievements"
        let lastSeenTimestampKey = "achievementsLastFetch"

        Task {
            do {
                isLoading = true
                async let profileTask = ProfileService.getProfile()
                // Load last fetch timestamp to support incremental API calls if available
                let lastFetch: Date? = {
                    if let ts = UserDefaults.standard.object(forKey: lastSeenTimestampKey) as? Double {
                        return Date(timeIntervalSince1970: ts)
                    }
                    return nil
                }()
                async let achievementsTask: [AchievementModel] = AchievementService.getAchievements(since: lastFetch)
                profile = try await profileTask
                let fetched = try await achievementsTask
                achievements = fetched
                // Determine which achievements are newly unlocked (unlocked==true)
                let unlockedIDs = Set(fetched.filter { $0.unlocked }.map { $0.id })
                let seenIDs: Set<String> = {
                    if let saved = UserDefaults.standard.string(forKey: lastSeenKey) {
                        return Set(saved.split(separator: ",").map(String.init))
                    }
                    return []
                }()
                let newIDs = unlockedIDs.subtracting(seenIDs)
                newAchievementIDs = newIDs
                // Persist current unlocked ids and timestamp
                UserDefaults.standard.set(unlockedIDs.joined(separator: ","), forKey: lastSeenKey)
                UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: lastSeenTimestampKey)
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
