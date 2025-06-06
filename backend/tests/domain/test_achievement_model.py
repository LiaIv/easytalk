# tests/domain/test_achievement_model.py
import pytest
from datetime import datetime
from pydantic import ValidationError

from domain.achievement import AchievementModel, AchievementType


class TestAchievementModel:
    """Тесты для валидации AchievementModel"""
    
    def test_valid_achievement_model(self):
        """Тест создания корректной модели достижения"""
        # Текущая дата
        now = datetime.now()
        
        # Создаем корректную запись достижения
        achievement = AchievementModel(
            achievement_id="ach123",
            user_id="user123",
            type=AchievementType.PERFECT_STREAK,
            earned_at=now,
            session_id="session123"
        )
        
        # Проверяем, что поля заполнены правильно
        assert achievement.achievement_id == "ach123"
        assert achievement.user_id == "user123"
        assert achievement.type == AchievementType.PERFECT_STREAK
        assert achievement.earned_at == now
        assert achievement.session_id == "session123"
        
    def test_achievement_type_enum(self):
        """Тест проверки типов достижений через Enum"""
        # Проверяем, что все ожидаемые типы достижений определены
        assert AchievementType.PERFECT_STREAK == "perfect_streak"
        assert AchievementType.WEEKLY_FIFTY == "weekly_fifty"
        
        # Создаем достижения с разными типами
        ach1 = AchievementModel(
            achievement_id="ach1",
            user_id="user123",
            type=AchievementType.PERFECT_STREAK,
            earned_at=datetime.now()
        )
        
        ach2 = AchievementModel(
            achievement_id="ach2",
            user_id="user123",
            type=AchievementType.WEEKLY_FIFTY,
            earned_at=datetime.now()
        )
        
        assert ach1.type == AchievementType.PERFECT_STREAK
        assert ach2.type == AchievementType.WEEKLY_FIFTY
        
    def test_achievement_invalid_type(self):
        """Тест для проверки недопустимого типа достижения"""
        # Проверяем, что создание с неверным типом достижения вызывает ошибку
        with pytest.raises(ValidationError) as error_info:
            AchievementModel(
                achievement_id="ach123",
                user_id="user123",
                type="invalid_type",  # Неверный тип
                earned_at=datetime.now()
            )
        
        # Убеждаемся, что причина ошибки связана с валидацией типа
        errors = error_info.value.errors()
        assert any("type" in error.get("loc", []) for error in errors)
        
    def test_achievement_optional_session_id(self):
        """Тест для проверки опционального поля session_id"""
        # Weekly Fifty может не иметь session_id, так как может быть заработано не в конкретной сессии
        achievement = AchievementModel(
            achievement_id="ach123",
            user_id="user123",
            type=AchievementType.WEEKLY_FIFTY,
            earned_at=datetime.now()
            # session_id не указан (опционален)
        )
        
        assert achievement.session_id is None
        
    def test_achievement_model_required_fields(self):
        """Тест для проверки обязательных полей"""
        now = datetime.now()
        
        # Проверяем, что создание без achievement_id вызывает ошибку
        with pytest.raises(ValidationError):
            AchievementModel(
                user_id="user123",
                type=AchievementType.PERFECT_STREAK,
                earned_at=now
                # achievement_id отсутствует
            )
        
        # Проверяем, что создание без user_id вызывает ошибку
        with pytest.raises(ValidationError):
            AchievementModel(
                achievement_id="ach123",
                type=AchievementType.PERFECT_STREAK,
                earned_at=now
                # user_id отсутствует
            )
        
        # Проверяем, что создание без type вызывает ошибку
        with pytest.raises(ValidationError):
            AchievementModel(
                achievement_id="ach123",
                user_id="user123",
                earned_at=now
                # type отсутствует
            )
        
        # Проверяем, что создание без earned_at вызывает ошибку
        with pytest.raises(ValidationError):
            AchievementModel(
                achievement_id="ach123",
                user_id="user123",
                type=AchievementType.PERFECT_STREAK
                # earned_at отсутствует
            )
