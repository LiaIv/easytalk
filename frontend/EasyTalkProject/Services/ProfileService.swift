import Foundation

/// Service layer for profile-related network operations.
struct ProfileService {
    /// Fetch current user profile.
    static func getProfile() async throws -> UserModel {
        try await APIClient.shared.send(Endpoints.GetProfile())
    }

    /// Update current user profile on server.
    static func updateProfile(_ request: UpdateProfileRequest) async throws -> UserModel {
        try await APIClient.shared.send(Endpoints.UpdateProfile(request))
    }
}
