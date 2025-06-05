//
//  AnimalGuessGameScreen.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 14.04.2025.
//

import SwiftUI

struct Animal: Identifiable, Equatable {
    let id = UUID()
    let name: String
    let imageName: String
    let options: [String]
    
    static func == (lhs: Animal, rhs: Animal) -> Bool {
        lhs.id == rhs.id
    }
}

struct AnimalGuessGameScreen: View {
    @State private var animals: [Animal] = [
        Animal(name: "Cat", imageName: "avatar", options: ["Cat", "Dog", "Rabbit", "Hamster"]),
        Animal(name: "Dog", imageName: "avatar", options: ["Elephant", "Dog", "Lion", "Tiger"]),
        Animal(name: "Rabbit", imageName: "avatar", options: ["Fox", "Wolf", "Rabbit", "Squirrel"])
    ]
    
    @State private var currentIndex = 0
    @State private var score = 0
    @State private var showingResult = false
    @State private var selectedOption: String? = nil
    @State private var isCorrect: Bool? = nil
    @Environment(\.dismiss) private var dismiss
    
    var currentAnimal: Animal {
        animals[currentIndex]
    }
    
    var body: some View {
        ZStack {
            Color(red: 230/255, green: 245/255, blue: 255/255)
                .ignoresSafeArea()
            
            VStack(spacing: 20) {
                Text("Угадай животное")
                    .font(.title)
                    .fontWeight(.bold)
                    .padding()
                
                Image(currentAnimal.imageName)
                    .resizable()
                    .scaledToFit()
                    .frame(height: 200)
                    .cornerRadius(10)
                    .shadow(radius: 5)
                    .padding()
                
                Text("Что это за животное?")
                    .font(.headline)
                    .padding()
                
                VStack(spacing: 15) {
                    ForEach(currentAnimal.options, id: \.self) { option in
                        Button(action: {
                            checkAnswer(option)
                        }) {
                            Text(option)
                                .font(.title3)
                                .padding()
                                .frame(maxWidth: .infinity)
                                .background(
                                    selectedOption == option ?
                                    (isCorrect == true ? Color.green : Color.red) :
                                    Color.blue.opacity(0.6)
                                )
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                        .disabled(selectedOption != nil)
                    }
                }
                .padding()
                
                if selectedOption != nil {
                    Button("Следующий вопрос") {
                        nextQuestion()
                    }
                    .font(.headline)
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .padding()
                }
                
                Text("Счет: \(score)/\(animals.count)")
                    .font(.headline)
                    .padding()
            }
            .padding()
        }
        .alert("Игра завершена!", isPresented: $showingResult) {
            Button("Начать заново", role: .cancel) {
                resetGame()
            }
            Button("Выйти") {
                dismiss()
            }
        } message: {
            Text("Ваш результат: \(score) из \(animals.count)")
        }
    }
    
    func checkAnswer(_ option: String) {
        selectedOption = option
        isCorrect = option == currentAnimal.name
        
        if isCorrect == true {
            score += 1
        }
    }
    
    func nextQuestion() {
        if currentIndex + 1 < animals.count {
            currentIndex += 1
            selectedOption = nil
            isCorrect = nil
        } else {
            showingResult = true
        }
    }
    
    func resetGame() {
        currentIndex = 0
        score = 0
        selectedOption = nil
        isCorrect = nil
    }
}

#Preview {
    AnimalGuessGameScreen()
}
