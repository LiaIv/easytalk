from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from typing import List

from shared.auth import get_current_user_id

router = APIRouter(prefix="/achievements", tags=["achievements"])

# --------------------- Models ---------------------
class AchievementModel(BaseModel):
    id: str
    name: str
    description: str
    icon_url: HttpUrl | None = None
    unlocked: bool = False

# ------------------ Static catalogue ------------------
# Пока что каталог ачивок хранится в коде; можно будет вынести в Firestore или конфиг.
_CATALOGUE: list[dict] = [
    {
        "id": "weekly_fifty",
        "name": "50 за неделю",
        "description": "Набери 50 очков за последние 7 дней",
        "icon_url": None,
    }
]

# Dependency
from shared.dependencies import get_achievement_service, AchievementService

# --------------------- Routes ---------------------
@router.get("", response_model=list[AchievementModel])
async def list_achievements(
    uid: str = Depends(get_current_user_id),
    ach_service: AchievementService = Depends(get_achievement_service),
):
    """Return catalogue with unlocked flag from Firestore."""
    # Обновляем достижения (например, еженедельные)
    await ach_service.check_weekly_achievement(uid)
    # Получаем разблокированные достижения пользователя
    unlocked_models = await ach_service._achievement_repo.get_user_achievements(uid)
    unlocked_ids = {a.type.value for a in unlocked_models}
    # Маппим в ответ
    return [AchievementModel(**item, unlocked=item["id"] in unlocked_ids) for item in _CATALOGUE]
