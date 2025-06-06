# functions/tests/repositories/test_session_repository.py
import pytest
from datetime import datetime
from domain.session import SessionModel, RoundDetail, SessionStatus
from repositories.session_repository import SessionRepository


class TestSessionRepository:
    """Тесты для SessionRepository"""

    @pytest.fixture(scope="function")
    def session_repository(self, firestore_client, clean_firestore):
        """Фикстура для создания экземпляра SessionRepository"""
        return SessionRepository()

    @pytest.fixture(scope="function")
    def sample_session(self):
        """Фикстура для создания тестовой сессии"""
        return SessionModel(
            session_id="test_session_123",
            user_id="test_user_123",
            game_type="guess_animal",
            start_time=datetime.now(),
            end_time=None,
            status=SessionStatus.ACTIVE,
            score=0,
            details=[]
        )
    
    @pytest.fixture(scope="function")
    def sample_round_details(self):
        """Фикстура для создания тестовых деталей раунда"""
        return [
            RoundDetail(
                question_id="dog_1",
                answer="Собака",
                is_correct=True,
                time_spent=2.5
            ),
            RoundDetail(
                question_id="cat_1",
                answer="Киска",
                is_correct=False,
                time_spent=3.2
            )
        ]

    def test_create_session(self, session_repository, sample_session, firestore_client):
        """Тест создания сессии в БД"""
        # Создаем сессию
        session_repository.create_session(sample_session)
        
        # Проверяем, что сессия создана в Firestore
        doc = firestore_client.collection("sessions").document(sample_session.session_id).get()
        assert doc.exists
        
        # Проверяем, что данные корректны
        session_data = doc.to_dict()
        assert session_data["user_id"] == sample_session.user_id
        assert session_data["game_type"] == sample_session.game_type
        assert isinstance(session_data["start_time"], str)  # При сериализации с mode="json" дата сериализуется в строку
        assert session_data["status"] == sample_session.status
        
        # Проверяем, что исключенные поля не были сохранены
        assert "session_id" not in session_data
        # С моделью SessionModel поле end_time может быть сохранено как null
        if "end_time" in session_data:
            assert session_data["end_time"] is None
        assert "score" not in session_data
        assert "details" not in session_data
    
    def test_get_session(self, session_repository, sample_session, firestore_client):
        """Тест получения сессии по ID"""
        # Создаем сессию для теста
        data = sample_session.model_dump(mode="json", exclude={"session_id", "ended_at", "score", "details"})
        firestore_client.collection("sessions").document(sample_session.session_id).set(data)
        
        # Получаем сессию через репозиторий
        session = session_repository.get_session(sample_session.session_id)
        
        # Проверяем, что сессия получена корректно
        assert session is not None
        assert session.session_id == sample_session.session_id
        assert session.user_id == sample_session.user_id
        assert session.game_type == sample_session.game_type
    
    def test_get_session_not_found(self, session_repository):
        """Тест получения несуществующей сессии"""
        # Пытаемся получить несуществующую сессию
        session = session_repository.get_session("non_existent_session")
        
        # Проверяем, что результат None
        assert session is None
    
    def test_update_session(self, session_repository, sample_session, sample_round_details, firestore_client):
        """Тест обновления сессии с деталями раундов"""
        # Создаем сессию для теста
        data = sample_session.model_dump(mode="json", exclude={"session_id", "end_time", "score", "details"})
        firestore_client.collection("sessions").document(sample_session.session_id).set(data)
        
        # Обновляем сессию с деталями
        end_time = datetime.now()
        score = 10
        session_repository.update_session(
            sample_session.session_id,
            sample_round_details,
            end_time,
            score
        )
        
        # Получаем обновленную сессию из БД
        doc = firestore_client.collection("sessions").document(sample_session.session_id).get()
        assert doc.exists
        
        # Проверяем, что данные обновлены корректно
        session_data = doc.to_dict()
        assert session_data["user_id"] == sample_session.user_id
        assert session_data["game_type"] == sample_session.game_type
        assert isinstance(session_data["start_time"], str)  # При сериализации с mode="json" дата сериализуется в строку
        assert isinstance(session_data["ended_at"], str)  # Дата сериализована в ISO строку
        assert session_data["score"] == score
        
        # Проверяем детали раундов
        assert "details" in session_data
        assert len(session_data["details"]) == len(sample_round_details)
        assert session_data["details"][0]["question_id"] == sample_round_details[0].question_id
        assert session_data["details"][0]["is_correct"] == sample_round_details[0].is_correct
        assert session_data["details"][1]["answer"] == sample_round_details[1].answer
