from __future__ import annotations

import plotly.express as px
import streamlit as st

from apps.streamlit.api_client import cached_opportunities
from apps.streamlit.components import (
    dataframe_from_response,
    page_header,
    safe_call,
    show_api_error,
)


page_header(
    "Opportunity Intelligence",
    "Prioritize measurable opportunities using value-at-risk and recovery scenarios.",
)


response, error = safe_call(cached_opportunities)

if error:
    show_api_error(error)
    st.stop()


df = dataframe_from_response(response)


if df.empty:
    st.info(
        "No opportunity records are currently available."
    )
    st.stop()


st.subheader("Opportunity Portfolio")

st.dataframe(
    df,
    use_container_width=True,
)


priority_column = next(
    (
        column
        for column in [
            "priority",
            "opportunity_priority",
        ]
        if column in df.columns
    ),
    None,
)


if priority_column:

    priority_counts = (
        df[priority_column]
        .value_counts()
        .reset_index()
    )

    priority_counts.columns = [
        "priority",
        "count",
    ]

    fig = px.bar(
        priority_counts,
        x="priority",
        y="count",
        title="Opportunity Priority Distribution",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


value_column = next(
    (
        column
        for column in [
            "recoverable_value",
            "estimated_recovered_value",
            "value_at_risk",
        ]
        if column in df.columns
    ),
    None,
)


if value_column:

    chart_df = (
        df.sort_values(
            value_column,
            ascending=False,
        )
        .head(15)
    )

    dimension_column = next(
        (
            column
            for column in [
                "dimension",
                "merchant_key",
                "partner_key",
                "region_key",
            ]
            if column in chart_df.columns
        ),
        chart_df.columns[0],
    )

    fig = px.bar(
        chart_df,
        x=dimension_column,
        y=value_column,
        title="Largest Estimated Recovery Opportunities",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Selected Opportunity")

selected_index = st.selectbox(
    "Select opportunity",
    options=list(df.index),
)

st.json(
    df.loc[selected_index].to_dict()
)