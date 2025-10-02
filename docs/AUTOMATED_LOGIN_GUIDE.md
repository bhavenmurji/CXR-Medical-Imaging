# Automated CheXpert Login & URL Retrieval

This guide explains how to use the automated browser script to login to Stanford CheXpert and retrieve fresh download URLs.

## Prerequisites

✅ **Already set up for you:**
- Python virtual environment (`venv/`)
- Playwright library installed
- Chromium browser (installing...)

## Quick Start

### Option 1: Interactive (Recommended for first time)

Run the script and enter credentials when prompted:

```bash
./scripts/run_chexpert_login.sh
```

This will:
1. Launch Chrome browser (visible)
2. Navigate to CheXpert page
3. Prompt you for email and password
4. Attempt to login and retrieve URLs
5. Take screenshots at each step (saved to `logs/`)
6. Keep browser open for manual verification
7. Save URLs to console and optionally to file

### Option 2: With Command Line Arguments

```bash
# Provide email as argument
./scripts/run_chexpert_login.sh --email your.email@stanford.edu

# Provide both email and password
./scripts/run_chexpert_login.sh --email your.email@stanford.edu --password yourpass

# Save URLs to file
./scripts/run_chexpert_login.sh --save chexpert_urls.json
```

### Option 3: Using Environment Variables (Most Secure)

```bash
# Set credentials as environment variables
export CHEXPERT_EMAIL="your.email@stanford.edu"
export CHEXPERT_PASSWORD="yourpassword"

# Run script (will use env vars automatically)
./scripts/run_chexpert_login.sh --save chexpert_urls.json
```

### Option 4: Headless Mode (No Browser Window)

```bash
# Run without showing browser window
./scripts/run_chexpert_login.sh --headless --save urls.json
```

## What the Script Does

1. **Launches Chrome** - Opens a real Chrome browser window
2. **Navigates to CheXpert** - Goes to Stanford CheXpert competition page
3. **Looks for Download** - Searches for download button/link
4. **Handles Login** - If redirected to login page, fills credentials
5. **Extracts URLs** - Searches page for Azure blob storage URLs
6. **Takes Screenshots** - Captures images at each step for debugging
7. **Saves Results** - Outputs URLs to console and optionally to JSON file

## Screenshots Captured

All screenshots are saved to `logs/` directory:

- `chexpert_01_initial.png` - Initial CheXpert page
- `chexpert_02_no_download.png` - If download button not found
- `chexpert_03_after_click.png` - After clicking download
- `chexpert_04_aimi_login.png` - Login page (if redirected)
- `chexpert_05_before_submit.png` - Before submitting login
- `chexpert_06_after_login.png` - After successful login
- `chexpert_07_final.png` - Final page with URLs
- `chexpert_error.png` - If any error occurs

## Manual Intervention

If the automation doesn't find URLs automatically:

1. **Browser stays open** - You can manually navigate
2. **Screenshots available** - Check `logs/` for captured images
3. **Page HTML saved** - Review `logs/chexpert_final_page.html`
4. **Manual extraction** - Copy URLs from browser

### Manual Steps if Needed:

1. When browser opens, navigate to downloads manually
2. Accept any terms/agreements
3. Right-click on download links → Copy Link Address
4. Paste URLs into `scripts/download_chexpert_training.py`

## Output Format

If URLs are found, they'll be printed like this:

```
✅ Found 11 download URLs:

batch1:
  https://aimistanforddatasets01.blob.core.windows.net/chexpertchestxrays-u20210408/CheXpert-v1.0%20batch%201...

batch2:
  https://aimistanforddatasets01.blob.core.windows.net/chexpertchestxrays-u20210408/CheXpert-v1.0%20batch%202...
```

### JSON Output (with --save flag)

```json
{
  "timestamp": "2025-10-01T12:00:00",
  "email": "your.email@stanford.edu",
  "urls": {
    "batch1": "https://aimistanforddatasets01.blob.core.windows.net/...",
    "batch2": "https://aimistanforddatasets01.blob.core.windows.net/...",
    ...
  }
}
```

## After Getting URLs

Once you have the URLs:

### Automatic Update (Coming Soon)

```bash
# Will be implemented: automatically update download script
./scripts/update_download_urls.sh chexpert_urls.json
```

### Manual Update

1. Open `scripts/download_chexpert_training.py`
2. Find the `BATCH_URLS` dictionary (lines 22-78)
3. Replace each URL with the new ones
4. Save the file

Example:
```python
BATCH_URLS = {
    "batch1": {
        "url": "YOUR_NEW_URL_HERE",  # ← Paste new URL
        "size_mb": 509,
        "filename": "batch1.zip"
    },
    # ... repeat for all batches
}
```

## Troubleshooting

### Playwright Not Found

```bash
source venv/bin/activate
pip install playwright
playwright install chromium
```

### Login Failed

1. Check credentials are correct
2. Try logging in manually in the browser first
3. Check if Stanford requires 2FA (may need manual intervention)
4. Review screenshots in `logs/` directory

### No URLs Found

1. Check `logs/chexpert_final_page.html` - search for "blob.core.windows.net"
2. The page might require accepting terms/agreements first
3. URLs might be behind JavaScript/AJAX - check Network tab manually
4. Try running again in non-headless mode to see what's happening

### Chrome Not Found

If using system Chrome fails:

```bash
# Install Chromium via Playwright
source venv/bin/activate
playwright install chromium

# Then modify script to use Chromium instead of Chrome
```

## Security Notes

⚠️ **Never commit credentials to git!**

✅ **Best practices:**
- Use environment variables for credentials
- Add `chexpert_urls.json` to `.gitignore`
- Don't share screenshots (may contain session tokens)
- URLs contain SAS tokens - treat as sensitive

## Complete Example Workflow

```bash
# 1. Set credentials (one time)
export CHEXPERT_EMAIL="your.email@stanford.edu"
export CHEXPERT_PASSWORD="yourpassword"

# 2. Run automated retrieval
./scripts/run_chexpert_login.sh --save chexpert_urls.json

# 3. Check output
cat chexpert_urls.json

# 4. Update download script (manual for now)
nano scripts/download_chexpert_training.py

# 5. Start downloads
python3 scripts/download_chexpert_training.py --parallel 2

# 6. Monitor in another terminal
./scripts/monitor_downloads.sh
```

## Advanced Options

### Custom Browser Path

Edit `scripts/get_chexpert_urls.py` and modify:

```python
browser = await p.chromium.launch(
    headless=headless,
    executable_path='/path/to/your/chrome',  # Add this line
    args=['--start-maximized']
)
```

### Timeout Adjustments

If pages load slowly, increase timeouts in script:

```python
await page.wait_for_timeout(5000)  # Increase from 2000 to 5000ms
```

### Debug Mode

For more verbose output:

```python
# Add at top of script
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

If automation fails:
1. Check screenshots in `logs/`
2. Review HTML output in `logs/chexpert_final_page.html`
3. Try manual login in browser
4. Contact Stanford support for download access
5. Report issues with script behavior

---

**Next:** Once URLs are retrieved, follow [TROUBLESHOOTING_SUMMARY.md](TROUBLESHOOTING_SUMMARY.md) to update and run the download script.
