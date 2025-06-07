//
//  GameView.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import SwiftUI
import Combine

enum GameType: Hashable, Identifiable {
    case sentence
    case animal

    var id: Self { self }
}

struct GameView: View {
    @State private var selectedGame: GameType?
    @Binding var hideTabBar: Bool
    @Environment(\.presentationMode) var presentationMode
    
    let borderWidth: CGFloat = 6
    
    // Инициализатор по умолчанию для случаев, когда binding не передается
    init(hideTabBar: Binding<Bool>? = nil) {
        self._hideTabBar = hideTabBar ?? .constant(false)
    }
    
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
            .navigationDestination(item: $selectedGame) { game in
                switch game {
                case .sentence:
                    // Свойство для скрытия TabBar при переходе на экран игры
                    SentenceGameScreen()
                        .hideCustomTabBar() // Используем наш новый модификатор
                case .animal:
                    // Скрываем TabBar также и для игры с животными
                    AnimalGuessGameScreen()
                        .hideTabBar() // Используем наш новый модификатор
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
