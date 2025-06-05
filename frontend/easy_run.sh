#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Запуск приложения EasyTalk в симуляторе${NC}"

# Запускаем симулятор
echo -e "${YELLOW}📲 Запуск симулятора iPhone...${NC}"
open -a Simulator

# Запускаем Xcode минимизированным
echo -e "${YELLOW}🔄 Запуск Xcode (минимизированно)...${NC}"
open -a Xcode -j /Users/ruzaliia/Apps/easytalk/frontend/EasyTalkProject.xcodeproj

echo -e "${GREEN}✅ Симулятор и Xcode запущены!${NC}"
echo -e "${BLUE}📱 Теперь нажмите кнопку ▶️ (Run) в Xcode или используйте сочетание клавиш Cmd+R${NC}"
echo -e "${YELLOW}⚠️ После внесения изменений в код в Windsurf, просто нажмите Cmd+R в Xcode для обновления приложения${NC}"
echo -e "${BLUE}💡 Вы можете продолжать работать в Windsurf, а Xcode будет работать в фоне${NC}"
