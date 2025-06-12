# EasyTalk

## О проекте

EasyTalk — это образовательное iOS-приложение для детей 8-13 лет, разрабатываемое как монорепозиторий с бэкендом на FastAPI (Python) и фронтендом на SwiftUI. Основная цель проекта — повысить мотивацию к изучению английского языка через игровые механики, визуальную обратную связь и систему достижений.

## Архитектура проекта

Проект следует принципам чистой архитектуры (Clean Architecture) с четким разделением ответственности и упрощенным подходом:

### Доменный слой (Domain)

- Содержит бизнес-модели (`UserModel`, `SessionModel`, `ProgressRecord`, `AchievementModel`)
- Определяет основные сущности и их поведение
- Не зависит от внешних фреймворков и библиотек

### Слой репозиториев (Repositories)

- Предоставляет интерфейсы для работы с данными
- Реализует взаимодействие с Firestore
- Инкапсулирует операции CRUD для всех сущностей

### Слой сервисов (Services)

- Реализует бизнес-логику приложения
- Координирует работу между репозиториями
- Реализует механики достижений (`Perfect Streak`, `Weekly Fifty`)

### Слой API (Routers)

- Предоставляет REST API для взаимодействия с клиентами
- Обрабатывает HTTP-запросы и возвращает ответы
- Обеспечивает аутентификацию и авторизацию

## Функциональность

### Мини-игры

- **Guess the Animal**: выбор правильного названия на основе изображения или аудиоподсказки
- **Build a Sentence**: составление предложений из перемешанных слов

### Отслеживание прогресса

- Ежедневное отслеживание очков и правильных ответов
- Визуализация прогресса в профиле пользователя
- Аналитика успеваемости по неделям

### Система достижений

- **Perfect Streak**: за 10 правильных ответов подряд
- **Weekly Fifty**: за набор 50 очков за неделю

### Фронтенд (планируется)

- **Swift/SwiftUI** для iOS-приложения

## Установка и запуск

### Требования

- Python 3.9 или выше
- Firebase CLI (для эмуляторов Firebase)
- pip или другой менеджер зависимостей Python
- poetry (для управления зависимостями)

### Настройка окружения

1. Клонирование репозитория:

   ```bash
   git clone https://github.com/yourusername/easytalk.git
   cd easytalk
   ```

2. Переход в директорию backend и установка зависимостей:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   # или venv\Scripts\activate  # для Windows
   pip install -r requirements.txt

   # Также мы используем поетри и тут другой способ
   poetry install
   ```

3. Настройка Firebase эмуляторов:

   ```bash
   # Установите Firebase CLI (если ещё не установлен)
   npm install -g firebase-tools
   
   # Запустите эмуляторы Firebase (из корня проекта)
   firebase emulators:start
   ```

4. Добавьте файл с учетными данными Firebase:

   Создайте файл `backend/shared/serviceAccountKey.json` с учетными данными вашего проекта Firebase.

### Устаревший способ: Запуск сервера для разработки (см. новый раздел ниже)

1. Сначала установите переменные окружения для подключения к эмуляторам:

   ```bash
   export FIRESTORE_EMULATOR_HOST=localhost:8080
   export FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
   export GOOGLE_APPLICATION_CREDENTIALS="./shared/serviceAccountKey.json"
   export DEBUG=True
   ```

2. Запустите FastAPI приложение:

   ```bash
   cd backend  # если вы еще не в этой директории
   uvicorn main:app --reload --port 8080
   # или другой вариант через poetry
   poetry run uvicorn main:app --reload
   ```

После запуска, API будет доступно по адресу: `http://localhost:8080`

Документация Swagger UI: `http://localhost:8080/docs`  
Альтернативная документация ReDoc: `http://localhost:8080/redoc`

## Локальная разработка с эмуляторами Firebase

Для локальной разработки и тестирования бэкенда EasyTalk использует эмуляторы Firebase для Auth и Firestore.

### 1. Настройка переменных окружения (.env)

В директории `backend/` создайте файл `.env` со следующим содержимым. Этот файл будет автоматически загружаться при старте приложения для конфигурации эмуляторов:

```env
FIRESTORE_EMULATOR_HOST=localhost:9090
FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
GCLOUD_PROJECT=easytalk-emulator
# DEBUG=True # Раскомментируйте для дополнительного вывода отладочной информации
```

**Важно:** Убедитесь, что порты (`9090` для Firestore, `9099` для Auth) соответствуют тем, что указаны в вашей конфигурации `firebase.json`.

### 2. Запуск эмуляторов Firebase

Перед запуском бэкенд-приложения необходимо запустить эмуляторы Firebase. Выполните команду из **корневой директории проекта** (`/Users/ruzaliia/Apps/easytalk/`):

```bash
firebase emulators:start
```

Это запустит локальные версии Firestore, Firebase Auth и других сервисов, если они настроены. Обычно UI эмуляторов доступен по адресу `http://localhost:4000`.

### 3. Запуск FastAPI бэкенда

После запуска эмуляторов, перейдите в директорию `backend/` и запустите FastAPI приложение с помощью Poetry и Uvicorn:

```bash
cd backend
poetry run uvicorn main:app --reload
```

Сервер будет доступен по адресу `http://127.0.0.1:8000` (или `http://localhost:8000`). Документация API (Swagger UI) будет доступна по адресу `http://localhost:8000/docs`.

### 4. Получение Firebase ID Токена для тестирования API

Для доступа к защищенным эндпоинтам API требуется Firebase ID токен, переданный в заголовке `Authorization: Bearer <ID_TOKEN>`.

#### А. Получение токена от ЭМУЛЯТОРА Firebase Auth

Это наиболее удобный способ для локального тестирования с Postman или другими HTTP-клиентами.

1. **Создайте пользователя в эмуляторе Auth:**

  - **Через UI эмулятора:** Откройте `http://localhost:4000` в браузере, перейдите на вкладку "Authentication" и добавьте нового пользователя (например, `test@example.com` с паролем `password123`).
  - **Через REST API (например, Postman):**
    - **URL:** `POST http://localhost:9099/identitytoolkit.googleapis.com/v1/accounts?key=ANY_STRING_CAN_BE_USED_AS_KEY_FOR_EMULATOR`
    - **Тело (JSON):**

      ```json
      {
        "email": "test@example.com",
        "password": "password123",
        "returnSecureToken": false
      }
      ```

1. **Войдите пользователем и получите ID токен (через REST API):**

  - **URL:** `POST http://localhost:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=ANY_STRING_CAN_BE_USED_AS_KEY_FOR_EMULATOR`
  - **Тело (JSON):**

    ```json
        {
          "email": "test@example.com",
          "password": "password123",
          "returnSecureToken": true
        }
    ```

  - В ответе на этот запрос будет поле `idToken`. Скопируйте его значение.

1. **Используйте токен:** Вставляйте полученный `idToken` в заголовок `Authorization` ваших запросов к API:
    `Authorization: Bearer <idToken_полученный_на_шаге_2>`

#### Б. Получение токена от РЕАЛЬНОГО проекта Firebase (через клиентское приложение)

Если вам нужно протестировать взаимодействие с реальным (не эмуляторным) проектом Firebase, токен должен быть сгенерирован клиентским приложением (например, вашим iOS-приложением), которое настроено на работу с этим реальным проектом.

1. Убедитесь, что ваше клиентское приложение (iOS) корректно настроено для работы с вашим продакшн/девелопмент проектом Firebase (правильный `GoogleService-Info.plist`).
2. Реализуйте в клиентском приложении логику входа пользователя через Firebase Authentication.
3. После успешного входа пользователя получите его ID токен. Пример для Swift (iOS):

  ```swift
    import FirebaseAuth

    Auth.auth().currentUser?.getIDTokenResult(forcingRefresh: true) { result, error in
        if let error = error {
            print("Error getting ID token: \(error.localizedDescription)")
            return
        }
        guard let token = result?.token else {
            print("No token found")
            return
        }
        print("Firebase ID Token (for REAL project): \(token)")
        // Этот токен можно передать на бэкенд или использовать для тестов
    }
    ```

    Этот токен затем можно использовать для отправки запросов к вашему API, если оно настроено на работу с тем же реальным проектом Firebase.

## Структура проекта

```bash
/easytalk/
├── .git/               # Git-репозиторий
├── .gitignore          # Общие исключения для репозитория
├── README.md           # Этот файл с документацией
├── backend/            # Бэкенд на FastAPI
│   ├── domain/         # Доменные модели (UserModel, SessionModel и т.д.)
│   ├── repositories/   # Репозитории для работы с Firestore
│   ├── routers/        # FastAPI роутеры (API эндпоинты)
│   ├── services/       # Слой бизнес-логики
│   ├── shared/         # Общие компоненты и утилиты
│   │   └── config.py   # Конфигурация приложения
│   ├── tests/          # Тесты
│   │   ├── domain/     # Тесты доменных моделей
│   │   ├── repositories/ # Тесты репозиториев
│   │   ├── routers/   # Тесты API эндпоинтов
│   │   └── services/  # Тесты сервисов
│   ├── main.py         # Точка входа FastAPI приложения
│   └── requirements.txt # Зависимости проекта
└── frontend/          # Фронтенд на iOS (SwiftUI)
```

## API эндпоинты

Все API эндпоинты имеют префикс `/api`

### Профиль пользователя

- `GET /api/profile` — получение информации о профиле пользователя
- `PUT /api/profile` — обновление профиля пользователя

### Игровые сессии

- `POST /api/session/start` — начало игровой сессии
- `PATCH /api/session/finish` — завершение игровой сессии
- `GET /api/session/active` — получение активной сессии пользователя

### Прогресс

- `POST /api/progress` — запись прогресса пользователя
- `GET /api/progress` — получение прогресса пользователя
- `GET /api/progress/weekly-summary` — получение сводки по неделям

### Контент

- `GET /api/content/animals` — получение списка животных для игры Guess the Animal

## Технологический стек

### Бэкенд

- **Python** — основной язык программирования
- **FastAPI** — веб-фреймворк для создания API
- **Pydantic** — валидация данных и сериализация
- **Firebase Admin SDK** — взаимодействие с Firebase Auth и Firestore
- **Pytest** — тестирование
- **Uvicorn** — ASGI-сервер для запуска FastAPI приложений

Аутентификация реализована с использованием Firebase Auth и JWT-токенов. Для доступа к защищенным эндпоинтам требуется заголовок `Authorization: Bearer <token>` с валидным Firebase ID-токеном.

## Запланированные улучшения

- Интеграция с Firebase для push-уведомлений
- Улучшенная аналитика прогресса обучения
- Система рекомендаций для персонализированного обучения
- Социальные функции (соревнования, рейтинги)
- iOS-приложение с интуитивным интерфейсом

## Тестирование

### Запуск тестов

Перед запуском тестов убедитесь, что вы находитесь в виртуальном окружении и установили необходимые переменные окружения:

```bash
export FIRESTORE_EMULATOR_HOST=localhost:8080
export FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
export GOOGLE_APPLICATION_CREDENTIALS="./shared/serviceAccountKey.json"
export DEBUG=True
```

Запуск всех тестов:

```bash
cd backend
pytest
```

Запуск конкретного модуля тестов:

```bash
pytest tests/routers/test_profile_router.py -v
```

Проект содержит более 100 тестов, покрывающих доменные модели, репозитории, сервисы и API эндпоинты.

## Лицензия

Проект распространяется под лицензией MIT. Подробности см. в файле LICENSE.

## Контакты

По вопросам и предложениям по проекту:

- GitHub: [LiaIv/easytalk](https://github.com/LiaIv/easytalk)

## Шпаргалка по запуску

### 1. Запуск эмуляторов Firebase

```bash
# В корневой директории проекта
firebase emulators:start
```

### 2. Запуск FastAPI приложения

```bash
# Переход в директорию backend
cd /Users/ruzaliia/Apps/easytalk/backend

# Активация виртуального окружения
source venv/bin/activate

# Экспорт переменных для эмуляторов
export FIRESTORE_EMULATOR_HOST=localhost:8080
export FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
export GOOGLE_APPLICATION_CREDENTIALS="./shared/serviceAccountKey.json"
export DEBUG=True

# Запуск FastAPI приложения
uvicorn main:app --reload --port 8080
```
