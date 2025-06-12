import SwiftUI

// Data Models
struct Animal: Identifiable {
    let id = UUID()
    let name: String
    let imageName: String // Should be actual image names from assets
    let options: [String]
}

enum RoundResultStatus {
    case pending, correct, incorrect
}

// Progress Dots View
struct ProgressDotsView: View {
    let totalRounds: Int
    let roundResults: [RoundResultStatus]
    
    var body: some View {
        HStack(spacing: 6) { // Reduced spacing
            ForEach(0..<totalRounds, id: \.self) { index in
                Circle()
                    .frame(width: 10, height: 10) // Smaller dots
                    .foregroundColor(dotColor(for: index))
            }
        }
    }
    
    private func dotColor(for index: Int) -> Color {
        guard index < roundResults.count else { return Color.gray.opacity(0.4) } // Default for out of bounds
        
        switch roundResults[index] {
        case .pending:
            return Color.gray.opacity(0.4) // Light gray for pending, as in screenshot
        case .correct:
            return .green
        case .incorrect:
            return .red
        }
    }
}

struct AnimalGuessGameScreen: View {
    private let totalRounds = 10

    // User will need to update these with actual data and themed images
    @State private var animals: [Animal] = [
        Animal(name: "Fish", imageName: "fish_placeholder", options: ["Fish", "Lion", "Frog", "Cat"]),
        Animal(name: "Dog", imageName: "dog_placeholder", options: ["Elephant", "Dog", "Lion", "Tiger"]),
        Animal(name: "Rabbit", imageName: "rabbit_placeholder", options: ["Fox", "Wolf", "Rabbit", "Squirrel"]),
        Animal(name: "Bear", imageName: "bear_placeholder", options: ["Bear", "Panda", "Koala", "Grizzly"]),
        Animal(name: "Monkey", imageName: "monkey_placeholder", options: ["Chimpanzee", "Gorilla", "Orangutan", "Monkey"]),
        Animal(name: "Lion", imageName: "lion_placeholder", options: ["Lion", "Tiger", "Leopard", "Jaguar"]),
        Animal(name: "Elephant", imageName: "elephant_placeholder", options: ["Elephant", "Rhino", "Hippo", "Mammoth"]),
        Animal(name: "Panda", imageName: "panda_placeholder", options: ["Panda", "Red Panda", "Sloth", "Koala"]),
        Animal(name: "Fox", imageName: "fox_placeholder", options: ["Fox", "Wolf", "Coyote", "Dingo"]),
        Animal(name: "Tiger", imageName: "tiger_placeholder", options: ["Tiger", "Lion", "Panther", "Cheetah"])
    ]
    
    @State private var currentIndex = 0
    @State private var score = 0
    @State private var showingResult = false
    @State private var selectedOption: String? = nil
    @State private var isCorrect: Bool? = nil
    @State private var roundResults: [RoundResultStatus]

    @Environment(\.dismiss) private var dismiss
    
    init() {
        // Initialize roundResults with pending status for all rounds
        _roundResults = State(initialValue: Array(repeating: .pending, count: totalRounds))
    }

    var currentAnimal: Animal {
        // Ensure currentIndex does not go out of bounds
        animals[min(currentIndex, animals.count - 1)]
    }
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // Light blue background
                Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.6)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Top Bar
                    HStack {
                        Button(action: { dismiss() }) {
                            Image(systemName: "chevron.left")
                                .font(.title2.weight(.medium))
                                .foregroundColor(Color(white: 0.2))
                        }
                        Spacer()
                        ProgressDotsView(totalRounds: totalRounds, roundResults: roundResults)
                        Spacer()
                        // Placeholder for right side to balance chevron.left
                        Image(systemName: "chevron.left").opacity(0) 
                            .font(.title2.weight(.medium))
                    }
                    .padding(.horizontal)
                    .padding(.top, geometry.safeAreaInsets.top > 0 ? 0 : 10) // Adjust top padding based on safe area
                    .padding(.bottom, 5)

                    // Animal Image
                    Image(currentAnimal.imageName)
                        .resizable()
                        .scaledToFit() 
                        .frame(height: geometry.size.height * 0.48) // Increased height for larger image
                        .background(Color.white.opacity(0.3)) // Placeholder background for image area
                        .cornerRadius(15)
                        .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
                        .padding(.horizontal, 10)
                        .padding(.top, 10) // Опускаем изображение немного вниз
                        .padding(.bottom, 15)
                    
                    // Reveal Answer Area
                    Text(selectedOption != nil ? currentAnimal.name : "Какое это животное?")
                        .font(selectedOption != nil ? .title.bold() : .title2.weight(.medium))
                        .foregroundColor(Color(white: 0.25))
                        .padding(.vertical, 22) // Increased vertical padding for taller reveal area
                        .frame(maxWidth: .infinity)
                        .background(Color(white: 0.88, opacity: 0.9))
                        .cornerRadius(12)
                        .padding(.horizontal, 20)
                        .padding(.bottom, 15) // Reduced bottom padding to bring buttons closer
                    // Spacer() // Removed Spacer to raise options grid up

                    // Answer Options Grid
                    LazyVGrid(columns: [GridItem(.flexible(), spacing: 15), GridItem(.flexible(), spacing: 20)], spacing: 20) {
                        ForEach(currentAnimal.options, id: \.self) { option in
                            Button(action: {
                                if selectedOption == nil { checkAnswer(option) }
                            }) {
                                Text(option)
                                    .font(.headline)
                                    .fontWeight(.medium)
                                    .padding(.vertical, 18)
                                    .frame(maxWidth: .infinity)
                                    .background(buttonBackgroundColor(for: option))
                                    .foregroundColor(.white)
                                    .cornerRadius(12)
                                    .shadow(color: .black.opacity(0.15), radius: 3, x: 0, y: 2)
                            }
                            // Disable other buttons after an option is selected, but still show correct if user was wrong
                            .disabled(selectedOption != nil && option != selectedOption && !(option == currentAnimal.name && isCorrect == false) )
                        }
                    }
                    .padding(.top, 20) // Опускаем кнопки вниз
                    .padding(.horizontal, 20) // Горизонтальные отступы для сетки
                    
                    // Next Question / Finish Game Button
                    if selectedOption != nil {
                        Button(currentIndex + 1 < totalRounds ? "Следующий вопрос" : "Завершить игру") {
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
                    
                    Spacer() // Spacer at the bottom
                }
            }
        }
        #if os(iOS)
        .toolbar(.hidden, for: .navigationBar) // Hides the standard navigation bar (iOS 16+)
        #endif
        .alert("Игра завершена!", isPresented: $showingResult) {
            Button("Начать заново", role: .cancel) { resetGame() }
            Button("Выйти") { dismiss() }
        } message: {
            Text("Ваш результат: \(score) из \(totalRounds)")
        }
    }
    
    func buttonBackgroundColor(for option: String) -> Color {
        let defaultColor = Color(white: 0.25, opacity: 0.9)
        let disabledLookColor = Color(white: 0.4, opacity: 0.7)

        guard let selOpt = selectedOption else {
            return defaultColor // Default button color before any selection
        }
        
        // An option has been selected
        if selOpt == option { // This is the button that was tapped
            return isCorrect == true ? Color.green.opacity(0.8) : Color.red.opacity(0.8)
        } else { // Other buttons not tapped
            // If the user was wrong, highlight the correct answer in green
            if option == currentAnimal.name && isCorrect == false { 
                 return Color.green.opacity(0.8)
            }
            // Otherwise, make other non-tapped buttons look inactive
            return disabledLookColor 
        }
    }

    func checkAnswer(_ option: String) {
        selectedOption = option
        let correct = option == currentAnimal.name
        isCorrect = correct
        
        if correct {
            score += 1
            if currentIndex < roundResults.count { roundResults[currentIndex] = .correct }
        } else {
            if currentIndex < roundResults.count { roundResults[currentIndex] = .incorrect }
        }
    }
    
    func nextQuestion() {
        if currentIndex + 1 < totalRounds {
            currentIndex += 1
            selectedOption = nil // Reset for the next question
            isCorrect = nil
        } else {
            showingResult = true // All rounds finished
        }
    }
    
    func resetGame() {
        currentIndex = 0
        score = 0
        selectedOption = nil
        isCorrect = nil
        // Reset round results to pending
        roundResults = Array(repeating: .pending, count: totalRounds) 
    }
}

#Preview("Animal Guess Game iOS") { // Имя превью задается здесь
    NavigationView { // Оборачиваем в NavigationView для контекста, если экран обычно пушится
        AnimalGuessGameScreen()
    }
    // Выбор устройства для превью осуществляется через Canvas Xcode
}
