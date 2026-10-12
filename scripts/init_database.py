import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.database.connection import Base, engine
from app.models import (
    DimDate,
    DimMerchant,
    DimPartner,
    DimRegion,
    DimCategory,
    DimErrorCode,
)


def initialize_database():
    print("Initializing NEXUS-M database...")

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")

    print("\nRegistered tables:")

    for table_name in Base.metadata.tables:
        print(f"  - {table_name}")


if __name__ == "__main__":
    initialize_database()