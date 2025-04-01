from typing import List, Optional
from uuid import UUID

from app.application.interfaces.game_session_repository import GameSessionRepository
from app.application.interfaces.user_repository import UserRepository
from app.domain.entities.game_session import GameSession
from app.domain.value_objects.difficulty_level import DifficultyLevel


class GameUseCase:
    """Use case for game-related operations."""
    
    def __init__(
        self, 
        game_session_repository: GameSessionRepository,
        user_repository: UserRepository
    ):
        self.game_session_repository = game_session_repository
        self.user_repository = user_repository
    
    async def start_game_session(
        self, 
        user_id: UUID, 
        game_type: str, 
        difficulty_level: str,
        total_questions: int
    ) -> GameSession:
        """Start a new game session for a user."""
        # Validate difficulty level
        try:
            DifficultyLevel(difficulty_level.lower())
        except ValueError:
            raise ValueError(f"Invalid difficulty level: {difficulty_level}")
        
        # Validate user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Create new game session
        game_session = GameSession(
            user_id=user_id,
            game_type=game_type,
            difficulty_level=difficulty_level.lower(),
            total_questions=total_questions,
            max_score=total_questions * 10  # Assuming 10 points per correct answer
        )
        
        # Save game session
        created_session = await self.game_session_repository.create(game_session)
        return created_session
    
    async def submit_game_results(
        self, 
        session_id: UUID, 
        score: int, 
        correct_answers: int
    ) -> GameSession:
        """Submit results for a completed game session."""
        # Get game session
        game_session = await self.game_session_repository.get_by_id(session_id)
        if not game_session:
            raise ValueError(f"Game session with ID {session_id} not found")
        
        # Complete the game session
        experience_earned = game_session.complete(
            score=score,
            correct_answers=correct_answers,
            total_questions=game_session.total_questions
        )
        
        # Update user experience points
        user = await self.user_repository.get_by_id(game_session.user_id)
        if not user:
            raise ValueError(f"User with ID {game_session.user_id} not found")
        
        # Add experience points and check if level up occurred
        level_up = user.add_experience(experience_earned)
        
        # Update user
        await self.user_repository.update(user)
        
        # Update game session
        updated_session = await self.game_session_repository.update(game_session)
        
        # Return updated session with level up info
        return updated_session, level_up
    
    async def get_user_game_history(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[GameSession]:
        """Get game history for a specific user."""
        # Validate user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get game sessions
        sessions = await self.game_session_repository.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        return sessions
    
    async def get_game_session_details(self, session_id: UUID) -> GameSession:
        """Get details for a specific game session."""
        game_session = await self.game_session_repository.get_by_id(session_id)
        if not game_session:
            raise ValueError(f"Game session with ID {session_id} not found")
        
        return game_session
