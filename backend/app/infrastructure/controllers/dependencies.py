from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from app.application.use_cases.auth_use_case import AuthUseCase
from app.domain.entities.user import User
from app.infrastructure.persistence.mongodb.user_repository import MongoDBUserRepository

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Initialize repositories
user_repository = MongoDBUserRepository()

# Initialize use cases
auth_use_case = AuthUseCase(user_repository)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the JWT token.
    This dependency will be used to protect API endpoints.
    """
    try:
        user = await auth_use_case.get_current_user(token)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Check if the current user is active.
    This dependency can be used for endpoints that require an active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
