# functions/tests/test_achievement_service.py

import uuid
import pytest
from datetime import date, datetime, timedelta
from domain.progress import ProgressRecord
from repositories.progress_repository import ProgressRepository
from repositories.achievement_repository import AchievementRepository
from services.achievement_service import AchievementService

@pytest.fixture()
def progress_repo():
    return ProgressRepository()

@pytest.fixture()
def achievement_repo():
    return AchievementRepository()

@pytest.fixture()
def achievement_service(achievement_repo, progress_repo):
    return AchievementService(achievement_repo, progress_repo)

def test_check_weekly_achievement_creates_if_threshold_exceeded(
    progress_repo, achievement_repo, achievement_service
):
    user_id = f"serv_user1_{uuid.uuid4()}" # Уникальный user_id
    today = date.today()
    for i in range(7):
        record_date = today - timedelta(days=i)
        progress_repo.record_daily_score(
            record=ProgressRecord(user_id=user_id, date=record_date, daily_score=10)
        )
   
    week_start_for_check = (datetime.utcnow().date() - timedelta(days=7))
   
    achievement_repo.delete_weekly_achievements(user_id, week_start_for_check)
   
    assert not achievement_repo.exists_weekly_achievement(user_id, week_start_for_check)
   
    achievement_service.check_weekly_achievement(user_id) 
   
    assert achievement_repo.exists_weekly_achievement(user_id, week_start_for_check)

def test_check_weekly_achievement_does_not_create_if_not_exceeded(
    progress_repo, achievement_repo, achievement_service
):
    user_id = "serv_user2"
    # Запишем 3 записи с daily_score = 5 (итого 15 за неделю)
    today = date.today()
    for i in range(3):
        record_date = today - timedelta(days=i)
        progress_repo.record_daily_score(
            record=ProgressRecord(user_id=user_id, date=record_date, daily_score=5)
        )

    week_start = (datetime.utcnow() - timedelta(days=7)).date()
    # Убеждаемся, что пока достижения нет
    assert not achievement_repo.exists_weekly_achievement(user_id, week_start)

    # Запускаем проверку
    achievement_service.check_weekly_achievement(user_id)

    # По-прежнему не должно быть достижения
    assert not achievement_repo.exists_weekly_achievement(user_id, week_start)
