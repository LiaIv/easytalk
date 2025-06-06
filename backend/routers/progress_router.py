# backend/routers/progress_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta

from backend.domain.progress import ProgressRecord
from backend.services.progress_service import ProgressService
from backend.shared.auth import get_current_user_id
from backend.shared.utils import to_iso_datetime, from_iso_datetime

# Инициализируем сервис прогресса
progress_service = ProgressService()

# Создаем роутер для прогресса
router = APIRouter(prefix="/progress", tags=["progress"])

# Модель для запроса сохранения прогресса
class SaveProgressRequest(BaseModel):
    score: int = Field(..., ge=0, description="Количество очков за день")
    correct_answers: int = Field(..., ge=0, description="Количество правильных ответов")
    total_answers: int = Field(..., ge=0, description="Общее количество ответов")
    time_spent: float = Field(..., ge=0.0, description="Время в секундах")
    date: Optional[str] = Field(None, description="Дата в формате ISO (YYYY-MM-DD)")


# Модель для ответа о сохранении прогресса
class SaveProgressResponse(BaseModel):
    message: str
    progress_id: str


# Модель ответа с данными о прогрессе
class ProgressItemResponse(BaseModel):
    date: str
    daily_score: int
    correct_answers: int
    total_answers: int
    success_rate: float
    time_spent: Optional[float] = None

# Модель для данных прогресса
class ProgressResponse(BaseModel):
    data: List[ProgressItemResponse]
    total_score: int
    average_score: float
    success_rate: Optional[float] = None


@router.post("", response_model=SaveProgressResponse)
async def save_progress(request: SaveProgressRequest, uid: str = Depends(get_current_user_id)):
    """
    Сохранить ежедневный прогресс пользователя.
    Требуется токен авторизации.
    """
    # Проверяем, что очки не отрицательные (уже валидация через Field)
    
    # Если дата не указана, используем текущую
    progress_date = None
    if request.date:
        try:
            progress_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid date format. Use YYYY-MM-DD."
            )
    
    try:
        # Используем сервис для сохранения прогресса
        progress_id = progress_service.record_progress(
            user_id=uid,
            score=request.score,
            correct_answers=request.correct_answers,
            total_answers=request.total_answers,
            time_spent=request.time_spent,
            record_date=progress_date
        )
        
        return SaveProgressResponse(
            message="Progress saved successfully",
            progress_id=progress_id
        )
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save progress: {str(e)}"
        )


@router.get("", response_model=ProgressResponse)
async def get_progress(
    days: int = Query(7, ge=1, le=30, description="Количество дней для выборки"),
    uid: str = Depends(get_current_user_id)
):
    """
    Получить прогресс пользователя за указанное количество дней.
    Требуется токен авторизации.
    """
    try:
        # Используем сервис для получения прогресса
        progress_data = progress_service.get_progress(uid, days)
        
        # Если данных нет, возвращаем пустой ответ
        if not progress_data["data"]:
            return ProgressResponse(
                data=[],
                total_score=0,
                average_score=0.0
            )
        
        # Преобразуем данные в ожидаемый формат ответа
        response_data = []
        for item in progress_data["data"]:
            response_data.append(ProgressItemResponse(
                date=item["date"],
                daily_score=item["score"],  # Переименовываем score в daily_score для совместимости
                success_rate=item["success_rate"],
                correct_answers=item["correct_answers"],
                total_answers=item["total_answers"],
                time_spent=item["time_spent"]
            ))
        
        return ProgressResponse(
            data=response_data,
            total_score=progress_data["total_score"],
            average_score=progress_data["average_score"],
            success_rate=progress_data["success_rate"]
        )
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress data: {str(e)}"
        )


# Модель для ответа недельной сводки
class WeeklySummaryResponse(BaseModel):
    total_weekly_score: int

@router.get("/weekly-summary", response_model=WeeklySummaryResponse)
async def get_weekly_summary(uid: str = Depends(get_current_user_id)):
    """
    Получить общее количество очков пользователя за последнюю неделю.
    Требуется токен авторизации.
    """
    try:
        total_score = progress_service.get_weekly_summary(user_id=uid)
        return WeeklySummaryResponse(total_weekly_score=total_score)
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get weekly summary: {str(e)}"
        )
