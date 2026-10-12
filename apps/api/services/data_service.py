from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


class AnalyticalDataService:
    """
    Central access layer for NEXUS-M analytical outputs.
    """

    def __init__(
        self,
        processed_dir: Path = PROCESSED_DIR,
    ):

        self.processed_dir = Path(
            processed_dir
        )

    def _read_csv(
        self,
        relative_path: str,
    ) -> pd.DataFrame:

        path = (
            self.processed_dir
            / relative_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Analytical output not found: {path}"
            )

        return pd.read_csv(path)

    def _read_json(
        self,
        relative_path: str,
    ) -> dict[str, Any]:

        path = (
            self.processed_dir
            / relative_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Analytical output not found: {path}"
            )

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------

    def get_kpis(self) -> dict[str, Any]:

        path = (
            self.processed_dir
            / "phase7"
            / "kpi_summary.json"
        )

        if path.exists():

            return self._read_json(
                "phase7/kpi_summary.json"
            )

        # Fallback to Phase 4
        return self._read_json(
            "phase4/core_kpis.json"
        )

    # ---------------------------------------------------------
    # Merchant segmentation
    # ---------------------------------------------------------

    def get_merchants(
        self,
    ) -> pd.DataFrame:

        return self._read_csv(
            "phase8/merchant_segments.csv"
        )

    # ---------------------------------------------------------
    # Partner performance
    # ---------------------------------------------------------

    def get_partners(
        self,
    ) -> pd.DataFrame:

        return self._read_csv(
            "phase4/partner_performance.csv"
        )

    # ---------------------------------------------------------
    # Regional performance
    # ---------------------------------------------------------

    def get_regions(
        self,
    ) -> pd.DataFrame:

        return self._read_csv(
            "phase4/regional_performance.csv"
        )

    # ---------------------------------------------------------
    # Anomalies
    # ---------------------------------------------------------

    def get_anomalies(
        self,
    ) -> pd.DataFrame:

        return self._read_csv(
            "phase9/anomaly_results.csv"
        )

    # ---------------------------------------------------------
    # Root causes
    # ---------------------------------------------------------

    def get_root_causes(
        self,
    ) -> dict[str, pd.DataFrame]:

        dimensions = [
            "partner_key",
            "region_key",
            "category_key",
            "error_code",
            "merchant_key",
        ]

        result = {}

        for dimension in dimensions:

            result[dimension] = self._read_csv(
                f"phase10/{dimension}_root_causes.csv"
            )

        return result

    # ---------------------------------------------------------
    # Opportunities
    # ---------------------------------------------------------

    def get_opportunities(
        self,
    ) -> pd.DataFrame:

        return self._read_csv(
            "phase11/opportunity_priorities.csv"
        )

    # ---------------------------------------------------------
    # Reconciliation
    # ---------------------------------------------------------

    def get_reconciliation(
        self,
    ) -> pd.DataFrame:

        return self._read_csv(
            "phase12/reconciliation_details.csv"
        )

    def get_reconciliation_summary(
        self,
    ) -> dict[str, Any]:

        return self._read_json(
            "phase12/reconciliation_summary.json"
        )

    # ---------------------------------------------------------
    # Pagination
    # ---------------------------------------------------------

    @staticmethod
    def paginate(
        df: pd.DataFrame,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:

        page = max(page, 1)

        page_size = min(
            max(page_size, 1),
            500,
        )

        total = len(df)

        pages = (
            math.ceil(total / page_size)
            if total
            else 1
        )

        start = (
            (page - 1)
            * page_size
        )

        end = start + page_size

        records = (
            df.iloc[start:end]
            .replace({float("nan"): None})
            .to_dict(
                orient="records"
            )
        )

        return {
            "items": records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }