import pytest
from datetime import datetime
import uuid
from unittest.mock import AsyncMock, patch

from domain.session import SessionModel, RoundDetail, SessionStatus
from domain.achievement import AchievementModel, AchievementType
from repositories.session_repository import SessionRepository
from repositories.achievement_repository import AchievementRepository
from services.session_service import SessionService


class TestSessionService:
    """Тесты для сервиса управления сессиями"""

    @pytest.fixture
    def session_repository_mock(self):
        """Мок для SessionRepository"""
        mock = AsyncMock(spec=SessionRepository)
        return mock

    @pytest.fixture
    def achievement_repository_mock(self):
        """Мок для AchievementRepository"""
        mock = AsyncMock(spec=AchievementRepository)
        return mock

    @pytest.fixture
    def session_service(self, session_repository_mock, achievement_repository_mock):
        """Создание экземпляра сервиса с подставленными моками"""
        return SessionService(
            session_repo=session_repository_mock,
            achievement_repo=achievement_repository_mock
        )

    @pytest.fixture
    def sample_round_details_all_correct(self):
        """Фикстура для деталей раунда, где все ответы правильные"""
        return [
            RoundDetail(question_id=f"q{i}", answer="Correct", is_correct=True, time_spent=1.0)
            for i in range(10)
        ]

    @pytest.fixture
    def sample_round_details_some_incorrect(self):
        """Фикстура для деталей раунда с некоторыми неправильными ответами"""
        details = []
        for i in range(10):
            # Делаем неправильными ответы с индексами 3 и 7
            is_correct = i not in [3, 7]
            details.append(RoundDetail(
                question_id=f"q{i}",
                answer="Answer" if is_correct else "Wrong",
                is_correct=is_correct,
                time_spent=1.0
            ))
        return details

    @pytest.mark.asyncio
    @patch('uuid.uuid4', return_value='test-uuid-123')
    async def test_start_session(self, mock_uuid, session_service, session_repository_mock):
        """Тест создания новой сессии"""
        user_id = "test_user_123"
        game_type = "guess_animal"
        
        # Вызываем тестируемый метод
        session_id = await session_service.start_session(user_id, game_type)
        
        # Проверяем, что вернулся ожидаемый ID
        assert session_id == "test-uuid-123"
        
        # Проверяем, что репозиторий вызван с правильными параметрами
        session_repository_mock.create_session.assert_awaited_once()
        
        # Проверяем параметры, переданные в метод create_session
        called_session = session_repository_mock.create_session.await_args.args[0]
        assert isinstance(called_session, SessionModel)
        assert called_session.session_id == session_id
        assert called_session.user_id == user_id
        assert called_session.game_type == game_type
        assert called_session.status == SessionStatus.ACTIVE
        assert called_session.score == 0
        assert called_session.details == []
        assert isinstance(called_session.start_time, datetime)
        assert called_session.end_time is None

    @pytest.mark.asyncio
    async def test_finish_session_without_achievement(
        self, session_service, session_repository_mock, achievement_repository_mock, 
        sample_round_details_some_incorrect
    ):
        """Тест завершения сессии без достижения Perfect Streak"""
        session_id = "test_session_123"
        user_id = "test_user_123"
        score = 80
        
        # Вызываем тестируемый метод
        await session_service.finish_session(session_id, user_id, sample_round_details_some_incorrect, score)
        
        # Проверяем, что update_session вызван с правильными параметрами
        session_repository_mock.update_session.assert_awaited_once()
        args = session_repository_mock.update_session.await_args.args
        assert args[0] == session_id
        assert args[1] == sample_round_details_some_incorrect
        assert isinstance(args[2], datetime)  # end_time
        assert args[3] == score
        
        # Проверяем, что create_achievement не вызывался
        achievement_repository_mock.create_achievement.assert_not_awaited()

    @pytest.mark.asyncio
    @patch('uuid.uuid4', return_value='achievement-uuid-123')
    async def test_finish_session_with_achievement(
        self, mock_uuid, session_service, session_repository_mock, 
        achievement_repository_mock, sample_round_details_all_correct
    ):
        """Тест завершения сессии с достижением Perfect Streak"""
        session_id = "test_session_456"
        user_id = "test_user_456"
        score = 100
        
        # Вызываем тестируемый метод
        await session_service.finish_session(session_id, user_id, sample_round_details_all_correct, score)
        
        # Проверяем, что update_session вызван с правильными параметрами
        session_repository_mock.update_session.assert_awaited_once()
        args = session_repository_mock.update_session.await_args.args
        assert args[0] == session_id
        assert args[1] == sample_round_details_all_correct
        assert isinstance(args[2], datetime)  # end_time
        assert args[3] == score
        
        # Проверяем, что create_achievement вызван с правильными параметрами
        achievement_repository_mock.create_achievement.assert_awaited_once()
        achievement = achievement_repository_mock.create_achievement.await_args.args[0]
        assert isinstance(achievement, AchievementModel)
        assert achievement.achievement_id == "achievement-uuid-123"
        assert achievement.user_id == user_id
        assert achievement.type == AchievementType.PERFECT_STREAK
        assert isinstance(achievement.earned_at, datetime)
        assert achievement.session_id == session_id
