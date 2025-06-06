# functions/domain/progress.py

from pydantic import BaseModel, conint
from datetime import date

class ProgressRecord(BaseModel):
    user_id: str
    date: date
    daily_score: conint(ge=0)

    class Config:
        orm_mode = True
