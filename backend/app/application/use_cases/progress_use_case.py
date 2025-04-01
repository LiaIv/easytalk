from typing import Dict, List
from uuid import UUID

from app.application.interfaces.achievement_repository import AchievementRepository
from app.application.interfaces.game_session_repository import GameSessionRepository
from app.application.interfaces.user_repository import UserRepository
from app.domain.entities.achievement import Achievement
from app.domain.entities.user import User


class ProgressUseCase:
    """Use case for user progress and achievement-related operations."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        game_session_repository: GameSessionRepository,
        achievement_repository: AchievementRepository
    ):
        self.user_repository = user_repository
        self.game_session_repository = game_session_repository
        self.achievement_repository = achievement_repository
    
    async def get_user_stats(self, user_id: UUID) -> Dict:
        """Get comprehensive statistics for a user."""
        # Validate user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get game statistics
        game_stats = await self.game_session_repository.get_user_stats(user_id)
        
        # Combine with user profile stats
        stats = {
            "user_id": str(user.id),
            "username": user.username,
            "level": user.level,
            "experience_points": user.experience_points,
            "next_level_exp": (user.level * 100),  # Simple formula, adjust as needed
            "achievements_count": len(user.achievement_ids),
            **game_stats  # Include game stats (total_games, avg_score, etc.)
        }
        
        return stats
    
    async def get_user_achievements(self, user_id: UUID) -> List[Achievement]:
        """Get all achievements earned by a user."""
        # Validate user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get achievements
        achievements = await self.achievement_repository.get_user_achievements(user_id)
        return achievements
    
    async def check_and_award_achievements(self, user_id: UUID) -> List[Achievement]:
        """
        Check if user is eligible for any new achievements and award them.
        Returns a list of newly awarded achievements.
        """
        # Validate user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check and award achievements
        new_achievements = await self.achievement_repository.check_and_award_achievements(user_id)
        
        # Update user with new achievements if any were awarded
        if new_achievements:
            for achievement in new_achievements:
                user.add_achievement(achievement.id)
                # Award experience points for each achievement
                user.add_experience(achievement.experience_reward)
            
            # Save updated user
            await self.user_repository.update(user)
        
        return new_achievements
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get leaderboard of top users by experience points."""
        # Get all users
        users = await self.user_repository.list_users(limit=limit)
        
        # Sort by experience points (descending)
        users.sort(key=lambda u: u.experience_points, reverse=True)
        
        # Format leaderboard data
        leaderboard = [
            {
                "user_id": str(user.id),
                "username": user.username,
                "level": user.level,
                "experience_points": user.experience_points,
                "rank": i + 1
            }
            for i, user in enumerate(users[:limit])
        ]
        
        return leaderboard
