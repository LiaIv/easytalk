import SwiftUI

/// New game screen that builds a sentence from shuffled words using real backend data.
struct BuildSentenceGameScreen: View {
    @StateObject private var vm = BuildSentenceViewModel()
    @EnvironmentObject var toast: ToastManager
    @Environment(\.dismiss) private var dismiss

    // UI State
    @State private var shuffledWords: [String] = []
    @State private var userSentence: [String] = []
    @State private var flashColor: Color? = nil
    @State private var showAlert: Bool = false
    @State private var alertMessage: String = ""
    @State private var progressColors: [Color] = []

    var body: some View {
        ZStack {
            (flashColor ?? Color(red: 230/255, green: 245/255, blue: 255/255))
                .ignoresSafeArea()
                .animation(.easeInOut(duration: 0.3), value: flashColor)

            if vm.isLoading {
                ProgressView("Загрузка…")
            } else if let sentence = vm.currentSentence {
                VStack(spacing: 16) {
                    topBar
                    progressDots
                    Text("Составь предложение")
                        .font(.title).bold()

                    sentenceArea
                    actionButtons
                    Spacer()
                    wordsGrid
                }
                .padding()
            } else if let error = vm.error {
                VStack {
                    Text(error).foregroundColor(.red)
                    Button("Повторить") { vm.startGame() }
                }
            }
        }
        // Alerts
        .alert(isPresented: $showAlert) {
            Alert(title: Text(alertTitle), message: Text(alertMessage), dismissButton: .default(Text("OK")) {
                proceedToNext()
            })
        }
        // Session finished alert
        .alert("Игра завершена!", isPresented: $vm.isFinished) {
            Button("Начать заново", role: .cancel) { resetGame() }
            Button("Выйти") { dismiss() }
        } message: {
            Text("Ваш результат: \(score()) из \(vm.sentences.count)")
        }
        .onAppear {
            vm.startGame()
        }
        .onChange(of: vm.sentences) { new in
            progressColors = Array(repeating: .gray, count: new.count)
        }
        .onChange(of: vm.currentIndex) { _ in
            loadCurrentSentence()
        }
        .onChange(of: vm.error) { _ in
            if let msg = vm.error {
                toast.show(msg)
            }
        }
    }

    // MARK: - Subviews
    private var topBar: some View {
        HStack {
            Button { dismiss() } label: {
                Image(systemName: "chevron.left").font(.title2.weight(.medium))
            }
            Spacer()
        }
        .padding(.horizontal)
        .foregroundColor(Color(white: 0.2))
    }

    private var progressDots: some View {
        HStack(spacing: 10) {
            ForEach(progressColors.indices, id: \.self) { idx in
                Circle()
                    .fill(progressColors[idx])
                    .frame(width: 20, height: 20)
                    .overlay(Circle().stroke(Color.black.opacity(0.5), lineWidth: 1))
            }
        }
    }

    private var sentenceArea: some View {
        ZStack(alignment: .leading) {
            RoundedRectangle(cornerRadius: 10)
                .fill(Color.gray.opacity(0.15))
                .frame(height: 200)

            if userSentence.isEmpty {
                Text("Нажми на слово для добавления")
                    .foregroundColor(.gray)
                    .padding(.leading)
            } else {
                WrapWordsView(words: userSentence, userSentence: .constant([])) { _ in }
                    .padding()
            }
        }
        .padding(.horizontal)
    }

    private var wordsGrid: some View {
        WrapWordsView(words: shuffledWords, userSentence: $userSentence) { word in
            withAnimation(.spring()) {
                userSentence.append(word)
                shuffledWords.removeAll { $0 == word }
            }
        }
        .padding()
    }

    private var actionButtons: some View {
        HStack {
            Button("Очистить") {
                withAnimation {
                    shuffledWords += userSentence
                    userSentence.removeAll()
                }
            }
            .padding()
            .background(Color.red.opacity(0.2))
            .cornerRadius(10)

            Button("Готово") {
                checkSentence()
            }
            .disabled(!isSentenceComplete())
            .padding()
            .background(Color.blue.opacity(0.2))
            .cornerRadius(10)
        }
    }

    // MARK: - Helpers
    private func loadCurrentSentence() {
        guard let sentence = vm.currentSentence else { return }
        shuffledWords = sentence.words.shuffled()
        userSentence = []
    }

    private func isSentenceComplete() -> Bool {
        guard let sentence = vm.currentSentence else { return false }
        return userSentence.count == sentence.words.count
    }

    private func checkSentence() {
        guard let sentence = vm.currentSentence else { return }
        let assembled = userSentence.joined(separator: " ")
        let correct = assembled == sentence.sentence

        alertMessage = correct ? "Верно!" : "Неверно."
        showAlert = true

        withAnimation {
            if correct {
                flashColor = Color.green.opacity(0.3)
                progressColors[vm.currentIndex] = .green
            } else {
                flashColor = Color.red.opacity(0.3)
                progressColors[vm.currentIndex] = .red
            }
        }

        vm.submitAnswer(userSentence: assembled, isCorrect: correct, timeSpent: 0)

        // reset flash color later
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { flashColor = nil }
    }

    private var alertTitle: String {
        if vm.currentIndex + 1 < vm.sentences.count {
            return "Следующее предложение."
        } else {
            return "Ты завершил игру."
        }
    }

    private func proceedToNext() {
        if vm.currentIndex + 1 < vm.sentences.count {
            vm.currentIndex += 1
        } else {
            // finished, vm will handle isFinished
        }
    }

    private func resetGame() {
        vm.startGame()
    }

    private func score() -> Int {
        progressColors.filter { $0 == .green }.count
    }
}

// MARK: - Preview
struct BuildSentenceGameScreen_Previews: PreviewProvider {
    static var previews: some View {
        BuildSentenceGameScreen()
    }
}
