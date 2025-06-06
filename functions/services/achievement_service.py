# functions/services/achievement_service.py

from datetime import datetime, timedelta
from repositories.achievement_repository import AchievementRepository
from repositories.progress_repository import ProgressRepository
from domain.achievement import AchievementModel, AchievementType
import uuid

class AchievementService:
    def __init__(
        self,
        achievement_repo: AchievementRepository,
        progress_repo: ProgressRepository
    ):
        self._achievement_repo = achievement_repo
        self._progress_repo = progress_repo

    def check_weekly_achievement(self, user_id: str) -> None:
        week_ago = datetime.utcnow() - timedelta(days=7)
        total = self._progress_repo.sum_scores_for_week(user_id, week_ago)
        if total >= 50:
            week_start = week_ago.date()
            if not self._achievement_repo.exists_weekly_achievement(user_id, week_start):
                ach_id = str(uuid.uuid4())
                achievement = AchievementModel(
                    achievement_id=ach_id,
                    user_id=user_id,
                    type=AchievementType.WEEKLY_FIFTY,
                    earned_at=datetime.utcnow(),
                    period_start_date=week_start
                )
                self._achievement_repo.create_achievement(achievement)
