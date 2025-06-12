from fastapi import Depends
from google.cloud.firestore_v1.async_client import AsyncClient as FirestoreClient
from google.auth.credentials import AnonymousCredentials

# Импорты репозиториев
from repositories.user_repository import UserRepository
from repositories.achievement_repository import AchievementRepository
from repositories.session_repository import SessionRepository
from repositories.progress_repository import ProgressRepository

# Обертка, возвращающая AsyncClient, используя эмулятор, если он настроен
def _create_async_client() -> FirestoreClient:
    import os
    project_id = os.getenv("GCLOUD_PROJECT", "easytalk-emulator")
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        return FirestoreClient(project=project_id, credentials=AnonymousCredentials())
    return FirestoreClient(project=project_id)

def get_db() -> FirestoreClient:
    """FastAPI dependency that returns Async Firestore client."""
    return _create_async_client()

def get_user_repository(db: FirestoreClient = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)

def get_achievement_repository(db: FirestoreClient = Depends(get_db)) -> AchievementRepository:
    return AchievementRepository(db=db)

def get_session_repository(db: FirestoreClient = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db=db)

def get_progress_repository(db: FirestoreClient = Depends(get_db)) -> ProgressRepository:
    return ProgressRepository(db=db)

# ---------- Service-level dependencies ----------
from services.progress_service import ProgressService
from services.session_service import SessionService

def get_progress_service(
    progress_repo: ProgressRepository = Depends(get_progress_repository),
) -> ProgressService:
    """FastAPI dependency returning ProgressService instance."""
    return ProgressService(progress_repo)

def get_session_service(
    session_repo: SessionRepository = Depends(get_session_repository),
    achievement_repo: AchievementRepository = Depends(get_achievement_repository),
) -> SessionService:
    """FastAPI dependency returning SessionService instance."""
    return SessionService(session_repo=session_repo, achievement_repo=achievement_repo)
