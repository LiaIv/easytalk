import SwiftUI

/// Integrated screen that works with GuessAnimalViewModel & backend.
struct GuessAnimalGameScreen: View {
    @StateObject private var vm = GuessAnimalViewModel()
    @Environment(\.dismiss) private var dismiss

    // UI State
    @State private var selectedOption: String? = nil
    @State private var isCorrect: Bool? = nil
    @State private var roundResults: [RoundResultStatus] = []
    private let optionsPerQuestion = 4

    var body: some View {
        ZStack {
            Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.6).ignoresSafeArea()

            if vm.isLoading {
                ProgressView("Загрузка…")
            } else if let animal = vm.currentAnimal {
                GeometryReader { geo in
                    VStack(spacing: 0) {
                        topBar(safeInsets: geo.safeAreaInsets)
                        animalImage(for: animal, height: geo.size.height * 0.48)
                        revealArea(animal: animal)
                        optionsGrid(animal: animal)
                        nextButton()
                        Spacer()
                    }
                }
                .alert("Игра завершена!", isPresented: $vm.isFinished) {
                    Button("Начать заново", role: .cancel) { resetGame() }
                    Button("Выйти") { dismiss() }
                } message: {
                    Text("Ваш результат: \(vm.animals.isEmpty ? 0 : score()) из \(vm.animals.count)")
                }
            } else if let error = vm.error {
                VStack {
                    Text(error).foregroundColor(.red)
                    Button("Повторить") { vm.startGame() }
                }
            }
        }
        .toolbar(.hidden, for: .navigationBar)
        .onAppear {
            vm.startGame()
        }
        .onChange(of: vm.animals) { animals in
            roundResults = Array(repeating: .pending, count: animals.count)
        }
    }

    // MARK: - Subviews
    private func topBar(safeInsets: EdgeInsets) -> some View {
        HStack {
            Button { dismiss() } label: {
                Image(systemName: "chevron.left").font(.title2.weight(.medium))
            }
            Spacer()
            ProgressDotsView(totalRounds: vm.animals.count, roundResults: roundResults)
            Spacer()
            Image(systemName: "chevron.left").opacity(0) // balancing spacer
        }
        .padding(.horizontal)
        .padding(.top, safeInsets.top > 0 ? 0 : 10)
        .padding(.bottom, 5)
        .foregroundColor(Color(white: 0.2))
    }

    private func animalImage(for animal: AnimalContent, height: CGFloat) -> some View {
        AsyncImage(url: URL(string: animal.imageUrl ?? "")) { phase in
            switch phase {
            case .success(let image):
                image.resizable().scaledToFit()
            case .failure(_):
                Image(systemName: "photo").resizable().scaledToFit().foregroundColor(.gray.opacity(0.6))
            default:
                ProgressView()
            }
        }
        .frame(height: height)
        .background(Color.white.opacity(0.3))
        .cornerRadius(15)
        .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
        .padding(.horizontal, 10)
        .padding(.top, 10)
        .padding(.bottom, 15)
    }

    private func revealArea(animal: AnimalContent) -> some View {
        Text(selectedOption != nil ? animal.englishName : "Какое это животное?")
            .font(selectedOption != nil ? .title.bold() : .title2.weight(.medium))
            .foregroundColor(Color(white: 0.25))
            .padding(.vertical, 22)
            .frame(maxWidth: .infinity)
            .background(Color(white: 0.88, opacity: 0.9))
            .cornerRadius(12)
            .padding(.horizontal, 20)
            .padding(.bottom, 15)
    }

    private func optionsGrid(animal: AnimalContent) -> some View {
        let opts = options(for: animal)
        return LazyVGrid(columns: [GridItem(.flexible(), spacing: 15), GridItem(.flexible(), spacing: 20)], spacing: 20) {
            ForEach(opts, id: \.
self) { option in
                Button {
                    if selectedOption == nil { checkAnswer(option, correctAnswer: animal.englishName) }
                } label: {
                    Text(option)
                        .font(.headline)
                        .fontWeight(.medium)
                        .padding(.vertical, 18)
                        .frame(maxWidth: .infinity)
                        .background(buttonBackgroundColor(for: option, correct: animal.englishName))
                        .foregroundColor(.white)
                        .cornerRadius(12)
                        .shadow(color: .black.opacity(0.15), radius: 3, x: 0, y: 2)
                }
                .disabled(selectedOption != nil)
            }
        }
        .padding(.top, 20)
        .padding(.horizontal, 20)
    }

    private func nextButton() -> some View {
        Group {
            if selectedOption != nil {
                Button(vm.currentIndex + 1 < vm.animals.count ? "Следующий вопрос" : "Завершить игру") {
                    nextQuestion()
                }
                .font(.headline.bold())
                .padding()
                .frame(maxWidth: .infinity)
                .background(Color.blue.opacity(0.8))
                .foregroundColor(.white)
                .cornerRadius(12)
                .padding(.horizontal, 20)
                .padding(.top, 25)
                .shadow(color: .black.opacity(0.15), radius: 3, x: 0, y: 2)
            }
        }
    }

    // MARK: - Logic helpers
    private func options(for animal: AnimalContent) -> [String] {
        if let cached = cachedOptions[animal.id] { return cached }
        var pool = vm.animals.map { $0.englishName }
        pool.removeAll(where: { $0 == animal.englishName })
        pool.shuffle()
        let distractors = Array(pool.prefix(optionsPerQuestion - 1))
        var arr = distractors + [animal.englishName]
        arr.shuffle()
        cachedOptions[animal.id] = arr
        return arr
    }
    @State private var cachedOptions: [String: [String]] = [:]

    private func checkAnswer(_ option: String, correctAnswer: String) {
        selectedOption = option
        let correct = option == correctAnswer
        isCorrect = correct
        vm.submitAnswer(questionId: vm.currentAnimal?.id ?? "", userAnswer: option, isCorrect: correct, timeSpent: 0) // TODO: time
        if let idx = vm.currentIndex, idx < roundResults.count {
            roundResults[idx] = correct ? .correct : .incorrect
        }
    }

    private func nextQuestion() {
        selectedOption = nil
        isCorrect = nil
        if vm.currentIndex + 1 < vm.animals.count {
            vm.currentIndex += 1 // Access via published property
        } else {
            // vm will mark isFinished
        }
    }

    private func resetGame() {
        selectedOption = nil
        isCorrect = nil
        vm.startGame()
    }

    private func buttonBackgroundColor(for option: String, correct: String) -> Color {
        let defaultColor = Color(white: 0.25, opacity: 0.9)
        let disabledLookColor = Color(white: 0.4, opacity: 0.7)
        guard let sel = selectedOption else { return defaultColor }
        if sel == option {
            return isCorrect == true ? Color.green.opacity(0.8) : Color.red.opacity(0.8)
        } else {
            if option == correct && isCorrect == false {
                return Color.green.opacity(0.8)
            }
            return disabledLookColor
        }
    }

    private func score() -> Int {
        roundResults.filter { $0 == .correct }.count
    }
}

// MARK: - Supporting enums & previews
private enum RoundResultStatus {
    case pending, correct, incorrect
}

struct GuessAnimalGameScreen_Previews: PreviewProvider {
    static var previews: some View {
        GuessAnimalGameScreen()
    }
}
