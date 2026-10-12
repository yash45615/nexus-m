from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from apps.streamlit.api_client import cached_kpis
from apps.streamlit.components import (
    find_metric,
    format_number,
    page_header,
    safe_call,
    show_api_error,
)


page_header(
    "KPI Monitoring",
    "Monitor the core analytical metrics used by NEXUS-M.",
)


response, error = safe_call(cached_kpis)

if error:
    show_api_error(error)
    st.stop()


data = response or {}

metrics = data.get(
    "metrics",
    data,
)


records = []

if isinstance(metrics, dict):
    for name, value in metrics.items():

        try:
            numeric_value = float(value)

        except (TypeError, ValueError):
            continue

        records.append(
            {
                "metric": name,
                "value": numeric_value,
            }
        )


df = pd.DataFrame(records)


if df.empty:
    st.warning(
        "No numeric KPI metrics are available."
    )
    st.stop()


st.subheader("Metric Registry")

st.dataframe(
    df,
    use_container_width=True,
)


st.subheader("KPI Visualization")

fig = px.bar(
    df,
    x="metric",
    y="value",
    title="NEXUS-M KPI Values",
)

fig.update_layout(
    xaxis_tickangle=-45,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


st.subheader("Selected Business KPIs")

col1, col2, col3, col4 = st.columns(4)

success_rate = find_metric(
    metrics,
    ["success_rate"],
)

failure_rate = find_metric(
    metrics,
    ["failure_rate"],
)

transactions = find_metric(
    metrics,
    ["transaction_count"],
)

value = find_metric(
    metrics,
    ["total_transaction_value"],
)

with col1:
    st.metric(
        "Success Rate",
        f"{success_rate:.2f}%",
    )

with col2:
    st.metric(
        "Failure Rate",
        f"{failure_rate:.2f}%",
    )

with col3:
    st.metric(
        "Transactions",
        format_number(transactions),
    )

with col4:
    st.metric(
        "Transaction Value",
        format_number(value),
    )