import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

from domain.user import UserModel
from routers.profile_router import UpdateProfileRequest # Импортируем из роутера, т.к. там определена
from repositories.user_repository import UserRepository # Для мокирования
from shared.dependencies import get_user_repository

# Путь к экземпляру user_repository в модуле profile_router
TEST_USER_ID = "test_profile_user_123"

# Фикстура для клиента с переопределенной авторизацией
@pytest.fixture
def client_with_auth_override(client: TestClient):
    from shared.auth import get_current_user_id
    async def override_get_current_user_id():
        return TEST_USER_ID
    client.app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    yield client
    client.app.dependency_overrides.clear()

# --- Тесты для GET /api/profile ---

@pytest.mark.asyncio
async def test_get_profile_success_exists(client_with_auth_override: TestClient):
    """Тест успешного получения существующего профиля GET /api/profile"""
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_user = AsyncMock()
    
    expected_user_data = {
        "uid": TEST_USER_ID,
        "email": "test@example.com",
        "display_name": "Test User",
        "photo_url": "http://example.com/photo.jpg",
        "level": "beginner",
        "created_at": datetime.now(timezone.utc)
    }
    expected_user = UserModel(**expected_user_data)
    mock_repo.get_user = AsyncMock(return_value=expected_user)
    
    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    response = client_with_auth_override.get("/api/profile")

    assert response.status_code == 200
    response_json = response.json()
    
    assert response_json["uid"] == expected_user.uid
    assert response_json["email"] == expected_user.email
    assert response_json["display_name"] == expected_user.display_name
    assert response_json["photo_url"] == str(expected_user.photo_url)
    assert response_json["level"] == expected_user.level
    assert response_json["created_at"] == expected_user.created_at.isoformat().replace("+00:00", "Z")
    
    mock_repo.get_user.assert_called_once_with(TEST_USER_ID)
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)

@pytest.mark.asyncio
async def test_get_profile_user_not_found(client_with_auth_override: TestClient):
    """
    Тест GET /api/profile когда пользователь не существует.
    Ожидаем 404, так как профиль не найден.
    """
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_user = AsyncMock(return_value=None) # Пользователь не найден
    
    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    response = client_with_auth_override.get("/api/profile")

    assert response.status_code == 404 # Изменено с 500 на 404
    response_json = response.json()
    assert response_json["detail"] == "User profile not found" # Новая проверка
    
    mock_repo.get_user.assert_called_once_with(TEST_USER_ID)
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)

def test_get_profile_unauthorized(client: TestClient):
    """Тест получения профиля без авторизации GET /api/profile"""
    response = client.get("/api/profile")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

@pytest.mark.asyncio
async def test_get_profile_repository_exception(client_with_auth_override: TestClient):
    """Тест получения профиля при ошибке репозитория GET /api/profile"""
    mock_repo = MagicMock(spec=UserRepository)
    error_message = "Database connection error"
    mock_repo.get_user = AsyncMock(side_effect=RuntimeError(error_message))

    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    response = client_with_auth_override.get("/api/profile")

    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    # Проверяем, что сообщение об ошибке из репозитория включено в ответ
    assert error_message in response_json["detail"] 
    assert f"Failed to get user profile: {error_message}" == response_json["detail"]
    
    mock_repo.get_user.assert_called_once_with(TEST_USER_ID)
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)


# --- Тесты для PUT /api/profile ---

@pytest.mark.asyncio
async def test_update_profile_success_full_update_existing_user(client_with_auth_override: TestClient):
    """Тест успешного полного обновления существующего профиля PUT /api/profile"""
    mock_repo = MagicMock(spec=UserRepository)
    
    original_user_data = {
        "uid": TEST_USER_ID,
        "email": "original@example.com",
        "display_name": "Original Name",
        "photo_url": "http://example.com/original.jpg",
        "level": "beginner",
        "created_at": datetime.now(timezone.utc)
    }
    original_user = UserModel(**original_user_data)
    mock_repo.get_user = AsyncMock(return_value=original_user)
    mock_repo.create_or_update_user = AsyncMock()

    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    update_payload = {
        "display_name": "Updated Name",
        "email": "updated@example.com",
        "photo_url": "http://example.com/updated.jpg"
    }

    response = client_with_auth_override.put("/api/profile", json=update_payload)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["uid"] == TEST_USER_ID
    assert response_json["email"] == update_payload["email"]
    assert response_json["display_name"] == update_payload["display_name"]
    assert response_json["photo_url"] == update_payload["photo_url"]
    assert response_json["level"] == original_user.level
    assert response_json["created_at"] == original_user.created_at.isoformat().replace("+00:00", "Z")

    mock_repo.get_user.assert_called_once_with(TEST_USER_ID)
    
    assert mock_repo.create_or_update_user.call_count == 1
    called_with_user = mock_repo.create_or_update_user.call_args[0][0]
    assert isinstance(called_with_user, UserModel)
    assert called_with_user.uid == TEST_USER_ID
    assert called_with_user.email == update_payload["email"]
    assert called_with_user.display_name == update_payload["display_name"]
    assert str(called_with_user.photo_url) == update_payload["photo_url"]
    assert called_with_user.level == original_user.level
    assert called_with_user.created_at == original_user.created_at
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)


@pytest.mark.asyncio
async def test_update_profile_success_partial_update_existing_user(client_with_auth_override: TestClient):
    """Тест успешного частичного обновления существующего профиля PUT /api/profile"""
    mock_repo = MagicMock(spec=UserRepository)
    
    original_user_data = {
        "uid": TEST_USER_ID,
        "email": "partial@example.com",
        "display_name": "Partial Original Name",
        "photo_url": "http://example.com/partial_original.jpg",
        "level": "intermediate",
        "created_at": datetime.now(timezone.utc)
    }
    original_user = UserModel(**original_user_data)
    mock_repo.get_user = AsyncMock(return_value=original_user)
    mock_repo.create_or_update_user = AsyncMock()

    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    update_payload = {
        "display_name": "Partial Updated Name"
    }

    response = client_with_auth_override.put("/api/profile", json=update_payload)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["uid"] == TEST_USER_ID
    assert response_json["email"] == original_user.email
    assert response_json["display_name"] == update_payload["display_name"]
    assert response_json["photo_url"] == str(original_user.photo_url)
    assert response_json["level"] == original_user.level
    assert response_json["created_at"] == original_user.created_at.isoformat().replace("+00:00", "Z")

    mock_repo.get_user.assert_called_once_with(TEST_USER_ID)
    
    called_with_user = mock_repo.create_or_update_user.call_args[0][0]
    assert isinstance(called_with_user, UserModel)
    assert called_with_user.uid == TEST_USER_ID
    assert called_with_user.email == original_user.email
    assert called_with_user.display_name == update_payload["display_name"]
    assert called_with_user.photo_url == original_user.photo_url
    assert called_with_user.level == original_user.level
    assert called_with_user.created_at == original_user.created_at
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)


@pytest.mark.asyncio
async def test_update_profile_success_new_user(client_with_auth_override: TestClient):
    """Тест успешного обновления (создания) профиля для нового пользователя PUT /api/profile"""
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_user = AsyncMock(return_value=None)
    mock_repo.create_or_update_user = AsyncMock()

    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    update_payload = {
        "display_name": "New User Name",
        "email": "newuser@example.com",
        "photo_url": "http://example.com/newuser.jpg"
    }

    response = client_with_auth_override.put("/api/profile", json=update_payload)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["uid"] == TEST_USER_ID
    assert response_json["email"] == update_payload["email"]
    assert response_json["display_name"] == update_payload["display_name"]
    assert response_json["photo_url"] == update_payload["photo_url"]
    assert response_json["level"] is None
    assert response_json["created_at"] is None 

    mock_repo.get_user.assert_called_once_with(TEST_USER_ID)
    
    called_with_user = mock_repo.create_or_update_user.call_args[0][0]
    assert isinstance(called_with_user, UserModel)
    assert called_with_user.uid == TEST_USER_ID
    assert called_with_user.email == update_payload["email"]
    assert called_with_user.display_name == update_payload["display_name"]
    assert str(called_with_user.photo_url) == update_payload["photo_url"]
    assert called_with_user.level is None
    assert called_with_user.created_at is None
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)


# --- Следующие тесты для PUT /api/profile (ошибки, авторизация) ---

def test_update_profile_unauthorized(client: TestClient):
    """Тест обновления профиля без авторизации PUT /api/profile"""
    update_payload = {"display_name": "Unauthorized Update"}
    response = client.put("/api/profile", json=update_payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

@pytest.mark.asyncio
async def test_update_profile_validation_error_invalid_email(client_with_auth_override: TestClient):
    """Тест обновления профиля с невалидным email PUT /api/profile (ожидаем 422)"""
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_user = AsyncMock(return_value=None)
    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    update_payload = {"email": "not-a-valid-email"}
    response = client_with_auth_override.put("/api/profile", json=update_payload)

    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)
    assert len(response_json["detail"]) == 1
    assert response_json["detail"][0]["type"] == "value_error"
    assert "email" in response_json["detail"][0]["loc"]
    assert "valid email address" in response_json["detail"][0]["msg"].lower()
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)

@pytest.mark.asyncio
async def test_update_profile_new_user_missing_email(client_with_auth_override: TestClient):
    """Тест создания нового профиля без email PUT /api/profile (ожидаем 422)"""
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_user = AsyncMock(return_value=None) # Пользователя нет
    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    update_payload = {"display_name": "New User Without Email"} # Нет email
    response = client_with_auth_override.put("/api/profile", json=update_payload)

    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)
    assert len(response_json["detail"]) == 1
    assert response_json["detail"][0]["type"] == "missing"
    assert "email" in response_json["detail"][0]["loc"]
    assert "Field required for new user profile" in response_json["detail"][0]["msg"]
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)

@pytest.mark.asyncio
async def test_update_profile_get_user_exception(client_with_auth_override: TestClient):
    """Тест обновления профиля, когда user_repository.get_user вызывает исключение"""
    mock_repo = MagicMock(spec=UserRepository)
    error_message = "Get user DB error"
    mock_repo.get_user = AsyncMock(side_effect=RuntimeError(error_message))
    mock_repo.create_or_update_user = AsyncMock()

    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    update_payload = {"display_name": "Test Name", "email": "test@example.com"}
    response = client_with_auth_override.put("/api/profile", json=update_payload)

    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert error_message in response_json["detail"]
    assert f"Failed to update profile: {error_message}" == response_json["detail"]
    
    mock_repo.get_user.assert_called_once_with(TEST_USER_ID)
    mock_repo.create_or_update_user.assert_not_called()
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)


@pytest.mark.asyncio
async def test_update_profile_create_or_update_user_exception(client_with_auth_override: TestClient):
    """Тест обновления профиля, когда user_repository.create_or_update_user вызывает исключение"""
    mock_repo = MagicMock(spec=UserRepository)
    original_user_data = {
        "uid": TEST_USER_ID, "email": "test@example.com", "created_at": datetime.now(timezone.utc)
    }
    mock_repo.get_user = AsyncMock(return_value=UserModel(**original_user_data))
    
    error_message = "Create/Update user DB error"
    mock_repo.create_or_update_user = AsyncMock(side_effect=RuntimeError(error_message))

    client_with_auth_override.app.dependency_overrides[get_user_repository] = lambda: mock_repo

    update_payload = {"display_name": "Test Name", "email": "another@example.com"}
    response = client_with_auth_override.put("/api/profile", json=update_payload)

    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert error_message in response_json["detail"]
    assert f"Failed to update profile: {error_message}" == response_json["detail"]

    mock_repo.get_user.assert_called_once_with(TEST_USER_ID)
    mock_repo.create_or_update_user.assert_called_once()
    client_with_auth_override.app.dependency_overrides.pop(get_user_repository, None)
