# EasyTalk — Образовательное приложение для изучения английского языка

## Общее описание

EasyTalk — образовательное iOS-приложение для детей 8-13 лет, направленное на повышение мотивации к изучению английского языка через игровую механику, визуальную обратную связь и систему достижений.

## Основные компоненты

### Клиент (iOS)

- **Технологии:** SwiftUI, Combine, MVVM
- **Firebase SDK:** Authentication, Firestore, (опционально) Storage
- **Обработка данных:**
  - CRUD через Firestore SDK
  - HTTP API запросы к FastAPI для бизнес-логики
- **Основные экраны:** Auth, Games, Learning, Profile

### Сервер (FastAPI + Firebase)

- **Язык:** Python 3.13 с FastAPI и Pydantic
- **Архитектура бэкенда (слоистая):**
  1. **Домен:** Pydantic-модели (`UserModel`, `SessionModel`, `AchievementModel`, и т.д.)
  2. **Репозитории:** Firestore CRUD операции (`SessionRepository`, `UserRepository`)
  3. **Сервисы:** Бизнес-логика (`SessionService`, `AchievementService`)
  4. **API:** Эндпоинты типа `/api/session/start`, `/api/session/finish`, `/api/progress`, `/api/profile`, `/api/content/animals`
- **Проверка токена:** через `AuthService.verify_token()` с использованием Firebase Admin SDK

### Мини-игры

1. **Угадай животное** — выбрать правильное название на основе изображения или аудио-подсказки
2. **Построй предложение** — составить грамматически правильные предложения из перемешанных слов

### Прогресс и достижения

- Ежедневное отслеживание прогресса
- Награды за 10 правильных ответов подряд (*Perfect Streak*) и набор 50 баллов за неделю (*Weekly Fifty*)

### Хранилище данных (Firestore)

- **Коллекции:** `sessions`, `achievements`, `progress`, `users`, `content/animals`
- **Правила безопасности:**
  - Пользователи могут получить доступ только к своим документам
  - Доступ только для чтения к `content/animals`
  - Валидация полей (напр., массив `details` должен содержать ровно 10 элементов)
