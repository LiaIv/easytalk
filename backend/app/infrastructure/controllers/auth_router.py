from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.application.use_cases.auth_use_case import AuthUseCase
from app.domain.entities.user import User
from app.infrastructure.controllers.dependencies import get_current_active_user
from app.infrastructure.persistence.mongodb.user_repository import MongoDBUserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize repositories
user_repository = MongoDBUserRepository()

# Initialize use cases
auth_use_case = AuthUseCase(user_repository)

# Pydantic models for request/response validation
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str = None
    last_name: str = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: str = None
    last_name: str = None
    level: int
    experience_points: int

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        user = await auth_use_case.register(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "level": user.level,
            "experience_points": user.experience_points
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token."""
    try:
        token_data = await auth_use_case.login(
            email=form_data.username,  # OAuth2 form uses 'username' field for email
            password=form_data.password
        )
        return token_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "level": current_user.level,
        "experience_points": current_user.experience_points
    }
