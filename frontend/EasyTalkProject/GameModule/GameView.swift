//
//  GameView.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import SwiftUI

struct GameView: View {
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
                    NavigationLink(destination: SentenceGameScreen()) {
                        GameButton(title: "Составь предложение", borderWidth: borderWidth)
                    }

                    // Кнопка "Угадай животное"
                    NavigationLink(destination: AnimalGuessGameScreen()) {
                        GameButton(title: "Угадай животное", borderWidth: borderWidth)
                    }

                    Spacer()
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
                .contentShape(Rectangle()) // Важно для клика по всей области

            Text(title)
                .font(.custom("Georgia", size: 28))
                .foregroundColor(Color("colorGameText"))
        }
    }
}


#Preview {
    GameView()
}
