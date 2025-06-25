# backend/domain/achievement.py

from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum

# Определение типов достижений
class AchievementType(str, Enum):
    PERFECT_STREAK = "perfect_streak"
    WEEKLY_FIFTY = "weekly_fifty"
    # добавим дополнительные типы при необходимости

# Модель достижения
class AchievementModel(BaseModel):
    achievement_id: str
    user_id: str
    type: AchievementType
    earned_at: datetime
    session_id: str | None = None  # Опционально: ID сессии, в которой было получено достижение
    period_start_date: date | None = None  # Начало периода для еженедельных достижений (weekly_fifty)

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
