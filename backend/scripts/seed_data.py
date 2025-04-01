#!/usr/bin/env python
"""
Скрипт для загрузки начальных данных в MongoDB для разработки и тестирования.
Запуск: uv run python -m scripts.seed_data
"""

import asyncio
import datetime
import uuid
from pymongo import MongoClient

from app.config.settings import settings
from app.application.use_cases.auth_use_case import AuthUseCase
from app.infrastructure.persistence.mongodb.user_repository import MongoDBUserRepository
from app.infrastructure.persistence.mongodb.achievement_repository import MongoDBachievementRepository


async def seed_users():
    """Создание тестовых пользователей."""
    print("Создание тестовых пользователей...")
    client = MongoClient(settings.MONGO_URI)
    user_repository = MongoDBUserRepository(client=client)
    auth_use_case = AuthUseCase(user_repository=user_repository)
    
    # Проверяем, существует ли пользователь
    test_user = await user_repository.get_by_email("test@example.com")
    
    if not test_user:
        print("Создание тестового пользователя...")
        try:
            await auth_use_case.register(
                username="testuser",
                email="test@example.com",
                password="password123",
                first_name="Test",
                last_name="User"
            )
            print("Тестовый пользователь создан успешно!")
        except ValueError as e:
            print(f"Ошибка при создании пользователя: {e}")
    else:
        print("Тестовый пользователь уже существует.")


async def seed_achievements():
    """Создание достижений."""
    print("Создание достижений...")
    client = MongoClient(settings.MONGO_URI)
    achievement_repository = MongoDBachievementRepository(client=client)
    
    # Пример достижений
    achievements = [
        {
            "id": str(uuid.uuid4()),
            "name": "Первые шаги",
            "description": "Завершите свою первую игру",
            "icon_url": "/assets/achievements/first_steps.png",
            "experience_reward": 50,
            "required_games": 1,
            "created_at": datetime.datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Словарный запас",
            "description": "Достигните точности 80% в игре на словарный запас",
            "icon_url": "/assets/achievements/vocabulary.png",
            "experience_reward": 100,
            "required_accuracy": 80.0,
            "created_at": datetime.datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Уровень 5",
            "description": "Достигните 5 уровня",
            "icon_url": "/assets/achievements/level5.png",
            "experience_reward": 200,
            "required_level": 5,
            "created_at": datetime.datetime.utcnow()
        }
    ]
    
    # Добавляем достижения в базу данных
    collection = client[settings.MONGO_DB_NAME]["achievements"]
    for achievement in achievements:
        # Проверяем, существует ли достижение с таким именем
        existing = await collection.find_one({"name": achievement["name"]})
        if not existing:
            await collection.insert_one(achievement)
            print(f"Достижение '{achievement['name']}' добавлено.")
        else:
            print(f"Достижение '{achievement['name']}' уже существует.")


async def main():
    """Основная функция для запуска всех seed-функций."""
    print(f"Подключение к MongoDB: {settings.MONGO_URI}")
    
    # Создаем необходимые коллекции, если они не существуют
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    collections = ["users", "game_sessions", "achievements"]
    
    for coll_name in collections:
        if coll_name not in db.list_collection_names():
            db.create_collection(coll_name)
            print(f"Создана коллекция '{coll_name}'")
    
    # Запускаем seed-функции
    await seed_users()
    await seed_achievements()
    
    print("Загрузка начальных данных завершена!")


if __name__ == "__main__":
    asyncio.run(main())
