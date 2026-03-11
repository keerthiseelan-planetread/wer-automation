"""Incremental report processing with MongoDB caching."""

import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from app.database.db_operations import (
    get_parameter_hash,
    fetch_processed_file_ids,
    get_all_results_for_parameters,
    save_wer_results,
    update_processing_metadata,
    identify_new_files,
    merge_results,
    update_tool_summary_metrics
)
from app.database.db_validation import validate_db_integrity
from app.database.init_db import initialize_database
from app.drive.drive_utils import list_srt_files_with_metadata
from app.wer_engine.srt_parser import parse_srt
from app.wer_engine.wer_calculater import calculate_wer

logger = logging.getLogger(__name__)


def process_with_incremental_caching(
    year: int,
    month: str,
    language: str,
    drive_service,
    original_folder_id: str,
    ai_generated_folder_id: str,
    build_ai_mapping_func,
    match_original_with_ai_func,
    download_file_content_func
) -> Tuple[List[Dict], Dict]:
    """
    Process WER report with incremental caching logic.
    
    This is the main orchestration function that:
    1. Checks MongoDB for cached results
    2. Identifies new files added to AI_Generated_Files
    3. Processes only NEW files (not cached ones)
    4. Merges new results with cached results
    5. Saves everything back to MongoDB
    6. Returns combined results
    
    Args:
        year: Year value
        month: Month name
        language: Language name
        drive_service: Google Drive API service
        original_folder_id: Folder ID for Original_Files
        ai_generated_folder_id: Folder ID for AI_Generated_Files
        build_ai_mapping_func: Function to build AI tool mapping
        match_original_with_ai_func: Function to match original with AI files
        download_file_content_func: Function to download SRT content
        
    Returns:
        Tuple[List[Dict], Dict]: (combined_results, processing_info)
        
        processing_info contains:
        {
            "status": "success" or "error",
            "total_files": number of final results,
            "newly_processed": number of newly processed files,
            "cached_files": number of files from cache,
            "deleted_files": number of files marked as archived,
            "processing_time_seconds": time taken,
            "error_message": if status is "error"
        }
    """
    start_time = datetime.utcnow()
    processing_info = {
        "status": "success",
        "total_files": 0,
        "newly_processed": 0,
        "cached_files": 0,
        "deleted_files": 0,
        "processing_time_seconds": 0,
        "error_message": None
    }
    
    try:
        logger.info(f"Starting incremental processing for {year}/{month}/{language}")
        
        # ===== Step 0: Initialize database (if needed) =====
        try:
            initialize_database()
            logger.info("Database initialized")
        except Exception as e:
            logger.warning(f"Could not initialize database (may already exist): {str(e)}")
        
        # ===== Step 1: Validate database integrity =====
        is_valid, validation_msg = validate_db_integrity(year, month, language)
        if not is_valid:
            logger.warning(f"Database validation warning: {validation_msg}")
        
        # ===== Step 2: Fetch previous processing metadata =====
        logger.info("Checking for cached results...")
        cached_file_ids = fetch_processed_file_ids(year, month, language)
        
        if cached_file_ids:
            # Verify that actual WER results also exist - not just metadata
            existing_results_check = get_all_results_for_parameters(year, month, language)
            if not existing_results_check:
                logger.warning(
                    f"Metadata has {len(cached_file_ids)} file IDs but WER results are empty. "
                    "DB is in inconsistent state - forcing full reprocess."
                )
                cached_file_ids = []  # Reset so all files get reprocessed
            else:
                logger.info(f"Found {len(cached_file_ids)} previously processed files with {len(existing_results_check)} WER results")
        else:
            logger.info("No previous processing found - will process all files")
        
        # ===== Step 3: Get current file list from Google Drive =====
        logger.info("Fetching current file list from Google Drive...")
        current_ai_files = list_srt_files_with_metadata(drive_service, ai_generated_folder_id)
        current_file_ids = [f['id'] for f in current_ai_files]
        
        logger.info(f"Found {len(current_file_ids)} files currently in AI_Generated_Files")
        
        # ===== Step 4: Identify new vs deleted files =====
        new_file_ids, deleted_file_ids = identify_new_files(current_file_ids, cached_file_ids)
        
        logger.info(f"New files: {len(new_file_ids)}, Deleted files: {len(deleted_file_ids)}")
        
        # ===== Step 5: Decide processing strategy =====
        if not cached_file_ids or len(new_file_ids) > 0:
            # Either first time or new files added - need to process
            logger.info("Processing reports...")
            
            if not cached_file_ids:
                # First time - process all files
                logger.info("First-time processing - will process all files")
                files_to_process = current_ai_files
            else:
                # Incremental - process only new files
                logger.info(f"Incremental processing - processing {len(new_file_ids)} new files")
                files_to_process = [f for f in current_ai_files if f['id'] in new_file_ids]
            
            # Get original files
            original_files = list_srt_files_with_metadata(drive_service, original_folder_id)
            
            # Calculate WER for files to process
            new_wer_results = _calculate_wer_for_files(
                files_to_process,
                original_files,
                drive_service,
                build_ai_mapping_func,
                match_original_with_ai_func,
                download_file_content_func
            )
            
            logger.info(f"WER calculation returned {len(new_wer_results)} results")
            if new_wer_results:
                logger.info(f"Sample result: {new_wer_results[0]}")
            
            processing_info["newly_processed"] = len(new_wer_results)
            
            # ===== Step 6: Get existing cached results =====
            existing_results = get_all_results_for_parameters(year, month, language)
            processing_info["cached_files"] = len(existing_results)
            
            # ===== Step 7: Merge results =====
            logger.info("Merging cached and new results...")
            combined_results = merge_results(
                existing_results,
                new_wer_results,
                deleted_file_ids
            )
            
            logger.info(f"Merge complete: {len(existing_results)} existing + {len(new_wer_results)} new = {len(combined_results)} combined")
            
            # Count archived files
            archived_count = sum(1 for r in combined_results if r.get('file_status') == 'archived')
            processing_info["deleted_files"] = archived_count
            
            # ===== Step 8: Save to MongoDB =====
            logger.info(f"Saving {len(combined_results)} results to MongoDB...")
            save_success = save_wer_results(year, month, language, combined_results)
            logger.info(f"Save result: {save_success}")
            
            if not save_success:
                raise Exception("Failed to save WER results to MongoDB")
            
            # Update metadata ONLY after WER results are confirmed saved
            # Extract matched AI file IDs from the WER results (skip unmatched files)
            processed_ai_file_ids = list(set([
                result.get('file_id') for result in combined_results 
                if result.get('file_id') and result.get('file_status') != 'archived'
            ]))
            
            if not processed_ai_file_ids:
                # Fallback: if file_id not in results, use current_ai_files that were in files_to_process
                processed_ai_file_ids = [f['id'] for f in files_to_process]
            
            logger.info(f"Tracking {len(processed_ai_file_ids)} matched files for this batch")
            update_success = update_processing_metadata(year, month, language, processed_ai_file_ids)
            
            if not update_success:
                logger.warning("Failed to update processing metadata")
            
            # ===== Step 9: Update tool metrics =====
            try:
                update_tool_summary_metrics(year, month, language, combined_results)
                logger.info("Tool metrics updated")
            except Exception as e:
                logger.warning(f"Could not update tool metrics: {str(e)}")
            
        else:
            # No new files - just retrieve cached results
            logger.info("No new files detected - retrieving cached results only")
            combined_results = get_all_results_for_parameters(year, month, language)
            processing_info["cached_files"] = len(combined_results)
            processing_info["newly_processed"] = 0
        
        processing_info["total_files"] = len(combined_results)
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_info["processing_time_seconds"] = (end_time - start_time).total_seconds()
        
        logger.info(
            f"Processing complete: {processing_info['total_files']} total files, "
            f"{processing_info['newly_processed']} newly processed, "
            f"{processing_info['cached_files']} from cache"
        )
        
        return combined_results, processing_info
        
    except Exception as e:
        logger.error(f"Error in incremental processing: {str(e)}", exc_info=True)
        
        processing_info["status"] = "error"
        processing_info["error_message"] = str(e)
        
        # Fallback: Try to return cached results if available
        try:
            logger.info("Attempting to return cached results as fallback...")
            cached_results = get_all_results_for_parameters(year, month, language)
            if cached_results:
                logger.info(f"Returning {len(cached_results)} cached results")
                processing_info["status"] = "partial_success"
                processing_info["total_files"] = len(cached_results)
                return cached_results, processing_info
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}")
        
        return [], processing_info


def _calculate_wer_for_files(
    ai_files: List[Dict],
    original_files: List[Dict],
    drive_service,
    build_ai_mapping_func,
    match_original_with_ai_func,
    download_file_content_func
) -> List[Dict]:
    """
    Calculate WER for a specific set of files.
    
    Args:
        ai_files: List of AI-generated file objects to process
        original_files: List of original file objects
        drive_service: Google Drive API service
        build_ai_mapping_func: Function to build AI tool mapping
        match_original_with_ai_func: Function to match files
        download_file_content_func: Function to download content
        
    Returns:
        List[Dict]: WER calculation results
    """
    try:
        wer_results = []
        
        logger.info(f"Starting WER calculation for {len(ai_files)} AI files and {len(original_files)} original files")
        
        # Build AI mapping from files
        ai_mapping = build_ai_mapping_func(ai_files)
        logger.info(f"Built AI mapping: {len(ai_mapping)} AI tools")
        
        # Map original files with AI versions (CORRECT: two separate args, not a dict)
        matched_pairs = match_original_with_ai_func(original_files, ai_mapping)
        logger.info(f"Found {len(matched_pairs)} matched file pairs")
        
        if not matched_pairs:
            logger.warning("No matched file pairs found - check your Original and AI file naming")
            return wer_results
        # Calculate WER for each pair
        for pair in matched_pairs:
            base_name = pair.get('base_name')
            original_file = pair.get('original_file')
            ai_versions = pair.get('ai_versions', [])
            
            # Download and parse original file
            try:
                original_content = download_file_content_func(drive_service, original_file['id'])
                original_text = parse_srt(original_content)
            except Exception as e:
                logger.warning(f"Could not process original file {base_name}: {str(e)}")
                continue
            
            # Calculate WER for each AI version
            for ai_version in ai_versions:
                ai_tool = ai_version.get('ai_tool', 'unknown')
                ai_file_id = ai_version.get('file_id')
                
                try:
                    # Download and parse AI file
                    ai_content = download_file_content_func(drive_service, ai_file_id)
                    ai_text = parse_srt(ai_content)
                    
                    # Calculate WER - returns dict {"wer": score}
                    wer_result = calculate_wer(original_text, ai_text)
                    logger.debug(f"calculate_wer returned: {type(wer_result)} = {wer_result}")
                    
                    # Extract numeric wer_score - be very defensive
                    if isinstance(wer_result, dict):
                        wer_score = wer_result.get('wer', 0)
                    else:
                        wer_score = wer_result
                    
                    logger.debug(f"Extracted wer_score: {type(wer_score)} = {wer_score}")
                    
                    # Ensure it's a number
                    try:
                        wer_score = float(wer_score)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert WER score to float for {ai_tool}: {wer_score}")
                        continue
                    
                    # Create result record
                    result = {
                        "base_name": base_name,
                        "ai_tool": ai_tool,
                        "wer_score": wer_score,
                        "processed_timestamp": datetime.utcnow(),
                        "google_drive_file_id": ai_file_id,
                        "file_status": "current"
                    }
                    
                    wer_results.append(result)
                    # Safe logging - handle both dict and numeric wer_score
                    score_val = wer_score.get('wer', wer_score) if isinstance(wer_score, dict) else wer_score
                    try:
                        logger.info(f"Calculated WER: {base_name} + {ai_tool} = {float(score_val):.2f}%")
                    except:
                        logger.info(f"Calculated WER: {base_name} + {ai_tool} = {score_val}")
                    
                except Exception as e:
                    logger.warning(f"Could not calculate WER for {base_name} ({ai_tool}): {str(e)}")
                    continue
        
        logger.info(f"Calculated WER for {len(wer_results)} file pairs")
        return wer_results
        
    except Exception as e:
        logger.error(f"Error calculating WER for files: {str(e)}", exc_info=True)
        return []


def get_processing_summary(results: List[Dict]) -> Dict:
    """
    Generate summary statistics from results.
    
    Args:
        results: List of WER results
        
    Returns:
        Dict: Summary statistics by AI tool
    """
    summary = {}
    
    for result in results:
        if result.get('file_status') == 'archived':
            continue  # Skip archived files
        
        ai_tool = result.get('ai_tool', 'unknown')
        wer_score = result.get('wer_score', 0)
        
        # Handle dict-formatted scores (defensive)
        if isinstance(wer_score, dict):
            wer_score = wer_score.get('wer', 0)
        
        try:
            wer_score = float(wer_score)
        except (ValueError, TypeError):
            logger.warning(f"Invalid WER score for {ai_tool}: {wer_score}")
            continue
        
        if ai_tool not in summary:
            summary[ai_tool] = {
                'scores': [],
                'count': 0
            }
        
        summary[ai_tool]['scores'].append(wer_score)
        summary[ai_tool]['count'] += 1
    
    # Calculate statistics
    for tool in summary:
        scores = summary[tool]['scores']
        summary[tool]['average'] = sum(scores) / len(scores) if scores else 0
        summary[tool]['best'] = min(scores) if scores else 0
        summary[tool]['worst'] = max(scores) if scores else 0
        del summary[tool]['scores']  # Remove raw scores from output
    
    return summary