from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from apps.streamlit.api_client import cached_anomalies
from apps.streamlit.components import (
    dataframe_from_response,
    page_header,
    safe_call,
    show_api_error,
)


page_header(
    "Anomaly Investigation",
    "Investigate statistical and machine-learning detected anomalies.",
)


response, error = safe_call(cached_anomalies)

if error:
    show_api_error(error)
    st.stop()


df = dataframe_from_response(response)


if df.empty:
    st.info(
        "No anomaly records are currently available."
    )
    st.stop()


st.subheader("Anomaly Dataset")

st.dataframe(
    df,
    use_container_width=True,
)


st.subheader("Severity Distribution")

severity_column = next(
    (
        column
        for column in [
            "severity",
            "anomaly_severity",
        ]
        if column in df.columns
    ),
    None,
)


if severity_column:

    severity_counts = (
        df[severity_column]
        .value_counts()
        .reset_index()
    )

    severity_counts.columns = [
        "severity",
        "count",
    ]

    fig = px.bar(
        severity_counts,
        x="severity",
        y="count",
        title="Anomalies by Severity",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Anomaly Timeline")

date_column = next(
    (
        column
        for column in [
            "date",
            "transaction_date",
            "created_at",
        ]
        if column in df.columns
    ),
    None,
)


if date_column:

    timeline = df.copy()

    timeline[date_column] = pd.to_datetime(
        timeline[date_column],
        errors="coerce",
    )

    timeline = (
        timeline
        .dropna(subset=[date_column])
        .groupby(date_column)
        .size()
        .reset_index(name="anomaly_count")
    )

    fig = px.line(
        timeline,
        x=date_column,
        y="anomaly_count",
        markers=True,
        title="Anomaly Frequency Over Time",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Investigation Record")

selected_index = st.selectbox(
    "Select anomaly",
    options=list(df.index),
)


selected = df.loc[selected_index]

st.json(
    selected.to_dict()
)