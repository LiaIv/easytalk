# functions/tests/test_session_service.py

import pytest
from datetime import datetime, timedelta
from domain.session import SessionModel, RoundDetail
from domain.achievement import AchievementModel
from repositories.session_repository import SessionRepository
from repositories.achievement_repository import AchievementRepository
from services.session_service import SessionService
from google.cloud.exceptions import NotFound


@pytest.fixture()
def session_repo():
    return SessionRepository()


@pytest.fixture()
def achievement_repo():
    return AchievementRepository()


@pytest.fixture()
def session_service(session_repo, achievement_repo):
    return SessionService(session_repo, achievement_repo)


def test_start_session_creates_document(session_service, session_repo):
    """
    Проверяем, что start_session записывает сессию в Firestore.
    """
    user_id = "user_test"
    game_type = "guess_animal"
    session_id = session_service.start_session(user_id, game_type)

    # Попробуем получить созданную сессию через репозиторий
    fetched = session_repo.get_session(session_id)
    assert fetched is not None
    assert fetched.user_id == user_id
    assert fetched.game_type == game_type
    # Пока мы не закрывали сессию, details, ended_at и score должны быть None
    assert fetched.details is None
    assert fetched.ended_at is None
    assert fetched.score is None


def test_finish_session_updates_and_creates_achievement(session_service, session_repo, achievement_repo):
    """
    1) Создаём сессию ручным вызовом start_session.
    2) Формируем details с 10 правильными результатами → ожидаем создание достижения perfect_streak.
    3) Проверяем, что в коллекции 'sessions' появились новые поля, и в 'achievements' документ.
    """
    user_id = "user_test2"
    game_type = "build_sentence"
    session_id = session_service.start_session(user_id, game_type)

    # Генерируем 10 RoundDetail, все is_correct=True
    details = [
        RoundDetail(round_index=i + 1, is_correct=True, attempts=1)
        for i in range(10)
    ]
    score = 100

    # Завершаем сессию
    session_service.finish_session(session_id, user_id, details, score)

    # Проверяем, что сессия обновлена
    fetched = session_repo.get_session(session_id)
    assert fetched is not None
    assert fetched.score == score
    assert isinstance(fetched.details, list)
    assert len(fetched.details) == 10
    assert all(d.is_correct for d in fetched.details)

    # Проверяем, что достижение Perfect Streak создано
    achievements = achievement_repo.get_user_achievements(user_id)
    # Среди достижений должен быть хотя бы один тип 'perfect_streak'
    assert any(a.type == "perfect_streak" for a in achievements)


def test_finish_session_without_perfect_streak_does_not_create_achievement(session_service, session_repo, achievement_repo):
    """
    Если не все is_correct=True, достижение perfect_streak не создаётся.
    """
    user_id = "user_test3"
    game_type = "guess_animal"
    session_id = session_service.start_session(user_id, game_type)

    # Генерируем 10 RoundDetail, но хотя бы один is_correct=False
    details = [
        RoundDetail(round_index=i + 1, is_correct=(i != 5), attempts=1)  # 6-й элемент False
        for i in range(10)
    ]
    score = 50

    session_service.finish_session(session_id, user_id, details, score)

    # Проверяем, что достижение НЕ создано
    achievements = achievement_repo.get_user_achievements(user_id)
    assert all(a.type != "perfect_streak" for a in achievements)
