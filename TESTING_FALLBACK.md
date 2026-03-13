# Testing the Fallback Strategy

## Quick Test Methods

### Method 1: Check Log Messages (Easiest) ✅

The Streamlit logs will show which layer is being used:

```
✅ SUCCESS:        "Processing complete!" 
                   → Layer 1 (MongoDB) ✓

⚠️ LAYER 2:        "Using local cached results"
                   → Layer 2 (Local Cache) ✓

⚠️ LAYER 3:        "Fresh calculation (no caching)"
                   → Layer 3 (Fresh Calculation) ✓

❌ CRITICAL:       "All fallback layers exhausted"
                   → All layers failed ✗
```

**Where to find logs:**
1. Open Streamlit terminal
2. Look for the icon/message after "Generate Report"

---

## Method 2: Verify Cache Files (File System) 📁

### Step 1: Generate a report successfully

1. Open your Streamlit app
2. Select: `Punjabi`, `May`, `2025`
3. Click "Generate Report"
4. Wait for completion

### Step 2: Check if cache file was created

```powershell
# Navigate to cache directory
cd "F:\Office Work\wer-automation\app\assets\cache"

# List all cache files
Get-ChildItem

# Should show files like: a1b2c3d4e5f6..._results.json
```

### Step 3: View cache file contents

```powershell
# Pick one cache file and view it
(Get-Content "a1b2c3d4e5f6..._results.json") | ConvertFrom-Json | Format-Table

# Or in Python
python -c "import json; print(json.load(open('a1b2c3d4e5f6..._results.json')))"
```

**Expected output:**
```json
{
  "parameter_hash": "a1b2c3d4...",
  "year": 2025,
  "month": "May",
  "language": "Punjabi",
  "results": [...],
  "cached_at": "2026-03-13T10:30:15",
  "total_files_cached": 20
}
```

✅ If you see this, **local cache is working!**

---

## Method 3: Test Layer 1 (MongoDB Success) 🟢

### Current: System uses MongoDB when it's available

**To verify MongoDB is working:**

```python
# Run in Python terminal
from app.database.mongo_connection import get_database

try:
    db = get_database()
    print("✅ MongoDB connection: SUCCESS")
except Exception as e:
    print(f"❌ MongoDB connection: FAILED - {e}")
```

**Expected:** Connection successful message

---

## Method 4: Test Layer 2 (Local Cache Fallback) 🟡

### Simulate MongoDB failure and test local cache

**Step 1: Ensure you have a cached result**
- Generate report once successfully (creates cache file)

**Step 2: Disconnect MongoDB temporarily**
```powershell
# Easiest: Disconnect internet or disable MongoDB
# Option A: Pause your MongoDB service
# Option B: In Windows: Settings → Network → Disable WiFi
# Option C: Edit .env and comment out MONGODB_URI (not recommended for production)
```

**Step 3: Generate same report again**
- Select: `Punjabi`, `May`, `2025` (same as before)
- Click "Generate Report"

**Step 4: Check result**
- Should show: **"⚠️ Using local cached results"**
- Results should be from previous run
- Status shows: `partial_success_local_cache`

✅ **If you see this, Layer 2 is working!**

---

## Method 5: Test Layer 3 (Fresh Calculation) 🟠

### Simulate MongoDB + Cache failure, trigger fresh calculation

**Step 1: Delete cache files**
```powershell
cd "F:\Office Work\wer-automation\app\assets\cache"
Remove-Item *.json -Force
```

**Step 2: Keep MongoDB disconnected**
(From Method 4, still disconnected)

**Step 3: Generate report again**
- Select: `Punjabi`, `May`, `2025`
- Click "Generate Report"

**Step 4: Check result**
- Should show: **"⚠️ Fresh calculation (no caching)"**
- Will take longer (recalculating from Google Drive)
- New cache file should be created automatically

**Step 5: Verify new cache was created**
```powershell
# Check cache directory
ls app/assets/cache
# Should show a new .json file
```

✅ **If you see fresh results + new cache file, Layer 3 is working!**

---

## Method 6: Automated Testing Script 🤖

Easy Python script to test all layers:

```python
# save as: test_fallback_layers.py

from app.Services.local_cache_manager import (
    load_results_from_local_cache,
    save_results_to_local_cache,
    get_cache_stats
)
from app.database.db_operations import get_all_results_for_parameters

# Test parameters
test_year = 2025
test_month = "May"
test_language = "Punjabi"

print("=" * 60)
print("FALLBACK STRATEGY TEST")
print("=" * 60)

# TEST 1: Check MongoDB
print("\n1️⃣ TEST LAYER 1 (MongoDB):")
try:
    mongo_results = get_all_results_for_parameters(test_year, test_month, test_language)
    if mongo_results:
        print(f"   ✅ MongoDB: Found {len(mongo_results)} cached results")
    else:
        print(f"   ⚠️ MongoDB: No cached results (might be first run)")
except Exception as e:
    print(f"   ❌ MongoDB: CONNECTION FAILED - {e}")

# TEST 2: Check Local Cache
print("\n2️⃣ TEST LAYER 2 (Local Cache):")
try:
    local_results = load_results_from_local_cache(test_year, test_month, test_language)
    if local_results:
        print(f"   ✅ Local Cache: Found {len(local_results)} cached results")
    else:
        print(f"   ⚠️ Local Cache: No cached results (generate report first)")
except Exception as e:
    print(f"   ❌ Local Cache: ERROR - {e}")

# TEST 3: Check Cache Statistics
print("\n3️⃣ CACHE STATISTICS:")
try:
    stats = get_cache_stats()
    print(f"   📁 Directory: {stats.get('cache_directory')}")
    print(f"   📊 Files: {stats.get('total_files')}")
    print(f"   💾 Size: {stats.get('total_size_mb')} MB")
    print(f"   🔧 Status: {stats.get('status')}")
except Exception as e:
    print(f"   ❌ Error getting stats: {e}")

# TEST 4: Simulate Layer 2 + 3
print("\n4️⃣ SAVE TEST (create new cache entry):")
try:
    test_results = [
        {"base_name": "test", "ai_tool": "test", "wer_score": 50.0},
    ]
    save_success = save_results_to_local_cache(test_year, test_month, test_language, test_results)
    if save_success:
        print(f"   ✅ Save: Successfully saved test results")
    else:
        print(f"   ❌ Save: Failed to save test results")
except Exception as e:
    print(f"   ❌ Save: ERROR - {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
```

**Run the test:**
```powershell
cd "F:\Office Work\wer-automation"
python test_fallback_layers.py
```

**Expected output:**
```
============================================================
FALLBACK STRATEGY TEST
============================================================

1️⃣ TEST LAYER 1 (MongoDB):
   ✅ MongoDB: Found 20 cached results

2️⃣ TEST LAYER 2 (Local Cache):
   ✅ Local Cache: Found 20 cached results

3️⃣ CACHE STATISTICS:
   📁 Directory: F:\Office Work\wer-automation\app\assets\cache
   📊 Files: 5
   💾 Size: 12.5 MB
   🔧 Status: healthy

4️⃣ SAVE TEST (create new cache entry):
   ✅ Save: Successfully saved test results

============================================================
TEST COMPLETE
============================================================
```

---

## Method 7: Real-Time Log Inspection 🔍

Monitor the actual logs while generating reports:

### Option A: Streamlit Terminal Output

```powershell
# Terminal shows:
2026-03-13 10:30:15 - INFO - Starting incremental processing for 2025/May/Punjabi
2026-03-13 10:30:20 - INFO - Saved 20 results to local cache successfully
2026-03-13 10:30:22 - INFO - Processing complete: 20 total files
```

### Option B: Python Logging

```python
import logging

# Set logging to DEBUG to see everything
logging.basicConfig(level=logging.DEBUG)

# Then run your report generation
# Will show detailed logs including which layer was used
```

### Option C: File Logs

```powershell
# Some logs are written to files (if configured)
Get-Content "logs/app.log" -Tail 50  # Last 50 lines
```

---

## Status Codes Reference 📋

When you generate a report, check the `processing_info["status"]`:

| Status Code | Meaning | Layer |
|------------|---------|-------|
| `success` | All systems working, fresh processing | Layer 1 ✅ |
| `partial_success_mongodb_cache` | MongoDB working, using cache | Layer 1 ✅ |
| `partial_success_local_cache` | MongoDB down, local cache working | Layer 2 🟡 |
| `fresh_calculation_no_cache` | Both down, recalculating fresh | Layer 3 🟠 |
| `critical_failure` | Everything failed | ❌ |

---

## Complete Testing Checklist ✓

### Pre-Testing
- [ ] App is running with Streamlit
- [ ] Have both `Punjabi May 2025` data available
- [ ] MongoDB is running

### Layer 1 Test
- [ ] Generate report normally
- [ ] See "✅ Processing complete!"
- [ ] Cache file created in `app/assets/cache/`

### Layer 2 Test
- [ ] Already have cache file from Layer 1
- [ ] Disconnect MongoDB (pause service)
- [ ] Generate same report
- [ ] See "⚠️ Using local cached results"
- [ ] Same results as Layer 1

### Layer 3 Test
- [ ] Cache files deleted
- [ ] MongoDB still disconnected
- [ ] Generate report
- [ ] See "⚠️ Fresh calculation (no caching)"
- [ ] New cache file created
- [ ] Results appear (might be slower)

### Cleanup
- [ ] Reconnect MongoDB
- [ ] Restart Streamlit app
- [ ] Verify normal operation returns

---

## Troubleshooting Test Issues

### "Cache file not created"
- Check permissions: `app/assets/cache/` must be writable
- Check disk space: at least 1 GB free
- Run as administrator if on Windows

### "Local cache not found"
- Generate report at least once successfully
- Check file exists: `ls app/assets/cache/`
- May be named with hash, check contents

### "Fresh calculation still failed"
- Check Google Drive credentials
- Check internet connection
- Verify `SERVICE_ACCOUNT_PATH` in `.env`

### "MongoDB connection always fails"
- Check MongoDB is running: `mongosh` in terminal
- Check connection string in `.env`
- Try from MongoDB Atlas dashboard

---

## Quick Commands

```powershell
# Check if cache exists
Test-Path "F:\Office Work\wer-automation\app\assets\cache"

# List all cache files
Get-ChildItem "F:\Office Work\wer-automation\app\assets\cache" -File

# Clear all cache (testing)
Remove-Item "F:\Office Work\wer-automation\app\assets\cache\*.json"

# Check cache size
(Get-ChildItem "F:\Office Work\wer-automation\app\assets\cache\" -File | 
  Measure-Object -Property Length -Sum).Sum / 1MB

# View one cache file
Get-Content "F:\Office Work\wer-automation\app\assets\cache\abc123...json" -Raw | ConvertFrom-Json
```

---

**Testing Status**: Ready to test  
**Last Updated**: 2026-03-13
