# CXR Dataset Download Status Report

Generated: October 1, 2025

## Summary

**Disk Space:** 957.7 GB available (sufficient for ~470GB download)

**Current Status:**
- ✅ Batch 1 (validation): Downloaded (486 MB)
- ❌ Batches 2-11 (training): Azure SAS URLs expired

## Issues Identified

### 1. NIH Download Issue
- **Status:** Logged downloads but no images saved
- **Cause:** The Radiopaedia dataset was downloaded from Kaggle (3,783 images), not NIH ChestX-ray14
- **Evidence:**
  - `NIH/metadata/download_log.json` contains 7,104 entries for radiopaedia images
  - `NIH/Images` directory is empty (0 PNG files)
  - Only `NIH/captions` has caption files
- **Resolution Needed:** Configure proper NIH download source

### 2. CheXpert Training Batches
- **Status:** Azure SAS URLs have expired
- **Issue:**
  - HTTP 404 errors for batches 2-11
  - HTTP 416 (Range Not Satisfiable) for batch 1 (already complete)
- **Cause:** SAS tokens expired on 2025-10-31
- **Resolution:** Need to regenerate Stanford Azure SAS URLs

## Working Data

### CheXpert Validation Set
- **Location:** `temp/chexpert_full/CheXpert-v1.0 batch 1 (validate & csv)/`
- **Status:** ✅ Complete
- **Size:** 486 MB
- **Contents:** Validation images and CSV

### Radiopaedia Dataset
- **Location:** `NIH/` directory (misnamed)
- **Status:** ✅ Downloaded (via Kaggle)
- **Images:** 3,783 chest X-rays
- **Size:** 505 MB metadata + captions

### Master Index
- **Location:** `metadata/master_index.csv`
- **Images cataloged:** 3,783 (all Radiopaedia)
- **Captions:** 3,783 text files

## Next Steps

### Immediate Actions

1. **Get Fresh CheXpert URLs**
   - Request new Stanford Azure SAS tokens
   - Alternative: Use Stanford's official download process
   - URL: https://stanfordmlgroup.github.io/competitions/chexpert/

2. **Fix NIH Download**
   - Option A: Use Kaggle API (requires ~150GB disk space)
   - Option B: Use NIH Box.com direct links (12 batches × ~4GB each)
   - Current config in `cxr_dataset_downloader/downloaders/nih_downloader.py`

3. **Verify Existing Data**
   - Extract batch1.zip validation data
   - Process Radiopaedia images (already downloaded)
   - Generate proper master index

### Scripts Created

1. **`scripts/download_chexpert_training.py`**
   - Parallel batch downloader (2-3 concurrent streams)
   - Resume capability with progress tracking
   - Handles 470GB across 11 batches
   - **Status:** Ready but needs fresh URLs

2. **`scripts/monitor_downloads.sh`**
   - Real-time progress monitoring
   - Disk usage tracking
   - Batch completion status

## Resource Requirements

### CheXpert Training (Batches 2-11)
- **Size:** ~420 GB (11 batches × ~38GB average)
- **Time:** 2-8 hours with good connection
- **Parallel:** 2-3 concurrent downloads recommended

### NIH ChestX-ray14
- **Size:** ~45 GB compressed, ~100 GB extracted
- **Images:** 112,120 chest X-rays
- **Time:** 1-4 hours for full dataset

### Total Project Estimate
- **Combined Size:** ~600 GB
- **Available Space:** 957 GB ✅
- **Buffer:** 357 GB remaining

## File Organization

```
/Users/bhavenmurji/Development/MeData/Imaging/CXR/
├── Images/          (3,783 images - Radiopaedia only)
├── captions/        (3,783 caption files)
├── metadata/        (download logs, master index)
├── NIH/             (Radiopaedia data, misnamed)
│   ├── Images/      (empty, should contain NIH images)
│   └── metadata/    (7,104 radiopaedia entries)
├── temp/
│   └── chexpert_azure/
│       └── batch1.zip (486 MB - validation set)
└── scripts/
    ├── download_chexpert_training.py
    └── monitor_downloads.sh
```

## Recommendations

1. **Priority 1:** Get fresh CheXpert Azure URLs from Stanford
2. **Priority 2:** Complete NIH download using Kaggle API
3. **Priority 3:** Extract and process batch1 validation data
4. **Priority 4:** Generate comprehensive master index

## Commands to Resume

### Check Download Status
```bash
# Monitor active downloads
./scripts/monitor_downloads.sh

# Check progress file
cat temp/chexpert_azure/download_progress.json

# View download logs
tail -f logs/download.log
```

### When URLs are Updated
```bash
# Start parallel download (2 concurrent)
python3 scripts/download_chexpert_training.py --parallel 2

# Or sequential (safer)
python3 scripts/download_chexpert_training.py --parallel 1
```

### NIH Download
```bash
# Using the main downloader
cd cxr_dataset_downloader
python3 main.py download --source nih --no-resume
```
