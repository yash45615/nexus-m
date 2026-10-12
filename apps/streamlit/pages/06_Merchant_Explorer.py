from __future__ import annotations

import plotly.express as px
import streamlit as st

from apps.streamlit.api_client import cached_merchants
from apps.streamlit.components import (
    dataframe_from_response,
    page_header,
    safe_call,
    show_api_error,
)


page_header(
    "Merchant Explorer",
    "Explore merchant performance, segmentation, and operational risk.",
)


response, error = safe_call(cached_merchants)

if error:
    show_api_error(error)
    st.stop()


df = dataframe_from_response(response)


if df.empty:
    st.info(
        "No merchant records are currently available."
    )
    st.stop()


st.subheader("Merchant Portfolio")

st.dataframe(
    df,
    use_container_width=True,
)


segment_column = next(
    (
        column
        for column in [
            "business_segment",
            "segment",
            "merchant_segment",
        ]
        if column in df.columns
    ),
    None,
)


if segment_column:

    counts = (
        df[segment_column]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "segment",
        "merchant_count",
    ]

    fig = px.pie(
        counts,
        names="segment",
        values="merchant_count",
        title="Merchant Segmentation",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Merchant Detail")

merchant_column = next(
    (
        column
        for column in [
            "merchant_key",
            "merchant_id",
        ]
        if column in df.columns
    ),
    None,
)


if merchant_column:

    selected = st.selectbox(
        "Select merchant",
        df[merchant_column].astype(str).tolist(),
    )

    merchant_row = df[
        df[merchant_column].astype(str)
        == selected
    ]

    if not merchant_row.empty:
        st.json(
            merchant_row.iloc[0].to_dict()
        )