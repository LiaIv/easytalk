import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.application.interfaces.user_repository import UserRepository
from app.config.settings import settings
from app.domain.entities.user import User


class AuthUseCase:
    """Use case for authentication-related operations."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register(self, username: str, email: str, password: str, 
                       first_name: Optional[str] = None, 
                       last_name: Optional[str] = None) -> User:
        """Register a new user."""
        # Check if user with this email already exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Check if username is already taken
        existing_username = await self.user_repository.get_by_username(username)
        if existing_username:
            raise ValueError("Username is already taken")
        
        # Hash the password
        hashed_password = self._hash_password(password)
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Save user to repository
        created_user = await self.user_repository.create(new_user)
        return created_user
    
    async def login(self, email: str, password: str) -> dict:
        """Login a user and return access token."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not self._verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")
        
        # Generate JWT token
        access_token = self._create_access_token(
            data={"sub": str(user.id), "email": user.email, "username": user.username}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "username": user.username
        }
    
    async def get_current_user(self, token: str) -> User:
        """Decode JWT token and return the current user."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise ValueError("Invalid authentication credentials")
        except jwt.PyJWTError:
            raise ValueError("Invalid authentication credentials")
        
        user = await self.user_repository.get_by_id(UUID(user_id))
        if user is None:
            raise ValueError("User not found")
            
        return user
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        return hashed_password.decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hashed password."""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def _create_access_token(self, data: dict) -> str:
        """Create a new JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
