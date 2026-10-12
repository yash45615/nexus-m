from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from apps.streamlit.api_client import cached_root_causes
from apps.streamlit.components import (
    page_header,
    safe_call,
    show_api_error,
)


page_header(
    "Root-Cause Explorer",
    "Drill into the dimensions responsible for KPI deterioration.",
)


response, error = safe_call(cached_root_causes)

if error:
    show_api_error(error)
    st.stop()


root_causes = response or {}


if not root_causes:
    st.info(
        "No root-cause data is currently available."
    )
    st.stop()


dimension_names = [
    key
    for key, value in root_causes.items()
    if isinstance(value, dict)
]


if not dimension_names:
    st.warning(
        "The API returned no root-cause dimensions."
    )
    st.stop()


selected_dimension = st.selectbox(
    "Investigation dimension",
    dimension_names,
)


dimension_data = root_causes.get(
    selected_dimension,
    {},
)


items = dimension_data.get(
    "items",
    [],
)


df = pd.DataFrame(items)


if df.empty:
    st.info(
        "No records available for this dimension."
    )
    st.stop()


st.subheader(
    f"{selected_dimension} Investigation"
)


st.dataframe(
    df,
    use_container_width=True,
)


score_column = next(
    (
        column
        for column in [
            "root_cause_score",
            "score",
        ]
        if column in df.columns
    ),
    None,
)


if score_column:

    chart_df = (
        df.sort_values(
            score_column,
            ascending=False,
        )
        .head(10)
    )

    dimension_column = (
        selected_dimension
        if selected_dimension in chart_df.columns
        else chart_df.columns[0]
    )

    fig = px.bar(
        chart_df,
        x=dimension_column,
        y=score_column,
        title="Highest Root-Cause Scores",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Root-Cause Record")


selected_index = st.selectbox(
    "Select record",
    options=list(df.index),
)


st.json(
    df.loc[selected_index].to_dict()
)