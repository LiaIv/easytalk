# backend/shared/dependencies.py

from fastapi import Depends
from google.cloud.firestore_v1.client import Client as FirestoreClient
from .firebase_client import get_firestore_client

# Импорты репозиториев
from repositories.user_repository import UserRepository
from repositories.achievement_repository import AchievementRepository
from repositories.session_repository import SessionRepository
from repositories.progress_repository import ProgressRepository

def get_db() -> FirestoreClient:
    """FastAPI dependency to get Firestore client."""
    return get_firestore_client()

def get_user_repository(db: FirestoreClient = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)

def get_achievement_repository(db: FirestoreClient = Depends(get_db)) -> AchievementRepository:
    return AchievementRepository(db=db)

def get_session_repository(db: FirestoreClient = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db=db)

def get_progress_repository(db: FirestoreClient = Depends(get_db)) -> ProgressRepository:
    return ProgressRepository(db=db)
