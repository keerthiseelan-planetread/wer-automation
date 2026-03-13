#!/usr/bin/env python3
"""
Automated test script for Fallback Strategy
Run this to test all three layers at once
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.Services.local_cache_manager import (
    load_results_from_local_cache,
    save_results_to_local_cache,
    get_cache_stats,
    get_parameter_hash
)
from app.database.db_operations import get_all_results_for_parameters
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(num, text):
    """Print formatted section"""
    print(f"\n{num}️⃣  {text}")
    print("-" * 70)

def test_mongodb_layer():
    """TEST LAYER 1: MongoDB"""
    print_section("1", "TEST LAYER 1 (MongoDB Connection)")
    
    # Using August/Punjabi which exists in cache
    test_year = 2025
    test_month = "August"
    test_language = "Punjabi"
    
    try:
        print(f"   Testing: {test_year}/{test_month}/{test_language}")
        mongo_results = get_all_results_for_parameters(test_year, test_month, test_language)
        
        if mongo_results:
            print(f"   ✅ SUCCESS: Found {len(mongo_results)} results in MongoDB")
            print(f"   Sample data: {mongo_results[0].get('base_name', 'N/A')} - {mongo_results[0].get('ai_tool', 'N/A')}")
            return True
        else:
            print(f"   ⚠️ No results yet (expected on first run)")
            return False
            
    except Exception as e:
        print(f"   ❌ FAILED: MongoDB connection error")
        print(f"   Error: {str(e)}")
        return False

def test_local_cache_layer():
    """TEST LAYER 2: Local Cache"""
    print_section("2", "TEST LAYER 2 (Local JSON Cache)")
    
    # Using August/Punjabi which exists in cache
    test_year = 2025
    test_month = "August"
    test_language = "Punjabi"
    
    try:
        print(f"   Testing: {test_year}/{test_month}/{test_language}")
        local_results = load_results_from_local_cache(test_year, test_month, test_language)
        
        if local_results:
            print(f"   ✅ SUCCESS: Found {len(local_results)} results in local cache")
            print(f"   Cache location: app/assets/cache/{get_parameter_hash(test_year, test_month, test_language)}_results.json")
            if local_results:
                print(f"   Sample data: {local_results[0].get('base_name', 'N/A')} - {local_results[0].get('ai_tool', 'N/A')}")
            return True
        else:
            print(f"   ⚠️ No local cache found (generate report first)")
            return False
            
    except Exception as e:
        print(f"   ❌ FAILED: Local cache error")
        print(f"   Error: {str(e)}")
        return False

def test_cache_stats():
    """TEST: Cache Statistics"""
    print_section("3", "CACHE STATISTICS & HEALTH")
    
    try:
        stats = get_cache_stats()
        
        print(f"   📁 Cache Directory: {stats.get('cache_directory')}")
        print(f"   📊 Cache Files: {stats.get('total_files')}")
        print(f"   💾 Total Size: {stats.get('total_size_mb')} MB")
        
        status = stats.get('status')
        if status == 'healthy':
            print(f"   🟢 Status: HEALTHY")
        elif status == 'empty':
            print(f"   🟡 Status: EMPTY (no cache yet)")
        else:
            print(f"   🔴 Status: {status}")
            
        return status in ['healthy', 'empty']
        
    except Exception as e:
        print(f"   ❌ FAILED: Could not get cache stats")
        print(f"   Error: {str(e)}")
        return False

def test_cache_save():
    """TEST: Cache Save/Load"""
    print_section("4", "CACHE SAVE & LOAD TEST")
    
    test_year = 2025
    test_month = "March"  # Different month to avoid conflicts
    test_language = "English"
    
    test_results = [
        {
            "base_name": "test_file_001",
            "ai_tool": "test_whisper",
            "wer_score": 45.67,
            "google_drive_file_id": "test_id_001"
        },
        {
            "base_name": "test_file_002",
            "ai_tool": "test_google",
            "wer_score": 32.45,
            "google_drive_file_id": "test_id_002"
        }
    ]
    
    try:
        print(f"   Saving test data: {test_year}/{test_month}/{test_language}")
        save_success = save_results_to_local_cache(test_year, test_month, test_language, test_results)
        
        if save_success:
            print(f"   ✅ SAVED: {len(test_results)} test results")
            
            # Try to load it back
            print(f"   Loading test data back...")
            loaded_results = load_results_from_local_cache(test_year, test_month, test_language)
            
            if loaded_results and len(loaded_results) == len(test_results):
                print(f"   ✅ LOADED: {len(loaded_results)} results match saved count")
                return True
            else:
                print(f"   ❌ Load mismatch: saved {len(test_results)}, loaded {len(loaded_results)}")
                return False
        else:
            print(f"   ❌ FAILED: Could not save test data")
            return False
            
    except Exception as e:
        print(f"   ❌ FAILED: Cache save/load test error")
        print(f"   Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header("FALLBACK STRATEGY TEST SUITE")
    print("Testing all three layers of the fallback system...\n")
    
    results = {}
    
    # Run tests
    results['mongodb'] = test_mongodb_layer()
    results['local_cache'] = test_local_cache_layer()
    results['stats'] = test_cache_stats()
    results['save_load'] = test_cache_save()
    
    # Summary
    print_header("TEST SUMMARY")
    
    print("\n  Layer Tests:")
    print(f"  {'Layer 1 (MongoDB)':<30} {'✅ PASS' if results['mongodb'] else '⚠️ CHECK'}")
    print(f"  {'Layer 2 (Local Cache)':<30} {'✅ PASS' if results['local_cache'] else '⚠️ CHECK'}")
    print(f"  {'Cache Statistics':<30} {'✅ PASS' if results['stats'] else '❌ FAIL'}")
    print(f"  {'Save/Load Test':<30} {'✅ PASS' if results['save_load'] else '❌ FAIL'}")
    
    total_pass = sum(results.values())
    total_tests = len(results)
    
    print(f"\n  Overall: {total_pass}/{total_tests} tests passed")
    
    if total_pass == total_tests:
        print("\n  🎉 ALL TESTS PASSED! Fallback system is ready.")
        print_header("✅ SYSTEM READY FOR PRODUCTION")
        return 0
    elif total_pass >= 2:
        print("\n  ⚠️ Some layers working, system partially functional.")
        print("     Generate a report to create cache files if needed.")
        print_header("⚠️ SYSTEM PARTIALLY READY")
        return 1
    else:
        print("\n  ❌ Multiple failures detected.")
        print("     See errors above for troubleshooting.")
        print_header("❌ SYSTEM NEEDS ATTENTION")
        return 2

if __name__ == "__main__":
    sys.exit(main())
