from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from apps.streamlit.components import page_header


page_header(
    "Data Quality",
    "Monitor completeness, validity, consistency, and governance checks.",
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

PHASE6_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "phase6"
)


if not PHASE6_DIR.exists():

    st.warning(
        """
Phase 6 Data Quality outputs have not been generated yet.

This page is intentionally waiting for the Data Quality &
Governance Engine from Phase 6.
"""
    )

    st.info(
        """
Expected future outputs:

- data_quality_results.csv
- data_quality_summary.json
- schema_validation.csv
- referential_integrity.csv
- freshness_results.csv
"""
    )

    st.stop()


st.success(
    "Phase 6 data-quality output detected."
)


csv_path = PHASE6_DIR / "data_quality_results.csv"


if csv_path.exists():

    df = pd.read_csv(csv_path)

    st.subheader(
        "Data Quality Results"
    )

    st.dataframe(
        df,
        use_container_width=True,
    )

else:

    st.info(
        "data_quality_results.csv has not been generated."
    )


json_path = PHASE6_DIR / "data_quality_summary.json"


if json_path.exists():

    import json

    summary = json.loads(
        json_path.read_text(
            encoding="utf-8"
        )
    )

    st.subheader(
        "Data Quality Summary"
    )

    st.json(summary)