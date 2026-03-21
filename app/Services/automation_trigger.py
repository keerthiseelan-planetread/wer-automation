"""Automation trigger that processes all available Google Drive folders."""

import logging
from datetime import datetime
from typing import Dict, List, Tuple
from app.database.db_operations import delete_empty_results

logger = logging.getLogger(__name__)


def get_all_subfolders(service, parent_id: str) -> List[Dict]:
    """
    Get all subfolders within a parent folder.
    
    Args:
        service: Google Drive API service
        parent_id: Parent folder ID
        
    Returns:
        List of folder dictionaries with 'id' and 'name' keys
    """
    try:
        query = (
            f"'{parent_id}' in parents "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false"
        )
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1000
        ).execute()
        
        return results.get('files', [])
    except Exception as e:
        logger.error(f"Error listing subfolders in {parent_id}: {str(e)}")
        return []


def run_all_folders() -> Dict:
    """
    Automatically process all available Google Drive folders.
    
    This function:
    1. Lists all Years in the root folder
    2. For each Year, lists all Months
    3. For each Month, lists all Languages
    4. For each Language, calls process_with_incremental_caching
    5. Logs progress and results
    
    Returns:
        dict: Summary of automation execution with counts and timing
    """
    try:
        from app.config import Config
        from app.drive.drive_service import get_drive_service
        from app.drive.drive_utils import find_folder, list_srt_files
        from app.Services.incremental_processor import process_with_incremental_caching
        from app.Services.file_matcher import build_ai_mapping, match_original_with_ai
        from app.drive.drive_utils import download_file_content
        
        # Initialize
        service = get_drive_service()
        root_id = Config.GOOGLE_DRIVE_ROOT_ID
        start_time = datetime.now()
        
        stats = {
            'total_folders_processed': 0,
            'successful_folders': 0,
            'failed_folders': 0,
            'errors': [],
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': None,
            'duration_seconds': 0
        }
        
        logger.info(f"Starting automation trigger at {start_time}")
        logger.info(f"Root folder ID: {root_id}")
        
        # Get all years
        years = get_all_subfolders(service, root_id)
        logger.info(f"Found {len(years)} year folders")
        
        if not years:
            logger.warning("No year folders found in root")
            stats['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            stats['duration_seconds'] = (datetime.now() - start_time).total_seconds()
            return stats
        
        # Iterate through years
        for year_folder in years:
            year_name = year_folder['name']
            year_id = year_folder['id']
            
            logger.info(f"Processing year: {year_name}")
            
            # Get all months in this year
            months = get_all_subfolders(service, year_id)
            logger.info(f"  Found {len(months)} month folders in {year_name}")
            
            for month_folder in months:
                month_name = month_folder['name']
                month_id = month_folder['id']
                
                logger.info(f"  Processing month: {year_name}/{month_name}")
                
                # Get all languages in this month
                languages = get_all_subfolders(service, month_id)
                logger.info(f"    Found {len(languages)} language folders in {year_name}/{month_name}")
                
                for language_folder in languages:
                    language_name = language_folder['name']
                    language_id = language_folder['id']
                    
                    try:
                        # Check if Original_Files and AI_Generated_Files exist
                        original_folder = find_folder(service, language_id, "Original_Files")
                        ai_folder = find_folder(service, language_id, "AI_Generated_Files")
                        
                        # Skip languages that don't have both required folders
                        if not original_folder or not ai_folder:
                            logger.debug(
                                f"    ⊘ Skipping (missing folders): {year_name}/{month_name}/{language_name}"
                            )
                            continue
                        
                        original_id = original_folder[0]["id"]
                        ai_id = ai_folder[0]["id"]
                        
                        # Check if there are any .srt files in Original_Files and AI_Generated_Files
                        original_files = list_srt_files(service, original_id)
                        ai_files = list_srt_files(service, ai_id)
                        
                        # Skip if either folder is empty (no files to process)
                        if not original_files or not ai_files:
                            logger.debug(
                                f"    ⊘ Skipping (no files): {year_name}/{month_name}/{language_name}"
                            )
                            continue
                        
                        stats['total_folders_processed'] += 1
                        
                        logger.info(f"    Processing: {year_name}/{month_name}/{language_name}")
                        
                        # Process with incremental caching
                        results_raw, processing_info = process_with_incremental_caching(
                            year=int(year_name),
                            month=month_name,
                            language=language_name,
                            drive_service=service,
                            original_folder_id=original_id,
                            ai_generated_folder_id=ai_id,
                            build_ai_mapping_func=build_ai_mapping,
                            match_original_with_ai_func=match_original_with_ai,
                            download_file_content_func=download_file_content,
                            progress_callback=None  # No UI progress for automation
                        )
                        
                        # Skip logging/counting if no files were found
                        if processing_info['total_files'] == 0:
                            logger.debug(
                                f"    ⊘ Skipped (no files found): {year_name}/{month_name}/{language_name}"
                            )
                            # Delete the empty result document that was created
                            delete_empty_results(
                                year=int(year_name),
                                month=month_name,
                                language=language_name
                            )
                            continue
                        
                        # Count as successful if status contains "success" (includes partial_success variants)
                        if 'success' in processing_info['status']:
                            stats['successful_folders'] += 1
                            status_label = ""
                            if processing_info['status'] == 'success':
                                status_label = "✓"
                            elif 'partial_success' in processing_info['status']:
                                status_label = "⚠️ (fallback)"
                            elif 'fresh_calculation' in processing_info['status']:
                                status_label = "⚠️ (recalc)"
                            
                            logger.info(
                                f"    {status_label} {year_name}/{month_name}/{language_name}: "
                                f"{processing_info['total_files']} files "
                                f"(new: {processing_info['newly_processed']}, "
                                f"cached: {processing_info['cached_files']}) "
                                f"[{processing_info['status']}]"
                            )
                        else:
                            stats['failed_folders'] += 1
                            logger.warning(
                                f"    ✗ {year_name}/{month_name}/{language_name}: "
                                f"Processing failed - {processing_info['status']}"
                            )
                    
                    except Exception as e:
                        stats['failed_folders'] += 1
                        error_msg = f"Error processing {year_name}/{month_name}/{language_name}: {str(e)}"
                        logger.error(f"    ✗ {error_msg}")
                        stats['errors'].append(error_msg)
        
        # Calculate duration
        end_time = datetime.now()
        stats['end_time'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
        stats['duration_seconds'] = (end_time - start_time).total_seconds()
        
        # Log summary
        logger.info("=" * 60)
        logger.info("AUTOMATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total folders processed: {stats['total_folders_processed']}")
        logger.info(f"Successful: {stats['successful_folders']}")
        logger.info(f"Failed: {stats['failed_folders']}")
        logger.info(f"Duration: {stats['duration_seconds']:.2f} seconds")
        if stats['errors']:
            logger.info(f"Errors ({len(stats['errors'])}):")
            for error in stats['errors']:
                logger.info(f"  - {error}")
        logger.info("=" * 60)
        
        return stats
    
    except Exception as e:
        logger.error(f"Critical error in automation trigger: {str(e)}", exc_info=True)
        return {
            'error': str(e),
            'status': 'failed',
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S') if 'start_time' in locals() else None,
            'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
        }
