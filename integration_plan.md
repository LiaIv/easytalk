# План интеграции фронта и бэка EasyTalk

> Версия: 2025-06-15

## 1. Подготовка окружений

### 1.1 Бэкенд
- Локально: `firebase emulators:start` (Firestore :9090, Auth :9099) → `poetry run uvicorn main:app --reload` из `backend/`.
- Прод: Cloud Run; образ из `backend/dockerfile`, порт 8080.

### 1.2 Фронтенд
- Xcode 15+, iOS 15+.
- Добавить `Config.plist` со строками `baseURL`, `useEmulators`, `firebaseProjectId`.
- Подключить Firebase SDK через SPM (Auth, Firestore, Messaging).

## 2. Синхронизация контрактов (OpenAPI ↔ Swift)

1. Генерация моделей и клиента:
   ```bash
   brew install openapi-generator
   openapi-generator generate \
     -g swift5 \
     -i ../openapi.json \
     -o ../frontend/ApiClient \
     --additional-properties=projectName=EasyTalkAPI,swiftPackagePathSources=Sources
   ```
2. Если генерация не подходит — вручную создать `Codable`-модели (`UserModel`, `SessionModel`, …) в `frontend/EasyTalkProject/Models`.
3. Декодер: `JSONDecoder.keyDecodingStrategy = .convertFromSnakeCase`.
4. Обновление спеки через git-тег `api-vX.Y` и команду `make update-spec`.

## 3. Слой Networking (Swift)

- **Пакет `Networking`** (SPM target)
  - `APIEndpoint` — enum, формирует `URLRequest`.
  - `APIClient` — `async func send<T: Decodable>(_ endpoint: APIEndpoint) -> T`.
  - Middleware: `AuthInterceptor`, `RetryPolicy` (3 попытки), `NetworkLogger` (DEBUG).
- Кэш `URLCache.shared` для GET контента ( сутки ).

## 4. Авторизация и токены

1. Расширить `AuthService.swift`:
   ```swift
   func idToken(forceRefresh: Bool = false) async throws -> String
   ```
2. `TokenProvider` кеширует токен + `expiryDate`.
3. При `401` → refresh → повтор запроса → logout при неудаче.
4. Первый логин: `GET /api/profile`; если 404 → `PUT /api/profile`.

## 5. Интеграция фич

### 5.1 Guess the Animal
1. `POST /api/session/start {game_type:"guess_animal"}`.
2. `GET /api/content/animals?difficulty&limit=10`.
3. Сохранять локально `RoundDetail`.
4. При завершении: `PATCH /api/session/finish?session_id=…` + тело `FinishSessionRequest`.
5. `POST /api/progress`.

### 5.2 Build a Sentence
- Аналогично, контент — `GET /api/content/sentences`.

### 5.3 Progress
- `GET /api/progress/weekly-summary` → SwiftCharts.

### 5.4 Achievements
- Использовать weekly-summary; позже эндпоинт `/api/achievements`.

### 5.5 Профиль
- `PUT /api/profile` для изменения данных.

## 6. Обработка ошибок и UX

- `APIError` enum: `.network`, `.unauthorized`, `.validation`, `.server`, `.unknown`.
- Toast для нет критических ошибок; Alert + Retry для критических.
- Логирование в Firebase Crashlytics.

## 7. Тестирование

- **Unit**: моки через `URLProtocolMock`.
- **UI**: сценарий login → session → finish → summary.
- **Контрактные**: Newman + OpenAPI в GitHub Actions.

## 8. CI/CD

- GitHub Actions:
  - `backend-test` → `pytest`.
  - `ios-build` → `xcodebuild`.
  - `contract-test` → newman.
  - `deploy-backend` → gcloud run deploy.
- Fastlane для TestFlight.

## 9. Roadmap (6 недель)

| Неделя | Задачи |
|--------|--------|
|1|Networking, модели, `/profile`|
|2|Guess the Animal end-to-end|
|3|Build a Sentence, `GameEngine`|
|4|Progress UI, Achievements v0|
|5|UX-полировка, локализация, Push|
|6|Интегр. тесты, CI/CD, TestFlight|

## 10. Риски и меры

- **Firestore latency** → индексы, пагинация.
- **Смена API** → file-lock `openapi.json`, semver.
- **Маленькие экраны** → адаптивный UI (`GeometryReader`).

## 11. Коммуникация

- Slack `#easytalk-sync`, daily 10 UTC.
- PR с изменениями `openapi.json` + Postman collection.
- Обновление UML в `diagrams/` перед sprint-review.
