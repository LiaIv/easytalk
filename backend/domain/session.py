# backend/domain/session.py

from pydantic import BaseModel, conint, Field, field_validator
from typing import List, Literal
from datetime import datetime
from enum import Enum

# Определение статуса сессии
class SessionStatus(str, Enum):
    ACTIVE = "active"
    FINISHED = "finished"
    ABANDONED = "abandoned"

# Детали раунда в игровой сессии
class RoundDetail(BaseModel):
    question_id: str
    answer: str
    is_correct: bool
    time_spent: float = Field(ge=0)  # Время в секундах, должно быть >= 0

# Модель игровой сессии
class SessionModel(BaseModel):
    session_id: str
    user_id: str
    game_type: Literal["guess_animal", "build_sentence"]
    start_time: datetime
    end_time: datetime | None = None
    status: SessionStatus
    score: conint(ge=0) | None = None
    details: List[RoundDetail] = Field(default_factory=list)  # Список деталей раунда
    
    # Валидатор для проверки количества деталей (максимум 10)
    @field_validator("details")
    def validate_details_length(cls, v):
        if len(v) > 10:
            raise ValueError("максимальное количество деталей в сессии - 10")
        return v

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
