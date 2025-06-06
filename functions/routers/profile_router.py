# functions/routers/profile_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from shared.auth import get_current_user_id
from domain.user import UserModel
from repositories.user_repository import UserRepository

# Инициализируем репозиторий пользователей
user_repository = UserRepository()

# Создаем роутер для профиля
router = APIRouter(prefix="/profile", tags=["profile"])

# Модель для обновления профиля
class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = None


@router.get("", response_model=UserModel)
async def get_profile(uid: str = Depends(get_current_user_id)):
    """
    Получить профиль текущего пользователя.
    Требуется токен авторизации.
    """
    # Получаем профиль из репозитория
    user = await user_repository.get_user(uid)
    
    # Если пользователь не найден, создаем базовую запись
    if not user:
        user = UserModel(uid=uid)
        
    return user


@router.put("", response_model=UserModel)
async def update_profile(
    update_data: UpdateProfileRequest, 
    uid: str = Depends(get_current_user_id)
):
    """
    Обновить профиль текущего пользователя.
    Требуется токен авторизации.
    """
    # Получаем текущий профиль
    current_user = await user_repository.get_user(uid)
    
    # Если пользователь не найден, создаем базовую запись
    if not current_user:
        current_user = UserModel(uid=uid)
    
    # Обновляем только предоставленные поля
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # Создаем обновленную модель
    updated_user = UserModel(
        uid=uid,
        email=update_dict.get("email", current_user.email),
        display_name=update_dict.get("display_name", current_user.display_name),
        photo_url=update_dict.get("photo_url", current_user.photo_url)
    )
    
    # Сохраняем в репозиторий
    await user_repository.create_or_update_user(updated_user)
    
    return updated_user
