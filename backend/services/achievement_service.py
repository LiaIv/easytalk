# backend/services/achievement_service.py

from datetime import datetime, timedelta, timezone
from fastapi import Depends
from repositories.achievement_repository import AchievementRepository
from repositories.progress_repository import ProgressRepository
from domain.achievement import AchievementModel, AchievementType
from shared.dependencies import get_achievement_repository, get_progress_repository
import uuid

class AchievementService:
    def __init__(
        self,
        achievement_repo: AchievementRepository = Depends(get_achievement_repository),
        progress_repo: ProgressRepository = Depends(get_progress_repository)
    ):
        self._achievement_repo = achievement_repo
        self._progress_repo = progress_repo

    def check_weekly_achievement(self, user_id: str) -> None:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        total = self._progress_repo.sum_scores_for_week(user_id, week_ago)
        if total >= 50:
            week_start = week_ago.date()
            if not self._achievement_repo.exists_weekly_achievement(user_id, week_start):
                ach_id = str(uuid.uuid4())
                achievement = AchievementModel(
                    achievement_id=ach_id,
                    user_id=user_id,
                    type=AchievementType.WEEKLY_FIFTY,
                    earned_at=datetime.now(timezone.utc),
                    period_start_date=week_start
                )
                self._achievement_repo.create_achievement(achievement)
