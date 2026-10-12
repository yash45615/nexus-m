from fastapi import FastAPI, HTTPException

from app.config import settings
from app.database.connection import test_database_connection


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "NEXUS-M — Autonomous Merchant & "
        "Network Intelligence Platform"
    ),
)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": (
            "NEXUS-M analytical intelligence "
            "platform is running."
        ),
    }


@app.get("/health")
def health_check():
    try:
        database = test_database_connection()

        return {
            "status": "healthy",
            "application": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "database": {
                "status": "connected",
                "name": database,
            },
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "unavailable",
                "error": str(exc),
            },
        )