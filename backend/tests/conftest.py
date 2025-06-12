# tests/conftest.py
import os
import pytest
import pytest_asyncio
# Импортируем новые функции из нашего firebase_client
from shared.firebase_client import (
    initialize_app_for_context as initialize_firebase_app,
    _DEFAULT_APP_NAME,
    get_firestore_client as get_admin_firestore_client 
)

_EMULATOR_PROJECT_ID = "easytalk-emulator" # Определяем локально
from firebase_admin import credentials, get_app as get_firebase_app, delete_app as delete_firebase_app, App as FirebaseApp
from google.cloud.firestore import Client as GoogleFirestoreClient # Используем клиент google-cloud-firestore напрямую
from google.cloud.firestore_v1.async_client import AsyncClient  # добавлен импорт асинхронного клиента

# Константы для тестов
TEST_USER_ID = "test_user_123"
EMULATOR_PROJECT_ID = "easytalk-emulator" # Определим константу

@pytest.fixture(scope="session", autouse=True)
def setup_emulator_environment():
    """
    Устанавливает переменные окружения для эмулятора для всей тестовой сессии.
    autouse=True гарантирует, что эта фикстура выполняется перед всеми остальными.
    """
    print("\n[CONTEST_DEBUG] Setting up emulator environment variables via autouse fixture.")
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:9090"
    os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "localhost:9099"
    os.environ["FIRESTORE_PROJECT_ID"] = _EMULATOR_PROJECT_ID


@pytest.fixture(scope="session")
def firebase_app_for_testing() -> FirebaseApp:
    print("\n[CONTEST_DEBUG] ENTERING firebase_app_for_testing fixture")
    """
    Инициализирует СТАНДАРТНОЕ Firebase приложение (_DEFAULT_APP_NAME) для тестов.
    Зависит от `setup_emulator_environment` для установки переменных окружения.
    """
    app_instance = initialize_firebase_app(is_emulator=True, project_id=_EMULATOR_PROJECT_ID, app_name=_DEFAULT_APP_NAME)
    print("[CONTEST_DEBUG] Firebase app initialized successfully in firebase_app_for_testing.")
    print("[CONTEST_DEBUG] EXITING firebase_app_for_testing fixture")
    return app_instance

@pytest.fixture(scope="session")
def firestore_client_for_testing() -> GoogleFirestoreClient:
    print("[CONTEST_DEBUG] ENTERING firestore_client_for_testing fixture")
    print("[CONTEST_DEBUG] Initializing Firestore client for testing...")
    """
    Предоставляет синхронный клиент Firestore для большинства тестов.
    """
    client = GoogleFirestoreClient(project=_EMULATOR_PROJECT_ID)
    return client

@pytest.fixture(scope="function")
def clean_firestore(firestore_client_for_testing: GoogleFirestoreClient):
    print("[CONTEST_DEBUG] ENTERING clean_firestore fixture (setup)")
    """Очищаем коллекции перед тестом и после."""
    for collection_name in ["users","sessions","progress","achievements"]:
        for doc in firestore_client_for_testing.collection(collection_name).stream():
            doc.reference.delete()
    yield firestore_client_for_testing
    for collection_name in ["users","sessions","progress","achievements"]:
        for doc in firestore_client_for_testing.collection(collection_name).stream():
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

from fastapi.testclient import TestClient
from main import app  # Путь к app относительно backend/

@pytest.fixture(scope="module")
def client():
    """
    Фикстура для предоставления TestClient для FastAPI приложения.
    """
    with TestClient(app) as c:
        yield c

# Фикстура для TestClient с переопределенной зависимостью get_db
@pytest.fixture
def test_client_overridden_db(clean_firestore):
    from main import app as main_fastapi_app  # Импортируем FastAPI app здесь, чтобы избежать проблем с порядком инициализации
    from shared.dependencies import get_db # Импортируем оригинальную зависимость
    from google.cloud.firestore import Client # Для тайп-хинта

    # ---- START DIAGNOSTIC PRINTS ----
    print(f"\n[CONTEST_DEBUG] Inside test_client_overridden_db fixture.")
    print(f"[CONTEST_DEBUG] main_fastapi_app object: {main_fastapi_app}")
    print(f"[CONTEST_DEBUG] type(main_fastapi_app): {type(main_fastapi_app)}")
    if hasattr(main_fastapi_app, 'dependency_overrides'):
        print(f"[CONTEST_DEBUG] main_fastapi_app.dependency_overrides before: {main_fastapi_app.dependency_overrides}")
    else:
        print(f"[CONTEST_DEBUG] main_fastapi_app has NO dependency_overrides attribute!")
    # ---- END DIAGNOSTIC PRINTS ----

    def get_db_override() -> Client:
        # clean_firestore это и есть экземпляр firestore_client_for_testing
        return clean_firestore # Возвращаем клиент из фикстуры clean_firestore

    # Сохраняем оригинальные переопределения ИМЕННО для main_fastapi_app
    original_overrides = main_fastapi_app.dependency_overrides.copy() 
    main_fastapi_app.dependency_overrides[get_db] = get_db_override

    # ---- START DIAGNOSTIC PRINTS ----
    if hasattr(main_fastapi_app, 'dependency_overrides'):
        print(f"[CONTEST_DEBUG] main_fastapi_app.dependency_overrides after: {main_fastapi_app.dependency_overrides}")
    # ---- END DIAGNOSTIC PRINTS ----
    
    # Создаем TestClient с main_fastapi_app
    client = TestClient(main_fastapi_app) 
    yield client
    
    # Восстанавливаем оригинальные переопределения для main_fastapi_app
    main_fastapi_app.dependency_overrides = original_overrides # Очищаем переопределения после теста
    print(f"[CONTEST_DEBUG] test_client_overridden_db fixture teardown complete.\n")

# Отдельный асинхронный клиент для тестов, требующих AsyncClient (репозиторий достижений)
@pytest_asyncio.fixture(scope="function")
async def async_firestore_client():
    """Возвращает AsyncClient, настроенный на эмулятор"""
    from google.auth.credentials import AnonymousCredentials
    client = AsyncClient(project=_EMULATOR_PROJECT_ID, credentials=AnonymousCredentials())
    yield client
    # Clean achievements collection
    async for doc in client.collection("achievements").stream():
        await doc.reference.delete()

# Добавляем clean_firestore_async fixture
@pytest_asyncio.fixture(scope="function")
async def clean_firestore_async(async_firestore_client: AsyncClient):
    """Очистка Firestore (AsyncClient) перед/после теста"""
    # Удаляем документы из коллекции achievements перед тестом
    async for doc in async_firestore_client.collection("achievements").stream():
        await doc.reference.delete()
    yield async_firestore_client
    async for doc in async_firestore_client.collection("achievements").stream():
        await doc.reference.delete()
