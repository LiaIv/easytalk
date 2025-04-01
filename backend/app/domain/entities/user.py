from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class User:
    """User entity representing a registered user in the system."""
    
    username: str
    email: str
    hashed_password: str
    id: UUID = field(default_factory=uuid4)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now(datetime.timezone.utc))
    updated_at: datetime = field(default_factory=datetime.now(datetime.timezone.utc))
    avatar_url: Optional[str] = None
    is_active: bool = True
    experience_points: int = 0
    level: int = 1
    
    # Relationships
    achievement_ids: List[UUID] = field(default_factory=list)
    
    def update_profile(self, first_name: Optional[str] = None, 
                       last_name: Optional[str] = None, 
                       avatar_url: Optional[str] = None):
        """Update user profile information."""
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if avatar_url is not None:
            self.avatar_url = avatar_url
        self.updated_at = datetime.utcnow()
    
    def add_experience(self, points: int) -> bool:
        """
        Add experience points to the user and check if level up occurred.
        Returns True if level up happened, False otherwise.
        """
        self.experience_points += points
        
        # Simple level up logic - adjust as needed for your game mechanics
        new_level = 1 + self.experience_points // 100
        level_up = new_level > self.level
        
        if level_up:
            self.level = new_level
            
        self.updated_at = datetime.utcnow()
        return level_up
    
    def add_achievement(self, achievement_id: UUID):
        """Add achievement to user's list if not already added."""
        if achievement_id not in self.achievement_ids:
            self.achievement_ids.append(achievement_id)
            self.updated_at = datetime.utcnow()
