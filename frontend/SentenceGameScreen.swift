//
//  SentenceGameScreen.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 14.04.2025.
//

import SwiftUI

enum LanguageLevel {
    case beginner
    case preIntermediate
    case intermediate
}

struct SentenceGameScreen: View {
    @State private var currentIndex: Int = 0
    @State private var correctSentence: String = ""
    @State private var shuffledWords: [String] = []
    @State private var userSentence: [String] = []
    @State private var showNext: Bool = false
    @State private var message: String = ""
    @Environment(\.dismiss) private var dismiss
    @State private var progressColors: [Color] = Array(repeating: .gray, count: 10)
    
    @State private var currentLevel: LanguageLevel = .intermediate
    
    var beginnerSentences: [String] = [
        "I have a cat.",
        "She is my sister.",
        "This is my book.",
        "We like pizza.",
        "He is a doctor.",
        "The sun is yellow.",
        "I am happy today.",
        "My name is Anna.",
        "They are good friends.",
        "I like this movie."
    ]
    
    var preIntermediateSentences: [String] = [
        "I usually have breakfast at 8 a.m.",
        "She is reading a book right now.",
        "We went to the park yesterday.",
        "They are playing football in the garden.",
        "He doesn't like spicy food.",
        "My best friend lives in another city.",
        "It was very cold last winter.",
        "I want to buy a new phone.",
        "We are planning a trip to Italy.",
        "She can speak three languages."
    ]
    
    var intermediateSentences: [String] = [
        "If it rains tomorrow, we will stay at home.",
        "She has been working here for five years.",
        "I wish I could travel more often.",
        "They had already left when I arrived.",
        "You should call him before visiting.",
        "Although he was tired, he finished the project.",
        "We might go hiking next weekend.",
        "The movie was so boring that we left early.",
        "He promised that he would help me with the homework.",
        "By the time we got to the station, the train had already departed."
    ]
    
    var selectedSentences: [String] {
        switch currentLevel {
        case .beginner:
            return beginnerSentences
        case .preIntermediate:
            return preIntermediateSentences
        case .intermediate:
            return intermediateSentences
        }
    }
    
    var body: some View {
        VStack(spacing: 20) {
            HStack(spacing: 10) {
                ForEach(0..<10, id: \.self) { index in
                    Circle()
                        .fill(progressColors[index])
                        .frame(width: 20, height: 20)
                        .overlay(
                            Circle()
                                .stroke(Color.black.opacity(0.2), lineWidth: 1)
                        )
                }
            }

            Text("Составь предложение")
                .font(.title)
                .transition(.opacity.combined(with: .slide))
                .animation(.easeInOut(duration: 0.4), value: userSentence)

            ZStack(alignment: .leading) {
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 100)

                if userSentence.isEmpty {
                    Text("Перетащи слова сюда")
                        .foregroundColor(.gray)
                        .padding(.leading)
                } else {
                    ScrollView(.horizontal) {
                        HStack {
                            ForEach(userSentence, id: \.self) { word in
                                Text(word)
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 5)
                                    .background(Color.green.opacity(0.3))
                                    .cornerRadius(8)
                                    .transition(.scale.combined(with: .opacity))
                                    .animation(.spring(), value: userSentence)
                            }
                        }
                        .padding()
                    }
                }
            }
            .padding(.horizontal)

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
                .padding()
                .background(Color.blue.opacity(0.2))
                .cornerRadius(10)
            }

            Spacer()

            WrapWordsView(words: shuffledWords, onWordTap: { word in
                withAnimation(.spring()) {
                    userSentence.append(word)
                    shuffledWords.removeAll { $0 == word }
                }
            })
            .padding()
        }
        .padding()
        .onAppear {
            loadNewSentence()
        }
        .alert(isPresented: $showNext) {
            Alert(
                title: Text(currentIndex + 1 < selectedSentences.count ? "Следующее предложение." : "Ты завершил игру."),
                message: Text(message),
                dismissButton: .default(Text("OK")) {
                    if currentIndex + 1 < selectedSentences.count {
                        currentIndex += 1
                        loadNewSentence()
                    } else {
                        dismiss()
                    }
                }
            )
        }
    }
    
    func loadNewSentence() {
        let sentence = selectedSentences[currentIndex]
        correctSentence = sentence.trimmingCharacters(in: .punctuationCharacters)
        shuffledWords = correctSentence.components(separatedBy: " ").shuffled()
        userSentence = []
    }
    
    func checkSentence() {
        let user = userSentence.joined(separator: " ")
        let isCorrect = (user + "." == correctSentence + ".")
        progressColors[currentIndex] = isCorrect ? .green : .red
        message = isCorrect ? "Верно!" : "Не верно."
        showNext = true
    }
}

struct WrapWordsView: View {
    let words: [String]
    let onWordTap: (String) -> Void

    var body: some View {
        VStack {
            let columns = [GridItem(.adaptive(minimum: 80))]
            LazyVGrid(columns: columns, spacing: 10) {
                ForEach(words, id: \.self) { word in
                    Text(word)
                        .padding()
                        .background(Color.blue.opacity(0.2))
                        .cornerRadius(10)
                        .onTapGesture {
                            onWordTap(word)
                        }
                        .transition(.scale)
                        .animation(.spring(), value: words)
                }
            }
        }
    }
}

#Preview {
    SentenceGameScreen()
}

