import SwiftUI

// Модификатор для скрытия TabBar при показе экрана игры
struct HideTabBarModifier: ViewModifier {
    
    // Применяем модификатор к представлению
    func body(content: Content) -> some View {
        #if os(iOS)
        content
            // Скрываем TabBar с помощью модификатора toolbar
            .toolbar(.hidden, for: .tabBar)
            // Растягиваем контент на весь экран, чтобы не было места для TabBar
            .edgesIgnoringSafeArea(.bottom)
        #else
        // Для других платформ просто возвращаем контент без изменений
        content
        #endif
    }
}

// Удобное расширение для View
extension View {
    // Функция для скрытия TabBar
    func hideTabBar() -> some View {
        self.modifier(HideTabBarModifier())
    }
}
