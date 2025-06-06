# tests/domain/test_session_model.py
import pytest
from datetime import datetime
from pydantic import ValidationError

from domain.session import SessionModel, RoundDetail, SessionStatus


class TestSessionModel:
    """Тесты для валидации SessionModel"""
    
    def test_valid_session_model(self):
        """Тест создания корректной модели игровой сессии"""
        # Создаем список с 10 деталями раундов
        details = [
            RoundDetail(
                question_id=f"q{i}", 
                answer=f"answer{i}", 
                is_correct=i % 2 == 0, 
                time_spent=i+1
            ) for i in range(10)
        ]
        
        now = datetime.now()
        
        # Создаем полностью заполненный объект сессии
        session = SessionModel(
            session_id="test123",
            user_id="user123",
            game_type="guess_animal",
            start_time=now,
            end_time=now,
            status=SessionStatus.FINISHED,
            score=7,
            details=details
        )
        
        # Проверяем, что поля заполнены правильно
        assert session.session_id == "test123"
        assert session.user_id == "user123"
        assert session.game_type == "guess_animal"
        assert session.start_time == now
        assert session.end_time == now
        assert session.status == SessionStatus.FINISHED
        assert session.score == 7
        assert len(session.details) == 10
        
    def test_session_model_active_status(self):
        """Тест создания модели с активным статусом"""
        # Создаем модель с активным статусом и минимальными данными
        now = datetime.now()
        session = SessionModel(
            session_id="test123",
            user_id="user123",
            game_type="build_sentence",
            start_time=now,
            status=SessionStatus.ACTIVE
            # end_time и score не указаны для активной сессии
        )
        
        # Проверяем статус и отсутствие end_time и score
        assert session.status == SessionStatus.ACTIVE
        assert session.end_time is None
        assert session.score is None
        assert session.details == []
        
    def test_session_model_invalid_game_type(self):
        """Тест для проверки валидации типа игры"""
        # Проверяем, что создание с неверным типом игры вызывает ошибку
        with pytest.raises(ValidationError) as error_info:
            SessionModel(
                session_id="test123",
                user_id="user123",
                game_type="invalid_game",  # Неверный тип игры
                start_time=datetime.now(),
                status=SessionStatus.ACTIVE
            )
        
        # Убеждаемся, что причина ошибки связана с валидацией game_type
        errors = error_info.value.errors()
        assert any("game_type" in error.get("loc", []) for error in errors)
        
    def test_session_model_too_many_details(self):
        """Тест для проверки максимального количества деталей (10)"""
        # Создаем список с 11 деталями (больше максимума)
        too_many_details = [
            RoundDetail(
                question_id=f"q{i}", 
                answer=f"answer{i}", 
                is_correct=i % 2 == 0, 
                time_spent=i+1
            ) for i in range(11)  # 11 элементов
        ]
        
        # Проверяем, что создание с более чем 10 деталями вызывает ошибку
        with pytest.raises(ValidationError) as error_info:
            SessionModel(
                session_id="test123",
                user_id="user123",
                game_type="guess_animal",
                start_time=datetime.now(),
                status=SessionStatus.FINISHED,
                end_time=datetime.now(),
                score=7,
                details=too_many_details  # Слишком много деталей
            )
        
        # Убеждаемся, что причина ошибки связана с количеством элементов
        errors = error_info.value.errors()
        assert any("details" in str(error.get("loc", [])) for error in errors)
        
        # Проверяем содержание сообщения об ошибке
        error_messages = [error.get("msg", "").lower() for error in errors]
        # В нашем валидаторе используется именно это сообщение об ошибке
        assert any("максимальное количество деталей" in msg for msg in error_messages)
        
    def test_round_detail_validation(self):
        """Тест для валидации модели RoundDetail"""
        # Проверяем корректное создание
        detail = RoundDetail(
            question_id="q1",
            answer="lion",
            is_correct=True,
            time_spent=3.5
        )
        
        assert detail.question_id == "q1"
        assert detail.answer == "lion"
        assert detail.is_correct is True
        assert detail.time_spent == 3.5
        
        # Проверяем валидацию отрицательного времени
        with pytest.raises(ValidationError) as error_info:
            RoundDetail(
                question_id="q1",
                answer="lion",
                is_correct=True,
                time_spent=-1  # Отрицательное время
            )
            
        errors = error_info.value.errors()
        assert any("time_spent" in error.get("loc", []) for error in errors)
        assert any("greater than or equal" in error.get("msg", "") for error in errors)
