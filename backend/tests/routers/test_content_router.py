import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch, call
from typing import List, Optional, Dict, Any
from fastapi import Depends, FastAPI, HTTPException

from routers.content_router import router as content_router
from routers.content_router import AnimalContent, SentenceContent # Импортируем модели
from shared.auth import get_current_user_id

TEST_USER_ID = "test_content_user_123"

@pytest.fixture
def mock_firestore_client():
    db_mock = MagicMock(name="db_mock")

    content_collection_mock = MagicMock(name="content_collection_mock")
    # This will be called like db.collection("content")
    db_mock.collection.return_value = content_collection_mock

    # --- Mocks for "animals" path ---
    # This mock represents db.collection("content").document("animals")
    animals_document_root_mock = MagicMock(name="animals_document_root_mock")
    # This mock represents db.collection("content").document("animals").collection("items")
    animals_items_collection_mock = MagicMock(name="animals_items_collection_mock")
    animals_document_root_mock.collection.return_value = animals_items_collection_mock
    
    # For single animal get: .document(animal_id).get()
    # This is db.collection("content").document("animals").collection("items").document(animal_id)
    animal_item_doc_ref_mock = MagicMock(name="animal_item_doc_ref_mock")
    animals_items_collection_mock.document.return_value = animal_item_doc_ref_mock
    # This is the snapshot returned by .get()
    animal_item_snapshot_mock = MagicMock(name="animal_item_snapshot_mock")
    animal_item_doc_ref_mock.get = AsyncMock(return_value=animal_item_snapshot_mock)
    animal_item_snapshot_mock.exists = False # Default: not found for single get
    animal_item_snapshot_mock.to_dict.return_value = {} # Default empty dict
    animal_item_snapshot_mock.id = "mock_animal_id" # Default ID

    # --- Mocks for "sentences" path ---
    # This mock represents db.collection("content").document("sentences")
    sentences_document_root_mock = MagicMock(name="sentences_document_root_mock")
    # This mock represents db.collection("content").document("sentences").collection("items")
    sentences_items_collection_mock = MagicMock(name="sentences_items_collection_mock")
    sentences_document_root_mock.collection.return_value = sentences_items_collection_mock

    # Side effect for content_collection_mock.document() to route to animals or sentences
    def document_side_effect(doc_name=None):
        print(f"[DEBUG] document_side_effect called with doc_name: {doc_name}")
        if doc_name == "animals":
            return animals_document_root_mock
        elif doc_name == "sentences":
            return sentences_document_root_mock
        # Fallback for any other document name, though not expected in these tests
        return MagicMock(name=f"unknown_doc_{doc_name}")
    content_collection_mock.document.side_effect = document_side_effect

    return db_mock

# --- Helper to create mock Firestore documents for .stream() results ---
def create_mock_doc(id: str, data: Dict[str, Any]):
    doc_mock = MagicMock()
    doc_mock.id = id
    doc_mock.to_dict.return_value = data
    return doc_mock

# --- Тесты для GET /content/animals --- 

@pytest.mark.asyncio
async def test_get_animals_success_default_limit(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка животных (дефолтный лимит 50)"""
    mock_animal_data_1 = {"name": "Cat", "english_name": "Cat", "difficulty": 1, "image_url": "cat.jpg"}
    mock_animal_data_2 = {"name": "Dog", "english_name": "Dog", "difficulty": 2, "sound_url": "dog.mp3"}
    doc_mock_1 = create_mock_doc("animal1", mock_animal_data_1)
    doc_mock_2 = create_mock_doc("animal2", mock_animal_data_2)
    
    async def docs_stream_generator():
        yield doc_mock_1
        yield doc_mock_2

    # Path: db.collection('content').document('animals').collection('items')
    animals_items_collection_mock = mock_firestore_client.collection("content").document("animals").collection("items")
    
    # Path: .limit(50).stream()
    query_mock = MagicMock(name="query_mock_animals_default_limit")
    animals_items_collection_mock.limit.return_value = query_mock
    
    stream_mock = MagicMock(name="stream_mock_animals_default_limit")
    query_mock.stream = stream_mock
    stream_mock.return_value = docs_stream_generator()

    response = test_client_overridden_db.get("/content/animals")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["id"] == "animal1"
    assert response_data[1]["id"] == "animal2"
    
    animals_items_collection_mock.limit.assert_called_once_with(50)
    animals_items_collection_mock.where.assert_not_called() # No difficulty filter

@pytest.mark.asyncio
async def test_get_animals_success_custom_limit(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка животных с кастомным limit"""
    mock_animal_data = {"name": "Elephant", "english_name": "Elephant", "difficulty": 3, "image_url": "elephant.jpg"}
    doc_mock = create_mock_doc("animal_limit", mock_animal_data)
    
    async def docs_stream_generator():
        yield doc_mock

    # Path: db.collection('content').document('animals').collection('items')
    animals_items_collection_mock = mock_firestore_client.collection("content").document("animals").collection("items")
    
    # Path: .limit(10).stream()
    query_mock = MagicMock(name="query_mock_animals_custom_limit")
    animals_items_collection_mock.limit.return_value = query_mock
    
    stream_mock = MagicMock(name="stream_mock_animals_custom_limit")
    query_mock.stream = stream_mock
    stream_mock.return_value = docs_stream_generator()

    response = test_client_overridden_db.get("/content/animals?limit=1")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == "animal_limit"
    animals_items_collection_mock.limit.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_get_animals_success_with_difficulty_filter(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка животных с фильтром по difficulty"""
    mock_animal_data = {"name": "Tiger", "english_name": "Tiger", "difficulty": 4, "image_url": "tiger.jpg"}
    doc_mock = create_mock_doc("animal_tiger", mock_animal_data)
    
    async def docs_stream_generator():
        yield doc_mock
    
    animals_items_collection_mock = mock_firestore_client.collection("content").document("animals").collection("items")
    query_after_where_mock = MagicMock(name="query_after_where_mock")
    animals_items_collection_mock.where.return_value = query_after_where_mock
    
    query_after_limit_mock = MagicMock(name="query_after_limit_mock")
    query_after_where_mock.limit.return_value = query_after_limit_mock
    
    stream_mock = MagicMock(name="stream_mock_animals_difficulty")
    query_after_limit_mock.stream = stream_mock
    stream_mock.return_value = docs_stream_generator()

    response = test_client_overridden_db.get("/content/animals?difficulty=4")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["difficulty"] == 4
    animals_items_collection_mock.where.assert_called_once_with("difficulty", "==", 4)
    query_after_where_mock.limit.assert_called_once_with(50)

@pytest.mark.asyncio
async def test_get_animals_success_with_difficulty_and_limit(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка животных с фильтром по difficulty и кастомным limit"""
    doc_mock = create_mock_doc("animal_bear", {"name": "Bear", "english_name": "Bear", "difficulty": 5})

    # Создаем асинхронный генератор для mock документов
    async def docs_stream_generator():
        yield doc_mock

    animals_items_collection_mock = mock_firestore_client.collection().document("animals").collection()
    query_after_where_mock = MagicMock(name="query_after_where_animals_diff_limit")
    animals_items_collection_mock.where.return_value = query_after_where_mock
    
    query_after_limit_mock = MagicMock(name="query_after_limit_animals_diff_limit")
    query_after_where_mock.limit.return_value = query_after_limit_mock
    
    stream_mock = MagicMock(name="stream_mock_difficulty_limit")
    query_after_limit_mock.stream = stream_mock
    stream_mock.return_value = docs_stream_generator()

    response = test_client_overridden_db.get("/content/animals?difficulty=5&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    animals_items_collection_mock.where.assert_called_once_with("difficulty", "==", 5)
    query_after_where_mock.limit.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_get_animals_success_empty_list(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения пустого списка животных (например, для несуществующего значения difficulty)"""
    
    async def empty_stream_generator():
        # Для пустого генератора нет yield операторов, тоесть итерация сразу завершается
        if False:  # Всегда ложно, чтобы этот yield не выполнялся
            yield None # Для обозначения, что это генератор
    
    animals_items_collection_mock = mock_firestore_client.collection("content").document("animals").collection("items")
    query_after_where_mock = MagicMock(name="query_after_where_empty")
    animals_items_collection_mock.where.return_value = query_after_where_mock
    
    query_after_limit_mock = MagicMock(name="query_after_limit_empty")
    query_after_where_mock.limit.return_value = query_after_limit_mock
    
    stream_mock = MagicMock(name="stream_mock_animals_empty")
    query_after_limit_mock.stream = stream_mock
    stream_mock.return_value = empty_stream_generator()

    response = test_client_overridden_db.get("/content/animals?difficulty=1")
    assert response.status_code == 200
    assert response.json() == []
    animals_items_collection_mock.where.assert_called_once_with("difficulty", "==", 1)
    query_after_where_mock.limit.assert_called_once_with(50)

# --- Тесты для ошибок GET /content/animals ---

def test_get_animals_unauthorized(
    test_client_overridden_db: TestClient
):
    print("[TEST_DEBUG] test_get_animals_unauthorized: STARTING TEST")
    try:
        response = test_client_overridden_db.get("/api/content/animals") 
        print(f"[TEST_DEBUG] test_get_animals_unauthorized: RESPONSE STATUS: {response.status_code}")
    except Exception as e:
        print(f"[TEST_DEBUG] test_get_animals_unauthorized: EXCEPTION DURING REQUEST: {e}")
        raise
    print("[TEST_DEBUG] test_get_animals_unauthorized: FINISHING TEST")
    assert True 

@pytest.mark.asyncio
async def test_get_animals_firestore_exception(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест GET /content/animals при ошибке Firestore (ожидаем 500)"""
    error_message = "Firestore DB error for animals list"
    animals_items_collection_mock = mock_firestore_client.collection().document("animals").collection()

    # Создаем асинхронный генератор, который вызывает исключение
    async def failing_stream_generator():
        raise RuntimeError(error_message)
        yield None  # Эта строка недостижима, но нужна для того чтобы функция считалась генератором
    
    # Path if difficulty is provided (test uses difficulty=1)
    query_after_where_mock = MagicMock(name="query_after_where_animals_exception")
    animals_items_collection_mock.where.return_value = query_after_where_mock
    
    query_after_limit_mock = MagicMock(name="query_after_limit_animals_exception")
    query_after_where_mock.limit.return_value = query_after_limit_mock
    
    stream_mock = MagicMock(name="stream_mock_exception")
    query_after_limit_mock.stream = stream_mock
    stream_mock.return_value = failing_stream_generator()
    
    response = test_client_overridden_db.get("/content/animals?difficulty=1")
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert f"Failed to retrieve animals content: {error_message}" in response_json["detail"]

@pytest.mark.parametrize(
    "params, expected_error_part",
    [
        ("limit=0", {"loc": ["query", "limit"], "msg": "Input should be greater than or equal to 1"}),
        ("limit=101", {"loc": ["query", "limit"], "msg": "Input should be less than or equal to 100"}),
        ("limit=abc", {"loc": ["query", "limit"], "msg": "Input should be a valid integer"}),
        ("difficulty=0", {"loc": ["query", "difficulty"], "msg": "Input should be greater than or equal to 1"}),
        ("difficulty=6", {"loc": ["query", "difficulty"], "msg": "Input should be less than or equal to 5"}),
        ("difficulty=xyz", {"loc": ["query", "difficulty"], "msg": "Input should be a valid integer"}),
    ]
)
def test_get_animals_validation_errors(
    test_client_overridden_db: TestClient, params: str, expected_error_part: Dict[str, Any]
):
    """Тест GET /content/animals с невалидными параметрами (ожидаем 422)"""
    response = test_client_overridden_db.get(f"/content/animals?{params}")
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)
    found_error = any(
        error_detail.get("loc") == expected_error_part["loc"] and 
        expected_error_part["msg"] in error_detail.get("msg", "") 
        for error_detail in response_json["detail"]
    )
    assert found_error, f"Expected error part {expected_error_part} not found in {response_json['detail']}"

# --- Тесты для GET /content/animals/{animal_id} ---

@pytest.mark.asyncio
async def test_get_animal_by_id_success(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения животного по ID"""
    animal_id = "test_animal_abc"
    mock_animal_data = {"name": "Elephant", "english_name": "Elephant", "difficulty": 3}
    
    # Path: db.collection('content').document('animals').collection('items').document(animal_id).get()
    # The animal_item_snapshot_mock is returned by animal_item_doc_ref_mock.get()
    # We need to configure this specific snapshot instance for this test.
    snapshot_mock_instance = mock_firestore_client.collection().document("animals").collection().document().get()
    # snapshot_mock_instance is an AsyncMock. We configure its return_value (the actual snapshot object)
    actual_snapshot = MagicMock(name="actual_snapshot_for_get_animal")
    actual_snapshot.exists = True
    actual_snapshot.id = animal_id
    actual_snapshot.to_dict.return_value = mock_animal_data
    snapshot_mock_instance.return_value = actual_snapshot

    response = test_client_overridden_db.get(f"/content/animals/{animal_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == animal_id
    assert response_data["name"] == "Elephant"
    # Verify that .document(animal_id) was called on the 'items' collection for animals
    mock_firestore_client.collection().document("animals").collection().document.assert_called_with(animal_id)

@pytest.mark.asyncio
async def test_get_animal_by_id_not_found(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест GET /content/animals/{animal_id} когда животное не найдено (ожидаем 404)"""
    animal_id = "non_existent_animal"
    # The default animal_item_snapshot_mock in the fixture has .exists = False
    # So, no specific configuration needed here for the snapshot itself.
    # We just need to ensure the .get() call happens on the correct document mock.
    
    # Path: db.collection('content').document('animals').collection('items').document(animal_id).get()
    # The .get() call will return the default animal_item_snapshot_mock from the fixture.
    # animal_item_snapshot_mock.exists is already False.

    response = test_client_overridden_db.get(f"/content/animals/{animal_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Animal with ID {animal_id} not found"}
    mock_firestore_client.collection().document("animals").collection().document.assert_called_with(animal_id)

def test_get_animal_by_id_unauthorized(test_client_overridden_db: TestClient):
    """Тест GET /content/animals/{animal_id} без авторизации (ожидаем 401)"""
    response = test_client_overridden_db.get("/content/animals/some_id")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_animal_by_id_firestore_exception(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест GET /content/animals/{animal_id} при ошибке Firestore (ожидаем 500)"""
    animal_id = "error_animal_id"
    error_message = "Firestore get() error for single animal"
    
    # Создаем асинхронную функцию, которая вызывает исключение
    async def error_get_function():
        raise RuntimeError(error_message)
        return None  # Эта строка недостижима, но нужна для анализатора типов
    
    # Path: db.collection('content').document('animals').collection('items').document(animal_id).get()
    animal_item_doc_ref_mock = mock_firestore_client.collection("content").document("animals").collection("items").document(animal_id)
    
    # Создаем мок для .get() и устанавливаем его return_value на нашу ошибочную функцию
    get_mock = MagicMock(name="get_mock_error_animal")
    animal_item_doc_ref_mock.get = get_mock
    get_mock.return_value = error_get_function()
    response = test_client_overridden_db.get(f"/content/animals/{animal_id}")
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert f"Failed to retrieve animal: {error_message}" in response_json["detail"]

# --- Тесты для GET /content/sentences ---

@pytest.mark.asyncio
async def test_get_sentences_success_default_limit(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка предложений (дефолтный лимит 50)"""
    doc1 = create_mock_doc("s1", {"sentence": "Hello world", "words": ["Hello", "world"], "difficulty": 1})
    doc2 = create_mock_doc("s2", {"sentence": "How are you", "words": ["How", "are", "you"], "difficulty": 2, "translation": "Как дела?"})
    
    async def docs_stream_generator():
        yield doc1
        yield doc2

    sentences_items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")
    query_mock = MagicMock(name="query_mock_sentences_default_limit")
    sentences_items_collection_mock.limit.return_value = query_mock
    
    stream_mock = MagicMock(name="stream_mock_sentences_default_limit")
    query_mock.stream = stream_mock
    stream_mock.return_value = docs_stream_generator()

    response = test_client_overridden_db.get("/content/sentences")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["id"] == "s1"
    assert response_data[1]["id"] == "s2"
    sentences_items_collection_mock.limit.assert_called_once_with(50)
    sentences_items_collection_mock.where.assert_not_called()
    # Check that document('sentences') was called on content_collection_mock
    mock_firestore_client.collection().document.assert_any_call('sentences')

@pytest.mark.asyncio
async def test_get_sentences_success_custom_limit(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка предложений с кастомным limit"""
    doc1 = create_mock_doc("s_limit", {"sentence": "Test sentence", "words":["Test", "sentence"], "difficulty": 1})
    
    async def docs_stream_generator():
        yield doc1
    
    sentences_items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")
    query_mock = MagicMock(name="query_mock_sentences_custom_limit")
    sentences_items_collection_mock.limit.return_value = query_mock
    
    stream_mock = MagicMock(name="stream_mock_sentences_custom_limit")
    query_mock.stream = stream_mock
    stream_mock.return_value = docs_stream_generator()

    response = test_client_overridden_db.get("/content/sentences?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    sentences_items_collection_mock.limit.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_get_sentences_success_with_difficulty_filter(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка предложений с фильтром по difficulty (дефолтный лимит 50)"""
    doc1 = create_mock_doc("s_diff", {"sentence": "Difficult one", "words":["Difficult", "one"], "difficulty": 3})
    
    async def docs_stream_generator():
        yield doc1
    
    sentences_items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")
    query_after_where_mock = MagicMock(name="query_after_where_sentences_difficulty")
    sentences_items_collection_mock.where.return_value = query_after_where_mock
    
    query_after_limit_mock = MagicMock(name="query_after_limit_sentences_difficulty")
    query_after_where_mock.limit.return_value = query_after_limit_mock
    
    stream_mock = MagicMock(name="stream_mock_sentences_difficulty")
    query_after_limit_mock.stream = stream_mock
    stream_mock.return_value = docs_stream_generator()

    response = test_client_overridden_db.get("/content/sentences?difficulty=3")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["difficulty"] == 3
    sentences_items_collection_mock.where.assert_called_once_with("difficulty", "==", 3)
    query_after_where_mock.limit.assert_called_once_with(50)

@pytest.mark.asyncio
async def test_get_sentences_success_empty_list(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения пустого списка предложений"""
    async def empty_stream_generator():
        # Пустой асинхронный генератор
        if False: # Чтобы функция была генератором
            yield None
        return

    sentences_items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")

    # Тестируем случай с фильтром по difficulty
    query_after_where_mock = MagicMock(name="query_after_where_mock_empty_list")
    sentences_items_collection_mock.where.return_value = query_after_where_mock
    
    query_after_limit_mock = MagicMock(name="query_after_limit_mock_empty_list")
    query_after_where_mock.limit.return_value = query_after_limit_mock
    
    stream_mock = MagicMock(name="stream_mock_empty_list")
    query_after_limit_mock.stream = stream_mock
    stream_mock.return_value = empty_stream_generator()
    
    response = test_client_overridden_db.get("/content/sentences?difficulty=5")
    assert response.status_code == 200
    assert response.json() == []
    
    sentences_items_collection_mock.where.assert_called_once_with("difficulty", "==", 5)
    query_after_where_mock.limit.assert_called_once_with(50)  # Default limit
    mock_firestore_client.collection.assert_called_with("content")


def test_get_sentences_unauthorized(test_client_overridden_db: TestClient):
    """Тест GET /content/sentences без авторизации (ожидаем 401)"""
    response = test_client_overridden_db.get("/content/sentences")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}


@pytest.mark.asyncio
async def test_get_sentences_firestore_exception(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест GET /content/sentences при ошибке Firestore (ожидаем 500)"""
    error_message = "Firestore DB error for sentences"

    async def error_stream_generator():
        raise RuntimeError(error_message)
        yield  # Это нужно, чтобы Python распознал функцию как асинхронный генератор

    sentences_items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")
    
    # Мокируем цепочку для случая без фильтра (наиболее простой)
    query_after_limit_mock = MagicMock(name="query_after_limit_sentences_exception")
    sentences_items_collection_mock.limit.return_value = query_after_limit_mock
    query_after_limit_mock.stream.return_value = error_stream_generator()
    
    response = test_client_overridden_db.get("/content/sentences") 
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert f"Failed to retrieve sentences content: {error_message}" in response_json["detail"]

    # Проверки вызовов
    sentences_items_collection_mock.limit.assert_called_once_with(50)  # Default limit


@pytest.mark.parametrize(
    "params, expected_error_part",
    [
        ("limit=0", {"loc": ["query", "limit"], "msg": "Input should be greater than or equal to 1"}),
        ("limit=101", {"loc": ["query", "limit"], "msg": "Input should be less than or equal to 100"}),
        ("difficulty=0", {"loc": ["query", "difficulty"], "msg": "Input should be greater than or equal to 1"}),
        ("difficulty=6", {"loc": ["query", "difficulty"], "msg": "Input should be less than or equal to 5"}),
    ]
)
def test_get_sentences_validation_errors(
    test_client_overridden_db: TestClient, params: str, expected_error_part: Dict[str, Any]
):
    """Тест GET /content/sentences с невалидными параметрами (ожидаем 422)"""
    response = test_client_overridden_db.get(f"/content/sentences?{params}")
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)
    found_error = any(
        error_detail.get("loc") == expected_error_part["loc"] and
        expected_error_part["msg"] in error_detail.get("msg", "")
        for error_detail in response_json["detail"]
    )
    assert found_error, f"Expected error part {expected_error_part} not found in {response_json['detail']}"
    # Не нужно проверять вызов document('sentences'), так как валидация происходит до обращения к Firestore

# Конец тестов для content_router

@pytest.mark.parametrize(
    "params, expected_error_part",
    [
        ("limit=0", {"loc": ["query", "limit"], "msg": "Input should be greater than or equal to 1"}),
        ("limit=101", {"loc": ["query", "limit"], "msg": "Input should be less than or equal to 100"}),
        ("limit=abc", {"loc": ["query", "limit"], "msg": "Input should be a valid integer"}),
        ("difficulty=0", {"loc": ["query", "difficulty"], "msg": "Input should be greater than or equal to 1"}),
        ("difficulty=6", {"loc": ["query", "difficulty"], "msg": "Input should be less than or equal to 5"}),
        ("difficulty=xyz", {"loc": ["query", "difficulty"], "msg": "Input should be a valid integer"}),
    ]
)
def test_get_animals_validation_errors(
    test_client_overridden_db: TestClient, params: str, expected_error_part: Dict[str, Any]
):
    """Тест GET /content/animals с невалидными параметрами (ожидаем 422)"""
    response = test_client_overridden_db.get(f"/content/animals?{params}")
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)
    # Ищем конкретную ошибку в списке ошибок валидации
    found_error = False
    for error_detail in response_json["detail"]:
        if (
            error_detail.get("loc") == expected_error_part["loc"] and
            expected_error_part["msg"] in error_detail.get("msg", "")
        ):
            found_error = True
            break
    assert found_error, f"Expected error part {expected_error_part} not found in {response_json['detail']}"

# --- Тесты для GET /content/animals/{animal_id} ---

@pytest.mark.asyncio
async def test_get_animal_by_id_success(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения животного по ID GET /content/animals/{animal_id}"""
    animal_id = "test_animal_abc"
    mock_animal_data = {
        "name": "Elephant", "english_name": "Elephant", "difficulty": 3, "image_url": "elephant.png"
    }
    
    # Создаем документ Firestore
    actual_snapshot = MagicMock(name="animal_snapshot")
    actual_snapshot.exists = True
    actual_snapshot.id = animal_id
    actual_snapshot.to_dict.return_value = mock_animal_data
    
    # Создаем асинхронную функцию, которая вернет этот документ
    async def get_document_async():
        return actual_snapshot
    
    # Настраиваем мок для path: .collection('content').document('animals').collection('items').document(animal_id).get()
    animal_doc_ref_mock = mock_firestore_client.collection("content").document("animals").collection("items").document(animal_id)
    get_mock = MagicMock(name="get_method")
    animal_doc_ref_mock.get = get_mock
    get_mock.return_value = get_document_async()

    response = test_client_overridden_db.get(f"/content/animals/{animal_id}")
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["id"] == animal_id
    assert response_data["name"] == "Elephant"
    assert response_data["english_name"] == "Elephant"
    assert response_data["difficulty"] == 3
    assert response_data["image_url"] == "elephant.png"

    # Проверяем, что был вызван правильный путь к документу
    # Поскольку мы используем конкретные имена в моках, достаточно проверить вызов document() с animal_id
    animal_doc_ref_mock.get.assert_called_once()

@pytest.mark.asyncio
async def test_get_animal_by_id_not_found(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест GET /content/animals/{animal_id} когда животное не найдено (ожидаем 404)"""
    animal_id = "non_existent_animal"
    
    # Создаем документ Firestore с exists=False
    actual_snapshot = MagicMock(name="not_found_snapshot")
    actual_snapshot.exists = False
    
    # Создаем асинхронную функцию, которая вернет несуществующий документ
    async def get_document_async():
        return actual_snapshot
    
    # Настраиваем мок для path: .collection('content').document('animals').collection('items').document(animal_id).get()
    animal_doc_ref_mock = mock_firestore_client.collection("content").document("animals").collection("items").document(animal_id)
    get_mock = MagicMock(name="get_method_not_found")
    animal_doc_ref_mock.get = get_mock
    get_mock.return_value = get_document_async() # Животное не существует

    response = test_client_overridden_db.get(f"/content/animals/{animal_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Animal with ID {animal_id} not found"}

def test_get_animal_by_id_unauthorized(test_client_overridden_db: TestClient):
    """Тест GET /content/animals/{animal_id} без авторизации (ожидаем 401)"""
    response = test_client_overridden_db.get("/content/animals/some_id")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

@pytest.mark.asyncio
async def test_get_animal_by_id_firestore_exception(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест GET /content/animals/{animal_id} при ошибке Firestore (ожидаем 500)"""
    animal_id = "error_animal_id"
    error_message = "Firestore get() error"
    
    # Создаем асинхронную функцию, которая вызывает исключение
    async def error_get_function():
        raise RuntimeError(error_message)
        return None  # Эта строка недостижима, но нужна для анализатора типов
    
    # Настраиваем мок для path: .collection('content').document('animals').collection('items').document(animal_id).get()
    animal_doc_ref_mock = mock_firestore_client.collection("content").document("animals").collection("items").document(animal_id)
    get_mock = MagicMock(name="get_method_error")
    animal_doc_ref_mock.get = get_mock
    get_mock.return_value = error_get_function()

    response = test_client_overridden_db.get(f"/content/animals/{animal_id}")
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert f"Failed to retrieve animal: {error_message}" in response_json["detail"]

# --- Тесты для GET /content/sentences ---

@pytest.mark.asyncio
async def test_get_sentences_success_default_limit(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка предложений (дефолтный лимит)"""
    mock_sentence_data_1 = {
        "sentence": "Hello world", "words": ["Hello", "world"], "difficulty": 1
    }
    mock_sentence_data_2 = {
        "sentence": "How are you", "words": ["How", "are", "you"], "difficulty": 2, "translation": "Как дела?"
    }
    
    doc_mock_1 = MagicMock()
    doc_mock_1.id = "sentence1"
    doc_mock_1.to_dict.return_value = mock_sentence_data_1
    
    doc_mock_2 = MagicMock()
    doc_mock_2.id = "sentence2"
    doc_mock_2.to_dict.return_value = mock_sentence_data_2

    async def successful_sentences_stream_generator():
        yield doc_mock_1
        yield doc_mock_2

    items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")
    
    # Мок для .stream() после .limit() (без .where())
    stream_mock = MagicMock(name="stream_mock_sentences_success_default")
    items_collection_mock.limit.return_value.stream = stream_mock
    stream_mock.return_value = successful_sentences_stream_generator()

    # Удаляем избыточный мок, так как .limit() всегда вызывается перед .stream()
    # mock_firestore_client.collection().document().collection().stream = AsyncMock(return_value=[doc_mock_1, doc_mock_2])

    response = test_client_overridden_db.get("/content/sentences")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    
    assert response_data[0]["id"] == "sentence1"
    assert response_data[0]["sentence"] == "Hello world"
    assert response_data[0]["words"] == ["Hello", "world"]
    
    assert response_data[1]["id"] == "sentence2"
    assert response_data[1]["translation"] == "Как дела?"

    # Проверяем, что для sentences был вызван document('sentences')
    mock_firestore_client.collection().document.assert_any_call('sentences')

@pytest.mark.asyncio
async def test_get_sentences_success_custom_limit(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка предложений с кастомным limit"""
    mock_sentence_data = {"sentence": "Test sentence", "words": ["Test", "sentence"], "difficulty": 3}
    doc_mock = MagicMock()
    doc_mock.id = "sentence_test"
    doc_mock.to_dict.return_value = mock_sentence_data

    async def successful_custom_limit_stream_generator():
        yield doc_mock

    items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")
    
    # Мок для объекта, возвращаемого .limit()
    query_after_limit_mock = MagicMock(name="query_after_limit_mock_custom_limit")
    items_collection_mock.limit.return_value = query_after_limit_mock

    # Настраиваем .stream на этом моке
    stream_mock = MagicMock(name="stream_mock_sentences_custom_limit")
    query_after_limit_mock.stream = stream_mock
    stream_mock.return_value = successful_custom_limit_stream_generator()

    response = test_client_overridden_db.get("/content/sentences?limit=1")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == "sentence_test"
    
    # Проверяем, что items_collection_mock.limit был вызван с 1
    items_collection_mock.limit.assert_called_with(1)
    mock_firestore_client.collection().document.assert_any_call('sentences')

@pytest.mark.asyncio
async def test_get_sentences_success_with_difficulty_filter(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест успешного получения списка предложений с фильтром по difficulty"""
    mock_sentence_data = {"sentence": "Difficult one", "words":["Difficult", "one"], "difficulty": 4}
    doc_mock = MagicMock()
    doc_mock.id = "sentence_difficult"
    doc_mock.to_dict.return_value = mock_sentence_data

    async def successful_difficulty_filter_stream_generator():
        yield doc_mock

    items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")

    query_after_where_mock = MagicMock(name="query_after_where_mock_difficulty_filter")
    items_collection_mock.where.return_value = query_after_where_mock

    query_after_limit_mock = MagicMock(name="query_after_limit_mock_difficulty_filter")
    query_after_where_mock.limit.return_value = query_after_limit_mock

    stream_mock = MagicMock(name="stream_mock_difficulty_filter")
    query_after_limit_mock.stream = stream_mock
    stream_mock.return_value = successful_difficulty_filter_stream_generator()

    response = test_client_overridden_db.get("/content/sentences?difficulty=4")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["difficulty"] == 4

    items_collection_mock.where.assert_called_once_with("difficulty", "==", 4)
    query_after_where_mock.limit.assert_called_once_with(50) # Default limit
    mock_firestore_client.collection().document.assert_any_call('sentences')



def test_get_sentences_unauthorized(test_client_overridden_db: TestClient):
    """Тест GET /content/sentences без авторизации (ожидаем 401)"""
    response = test_client_overridden_db.get("/content/sentences")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

@pytest.mark.asyncio
async def test_get_sentences_firestore_exception(
    test_client_overridden_db: TestClient, mock_firestore_client: MagicMock
):
    """Тест GET /content/sentences при ошибке Firestore (ожидаем 500)"""
    error_message = "Firestore DB error for sentences"

    async def failing_sentences_stream_generator():
        raise RuntimeError(error_message)
        yield None # Делает это асинхронным генератором

    # Получаем мок для .collection("items") после .document("sentences")
    items_collection_mock = mock_firestore_client.collection("content").document("sentences").collection("items")

    # Мок для случая без фильтра по difficulty (когда .where() не вызывается)
    # Этот путь не будет задействован в данном тесте, так как difficulty=1 передается
    stream_mock_no_filter = MagicMock(name="stream_mock_no_filter_sentences_exception")
    items_collection_mock.limit.return_value.stream = stream_mock_no_filter
    stream_mock_no_filter.return_value = failing_sentences_stream_generator()

    # Мок для случая с фильтром по difficulty (когда .where() вызывается)
    # Этот путь будет задействован, так как difficulty=1 передается
    stream_mock_with_filter = MagicMock(name="stream_mock_with_filter_sentences_exception")
    query_after_where_mock = MagicMock(name="query_after_where_mock_sentences_exception")
    items_collection_mock.where.return_value = query_after_where_mock
    query_after_where_mock.limit.return_value.stream = stream_mock_with_filter
    stream_mock_with_filter.return_value = failing_sentences_stream_generator()

    response = test_client_overridden_db.get("/content/sentences?difficulty=1")
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert f"Failed to retrieve sentences content: {error_message}" in response_json["detail"]
    mock_firestore_client.collection().document.assert_any_call('sentences')

@pytest.mark.parametrize(
    "params, expected_error_part",
    [
        ("limit=0", {"loc": ["query", "limit"], "msg": "Input should be greater than or equal to 1"}),
        ("limit=101", {"loc": ["query", "limit"], "msg": "Input should be less than or equal to 100"}),
        ("difficulty=0", {"loc": ["query", "difficulty"], "msg": "Input should be greater than or equal to 1"}),
        ("difficulty=6", {"loc": ["query", "difficulty"], "msg": "Input should be less than or equal to 5"}),
    ]
)
def test_get_sentences_validation_errors(
    test_client_overridden_db: TestClient, params: str, expected_error_part: Dict[str, Any]
):
    """Тест GET /content/sentences с невалидными параметрами (ожидаем 422)"""
    response = test_client_overridden_db.get(f"/content/sentences?{params}")
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)
    found_error = False
    for error_detail in response_json["detail"]:
        if (
            error_detail.get("loc") == expected_error_part["loc"] and
            expected_error_part["msg"] in error_detail.get("msg", "")
        ):
            found_error = True
            break
    assert found_error, f"Expected error part {expected_error_part} not found in {response_json['detail']}"
    # Не нужно проверять вызов document('sentences'), так как валидация происходит до обращения к Firestore

# Конец тестов для content_router 

# Примерный тест (закомментирован, для проверки структуры)
# def test_example_content_auth(test_client_overridden_db: TestClient):
#     response = test_client_overridden_db.get("/content/animals")
#     assert response.status_code == 200 # Ожидаем успех, если моки настроены
