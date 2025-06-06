# functions/routers/progress_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta

from domain.progress import ProgressRecord
from repositories.progress_repository import ProgressRepository
from shared.auth import get_current_user_id
from shared.utils import to_iso_datetime, from_iso_datetime

# Инициализируем репозиторий прогресса
progress_repository = ProgressRepository()

# Создаем роутер для прогресса
router = APIRouter(prefix="/progress", tags=["progress"])

# Модель для запроса сохранения прогресса
class SaveProgressRequest(BaseModel):
    daily_score: int = Field(..., ge=0, description="Количество очков за день")
    date: Optional[str] = Field(None, description="Дата в формате ISO (YYYY-MM-DD)")


# Модель для ответа о сохранении прогресса
class SaveProgressResponse(BaseModel):
    message: str
    progress_id: str


# Модель для данных прогресса
class ProgressResponse(BaseModel):
    data: List[Dict[str, Any]]
    total_score: int
    average_score: float


@router.post("", response_model=SaveProgressResponse)
async def save_progress(request: SaveProgressRequest, uid: str = Depends(get_current_user_id)):
    """
    Сохранить ежедневный прогресс пользователя.
    Требуется токен авторизации.
    """
    # Проверяем, что очки не отрицательные (уже валидация через Field)
    
    # Если дата не указана, используем текущую
    progress_date = date.today()
    if request.date:
        try:
            progress_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid date format. Use YYYY-MM-DD."
            )
    
    try:
        # Создаем запись о прогрессе
        progress_record = ProgressRecord(
            user_id=uid,
            date=progress_date.isoformat(),
            daily_score=request.daily_score
        )
        
        # Сохраняем в репозиторий
        progress_id = await progress_repository.save_progress(progress_record)
        
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
        # Рассчитываем дату начала периода
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)  # -1 т.к. включаем текущий день
        
        # Получаем записи из репозитория
        progress_records = await progress_repository.get_progress(
            uid, 
            start_date.isoformat(), 
            end_date.isoformat()
        )
        
        # Если записей нет, возвращаем пустой список
        if not progress_records:
            return ProgressResponse(
                data=[],
                total_score=0,
                average_score=0.0
            )
        
        # Конвертируем записи в формат для ответа и рассчитываем статистику
        data = []
        total_score = 0
        
        for record in progress_records:
            data.append({
                "date": record.date,
                "daily_score": record.daily_score
            })
            total_score += record.daily_score
        
        average_score = total_score / len(progress_records) if progress_records else 0
        
        return ProgressResponse(
            data=data,
            total_score=total_score,
            average_score=round(average_score, 1)
        )
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress data: {str(e)}"
        )
