from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.game_session import GameSession


class GameSessionRepository(ABC):
    """Interface for game session repository operations."""
    
    @abstractmethod
    async def create(self, game_session: GameSession) -> GameSession:
        """Create a new game session."""
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[GameSession]:
        """Get game session by ID."""
        pass
    
    @abstractmethod
    async def update(self, game_session: GameSession) -> GameSession:
        """Update an existing game session."""
        pass
    
    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Delete a game session by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[GameSession]:
        """Get all game sessions for a specific user with pagination."""
        pass
    
    @abstractmethod
    async def get_user_stats(self, user_id: UUID) -> dict:
        """
        Get user gameplay statistics.
        Returns a dictionary with stats like total_games, avg_score, etc.
        """
        pass
