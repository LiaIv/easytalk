import Foundation

// MARK: - User & Profile
public struct UserModel: Codable {
    public let uid: String
    public let email: String
    public let displayName: String?
    public let photoUrl: String?
    public let level: String?
    public let createdAt: Date?
}

public struct UpdateProfileRequest: Codable {
    public let displayName: String?
    public let email: String?
    public let photoUrl: String?
    public let level: String?

    public init(displayName: String? = nil,
                email: String? = nil,
                photoUrl: String? = nil,
                level: String? = nil) {
        self.displayName = displayName
        self.email = email
        self.photoUrl = photoUrl
        self.level = level
    }
}

// MARK: - Session
public enum GameType: String, Codable {
    case guessAnimal = "guess_animal"
    case buildSentence = "build_sentence"
}

public enum SessionStatus: String, Codable {
    case active, finished, abandoned
}

public struct RoundDetail: Codable {
    public let questionId: String
    public let answer: String
    public let isCorrect: Bool
    public let timeSpent: Double
}

public struct SessionModel: Codable {
    public let sessionId: String
    public let userId: String
    public let gameType: GameType
    public let startTime: Date
    public let endTime: Date?
    public let status: SessionStatus
    public let score: Int?
    public let details: [RoundDetail]?
}

public struct StartSessionRequest: Codable {
    public let gameType: GameType
}

public struct StartSessionResponse: Codable {
    public let sessionId: String
}

public struct FinishSessionRequest: Codable {
    public let details: [RoundDetail]
    public let score: Int
}

public struct FinishSessionResponse: Codable {
    public let message: String
}

// MARK: - Progress
public struct SaveProgressRequest: Codable {
    public let score: Int
    public let correctAnswers: Int
    public let totalAnswers: Int
    public let timeSpent: Double
    public let date: String?
}

public struct SaveProgressResponse: Codable {
    public let message: String
    public let progressId: String
}

public struct ProgressItemResponse: Codable {
    public let date: String
    public let dailyScore: Int
    public let correctAnswers: Int
    public let totalAnswers: Int
    public let successRate: Double
    public let timeSpent: Double?
}

public struct ProgressResponse: Codable {
    public let data: [ProgressItemResponse]
    public let totalScore: Int
    public let averageScore: Double
    public let successRate: Double?
}

public struct WeeklySummaryResponse: Codable {
    public let totalWeeklyScore: Int
}

// MARK: - Content models
public struct AnimalContent: Codable {
    public let id: String
    public let name: String
    public let englishName: String
    public let imageUrl: String?
    public let soundUrl: String?
    public let difficulty: Int
    public let description: String?
}

public struct SentenceContent: Codable {
    public let id: String
    public let sentence: String
    public let words: [String]
    public let difficulty: Int
    public let translation: String?
}

// MARK: - Achievements
public struct AchievementModel: Codable, Identifiable {
    public let id: String
    public let name: String
    public let description: String
    public let iconUrl: String?
    public let unlocked: Bool
}
