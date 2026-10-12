from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def page_header(
    title: str,
    description: str,
) -> None:
    st.title(title)
    st.caption(description)


def section_title(title: str) -> None:
    st.subheader(title)


def show_api_error(error: str | None) -> None:
    if error:
        st.error(
            "Unable to reach the NEXUS-M Analytical API."
        )
        st.code(error)


def dataframe_from_response(
    response: dict[str, Any] | None,
) -> pd.DataFrame:
    if not response:
        return pd.DataFrame()

    items = response.get("items", [])

    if not isinstance(items, list):
        return pd.DataFrame()

    return pd.DataFrame(items)


def extract_items(
    response: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not response:
        return []

    items = response.get("items", [])

    if isinstance(items, list):
        return items

    return []


def safe_number(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        if value is None:
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


def format_number(value: Any) -> str:
    number = safe_number(value)

    if abs(number) >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"

    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"

    if abs(number) >= 1_000:
        return f"{number / 1_000:.2f}K"

    return f"{number:,.2f}"


def find_metric(
    kpis: dict[str, Any],
    names: list[str],
    default: float = 0.0,
) -> float:
    """
    Locate a KPI using several possible naming conventions.
    """

    for name in names:
        if name in kpis:
            return safe_number(
                kpis[name],
                default,
            )

    return default


def status_badge(status: str) -> None:
    status_upper = str(status).upper()

    if status_upper in {
        "HEALTHY",
        "OK",
        "NORMAL",
        "GOOD",
    }:
        st.success(status_upper)

    elif status_upper in {
        "WARNING",
        "MEDIUM",
    }:
        st.warning(status_upper)

    else:
        st.error(status_upper)