# GitHub Actions - Daily WER Automation Scheduler

Complete setup guide for running WER automation on schedule using GitHub Actions (completely free).

---

## Overview

**What is GitHub Actions?**
- GitHub's built-in CI/CD automation service
- Runs on GitHub's servers (not your Render instance)
- Completely free for public repos, 2,000 min/month for private repos
- Runs automatically on a schedule regardless of your app status

**How it works:**
```
GitHub Actions (Daily, 2:00 AM UTC)
    ↓ (Runs independently of Render)
    ↓ Installs dependencies
    ↓ Creates service account file from secrets
    ↓ Runs: python scripts/run_scheduler_once.py
    ↓ Calls: run_all_folders() from app
    ↓ Updates: MongoDB with latest WER data
    ↓ Logs: Full execution logs in GitHub
```

---

## Setup Instructions

### Step 1: Add GitHub Secrets

Secrets are encrypted environment variables that GitHub Actions uses securely.

**How to add secrets:**
1. Go to your GitHub repository
2. Click **Settings** (top right)
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

**Add these 4 secrets:**

| Secret Name | Value | Where to get it |
|------------|-------|-----------------|
| `MONGODB_URI` | Your MongoDB connection string | From your `.env` file |
| `GOOGLE_DRIVE_ROOT_ID` | Google Drive root folder ID | From your `.env` file |
| `ALLOWED_USERS` | Comma-separated allowed users | From your `.env` file |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | **Full JSON content** of service account file | See below ↓ |

**Getting GOOGLE_SERVICE_ACCOUNT_JSON:**
1. Open your `app/service.account.json` file
2. Copy the **entire content** (all JSON)
3. In GitHub Secrets, paste it exactly as is (multi-line is fine)
4. Name it: `GOOGLE_SERVICE_ACCOUNT_JSON`

Example:
```json
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  ...
}
```

---

### Step 2: Verify Workflow File

The workflow file should already be at: `.github/workflows/scheduler.yml`

Check that it exists:
1. Go to your GitHub repo
2. Click **Actions** tab
3. You should see **"Daily WER Automation Scheduler"** workflow listed

---

### Step 3: Test the Workflow

**Manual test (before automation):**
1. Go to **Actions** tab in GitHub
2. Click **Daily WER Automation Scheduler** workflow
3. Click **Run workflow** → **Run workflow** button
4. Wait and watch the logs in real-time

Expected output in logs:
```
================================================================================
[SCHEDULER] WER Automation - GitHub Actions Edition
[SCHEDULER] Started at 2024-03-24 10:30:45 UTC
================================================================================
✓ All environment variables validated
================================================================================
[WER AUTOMATION JOB] Starting
[WER AUTOMATION JOB] Time: 2024-03-24 10:30:45 UTC
...
[WER AUTOMATION JOB] ✓ Completed successfully
```

---

## How to Monitor

### View Logs

1. Go to **Actions** tab
2. Click the latest workflow run
3. Click **run-scheduler** job
4. Scroll to see full output

### Check Execution History

**All scheduled runs are logged:**
- Click **Actions** → **Daily WER Automation Scheduler**
- You'll see all past and future scheduled runs

### Understand the Timeline

```
Each day:
  2:00 AM UTC ← GitHub Actions runs (exact time)
       ↓
  Logs appear in GitHub Actions
       ↓
  MongoDB updated with latest WER data
       ↓
  You can view results in Streamlit dashboard
```

---

## Customization

### Change Scheduled Time

Edit `.github/workflows/scheduler.yml`:

**Current (2:00 AM UTC):**
```yaml
schedule:
  - cron: '0 2 * * *'
```

**Cron format:** `minute hour day month weekday`

**Examples:**
- `0 0 * * *` → Midnight (00:00) UTC
- `0 6 * * *` → 6:00 AM UTC
- `0 14 * * *` → 2:00 PM UTC
- `0 2 * * 1` → 2:00 AM UTC, Mondays only
- `30 3 * * *` → 3:30 AM UTC

[Cron expression tool](https://crontab.guru/)

### Disable Scheduler

Option 1: Pause the workflow (temporary)
- Go to Actions → Workflow → Click "..." → Disable workflow

Option 2: Remove the schedule trigger (permanent)
- Edit `.github/workflows/scheduler.yml`
- Remove or comment out the schedule section
- Keep `workflow_dispatch` for manual triggers only

---

## Troubleshooting

### Job Failed - Check These:

**1. Secrets not set correctly**
```
Error: Missing environment variables
```
Solution: Go to Settings → Secrets and verify all 4 are added

**2. Service account file invalid**
```
Error: Service account file is not valid JSON
```
Solution: 
- Open `app/service.account.json` locally
- Ensure it's valid JSON (no extra quotes or escaping)
- Copy the raw content to GitHub secret

**3. MongoDB connection failed**
```
Error: Failed to connect to MongoDB
```
Solution: 
- Verify MONGODB_URI secret is correct
- Check MongoDB network settings allow GitHub's IP

**4. Google Drive access denied**
```
Error: unauthorized
```
Solution:
- Regenerate service account JSON from Google Cloud Console
- Update GitHub secret with new JSON

### Debug Mode

For detailed logs, manually trigger with debug:
1. Go to **Actions**
2. Click **Daily WER Automation Scheduler**
3. Click **Run workflow** dropdown
4. Enable debug logging (optional)
5. Click **Run workflow**

---

## Important Notes

✅ **What's free:**
- Unlimited workflow runs for public repos
- 2,000 min/month for private repos (usually enough for daily tasks)
- No extra cost beyond GitHub

✅ **Security:**
- Service account file never exposed (stored in secrets)
- All credentials encrypted by GitHub
- No sensitive data in logs

✅ **Reliability:**
- Runs on GitHub's infrastructure (99.9% uptime)
- Doesn't depend on your Render service
- Survives Render deployments/restarts

⚠️ **Limitations:**
- Cron accuracy: ±5 minutes (usually exact)
- Max 20 parallel workflows (plenty for one scheduler)
- Logs kept for 90 days

---

## Example: View Logs

After workflow runs, logs look like:

```
[SCHEDULER] WER Automation - GitHub Actions Edition
[SCHEDULER] Started at 2024-03-24 02:00:15 UTC
================================================================================
[SCHEDULER] ✓ All environment variables validated
================================================================================
[WER AUTOMATION JOB] Starting
[WER AUTOMATION JOB] Time: 2024-03-24 02:00:15 UTC
[WER AUTOMATION JOB] Platform: GitHub Actions
================================================================================
Processing year: 2024
Found 12 month folders
Processing month: 01-January
  Processing language: en
    ✓ Processed 45 files
    ✓ WER scores calculated
    ✓ Results stored in MongoDB
  Processing language: es
    ✓ Processed 32 files
    ✓ WER scores calculated
    ✓ Results stored in MongoDB
...
[WER AUTOMATION JOB] ✓ Completed successfully
[WER AUTOMATION JOB] Summary:
  • total_folders_processed: 24
  • successful_folders: 24
  • failed_folders: 0
  • start_time: 2024-03-24 02:00:15
  • end_time: 2024-03-24 02:15:32
  • duration_seconds: 917
================================================================================
```

---

## Next Steps

1. ✅ Add the 4 GitHub Secrets (Settings → Secrets)
2. ✅ Verify workflow file exists (.github/workflows/scheduler.yml)
3. ✅ Test workflow manually (Actions → Run workflow)
4. ✅ Monitor first automated run (check at 2:01 AM UTC tomorrow)
5. ✅ If tests pass, remove Procfile scheduler line (optional - to clean up)

---

## Questions?

- Check GitHub Actions tab for logs
- Look for error messages in workflow output
- Verify secrets in Settings → Secrets
- Test manually before relying on schedule
