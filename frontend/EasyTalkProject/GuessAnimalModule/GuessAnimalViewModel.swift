import Foundation
import Combine

@MainActor
final class GuessAnimalViewModel: ObservableObject {
    // MARK: - Published state
    @Published var animals: [AnimalContent] = []
    @Published var currentIndex: Int = 0
    @Published var sessionId: String?
    @Published var isLoading: Bool = false
    @Published var error: String?
    @Published var isFinished: Bool = false

    // MARK: - Private state
    private var details: [RoundDetail] = []
    private var score: Int = 0

    // MARK: - Public helpers
    var currentAnimal: AnimalContent? {
        guard currentIndex < animals.count else { return nil }
        return animals[currentIndex]
    }

    /// Starts a new game session and preloads animals.
    func startGame(difficulty: Int? = nil, limit: Int = 10) {
        Task {
            isLoading = true
            do {
                sessionId = try await GameService.startGuessAnimalSession()
                animals = try await GameService.fetchAnimals(difficulty: difficulty, limit: limit)
                currentIndex = 0
                details = []
                score = 0
            } catch {
                self.error = error.localizedDescription
            }
            isLoading = false
        }
    }

    /// Call when user answers (taps variant) and proceed to next question.
    func submitAnswer(questionId: String, userAnswer: String, isCorrect: Bool, timeSpent: Double) {
        let detail = RoundDetail(questionId: questionId, answer: userAnswer, isCorrect: isCorrect, timeSpent: timeSpent)
        details.append(detail)
        if isCorrect { score += 1 }
        currentIndex += 1
        if currentIndex >= animals.count {
            finishGame()
        }
    }

    /// Finish session and send results to the server.
    private func finishGame() {
        guard let sid = sessionId else { return }
        isLoading = true
        Task {
            do {
                _ = try await GameService.finishSession(sessionId: sid, details: details, score: score)
                isFinished = true
            } catch {
                self.error = error.localizedDescription
            }
            isLoading = false
        }
    }
}
