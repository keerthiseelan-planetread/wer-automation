from app.database.mongo_connection import get_mongo_client


def get_db():
    """Return the shared MongoDB client."""
    return get_mongo_client()