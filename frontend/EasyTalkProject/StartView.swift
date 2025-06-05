import SwiftUI
import Foundation

struct StartView: View {
    // Состояние авторизации
    @State private var isUserLoggedIn = false
    
    var body: some View {
        // Проверка состояния авторизации
        Group {
            if isUserLoggedIn {
                // Если пользователь авторизован - перенаправляем на GameView
                NavigationView {
                    Text("Переход к экрану игр")
                        .onAppear {
                            // Добавляем небольшую задержку для перехода
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                                // Переходим к EasyTalkProjectApp и меняем там корневой экран на GameView
                                UserDefaults.standard.set(true, forKey: "showGameView")
                                NotificationCenter.default.post(name: Notification.Name("SwitchToGameView"), object: nil)
                            }
                        }
                }
            } else {
                // Если не авторизован - показываем экран авторизации
                AuthView()
            }
        }
        .onAppear {
            // Проверяем статус при загрузке экрана
            checkLoginStatus()
        }
    }
    
    // Проверка статуса авторизации пользователя
    private func checkLoginStatus() {
        // Проверяем, сохранен ли статус авторизации в UserDefaults
        if UserDefaults.standard.bool(forKey: "isUserLoggedIn") {
            // Пользователь был авторизован ранее
            isUserLoggedIn = true
        } else {
            // Пользователь не авторизован
            isUserLoggedIn = false
        }
    }
}

// Расширение для сохранения состояния авторизации
extension UserDefaults {
    // Метод для установки статуса авторизации
    static func setLoggedIn(value: Bool) {
        UserDefaults.standard.set(value, forKey: "isUserLoggedIn")
        UserDefaults.standard.synchronize()
    }
}

#Preview {
    StartView()
}
