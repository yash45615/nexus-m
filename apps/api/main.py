from fastapi import FastAPI

from app.config import settings

from apps.api.routes import (
    health,
    kpis,
    merchants,
    partners,
    analytics,
)


app = FastAPI(
    title="NEXUS-M Analytical API",
    version=settings.app_version,
    description=(
        "REST API for the NEXUS-M "
        "Autonomous Merchant & Network "
        "Intelligence Platform."
    ),
)


app.include_router(
    health.router
)

app.include_router(
    kpis.router
)

app.include_router(
    merchants.router
)

app.include_router(
    partners.router
)

app.include_router(
    analytics.router
)


@app.get("/")
def root():

    return {
        "name": "NEXUS-M",
        "service": "Analytical API",
        "version": settings.app_version,
        "message": (
            "NEXUS-M analytical "
            "API is running."
        ),
    }