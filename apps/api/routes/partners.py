from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_service import (
    AnalyticalDataService,
)

router = APIRouter(
    prefix="/api/v1/partners",
    tags=["Partners"],
)

service = AnalyticalDataService()


@router.get("")
def get_partners(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        50,
        ge=1,
        le=500,
    ),
):

    try:

        df = service.get_partners()

        return service.paginate(
            df,
            page=page,
            page_size=page_size,
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )