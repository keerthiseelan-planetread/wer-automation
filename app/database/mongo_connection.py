"""MongoDB connection and client management."""

import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from app.config import Config

logger = logging.getLogger(__name__)

# Global client instance (singleton pattern)
_mongo_client = None


def get_mongo_client(timeout=5000):
    """
    Get or create MongoDB client with connection pooling.
    
    Args:
        timeout: Connection timeout in milliseconds
        
    Returns:
        MongoClient: MongoDB client instance
        
    Raises:
        ConnectionError: If unable to connect to MongoDB
    """
    global _mongo_client
    
    if _mongo_client is not None:
        return _mongo_client
    
    try:
        logger.info("Connecting to MongoDB...")
        _mongo_client = MongoClient(
            Config.MONGODB_URI,
            serverSelectionTimeoutMS=timeout,
            connectTimeoutMS=timeout,
            socketTimeoutMS=timeout,
            retryWrites=True,
            w="majority",
            ssl=True,
            tlsAllowInvalidCertificates=True
        )
        
        # Verify connection with shorter timeout
        logger.info("Verifying MongoDB connection...")
        _mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return _mongo_client
        
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise ConnectionError(f"MongoDB connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
        raise ConnectionError(f"Unexpected MongoDB error: {str(e)}")


def get_database(db_name=None):
    """
    Get MongoDB database instance.
    
    Args:
        db_name: Database name (defaults to config value)
        
    Returns:
        Database: MongoDB database instance
    """
    if db_name is None:
        db_name = Config.MONGODB_DB_NAME
    
    client = get_mongo_client()
    return client[db_name]


def close_mongo_connection():
    """Close MongoDB client connection."""
    global _mongo_client
    if _mongo_client is not None:
        try:
            _mongo_client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
        finally:
            _mongo_client = None


def reset_mongo_connection():
    """Reset MongoDB client (useful for testing)."""
    global _mongo_client
    if _mongo_client is not None:
        close_mongo_connection()
    _mongo_client = None