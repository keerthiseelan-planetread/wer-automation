"""Phase 2 Testing Script - Incremental Processing Integration"""

from dotenv import load_dotenv
load_dotenv()

import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

print("\n" + "=" * 70)
print("PHASE 2 TESTING - Incremental Processing Module")
print("=" * 70 + "\n")

# Test 1: Database Connection
print("TEST 1: Database Connection")
print("-" * 70)
try:
    from app.database.mongo_connection import get_mongo_client, close_mongo_connection
    client = get_mongo_client()
    client.admin.command('ping')
    print("✅ MongoDB Connection: SUCCESS")
    close_mongo_connection()
except Exception as e:
    print(f"❌ MongoDB Connection: FAILED - {str(e)}")
    sys.exit(1)

# Test 2: Database Operations
print("\nTEST 2: Database Operations Module")
print("-" * 70)
try:
    from app.database.db_operations import (
        get_parameter_hash,
        fetch_processed_file_ids,
        save_wer_results,
        get_all_results_for_parameters,
        update_processing_metadata,
        identify_new_files,
        merge_results
    )
    
    # Test parameter hash generation
    test_hash = get_parameter_hash(2024, "March", "English")
    assert isinstance(test_hash, str) and len(test_hash) == 64, "Hash generation failed"
    print("✅ Parameter Hash Generation: SUCCESS")
    
    # Test new vs processed file identification
    current_ids = ["file1", "file2", "file3", "file4", "file5"]
    processed_ids = ["file1", "file2", "file3"]
    new_files, deleted_files = identify_new_files(current_ids, processed_ids)
    assert set(new_files) == {"file4", "file5"}, f"Expected ['file4', 'file5'], got {new_files}"
    assert deleted_files == [], f"Expected [], got {deleted_files}"
    print("✅ New File Identification: SUCCESS")
    
    # Test result merging
    existing = [
        {"base_name": "video1", "ai_tool": "whisper", "wer_score": 15.0, "file_status": "current"},
        {"base_name": "video2", "ai_tool": "google", "wer_score": 20.0, "file_status": "current"}
    ]
    new_results = [
        {"base_name": "video3", "ai_tool": "whisper", "wer_score": 18.0, "file_status": "current"}
    ]
    merged = merge_results(existing, new_results)
    assert len(merged) == 3, f"Expected 3 results, got {len(merged)}"
    print("✅ Result Merging: SUCCESS")
    
except Exception as e:
    print(f"❌ Database Operations: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Database Validation
print("\nTEST 3: Database Validation Module")
print("-" * 70)
try:
    from app.database.db_validation import validate_db_integrity, get_database_health
    
    # Test database health
    health = get_database_health()
    assert "collections" in health, "Health check failed - missing collections"
    print(f"✅ Database Health Check: SUCCESS")
    print(f"   Collections: {list(health['collections'].keys())}")
    
    for col_name, col_stats in health['collections'].items():
        print(f"   - {col_name}: {col_stats['document_count']} docs, {col_stats['size_mb']} MB")
    
except Exception as e:
    print(f"❌ Database Validation: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Drive Utils Extensions
print("\nTEST 4: Drive Utilities Extensions")
print("-" * 70)
try:
    from app.drive.drive_utils import list_srt_files_with_metadata
    
    # Check function exists and is callable
    assert callable(list_srt_files_with_metadata), "list_srt_files_with_metadata not callable"
    print("✅ list_srt_files_with_metadata Function: EXISTS")
    
except Exception as e:
    print(f"❌ Drive Utilities: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Incremental Processor Module
print("\nTEST 5: Incremental Processor Module")
print("-" * 70)
try:
    from app.Services.incremental_processor import (
        process_with_incremental_caching,
        get_processing_summary,
        _calculate_wer_for_files
    )
    
    assert callable(process_with_incremental_caching), "Processor not callable"
    print("✅ Incremental Processor Function: EXISTS")
    
    # Test processing summary generation
    test_results = [
        {"base_name": "video1", "ai_tool": "whisper", "wer_score": 15.0, "file_status": "current"},
        {"base_name": "video2", "ai_tool": "whisper", "wer_score": 18.0, "file_status": "current"},
        {"base_name": "video3", "ai_tool": "google", "wer_score": 12.0, "file_status": "current"},
    ]
    
    summary = get_processing_summary(test_results)
    assert "whisper" in summary, "Whisper tool not in summary"
    assert "google" in summary, "Google tool not in summary"
    
    whisper_avg = summary["whisper"]["average"]
    assert whisper_avg == 16.5, f"Expected whisper avg 16.5, got {whisper_avg}"
    
    print("✅ Processing Summary Generation: SUCCESS")
    print(f"   Summary: {summary}")
    
except Exception as e:
    print(f"❌ Incremental Processor: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Integration Test - Mock Flow
print("\nTEST 6: Integration Test - Mock Processing Flow")
print("-" * 70)
try:
    from app.database.db_operations import (
        get_parameter_hash,
        save_wer_results,
        update_processing_metadata,
        get_all_results_for_parameters
    )
    
    # Simulate first-time processing
    test_year = 2024
    test_month = "March"
    test_language = "English"
    
    # Mock WER results from first run
    mock_results_run1 = [
        {
            "base_name": "video1",
            "ai_tool": "whisper",
            "wer_score": 15.23,
            "processed_timestamp": datetime.utcnow(),
            "google_drive_file_id": "file_id_1",
            "file_status": "current"
        },
        {
            "base_name": "video1",
            "ai_tool": "google",
            "wer_score": 12.45,
            "processed_timestamp": datetime.utcnow(),
            "google_drive_file_id": "file_id_2",
            "file_status": "current"
        }
    ]
    
    # Save first run
    save_success = save_wer_results(test_year, test_month, test_language, mock_results_run1)
    assert save_success, "Failed to save results"
    print("✅ Saved first-run results (2 files)")
    
    # Update metadata
    file_ids_run1 = ["file_id_1", "file_id_2"]
    update_success = update_processing_metadata(test_year, test_month, test_language, file_ids_run1)
    assert update_success, "Failed to update metadata"
    print("✅ Updated processing metadata")
    
    # Retrieve results
    retrieved_results = get_all_results_for_parameters(test_year, test_month, test_language)
    assert len(retrieved_results) == 2, f"Expected 2 results, got {len(retrieved_results)}"
    print(f"✅ Retrieved results from database: {len(retrieved_results)} files")
    
    # Simulate second run with merged results
    mock_results_run2 = [
        {
            "base_name": "video2",
            "ai_tool": "whisper",
            "wer_score": 18.90,
            "processed_timestamp": datetime.utcnow(),
            "google_drive_file_id": "file_id_3",
            "file_status": "current"
        }
    ]
    
    # Merge results
    from app.database.db_operations import merge_results
    merged = merge_results(retrieved_results, mock_results_run2)
    assert len(merged) == 3, f"Expected 3 merged results, got {len(merged)}"
    print(f"✅ Merged results: {len(retrieved_results)} cached + {len(mock_results_run2)} new = {len(merged)} total")
    
    # Save merged results
    save_success = save_wer_results(test_year, test_month, test_language, merged)
    assert save_success, "Failed to save merged results"
    
    # Update metadata with new file IDs
    file_ids_run2 = ["file_id_1", "file_id_2", "file_id_3"]
    update_success = update_processing_metadata(test_year, test_month, test_language, file_ids_run2)
    assert update_success, "Failed to update metadata for run 2"
    print("✅ Updated metadata after second run")
    
    # Retrieve final results
    final_results = get_all_results_for_parameters(test_year, test_month, test_language)
    assert len(final_results) == 3, f"Expected 3 final results, got {len(final_results)}"
    print(f"✅ Final result count verified: {len(final_results)} files")
    
    print("\n✅ Integration Test Passed!")
    print("   Scenario: First-time processing (2 files) → Second run (1 new file)")
    print("   Result: Successfully merged 2 cached + 1 new = 3 total")
    
except Exception as e:
    print(f"❌ Integration Test: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final Summary
print("\n" + "=" * 70)
print("PHASE 2 TESTING COMPLETE - ALL TESTS PASSED! ✅")
print("=" * 70)
print("\nSummary:")
print("  ✅ MongoDB Connection Working")
print("  ✅ Database Operations Functions Working")
print("  ✅ Database Validation Working")
print("  ✅ Drive Utilities Extensions Available")
print("  ✅ Incremental Processor Module Loaded")
print("  ✅ End-to-End Integration Test Passed")
print("\nPhase 2 is ready for integration with Streamlit UI!")
print("=" * 70 + "\n")
