# WordPress WER Rankings Plugin - Quick Start Guide

## 3-Step Installation

### Step 1: Upload Plugin to WordPress

1. Go to: **WordPress Admin → Plugins → Add New**
2. Click **Upload Plugin**
3. Select **wer-tool-rankings.php**
4. Click **Install Now**

### Step 2: Activate Plugin

1. Click **Activate Plugin**
2. You should see "WER Rankings" in the admin sidebar

### Step 3: Add to Your Page

Create a new page or post and add this shortcode:

```
[wer_tool_rankings]
```

OR with custom settings:

```
[wer_tool_rankings year="2024" month="January" backend_url="https://wer-automation-api.onrender.com"]
```

That's it! The plugin will now:
✅ Show a language selector dropdown
✅ Display a "Load Rankings" button
✅ Show top 10 AI tools ranked by WER
✅ Allow users to switch languages dynamically

---

## What Users Will See

### UI Layout:

```
╔════════════════════════════════════════════════════════╗
║  🏆 AI Tools Rankings - Word Error Rate               ║
║  Top 10 tools ranked by lowest average WER            ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  Language: [English ▼]  [Load Rankings]               ║
║                                                        ║
║  ┌─────────────────────────────────────────────────┐  ║
║  │ Rank │ Tool        │ Avg WER │ Best │ Files    │  ║
║  ├─────────────────────────────────────────────────┤  ║
║  │ 🥇  │ Whisper     │ 15.30%  │ 12.5 │ 45       │  ║
║  │ 🥈  │ Google ST   │ 16.80%  │ 14.2 │ 40       │  ║
║  │ 🥉  │ AWS Transcr │ 17.20%  │ 15.1 │ 38       │  ║
║  │ #4  │ Azure STT   │ 18.50%  │ 16.0 │ 35       │  ║
║  │ #5  │ IBM Watson  │ 19.30%  │ 17.5 │ 32       │  ║
║  │ #6  │ Deepgram    │ 20.10%  │ 18.2 │ 30       │  ║
║  │ #7  │ Descript    │ 21.50%  │ 19.0 │ 28       │  ║
║  │ #8  │ Rev.ai      │ 22.30%  │ 20.1 │ 25       │  ║
║  │ #9  │ AssemblyAI  │ 23.80%  │ 21.5 │ 22       │  ║
║  │ #10 │ CloudAPI    │ 24.90%  │ 22.8 │ 20       │  ║
║  └─────────────────────────────────────────────────┘  ║
║                                                        ║
║  Data from WER Automation Backend | Year: 2024        ║
╚════════════════════════════════════════════════════════╝
```

---

## Ranking System

The plugin **automatically ranks tools** by Average WER:

| Rank | Lower Average WER | Status |
|------|------------------|--------|
| 🥇 Rank #1 | 15.30% | Best Performing |
| 🥈 Rank #2 | 16.80% | 2nd Best |
| 🥉 Rank #3 | 17.20% | 3rd Best |
| #4-#10 | Higher WER | Ranked by score |

**Key Point:** The tool with the **LOWEST Average WER gets Rank #1** (Lower is Better)

---

## Features in Action

### Language Switching

```
Select Language: [English ▼]  [Load Rankings]
                    ↓
              Spanish
              French
              German
              Hindi
              Chinese
              etc.
```

User selects language → Clicks "Load Rankings" → Table updates with new data

### Data Columns Explained

```
┌──────────────────────────────────────────────────────────┐
│ Rank │ AI Tool    │ Avg WER │ Best │ Worst │ Files      │
├──────────────────────────────────────────────────────────┤
│      │            │  (%)    │ (%)  │ (%)   │ Count      │
│ 🥇  │ Whisper    │ 15.30   │ 12.5 │ 18.2  │ 45 files   │
└──────────────────────────────────────────────────────────┘
       ↓           ↓          ↓      ↓      ↓       ↓
     Position    Tool Name  Average Best  Worst  How Many
                           Score   Score  Score  Files
                                                Tested
```

---

## Shortcode Parameters

### Default (No Parameters)

```
[wer_tool_rankings]
```

Uses:
- Today's year
- Today's month
- Default backend: https://wer-automation-api.onrender.com

### With All Parameters

```
[wer_tool_rankings year="2024" month="January" backend_url="https://your-api.com"]
```

**year** = "2024"
**month** = "January" (Full name, capitalized)
**backend_url** = Your FastAPI URL

---

## Troubleshooting Tips

### If rankings don't show:

1. **Check backend is running:**
   ```
   https://wer-automation-api.onrender.com/
   ```
   Should return: `{"message":"WER Backend Running 🚀"}`

2. **Check language has data:**
   Try "English (en)" first
   Other languages may not have metrics yet

3. **Check browser console:** (Press F12)
   Look for red error messages
   Report any "CORS" errors

### If table looks ugly:

1. Check your WordPress theme is compatible
2. Disable other CSS plugins temporarily
3. Clear WordPress cache

---

## File Structure for Deployment

```
wer-automation/
├── wordpress-plugin/
│   ├── wer-tool-rankings.php    ← Main plugin file
│   ├── README.md                ← Full documentation
│   └── QUICKSTART.md            ← This file
├── backend/
│   └── main.py                  ← Your FastAPI backend
└── ... (other project files)
```

---

## Next Steps

1. ✅ Copy `wer-tool-rankings.php` to WordPress plugins folder
2. ✅ Activate plugin in WordPress admin
3. ✅ Create new page and add shortcode
4. ✅ Test with different languages
5. ✅ Customize colors/fonts if needed (edit CSS in plugin)

---

## API Endpoint Being Called

The plugin calls your backend endpoint:

```
GET https://wer-automation-api.onrender.com/api/wer/get-tool-summary-metrics
    ?year=2024
    &month=January
    &language=en
```

**Your backend must return:**

```json
{
  "status": "success",
  "data": {
    "ToolName": {
      "average_wer": 15.3,
      "best_wer": 12.5,
      "worst_wer": 18.2,
      "files_count": 45
    },
    ...
  }
}
```

This should already be working based on your FastAPI implementation! ✅

---

## Support

Need help? Check:
1. Browser console (F12) for errors
2. WordPress logs for PHP errors
3. Backend logs: `https://wer-automation-api.onrender.com/`
4. README.md for detailed documentation

---

**Happy Ranking! 🏆**
