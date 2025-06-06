# functions/main.py (FastAPI version)
import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Импорт инфраструктурных компонентов
from shared.firebase_client import initialize_firebase

# Импорт роутеров
from routers.profile_router import router as profile_router
from routers.session_router import router as session_router
from routers.progress_router import router as progress_router
from routers.content_router import router as content_router

# --- Инициализация Firebase Admin SDK ---
initialize_firebase()

# --- Создание FastAPI приложения ---
app = FastAPI(
    title="EasyTalk API",
    description="API сервер для детского образовательного приложения EasyTalk",
    version="1.0.0"
)

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
app.include_router(content_router, prefix="/api")


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
    # Или можно использовать: uvicorn main:app --reload --host 0.0.0.0 --port 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), reload=True)
    print("\n FastAPI сервер запущен на http://localhost:8080")
    print("\n Документация API доступна по адресу http://localhost:8080/docs")
