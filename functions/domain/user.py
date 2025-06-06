# functions/domain/user.py

from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime
from typing import Optional

class UserModel(BaseModel):
    uid: str
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[HttpUrl] = None
    level: Optional[str] = None  # например, "beginner" | "intermediate" | "advanced"
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
