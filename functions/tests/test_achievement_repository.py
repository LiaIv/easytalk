# functions/tests/test_achievement_repository.py

import pytest
from datetime import datetime, date
from domain.achievement import AchievementModel
from repositories.achievement_repository import AchievementRepository

@pytest.fixture()
def achievement_repo():
    return AchievementRepository()

def test_create_and_get_user_achievement(achievement_repo):
    user_id = "ach_user1"
    ach_id = "ach_test_1"
    achievement = AchievementModel(
        achievement_id=ach_id,
        user_id=user_id,
        type="perfect_streak",
        earned_at=datetime.utcnow(),
        period_start_date=None
    )
    achievement_repo.create_achievement(achievement)

    achievements = achievement_repo.get_user_achievements(user_id)
    assert any(a.achievement_id == ach_id for a in achievements)

def test_exists_weekly_achievement(achievement_repo):
    user_id = "ach_user2" 
    period_start = date.today()
    ach_id = "ach_test_2"

    # ===== ВАЖНО: ДОБАВЬТЕ ЭТУ СТРОКУ =====
    achievement_repo.delete_weekly_achievements(user_id, period_start)
    # =======================================

    # Сначала убеждаемся, что в базе нет weekly_achievement
    assert not achievement_repo.exists_weekly_achievement(user_id, period_start)

    # Создаём достижение weekly_fifty
    achievement = AchievementModel(
        achievement_id=ach_id,
        user_id=user_id,
        type="weekly_fifty",
        earned_at=datetime.utcnow(), # Используем datetime
        period_start_date=period_start
    )
    achievement_repo.create_achievement(achievement)
    assert achievement_repo.exists_weekly_achievement(user_id, period_start)
