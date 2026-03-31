# WER Tool Rankings WordPress Plugin

A WordPress plugin that displays AI tool rankings based on Word Error Rate (WER) metrics from your WER Automation API.

## Features

✅ **Language Selection** - Choose from 10+ languages (English, Spanish, French, German, Italian, Portuguese, Hindi, Chinese, Japanese, Arabic)

✅ **Top 10 Rankings** - Displays the best performing AI tools based on lowest average WER

✅ **Ranked Table** - Shows columns for:
- Rank (with medals 🥇🥈🥉 for top 3)
- AI Tool Name
- Language
- Average WER Score
- Best WER Score
- Worst WER Score
- Files Tested Count

✅ **Responsive Design** - Works perfectly on desktop and mobile devices

✅ **Real-time Data** - Fetches data from your FastAPI backend on-demand

✅ **Beautiful UI** - Professional styling with loading spinner and error handling

## Installation

1. Upload the `wer-tool-rankings.php` file to your WordPress plugins directory:
   ```
   /wp-content/plugins/wer-tool-rankings/wer-tool-rankings.php
   ```

2. Activate the plugin from WordPress Admin Dashboard → Plugins

3. The plugin will appear in the sidebar under "WER Rankings"

## Usage

### Basic Usage

Add this shortcode to any page or post:

```
[wer_tool_rankings]
```

### Advanced Usage with Parameters

```
[wer_tool_rankings year="2024" month="January" backend_url="https://wer-automation-api.onrender.com"]
```

**Parameters:**
- `year` - Year for the data (default: current year)
- `month` - Month name (default: current month)  
- `backend_url` - Your FastAPI backend URL (default: https://wer-automation-api.onrender.com)

### Example Page Setup

1. Create a new page in WordPress
2. Title: "AI Tool Rankings"
3. Add this to the content:
   ```
   [wer_tool_rankings year="2024" month="January"]
   ```
4. Publish

## How It Works

1. **User selects a language** from the dropdown (English, Spanish, etc.)
2. **User clicks "Load Rankings"** button
3. **Plugin fetches data** from your FastAPI endpoint:
   ```
   GET https://wer-automation-api.onrender.com/api/wer/get-tool-summary-metrics
   ?year=2024&month=January&language=en
   ```
4. **Data is sorted** by Average WER (lowest/best first)
5. **Top 10 tools displayed** in a ranked table

## API Endpoint Requirements

Your FastAPI backend must have this endpoint:

```
GET /api/wer/get-tool-summary-metrics?year=YYYY&month=Month&language=code
```

Expected Response Format:

```json
{
  "status": "success",
  "data": {
    "Whisper": {
      "average_wer": 15.3,
      "best_wer": 12.5,
      "worst_wer": 18.2,
      "files_count": 45
    },
    "Google Speech": {
      "average_wer": 16.8,
      "best_wer": 14.2,
      "worst_wer": 19.5,
      "files_count": 40
    }
  }
}
```

## Ranking Logic

The plugin sorts tools by **Average WER in ascending order**:
- **Lower WER = Higher Rank (Better Performance)**
- **Rank #1** = Lowest average WER (best performing tool)
- **Rank #10** = 10th lowest average WER

## Table Columns

| Column | Description |
|--------|------------|
| **Rank** | Position 1-10 (with medals for top 3) |
| **AI Tool** | Name of the AI tool/model |
| **Language** | Selected language code |
| **Average WER** | Average Word Error Rate (lower is better) |
| **Best WER** | Lowest WER score achieved |
| **Worst WER** | Highest WER score recorded |
| **Files Tested** | Number of audio files tested |

## Customization

### Change Default Language

Edit the `<select>` options in the plugin:

```php
<option value="en">English</option>
<option value="es">Spanish</option>
<!-- Add more languages here -->
```

### Change Backend URL

If your API is hosted elsewhere, use the shortcode parameter:

```
[wer_tool_rankings backend_url="https://your-custom-url.com"]
```

### Modify Styling

All CSS is embedded in the plugin. Look for the `<style>` section to customize colors, fonts, spacing, etc.

## Files Included

```
wer-tool-rankings/
├── wer-tool-rankings.php    (Main plugin file)
└── README.md               (This file)
```

## Requirements

- WordPress 5.0+
- PHP 7.2+
- Modern browser with Fetch API support

## CORS Configuration

Make sure your FastAPI backend has CORS enabled (should already be configured):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your WordPress domain
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### "Error loading rankings"

**Problem:** CORS error or backend unreachable  
**Solution:** 
1. Check backend URL in shortcode is correct
2. Verify backend is running and accessible
3. Ensure CORS is enabled on backend

### "No data available for this language"

**Problem:** Selected language has no data  
**Solution:** 
1. Check your database has metrics for this language
2. Try a different language
3. Verify data was uploaded to backend

### Table Not Displaying

**Problem:** Plugin shortcode not working  
**Solution:**
1. Verify plugin is activated in Admin → Plugins
2. Check you're using correct shortcode: `[wer_tool_rankings]`
3. Check browser console for JavaScript errors

## Support

For issues or feature requests, contact the WER Automation team.

## License

This plugin is part of the WER Automation project.
