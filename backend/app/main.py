from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.infrastructure.controllers import auth_router, game_router, progress_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for EasyTalk English Learning App",
    version=settings.APP_VERSION,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(game_router, prefix=settings.API_PREFIX)
app.include_router(progress_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_PREFIX,
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
