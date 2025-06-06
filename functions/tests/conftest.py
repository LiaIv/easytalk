# tests/conftest.py
import os
import pytest
from firebase_admin import initialize_app, delete_app, get_app
from firebase_admin import firestore

from shared.firebase_client import get_firestore

# Настраиваем переменные окружения для тестов
os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:9090'
os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = 'localhost:9099'
os.environ['DEBUG'] = 'True'

# Константы для тестов
TEST_USER_ID = "test_user_123"


@pytest.fixture(scope="session")
def firebase_app():
    """
    Фикстура для инициализации Firebase App для тестов
    """
    # Пытаемся получить уже инициализированное приложение или создаем новое
    try:
        app = get_app()
        yield app
    except ValueError:
        app = initialize_app(name="testapp")
        yield app
    finally:
        try:
            delete_app(app)
        except ValueError:
            pass


@pytest.fixture(scope="function")
def firestore_client(firebase_app):
    """
    Фикстура для доступа к Firestore в тестах
    """
    return get_firestore()


@pytest.fixture(scope="function")
def clean_firestore(firestore_client):
    """
    Фикстура для очистки тестовых данных в Firestore перед и после каждого теста
    """
    # Список коллекций, которые нужно очистить перед и после тестов
    collections_to_clean = ["users", "sessions", "achievements", "progress"]
    
    # Очищаем перед тестом
    for collection in collections_to_clean:
        docs = firestore_client.collection(collection).limit(100).stream()
        for doc in docs:
            doc.reference.delete()
    
    # Запускаем тест
    yield
    
    # Очищаем после теста
    for collection in collections_to_clean:
        docs = firestore_client.collection(collection).limit(100).stream()
        for doc in docs:
            doc.reference.delete()


@pytest.fixture(scope="function")
def test_user_id():
    """
    Фикстура, возвращающая тестовый ID пользователя
    """
    return TEST_USER_ID


@pytest.fixture(scope="function")
def mock_auth_header():
    """
    Фикстура, возвращающая заголовок авторизации для тестов
    """
    return {"Authorization": f"Bearer TEST_TOKEN"}
