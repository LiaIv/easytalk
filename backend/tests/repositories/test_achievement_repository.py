# backend/tests/repositories/test_achievement_repository.py

import pytest
from datetime import date, datetime, timezone, timedelta
import uuid
from google.cloud.firestore_v1.base_query import FieldFilter
from domain.achievement import AchievementModel, AchievementType
from repositories.achievement_repository import AchievementRepository


class TestAchievementRepository:
    """Тесты для репозитория достижений пользователей"""

    @pytest.fixture(autouse=True)
    def clear_achievements_collection(self, firestore_client):
        """Очищает коллекцию achievements перед каждым тестом"""
        collection_ref = firestore_client.collection("achievements")
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        yield # Тест выполняется здесь
        # Очистка после теста (если необходимо, но обычно yield достаточно)

    @pytest.fixture
    def achievement_repository(self):
        """Инициализируем репозиторий для тестов"""
        return AchievementRepository()

    @pytest.fixture
    def sample_perfect_streak(self):
        """Фикстура для достижения типа Perfect Streak"""
        return AchievementModel(
            achievement_id=f"perfect_streak_{uuid.uuid4()}",
            user_id="test_user_123",
            type=AchievementType.PERFECT_STREAK,
            earned_at=datetime.now(timezone.utc),
            session_id="test_session_123"
        )

    @pytest.fixture
    def sample_weekly_fifty(self):
        """Фикстура для достижения типа Weekly Fifty"""
        # Начало текущей недели
        period_start = date.today() - timedelta(days=date.today().weekday())
        return AchievementModel(
            achievement_id=f"weekly_fifty_{uuid.uuid4()}",
            user_id="test_user_123",
            type=AchievementType.WEEKLY_FIFTY,
            earned_at=datetime.now(timezone.utc),
            period_start_date=period_start
        )

    def test_create_achievement(self, achievement_repository, sample_perfect_streak, firestore_client):
        """Тест создания достижения в БД"""
        # Создаем достижение
        achievement_repository.create_achievement(sample_perfect_streak)

        # Проверяем, что достижение создано в Firestore
        doc = firestore_client.collection("achievements").document(sample_perfect_streak.achievement_id).get()
        assert doc.exists

        # Проверяем, что данные корректны
        achievement_data = doc.to_dict()
        assert achievement_data["user_id"] == sample_perfect_streak.user_id
        assert achievement_data["type"] == sample_perfect_streak.type.value
        assert isinstance(achievement_data["earned_at"], str)  # Дата сериализована в строку
        assert achievement_data["session_id"] == sample_perfect_streak.session_id

    def test_create_weekly_achievement(self, achievement_repository, sample_weekly_fifty, firestore_client):
        """Тест создания еженедельного достижения в БД"""
        # Создаем достижение
        achievement_repository.create_achievement(sample_weekly_fifty)

        # Проверяем, что достижение создано в Firestore
        doc = firestore_client.collection("achievements").document(sample_weekly_fifty.achievement_id).get()
        assert doc.exists

        # Проверяем, что данные корректны
        achievement_data = doc.to_dict()
        assert achievement_data["user_id"] == sample_weekly_fifty.user_id
        assert achievement_data["type"] == sample_weekly_fifty.type.value
        assert isinstance(achievement_data["earned_at"], str)  # Дата сериализована в строку
        assert achievement_data["period_start_date"] == sample_weekly_fifty.period_start_date.isoformat()

    def test_get_user_achievements(self, achievement_repository, sample_perfect_streak, sample_weekly_fifty, firestore_client):
        """Тест получения всех достижений пользователя"""
        # Создаем несколько достижений для одного пользователя
        user_id = "test_user_456"
        
        # Изменяем user_id в наших фикстурах для этого теста
        sample_perfect_streak.user_id = user_id
        sample_weekly_fifty.user_id = user_id
        
        # Сохраняем достижения напрямую в Firestore
        firestore_client.collection("achievements").document(sample_perfect_streak.achievement_id).set(
            sample_perfect_streak.model_dump(mode="json")
        )
        
        firestore_client.collection("achievements").document(sample_weekly_fifty.achievement_id).set(
            sample_weekly_fifty.model_dump(mode="json")
        )
        
        # Получаем достижения пользователя
        achievements = achievement_repository.get_user_achievements(user_id)
        
        # Проверяем, что получены оба достижения
        assert len(achievements) == 2
        
        # Создаем сет типов достижений для проверки
        achievement_types = {achievement.type for achievement in achievements}
        assert AchievementType.PERFECT_STREAK in achievement_types
        assert AchievementType.WEEKLY_FIFTY in achievement_types
        
    def test_exists_weekly_achievement(self, achievement_repository, sample_weekly_fifty, firestore_client):
        """Тест проверки существования еженедельного достижения"""
        user_id = "test_user_789"
        period_start = date.today() - timedelta(days=date.today().weekday())
        
        # Создаем достижение с конкретным периодом
        sample_weekly_fifty.user_id = user_id
        sample_weekly_fifty.period_start_date = period_start
        
        # Сохраняем достижение в БД
        firestore_client.collection("achievements").document(sample_weekly_fifty.achievement_id).set(
            sample_weekly_fifty.model_dump(mode="json")
        )
        
        # Проверяем существование достижения для этого периода
        exists = achievement_repository.exists_weekly_achievement(user_id, period_start)
        assert exists is True
        
        # Проверяем для другого периода (должно быть False)
        other_period = period_start - timedelta(days=7)
        exists = achievement_repository.exists_weekly_achievement(user_id, other_period)
        assert exists is False
        
    def test_delete_weekly_achievements(self, achievement_repository, firestore_client):
        """Тест удаления еженедельных достижений"""
        user_id = "test_user_999"
        period_start = date.today() - timedelta(days=date.today().weekday())
        
        # Создаем несколько достижений с одинаковым периодом
        for i in range(3):
            achievement = AchievementModel(
                achievement_id=f"weekly_fifty_{uuid.uuid4()}",
                user_id=user_id,
                type=AchievementType.WEEKLY_FIFTY,
                earned_at=datetime.now(timezone.utc),
                period_start_date=period_start
            )
            
            # Сохраняем достижение в БД
            firestore_client.collection("achievements").document(achievement.achievement_id).set(
                achievement.model_dump(mode="json")
            )
        
        # Проверяем, что достижения были созданы
        query = (
            firestore_client.collection("achievements")
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("type", "==", "weekly_fifty"))
            .where(filter=FieldFilter("period_start_date", "==", period_start.isoformat()))
        )
        docs = list(query.stream())
        assert len(docs) == 3
        
        # Удаляем еженедельные достижения
        achievement_repository.delete_weekly_achievements(user_id, period_start)
        
        # Проверяем, что достижения были удалены
        docs = list(query.stream())
        assert len(docs) == 0
