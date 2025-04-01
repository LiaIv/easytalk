from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List

from app.application.use_cases.progress_use_case import ProgressUseCase
from app.domain.entities.user import User
from app.infrastructure.controllers.dependencies import get_current_active_user
from app.infrastructure.persistence.mongodb.achievement_repository import MongoDBachievementRepository
from app.infrastructure.persistence.mongodb.game_session_repository import MongoDBGameSessionRepository
from app.infrastructure.persistence.mongodb.user_repository import MongoDBUserRepository

router = APIRouter(prefix="/progress", tags=["Progress"])

# Initialize repositories
user_repository = MongoDBUserRepository()
game_session_repository = MongoDBGameSessionRepository()
achievement_repository = MongoDBachievementRepository(
    user_repository=user_repository,
    game_session_repository=game_session_repository
)

# Initialize use cases
progress_use_case = ProgressUseCase(
    user_repository=user_repository,
    game_session_repository=game_session_repository,
    achievement_repository=achievement_repository
)

# Pydantic models for request/response validation
class AchievementResponse(BaseModel):
    id: str
    name: str
    description: str
    icon_url: str
    experience_reward: int

class UserStatsResponse(BaseModel):
    user_id: str
    username: str
    level: int
    experience_points: int
    next_level_exp: int
    achievements_count: int
    total_games: int = 0
    avg_score: float = 0
    highest_score: int = 0
    accuracy_percentage: float = 0
    total_xp_earned: int = 0

class LeaderboardEntryResponse(BaseModel):
    user_id: str
    username: str
    level: int
    experience_points: int
    rank: int

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(current_user: User = Depends(get_current_active_user)):
    """Get comprehensive statistics for the current user."""
    try:
        stats = await progress_use_case.get_user_stats(user_id=current_user.id)
        return stats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/achievements", response_model=List[AchievementResponse])
async def get_user_achievements(current_user: User = Depends(get_current_active_user)):
    """Get all achievements earned by the current user."""
    try:
        achievements = await progress_use_case.get_user_achievements(user_id=current_user.id)
        return [
            {
                "id": str(achievement.id),
                "name": achievement.name,
                "description": achievement.description,
                "icon_url": achievement.icon_url,
                "experience_reward": achievement.experience_reward
            }
            for achievement in achievements
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/check-achievements", response_model=List[AchievementResponse])
async def check_and_award_achievements(current_user: User = Depends(get_current_active_user)):
    """Check if user is eligible for any new achievements and award them."""
    try:
        new_achievements = await progress_use_case.check_and_award_achievements(user_id=current_user.id)
        return [
            {
                "id": str(achievement.id),
                "name": achievement.name,
                "description": achievement.description,
                "icon_url": achievement.icon_url,
                "experience_reward": achievement.experience_reward
            }
            for achievement in new_achievements
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/leaderboard", response_model=List[LeaderboardEntryResponse])
async def get_leaderboard(limit: int = 10):
    """Get leaderboard of top users by experience points."""
    try:
        leaderboard = await progress_use_case.get_leaderboard(limit=limit)
        return leaderboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
