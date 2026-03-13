"""Local JSON cache manager for offline/fallback support."""

import json
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path("app/assets/cache")


def get_cache_directory():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def get_parameter_hash(year: int, month: str, language: str) -> str:
    """Generate hash for parameters (same as MongoDB version)."""
    param_string = f"{year}_{month}_{language}"
    return hashlib.sha256(param_string.encode()).hexdigest()


def get_cache_file_path(year: int, month: str, language: str) -> Path:
    """Get local cache file path for given parameters."""
    param_hash = get_parameter_hash(year, month, language)
    cache_dir = get_cache_directory()
    return cache_dir / f"{param_hash}_results.json"


def save_results_to_local_cache(year: int, month: str, language: str, 
                                results: List[Dict]) -> bool:
    """
    Save WER results to local JSON cache as fallback.
    
    Args:
        year: Year value
        month: Month name
        language: Language name
        results: List of WER result dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cache_file = get_cache_file_path(year, month, language)
        
        # Convert any non-serializable objects to strings
        serializable_results = []
        for result in results:
            clean_result = {}
            for key, value in result.items():
                # Handle datetime objects
                if isinstance(value, datetime):
                    clean_result[key] = value.isoformat()
                # Handle bytes
                elif isinstance(value, bytes):
                    clean_result[key] = value.decode('utf-8', errors='ignore')
                # Handle BSON types (MongoDB specific)
                elif hasattr(value, '__dict__') and '$' in str(type(value)):
                    clean_result[key] = str(value)
                else:
                    clean_result[key] = value
            serializable_results.append(clean_result)
        
        cache_data = {
            "parameter_hash": get_parameter_hash(year, month, language),
            "year": year,
            "month": month,
            "language": language,
            "results": serializable_results,
            "cached_at": datetime.utcnow().isoformat(),
            "total_files_cached": len(serializable_results)
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(serializable_results)} results to local cache: {cache_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving to local cache: {str(e)}")
        return False


def load_results_from_local_cache(year: int, month: str, language: str) -> Optional[List[Dict]]:
    """
    Load WER results from local JSON cache.
    
    Args:
        year: Year value
        month: Month name
        language: Language name
        
    Returns:
        List[Dict]: Results if found, None otherwise
    """
    try:
        cache_file = get_cache_file_path(year, month, language)
        
        if not cache_file.exists():
            logger.debug(f"Local cache not found: {cache_file}")
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        results = cache_data.get('results', [])
        cached_at = cache_data.get('cached_at', 'unknown')
        
        logger.info(f"Loaded {len(results)} results from local cache (cached at: {cached_at})")
        return results
        
    except Exception as e:
        logger.error(f"Error loading from local cache: {str(e)}")
        return None


def clear_old_cache(max_age_days: int = 30) -> int:
    """
    Clean up cache files older than specified days.
    
    Args:
        max_age_days: Maximum age in days
        
    Returns:
        int: Number of files deleted
    """
    try:
        cache_dir = get_cache_directory()
        if not cache_dir.exists():
            return 0
        
        deleted_count = 0
        now = datetime.utcnow().timestamp()
        
        for cache_file in cache_dir.glob("*_results.json"):
            file_age_days = (now - cache_file.stat().st_mtime) / 86400
            if file_age_days > max_age_days:
                cache_file.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old cache file: {cache_file}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old cache files")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error clearing old cache: {str(e)}")
        return 0


def get_cache_stats() -> Dict:
    """Get statistics about local cache."""
    try:
        cache_dir = get_cache_directory()
        cache_files = list(cache_dir.glob("*_results.json"))
        
        total_size_mb = sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
        
        return {
            "cache_directory": str(cache_dir),
            "total_files": len(cache_files),
            "total_size_mb": round(total_size_mb, 2),
            "status": "healthy" if len(cache_files) > 0 else "empty"
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return {"status": "error", "message": str(e)}
