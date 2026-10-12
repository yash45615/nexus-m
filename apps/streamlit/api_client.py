from __future__ import annotations

from typing import Any

import requests
import streamlit as st

from apps.streamlit.config import API_BASE_URL, REQUEST_TIMEOUT


class APIClient:
    """Client for the NEXUS-M Analytical API."""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout: int = REQUEST_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"

        response = requests.get(
            url,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def health(self) -> dict[str, Any]:
        return self.get("/health")

    def get_kpis(self) -> dict[str, Any]:
        return self.get("/api/v1/kpis")

    def get_merchants(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        return self.get(
            "/api/v1/merchants",
            params={
                "page": page,
                "page_size": page_size,
            },
        )

    def get_merchant(
        self,
        merchant_id: str,
    ) -> dict[str, Any]:
        return self.get(
            f"/api/v1/merchants/{merchant_id}"
        )

    def get_partners(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        return self.get(
            "/api/v1/partners",
            params={
                "page": page,
                "page_size": page_size,
            },
        )

    def get_regions(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        return self.get(
            "/api/v1/regions",
            params={
                "page": page,
                "page_size": page_size,
            },
        )

    def get_anomalies(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        return self.get(
            "/api/v1/anomalies",
            params={
                "page": page,
                "page_size": page_size,
            },
        )

    def get_root_causes(
        self,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        return self.get(
            "/api/v1/root-causes",
            params={
                "page": page,
                "page_size": page_size,
            },
        )

    def get_opportunities(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        return self.get(
            "/api/v1/opportunities",
            params={
                "page": page,
                "page_size": page_size,
            },
        )

    def get_reconciliation(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        return self.get(
            "/api/v1/reconciliation",
            params={
                "page": page,
                "page_size": page_size,
            },
        )

    def get_reconciliation_summary(self) -> dict[str, Any]:
        return self.get(
            "/api/v1/reconciliation/summary"
        )


@st.cache_resource
def get_api_client() -> APIClient:
    return APIClient()


@st.cache_data(ttl=60)
def cached_health() -> dict[str, Any]:
    return get_api_client().health()


@st.cache_data(ttl=60)
def cached_kpis() -> dict[str, Any]:
    return get_api_client().get_kpis()


@st.cache_data(ttl=60)
def cached_merchants() -> dict[str, Any]:
    return get_api_client().get_merchants(
        page=1,
        page_size=500,
    )


@st.cache_data(ttl=60)
def cached_partners() -> dict[str, Any]:
    return get_api_client().get_partners(
        page=1,
        page_size=500,
    )


@st.cache_data(ttl=60)
def cached_regions() -> dict[str, Any]:
    return get_api_client().get_regions(
        page=1,
        page_size=500,
    )


@st.cache_data(ttl=60)
def cached_anomalies() -> dict[str, Any]:
    return get_api_client().get_anomalies(
        page=1,
        page_size=500,
    )


@st.cache_data(ttl=60)
def cached_root_causes() -> dict[str, Any]:
    return get_api_client().get_root_causes(
        page=1,
        page_size=100,
    )


@st.cache_data(ttl=60)
def cached_opportunities() -> dict[str, Any]:
    return get_api_client().get_opportunities(
        page=1,
        page_size=500,
    )


@st.cache_data(ttl=60)
def cached_reconciliation() -> dict[str, Any]:
    return get_api_client().get_reconciliation(
        page=1,
        page_size=500,
    )


@st.cache_data(ttl=60)
def cached_reconciliation_summary() -> dict[str, Any]:
    return get_api_client().get_reconciliation_summary()


def safe_call(function):
    """
    Execute an API function and convert connection failures
    into a Streamlit-friendly result.
    """
    try:
        return function(), None

    except requests.RequestException as exc:
        return None, str(exc)

    except Exception as exc:
        return None, str(exc)