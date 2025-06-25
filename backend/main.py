# backend/main.py (FastAPI version)
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
# Это должно быть сделано до импорта других модулей, которые могут использовать эти переменные
load_dotenv()

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Импорт инфраструктурных компонентов
# Заменяем старый импорт на новый
from shared.firebase_client import initialize_app_for_context, _DEFAULT_APP_NAME

# Импорт роутеров
from routers.profile_router import router as profile_router
from routers.session_router import router as session_router
from routers.progress_router import router as progress_router
from routers.content_router import router as content_router
from routers.achievement_router import router as achievement_router

# --- Firebase Startup Event ---

# --- Создание FastAPI приложения ---
app = FastAPI(
    title="EasyTalk API",
    description="API сервер для детского образовательного приложения EasyTalk",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initializes Firebase on application startup."""
    print("[main.py] FastAPI app startup: Initializing Firebase...")
    # The initialize_app_for_context function will now determine the environment by itself.
    initialize_app_for_context()
    print("[main.py] Firebase initialized on startup.")
    # Seed initial game content if collections are empty
    try:
        from scripts.seed_games import seed_if_empty
        await seed_if_empty()
    except Exception as e:
        print(f"[main.py] Warning: seeding initial content failed: {e}")

# --- Настройка CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Подключение роутеров ---
app.include_router(profile_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
# Эндпоинты контента (content) и достижений (achievement)
app.include_router(content_router, prefix="/api")
app.include_router(achievement_router, prefix="/api")


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности API."""
    return {
        "message": "EasyTalk API работает",
        "docs": "/docs",
        "status": "ok"
    }
# --- Запуск локального сервера ---
if __name__ == "__main__":
    # Для запуска локально: python main.py
    # Или можно использовать напрямую: uvicorn main:app --reload --host 0.0.0.0 --port 8080
    # Для режима перезагрузки (reload) нужно передавать имя модуля в виде строки
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), reload=True)
    print("\n FastAPI сервер запущен на http://localhost:8080")
    print("\n Документация API доступна по адресу http://localhost:8080/docs")
