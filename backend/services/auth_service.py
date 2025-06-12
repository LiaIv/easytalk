# backend/services/auth_service.py

from firebase_admin import auth
from fastapi import Depends
from domain.user import UserModel
from repositories.user_repository import UserRepository
from shared.dependencies import get_db
from google.cloud.firestore_v1.client import Client as FirestoreClient # Для type hinting
from datetime import datetime, timezone

class AuthService:
    def __init__(self, db: FirestoreClient = Depends(get_db)):
        self._user_repo = UserRepository(db=db)

    def register_user(self, email: str, password: str, display_name: str, level: str) -> UserModel:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        user = UserModel(
            uid=user_record.uid,
            email=email,
            display_name=display_name,
            avatar_url=None,
            level=level,
            created_at=datetime.now(timezone.utc)
        )
        self._user_repo.create_user(user)
        return user

    def verify_token(self, id_token: str) -> str:
        # Режим отладки для локального тестирования
        import os
        if os.environ.get('DEBUG') == 'True':
            print(f"DEBUG MODE: Пропускаем проверку токена: {id_token}")
            return id_token if id_token else 'test_user_id'
        
        # Реальная проверка токена через Firebase Auth
        try:
            decoded = auth.verify_id_token(id_token)
            return decoded["uid"]
        except Exception as e:
            print(f"Error verifying token: {e}")
            raise e
