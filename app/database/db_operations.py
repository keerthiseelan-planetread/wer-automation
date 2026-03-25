# """MongoDB database operations for WER calculations."""

# import logging
# import hashlib
# from datetime import datetime
# from typing import List, Dict, Optional, Tuple
# from pymongo import ASCENDING, DESCENDING
# from pymongo.errors import DuplicateKeyError
# from app.database.mongo_connection import get_database
# from app.config import Config

# logger = logging.getLogger(__name__)


# def get_parameter_hash(year: int, month: str, language: str) -> str:
#     """
#     Generate a unique hash for parameter combination.
    
#     Args:
#         year: Year value
#         month: Month name
#         language: Language name
        
#     Returns:
#         str: SHA256 hash of parameters
#     """
#     param_string = f"{year}_{month}_{language}"
#     return hashlib.sha256(param_string.encode()).hexdigest()


# def fetch_processed_file_ids(year: int, month: str, language: str) -> List[str]:
#     """
#     Fetch list of already-processed Google Drive file IDs.
    
#     Args:
#         year: Year value
#         month: Month name
#         language: Language name
        
#     Returns:
#         List[str]: List of processed file IDs, empty if no record exists
#     """
#     try:
#         db = get_database()
#         metadata_col = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]
        
#         param_hash = get_parameter_hash(year, month, language)
#         record = metadata_col.find_one({"parameter_hash": param_hash})
        
#         if record:
#             logger.info(f"Found {len(record.get('processed_file_ids', []))} processed files for {year}/{month}/{language}")
#             return record.get('processed_file_ids', [])
        
#         logger.info(f"No previous processing found for {year}/{month}/{language}")
#         return []
        
#     except Exception as e:
#         logger.error(f"Error fetching processed file IDs: {str(e)}")
#         return []


# def save_wer_results(year: int, month: str, language: str, 
#                     wer_results_list: List[Dict]) -> bool:
#     """
#     Save or update WER results in MongoDB.
    
#     Args:
#         year: Year value
#         month: Month name
#         language: Language name
#         wer_results_list: List of WER calculation results
#                          Format: [{"base_name": "...", "ai_tool": "...", 
#                                    "wer_score": 15.23, ...}, ...]
        
#     Returns:
#         bool: True if successful, False otherwise
#     """
#     try:
#         db = get_database()
#         wer_results_col = db[Config.MONGODB_COLLECTIONS["wer_results"]]
        
#         param_hash = get_parameter_hash(year, month, language)
        
#         # Add processed timestamp to each result if not present
#         for result in wer_results_list:
#             if 'processed_timestamp' not in result:
#                 result['processed_timestamp'] = datetime.utcnow()
#             if 'file_status' not in result:
#                 result['file_status'] = 'current'
#             # Normalize ai_tool to Title Case for consistency
#             if 'ai_tool' in result:
#                 result['ai_tool'] = result['ai_tool'].lower().title()
        
#         wer_doc = {
#             "parameter_hash": param_hash,
#             "year": year,
#             "month": month,
#             "language": language,
#             "results": wer_results_list,
#             "total_files_processed": len(wer_results_list),
#             "last_updated": datetime.utcnow(),
#             "created_at": datetime.utcnow()
#         }
        
#         # Use replace_one with upsert to save or update
#         result = wer_results_col.replace_one(
#             {"parameter_hash": param_hash},
#             wer_doc,
#             upsert=True
#         )
        
#         if result.upserted_id:
#             logger.info(f"Created new WER result document for {year}/{month}/{language}")
#         else:
#             logger.info(f"Updated WER result document for {year}/{month}/{language}")
        
#         return {"success": True, "message": None}
        
#     except Exception as e:
#         error_msg = str(e)
#         logger.error(f"Error saving WER results: {error_msg}")
#         return {"success": False, "message": error_msg}


# def merge_results(existing_results: List[Dict], new_results: List[Dict],
#                  deleted_file_ids: List[str] = None) -> List[Dict]:
#     """
#     Merge new WER calculations with existing cached results.
    
#     Args:
#         existing_results: Results already in database
#         new_results: Newly calculated results
#         deleted_file_ids: File IDs that were deleted (to mark as archived)
        
#     Returns:
#         List[Dict]: Merged results combining existing and new
#     """
#     try:
#         # Create dict for fast lookup of new results
#         new_results_dict = {
#             (r['base_name'], r['ai_tool']): r 
#             for r in new_results
#         }
        
#         merged = []
        
#         # Keep existing results that weren't deleted
#         for result in existing_results:
#             if result.get('google_drive_file_id') in (deleted_file_ids or []):
#                 # Mark as archived if file was deleted
#                 result['file_status'] = 'archived'
#                 merged.append(result)
#             else:
#                 # Check if this result was recalculated (new calculation)
#                 key = (result['base_name'], result['ai_tool'])
#                 if key in new_results_dict:
#                     # Use the new calculation
#                     merged.append(new_results_dict[key])
#                     del new_results_dict[key]
#                 else:
#                     # Keep existing result
#                     merged.append(result)
        
#         # Add any remaining new results that weren't in existing
#         merged.extend(new_results_dict.values())
        
#         logger.info(f"Merged results: kept {len(existing_results)} existing, added {len(new_results_dict)} new")
#         return merged
        
#     except Exception as e:
#         logger.error(f"Error merging results: {str(e)}")
#         return existing_results + new_results


# def get_all_results_for_parameters(year: int, month: str, language: str) -> List[Dict]:
#     """
#     Fetch all WER results for given parameters from database.
    
#     Args:
#         year: Year value
#         month: Month name
#         language: Language name
        
#     Returns:
#         List[Dict]: List of WER results, empty list if not found
#     """
#     try:
#         db = get_database()
#         wer_results_col = db[Config.MONGODB_COLLECTIONS["wer_results"]]
        
#         param_hash = get_parameter_hash(year, month, language)
#         record = wer_results_col.find_one({"parameter_hash": param_hash})
        
#         if record:
#             logger.info(f"Retrieved {len(record.get('results', []))} results for {year}/{month}/{language}")
#             return record.get('results', [])
        
#         logger.info(f"No results found for {year}/{month}/{language}")
#         return []
        
#     except Exception as e:
#         logger.error(f"Error fetching results: {str(e)}")
#         return []


# def update_processing_metadata(year: int, month: str, language: str, 
#                                file_ids: List[str]) -> bool:
#     """
#     Update metadata tracking which files have been processed.
    
#     Args:
#         year: Year value
#         month: Month name
#         language: Language name
#         file_ids: List of Google Drive file IDs that have been processed
        
#     Returns:
#         bool: True if successful, False otherwise
#     """
#     try:
#         db = get_database()
#         metadata_col = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]
        
#         param_hash = get_parameter_hash(year, month, language)
        
#         metadata_doc = {
#             "parameter_hash": param_hash,
#             "year": year,
#             "month": month,
#             "language": language,
#             "processed_file_ids": file_ids,
#             "last_sync_timestamp": datetime.utcnow(),
#             "last_drive_folder_scan": datetime.utcnow()
#         }
        
#         result = metadata_col.replace_one(
#             {"parameter_hash": param_hash},
#             metadata_doc,
#             upsert=True
#         )
        
#         logger.info(f"Updated metadata: {len(file_ids)} processed files for {year}/{month}/{language}")
#         return {"success": True, "message": None}
        
#     except Exception as e:
#         error_msg = str(e)
#         logger.error(f"Error updating processing metadata: {error_msg}")
#         return {"success": False, "message": error_msg}


# def identify_new_files(current_file_ids: List[str], processed_file_ids: List[str]) -> Tuple[List[str], List[str]]:
#     """
#     Identify new and deleted files by comparing current vs processed.
    
#     Args:
#         current_file_ids: Current file IDs from Google Drive
#         processed_file_ids: Previously processed file IDs from database
        
#     Returns:
#         Tuple[List[str], List[str]]: (new_file_ids, deleted_file_ids)
#     """
#     current_set = set(current_file_ids)
#     processed_set = set(processed_file_ids)
    
#     new_files = list(current_set - processed_set)
#     deleted_files = list(processed_set - current_set)
    
#     logger.info(f"File comparison: {len(new_files)} new, {len(deleted_files)} deleted, {len(current_set & processed_set)} unchanged")
    
#     return new_files, deleted_files


# def update_tool_summary_metrics(year: int, month: str, language: str, 
#                                wer_results: List[Dict]) -> bool:
#     """
#     Calculate and store tool-wise summary metrics (optional, for future use).
    
#     Args:
#         year: Year value
#         month: Month name
#         language: Language name
#         wer_results: List of WER results to calculate metrics from
        
#     Returns:
#         bool: True if successful
#     """
#     try:
#         db = get_database()
#         metrics_col = db[Config.MONGODB_COLLECTIONS["tool_summary_metrics"]]
        
#         # Calculate metrics per AI tool
#         tool_metrics = {}
        
#         for result in wer_results:
#             ai_tool = result.get('ai_tool', 'unknown')
#             wer_score = result.get('wer_score', 0)
            
#             # Handle dict-formatted scores (defensive)
#             if isinstance(wer_score, dict):
#                 wer_score = wer_score.get('wer', 0)
            
#             # Skip archived files
#             if result.get('file_status') == 'archived':
#                 continue
            
#             try:
#                 wer_score = float(wer_score)
#             except (ValueError, TypeError):
#                 logger.warning(f"Invalid WER score for {ai_tool}: {wer_score}")
#                 continue
            
#             if ai_tool not in tool_metrics:
#                 tool_metrics[ai_tool] = {
#                     'scores': [],
#                     'files_count': 0
#                 }
            
#             tool_metrics[ai_tool]['scores'].append(wer_score)
#             tool_metrics[ai_tool]['files_count'] += 1
        
#         # Calculate averages
#         metrics_summary = {}
#         for tool, data in tool_metrics.items():
#             scores = data['scores']
#             metrics_summary[tool] = {
#                 'average_wer': sum(scores) / len(scores) if scores else 0,
#                 'best_wer': min(scores) if scores else 0,
#                 'worst_wer': max(scores) if scores else 0,
#                 'files_count': data['files_count']
#             }
        
#         param_hash = get_parameter_hash(year, month, language)
        
#         metrics_doc = {
#             "parameter_hash": param_hash,
#             "year": year,
#             "month": month,
#             "language": language,
#             "tool_metrics": metrics_summary,
#             "updated_at": datetime.utcnow()
#         }
        
#         metrics_col.replace_one(
#             {"parameter_hash": param_hash},
#             metrics_doc,
#             upsert=True
#         )
        
#         logger.info(f"Updated tool metrics for {year}/{month}/{language}")
#         return {"success": True, "message": None}
        
#     except Exception as e:
#         error_msg = str(e)
#         logger.error(f"Error updating tool metrics: {error_msg}")
#         return {"success": False, "message": error_msg}


# def get_tool_summary_metrics(year: int, month: str, language: str) -> Dict:
#     """
#     Fetch tool summary metrics for given parameters.
    
#     Args:
#         year: Year value
#         month: Month name
#         language: Language name
        
#     Returns:
#         Dict: Tool metrics or empty dict if not found
#     """
#     try:
#         db = get_database()
#         metrics_col = db[Config.MONGODB_COLLECTIONS["tool_summary_metrics"]]
        
#         param_hash = get_parameter_hash(year, month, language)
#         record = metrics_col.find_one({"parameter_hash": param_hash})
        
#         if record:
#             return record.get('tool_metrics', {})
        
#         return {}
        
#     except Exception as e:
#         logger.error(f"Error fetching tool metrics: {str(e)}")
#         return {}

import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Tuple
from app.database.mongo_connection import get_database
from app.config import Config

logger = logging.getLogger(__name__)

# ----------------------------
# PARAM HASH
# ----------------------------
def get_parameter_hash(year: int, month: str, language: str) -> str:
    return hashlib.sha256(f"{year}_{month}_{language}".encode()).hexdigest()


# ----------------------------
# FETCH METADATA
# ----------------------------
def fetch_processed_file_ids(year: int, month: str, language: str) -> List[str]:
    db = get_database()
    col = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]

    doc = col.find_one({
        "parameter_hash": get_parameter_hash(year, month, language)
    })

    return doc.get("processed_file_ids", []) if doc else []


# ----------------------------
# GET RESULTS
# ----------------------------
def get_wer_results(year: int, month: str, language: str) -> List[Dict]:
    db = get_database()
    col = db[Config.MONGODB_COLLECTIONS["wer_results"]]

    doc = col.find_one({
        "parameter_hash": get_parameter_hash(year, month, language)
    })

    return doc.get("results", []) if doc else []


# ----------------------------
# IDENTIFY FILES
# ----------------------------
def identify_new_files(current: List[str], processed: List[str]) -> Tuple[List[str], List[str]]:
    return list(set(current) - set(processed)), list(set(processed) - set(current))


# ----------------------------
# MERGE RESULTS (🔥 FIXED)
# ----------------------------
def merge_results(existing: List[Dict], new: List[Dict], deleted_ids: List[str] = None) -> List[Dict]:
    deleted_ids = deleted_ids or []

    # ✅ Use file_id as unique key
    existing_dict = {
        r.get("google_drive_file_id"): r
        for r in existing if r.get("google_drive_file_id")
    }

    new_dict = {
        r.get("google_drive_file_id"): r
        for r in new if r.get("google_drive_file_id")
    }

    merged = []

    # ✅ Handle existing
    for file_id, old in existing_dict.items():

        # 🔴 If deleted → archive
        if file_id in deleted_ids:
            old["file_status"] = "archived"
            merged.append(old)

        # 🟢 If updated → replace
        elif file_id in new_dict:
            merged.append(new_dict[file_id])
            del new_dict[file_id]

        # ⚪ If unchanged → keep
        else:
            merged.append(old)

    # ✅ Add remaining new
    merged.extend(new_dict.values())

    return merged


# ----------------------------
# SAVE RESULTS (🔥 DUP FIX)
# ----------------------------
def save_wer_results(year: int, month: str, language: str, wer_results_list: List[Dict]):
    try:
        db = get_database()
        col = db[Config.MONGODB_COLLECTIONS["wer_results"]]

        param_hash = get_parameter_hash(year, month, language)
        now = datetime.utcnow()

        existing = col.find_one({"parameter_hash": param_hash})

        # ✅ Normalize data
        for r in wer_results_list:
            r.setdefault("processed_timestamp", now)
            r.setdefault("file_status", "current")
            r["ai_tool"] = r.get("ai_tool", "").lower().title()

        # 🔥 FIX: handle empty file_id
        unique = {}
        for r in wer_results_list:
            file_id = r.get("google_drive_file_id")

            # ✅ fallback unique key if empty
            key = file_id if file_id else str(id(r))

            unique[key] = r

        wer_results_list = list(unique.values())

        # 🚨 Prevent saving empty data
        if not wer_results_list:
            return {"success": False, "message": "No valid results to save"}

        doc = {
            "parameter_hash": param_hash,
            "year": year,
            "month": month,
            "language": language,
            "results": wer_results_list,
            "total_files_processed": len(wer_results_list),
            "last_updated": now,
            "created_at": existing.get("created_at", now) if existing else now
        }

        col.replace_one({"parameter_hash": param_hash}, doc, upsert=True)

        print("✅ FINAL SAVED LIST:", wer_results_list)

        return {"success": True}

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error saving WER results: {error_msg}")
        return {"success": False, "message": error_msg}


def delete_empty_results(year: int, month: str, language: str) -> bool:
    """
    Delete WER result document if it contains 0 files processed.
    Used to clean up empty folder results that shouldn't be stored.
    
    Args:
        year: Year value
        month: Month name
        language: Language name
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_database()
        wer_results_col = db[Config.MONGODB_COLLECTIONS["wer_results"]]
        
        param_hash = get_parameter_hash(year, month, language)
        
        # Delete the document if total_files_processed is 0
        result = wer_results_col.delete_one({
            "parameter_hash": param_hash,
            "total_files_processed": 0
        })
        
        if result.deleted_count > 0:
            logger.info(f"Deleted empty result document for {year}/{month}/{language}")
            return True
        
        return True  # No document to delete is also success
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting empty result: {error_msg}")
        return False


def merge_results(existing_results: List[Dict], new_results: List[Dict],
                 deleted_file_ids: List[str] = None) -> List[Dict]:
    """
    Merge new WER calculations with existing cached results.
    
    Args:
        existing_results: Results already in database
        new_results: Newly calculated results
        deleted_file_ids: File IDs that were deleted (to mark as archived)
        
    Returns:
        List[Dict]: Merged results combining existing and new
    """
    try:
        # Create dict for fast lookup of new results
        new_results_dict = {
            (r['base_name'], r['ai_tool']): r 
            for r in new_results
        }
        
        merged = []
        
        # Keep existing results that weren't deleted
        for result in existing_results:
            if result.get('google_drive_file_id') in (deleted_file_ids or []):
                # Mark as archived if file was deleted
                result['file_status'] = 'archived'
                merged.append(result)
            else:
                # Check if this result was recalculated (new calculation)
                key = (result['base_name'], result['ai_tool'])
                if key in new_results_dict:
                    # Use the new calculation
                    merged.append(new_results_dict[key])
                    del new_results_dict[key]
                else:
                    # Keep existing result
                    merged.append(result)
        
        # Add any remaining new results that weren't in existing
        merged.extend(new_results_dict.values())
        
        logger.info(f"Merged results: kept {len(existing_results)} existing, added {len(new_results_dict)} new")
        return merged
        
    except Exception as e:
        logger.error(f"Error merging results: {str(e)}")
        return existing_results + new_results


def get_all_results_for_parameters(year: int, month: str, language: str) -> List[Dict]:
    """
    Fetch all WER results for given parameters from database.
    
    Args:
        year: Year value
        month: Month name
        language: Language name
        
    Returns:
        List[Dict]: List of WER results, empty list if not found
    """
        logger.error(f"Error saving results: {str(e)}")
        return {"success": False, "message": str(e)}
    
    
# ----------------------------
# UPDATE METADATA
# ----------------------------
def update_processing_metadata(year: int, month: str, language: str, file_ids: List[str]):
    try:
        db = get_database()
        col = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]

        now = datetime.utcnow()
        param_hash = get_parameter_hash(year, month, language)
        existing = col.find_one({"parameter_hash": param_hash})

        doc = {
            "parameter_hash": param_hash,
            "year": year,
            "month": month,
            "language": language,
            "processed_file_ids": list(set(file_ids)),  # remove duplicates
            "last_sync_timestamp": now,
            "last_drive_folder_scan": now,
            "created_at": existing.get("created_at", now) if existing else now
        }

        col.replace_one({"parameter_hash": param_hash}, doc, upsert=True)

        return {"success": True}

    except Exception as e:
        logger.error(f"Error updating metadata: {str(e)}")
        return {"success": False, "message": str(e)}


# ----------------------------
# DELETE EMPTY RESULTS
# ----------------------------
def delete_empty_results(year: int, month: str, language: str) -> bool:
    try:
        db = get_database()
        col = db[Config.MONGODB_COLLECTIONS["wer_results"]]

        result = col.delete_one({
            "parameter_hash": get_parameter_hash(year, month, language),
            "total_files_processed": 0
        })

        return True

    except Exception as e:
        logger.error(f"Error deleting empty results: {str(e)}")
        return False


# ----------------------------
# TOOL METRICS (AUTO CALC)
# ----------------------------
def update_tool_summary_metrics(year: int, month: str, language: str, results: List[Dict]):
    try:
        db = get_database()
        col = db[Config.MONGODB_COLLECTIONS["tool_summary_metrics"]]

        tool_data = {}

        for r in results:
            if r.get("file_status") == "archived":
                continue

            tool = r.get("ai_tool", "Unknown")
            wer = float(r.get("wer_score", 0))

            if tool not in tool_data:
                tool_data[tool] = []

            tool_data[tool].append(wer)

        summary = {}

        for tool, scores in tool_data.items():
            summary[tool] = {
                "average_wer": sum(scores) / len(scores),
                "best_wer": min(scores),
                "worst_wer": max(scores),
                "files_count": len(scores)
            }

        col.replace_one(
            {"parameter_hash": get_parameter_hash(year, month, language)},
            {
                "parameter_hash": get_parameter_hash(year, month, language),
                "year": year,
                "month": month,
                "language": language,
                "tool_metrics": summary,
                "updated_at": datetime.utcnow()
            },
            upsert=True
        )

        return {"success": True}

    except Exception as e:
        logger.error(f"Error updating metrics: {str(e)}")
        return {"success": False, "message": str(e)}  
# ----------------------------
# GET METADATA
# ----------------------------
def get_processing_metadata(year: int, month: str, language: str) -> Dict:
    db = get_database()
    col = db[Config.MONGODB_COLLECTIONS["processing_metadata"]]

    doc = col.find_one({
        "parameter_hash": get_parameter_hash(year, month, language)
    })

    if doc:
        return {
            "processed_file_ids": doc.get("processed_file_ids", []),
            "last_sync_timestamp": doc.get("last_sync_timestamp"),
            "last_drive_folder_scan": doc.get("last_drive_folder_scan")
        }

    return {}
# ----------------------------
# GET TOOL METRICS
# ----------------------------
def get_tool_summary_metrics(year: int, month: str, language: str) -> Dict:
    db = get_database()
    col = db[Config.MONGODB_COLLECTIONS["tool_summary_metrics"]]

    doc = col.find_one({
        "parameter_hash": get_parameter_hash(year, month, language)
    })

    return doc.get("tool_metrics", {}) if doc else {}