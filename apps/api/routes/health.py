from fastapi import APIRouter

from app.config import settings

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health():

    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "service": "analytical-api",
    }