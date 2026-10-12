from __future__ import annotations

import plotly.express as px
import streamlit as st

from apps.streamlit.api_client import (
    cached_reconciliation,
    cached_reconciliation_summary,
)
from apps.streamlit.components import (
    dataframe_from_response,
    page_header,
    safe_call,
    show_api_error,
)


page_header(
    "Reconciliation",
    "Monitor transaction-to-settlement matching and financial exceptions.",
)


summary, summary_error = safe_call(
    cached_reconciliation_summary
)

if summary_error:
    show_api_error(summary_error)
else:

    summary = summary or {}

    st.subheader("Reconciliation Health")

    score = summary.get(
        "reconciliation_score"
    )

    exception_rate = summary.get(
        "exception_rate"
    )

    total_transactions = summary.get(
        "total_transactions"
    )

    exception_transactions = summary.get(
        "exception_transactions"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Score",
            f"{float(score):.2f}"
            if score is not None
            else "N/A",
        )

    with col2:
        st.metric(
            "Exception Rate",
            f"{float(exception_rate):.2f}%"
            if exception_rate is not None
            else "N/A",
        )

    with col3:
        st.metric(
            "Transactions",
            f"{int(total_transactions):,}"
            if total_transactions is not None
            else "N/A",
        )

    with col4:
        st.metric(
            "Exceptions",
            f"{int(exception_transactions):,}"
            if exception_transactions is not None
            else "N/A",
        )


st.divider()

response, error = safe_call(
    cached_reconciliation
)

if error:
    show_api_error(error)
    st.stop()


df = dataframe_from_response(response)


if df.empty:
    st.info(
        "No reconciliation records are currently available."
    )
    st.stop()


st.subheader("Reconciliation Records")

st.dataframe(
    df,
    use_container_width=True,
)


exception_column = next(
    (
        column
        for column in [
            "exception_type",
            "reconciliation_exception",
        ]
        if column in df.columns
    ),
    None,
)


if exception_column:

    counts = (
        df[exception_column]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "exception_type",
        "count",
    ]

    fig = px.bar(
        counts,
        x="exception_type",
        y="count",
        title="Reconciliation Exceptions",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )