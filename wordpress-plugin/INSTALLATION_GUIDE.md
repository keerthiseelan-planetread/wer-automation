# 🚀 WordPress Plugin Installation & Usage Guide

Complete step-by-step instructions to install and use the WER Tool Rankings plugin on your WordPress site.

---

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ WordPress site installed and running
- ✅ Admin access to WordPress dashboard
- ✅ FastAPI backend running at: `https://wer-automation-api.onrender.com`
- ✅ MongoDB database with tool summary metrics data
- ✅ File Manager access (FTP/SFTP) or WordPress plugin upload capability

---

## 📝 Step 1: Prepare the Plugin File

### Option A: Download from GitHub
1. Go to: https://github.com/keerthiseelan-planetread/wer-automation
2. Navigate to: `wordpress-plugin/wer-tool-rankings.php`
3. Click **Raw** to view raw code
4. Right-click → **Save As** → Save as `wer-tool-rankings.php`

### Option B: Copy from Local Folder
- File location: `f:\Office Work\wer-automation\wordpress-plugin\wer-tool-rankings.php`
- Copy this file to your desktop or downloads folder

---

## 🔧 Step 2: Create Plugin Folder in WordPress

### Via File Manager (FTP/SFTP):
1. Connect to your WordPress hosting using FTP client (FileZilla, WinSCP, etc.)
2. Navigate to: `/public_html/wp-content/plugins/`
3. Create new folder named: `wer-tool-rankings`
4. Upload `wer-tool-rankings.php` into this folder

**Final path should be:**
```
/public_html/wp-content/plugins/wer-tool-rankings/wer-tool-rankings.php
```

### Via WordPress File Manager (if available):
1. Go to WordPress Admin → Tools → File Manager
2. Navigate to: `wp-content/plugins/`
3. Right-click → Create Folder → Name it `wer-tool-rankings`
4. Upload `wer-tool-rankings.php` to this folder

---

## 🔌 Step 3: Activate the Plugin

### In WordPress Dashboard:
1. **Log in** to WordPress Admin: `https://yoursite.com/wp-admin/`
2. Go to: **Plugins** (left sidebar)
3. Search for: **"WER Tool Rankings"**
4. Click **Activate**

✅ You should see a green message: "Plugin activated"

---

## 📄 Step 4: Create a New Page/Post

### Create a New Page:
1. Go to: **Pages** → **Add New**
2. **Title**: "AI Tool Rankings" (or your preferred name)
3. **Status**: Publish (after adding content)
4. Click **Add Block** or **Edit** in the content area

### Create a New Post (Alternative):
1. Go to: **Posts** → **Add New**
2. **Title**: "AI Tool Rankings"
3. **Status**: Publish (after adding content)

---

## 🎯 Step 5: Add the Shortcode

### In Page/Post Content:

**Option 1: Simple Usage (Recommended)**
```
[wer_tool_rankings]
```

**Option 2: Custom Settings**
```
[wer_tool_rankings year="2024" month="January"]
```

**Option 3: Custom Backend URL**
```
[wer_tool_rankings year="2024" month="January" backend_url="https://wer-automation-api.onrender.com"]
```

### How to Add (Block Editor):
1. Click **+ Add Block**
2. Search for: **"Paragraph"**
3. Type or paste the shortcode:
   ```
   [wer_tool_rankings]
   ```

### How to Add (Classic Editor):
1. Click in the text area
2. Type or paste the shortcode:
   ```
   [wer_tool_rankings]
   ```

---

## 📚 Step 6: Publish the Page

1. Click **Publish** button
2. Wait for confirmation message
3. Click **View Page** to see the live rankings

---

## ✨ Step 7: What You'll See

### Page Display:

```
═══════════════════════════════════════════════════════════════
     🏆 AI Tools Rankings - Word Error Rate
     Top 10 tools ranked by lowest average WER (Lower is Better)
═══════════════════════════════════════════════════════════════

   Language: [Hindi ▼]    [Load Rankings]

┌─────────────────────────────────────────────────────────────┐
│ Rank  │  AI Tool                                            │
├─────────────────────────────────────────────────────────────┤
│ 🥇    │ Whisper                                             │
│ 🥈    │ Google Speech                                       │
│ 🥉    │ AWS Transcribe                                      │
│ #4    │ Azure Speech                                        │
│ #5    │ IBM Watson                                          │
│ #6    │ Deepgram                                            │
│ #7    │ Descript                                            │
│ #8    │ Rev.ai                                              │
│ #9    │ AssemblyAI                                          │
│ #10   │ CloudAPI                                            │
└─────────────────────────────────────────────────────────────┘

Data from WER Automation Backend | Year: 2024 | Month: January
═══════════════════════════════════════════════════════════════
```

---

## 🎨 Step 8: Customize (Optional)

### Change Available Languages

Edit the plugin file and modify the language options:

1. FTP → `/wp-content/plugins/wer-tool-rankings/wer-tool-rankings.php`
2. Find this section (around line 250):
```php
<select id="wer-language-select">
    <option value="hi">Hindi</option>
    <option value="pa">Punjabi</option>
    <option value="te">Telugu</option>
    <option value="mr">Marathi</option>
</select>
```

3. To add more languages, add new lines:
```php
<option value="bn">Bengali</option>
<option value="kn">Kannada</option>
```

### Change Page Title

Find this section (around line 225):
```php
<h2>🏆 AI Tools Rankings - Word Error Rate</h2>
<p>Top 10 tools ranked by lowest average WER (Lower is Better)</p>
```

Edit to your preferred title.

### Change Colors/Styling

Find the `<style>` section (lines 50-220) and modify:
- `#0073aa` = Main blue color
- `#005a87` = Dark blue color
- `#f9f9f9` = Background color

---

## 🧪 Step 9: Test the Plugin

### Test 1: Language Selection
1. Visit your WordPress page with the plugin
2. **Select different languages** from the dropdown:
   - Hindi
   - Punjabi
   - Telugu
   - Marathi
3. Each selection should update the results

### Test 2: Load Rankings
1. Click **"Load Rankings"** button
2. You should see:
   - Loading spinner briefly
   - Table appears with top 10 tools
   - Tools ranked by lowest WER

### Test 3: Check Data
1. Open browser **Developer Tools** (Press F12)
2. Go to **Console** tab
3. Click "Load Rankings"
4. Check for any red error messages
5. Data should show without errors

### Test 4: Mobile Responsiveness
1. Open page on **mobile phone** or tablet
2. Verify:
   - Language dropdown is visible
   - Table is readable (not too wide)
   - Button is clickable
   - Rankings display properly

---

## 🔍 Step 10: Verify Backend Connection

### Check if Backend is Running:

1. Open new browser tab
2. Visit: `https://wer-automation-api.onrender.com/`
3. You should see:
```json
{"message":"WER Backend Running 🚀"}
```

✅ If you see this, backend is running correctly.

### Check API Endpoint:

1. Go to: `https://wer-automation-api.onrender.com/api/wer/get-tool-summary-metrics?year=2024&month=January&language=hi`
2. You should see JSON data with tool metrics
3. If you see `{"status":"warning", "message":"No metrics found"}`, there's no data for that language

---

## ⚙️ Step 11: Configuration Options

### Using Shortcode Parameters:

**Default (Current Month/Year):**
```
[wer_tool_rankings]
```

**Specific Month:**
```
[wer_tool_rankings month="January"]
```

**Specific Year:**
```
[wer_tool_rankings year="2024"]
```

**Both Year & Month:**
```
[wer_tool_rankings year="2024" month="February"]
```

**Custom Backend URL:**
```
[wer_tool_rankings backend_url="https://your-custom-api.com"]
```

**All Parameters Combined:**
```
[wer_tool_rankings year="2024" month="March" backend_url="https://wer-automation-api.onrender.com"]
```

---

## 🐛 Troubleshooting

### Problem: Plugin Not Showing in Plugins List

**Solution:**
1. Check file path: `/wp-content/plugins/wer-tool-rankings/wer-tool-rankings.php`
2. Verify filename is exactly: `wer-tool-rankings.php`
3. Reload WordPress admin page (Ctrl+F5)
4. Check file permissions are 644 or 755

### Problem: Shortcode Shows as Text

**Solution:**
1. Verify plugin is **Activated** (not just installed)
2. Go to Plugins → Check "WER Tool Rankings" is marked as Active
3. Use correct shortcode: `[wer_tool_rankings]`
4. Clear WordPress cache if using a caching plugin

### Problem: Table Shows Loading Spinner Forever

**Solution:**
1. **Check backend is running:**
   ```
   https://wer-automation-api.onrender.com/
   ```
2. **Check browser console (F12)** for errors
3. **Check language has data:**
   - Try "Hello" in the dropdown
   - Not all languages may have metrics
4. **Check CORS is enabled** on backend
   - Should already be configured in FastAPI

### Problem: No Data/Warning Message

**Solution:**
1. Check MongoDB has metrics for selected language
2. Verify data was uploaded to backend:
   ```
   https://wer-automation-api.onrender.com/api/wer/get-tool-summary-metrics?year=2024&month=January&language=hi
   ```
3. Try a different language or month

### Problem: Table Looks Broken/Misaligned

**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Disable other CSS-related plugins temporarily
3. Check WordPress theme is compatible
4. Try a different browser (Chrome, Firefox, etc.)
5. Check window width is not too narrow

### Problem: "Error loading rankings" Message

**Solution:**
1. Open browser **Console** (F12)
2. Look for detailed error messages
3. Common causes:
   - Backend URL is incorrect
   - Backend is down
   - CORS is blocked
   - Network connection issue
4. Test backend URL in new tab manually

---

## 📊 Step 12: Monitor Usage (Optional)

### View Page Analytics:
1. Go to **Pages** in WordPress
2. Find your "AI Tool Rankings" page
3. Check **Views** and **Engagement**

### Monitor Backend:
1. Go to Render Dashboard: https://dashboard.render.com/
2. Select **wer-automation-api** service
3. View **Logs** for any errors
4. Check **Metrics** for usage patterns

---

## ✅ Verification Checklist

Before declaring installation complete, verify:

- [ ] Plugin folder exists at `/wp-content/plugins/wer-tool-rankings/`
- [ ] File `wer-tool-rankings.php` exists in plugin folder
- [ ] Plugin is **Activated** in WordPress admin
- [ ] Page/Post created with shortcode `[wer_tool_rankings]`
- [ ] Page displays without errors
- [ ] Language dropdown shows: Hindi, Punjabi, Telugu, Marathi
- [ ] "Load Rankings" button works
- [ ] Table displays top 10 tools with 2 columns
- [ ] Backend API returns data
- [ ] No errors in browser console (F12)
- [ ] Mobile view looks good
- [ ] Different languages load different data

---

## 🎓 Advanced: Multiple Instances

You can add the plugin to **multiple pages** with different configurations:

### Page 1: Hindi Rankings
```
https://yoursite.com/hindi-tools
[wer_tool_rankings year="2024" month="January"]
```

### Page 2: Punjabi Rankings
```
https://yoursite.com/punjabi-tools
[wer_tool_rankings year="2024" month="January"]
```

Each page will show different language data based on user selection!

---

## 🚀 Next Steps

1. ✅ Install plugin following steps 1-3
2. ✅ Create page following steps 4-6
3. ✅ Test functionality following steps 9-10
4. ✅ Customize if needed (step 8)
5. ✅ Share link with users!

---

## 📞 Support

**If you encounter issues:**

1. Check browser console for errors (F12)
2. Verify backend is running
3. Check MongoDB has data for selected language
4. Review troubleshooting section above
5. Check WordPress plugin compatibility

**For backend issues:**
- Render logs: https://dashboard.render.com/
- FastAPI documentation: https://fastapi.tiangolo.com/
- MongoDB connection: Check .env file

---

## 📚 File Structure Reference

```
Your WordPress / wp-content / plugins /
│
└── wer-tool-rankings/
    ├── wer-tool-rankings.php    ← Main plugin file
    ├── README.md                ← Plugin description
    └── INSTALLATION_GUIDE.md    ← This file
```

---

**Installation Complete! 🎉**

Your WordPress site now displays AI tool rankings powered by your WER Automation system!

