from __future__ import annotations

import streamlit as st

from apps.streamlit.api_client import (
    cached_health,
)
from apps.streamlit.components import show_api_error


st.set_page_config(
    page_title="NEXUS-M Analyst Console",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.sidebar.title("NEXUS-M")

st.sidebar.caption(
    "Autonomous Merchant & Network Intelligence Platform"
)

st.sidebar.divider()

st.sidebar.markdown(
    """
### Analyst Console

Use the navigation panel to explore:

- Executive KPIs
- Performance metrics
- Anomalies
- Root causes
- Opportunities
- Merchants
- Partners
- Reconciliation
- Data quality
"""
)

st.sidebar.divider()

try:
    health = cached_health()

    if health.get("status") == "healthy":
        st.sidebar.success(
            "API: Connected"
        )
    else:
        st.sidebar.warning(
            "API: Degraded"
        )

except Exception as exc:
    show_api_error(str(exc))


st.title("NEXUS-M")

st.subheader(
    "Autonomous Merchant & Network Intelligence Platform"
)

st.markdown(
    """
NEXUS-M converts payment-network data into actionable
business intelligence.

Use the analyst console to:

**Monitor → Investigate → Explain → Quantify → Act**
"""
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Analytical Layer",
        "Active",
    )

with col2:
    st.metric(
        "API Layer",
        "FastAPI",
    )

with col3:
    st.metric(
        "Visualization",
        "Streamlit + Plotly",
    )

st.info(
    """
Select a page from the left navigation to begin an analysis.
"""
)

st.caption(
    "NEXUS-M v1.0.0"
)