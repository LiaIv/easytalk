//
//  GameView.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import SwiftUI

enum GameType: Hashable {
    case sentence
    case animal
}

struct GameView: View {
    @State private var selectedGame: GameType?
    let borderWidth: CGFloat = 6

    var body: some View {
        NavigationStack {
            ZStack {
                Image("backgroundGame")
                    .resizable()
                    .edgesIgnoringSafeArea(.all)

                VStack(spacing: 20) {
                    Spacer().frame(height: 80)

                    // Кнопка "Составь предложение"
                    Button {
                        selectedGame = .sentence
                    } label: {
                        GameButton(title: "Составь предложение", borderWidth: borderWidth)
                    }

                    // Кнопка "Угадай животное"
                    Button {
                        selectedGame = .animal
                    } label: {
                        GameButton(title: "Угадай животное", borderWidth: borderWidth)
                    }

                    Spacer()
                }
                .padding()
            }
            .navigationDestination(for: GameType.self) { game in
                switch game {
                case .sentence:
                    SentenceGameScreen()
                case .animal:
                    AnimalGuessGameScreen()
                }
            }
        }
    }
}

struct GameButton: View {
    let title: String
    let borderWidth: CGFloat

    var body: some View {
        ZStack {
            Image("backgroundGameOne")
                .resizable()
                .frame(width: 365, height: 152)
                .cornerRadius(20)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.white, lineWidth: borderWidth)
                )
                .contentShape(Rectangle())

            Text(title)
                .font(.custom("Georgia", size: 28))
                .foregroundColor(Color("colorGameText"))
        }
    }
}




#Preview {
    GameView()
}
