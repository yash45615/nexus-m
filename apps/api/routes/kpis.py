from fastapi import APIRouter, HTTPException

from apps.api.services.data_service import (
    AnalyticalDataService,
)

router = APIRouter(
    prefix="/api/v1/kpis",
    tags=["KPIs"],
)

service = AnalyticalDataService()


@router.get("")
def get_kpis():

    try:

        return service.get_kpis()

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/{metric_name}")
def get_kpi(
    metric_name: str,
):

    try:

        data = service.get_kpis()

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    if metric_name not in data:

        raise HTTPException(
            status_code=404,
            detail=(
                f"KPI '{metric_name}' "
                "was not found."
            ),
        )

    return {
        "metric": metric_name,
        "value": data[metric_name],
    }