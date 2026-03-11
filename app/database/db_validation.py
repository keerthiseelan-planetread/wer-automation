"""Database validation and integrity checks."""

import logging
from typing import Dict, List, Tuple
from app.database.mongo_connection import get_database
from app.database.db_operations import get_parameter_hash
from app.config import Config

logger = logging.getLogger(__name__)


def validate_db_integrity(year: int, month: str, language: str) -> Tuple[bool, str]:
    """
    Validate database integrity for given parameters.
    
    Args:
        year: Year value
        month: Month name
        language: Language name
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    try:
        db = get_database()
        wer_results_col = db[Config.MONGODB_COLLECTIONS["wer_results"]]
        metadata_col = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]
        
        param_hash = get_parameter_hash(year, month, language)
        
        # Check if wer_results exists
        wer_record = wer_results_col.find_one({"parameter_hash": param_hash})
        metadata_record = metadata_col.find_one({"parameter_hash": param_hash})
        
        if not wer_record and not metadata_record:
            return True, "No records found (fresh start)"
        
        issues = []
        
        # Validate wer_results structure
        if wer_record:
            if 'results' not in wer_record:
                issues.append("WER record missing 'results' field")
            elif not isinstance(wer_record['results'], list):
                issues.append("WER results should be a list")
            
            if 'total_files_processed' not in wer_record:
                issues.append("Missing 'total_files_processed' counter")
            elif len(wer_record.get('results', [])) != wer_record['total_files_processed']:
                issues.append("Mismatch between results count and counter")
            
            # Validate each result has required fields
            for idx, result in enumerate(wer_record.get('results', [])):
                missing_fields = []
                for field in ['base_name', 'ai_tool', 'wer_score']:
                    if field not in result:
                        missing_fields.append(field)
                
                if missing_fields:
                    issues.append(f"Result {idx} missing fields: {missing_fields}")
        
        # Validate metadata structure
        if metadata_record:
            if 'processed_file_ids' not in metadata_record:
                issues.append("Metadata missing 'processed_file_ids' field")
            elif not isinstance(metadata_record['processed_file_ids'], list):
                issues.append("processed_file_ids should be a list")
        
        # Check consistency: file count in wer_record should match processed_file_ids count
        if wer_record and metadata_record:
            wer_count = len(wer_record.get('results', []))
            metadata_count = len(metadata_record.get('processed_file_ids', []))
            if wer_count != metadata_count:
                issues.append(f"Count mismatch: WER has {wer_count} results but metadata lists {metadata_count} files")
        
        if issues:
            issue_str = "; ".join(issues)
            logger.warning(f"Integrity issues found: {issue_str}")
            return False, issue_str
        
        logger.info(f"Database integrity check passed for {year}/{month}/{language}")
        return True, "All checks passed"
        
    except Exception as e:
        logger.error(f"Error validating database integrity: {str(e)}")
        return False, f"Validation error: {str(e)}"


def verify_cached_results_sample(year: int, month: str, language: str, 
                                 sample_size: int = 5) -> Tuple[bool, Dict]:
    """
    Spot-check sample of cached results (lightweight verification).
    
    Args:
        year: Year value
        month: Month name
        language: Language name
        sample_size: Number of results to sample
        
    Returns:
        Tuple[bool, Dict]: (is_valid, results_info)
    """
    try:
        db = get_database()
        wer_results_col = db[Config.MONGODB_COLLECTIONS["wer_results"]]
        
        param_hash = get_parameter_hash(year, month, language)
        record = wer_results_col.find_one({"parameter_hash": param_hash})
        
        if not record:
            return True, {"message": "No records to verify"}
        
        results = record.get('results', [])
        stats = {
            "total_results": len(results),
            "wer_scores": [],
            "ai_tools": set(),
            "files": set(),
            "issues": []
        }
        
        # Sample results
        import random
        sample = random.sample(results, min(sample_size, len(results)))
        
        for result in sample:
            wer_score = result.get('wer_score')
            ai_tool = result.get('ai_tool')
            base_name = result.get('base_name')
            file_status = result.get('file_status', 'unknown')
            
            # Validate wer_score range
            if wer_score is not None:
                if not (0 <= wer_score <= 100):
                    stats["issues"].append(f"{base_name}: WER score {wer_score} out of valid range")
                stats["wer_scores"].append(wer_score)
            
            stats["ai_tools"].add(ai_tool)
            stats["files"].add(base_name)
        
        stats["ai_tools"] = list(stats["ai_tools"])
        stats["files"] = list(stats["files"])
        
        is_valid = len(stats["issues"]) == 0
        
        return is_valid, stats
        
    except Exception as e:
        logger.error(f"Error verifying cached results: {str(e)}")
        return False, {"error": str(e)}


def get_database_health() -> Dict:
    """
    Get overall database health metrics.
    
    Returns:
        Dict: Health information including collection counts and sizes
    """
    try:
        db = get_database()
        
        health_info = {
            "status": "healthy",
            "collections": {}
        }
        
        for collection_name in Config.MONGODB_COLLECTIONS.values():
            col = db[collection_name]
            count = col.count_documents({})
            
            # Get collection size
            stats = db.command("collStats", collection_name)
            size_mb = stats.get('size', 0) / (1024 * 1024)
            
            health_info["collections"][collection_name] = {
                "document_count": count,
                "size_mb": round(size_mb, 2)
            }
        
        logger.info(f"Database health: {health_info}")
        return health_info
        
    except Exception as e:
        logger.error(f"Error getting database health: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}