# Подробный план доработки клиентского кода EasyTalk (iOS)

> Дата: 2025-06-15

## 1. Инфраструктура проекта

1. Разбить `EasyTalkProject` на Swift-Package-модули:
   * **CoreModels**
   * **Networking**
   * **Auth**
   * **Games**
   * **Profile**
   * **Utilities**
2. Создать Xcode **workspace** и подключить SPM-зависимости.
3. Добавить **SwiftLint** и **swiftformat** в build-phase.

---

## 2. Модели (CoreModels)

1. Сгенерировать или вручную написать `Codable`-структуры по схемам OpenAPI.
2. Реализовать `Equatable` и `Hashable` для SwiftUI и тестов.
3. Покрыть unit-тестами декодирование JSON (fixtures).

---

## 3. Networking

1. Создать пакет **Networking**:
   * `APIEndpoint` enum (path, method, query/body).
   * `APIClient` — generic `async` отправка, обработка 2xx/4xx/5xx.
   * Middleware:
     - `AuthInterceptor` (ID-токен, refresh on 401).
     - `RetryPolicy` (эксп. бэкофф, 3 попытки).
     - `NetworkLogger` (DEBUG).
2. Включить `URLCache` для изображений и GET-ответов (1 сут.).
3. Unit-тесты Networking с `URLProtocolMock`.

---

## 4. Аутентификация и токены

1. Расширить `AuthService`:

   ```swift
   func idToken(forceRefresh: Bool = false) async throws -> String
   ```

2. Реализовать `TokenProvider` (Singleton с TTL, auto-refresh).
3. Общий `AuthViewModel` для SignUp / SignIn / ForgotPassword.

---

## 5. Игровые модули

1. Протокол `GameEngine` (start, nextQuestion, finish).
2. **Guess the Animal**:
   * Экран выбора уровня → `GET /api/content/animals`.
   * `POST /api/session/start` → сбор `RoundDetail[]` → `PATCH /api/session/finish`.
3. **Build a Sentence** — аналогично, контент `/api/content/sentences`.
4. Оффлайн-режим: кэш последнего контента.

---

## 6. UI & UX

1. Дизайн-система (Color, Typography, ButtonStyle).
2. Адаптивность через `GeometryReader` / `Layout`.
3. State-handling: `ObservableObject` + `@Published` + async/await.
4. Компонент Toast/Alert для `APIError`.
5. Локализация (RU/EN).

---

## 7. Прогресс и достижения

1. Экран графика: SwiftCharts + `/progress/weekly-summary`.
2. Стрик вычислять локально и серверно; UI-бейджи.
3. Позже — push-напоминания через FCM.

---

## 8. Тестирование

1. Unit-тесты: модели, Networking, ViewModels.
2. UI-тесты (XCTest) основного флоу: login → play → finish.
3. Контракт-тесты Newman + CI.

---

## 9. CI/CD

1. GitHub Actions:
   * lint + format
   * build + test
   * upload IPA
2. Fastlane lanes: beta (TestFlight) и release (App Store).
3. Бот авто-обновления `openapi.json` и генерации моделей.

---

## 10. Таймлайн (4 недели)

| Неделя | Задачи |
|-------|---------|
| 1 | Инфраструктура, модели, Auth |
| 2 | Networking, Guess the Animal (E2E) |
| 3 | Build a Sentence, Progress UI, кэш |
| 4 | UX-полировка, тесты, CI, TestFlight |
