from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_service import (
    AnalyticalDataService,
)

router = APIRouter(
    prefix="/api/v1/merchants",
    tags=["Merchants"],
)

service = AnalyticalDataService()


@router.get("")
def get_merchants(
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

        df = service.get_merchants()

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


@router.get("/{merchant_id}")
def get_merchant(
    merchant_id: str,
):

    try:

        df = service.get_merchants()

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    possible_columns = [
        "merchant_key",
        "merchant_id",
    ]

    column = next(
        (
            c
            for c in possible_columns
            if c in df.columns
        ),
        None,
    )

    if column is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Merchant identifier "
                "column not found."
            ),
        )

    result = df[
        df[column].astype(str)
        == str(merchant_id)
    ]

    if result.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Merchant '{merchant_id}' "
                "was not found."
            ),
        )

    return result.iloc[0].to_dict()