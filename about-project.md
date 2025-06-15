---
trigger: always_on
---

## EasyTalk — Образовательное iOS-приложение для детей 8–13 лет (монорепозиторий)

EasyTalk — это монорепозиторий, объединяющий два независимых, но согласованных проекта:

* **`backend/`** — FastAPI-сервис на Python 3.13 с Firebase Auth/Firestore.
* **`frontend/`** — iOS-приложение на SwiftUI + Combine.

Цель — повысить мотивацию к изучению английского языка через мини-игры, визуальный прогресс и систему достижений.

---

## Структура репозитория

```text
/easytalk/
├── backend/            # FastAPI, Pydantic, Firebase Admin SDK
│   ├── domain/         # Доменные модели
│   ├── repositories/   # Работа с Firestore
│   ├── services/       # Бизнес-логика (Streak, Weekly Fifty)
│   ├── routers/        # REST-эндпоинты (profile, session, progress, content)
│   ├── shared/         # Конфиг, Firebase client, утилиты
│   ├── tests/          # >100 pytest-тестов + эмуляторы Firebase
│   └── main.py         # Точка входа (Uvicorn)
├── frontend/
│   └── EasyTalkProject # SwiftUI-приложение, MVVM, Firebase Auth SDK
├── diagrams/           # PlantUML-диаграммы потоков и архитектуры
├── openapi.json        # Актуальная спецификация API (генерируется FastAPI)
├── integration_plan.md # Детальный план сквозной интеграции (обновлён)
└── README.md           # Быстрый старт и шпаргалка по запуску
```

---

## Ключевой функционал

1. **Мини-игры**
   * *Guess the Animal* — угадай животное по изображению/аудио.
   * *Build a Sentence* — собери предложение из перемешанных слов.
2. **Прогресс и достижения**
   * Ежедневный учёт очков, правильных ответов, времени.
   * Достижения *Perfect Streak* (10 подряд) и *Weekly Fifty* (50 очков/нед.).
3. **Профиль** — уровень, аватар, статистика.

---

## Архитектура

### Backend (Clean Architecture)

1. **Domain** — Pydantic-модели `UserModel`, `SessionModel`, `ProgressItem`.
2. **Repositories** — обёртки Firestore (`SessionRepository`, `UserRepository`).
3. **Services** — бизнес-правила (`SessionService`, `AchievementService`).
4. **Routers** — REST (`/api/profile`, `/api/session`, `/api/progress`, `/api/content`).
5. **Shared** — `firebase_client.py` централизует инициализацию Firebase Admin SDK.

OpenAPI-спека автоматически публикуется в `openapi.json` и используется для генерации Swift-моделей.

### Frontend (SwiftUI, MVVM)

* **Combine + async/await** для реактивных потоков.
* `AuthService.swift` — Firebase Auth (email/password).
* `Networking` (план) — универсальный `APIClient` с `AuthInterceptor` и `RetryPolicy`.
* Модули: AuthView, GameModule, EducationModule, ProfileModule.

---

## Данные и безопасность

* **Firestore коллекции:** `users`, `sessions`, `progress`, `achievements`, `content/animals`, `content/sentences`.
* Доступ к документам ограничен UID пользователя; контент игр — только чтение.
* Валидация полей (например, `RoundDetail[]` ровно 10 элементов).

---

## CI/CD и инфраструктура

| Среда        | Инструменты                                                         |
|--------------|---------------------------------------------------------------------|
| **Local**    | Firebase Emulator Suite, Poetry, Uvicorn --reload, SwiftUI Preview  |
| **Testing**  | Pytest (>100), Swift XCTest, Newman (контракт-тесты)                |
| **CI**       | GitHub Actions: backend-test, ios-build, contract-test, deploy      |
| **Deploy**   | Docker → Cloud Run (backend), Fastlane → TestFlight (iOS)           |

---

## Бизнес-правила

* **Perfect Streak** — вычисляется сервисом при 10 подряд правильных ответах.
* **Weekly Fifty** — суммирование очков за 7 дней (cron Cloud Function).
* **Надёжность** — оффлайн-кэш на фронте, серверная валидация, retry-механизм.

---

## Статус на 2025-06-15

* Миграция `functions/` → `backend/` завершена, все импорты обновлены.
* Покрытие тестами роутеров: `profile (12)`, `session (13)`, `progress (11)`.
* Итоговое количество тестов — >100 (домен, сервисы, API).
* Добавлен файл `integration_plan.md` с пошаговым планом интеграции.

---

EasyTalk объединяет современную UX, продуманный бэкенд и геймификацию, делая обучение английскому увлекательным и эффективным.

**Goal:** to increase motivation for learning English through game mechanics, visual feedback, and achievement systems.

---

## Key Features

* **Mini-Games:**

  1. *Guess the Animal* — choose the correct name based on an image or audio prompt.
  2. *Build a Sentence* — arrange shuffled words into grammatically correct sentences.

* **Progress & Achievements:**

  * Daily tracking of progress.
  * Awards for 10 correct answers in a row (*Perfect Streak*) and earning 50 points per week (*Weekly Fifty*).

* **Feedback:**

  * Immediate response validation.
  * Hints for incorrect answers.
  * Graphs and profile-based progress analysis.

---

## Architecture

### Client (iOS)

* **Technologies:** SwiftUI, Combine, MVVM.
* **Firebase SDK:** Authentication, Firestore, (optional) Storage.
* **Data Handling:**

  * CRUD via Firestore SDK.
  * HTTP API requests to FastAPI for business logic.
* **Main Screens:** Auth, Games, Learning, Profile.

### Server (FastAPI + Firebase)

* **Language:** Python 3.13 with FastAPI and Pydantic.

* **Backend Architecture (Layered):**

  1. **Domain:** Pydantic models (`UserModel`, `SessionModel`, `AchievementModel`, etc.).
  2. **Repository:** Firestore CRUD operations (`SessionRepository`, `UserRepository`).
  3. **Service:** Business logic (`SessionService`, `AchievementService`).
  4. **API:** Endpoints like `/start_session`, `/finish_session`, `/record_progress`, `/profile`, `/content/animals`.

* **Token Verification:** via `AuthService.verify_token()` using Firebase Admin SDK.

---

## Data Storage & Security

* **Firestore Collections:** `sessions`, `achievements`, `progress`, `users`, `content/animals`.
* **Security Rules:**

  * Users can access only their own documents.
  * Read-only access to `content/animals`.
  * Field validation (e.g., `details` array must contain exactly 10 items).

---

## Business Logic

* **Perfect Streak:** triggers when a user answers 10 questions correctly in a row.
* **Weekly Fifty:** calculated weekly if the total score ≥ 50 over the last 7 days (via FastAPI or Cloud Function).
* **Reliability:** offline caching, server-side validation, and optional Node.js Cloud Functions integration.

---

## Infrastructure

* **Local Development:**

  * Firebase Emulator Suite (Firestore, Auth),
  * FastAPI (`uvicorn --reload`),
  * Debugging via Postman and SwiftUI Preview.

* **CI/CD:** GitHub Actions + Fastlane, Docker, Pytest, Swift XCTest.

* **Production:**

  * FastAPI deployed on Cloud Run,
  * Cloud Functions used for background processing,
  * Firebase Firestore/Auth/Storage for data and authentication.

---

## Conclusion

**EasyTalk** is a scalable, secure, and interactive English-learning app designed for children. It combines a modern user experience, a reliable backend architecture, and motivational mechanics to make learning both engaging and effective.
