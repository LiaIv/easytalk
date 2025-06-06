# functions/services/session_service.py

import uuid
from datetime import datetime
from domain.session import SessionModel, RoundDetail
from repositories.session_repository import SessionRepository
from repositories.achievement_repository import AchievementRepository
from domain.achievement import AchievementModel

class SessionService:
    def __init__(
        self,
        session_repo: SessionRepository,
        achievement_repo: AchievementRepository
    ):
        self._session_repo = session_repo
        self._achievement_repo = achievement_repo

    def start_session(self, user_id: str, game_type: str) -> str:
        session_id = str(uuid.uuid4())
        session = SessionModel(
            session_id=session_id,
            user_id=user_id,
            game_type=game_type,
            started_at=datetime.utcnow()
        )
        self._session_repo.create_session(session)
        return session_id

    def finish_session(
        self,
        session_id: str,
        user_id: str,
        details: list[RoundDetail],
        score: int
    ) -> None:
        ended_at = datetime.utcnow()
        self._session_repo.update_session(session_id, details, ended_at, score)

        # Правило «10 правильных подряд»
        if all(detail.is_correct for detail in details):
            ach_id = str(uuid.uuid4())
            achievement = AchievementModel(
                achievement_id=ach_id,
                user_id=user_id,
                type="perfect_streak",
                earned_at=datetime.utcnow(),
                period_start_date=None
            )
            self._achievement_repo.create_achievement(achievement)
