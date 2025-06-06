import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock
from typing import List
from datetime import datetime, timezone # Добавим timezone для offset-aware datetime

from backend.routers.session_router import (
    StartSessionRequest,
    StartSessionResponse,
    FinishSessionRequest,
    FinishSessionResponse
)
from backend.domain.session import SessionModel, RoundDetail, SessionStatus # Импортируем SessionStatus
from backend.services.session_service import SessionService # Для мокирования

# Путь к экземпляру session_service в модуле session_router
SESSION_SERVICE_PATH = "backend.routers.session_router.session_service"
TEST_USER_ID = "test_user_123"

# Фикстура для клиента с переопределенной авторизацией (аналогично test_progress_router)
@pytest.fixture
def client_with_auth_override(client: TestClient):
    from backend.shared.auth import get_current_user_id
    async def override_get_current_user_id():
        return TEST_USER_ID
    client.app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    yield client
    client.app.dependency_overrides.clear()

# --- Тесты для POST /api/session/start --- 

@pytest.mark.asyncio
@pytest.mark.parametrize("game_type", ["guess_animal", "build_sentence"])
async def test_start_session_success(
    client_with_auth_override: TestClient, monkeypatch, game_type: str
):
    """Тест успешного старта сессии POST /api/session/start"""
    mock_service = MagicMock(spec=SessionService)
    expected_session_id = "new_session_123"
    # Настраиваем AsyncMock для start_session
    mock_service.start_session = AsyncMock(return_value=expected_session_id)
    
    monkeypatch.setattr(SESSION_SERVICE_PATH, mock_service)

    response = client_with_auth_override.post(
        "/api/session/start", json={"game_type": game_type}
    )

    assert response.status_code == 200
    assert response.json() == {"session_id": expected_session_id}
    mock_service.start_session.assert_called_once_with(TEST_USER_ID, game_type)

@pytest.mark.asyncio
async def test_start_session_invalid_game_type(client_with_auth_override: TestClient):
    """Тест старта сессии с неверным game_type POST /api/session/start"""
    response = client_with_auth_override.post(
        "/api/session/start", json={"game_type": "invalid_game"}
    )
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    # Проверяем, что сообщение об ошибке содержит упоминание gameType и возможных значений
    assert "invalid gametype" in response_json["detail"].lower() 
    assert "guess_animal" in response_json["detail"].lower()
    assert "build_sentence" in response_json["detail"].lower()


def test_start_session_unauthorized(client: TestClient):
    """Тест старта сессии без авторизации POST /api/session/start"""
    response = client.post("/api/session/start", json={"game_type": "guess_animal"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

@pytest.mark.asyncio
async def test_start_session_service_exception(
    client_with_auth_override: TestClient, monkeypatch
):
    """Тест старта сессии при ошибке сервиса POST /api/session/start"""
    mock_service = MagicMock(spec=SessionService)
    # Настраиваем AsyncMock для start_session, который вызывает исключение
    mock_service.start_session = AsyncMock(side_effect=RuntimeError("Service failure"))

    monkeypatch.setattr(SESSION_SERVICE_PATH, mock_service)

    response = client_with_auth_override.post(
        "/api/session/start", json={"game_type": "guess_animal"}
    )
    
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert "Failed to start session: Service failure" in response_json["detail"]
    mock_service.start_session.assert_called_once_with(TEST_USER_ID, "guess_animal")


# --- Тесты для PATCH /api/session/finish --- 

@pytest.mark.asyncio
async def test_finish_session_success(client_with_auth_override: TestClient, monkeypatch):
    """Тест успешного завершения сессии PATCH /api/session/finish"""
    mock_service = MagicMock(spec=SessionService)
    mock_service.finish_session = AsyncMock() # Успешное завершение, ничего не возвращает
    
    monkeypatch.setattr(SESSION_SERVICE_PATH, mock_service)

    session_id_to_finish = "session_abc_123"
    request_data = {
        "details": [{
            "question_id": "q1_id",
            "answer": "a1",
            "is_correct": True,
            "time_spent": 5.5
        }],
        "score": 10
    }

    response = client_with_auth_override.patch(
        f"/api/session/finish?session_id={session_id_to_finish}",
        json=request_data
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Session finished successfully"}
    mock_service.finish_session.assert_called_once_with(
        TEST_USER_ID,
        session_id_to_finish,
        [RoundDetail(question_id="q1_id", answer="a1", is_correct=True, time_spent=5.5)],
        request_data["score"]
    )

@pytest.mark.asyncio
async def test_finish_session_not_found_value_error(
    client_with_auth_override: TestClient, monkeypatch
):
    """Тест завершения несуществующей сессии PATCH /api/session/finish (ValueError -> 404)"""
    mock_service = MagicMock(spec=SessionService)
    error_message = "Session not found to finish"
    mock_service.finish_session = AsyncMock(side_effect=ValueError(error_message))
    
    monkeypatch.setattr(SESSION_SERVICE_PATH, mock_service)

    session_id_to_finish = "non_existent_session"
    request_data = {"details": [], "score": 0}

    response = client_with_auth_override.patch(
        f"/api/session/finish?session_id={session_id_to_finish}",
        json=request_data
    )

    assert response.status_code == 404
    assert response.json() == {"detail": error_message}
    mock_service.finish_session.assert_called_once()

def test_finish_session_unauthorized(client: TestClient):
    """Тест завершения сессии без авторизации PATCH /api/session/finish"""
    response = client.patch(
        "/api/session/finish?session_id=any_session",
        json={"details": [], "score": 0}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

@pytest.mark.asyncio
async def test_finish_session_service_exception(
    client_with_auth_override: TestClient, monkeypatch
):
    """Тест завершения сессии при ошибке сервиса PATCH /api/session/finish"""
    mock_service = MagicMock(spec=SessionService)
    error_message = "Internal service error during finish"
    mock_service.finish_session = AsyncMock(side_effect=RuntimeError(error_message))

    monkeypatch.setattr(SESSION_SERVICE_PATH, mock_service)
    
    session_id_to_finish = "session_def_456"
    request_data = {"details": [], "score": 0}

    response = client_with_auth_override.patch(
        f"/api/session/finish?session_id={session_id_to_finish}",
        json=request_data
    )
    
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert f"Failed to finish session: {error_message}" in response_json["detail"]
    mock_service.finish_session.assert_called_once()


# --- Тесты для GET /api/session/active ---

@pytest.mark.asyncio
async def test_get_active_session_success_found(client_with_auth_override: TestClient, monkeypatch):
    """Тест успешного получения активной сессии GET /api/session/active (сессия найдена)"""
    mock_service = MagicMock(spec=SessionService)
    
    expected_session_data = {
        "session_id": "active_session_789",
        "user_id": TEST_USER_ID,
        "game_type": "guess_animal",
        "start_time": datetime.now(timezone.utc),
        "end_time": None,
        "status": SessionStatus.ACTIVE,
        "score": None,
        "details": []
    }
    expected_session = SessionModel(**expected_session_data)
    mock_service.get_active_session = AsyncMock(return_value=expected_session)
    
    monkeypatch.setattr(SESSION_SERVICE_PATH, mock_service)

    response = client_with_auth_override.get("/api/session/active")

    assert response.status_code == 200
    response_json = response.json()
    
    assert response_json["session_id"] == expected_session.session_id
    assert response_json["user_id"] == expected_session.user_id
    assert response_json["game_type"] == expected_session.game_type
    assert response_json["start_time"] == expected_session.start_time.isoformat().replace("+00:00", "Z")
    assert response_json["end_time"] == expected_session.end_time
    assert response_json["status"] == expected_session.status.value
    assert response_json["score"] == expected_session.score
    assert response_json["details"] == expected_session.details
    
    mock_service.get_active_session.assert_called_once_with(TEST_USER_ID)

@pytest.mark.asyncio
async def test_get_active_session_success_not_found(client_with_auth_override: TestClient, monkeypatch):
    """Тест успешного получения активной сессии GET /api/session/active (сессия не найдена)"""
    mock_service = MagicMock(spec=SessionService)
    mock_service.get_active_session = AsyncMock(return_value=None)
    
    monkeypatch.setattr(SESSION_SERVICE_PATH, mock_service)

    response = client_with_auth_override.get("/api/session/active")

    assert response.status_code == 404
    assert response.json() == {"detail": "No active session found"}
    mock_service.get_active_session.assert_called_once_with(TEST_USER_ID)

def test_get_active_session_unauthorized(client: TestClient):
    """Тест получения активной сессии без авторизации GET /api/session/active"""
    response = client.get("/api/session/active")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

@pytest.mark.asyncio
async def test_get_active_session_service_exception(client_with_auth_override: TestClient, monkeypatch):
    """Тест получения активной сессии при ошибке сервиса GET /api/session/active"""
    mock_service = MagicMock(spec=SessionService)
    error_message = "Service failure while fetching active session"
    mock_service.get_active_session = AsyncMock(side_effect=RuntimeError(error_message))

    monkeypatch.setattr(SESSION_SERVICE_PATH, mock_service)

    response = client_with_auth_override.get("/api/session/active")

    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert f"Failed to get active session: {error_message}" in response_json["detail"]
    mock_service.get_active_session.assert_called_once_with(TEST_USER_ID)

