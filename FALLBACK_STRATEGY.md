# MongoDB Fallback Strategy Documentation

## Overview

The WER Automation system now implements a **three-layer fallback strategy** to ensure reports are ALWAYS generated, even if MongoDB is unavailable.

## Fallback Layers

### Layer 1: MongoDB Primary Storage ✅
- **Status**: `success` or `partial_success_mongodb_cache`
- **Description**: Results are stored in MongoDB cloud database
- **Pros**: Fast, cloud-based, reliable
- **Cons**: Requires internet + MongoDB connection

### Layer 2: Local JSON Cache 💾
- **Status**: `partial_success_local_cache`
- **Description**: Results stored as JSON files in `app/assets/cache/`
- **Pros**: Works offline, persistent local storage
- **Cons**: Not automatically synced, only stores recent results

### Layer 3: Fresh Calculation 🔄
- **Status**: `fresh_calculation_no_cache`
- **Description**: Reports recalculated on-the-fly without any caching
- **Pros**: Always works, generates current data
- **Cons**: Slower, more resource-intensive
- **Fallback**: Results automatically saved to local cache

## Processing Logic Flow

```
User requests report (Year/Month/Language)
        ↓
Try: Save/retrieve from MongoDB
  ✓ Success → Use cached results
  ✗ Failed → Try Layer 2
        ↓
Try: Retrieve from local JSON cache
  ✓ Success → Use local cached results
  ✗ Failed → Try Layer 3
        ↓
Try: Fresh calculation from Google Drive
  ✓ Success → Calculate WER, save to local cache
  ✗ Failed → Critical failure (show error)
```

## Cache File Structure

Cache files are stored in `app/assets/cache/` with naming pattern:
```
{parameter_hash}_results.json
```

Example:
```json
{
  "parameter_hash": "a1b2c3d4...",
  "year": 2025,
  "month": "March",
  "language": "Punjabi",
  "results": [
    {
      "base_name": "Bhagi di dhee Song",
      "ai_tool": "whisper",
      "wer_score": 15.32,
      "google_drive_file_id": "xxxxx",
      "file_status": "current"
    }
  ],
  "cached_at": "2025-03-13T10:30:15.123456",
  "total_files_cached": 20
}
```

## Error Messages

| Status | Message | Action |
|--------|---------|--------|
| `success` | ✅ Processing complete | Using fresh + MongoDB cache |
| `partial_success_mongodb_cache` | ⚠️ Using MongoDB cached | MongoDB working, no new files |
| `partial_success_local_cache` | ⚠️ Using local cached | MongoDB down, local cache available |
| `fresh_calculation_no_cache` | ⚠️ Fresh calculation | Both DBs down, recalculated on-the-fly |
| `critical_failure` | ❌ Report generation failed | All layers exhausted |

## When Each Layer Activates

### Layer 1 (MongoDB)
- Initial processing attempt
- Tries to fetch from MongoDB first
- Saves successful results to MongoDB

### Layer 2 (Local Cache)
- MongoDB connection fails
- Local JSON cache file exists for the parameters
- System retrieves previously cached results

### Layer 3 (Fresh Calculation)
- Both MongoDB and local cache unavailable
- System downloads files from Google Drive
- Recalculates WER scores fresh
- Saves to local cache for future use

## Maintenance

### Cache Cleanup
The system provides automatic cache cleanup:
```python
from app.Services.local_cache_manager import clear_old_cache
clear_old_cache(max_age_days=30)  # Removes cache older than 30 days
```

### Cache Statistics
View cache status:
```python
from app.Services.local_cache_manager import get_cache_stats
stats = get_cache_stats()
print(stats)
# Output: {
#   'cache_directory': '/path/to/app/assets/cache',
#   'total_files': 45,
#   'total_size_mb': 12.5,
#   'status': 'healthy'
# }
```

## Benefits

✅ **Reliability**: Report generation never completely fails
✅ **Redundancy**: Three independent fallback mechanisms
✅ **Offline Support**: Works without internet if data was previously cached
✅ **Data Persistence**: Local backups survive application restarts
✅ **Transparency**: Users see which system is being used via status messages
✅ **Performance**: Falls back gracefully with minimal performance impact

## Configuration

### Cache Directory
Location: `app/assets/cache/`
Can be customized in `local_cache_manager.py`:
```python
CACHE_DIR = Path("app/assets/cache")  # Modify this path
```

### Cache Retention
By default: 30 days
Modify in `local_cache_manager.py`:
```python
def clear_old_cache(max_age_days: int = 30):  # Change 30 to desired days
```

## Testing the Fallback

To test the fallback layers:

1. **Test MongoDB Failure**:
   - Disconnect MongoDB: Pause MongoDB in network settings
   - Generate report: Should fall back to Layer 2/3
   - Result: See "Using local cached" or "Fresh calculation" message

2. **Test Local Cache**:
   - Delete cache files: `rm app/assets/cache/*`
   - MongoDB still down: Should trigger Layer 3
   - Result: Fresh calculation with new local cache

3. **Test Critical Failure** (simulated):
   - MongoDB down
   - No cache files
   - Invalid Google Drive credentials
   - Result: "Critical failure" error with troubleshooting tips

## Troubleshooting

### "Critical failure" Error

Check in order:
1. **MongoDB**: `ping mongodb connection` or check cloud dashboard
2. **Google Drive**: Verify `SERVICE_ACCOUNT_PATH` and permissions
3. **Permissions**: Ensure app/assets/cache is writable
4. **Space**: Check disk space for cache files

### Stale Cache

If reports show old data:
1. Check cache timestamp in JSON file
2. Clear cache manually: `python scripts/clear_cache.py`
3. Run report again to regenerate

### Performance Issues

If fresh calculation is slow:
1. Check internet speed to Google Drive
2. Check SRT file sizes (larger = slower)
3. Check concurrent users (limit processing queue)

---

**Last Updated**: 2026-03-13  
**Version**: 1.0 - Three-Layer Fallback Strategy
