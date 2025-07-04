import uuid
from datetime import datetime, timezone
from domain.session import SessionModel, RoundDetail, SessionStatus
from domain.achievement import AchievementModel, AchievementType
from fastapi import Depends
from repositories.session_repository import SessionRepository
from repositories.achievement_repository import AchievementRepository
from shared.dependencies import get_session_repository, get_achievement_repository


class SessionService:
    def __init__(
        self,
        session_repo: SessionRepository = Depends(get_session_repository),
        achievement_repo: AchievementRepository = Depends(get_achievement_repository),
    ):
        self._session_repo = session_repo
        self._achievement_repo = achievement_repo

    async def start_session(self, user_id: str, game_type: str) -> str:
        session_id = str(uuid.uuid4())
        session = SessionModel(
            session_id=session_id,
            user_id=user_id,
            game_type=game_type,
            start_time=datetime.now(timezone.utc),
            status=SessionStatus.ACTIVE,
            score=0,
            details=[],
        )
        await self._session_repo.create_session(session)
        return session_id

    async def finish_session(
        self, session_id: str, user_id: str, details: list[RoundDetail], score: int
    ) -> None:
        end_time = datetime.now(timezone.utc)
        await self._session_repo.update_session(session_id, details, end_time, score)

        # Правило «10 правильных подряд»
        if all(detail.is_correct for detail in details):
            ach_id = str(uuid.uuid4())
            achievement = AchievementModel(
                achievement_id=ach_id,
                user_id=user_id,
                type=AchievementType.PERFECT_STREAK,
                earned_at=datetime.now(timezone.utc),
                session_id=session_id,
            )
            await self._achievement_repo.create_achievement(achievement)

    async def get_active_session(self, user_id: str) -> SessionModel | None:
        """Возвращает текущую активную сессию пользователя."""
        return await self._session_repo.get_active_session_for_user(user_id)
