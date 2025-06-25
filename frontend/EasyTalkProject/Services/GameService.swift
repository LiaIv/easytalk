import Foundation

/// Service responsible for game-related API calls (sessions & content).
struct GameService {
    // MARK: - Guess the Animal
    /// Start a new "Guess the Animal" session on the server and returns its `sessionId`.
    static func startGuessAnimalSession() async throws -> String {
        let response: StartSessionResponse = try await APIClient.shared.send(
            Endpoints.StartSession(StartSessionRequest(gameType: .guessAnimal))
        )
        return response.sessionId
    }

    /// Fetches a list of animals to guess (optionally filtered by difficulty / limit).
    static func fetchAnimals(difficulty: Int? = nil, limit: Int? = nil) async throws -> [AnimalContent] {
        try await APIClient.shared.send(
            Endpoints.GetAnimals(difficulty: difficulty, limit: limit)
        )
    }

    /// Finish an ongoing session and persist user results.
    static func finishSession(sessionId: String, details: [RoundDetail], score: Int) async throws -> FinishSessionResponse {
        try await APIClient.shared.send(
            Endpoints.FinishSession(
                sessionId: sessionId,
                request: FinishSessionRequest(details: details, score: score)
            )
        )
    }

    // MARK: - Build a Sentence
    /// Start a new "Build a Sentence" session and return its `sessionId`.
    static func startBuildSentenceSession() async throws -> String {
        let response: StartSessionResponse = try await APIClient.shared.send(
            Endpoints.StartSession(StartSessionRequest(gameType: .buildSentence))
        )
        return response.sessionId
    }

    /// Fetch sentences content for the Build a Sentence game.
    static func fetchSentences(difficulty: Int? = nil, limit: Int? = nil) async throws -> [SentenceContent] {
        try await APIClient.shared.send(
            Endpoints.GetSentences(difficulty: difficulty, limit: limit)
        )
    }

    // MARK: - Incremental Updates
    /// Fetch animals updated since given version. Returns list of changed items and latest version.
    static func fetchAnimalsUpdate(since: Int, difficulty: Int? = nil) async throws -> ContentUpdate<AnimalContent> {
        try await APIClient.shared.send(
            Endpoints.GetAnimals(difficulty: difficulty, limit: nil, since: since)
        )
    }

    /// Fetch sentences updated since given version.
    static func fetchSentencesUpdate(since: Int, difficulty: Int? = nil) async throws -> ContentUpdate<SentenceContent> {
        try await APIClient.shared.send(
            Endpoints.GetSentences(difficulty: difficulty, limit: nil, since: since)
        )
    }
}
