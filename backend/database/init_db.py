from app.database.mongo_connection import get_database
from app.config import Config

def initialize_database():
    db = get_database()

    collections = [
        Config.WER_RESULTS_COLLECTION,
        Config.PROCESSING_METADATA_COLLECTION,
        Config.TOOL_SUMMARY_COLLECTION
    ]

    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)

    print("✅ MongoDB initialized with collections")