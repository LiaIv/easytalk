//
//  EnglishLevelView.swift
//  EasyTalkProject
//
//  Created on 09.05.2025.
//

import SwiftUI
// Импортируем необходимые зависимости

struct EnglishLevelView: View {
    @State private var selectedLevel: EnglishLevel?
    @State private var navigateToNextScreen = false
    @Binding var userEmail: String
    
    // Добавляем Environment object для закрытия экрана
    @Environment(\.presentationMode) var presentationMode
    
    enum EnglishLevel: String, CaseIterable {
        case beginner = "Начинающий"
        case intermediate = "Средний"
        case advanced = "Продвинутый"
        
        var emoji: String {
            switch self {
            case .beginner: return "🐤"
            case .intermediate: return "🎓"
            case .advanced: return "🦉"
            }
        }
    }
    
    var body: some View {
        VStack(spacing: 30) {
            Text("Какой у вас уровень английского?")
                .font(.system(size: 28, weight: .bold))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 20)
                .padding(.top, 50)
            
            ForEach(EnglishLevel.allCases, id: \.self) { level in
                Button {
                    selectedLevel = level
                } label: {
                    HStack {
                        Text(level.emoji)
                            .font(.system(size: 24))
                            .padding(.trailing, 10)
                        
                        Text(level.rawValue)
                            .font(.system(size: 20, weight: .medium))
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(selectedLevel == level ? Color("orange") : Color.clear, lineWidth: 2)
                    )
                }
                .buttonStyle(PlainButtonStyle())
                .padding(.horizontal, 20)
            }
            
            Spacer()
            
            Button {
                if selectedLevel != nil {
                    // Здесь можно сохранить выбранный уровень в профиле пользователя
                    navigateToNextScreen = true
                }
            } label: {
                Text("Далее")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(
                        selectedLevel != nil ?
                        LinearGradient(colors: [Color("yellow"), Color("orange")], startPoint: .leading, endPoint: .trailing) :
                        LinearGradient(colors: [Color.gray.opacity(0.5), Color.gray.opacity(0.7)], startPoint: .leading, endPoint: .trailing)
                    )
                    .cornerRadius(12)
                    .padding(.horizontal, 20)
                    .padding(.bottom, 30)
                    .font(.title3.bold())
                    .foregroundStyle(.black)
            }
            .disabled(selectedLevel == nil)
            .onChange(of: navigateToNextScreen) { _, newValue in
                if newValue {
                    // Здесь можно добавить логику сохранения выбранного уровня
                    // Для примера: UserDefaults.standard.set(selectedLevel?.rawValue, forKey: "userEnglishLevel")
                    
                    // Закрыть этот экран
                    presentationMode.wrappedValue.dismiss()
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color("lightBlue").edgesIgnoringSafeArea(.all))
    }
}

#Preview {
    EnglishLevelView(userEmail: .constant("test@example.com"))
}
