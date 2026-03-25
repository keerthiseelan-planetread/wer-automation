import os
import json
import logging
from dotenv import load_dotenv

# ✅ Load .env from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

logger = logging.getLogger(__name__)

class Config:
    # =========================
    # GOOGLE DRIVE
    # =========================
    GOOGLE_DRIVE_ROOT_ID = os.getenv("GOOGLE_DRIVE_ROOT_ID")
    SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")
    ALLOWED_USERS = os.getenv("ALLOWED_USERS")

    # =========================
    # MONGODB
    # =========================
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "wer_automation_db")

    # ✅ COLLECTION NAMES (FROM .env)
    WER_RESULTS_COLLECTION = os.getenv("WER_RESULTS_COLLECTION", "wer_results")
    PROCESSING_METADATA_COLLECTION = os.getenv(
        "PROCESSING_METADATA_COLLECTION", "processing_metadata"
    )
    TOOL_SUMMARY_COLLECTION = os.getenv(
        "TOOL_SUMMARY_COLLECTION", "tool_summary_metrics"
    )

    # =========================
    # VALIDATION
    # =========================
    @staticmethod
    def validate():
        missing = []

        if not Config.GOOGLE_DRIVE_ROOT_ID:
            missing.append("GOOGLE_DRIVE_ROOT_ID")
        if not Config.SERVICE_ACCOUNT_PATH:
            missing.append("SERVICE_ACCOUNT_PATH")
        if not Config.ALLOWED_USERS:
            missing.append("ALLOWED_USERS")
        if not Config.MONGODB_URI:
            missing.append("MONGODB_URI")

        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

        logger.info(f"Using MongoDB URI: {Config.MONGODB_URI}")
        logger.info(f"Using MongoDB DB: {Config.MONGODB_DB_NAME}")

        # Validate service account file
        if not os.path.exists(Config.SERVICE_ACCOUNT_PATH):
            raise ValueError(
                f"❌ Service account file not found: {Config.SERVICE_ACCOUNT_PATH}"
            )

        try:
            with open(Config.SERVICE_ACCOUNT_PATH, "r") as f:
                json.load(f)
            logger.info("✓ Service account JSON validated")
        except Exception as e:
            raise ValueError(f"Invalid service account JSON: {str(e)}")