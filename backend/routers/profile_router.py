from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from shared.auth import get_current_user_id
from domain.user import UserModel
from repositories.user_repository import UserRepository
from shared.dependencies import get_user_repository

# Создаем роутер для профиля
router = APIRouter(prefix="/profile", tags=["profile"])

# Модель для обновления профиля
class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = None
    level: Optional[str] = None  # beginner, preIntermediate, intermediate


@router.get("", response_model=UserModel)
async def get_profile(
    uid: str = Depends(get_current_user_id),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """
    Получить профиль текущего пользователя.
    Требуется токен авторизации.
    """
    try:
        # user_repository теперь внедряется через Depends
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
    uid: str = Depends(get_current_user_id),
    user_repository: UserRepository = Depends(get_user_repository)
):
    """
    Обновить профиль текущего пользователя.
    Требуется токен авторизации.
    """
    try:
        # user_repository теперь внедряется через Depends
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
                "level": update_dict.get("level"),
            }
        else:
            updated_user_data = {
                "uid": uid,
                "email": update_dict.get("email", current_user.email),
                "display_name": update_dict.get("display_name", current_user.display_name),
                "photo_url": update_dict.get("photo_url", current_user.photo_url),
                "level": update_dict.get("level", current_user.level),
                "created_at": current_user.created_at
            }
        
        updated_user = UserModel(**updated_user_data)
        
        # user_repository теперь внедряется через Depends
        await user_repository.create_or_update_user(updated_user)
        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
