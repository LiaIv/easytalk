//
//  SentenceGameScreen.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 14.04.2025.
//

import SwiftUI

struct SentenceGameScreen: View {
    @State private var currentIndex: Int = 0
    @State private var correctSentence: String = ""
    @State private var shuffledWords: [String] = []
    @State private var userSentence: [String] = []
    @State private var showNext: Bool = false
    @State private var message: String = ""
    @Environment(\.dismiss) private var dismiss

    @State private var progressColors: [Color] = Array(repeating: .gray, count: 10)

    let beginnerSentences = [
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
                title: Text(currentIndex + 1 < beginnerSentences.count ? "Следующее предложение." : "Ты завершил игру."),
                message: Text(message),
                dismissButton: .default(Text("OK")) {
                    if currentIndex + 1 < beginnerSentences.count {
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
        let sentence = beginnerSentences[currentIndex]
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
