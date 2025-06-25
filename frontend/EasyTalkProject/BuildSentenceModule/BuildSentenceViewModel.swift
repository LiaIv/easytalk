import Foundation
import Combine

@MainActor
final class BuildSentenceViewModel: ObservableObject {
    // MARK: - Published state
    @Published var sentences: [SentenceContent] = []
    @Published var currentIndex: Int = 0
    @Published var sessionId: String?
    @Published var isLoading: Bool = false
    @Published var error: String?
    @Published var isFinished: Bool = false

    // MARK: - Private state
    private var details: [RoundDetail] = []
    private var score: Int = 0

    // MARK: - Public helpers
    var currentSentence: SentenceContent? {
        guard currentIndex < sentences.count else { return nil }
        return sentences[currentIndex]
    }

    /// Starts a new game session.
    /// Loads cached sentences first, then asynchronously pulls incremental updates.
    func startGame(difficulty: Int? = nil) {
        // Determine difficulty from saved level if not provided
        let resolvedDifficulty: Int? = {
            if let diff = difficulty { return diff }
            if let level = UserDefaults.standard.string(forKey: "englishLevel") ?? UserDefaults.standard.string(forKey: "userLevelKey") {
                switch level {
                case "Begin": return 1
                case "Pre-Inter": return 2
                case "Interm": return 3
                default: return nil
                }
            }
            return nil
        }()
        let cache = LocalContentStore.shared
        sentences = cache.sentences
        currentIndex = 0
        details = []
        score = 0

        Task {
            isLoading = true
            defer { isLoading = false }
            do {
                // Attempt to start session (offline safe)
                if sessionId == nil {
                    do {
                        sessionId = try await GameService.startBuildSentenceSession()
                    } catch {
                        // Offline
                    }
                }

                let update = try await GameService.fetchSentencesUpdate(since: cache.contentVersion, difficulty: resolvedDifficulty)
                if !update.items.isEmpty {
                    cache.updateSentences(update.items, newVersion: update.version)
                    sentences = cache.sentences
                }
            } catch {
                print("Sentences update failed: \(error)")
            }
        }
    }

    /// Call when user finishes building sentence and submits.
    func submitAnswer(userSentence: String, isCorrect: Bool, timeSpent: Double) {
        guard let sentence = currentSentence else { return }
        let detail = RoundDetail(questionId: sentence.id, answer: userSentence, isCorrect: isCorrect, timeSpent: timeSpent)
        details.append(detail)
        if isCorrect { score += 1 }
        currentIndex += 1
        if currentIndex >= sentences.count {
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
                // Finish session first
                do {
                    _ = try await GameService.finishSession(sessionId: sid, details: details, score: score)
                } catch {
                    PendingSyncStore.shared.enqueueFinishSession(sessionId: sid, details: details, score: score)
                }

                // Save progress
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
