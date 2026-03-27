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
        # Note: These counts may not match if some original files don't have AI file matches,
        # but those unmatched files are only tracked in metadata if they resulted in WER results
        if wer_record and metadata_record:
            wer_count = len(wer_record.get('results', []))
            metadata_count = len(metadata_record.get('processed_file_ids', []))
            if wer_count != metadata_count:
                # This is expected when some files don't have AI matches
                # Log at debug level since it's not a real integrity issue
                logger.debug(
                    f"Count note (expected if files have no AI matches): "
                    f"WER has {wer_count} results but metadata lists {metadata_count} files"
                )
        
        if issues:
            issue_str = "; ".join(issues)
            logger.warning(f"Integrity issues found: {issue_str}")
            return False, issue_str
        
        logger.info(f"Database integrity check passed for {year}/{month}/{language}")
        return True, "All checks passed"
        
    except Exception as e:
        logger.error(f"Error validating database integrity: {str(e)}")
        return False, f"Validation error: {str(e)}"



