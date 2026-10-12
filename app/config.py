from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NEXUS-M"
    app_version: str = "1.0.0"
    environment: str = "development"

    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "nexus_m"
    database_user: str = "postgres"
    database_password: str = ""

    api_host: str = "127.0.0.1"
    api_port: int = 8000

    openai_api_key: str = ""

    vector_db_path: str = "./data/vector_store"

    raw_data_path: str = "./data/raw"
    processed_data_path: str = "./data/processed"
    synthetic_data_path: str = "./data/synthetic"

    anomaly_threshold: float = 3.0
    data_quality_threshold: float = 95.0
    reconciliation_threshold: float = 0.01

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()