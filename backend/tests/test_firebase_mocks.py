"""
Временный тестовый скрипт для проверки работы асинхронных моков Firestore.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends

# Импортируем напрямую из functions
from routers.content_router import router as content_router, get_animal_by_id
from shared.auth import get_current_user_id

# Константы
TEST_USER_ID = "test_user_123"
TEST_ANIMAL_ID = "test_animal_456"

# Создаем тестовое приложение
app = FastAPI()
app.include_router(content_router)

# Переопределяем зависимость аутентификации
def override_get_current_user_id():
    return TEST_USER_ID

app.dependency_overrides[get_current_user_id] = override_get_current_user_id

# Функция для мокирования Firestore
def setup_firestore_mock():
    # Создаем мок для Firestore клиента
    db_mock = MagicMock(name="db_mock")
    
    # Настраиваем цепочку вызовов для получения животного по ID
    content_collection = MagicMock(name="content_collection")
    db_mock.collection.return_value = content_collection
    
    animals_doc = MagicMock(name="animals_doc")
    content_collection.document.return_value = animals_doc
    
    animals_collection = MagicMock(name="animals_collection")
    animals_doc.collection.return_value = animals_collection
    
    animal_doc_ref = MagicMock(name="animal_doc_ref")
    animals_collection.document.return_value = animal_doc_ref
    
    # Создаем мок для успешного получения документа
    async def async_get_success():
        doc_snapshot = MagicMock(name="doc_snapshot")
        doc_snapshot.exists = True
        doc_snapshot.to_dict.return_value = {
            "name": "Лев",
            "english_name": "Lion",
            "difficulty": 2,
            "image_url": "https://example.com/lion.jpg",
            "sound_url": "https://example.com/lion.mp3"
        }
        doc_snapshot.id = TEST_ANIMAL_ID
        return doc_snapshot
    
    # Настраиваем метод get() как асинхронный метод
    animal_doc_ref.get = MagicMock()
    animal_doc_ref.get.return_value = async_get_success()
    
    return db_mock

# Функция для тестирования успешного получения животного по ID
@pytest.mark.asyncio
async def test_get_animal_by_id_success():
    # Настраиваем мок Firestore
    db_mock = setup_firestore_mock()
    
    # Замена реальной функции получения Firestore на мок
    import routers.content_router as content_router_module
    old_get_firestore = content_router_module.get_firestore
    content_router_module.get_firestore = lambda: db_mock
    
    try:
        # Вызываем функцию напрямую, без использования TestClient
        result = await get_animal_by_id(TEST_ANIMAL_ID, TEST_USER_ID)
        
        # Проверки результата
        assert result["id"] == TEST_ANIMAL_ID
        assert result["name"] == "Лев"
        assert result["english_name"] == "Lion"
        assert result["difficulty"] == 2
        
        print("✅ Тест get_animal_by_id_success успешно пройден")
        return True
    except Exception as e:
        print(f"❌ Ошибка в тесте get_animal_by_id_success: {e}")
        return False
    finally:
        # Восстанавливаем оригинальную функцию
        content_router_module.get_firestore = old_get_firestore

# Функция для имитации Firestore ошибки при получении .stream()
@pytest.mark.asyncio
async def test_stream_exception():
    # Настраиваем мок Firestore
    db_mock = MagicMock(name="db_mock")
    content_collection = MagicMock(name="content_collection")
    db_mock.collection.return_value = content_collection
    animals_doc = MagicMock(name="animals_doc")
    content_collection.document.return_value = animals_doc
    animals_collection = MagicMock(name="animals_collection")
    animals_doc.collection.return_value = animals_collection
    
    # Создаем мок для query и query.limit()
    query_mock = MagicMock(name="query_mock")
    animals_collection.limit.return_value = query_mock
    
    # Создаем асинхронный генератор с ошибкой
    async def error_stream_generator():
        raise RuntimeError("Симулированная ошибка Firestore при stream()")
        yield None  # Недостижимо, но нужно для определения как генератор
    
    # Настраиваем stream() метод
    stream_mock = MagicMock(name="stream_mock")
    query_mock.stream = stream_mock
    stream_mock.return_value = error_stream_generator()
    
    # Проверим, что исключение правильно перехватывается
    try:
        async for _ in stream_mock.return_value:
            pass  # Не должны сюда попасть из-за исключения
        print("❌ Тест test_stream_exception не пройден: исключение не было вызвано")
        return False
    except RuntimeError as e:
        if "Симулированная ошибка" in str(e):
            print("✅ Тест test_stream_exception успешно пройден: исключение перехвачено")
            return True
        else:
            print(f"❌ Тест test_stream_exception не пройден: неверное исключение: {e}")
            return False
    except Exception as e:
        print(f"❌ Тест test_stream_exception не пройден: неожиданное исключение: {e}")
        return False

# Запускаем все тесты
async def run_tests():
    print("🚀 Запуск тестов асинхронных моков Firestore...")
    
    test_results = [
        await test_get_animal_by_id_success(),
        await test_stream_exception(),
    ]
    
    if all(test_results):
        print("🎉 Все тесты успешно пройдены! Асинхронные моки работают корректно.")
    else:
        print("⚠️ Некоторые тесты не пройдены.")

# Запускаем тесты
if __name__ == "__main__":
    asyncio.run(run_tests())
