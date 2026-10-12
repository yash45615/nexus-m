from pathlib import Path

import pandas as pd

from app.data_config import SYNTHETIC_DATA_DIR


class AnalyticsDataLoader:
    """
    Loads NEXUS-M synthetic datasets into Pandas DataFrames.
    """

    def __init__(
        self,
        data_dir: Path = SYNTHETIC_DATA_DIR,
    ):
        self.data_dir = Path(data_dir)

    def load_transactions(self) -> pd.DataFrame:
        path = self.data_dir / "transactions.csv"

        df = pd.read_csv(
            path,
            parse_dates=["created_at"],
        )

        return df

    def load_merchants(self) -> pd.DataFrame:
        path = self.data_dir / "dim_merchant.csv"

        return pd.read_csv(path)

    def load_partners(self) -> pd.DataFrame:
        path = self.data_dir / "dim_partner.csv"

        return pd.read_csv(path)

    def load_regions(self) -> pd.DataFrame:
        path = self.data_dir / "dim_region.csv"

        return pd.read_csv(path)

    def load_categories(self) -> pd.DataFrame:
        path = self.data_dir / "dim_category.csv"

        return pd.read_csv(path)

    def load_error_codes(self) -> pd.DataFrame:
        path = self.data_dir / "dim_error_code.csv"

        return pd.read_csv(path)

    def load_settlements(self) -> pd.DataFrame:
        path = self.data_dir / "settlements.csv"

        return pd.read_csv(
            path,
            parse_dates=[
                "settlement_date",
                "created_at",
            ],
        )

    def load_partner_events(self) -> pd.DataFrame:
        path = self.data_dir / "partner_events.csv"

        return pd.read_csv(
            path,
            parse_dates=["event_timestamp"],
        )

    def load_all(self) -> dict[str, pd.DataFrame]:
        return {
            "transactions": self.load_transactions(),
            "merchants": self.load_merchants(),
            "partners": self.load_partners(),
            "regions": self.load_regions(),
            "categories": self.load_categories(),
            "error_codes": self.load_error_codes(),
            "settlements": self.load_settlements(),
            "partner_events": self.load_partner_events(),
        }