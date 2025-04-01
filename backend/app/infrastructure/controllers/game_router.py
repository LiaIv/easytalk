from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4
from typing import List, Optional

from app.application.use_cases.game_use_case import GameUseCase
from app.domain.entities.user import User
from app.infrastructure.controllers.dependencies import get_current_active_user
from app.infrastructure.persistence.mongodb.game_session_repository import MongoDBGameSessionRepository
from app.infrastructure.persistence.mongodb.user_repository import MongoDBUserRepository

router = APIRouter(prefix="/games", tags=["Games"])

# Initialize repositories
user_repository = MongoDBUserRepository()
game_session_repository = MongoDBGameSessionRepository()

# Initialize use cases
game_use_case = GameUseCase(
    game_session_repository=game_session_repository,
    user_repository=user_repository
)

# Pydantic models for request/response validation
class GameSessionCreate(BaseModel):
    game_type: str
    difficulty_level: str
    total_questions: int

class GameSessionResults(BaseModel):
    score: int
    correct_answers: int

class GameSessionResponse(BaseModel):
    id: str
    user_id: str
    game_type: str
    difficulty_level: str
    started_at: str
    completed_at: Optional[str] = None
    score: int
    max_score: int
    correct_answers: int
    total_questions: int
    experience_earned: int
    duration_seconds: Optional[int] = None
    accuracy_percentage: float

class GameSessionResultsResponse(BaseModel):
    session: GameSessionResponse
    level_up: bool = False

@router.post("/start", response_model=GameSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_game_session(
    game_data: GameSessionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Start a new game session."""
    try:
        game_session = await game_use_case.start_game_session(
            user_id=current_user.id,
            game_type=game_data.game_type,
            difficulty_level=game_data.difficulty_level,
            total_questions=game_data.total_questions
        )
        
        return {
            "id": str(game_session.id),
            "user_id": str(game_session.user_id),
            "game_type": game_session.game_type,
            "difficulty_level": game_session.difficulty_level,
            "started_at": game_session.started_at.isoformat(),
            "completed_at": game_session.completed_at.isoformat() if game_session.completed_at else None,
            "score": game_session.score,
            "max_score": game_session.max_score,
            "correct_answers": game_session.correct_answers,
            "total_questions": game_session.total_questions,
            "experience_earned": game_session.experience_earned,
            "duration_seconds": game_session.duration_seconds,
            "accuracy_percentage": game_session.accuracy_percentage
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{session_id}/submit", response_model=GameSessionResultsResponse)
async def submit_game_results(
    session_id: UUID4,
    results: GameSessionResults,
    current_user: User = Depends(get_current_active_user)
):
    """Submit results for a completed game session."""
    try:
        game_session, level_up = await game_use_case.submit_game_results(
            session_id=session_id,
            score=results.score,
            correct_answers=results.correct_answers
        )
        
        # Verify that the user owns this game session
        if game_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this game session"
            )
        
        return {
            "session": {
                "id": str(game_session.id),
                "user_id": str(game_session.user_id),
                "game_type": game_session.game_type,
                "difficulty_level": game_session.difficulty_level,
                "started_at": game_session.started_at.isoformat(),
                "completed_at": game_session.completed_at.isoformat() if game_session.completed_at else None,
                "score": game_session.score,
                "max_score": game_session.max_score,
                "correct_answers": game_session.correct_answers,
                "total_questions": game_session.total_questions,
                "experience_earned": game_session.experience_earned,
                "duration_seconds": game_session.duration_seconds,
                "accuracy_percentage": game_session.accuracy_percentage
            },
            "level_up": level_up
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/history", response_model=List[GameSessionResponse])
async def get_game_history(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get game history for the current user."""
    try:
        sessions = await game_use_case.get_user_game_history(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        return [
            {
                "id": str(session.id),
                "user_id": str(session.user_id),
                "game_type": session.game_type,
                "difficulty_level": session.difficulty_level,
                "started_at": session.started_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "score": session.score,
                "max_score": session.max_score,
                "correct_answers": session.correct_answers,
                "total_questions": session.total_questions,
                "experience_earned": session.experience_earned,
                "duration_seconds": session.duration_seconds,
                "accuracy_percentage": session.accuracy_percentage
            }
            for session in sessions
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{session_id}", response_model=GameSessionResponse)
async def get_game_session(
    session_id: UUID4,
    current_user: User = Depends(get_current_active_user)
):
    """Get details for a specific game session."""
    try:
        session = await game_use_case.get_game_session_details(session_id=session_id)
        
        # Verify that the user owns this game session
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this game session"
            )
        
        return {
            "id": str(session.id),
            "user_id": str(session.user_id),
            "game_type": session.game_type,
            "difficulty_level": session.difficulty_level,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "score": session.score,
            "max_score": session.max_score,
            "correct_answers": session.correct_answers,
            "total_questions": session.total_questions,
            "experience_earned": session.experience_earned,
            "duration_seconds": session.duration_seconds,
            "accuracy_percentage": session.accuracy_percentage
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
