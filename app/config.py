import os
from dotenv import load_dotenv

load_dotenv()

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

    @staticmethod
    def get_allowed_users():
        if not Config.ALLOWED_USERS:
            return {}

        users_dict = {}

        user_entries = Config.ALLOWED_USERS.split(",")

        for entry in user_entries:
            parts = entry.split(":")

            if len(parts) != 2:
                continue  # skip malformed entries

            email = parts[0].strip()
            hashed_password = parts[1].strip()

            users_dict[email] = hashed_password

        return users_dict