import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Config:
    # Google Drive Configuration
    GOOGLE_DRIVE_ROOT_ID = os.getenv("GOOGLE_DRIVE_ROOT_ID")
    SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")
    ALLOWED_USERS = os.getenv("ALLOWED_USERS")

    # ✅ MongoDB Configuration (DEFAULT → LOCAL COMPASS)
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
    MONGODB_DB_NAME = "wer-automation"
    
    # MongoDB Collections
    MONGODB_COLLECTIONS = {
        "wer_results": "wer_results",
        "processing_metadata": "processing_metadata",
        "tool_summary_metrics": "tool_summary_metrics"
    }

    # Scheduler Configuration
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"
    SCHEDULER_TIME = os.getenv("SCHEDULER_TIME", "02:00")  # Format: "HH:MM" (24-hour)
    SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "UTC")

    @staticmethod
    def validate():
        """Validate all configuration variables and their validity."""
        missing = []
        issues = []

        # Check required variables exist
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
        
        # ✅ Show which DB is being used
        logger.info(f"Using MongoDB URI: {Config.MONGODB_URI}")

        # Validate service account file exists
        if Config.SERVICE_ACCOUNT_PATH:
            if not os.path.exists(Config.SERVICE_ACCOUNT_PATH):
                raise ValueError(
                    f"❌ Unable to find Google service account file\n\n"
                    f"Expected location: {Config.SERVICE_ACCOUNT_PATH}\n\n"
                    f"What to do:\n"
                    f"1. Make sure the file '{os.path.basename(Config.SERVICE_ACCOUNT_PATH)}' exists\n"
                    f"2. Check SERVICE_ACCOUNT_PATH in .env\n"
                )
            
            # Validate JSON
            try:
                with open(Config.SERVICE_ACCOUNT_PATH, 'r') as f:
                    json.load(f)
                logger.info("✓ Service account file loaded successfully")
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Service account file is not valid JSON: {str(e)}"
                )
            except Exception as e:
                raise ValueError(
                    f"Cannot read service account file: {str(e)}"
                )
        
        # Validate MongoDB URI
        if Config.MONGODB_URI and not Config.MONGODB_URI.startswith("mongodb"):
            issues.append("MONGODB_URI is not valid")

        # ⚠️ Detect Atlas (just warning)
        if "mongodb+srv" in Config.MONGODB_URI:
            logger.warning("⚠️ You are using MongoDB Atlas. For Compass use mongodb://127.0.0.1:27017")

        if issues:
            logger.warning(f"Configuration warnings: {'; '.join(issues)}")

    @staticmethod
    def get_allowed_users():
        if not Config.ALLOWED_USERS:
            return {}

        users_dict = {}
        user_entries = Config.ALLOWED_USERS.split(",")
        
        skipped_count = 0
        for idx, entry in enumerate(user_entries):
            parts = entry.split(":")

            if len(parts) != 2:
                skipped_count += 1
                logger.warning(f"Invalid ALLOWED_USERS entry skipped: {entry}")
                continue

            email = parts[0].strip()
            hashed_password = parts[1].strip()
            
            if not email or not hashed_password:
                skipped_count += 1
                logger.warning(f"Empty email/password skipped: {entry}")
                continue

            users_dict[email] = hashed_password
        
        logger.info(f"Loaded {len(users_dict)} users")
        return users_dict