# CheXpert Download Troubleshooting Summary

**Date:** October 1, 2025
**Status:** ⚠️ Blocked - URLs Expired

## Issue Summary

The CheXpert training batch downloads are **blocked** due to expired Azure SAS (Shared Access Signature) URLs.

### Error Messages
- **Batch 1 (validation):** HTTP 416 - Range Not Satisfiable (file already complete)
- **Batches 2-11 (training):** HTTP 404 - Not Found (URLs expired)

### Root Cause
The Azure blob storage URLs have time-limited SAS tokens that expired on **2025-10-31T14:45:57Z**. We're past that expiration date.

## What's Working

✅ **Download Infrastructure:**
- Parallel download script created and tested
- Progress tracking system implemented
- Monitoring dashboard functional
- 957 GB disk space available (sufficient)

✅ **Already Downloaded:**
- CheXpert Batch 1 (validation): 486 MB ✓
- Radiopaedia dataset: 3,783 images ✓

## What's Needed: Fresh URLs from Stanford

### Method 1: Official CheXpert Website (Recommended)

1. Go to: https://stanfordmlgroup.github.io/competitions/chexpert/
2. Click "Download" button
3. Sign in or create account
4. Request download access
5. You'll receive fresh Azure URLs (valid for ~30 days)

### Method 2: Stanford AIMI Website

1. Visit: https://aimi.stanford.edu/chexpert-chest-x-rays
2. Complete registration/data use agreement
3. Download links will be provided

### Method 3: Contact Stanford Directly

If automated methods don't work:
- Email: stanfordmlgroup@gmail.com
- Subject: "CheXpert Dataset Download - Expired URLs"

## How to Update the Script

Once you have fresh URLs:

1. **Open the download script:**
   ```bash
   nano scripts/download_chexpert_training.py
   # or use your preferred editor
   ```

2. **Update the BATCH_URLS dictionary (lines 22-78):**
   ```python
   BATCH_URLS = {
       "batch1": {
           "url": "YOUR_NEW_BATCH1_URL_HERE",
           "size_mb": 509,
           "filename": "batch1.zip"
       },
       "batch2": {
           "url": "YOUR_NEW_BATCH2_URL_HERE",
           "size_mb": 42000,
           "filename": "batch2.zip"
       },
       # ... etc for batches 3-11
   }
   ```

3. **Save the file**

## Once URLs are Updated - Run This:

```bash
# Change to project directory
cd /Users/bhavenmurji/Development/MeData/Imaging/CXR

# Option 1: Parallel download (recommended, 2 concurrent streams)
python3 scripts/download_chexpert_training.py --parallel 2

# Option 2: Sequential (slower but safer)
python3 scripts/download_chexpert_training.py --parallel 1

# Option 3: Maximum speed (3 concurrent, requires good connection)
python3 scripts/download_chexpert_training.py --parallel 3
```

## Monitoring Progress

**In another terminal window:**
```bash
cd /Users/bhavenmurji/Development/MeData/Imaging/CXR
./scripts/monitor_downloads.sh
```

**Or check progress file directly:**
```bash
cat temp/chexpert_azure/download_progress.json
```

**Or view logs:**
```bash
tail -f logs/download.log
```

## Expected Download Stats

- **Total Size:** ~420 GB (batches 2-11)
- **Duration:** 2-8 hours depending on connection speed
- **Batch 1:** Will be skipped (already complete at 486 MB)
- **Progress:** Automatically saved, can resume if interrupted

## Alternative: Use Smaller CheXpert-Small Dataset

If the full dataset is too large, Stanford also offers CheXpert-small:

```bash
# Already have this in temp/chexpert_full/CheXpert-v1.0-small/
# Much smaller: ~11 GB instead of 470 GB
# Contains 223,414 images (subset of full dataset)
```

## NIH ChestX-ray14 Issue (Separate Problem)

The NIH download also needs attention:
- Currently downloaded Radiopaedia (3,783 images) instead of NIH
- NIH requires ~150 GB for full dataset (112,120 images)
- Can be addressed after CheXpert issue is resolved

**To fix NIH later:**
```bash
cd cxr_dataset_downloader
python3 main.py download --source nih
```

## Quick Reference

| Item | Status | Size | Action |
|------|--------|------|--------|
| CheXpert Batch 1 | ✅ Complete | 486 MB | None needed |
| CheXpert Batches 2-11 | ❌ Blocked | ~420 GB | Get fresh URLs |
| Radiopaedia | ✅ Complete | 505 MB | None needed |
| NIH ChestX-ray14 | ⏳ Pending | ~150 GB | Fix after CheXpert |
| Disk Space | ✅ Available | 957 GB | Sufficient |

## Support

If you encounter issues:
1. Check `docs/DOWNLOAD_STATUS.md` for detailed status
2. Review `logs/download.log` for error messages
3. Run `./scripts/monitor_downloads.sh` for real-time status

---
**Next Action:** Get fresh CheXpert URLs from Stanford, then update the script and restart downloads.
