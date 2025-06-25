import Foundation
import Combine

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var profile: UserModel?
    @Published var isLoading: Bool = false
    @Published var error: String?

    func load() {
        Task {
            do {
                isLoading = true
                profile = try await ProfileService.getProfile()
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
                    UpdateProfileRequest(displayName: name, email: nil, photoUrl: nil)
                )
                profile = updated
            } catch {
                error = error.localizedDescription
            }
        }
    }
}
