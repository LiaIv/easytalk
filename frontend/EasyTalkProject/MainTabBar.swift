//
//  MainTabBar.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import SwiftUI

struct MainTabBar: View {
    
    var viewModel: MainTabBarViewModel
    // Состояние для выбора вкладки по умолчанию
    @State private var selectedTab = 1 // Устанавливаем на игры (индекс 1)
    
    // Менеджер видимости TabBar
    @State private var hideTabBar = false
    
    var body: some View {
        ZStack {
            TabView(selection: $selectedTab) {
                // Возвращаем оригинальный порядок вкладок, но используем выбор по умолчанию
                EducationView()
                    .tabItem {
                        Label {
                            Text("учебник")
                        } icon: {
                            Image(systemName: selectedTab == 0 ? "book.fill" : "book")
                        }
                    }
                    .tag(0)
                
                GameView(hideTabBar: $hideTabBar) // Передаём байндинг для управления видимостью TabBar
                    .tabItem {
                        Label {
                            Text("мини-игры")
                        } icon: {
                            Image(systemName: selectedTab == 1 ? "gamecontroller.fill" : "gamecontroller")
                        }
                    }
                    .tag(1)
                
                ProfileView()
                    .tabItem {
                        Label {
                            Text("профиль")
                        } icon: {
                            Image(systemName: selectedTab == 2 ? "person.fill" : "person")
                        }
                    }
                    .tag(2)
            }
            // Применяем модификаторы стиля
            .accentColor(Color.blue) // Цвет выбранной вкладки
            .background(
                ZStack {
                    // Добавляем фон таббару в нижней части
                    VStack {
                        Spacer()
                        if !hideTabBar {
                            // Добавляем фон для TabBar с тенью
                            Rectangle()
                                .fill(Color(red: 0.97, green: 0.98, blue: 1.0))
                                .frame(height: 50)
                                .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: -2)
                        }
                    }
                }
            )
        }
        // Отслеживаем изменения видимости TabBar
        .onChange(of: hideTabBar) { _, newValue in
            // Обновляем UI при изменении видимости
            if newValue {
                // Если TabBar скрыт, делаем дополнительные настройки если нужно
            }
        }
    }
}
