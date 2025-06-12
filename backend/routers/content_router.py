from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel

from shared.auth import get_current_user_id
from shared.dependencies import get_db # Импортируем get_db
from google.cloud.firestore_v1.client import Client # Импортируем Client для тайп-хинта

# Создаем роутер для контента
router = APIRouter(prefix="/content", tags=["content"])


# Модель для контента животного
class AnimalContent(BaseModel):
    id: str
    name: str
    english_name: str
    image_url: Optional[str] = None
    sound_url: Optional[str] = None
    difficulty: int
    description: Optional[str] = None


@router.get("/animals", response_model=List[AnimalContent])
async def get_animals(uid: str = Depends(get_current_user_id), db: Client = Depends(get_db),
    difficulty: Optional[int] = Query(
        None, ge=1, le=5, description="Фильтр по сложности (1-5)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
):
    """
    Получить список животных для игры "Угадай животное".
    Можно фильтровать по уровню сложности.
    Требуется токен авторизации.
    """
    try:
        query = db.collection("content").document("animals").collection("items")

        if difficulty is not None:
            query = query.where("difficulty", "==", difficulty)

        query_with_limit = query.limit(limit)
        docs = query_with_limit.stream()

        result = []
        for doc in docs:  # Синхронный итератор Firestore
            data = doc.to_dict()
            data["id"] = doc.id
            result.append(AnimalContent(**data))

        return result
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve animals content: {str(e)}",
        )


@router.get("/animals/{animal_id}", response_model=AnimalContent)
async def get_animal_by_id(db: Client = Depends(get_db),
    animal_id: str = Path(..., description="Идентификатор животного"),
    uid: str = Depends(get_current_user_id),
):
    """
    Получить данные о конкретном животном по его ID.
    Требуется токен авторизации.
    """
    try:
        doc_ref = (
            db.collection("content")
            .document("animals")
            .collection("items")
            .document(animal_id)
        )
        doc = await doc_ref.get()

        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Animal with ID {animal_id} not found",
            )

        data = doc.to_dict()
        data["id"] = doc.id  # Добавляем идентификатор документа

        return AnimalContent(**data)
    except HTTPException:
        raise  # Перебрасываем уже созданное исключение
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve animal: {str(e)}",
        )


# Модель для контента предложений
class SentenceContent(BaseModel):
    id: str
    sentence: str
    words: List[str]
    difficulty: int
    translation: Optional[str] = None


@router.get("/sentences", response_model=List[SentenceContent])
async def get_sentences(db: Client = Depends(get_db),
    difficulty: Optional[int] = Query(
        None, ge=1, le=5, description="Фильтр по сложности (1-5)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    uid: str = Depends(get_current_user_id),
):
    """
    Получить список предложений для игры "Составь предложение".
    Можно фильтровать по уровню сложности.
    Требуется токен авторизации.
    """
    try:
        query = db.collection("content").document("sentences").collection("items")

        # Применяем фильтр по сложности, если указан
        if difficulty is not None:
            query = query.where("difficulty", "==", difficulty)

        # Получаем данные с лимитом
        docs = query.limit(limit).stream()

        # Преобразуем в список моделей
        result = []
        async for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id  # Добавляем идентификатор документа
            result.append(SentenceContent(**data))

        return result
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sentences content: {str(e)}",
        )
