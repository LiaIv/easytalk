# tests/conftest.py
import os
import pytest
# Импортируем новые функции из нашего firebase_client
from shared.firebase_client import (
    initialize_app_for_context as initialize_firebase_app,
    _DEFAULT_APP_NAME,
    get_firestore_client as get_admin_firestore_client 
)

_EMULATOR_PROJECT_ID = "easytalk-emulator" # Определяем локально
from firebase_admin import credentials, get_app as get_firebase_app, delete_app as delete_firebase_app, App as FirebaseApp
from google.cloud.firestore import Client as GoogleFirestoreClient # Используем клиент google-cloud-firestore напрямую

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
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
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
def firestore_client_for_testing() -> GoogleFirestoreClient: # Обновляем тип возвращаемого значения
    print("[CONTEST_DEBUG] ENTERING firestore_client_for_testing fixture")
    print("[CONTEST_DEBUG] Initializing Firestore client for testing...")
    """
    Предоставляет клиент Firestore (google.cloud.firestore.Client), настроенный для эмулируемого Firestore.
    Использует AnonymousCredentials и project_id эмулятора.
    Фикстура firebase_app_for_testing гарантирует, что Firebase Admin SDK (например, для auth)
    также настроен для эмуляторов.
    """
    # Создаем клиент Firestore напрямую, полагаясь на переменные окружения эмулятора
    # (FIRESTORE_EMULATOR_HOST) и project_id, установленные в firebase_app_for_testing.
    # Это гарантирует, что клиент Firestore настроен для эмулятора независимо от того,
    # как firebase_admin.App обрабатывает учетные данные.
    # Убедимся, что FIRESTORE_EMULATOR_HOST и FIRESTORE_PROJECT_ID установлены до этого вызова.
    # Фикстура firebase_app_for_testing должна это обеспечивать, даже если она не передается сюда напрямую.
    if not os.getenv("FIRESTORE_EMULATOR_HOST"):
        raise RuntimeError("FIRESTORE_EMULATOR_HOST is not set. Ensure firebase_app_for_testing ran or set it manually.")
    if not os.getenv("FIRESTORE_PROJECT_ID"):
        # _EMULATOR_PROJECT_ID должен быть установлен в firebase_app_for_testing
        # или здесь, если firebase_app_for_testing не вызывается явно перед этой фикстурой.
        # Для безопасности установим его здесь, если он не установлен.
        os.environ["FIRESTORE_PROJECT_ID"] = _EMULATOR_PROJECT_ID
        print(f"[CONTEST_DEBUG] FIRESTORE_PROJECT_ID was not set, setting to: {_EMULATOR_PROJECT_ID}")

    client = GoogleFirestoreClient(project=_EMULATOR_PROJECT_ID)
    print(f"[CONTEST_DEBUG] GoogleFirestoreClient created with project_id: {_EMULATOR_PROJECT_ID} (EMULATOR MODE via google-cloud-firestore)")
    print("[CONTEST_DEBUG] GoogleFirestoreClient obtained successfully.")
    print("[CONTEST_DEBUG] EXITING firestore_client_for_testing fixture")
    return client

@pytest.fixture(scope="function")
def clean_firestore(firestore_client_for_testing: GoogleFirestoreClient):
    print("[CONTEST_DEBUG] ENTERING clean_firestore fixture (setup)")
    print("[CONTEST_DEBUG] Cleaning Firestore data before test...")
    """
    Фикстура для очистки тестовых данных в Firestore перед и после каждого теста.
    Возвращает firestore_client_for_testing.
    """
    collections_to_clear = [
        "users", "sessions", "progress", "achievements",
        # Для вложенных коллекций путь указывается относительно клиента Firestore
        # Например, если 'content' -> документ 'animals' -> коллекция 'items'
        # то путь будет 'content/animals/items'.
        # Здесь предполагается, что 'animals' и 'sentences' это коллекции под 'content'
        # или что это документы, а 'items' - их подколлекции.
        # Эта логика очистки может потребовать адаптации под точную структуру.
        "content/animals/items", 
        "content/sentences/items"
    ]

    # Перед тестом: очистка
    for path_str in collections_to_clear:
        parts = path_str.split('/')
        current_ref = firestore_client_for_testing
        ref_to_clear = current_ref # Начинаем с клиента
        is_collection_path = True
        for i, part_name in enumerate(parts):
            if i % 2 == 0: # Ожидается имя коллекции
                ref_to_clear = ref_to_clear.collection(part_name)
            else: # Ожидается имя документа
                ref_to_clear = ref_to_clear.document(part_name)
                if i == len(parts) - 1: # Если последний элемент - документ, это не путь к коллекции
                    is_collection_path = False
        
        if is_collection_path and hasattr(ref_to_clear, 'stream'): # Убедимся, что это ссылка на коллекцию
            docs = ref_to_clear.stream()
            for doc in docs:
                doc.reference.delete(recursive=True) # recursive=True для удаления подколлекций, если API поддерживает
                                                    # Стандартный delete не рекурсивен. Для полной очистки может потребоваться более сложная логика.

    yield firestore_client_for_testing # Предоставляем клиент тесту

    print("[CONTEST_DEBUG] ENTERING clean_firestore fixture (teardown)")
    print("[CONTEST_DEBUG] Cleaning Firestore data after test...")
    # Очистка после теста: снова очистка
    for path_str in collections_to_clear:
        parts = path_str.split('/')
        current_ref = firestore_client_for_testing
        ref_to_clear = current_ref
        is_collection_path = True
        for i, part_name in enumerate(parts):
            if i % 2 == 0:
                ref_to_clear = ref_to_clear.collection(part_name)
            else:
                ref_to_clear = ref_to_clear.document(part_name)
                if i == len(parts) - 1:
                    is_collection_path = False
        
        if is_collection_path and hasattr(ref_to_clear, 'stream'):
            docs = ref_to_clear.stream()
            for doc in docs:
                doc.reference.delete(recursive=True)

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
from backend.main import app  # Путь к app относительно backend/

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
    from backend.shared.dependencies import get_db # Импортируем оригинальную зависимость
    from google.cloud.firestore_v1.client import Client # Для тайп-хинта

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
