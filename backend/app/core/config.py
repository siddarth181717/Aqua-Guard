"""
AquaGuard Backend Settings & Core Configuration
------------------------------------------------
Manages application configuration, database connection strings, JWT keys, and CORS rules.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AquaGuard Backend BaseSettings."""

    PROJECT_NAME: str = "AquaGuard"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "aquaguard_super_secret_jwt_key_change_in_production_2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "aquaguard_db"
    POSTGIS_DATABASE: str = "aquaguard_db"
    DATABASE_URL: str = ""

    # ML Model & Data Configuration
    ML_MODEL_PATH: str = "models/restoration_priority_model.pkl"
    DATA_DIRECTORY: str = "data"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000"
    ]

    # External APIs
    GEE_PROJECT_ID: str = "aquaguard-gee-project"
    VITE_API_BASE_URL: str = "http://localhost:8000/api/v1"
    NEXT_PUBLIC_API_BASE_URL: str = "http://localhost:8000/api/v1"

    def model_post_init(self, __context):
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if not self.POSTGIS_DATABASE:
            self.POSTGIS_DATABASE = self.POSTGRES_DB

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.development", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

