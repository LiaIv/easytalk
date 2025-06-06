# functions/domain/session.py

from pydantic import BaseModel, conint
from typing import List
from datetime import datetime

class RoundDetail(BaseModel):
    round_index: conint(ge=1, le=10)
    is_correct: bool
    attempts: conint(ge=1)

class SessionModel(BaseModel):
    session_id: str
    user_id: str
    game_type: str  # "guess_animal" | "build_sentence"
    started_at: datetime
    ended_at: datetime | None = None
    score: conint(ge=0) | None = None
    details: List[RoundDetail] | None = None

    class Config:
        orm_mode = True
