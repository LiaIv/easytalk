# functions/domain/achievement.py

from pydantic import BaseModel
from datetime import datetime, date

class AchievementModel(BaseModel):
    achievement_id: str
    user_id: str
    type: str  # "perfect_streak" | "weekly_fifty"
    earned_at: datetime
    period_start_date: date | None = None

    class Config:
        orm_mode = True
