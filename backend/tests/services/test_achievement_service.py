import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, date, timedelta

from repositories.achievement_repository import AchievementRepository
from repositories.progress_repository import ProgressRepository
from services.achievement_service import AchievementService
from domain.achievement import AchievementModel, AchievementType


class TestAchievementService:
    """Тесты для сервиса достижений"""

    @pytest.fixture
    def achievement_repository_mock(self):
        """Мок для AchievementRepository"""
        mock = AsyncMock(spec=AchievementRepository)
        return mock

    @pytest.fixture
    def progress_repository_mock(self):
        """Мок для ProgressRepository"""
        mock = AsyncMock(spec=ProgressRepository)
        return mock

    @pytest.fixture
    def achievement_service(self, achievement_repository_mock, progress_repository_mock):
        """Создание экземпляра сервиса с подставленными моками"""
        return AchievementService(
            achievement_repo=achievement_repository_mock,
            progress_repo=progress_repository_mock
        )

    @pytest.mark.asyncio
    @patch('uuid.uuid4', return_value='achievement-uuid-123')
    async def test_check_weekly_achievement_earned(self, mock_uuid, achievement_service, 
                                           achievement_repository_mock, progress_repository_mock):
        """Тест проверки и создания еженедельного достижения, когда оно заработано"""
        user_id = "test_user_123"
        
        # Настраиваем моки
        progress_repository_mock.sum_scores_for_week.return_value = 75  # Больше 50, должно создать достижение
        achievement_repository_mock.exists_weekly_achievement.return_value = False  # Достижение еще не существует
        
        # Вызываем тестируемый метод
        await achievement_service.check_weekly_achievement(user_id)
        
        # Проверяем, что вызвался метод sum_scores_for_week
        progress_repository_mock.sum_scores_for_week.assert_awaited_once()
        args = progress_repository_mock.sum_scores_for_week.call_args[0]
        assert args[0] == user_id
        assert isinstance(args[1], datetime)  # week_ago
        
        # Проверяем, что вызвался метод exists_weekly_achievement
        achievement_repository_mock.exists_weekly_achievement.assert_awaited_once()
        args = achievement_repository_mock.exists_weekly_achievement.call_args[0]
        assert args[0] == user_id
        assert isinstance(args[1], date)  # week_start
        
        # Проверяем, что достижение было создано
        achievement_repository_mock.create_achievement.assert_awaited_once()
        achievement = achievement_repository_mock.create_achievement.await_args.args[0]
        assert isinstance(achievement, AchievementModel)
        assert achievement.achievement_id == "achievement-uuid-123"
        assert achievement.user_id == user_id
        assert achievement.type == AchievementType.WEEKLY_FIFTY
        assert isinstance(achievement.earned_at, datetime)
        assert isinstance(achievement.period_start_date, date)

    @pytest.mark.asyncio
    async def test_check_weekly_achievement_not_enough_score(self, achievement_service, 
                                                     achievement_repository_mock, progress_repository_mock):
        """Тест проверки недостаточного количества очков для еженедельного достижения"""
        user_id = "test_user_123"
        
        # Настраиваем мок - недостаточно очков
        progress_repository_mock.sum_scores_for_week.return_value = 30  # Меньше 50, не должно создать достижение
        
        # Вызываем тестируемый метод
        await achievement_service.check_weekly_achievement(user_id)
        
        # Проверяем, что вызвался метод sum_scores_for_week
        progress_repository_mock.sum_scores_for_week.assert_awaited_once()
        
        # Проверяем, что метод exists_weekly_achievement не вызывался
        achievement_repository_mock.exists_weekly_achievement.assert_not_awaited()
        
        # Проверяем, что достижение не было создано
        achievement_repository_mock.create_achievement.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_check_weekly_achievement_already_exists(self, achievement_service, 
                                                   achievement_repository_mock, progress_repository_mock):
        """Тест проверки случая, когда еженедельное достижение уже существует"""
        user_id = "test_user_123"
        
        # Настраиваем моки
        progress_repository_mock.sum_scores_for_week.return_value = 100  # Достаточно очков
        achievement_repository_mock.exists_weekly_achievement.return_value = True  # Но достижение уже существует
        
        # Вызываем тестируемый метод
        await achievement_service.check_weekly_achievement(user_id)
        
        # Проверяем, что вызвался метод sum_scores_for_week
        progress_repository_mock.sum_scores_for_week.assert_awaited_once()
        
        # Проверяем, что вызвался метод exists_weekly_achievement
        achievement_repository_mock.exists_weekly_achievement.assert_awaited_once()
        
        # Проверяем, что достижение не было создано (т.к. оно уже существует)
        achievement_repository_mock.create_achievement.assert_not_awaited()
