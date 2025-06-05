#!/bin/bash

# Путь к проекту
PROJECT_PATH="/Users/ruzaliia/Apps/easytalk/frontend"
PROJECT_FILE="EasyTalkProject.xcodeproj"

# Открываем проект в Xcode
echo "🚀 Открываю проект в Xcode..."
open -a Xcode "$PROJECT_PATH/$PROJECT_FILE"

# Открываем симулятор
echo "📱 Запускаю симулятор..."
open -a Simulator

echo "✅ Готово! Теперь нажмите кнопку Run (▶️) в Xcode, чтобы запустить приложение в симуляторе."
echo "💡 Совет: После внесения изменений в код, просто нажмите Cmd+R в Xcode для перезапуска приложения."
