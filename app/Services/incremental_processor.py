"""Incremental report processing with MongoDB caching and local fallback."""

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
from app.Services.local_cache_manager import (
    load_results_from_local_cache,
    save_results_to_local_cache,
    get_cache_stats
)

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
    download_file_content_func,
    progress_callback=None
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
        progress_callback: Optional callback(current, total) to update UI during WER calculation
        
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
        "error_message": None,
        "db_errors": []
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
            logger.info("No previous processing found in MongoDB - checking local cache...")
            # Try local cache as fallback if MongoDB metadata not available
            local_cached_results = load_results_from_local_cache(year, month, language)
            if local_cached_results:
                logger.info(f"✅ Found {len(local_cached_results)} results in local JSON cache")
                
                # ===== Step 3: Get current file list from Google Drive =====
                logger.info("Fetching current file list from Google Drive (checking for new files)...")
                current_ai_files = list_srt_files_with_metadata(drive_service, ai_generated_folder_id)
                current_file_ids = [f['id'] for f in current_ai_files]
                logger.info(f"Found {len(current_file_ids)} files currently in AI_Generated_Files")
                
                # ===== Step 4: Get cached file IDs from cache results =====
                cached_file_ids_from_cache = [r.get('google_drive_file_id') for r in local_cached_results if r.get('google_drive_file_id')]
                logger.info(f"Local cache has {len(cached_file_ids_from_cache)} file IDs")
                
                # ===== Step 5: Check for new files =====
                new_file_ids, deleted_file_ids = identify_new_files(current_file_ids, cached_file_ids_from_cache)
                logger.info(f"Detected: {len(new_file_ids)} new files, {len(deleted_file_ids)} deleted files")
                
                # If no new/deleted files, return cache as-is
                if len(new_file_ids) == 0 and len(deleted_file_ids) == 0:
                    logger.info("No changes detected - returning cache as-is")
                    processing_info["status"] = "success"
                    processing_info["total_files"] = len(local_cached_results)
                    processing_info["cached_files"] = len(local_cached_results)
                    processing_info["newly_processed"] = 0
                    end_time = datetime.utcnow()
                    processing_info["processing_time_seconds"] = (end_time - start_time).total_seconds()
                    logger.info(f"Returning {len(local_cached_results)} cached results from local JSON cache")
                    return local_cached_results, processing_info
                
                # If new files exist, process them and merge with cache
                if len(new_file_ids) > 0:
                    logger.info(f"Processing {len(new_file_ids)} new files found since cache...")
                    
                    # Get original files
                    original_files = list_srt_files_with_metadata(drive_service, original_folder_id)
                    
                    # Process only new files
                    files_to_process = [f for f in current_ai_files if f['id'] in new_file_ids]
                    
                    new_wer_results = _calculate_wer_for_files(
                        files_to_process,
                        original_files,
                        drive_service,
                        build_ai_mapping_func,
                        match_original_with_ai_func,
                        download_file_content_func,
                        progress_callback=progress_callback
                    )
                    
                    # Merge new results with cached results
                    combined_results = merge_results(local_cached_results, new_wer_results, deleted_file_ids)
                    
                    logger.info(f"Merged {len(local_cached_results)} cached + {len(new_wer_results)} new = {len(combined_results)} total")
                    
                    # Save merged results back to cache
                    try:
                        save_results_to_local_cache(year, month, language, combined_results)
                        logger.info("✓ Merged results saved to local cache")
                    except Exception as cache_save_error:
                        logger.warning(f"Could not update local cache: {str(cache_save_error)}")
                    
                    processing_info["status"] = "success"
                    processing_info["total_files"] = len(combined_results)
                    processing_info["cached_files"] = len(local_cached_results)
                    processing_info["newly_processed"] = len(new_wer_results)
                    end_time = datetime.utcnow()
                    processing_info["processing_time_seconds"] = (end_time - start_time).total_seconds()
                    logger.info(f"Returning {len(combined_results)} merged results (cache + new)")
                    return combined_results, processing_info
        
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
                download_file_content_func,
                progress_callback=progress_callback  # Pass progress callback to track calculation
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
            save_result = save_wer_results(year, month, language, combined_results)
            logger.info(f"Save result: {save_result}")
            
            if not save_result.get('success'):
                error_msg = save_result.get('message', 'Unknown error')
                processing_info["db_errors"].append(f"MongoDB save failed: {error_msg}")
                logger.warning(f"Failed to save to MongoDB: {error_msg}, but will continue with local cache backup")
            
            # ===== ALWAYS save to local cache as backup (regardless of MongoDB success) =====
            logger.info(f"Saving {len(combined_results)} results to local JSON cache as backup...")
            try:
                local_cache_success = save_results_to_local_cache(year, month, language, combined_results)
                if local_cache_success:
                    logger.info("✅ Results saved to local cache successfully")
                else:
                    logger.warning("Could not save to local cache")
            except Exception as cache_error:
                logger.warning(f"Local cache backup failed: {str(cache_error)}")
            
            # Update metadata ONLY after WER results are confirmed saved
            # IMPORTANT: Accumulate file IDs cumulatively
            # 1. Start with previously cached IDs (base set of processed files)
            # 2. Add newly processed file IDs
            # 3. Remove any deleted file IDs
            
            tracked_file_ids = set(cached_file_ids or [])
            
            # Add file IDs from newly processed results
            for result in new_wer_results:
                if result.get('google_drive_file_id'):
                    tracked_file_ids.add(result['google_drive_file_id'])
            
            # Remove deleted files
            tracked_file_ids.difference_update(deleted_file_ids or [])
            
            # Validate: ensure all tracked IDs still exist in current files
            all_current_file_ids = set([f['id'] for f in current_ai_files])
            final_tracked_ids = list(tracked_file_ids & all_current_file_ids)
            
            logger.info(
                f"Metadata update: tracking {len(final_tracked_ids)} total files "
                f"(previously: {len(cached_file_ids)}, newly processed: {len(new_wer_results)}, deleted: {len(deleted_file_ids or [])})"
            )
            update_meta_result = update_processing_metadata(year, month, language, final_tracked_ids)
            
            if not update_meta_result.get('success'):
                error_msg = update_meta_result.get('message', 'Unknown error')
                processing_info["db_errors"].append(f"Metadata update failed: {error_msg}")
                logger.warning(f"Failed to update processing metadata: {error_msg}")
            
            # ===== Step 9: Update tool metrics =====
            tool_metrics_result = update_tool_summary_metrics(year, month, language, combined_results)
            if tool_metrics_result.get('success'):
                logger.info("Tool metrics updated")
            else:
                error_msg = tool_metrics_result.get('message', 'Unknown error')
                processing_info["db_errors"].append(f"Tool metrics update failed: {error_msg}")
                logger.warning(f"Could not update tool metrics: {error_msg}")
            
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
        
        # ===== FALLBACK LAYER 1: Try to return cached results from MongoDB =====
        logger.info("Fallback Layer 1: Attempting to retrieve MongoDB cached results...")
        try:
            cached_results = get_all_results_for_parameters(year, month, language)
            if cached_results:
                logger.info(f"✅ Fallback Layer 1 SUCCESS: Returning {len(cached_results)} MongoDB cached results")
                processing_info["status"] = "partial_success_mongodb_cache"
                processing_info["total_files"] = len(cached_results)
                return cached_results, processing_info
        except Exception as fallback1_error:
            logger.warning(f"Fallback Layer 1 failed: {str(fallback1_error)}")
        
        # ===== FALLBACK LAYER 2: Try to return cached results from local JSON cache =====
        logger.info("Fallback Layer 2: Attempting to retrieve local JSON cached results...")
        try:
            local_cached_results = load_results_from_local_cache(year, month, language)
            if local_cached_results:
                logger.info(f"✅ Fallback Layer 2 SUCCESS: Returning {len(local_cached_results)} local cached results")
                processing_info["status"] = "partial_success_local_cache"
                processing_info["total_files"] = len(local_cached_results)
                return local_cached_results, processing_info
        except Exception as fallback2_error:
            logger.warning(f"Fallback Layer 2 failed: {str(fallback2_error)}")
        
        # ===== FALLBACK LAYER 3: Fresh Calculation (process without caching) =====
        logger.info("Fallback Layer 3: Attempting fresh calculation without cached data...")
        try:
            # Get current files and process them fresh
            current_ai_files = list_srt_files_with_metadata(drive_service, ai_generated_folder_id)
            original_files = list_srt_files_with_metadata(drive_service, original_folder_id)
            
            logger.info(f"Fresh calculation: Found {len(current_ai_files)} AI files and {len(original_files)} original files")
            
            fresh_results = _calculate_wer_for_files(
                current_ai_files,
                original_files,
                drive_service,
                build_ai_mapping_func,
                match_original_with_ai_func,
                download_file_content_func,
                progress_callback=progress_callback  # Pass progress callback
            )
            
            if fresh_results:
                logger.info(f"✅ Fallback Layer 3 SUCCESS: Generated {len(fresh_results)} fresh results (without caching)")
                
                # Try to save to local cache for next time
                try:
                    save_results_to_local_cache(year, month, language, fresh_results)
                    logger.info("Fresh results also saved to local cache for offline access")
                except Exception as cache_save_error:
                    logger.warning(f"Could not save fresh results to local cache: {str(cache_save_error)}")
                
                processing_info["status"] = "fresh_calculation_no_cache"
                processing_info["total_files"] = len(fresh_results)
                processing_info["newly_processed"] = len(fresh_results)
                processing_info["cached_files"] = 0
                return fresh_results, processing_info
                
        except Exception as fallback3_error:
            logger.error(f"Fallback Layer 3 also failed: {str(fallback3_error)}", exc_info=True)
        
        # ===== ALL FALLBACKS EXHAUSTED =====
        logger.error("❌ All fallback layers exhausted - cannot generate report")
        processing_info["status"] = "critical_failure"
        processing_info["error_message"] = (
            f"Primary error: {str(e)}\n"
            "All fallback layers failed. "
            "Please check: 1) MongoDB connection, 2) Google Drive access, 3) File permissions"
        )
        return [], processing_info


def _calculate_wer_for_files(
    ai_files: List[Dict],
    original_files: List[Dict],
    drive_service,
    build_ai_mapping_func,
    match_original_with_ai_func,
    download_file_content_func,
    progress_callback=None
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
        progress_callback: Optional callback(current, total) to track progress
        
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
            logger.info("No matched file pairs found - no files to process for these parameters")
            return wer_results
        
        # Calculate WER for each pair
        total_pairs = len(matched_pairs)
        for pair_idx, pair in enumerate(matched_pairs):
            # Update progress
            if progress_callback:
                try:
                    progress_callback(pair_idx + 1, total_pairs)
                except Exception as cb_error:
                    logger.debug(f"Progress callback error: {str(cb_error)}")
            
            base_name = pair.get('base_name')
            original_file = pair.get('original_file')
            ai_versions = pair.get('ai_versions', [])
            
            # Download and parse original file
            try:
                original_content = download_file_content_func(drive_service, original_file['id'])
                original_text = parse_srt(original_content)
                if not original_text.strip():
                    logger.warning(f"Original file {base_name} parsed to empty text - skipping")
                    continue
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
                    
                    if not ai_text.strip():
                        logger.warning(f"AI file {base_name} ({ai_tool}) parsed to empty text - skipping")
                        continue
                    
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
    result_summary = {}
    for tool in summary:
        scores = summary[tool]['scores']
        result_summary[tool] = {
            'Average WER Score': sum(scores) / len(scores) if scores else 0,
            'Best WER Score': min(scores) if scores else 0,
            'Worst WER Score': max(scores) if scores else 0,
        }
    
    return result_summary