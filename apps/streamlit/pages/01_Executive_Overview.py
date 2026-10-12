from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from apps.streamlit.api_client import (
    cached_anomalies,
    cached_kpis,
    cached_opportunities,
    cached_partners,
    cached_reconciliation_summary,
)
from apps.streamlit.components import (
    dataframe_from_response,
    find_metric,
    format_number,
    page_header,
    safe_call,
    show_api_error,
)


page_header(
    "Executive Overview",
    "Executive command center for payment-network performance.",
)


kpis, kpi_error = safe_call(cached_kpis)

if kpi_error:
    show_api_error(kpi_error)
    st.stop()

kpi_data = kpis or {}

if "metrics" in kpi_data:
    kpi_values = kpi_data["metrics"]
else:
    kpi_values = kpi_data


transaction_count = find_metric(
    kpi_values,
    [
        "transaction_count",
        "transactions",
        "total_transactions",
    ],
)

success_rate = find_metric(
    kpi_values,
    [
        "success_rate",
        "authorization_success_rate",
    ],
)

failure_rate = find_metric(
    kpi_values,
    [
        "failure_rate",
        "authorization_failure_rate",
    ],
)

transaction_value = find_metric(
    kpi_values,
    [
        "total_transaction_value",
        "transaction_value",
        "total_value",
    ],
)

avg_latency = find_metric(
    kpi_values,
    [
        "average_processing_latency",
        "average_latency_ms",
        "avg_latency_ms",
    ],
)

p95_latency = find_metric(
    kpi_values,
    [
        "p95_processing_latency",
        "p95_latency_ms",
    ],
)


st.subheader("Network Health")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Transactions",
        format_number(transaction_count),
    )

with col2:
    st.metric(
        "Transaction Value",
        format_number(transaction_value),
    )

with col3:
    st.metric(
        "Success Rate",
        f"{success_rate:.2f}%",
    )


col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        "Failure Rate",
        f"{failure_rate:.2f}%",
    )

with col5:
    st.metric(
        "Average Latency",
        f"{avg_latency:.2f} ms",
    )

with col6:
    st.metric(
        "P95 Latency",
        f"{p95_latency:.2f} ms",
    )


st.divider()

st.subheader("Top Partners")

partners, partner_error = safe_call(
    cached_partners
)

if partner_error:
    show_api_error(partner_error)
else:
    partner_df = dataframe_from_response(
        partners
    )

    if not partner_df.empty:

        numeric_candidates = [
            "success_rate",
            "failure_rate",
            "transaction_count",
        ]

        available = [
            column
            for column in numeric_candidates
            if column in partner_df.columns
        ]

        if available:
            metric_column = available[0]

            chart_df = partner_df.head(10)

            fig = px.bar(
                chart_df,
                x="partner_key"
                if "partner_key" in chart_df.columns
                else chart_df.columns[0],
                y=metric_column,
                title=f"Top Partners — {metric_column}",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        st.dataframe(
            partner_df.head(10),
            use_container_width=True,
        )


st.divider()

st.subheader("Detected Anomalies")

anomalies, anomaly_error = safe_call(
    cached_anomalies
)

if anomaly_error:
    show_api_error(anomaly_error)
else:
    anomaly_df = dataframe_from_response(
        anomalies
    )

    if anomaly_df.empty:
        st.success(
            "No anomalies are currently exposed by the API."
        )
    else:
        st.dataframe(
            anomaly_df.head(10),
            use_container_width=True,
        )


st.divider()

st.subheader("Highest-Priority Opportunities")

opportunities, opportunity_error = safe_call(
    cached_opportunities
)

if opportunity_error:
    show_api_error(opportunity_error)
else:
    opportunity_df = dataframe_from_response(
        opportunities
    )

    if opportunity_df.empty:
        st.info(
            "No opportunity records are available."
        )
    else:
        st.dataframe(
            opportunity_df.head(10),
            use_container_width=True,
        )


st.divider()

st.subheader("Reconciliation Health")

reconciliation, reconciliation_error = safe_call(
    cached_reconciliation_summary
)

if reconciliation_error:
    show_api_error(reconciliation_error)
else:
    summary = reconciliation or {}

    score = summary.get(
        "reconciliation_score"
    )

    exception_rate = summary.get(
        "exception_rate"
    )

    col1, col2 = st.columns(2)

    with col1:
        if score is not None:
            st.metric(
                "Reconciliation Score",
                f"{float(score):.2f}",
            )
        else:
            st.metric(
                "Reconciliation Score",
                "N/A",
            )

    with col2:
        if exception_rate is not None:
            st.metric(
                "Exception Rate",
                f"{float(exception_rate):.2f}%",
            )
        else:
            st.metric(
                "Exception Rate",
                "N/A",
            )