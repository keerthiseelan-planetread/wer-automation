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

    # MongoDB Configuration
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DB_NAME = "wer-automation"
    
    # MongoDB Collections
    MONGODB_COLLECTIONS = {
        "wer_results": "wer_results",
        "processing_metadata": "processing_metadata",
        "tool_summary_metrics": "tool_summary_metrics"
    }

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
        
        # Validate service account file exists
        if Config.SERVICE_ACCOUNT_PATH:
            if not os.path.exists(Config.SERVICE_ACCOUNT_PATH):
                raise ValueError(
                    f"❌ Unable to find Google service account file\n\n"
                    f"Expected location: {Config.SERVICE_ACCOUNT_PATH}\n\n"
                    f"What to do:\n"
                    f"1. Make sure the file '{os.path.basename(Config.SERVICE_ACCOUNT_PATH)}' exists in the app folder\n"
                    f"2. Check that SERVICE_ACCOUNT_PATH in .env file has the correct filename\n"
                    f"3. If you don't have a service account file, download it from Google Cloud Console"
                )
            
            # Validate service account file is valid JSON
            try:
                with open(Config.SERVICE_ACCOUNT_PATH, 'r') as f:
                    json.load(f)
                logger.info("✓ Service account file loaded successfully")
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Service account file is not valid JSON at: {Config.SERVICE_ACCOUNT_PATH}\n"
                    f"Error: {str(e)}"
                )
            except Exception as e:
                raise ValueError(
                    f"Cannot read service account file: {Config.SERVICE_ACCOUNT_PATH}\n"
                    f"Error: {str(e)}"
                )
        
        # Validate MONGODB_URI format (basic check)
        if Config.MONGODB_URI and not Config.MONGODB_URI.startswith("mongodb"):
            issues.append("MONGODB_URI does not appear to be a valid MongoDB connection string")
        
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
                logger.warning(
                    f"ALLOWED_USERS entry {idx}: Invalid format (expected 'email:hash'). "
                    f"Skipped: '{entry.strip()[:50]}...'" if len(entry) > 50 else f"Skipped: '{entry.strip()}'"
                )
                continue

            email = parts[0].strip()
            hashed_password = parts[1].strip()
            
            if not email or not hashed_password:
                skipped_count += 1
                logger.warning(f"ALLOWED_USERS entry {idx}: Empty email or password. Skipped.")
                continue

            users_dict[email] = hashed_password
        
        if skipped_count > 0:
            logger.warning(
                f"Loaded {len(users_dict)} users, skipped {skipped_count} invalid entries from ALLOWED_USERS"
            )
        else:
            logger.info(f"Loaded {len(users_dict)} authorized users from ALLOWED_USERS")
        
        return users_dict