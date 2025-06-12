from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import List

from domain.session import RoundDetail, SessionModel
from services.session_service import SessionService
from shared.auth import get_current_user_id
from shared.dependencies import get_session_service

# Создаем роутер для сессий
router = APIRouter(prefix="/session", tags=["session"])

# Модель для запроса начала сессии
class StartSessionRequest(BaseModel):
    game_type: str  # Тип игры: "guess_animal" или "build_sentence"

# Модель для ответа о начале сессии
class StartSessionResponse(BaseModel):
    session_id: str

# Модель для данных завершения сессии
class FinishSessionRequest(BaseModel):
    details: List[RoundDetail]
    score: int

# Модель для ответа о завершении сессии
class FinishSessionResponse(BaseModel):
    message: str

@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    request: StartSessionRequest,
    uid: str = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
):
    """
    Начать новую игровую сессию заданного типа.
    Требуется токен авторизации.
    """
    # Проверяем тип игры
    if request.game_type not in ("guess_animal", "build_sentence"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid gameType. Must be 'guess_animal' or 'build_sentence'."
        )
    
    try:
        # Создаем сессию через сервис
        session_id = await session_service.start_session(uid, request.game_type)
        return StartSessionResponse(session_id=session_id)
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.patch("/finish", response_model=FinishSessionResponse)
async def finish_session(
    request: FinishSessionRequest,
    session_id: str = Query(..., description="ID сессии для завершения"),
    uid: str = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
):
    """
    Завершить игровую сессию с результатами и получить подтверждение.
    Требуется токен авторизации.
    """
    try:
        # Завершаем сессию через сервис
        await session_service.finish_session(uid, session_id, request.details, request.score)
        return FinishSessionResponse(message="Session finished successfully")
    except ValueError as e:
        # Если сессия не найдена
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to finish session: {str(e)}"
        )


@router.get("/active", response_model=SessionModel)
async def get_active_session(
    uid: str = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
):
    """
    Получить данные об активной сессии пользователя, если такая существует.
    Требуется токен авторизации.
    """
    try:
        # Получаем активную сессию через сервис
        session = await session_service.get_active_session(uid)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active session found"
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active session: {str(e)}"
        )
