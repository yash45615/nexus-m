from __future__ import annotations

import plotly.express as px
import streamlit as st

from apps.streamlit.api_client import cached_partners
from apps.streamlit.components import (
    dataframe_from_response,
    page_header,
    safe_call,
    show_api_error,
)


page_header(
    "Partner Intelligence",
    "Monitor payment-partner reliability, latency, and transaction performance.",
)


response, error = safe_call(cached_partners)

if error:
    show_api_error(error)
    st.stop()


df = dataframe_from_response(response)


if df.empty:
    st.info(
        "No partner records are currently available."
    )
    st.stop()


st.subheader("Partner Performance")

st.dataframe(
    df,
    use_container_width=True,
)


success_column = next(
    (
        column
        for column in [
            "success_rate",
            "authorization_success_rate",
        ]
        if column in df.columns
    ),
    None,
)


partner_column = next(
    (
        column
        for column in [
            "partner_key",
            "partner_id",
            "partner_name",
        ]
        if column in df.columns
    ),
    df.columns[0],
)


if success_column:

    chart_df = (
        df.sort_values(
            success_column,
            ascending=False,
        )
        .head(20)
    )

    fig = px.bar(
        chart_df,
        x=partner_column,
        y=success_column,
        title="Partner Success Rate",
    )

    fig.update_layout(
        xaxis_tickangle=-45,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Selected Partner")

selected_partner = st.selectbox(
    "Partner",
    df[partner_column].astype(str).tolist(),
)


selected = df[
    df[partner_column].astype(str)
    == selected_partner
]


if not selected.empty:

    st.json(
        selected.iloc[0].to_dict()
    )