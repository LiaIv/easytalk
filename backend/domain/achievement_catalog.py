"""Domain model for catalogued achievements.
These describe static achievement definitions (name, description, icon, etc.)
"""
from pydantic import BaseModel, HttpUrl

class AchievementCatalogItem(BaseModel):
    id: str
    name: str
    description: str
    icon_url: HttpUrl | None = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }
