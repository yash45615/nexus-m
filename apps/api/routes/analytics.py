from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_service import (
    AnalyticalDataService,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Analytics"],
)

service = AnalyticalDataService()


@router.get("/regions")
def get_regions(
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

        df = service.get_regions()

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


@router.get("/anomalies")
def get_anomalies(
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

        df = service.get_anomalies()

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


@router.get("/opportunities")
def get_opportunities(
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

        df = service.get_opportunities()

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


@router.get("/root-causes")
def get_root_causes():

    try:

        data = service.get_root_causes()

        return {
            dimension: service.paginate(
                df,
                page=1,
                page_size=50,
            )
            for dimension, df
            in data.items()
        }

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/reconciliation")
def get_reconciliation(
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

        df = service.get_reconciliation()

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


@router.get(
    "/reconciliation/summary"
)
def get_reconciliation_summary():

    try:

        return (
            service
            .get_reconciliation_summary()
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )