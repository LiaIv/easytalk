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

    /// Starts a new game session.
    /// 1. Immediately shows cached animals from `LocalContentStore` for offline responsiveness.
    /// 2. Asynchronously starts a session and requests incremental updates from backend.
    func startGame(difficulty: Int? = nil) {
        // Determine difficulty from saved level if not provided
        let resolvedDifficulty: Int? = {
            if let diff = difficulty { return diff }
            if let level = UserDefaults.standard.string(forKey: "englishLevel") {
                switch level {
                case "Begin": return 1
                case "Pre-Inter": return 2
                case "Interm": return 3
                default: return nil
                }
            }
            return nil
        }()
        // Load cached data first
        let cache = LocalContentStore.shared
        animals = cache.animals
        currentIndex = 0
        details = []
        score = 0

        // Start async work: create session + pull updates
        Task {
            isLoading = true
            defer { isLoading = false }
            do {
                // Try to start a session (may fail offline)
                if sessionId == nil {
                    do {
                        sessionId = try await GameService.startGuessAnimalSession()
                    } catch {
                        // Ignore if offline; game can still run with cached data
                    }
                }

                // Fetch incremental updates
                let update = try await GameService.fetchAnimalsUpdate(since: cache.contentVersion, difficulty: resolvedDifficulty)
                if !update.items.isEmpty {
                    cache.updateAnimals(update.items, newVersion: update.version)
                    animals = cache.animals // refresh UI
                }
            } catch {
                // Silently ignore network errors; user can still play offline
                print("Animals update failed: \(error)")
            }
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
            // Prepare progress payload
            let correctAnswers = details.filter { $0.isCorrect }.count
            let totalTime = details.reduce(0.0) { $0 + $1.timeSpent }
            let progressReq = SaveProgressRequest(
                score: score,
                correctAnswers: correctAnswers,
                totalAnswers: details.count,
                timeSpent: totalTime,
                date: nil
            )
            do {
                // Try finishing the session first
                do {
                    _ = try await GameService.finishSession(sessionId: sid, details: details, score: score)
                } catch {
                    PendingSyncStore.shared.enqueueFinishSession(sessionId: sid, details: details, score: score)
                }

                // Then attempt to save progress
                do {
                    _ = try await ProgressService.saveProgress(progressReq)
                } catch {
                    PendingSyncStore.shared.enqueueSaveProgress(progressReq)
                }

                isFinished = true
            } catch {
                self.error = error.localizedDescription
            }
            isLoading = false
        }
    }
}
