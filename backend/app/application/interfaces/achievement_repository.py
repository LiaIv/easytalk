from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.achievement import Achievement


class AchievementRepository(ABC):
    """Interface for achievement repository operations."""
    
    @abstractmethod
    async def create(self, achievement: Achievement) -> Achievement:
        """Create a new achievement."""
        pass
    
    @abstractmethod
    async def get_by_id(self, achievement_id: UUID) -> Optional[Achievement]:
        """Get achievement by ID."""
        pass
    
    @abstractmethod
    async def update(self, achievement: Achievement) -> Achievement:
        """Update an existing achievement."""
        pass
    
    @abstractmethod
    async def delete(self, achievement_id: UUID) -> bool:
        """Delete an achievement by ID."""
        pass
    
    @abstractmethod
    async def list_achievements(self, skip: int = 0, limit: int = 100) -> List[Achievement]:
        """List all achievements with pagination."""
        pass
    
    @abstractmethod
    async def get_user_achievements(self, user_id: UUID) -> List[Achievement]:
        """Get all achievements earned by a specific user."""
        pass
    
    @abstractmethod
    async def check_and_award_achievements(self, user_id: UUID) -> List[Achievement]:
        """
        Check if user is eligible for any new achievements and award them.
        Returns list of newly awarded achievements.
        """
        pass
