//
//  EasyTalkProjectApp.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 28.03.2025.
//

import SwiftUI
import Firebase

// Добавляем ключ для передачи видимости TabBar через Environment
struct TabBarHiddenKey: EnvironmentKey {
    static var defaultValue: Bool = false
}

// Расширяем EnvironmentValues для управления видимостью TabBar
extension EnvironmentValues {
    var tabBarHidden: Bool {
        get { self[TabBarHiddenKey.self] }
        set { self[TabBarHiddenKey.self] = newValue }
    }
}

@main
struct EasyTalkProjectApp: App {
    
    @UIApplicationDelegateAdaptor private var appDelegate: AppDelegate
    @State private var showGameView = false
    
    init() {
        // Проверяем сохраненные настройки при запуске
        // Устанавливаем начальное значение для флага showGameView
        _showGameView = State(initialValue: UserDefaults.standard.bool(forKey: "showGameView"))
    }
    
    var body: some Scene {
        WindowGroup {
            if showGameView {
                // При повторном входе или после авторизации показываем MainTabBar с возможностью переключения между экранами
                if let user = AuthService.shared.currentUser {
                    MainTabBar(viewModel: MainTabBarViewModel(user: user))
                } else {
                    // Фаллбэк, показываем TabBar с экраном игр по умолчанию
                    TabView {
                        GameView()
                            .tabItem {
                                Image(systemName: "gamecontroller.circle")
                                Text("мини-игры")
                            }
                        
                        EducationView()
                            .tabItem {
                                Image(systemName: "book")
                                Text("учебник")
                            }
                        
                        ProfileView()
                            .tabItem {
                                Image(systemName: "person")
                                Text("профиль")
                            }
                    }
                }
            } else {
                // При первом входе или после выхода показываем стартовый экран
                StartView()
            }
        }
    }
    
    class AppDelegate: NSObject, UIApplicationDelegate {
        
        func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
            
            FirebaseApp.configure()
            print("App Delegete")
            
            return true
        }
    }
}
