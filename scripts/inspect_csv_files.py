from pathlib import Path

import pandas as pd


DATA_DIR = Path("data") / "synthetic"


def main():
    print("Synthetic CSV files")
    print("=" * 60)

    if not DATA_DIR.exists():
        print(f"Directory not found: {DATA_DIR}")
        return

    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found.")
        return

    for file in csv_files:
        print()
        print(f"File: {file.name}")

        try:
            df = pd.read_csv(file)

            print(f"Rows: {len(df):,}")
            print(f"Columns: {len(df.columns)}")
            print(f"Column names: {list(df.columns)}")

        except Exception as exc:
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()