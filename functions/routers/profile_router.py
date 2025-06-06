# functions/routers/profile_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from functions.shared.auth import get_current_user_id
from functions.domain.user import UserModel
from functions.repositories.user_repository import UserRepository

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
    try:
        user = await user_repository.get_user(uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        # В реальном приложении здесь стоит логировать ошибку 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.put("", response_model=UserModel)
async def update_profile(
    update_data: UpdateProfileRequest, 
    uid: str = Depends(get_current_user_id)
):
    """
    Обновить профиль текущего пользователя.
    Требуется токен авторизации.
    """
    try:
        current_user = await user_repository.get_user(uid)
        update_dict = update_data.model_dump(exclude_unset=True)

        if not current_user:
            if "email" not in update_dict:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=[{"loc": ["body", "email"], "msg": "Field required for new user profile", "type": "missing"}]
                )
            updated_user_data = {
                "uid": uid,
                "email": update_dict.get("email"),
                "display_name": update_dict.get("display_name"),
                "photo_url": update_dict.get("photo_url"),
            }
        else:
            updated_user_data = {
                "uid": uid,
                "email": update_dict.get("email", current_user.email),
                "display_name": update_dict.get("display_name", current_user.display_name),
                "photo_url": update_dict.get("photo_url", current_user.photo_url),
                "level": current_user.level,
                "created_at": current_user.created_at
            }
        
        updated_user = UserModel(**updated_user_data)
        
        await user_repository.create_or_update_user(updated_user)
        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
