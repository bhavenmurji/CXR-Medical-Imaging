# USB Storage Setup Guide

## Overview
This project uses an external USB drive (BhavensUSB - 250GB) to store large medical imaging datasets, keeping your local MacBook storage free.

## USB Information
- **Name**: BhavensUSB
- **Capacity**: 250GB
- **Mount Point**: `/Volumes/BhavensUSB`
- **Project Data**: `/Volumes/BhavensUSB/CXR-Datasets`

## Directory Structure on USB

```
/Volumes/BhavensUSB/CXR-Datasets/
├── raw/                    # Original downloaded datasets
│   ├── nih-cxr14/         # NIH Chest X-ray14 (42GB)
│   ├── chexpert/          # CheXpert dataset
│   └── mimic-cxr/         # MIMIC-CXR dataset
├── processed/              # Processed/cleaned data
├── extracted/              # Extracted image-caption pairs
└── metadata/              # Dataset metadata and indices
```

## Quick Start

### 1. Download Dataset to USB

```bash
# Make sure USB is connected
ls /Volumes/BhavensUSB

# Activate Python environment
source venv/bin/activate

# Download NIH CXR-14 to USB (42GB)
./scripts/download_to_usb.sh
```

### 2. Process Data from USB

```bash
# Python scripts will automatically use paths from .env file
python process_chexpert_local.py

# Or specify USB path explicitly
python your_script.py --data-root /Volumes/BhavensUSB/CXR-Datasets
```

### 3. Check USB Usage

```bash
# Check available space
df -h /Volumes/BhavensUSB

# Check dataset sizes
du -sh /Volumes/BhavensUSB/CXR-Datasets/raw/*
```

## Environment Configuration

The `.env` file configures where data is stored:

```bash
DATA_ROOT=/Volumes/BhavensUSB/CXR-Datasets
RAW_DATA=${DATA_ROOT}/raw
PROCESSED_DATA=${DATA_ROOT}/processed
EXTRACTED_DATA=${DATA_ROOT}/extracted
METADATA_PATH=${DATA_ROOT}/metadata
```

## Important Notes

### When USB is Connected ✅
- Download datasets directly to USB
- Process images from USB
- Extract image-caption pairs to USB
- All large files stay on USB

### When USB is Disconnected ⚠️
- Scripts will fail if they try to access USB path
- Mount USB before running data processing
- Metadata and code stay on local MacBook

### Best Practices

1. **Always check USB is mounted first**:
   ```bash
   ls /Volumes/BhavensUSB || echo "USB not connected!"
   ```

2. **Safely eject when done**:
   - Don't eject while processing data
   - Check no processes are using USB
   - Use macOS "Eject" button

3. **Backup important results**:
   - USB is portable storage, not backup
   - Copy processed results to cloud/local when complete

4. **Monitor space**:
   ```bash
   # Before downloading new dataset
   df -h /Volumes/BhavensUSB
   ```

## Dataset Sizes (Approximate)

| Dataset | Size | Status |
|---------|------|--------|
| NIH CXR-14 | 42GB | Ready to download |
| CheXpert | 11GB | Requires registration |
| MIMIC-CXR | 377GB | Requires credentialed access |
| PadChest | 1TB+ | Very large |

## Troubleshooting

### USB not found
```bash
# Check if mounted
mount | grep BhavensUSB

# Remount if needed
diskutil list
diskutil mount /dev/diskX
```

### Out of space
```bash
# Find what's using space
du -sh /Volumes/BhavensUSB/CXR-Datasets/*

# Clean up temporary files
rm -rf /Volumes/BhavensUSB/CXR-Datasets/raw/*/*.zip
```

### Slow USB access
- USB 3.0 drive should give 100+ MB/s
- USB 2.0 will be much slower (20-40 MB/s)
- Check connection type in System Information

## Next Steps

1. ✅ USB connected and configured
2. ⏳ Download NIH CXR-14 dataset (run `./scripts/download_to_usb.sh`)
3. ⏳ Process images and extract captions
4. ⏳ Train models on processed data

---

**Storage Summary**:
- Local MacBook: Code, metadata, small files (~10GB)
- BhavensUSB: Large datasets, processed images (up to 250GB)
