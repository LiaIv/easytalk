from app.infrastructure.controllers.auth_router import router as auth_router
from app.infrastructure.controllers.game_router import router as game_router
from app.infrastructure.controllers.progress_router import router as progress_router

__all__ = ["auth_router", "game_router", "progress_router"]
