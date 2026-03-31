# ⚡ Quick Reference - WordPress Plugin Setup

## 🎯 Super Quick Setup (5 Minutes)

```
STEP 1: GET THE PLUGIN FILE
  📁 f:\Office Work\wer-automation\wordpress-plugin\wer-tool-rankings.php

STEP 2: UPLOAD TO WORDPRESS
  📂 /wp-content/plugins/wer-tool-rankings/wer-tool-rankings.php

STEP 3: ACTIVATE IN WORDPRESS
  🔌 WordPress Admin → Plugins → Activate "WER Tool Rankings"

STEP 4: ADD TO PAGE
  📝 Pages → Add New → Add Shortcode: [wer_tool_rankings]

STEP 5: PUBLISH & VIEW
  ✅ Click Publish → View Page
```

---

## 📊 Visual Setup Flow

```
┌─────────────────────────────┐
│  Your Computer              │
│  wer-tool-rankings.php      │
│  (Save this file)           │
└────────────┬────────────────┘
             │ Upload via FTP/File Manager
             ↓
┌─────────────────────────────┐
│  WordPress Server           │
│  /wp-content/plugins/       │
│  wer-tool-rankings/         │
│  wer-tool-rankings.php      │
└────────────┬────────────────┘
             │ Activate in Admin
             ↓
┌─────────────────────────────┐
│  WordPress Admin Dashboard  │
│  Plugins → Activate         │
│  ✅ Plugin Active           │
└────────────┬────────────────┘
             │ Add to Page
             ↓
┌─────────────────────────────┐
│  WordPress Page             │
│  [wer_tool_rankings]        │
│  ✅ Rankings Display!       │
└─────────────────────────────┘
```

---

## 🚀 Installation Methods

### Method 1: FTP Upload (Most Reliable)
```
1. Download FileZilla/WinSCP
2. Connect with FTP credentials
3. Navigate: /public_html/wp-content/plugins/
4. Create folder: wer-tool-rankings
5. Upload wer-tool-rankings.php
6. Activate in WordPress
```

### Method 2: File Manager (Via Hosting Panel)
```
1. Login to hosting (cPanel/Plesk)
2. File Manager → /public_html/wp-content/plugins/
3. Create folder: wer-tool-rankings
4. Upload wer-tool-rankings.php
5. Activate in WordPress
```

### Method 3: WordPress Upload (Easiest)
```
1. WordPress Admin → Plugins → Add New
2. Upload Plugin → wer-tool-rankings.php
3. Install Now → Activate
```

---

## 🎨 What You Get

### User Interface:
```
══════════════════════════════════════════
  🏆 AI Tools Rankings - Word Error Rate
══════════════════════════════════════════

  Language: [Hindi ▼]    [Load Rankings]

┌─────────────────────────┐
│ Rank │ AI Tool         │
├─────────────────────────┤
│ 🥇  │ Whisper         │
│ 🥈  │ Google Speech   │
│ 🥉  │ AWS Transcribe  │
│ #4  │ Azure STT       │
│ #5  │ IBM Watson      │
│ #6  │ Deepgram        │
│ #7  │ Descript        │
│ #8  │ Rev.ai          │
│ #9  │ AssemblyAI      │
│ #10 │ CloudAPI        │
└─────────────────────────┘
```

---

## 🔧 Configuration Examples

### Basic (Auto Year/Month):
```
[wer_tool_rankings]
```

### Specific Date:
```
[wer_tool_rankings year="2024" month="January"]
```

### Custom Backend:
```
[wer_tool_rankings backend_url="https://your-api.com"]
```

---

## 🔍 File Locations

### Local Machine:
```
f:\Office Work\wer-automation\wordpress-plugin\
├── wer-tool-rankings.php
├── README.md
├── INSTALLATION_GUIDE.md
└── QUICKSTART.md
```

### WordPress Server:
```
/public_html/wp-content/plugins/wer-tool-rankings/
└── wer-tool-rankings.php
```

### Shortcode in Page:
```
WordPress Dashboard:
  Pages → Your Page → [wer_tool_rankings]
```

---

## ⚡ Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| Plugin not visible in list | Check file path, reload admin page |
| Shortcode shows as text | Verify plugin is Activated |
| Blank table/loading forever | Check backend is running, check browser console |
| No data showing | Try different language, verify MongoDB has data |
| Page looks broken | Clear browser cache (Ctrl+Shift+Delete) |
| CORS error | Backend CORS already enabled, check URL |

---

## 🎯 Verification Steps

After installation, verify:

```
✅ Plugin appears in Plugins list
✅ Plugin is marked as Active (green)
✅ Page created with shortcode
✅ Language dropdown shows 4 languages
✅ Load Rankings button works
✅ Table displays top 10 tools
✅ Different languages load different data
✅ Browser console (F12) has no red errors
✅ Mobile view looks good
```

---

## 🌐 Languages Available

```
Language Selector Options:
├── 🇮🇳 Hindi (hi)
├── 🇮🇳 Punjabi (pa)
├── 🇮🇳 Telugu (te)
└── 🇮🇳 Marathi (mr)
```

---

## 📞 Testing URLs

Test backend connectivity:

```
Health Check:
👉 https://wer-automation-api.onrender.com/

Get Rankings:
👉 https://wer-automation-api.onrender.com/api/wer/get-tool-summary-metrics
   ?year=2024&month=January&language=hi
```

---

## 🎓 Advanced Usage

Add to multiple pages with different configs:

```
Page 1: /hindi-rankings
[wer_tool_rankings year="2024" month="January"]

Page 2: /monthly-rankings
[wer_tool_rankings year="2024" month="February"]

Page 3: /custom-backend
[wer_tool_rankings backend_url="https://custom.com"]
```

---

## 📝 Checklist for WordPress Admin

```
Installation Checklist:
☐ Download wer-tool-rankings.php
☐ Create folder in /wp-content/plugins/
☐ Upload plugin file
☐ Activate plugin in WordPress
☐ Create new page
☐ Add [wer_tool_rankings] shortcode
☐ Publish page
☐ Test rankings load
☐ Test language switching
☐ Share link with users
```

---

## 🚀 One-Click Installation Summary

**If your hosting supports it:**

1. WordPress Admin → **Plugins → Add New**
2. Click **Upload Plugin**
3. Select **wer-tool-rankings.php**
4. Click **Install Now**
5. Click **Activate Plugin**
6. Done! ✅

---

## 📊 Expected Data Format

Your API returns:

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
      ...
    }
  }
}
```

Plugin sorts by `average_wer` (ascending) and displays top 10.

---

## 🎯 Feature Overview

✅ Language selector (4 Indian languages)
✅ Top 10 rankings table
✅ 2-column layout (Rank + AI Tool)
✅ Medals for top 3 (🥇🥈🥉)
✅ Responsive mobile design
✅ Loading spinner
✅ Error handling
✅ Real-time data from backend
✅ Easy shortcode integration
✅ Fully customizable

---

## 💡 Pro Tips

- Add to sidebar widget for quick access
- Create pinned menu for easy navigation
- Use custom WordPress hooks to display anywhere
- Monitor Render logs for backend issues
- Test with different months/years
- Backup your WordPress site regularly
- Check for plugin updates periodically

---

**Setup Time: ~5-10 minutes ⏱️**

**User Training: ~2 minutes 📚**

**Ready to go! 🚀**
