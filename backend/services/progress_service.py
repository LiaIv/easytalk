from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import Depends
from repositories.progress_repository import ProgressRepository
from repositories.achievement_repository import AchievementRepository
from domain.achievement import AchievementModel, AchievementType
import uuid
from domain.progress import ProgressRecord
from shared.dependencies import get_progress_repository, get_achievement_repository

class ProgressService:
    def __init__(self, progress_repo: ProgressRepository = Depends(get_progress_repository), achievement_repo: AchievementRepository = Depends(get_achievement_repository)):
        self._progress_repo = progress_repo
        self._achievement_repo = achievement_repo
    
    async def record_progress(
        self,
        user_id: str,
        score: int,
        correct_answers: int,
        total_answers: int,
        time_spent: float,
        record_date: Optional[date] = None,
    ) -> str:
        """Создаёт запись о прогрессе и возвращает её ID."""
        # Если дата не указана, используем сегодняшнюю
        if record_date is None:
            record_date = date.today()

        progress_record = ProgressRecord(
            user_id=user_id,
            date=record_date,
            score=score,
            correct_answers=correct_answers,
            total_answers=total_answers,
            time_spent=time_spent,
        )

        await self._progress_repo.record_daily_score(progress_record)

        # ----- ACHIEVEMENT RULES -----
        await self._maybe_award_score_achievements(user_id)
        await self._maybe_award_streak_achievement(user_id, record_date)

        return f"{user_id}_{record_date.isoformat()}"
    
    # ---------- ACHIEVEMENT HELPERS ----------
    async def _maybe_award_score_achievements(self, user_id: str) -> None:
        """Проверяет общий счёт и выдаёт ачивки TOTAL_SCORE_*"""
        thresholds = [
            (50, AchievementType.TOTAL_SCORE_50),
            (100, AchievementType.TOTAL_SCORE_100),
            (500, AchievementType.TOTAL_SCORE_500),
        ]
        total_score = await self._progress_repo.sum_total_score(user_id)
        for score, ach_type in thresholds:
            if total_score >= score and not await self._achievement_repo.exists_achievement(user_id, ach_type):
                ach_id = str(uuid.uuid4())
                achievement = AchievementModel(
                    achievement_id=ach_id,
                    user_id=user_id,
                    type=ach_type,
                    earned_at=datetime.utcnow(),
                )
                await self._achievement_repo.create_achievement(achievement)

    async def _maybe_award_streak_achievement(self, user_id: str, today: date) -> None:
        """Выдаёт STREAK_7_DAYS, если есть записи за семь подряд дней включая today."""
        from datetime import timedelta
        start = today - timedelta(days=6)
        records = await self._progress_repo.get_progress(user_id, start.isoformat(), today.isoformat())
        if len(records) < 7:
            return
        recorded_dates = {r.date for r in records}
        if all((start + timedelta(i)) in recorded_dates for i in range(7)):
            if not await self._achievement_repo.exists_achievement(user_id, AchievementType.STREAK_7_DAYS):
                ach_id = str(uuid.uuid4())
                achievement = AchievementModel(
                    achievement_id=ach_id,
                    user_id=user_id,
                    type=AchievementType.STREAK_7_DAYS,
                    earned_at=datetime.utcnow(),
                    period_start_date=start,
                )
                await self._achievement_repo.create_achievement(achievement)

    async def get_progress(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Возвращает детализацию прогресса за *days* дней."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        records = await self._progress_repo.get_progress(
            user_id,
            start_date.isoformat(),
            end_date.isoformat(),
        )

        total_score = sum(r.score for r in records)
        total_correct = sum(r.correct_answers for r in records)
        total_answers = sum(r.total_answers for r in records)

        data = [
            {
                "date": r.date.isoformat(),
                "score": r.score,
                "success_rate": r.success_rate,
                "correct_answers": r.correct_answers,
                "total_answers": r.total_answers,
                "time_spent": r.time_spent,
            }
            for r in records
        ]

        average_score = total_score / len(records) if records else 0
        success_rate = total_correct / total_answers if total_answers else 0

        return {
            "data": data,
            "total_score": total_score,
            "average_score": round(average_score, 1),
            "success_rate": round(success_rate, 2),
        }
    
    async def get_weekly_summary(self, user_id: str) -> int:
        """Сумма очков за последние 7 дней."""
        week_ago = datetime.now() - timedelta(days=7)
        return await self._progress_repo.sum_scores_for_week(user_id, week_ago)
    
    # ---------- INTERNAL HELPER ----------
    
    async def _get_records_for_period(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[ProgressRecord]:
        """Вспомогательный метод (оставлен для возможного переиспользования)."""
        return await self._progress_repo.get_progress(
            user_id, start_date.isoformat(), end_date.isoformat()
        )
