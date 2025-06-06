import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import datetime # Добавим импорт datetime

from backend.main import app
from backend.shared.auth import get_current_user_id

PROGRESS_SERVICE_PATH = "backend.routers.progress_router.progress_service"
TEST_USER_ID = "test_user_progress_router"

@pytest.fixture
def client_with_auth_override(client: TestClient):
    """Переопределяет зависимость get_current_user_id для тестового клиента."""
    app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
    yield client
    app.dependency_overrides.clear()


def test_save_progress_success(client_with_auth_override: TestClient, monkeypatch):
    """
    Тест успешного сохранения прогресса POST /api/progress
    """
    mock_service = MagicMock()
    mock_service.record_progress.return_value = "mock_progress_id_123"
    monkeypatch.setattr(PROGRESS_SERVICE_PATH, mock_service)

    request_data = {
        "score": 100,
        "correct_answers": 10,
        "total_answers": 10,
        "time_spent": 120.5,
        "date": "2024-01-15"
    }
    
    response = client_with_auth_override.post("/api/progress", json=request_data)
    
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "Progress saved successfully"
    assert response_json["progress_id"] == "mock_progress_id_123"
    
    # Преобразуем строку даты в объект datetime.date для сравнения
    expected_date = datetime.date.fromisoformat(request_data["date"])

    mock_service.record_progress.assert_called_once_with(
        user_id=TEST_USER_ID,
        score=request_data["score"],
        correct_answers=request_data["correct_answers"],
        total_answers=request_data["total_answers"],
        time_spent=request_data["time_spent"],
        record_date=expected_date
    )

# Дальнейшие тесты будут добавлены здесь

def test_save_progress_invalid_data(client_with_auth_override: TestClient):
    """
    Тест сохранения прогресса с некорректными данными POST /api/progress
    Должен возвращать 422 Unprocessable Entity.
    """
    # Случай 1: Отсутствует обязательное поле 'score'
    invalid_data_missing_field = {
        # "score": 100, # Пропущено
        "correct_answers": 10,
        "total_answers": 10,
        "time_spent": 120.5,
        "date": "2024-01-15"
    }
    response = client_with_auth_override.post("/api/progress", json=invalid_data_missing_field)
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any("score" in err["loc"] for err in response_json["detail"] if "type" in err and err["type"] == "missing")


    # Случай 2: Некорректный тип данных для 'score' (строка вместо числа)
    invalid_data_wrong_type = {
        "score": "не число",
        "correct_answers": 10,
        "total_answers": 10,
        "time_spent": 120.5,
        "date": "2024-01-15"
    }
    response = client_with_auth_override.post("/api/progress", json=invalid_data_wrong_type)
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any("score" in err["loc"] for err in response_json["detail"] if "type" in err and "int_parsing" in err["type"])


    # Случай 3: Некорректный формат даты
    invalid_data_wrong_date_format = {
        "score": 100,
        "correct_answers": 10,
        "total_answers": 10,
        "time_spent": 120.5,
        "date": "15-01-2024" # Не ISO формат
    }
    response = client_with_auth_override.post("/api/progress", json=invalid_data_wrong_date_format)
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert response_json["detail"] == "Invalid date format. Use YYYY-MM-DD."


def test_get_progress_success(client_with_auth_override: TestClient, monkeypatch):
    """
    Тест успешного получения прогресса GET /api/progress
    """
    mock_service = MagicMock()

    # Данные, которые, как мы ожидаем, вернет сервис
    expected_service_output = {
        "data": [
            {
                "date": "2024-01-15",
                "score": 100, # Сервис возвращает 'score'
                "correct_answers": 10,
                "total_answers": 10,
                "success_rate": 1.0,
                "time_spent": 120.5
            }
        ],
        "total_score": 100,
        "average_score": 100.0,
        "success_rate": 1.0
    }
    mock_service.get_progress.return_value = expected_service_output
    monkeypatch.setattr(PROGRESS_SERVICE_PATH, mock_service)

    # Данные, которые, как мы ожидаем, вернет API (после преобразования)
    expected_api_response = {
        "data": [
            {
                "date": "2024-01-15",
                "daily_score": 100, # API возвращает 'daily_score'
                "correct_answers": 10,
                "total_answers": 10,
                "success_rate": 1.0,
                "time_spent": 120.5
            }
        ],
        "total_score": 100,
        "average_score": 100.0,
        "success_rate": 1.0
    }

    response = client_with_auth_override.get("/api/progress?days=7")
    
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == expected_api_response
    
    mock_service.get_progress.assert_called_once_with(TEST_USER_ID, 7)

def test_get_progress_invalid_days_param(client_with_auth_override: TestClient):
    """
    Тест получения прогресса с некорректным параметром 'days' GET /api/progress
    Должен возвращать 422 Unprocessable Entity.
    """
    # Случай 1: days < 1
    response = client_with_auth_override.get("/api/progress?days=0")
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any("days" in err["loc"] and "query" in err["loc"] for err in response_json["detail"] if "type" in err and "greater_than_equal" in err["type"])

    # Случай 2: days > 30
    response = client_with_auth_override.get("/api/progress?days=31")
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any("days" in err["loc"] and "query" in err["loc"] for err in response_json["detail"] if "type" in err and "less_than_equal" in err["type"])


def test_get_weekly_summary_success(client_with_auth_override: TestClient, monkeypatch):
    """
    Тест успешного получения еженедельной сводки GET /api/progress/weekly-summary
    """
    mock_service = MagicMock()
    expected_weekly_score = 150
    mock_service.get_weekly_summary.return_value = expected_weekly_score
    
    monkeypatch.setattr(PROGRESS_SERVICE_PATH, mock_service)

    response = client_with_auth_override.get("/api/progress/weekly-summary")
    
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {"total_weekly_score": expected_weekly_score}
    
    mock_service.get_weekly_summary.assert_called_once_with(user_id=TEST_USER_ID)


def test_save_progress_unauthorized(client: TestClient): # Используем client без auth override
    """
    Тест сохранения прогресса без авторизации POST /api/progress
    Должен возвращать 401 Unauthorized.
    """
    valid_data = {
        "score": 100,
        "correct_answers": 10,
        "total_answers": 10,
        "time_spent": 120.5,
        "date": "2024-01-15"
    }
    response = client.post("/api/progress", json=valid_data) # Вызов без заголовка авторизации
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."} # Стандартный ответ FastAPI

def test_save_progress_service_exception(client_with_auth_override: TestClient, monkeypatch):
    """
    Тест сохранения прогресса, когда сервис вызывает исключение POST /api/progress
    Должен возвращать 500 Internal Server Error.
    """
    mock_service = MagicMock()
    mock_service.record_progress.side_effect = RuntimeError("Database connection failed")
    monkeypatch.setattr(PROGRESS_SERVICE_PATH, mock_service)

    valid_data = {
        "score": 100,
        "correct_answers": 10,
        "total_answers": 10,
        "time_spent": 120.5,
        "date": "2024-01-15"
    }
    response = client_with_auth_override.post("/api/progress", json=valid_data)
    
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert "Failed to save progress: Database connection failed" in response_json["detail"]
    
    mock_service.record_progress.assert_called_once()


def test_get_progress_unauthorized(client: TestClient):
    """
    Тест получения прогресса без авторизации GET /api/progress
    Должен возвращать 401 Unauthorized.
    """
    response = client.get("/api/progress?days=7") # Вызов без заголовка авторизации
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

def test_get_progress_service_exception(client_with_auth_override: TestClient, monkeypatch):
    """
    Тест получения прогресса, когда сервис вызывает исключение GET /api/progress
    Должен возвращать 500 Internal Server Error.
    """
    mock_service = MagicMock()
    mock_service.get_progress.side_effect = RuntimeError("Service unavailable")
    monkeypatch.setattr(PROGRESS_SERVICE_PATH, mock_service)

    response = client_with_auth_override.get("/api/progress?days=7")
    
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert "Failed to get progress data: Service unavailable" in response_json["detail"]
    
    mock_service.get_progress.assert_called_once()

def test_get_weekly_summary_unauthorized(client: TestClient):
    """
    Тест получения еженедельной сводки без авторизации GET /api/progress/weekly-summary
    Должен возвращать 401 Unauthorized.
    """
    response = client.get("/api/progress/weekly-summary") # Вызов без заголовка авторизации
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated. Authorization header is missing."}

def test_get_weekly_summary_service_exception(client_with_auth_override: TestClient, monkeypatch):
    """
    Тест получения еженедельной сводки, когда сервис вызывает исключение GET /api/progress/weekly-summary
    Должен возвращать 500 Internal Server Error.
    """
    mock_service = MagicMock()
    mock_service.get_weekly_summary.side_effect = RuntimeError("Summary service failed")
    monkeypatch.setattr(PROGRESS_SERVICE_PATH, mock_service)

    response = client_with_auth_override.get("/api/progress/weekly-summary")
    
    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert "Failed to get weekly summary: Summary service failed" in response_json["detail"]
    
    mock_service.get_weekly_summary.assert_called_once()

