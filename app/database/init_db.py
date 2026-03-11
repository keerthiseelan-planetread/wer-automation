"""Database initialization and index creation."""

import logging
from pymongo.errors import CollectionInvalid, OperationFailure
from app.database.mongo_connection import get_database
from app.config import Config
from app.database.schemas import (
    WER_RESULT_SCHEMA,
    PROCESSING_METADATA_SCHEMA,
    TOOL_SUMMARY_METRICS_SCHEMA
)

logger = logging.getLogger(__name__)


def initialize_database():
    """
    Initialize MongoDB database with collections and indexes.
    Creates collections if they don't exist and sets up indexes.
    """
    try:
        db = get_database()
        logger.info("Initializing MongoDB database...")
        
        # Create collections with schema validation
        _create_collections(db)
        
        # Create indexes for performance
        _create_indexes(db)
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def _create_collections(db):
    """Create collections with JSON schema validation."""
    collections_config = {
        Config.MONGODB_COLLECTIONS["wer_results"]: WER_RESULT_SCHEMA,
        Config.MONGODB_COLLECTIONS["processing_metadata"]: PROCESSING_METADATA_SCHEMA,
        Config.MONGODB_COLLECTIONS["tool_summary_metrics"]: TOOL_SUMMARY_METRICS_SCHEMA,
    }
    
    for collection_name, schema in collections_config.items():
        try:
            if collection_name not in db.list_collection_names():
                db.create_collection(
                    collection_name,
                    validator={"$jsonSchema": schema}
                )
                logger.info(f"Created collection: {collection_name}")
            else:
                logger.info(f"Collection already exists: {collection_name}")
                
        except CollectionInvalid as e:
            logger.warning(f"Collection {collection_name} already exists: {str(e)}")
        except OperationFailure as e:
            logger.error(f"Failed to create collection {collection_name}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating collection {collection_name}: {str(e)}")
            raise


def _create_indexes(db):
    """Create indexes on collections for optimal query performance."""
    try:
        # Indexes for wer_results collection
        wer_results_col = db[Config.MONGODB_COLLECTIONS["wer_results"]]
        
        # Index on parameter_hash for fast lookups
        wer_results_col.create_index("parameter_hash", unique=False, background=True)
        logger.info("Created index on wer_results.parameter_hash")
        
        # Compound index on year, month, language
        wer_results_col.create_index(
            [("year", 1), ("month", 1), ("language", 1)],
            background=True
        )
        logger.info("Created compound index on wer_results (year, month, language)")
        
        # Index on last_updated for sorting
        wer_results_col.create_index("last_updated", background=True)
        logger.info("Created index on wer_results.last_updated")
        
        # Indexes for processing_metadata collection
        metadata_col = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]
        
        # Index on parameter_hash
        metadata_col.create_index("parameter_hash", unique=True, background=True)
        logger.info("Created unique index on processing_metadata.parameter_hash")
        
        # Compound index on year, month, language
        metadata_col.create_index(
            [("year", 1), ("month", 1), ("language", 1)],
            background=True
        )
        logger.info("Created compound index on processing_metadata (year, month, language)")
        
        # Indexes for tool_summary_metrics collection
        metrics_col = db[Config.MONGODB_COLLECTIONS["tool_summary_metrics"]]
        
        # Index on parameter_hash
        metrics_col.create_index("parameter_hash", background=True)
        logger.info("Created index on tool_summary_metrics.parameter_hash")
        
        logger.info("All indexes created successfully")
        
    except OperationFailure as e:
        logger.warning(f"Index creation failed (may already exist): {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating indexes: {str(e)}")
        raise


def drop_database():
    """Drop entire database (useful for development/testing only)."""
    try:
        client = get_database().client
        client.drop_database(Config.MONGODB_DB_NAME)
        logger.info(f"Dropped database: {Config.MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"Failed to drop database: {str(e)}")
        raise


def get_database_stats():
    """Get database statistics for monitoring."""
    try:
        db = get_database()
        stats = db.command("dbStats")
        return {
            "storage_size": stats.get("storageSize"),
            "data_size": stats.get("dataSize"),
            "collections": stats.get("collections")
        }
    except Exception as e:
        logger.error(f"Failed to get database stats: {str(e)}")
        return None