import os
from typing import List

from dotenv import load_dotenv

# Load the .env file (path relative to repository root)
load_dotenv("app/.env")


class Settings:
    # MongoDB settings (supports both MONGODB_URI and MONGO_URI)
    MONGODB_URI: str = os.getenv(
        "MONGODB_URI",
        os.getenv("MONGO_URI", "mongodb://localhost:27017/wer_automation"),
    )
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "wer_automation_db")

    # JWT / security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "wer_automation_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS / server
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()
    ]
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Google Drive / service account
    SERVICE_ACCOUNT_PATH: str = os.getenv(
        "SERVICE_ACCOUNT_PATH", "app/service.account.json"
    )
    GOOGLE_DRIVE_ROOT_ID: str = os.getenv("GOOGLE_DRIVE_ROOT_ID", "")

    # Raw allowed users string (parsed elsewhere)
    ALLOWED_USERS: str = os.getenv("ALLOWED_USERS", "")


settings = Settings()