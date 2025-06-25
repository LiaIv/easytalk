import Foundation
import FirebaseAuth

class AuthService {
    
    static let shared = AuthService()
    
    private init() {}
    
    private let auth = Auth.auth()
    
    var currentUser: User? {
        return auth.currentUser
    }
    
    func signUp(email: String, password: String, completion: @escaping(Result<User, Error>) -> ()) {
        
        auth.createUser(withEmail: email, password: password) { result, error in
            if let result = result {
                completion(.success(result.user))
            } else if let error = error {
                completion(.failure(error))
            }
        }
    }
    
    func signIn(email: String, password: String, completion: @escaping(Result<User, Error>) -> ()) {
        
        auth.signIn(withEmail: email, password: password) { result, error in
            
            if let result = result {
                completion(.success(result.user))
            } else if let error = error {
                completion(.failure(error))
            }

        }
        
    }
    
    /// Returns Firebase ID token for the current user. Forces refresh when `forceRefresh == true`.
    /// - Throws: `AuthError.noUser` when there is no signed-in user or the underlying Firebase error.
    func idToken(forceRefresh: Bool = false) async throws -> String {
        guard let user = auth.currentUser else {
            throw AuthError.noUser
        }
        return try await withCheckedThrowingContinuation { continuation in
            user.getIDTokenForcingRefresh(forceRefresh) { token, error in
                if let token = token {
                    continuation.resume(returning: token)
                } else {
                    continuation.resume(throwing: error ?? AuthError.tokenFailed)
                }
            }
        }
    }
}

/// Custom Auth-related errors.
enum AuthError: Error {
    case noUser
    case tokenFailed
}