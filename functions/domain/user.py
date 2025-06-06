# functions/domain/user.py

from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserModel(BaseModel):
    uid: str
    email: EmailStr
    display_name: str
    avatar_url: str | None = None
    level: str  # например, "beginner" | "intermediate" | "advanced"
    created_at: datetime

    class Config:
        orm_mode = True
