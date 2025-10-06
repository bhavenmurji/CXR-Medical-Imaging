#!/bin/bash
# Download NIH CXR-14 dataset to external USB drive
# Stores data on BhavensUSB to save local disk space

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Use USB path or fallback to local
DATA_ROOT=${DATA_ROOT:-"/Volumes/BhavensUSB/CXR-Datasets"}
USB_PATH="/Volumes/BhavensUSB"

# Check if USB is mounted
if [ ! -d "$USB_PATH" ]; then
    echo "❌ Error: BhavensUSB not found at $USB_PATH"
    echo "Please connect the USB drive and try again."
    exit 1
fi

echo "📥 Downloading NIH Chest X-ray14 dataset to USB..."
echo "💾 Storage location: $DATA_ROOT/raw/nih-cxr14"
echo ""

# Check available USB space
echo "💾 USB Storage Status:"
df -h "$USB_PATH" | grep -v Filesystem
echo ""

# Create directory structure
mkdir -p "$DATA_ROOT/raw/nih-cxr14"
cd "$DATA_ROOT/raw/nih-cxr14"

echo "⏬ Starting Kaggle download (42GB)..."
echo "This will take 30-60 minutes depending on your connection."
echo ""

# Download using Kaggle API
kaggle datasets download -d nih-chest-xrays/data --force

echo ""
echo "📦 Extracting archive..."
unzip -q data.zip

echo ""
echo "🧹 Cleaning up zip file to save space..."
rm data.zip

echo ""
echo "✅ Download complete!"
echo ""
echo "📊 Dataset location:"
echo "   $DATA_ROOT/raw/nih-cxr14"
echo ""
echo "📁 Contents:"
ls -lh

echo ""
echo "💾 USB disk usage:"
df -h "$USB_PATH"
du -sh "$DATA_ROOT/raw/nih-cxr14"

cd -

echo ""
echo "🎯 Next steps:"
echo "1. Verify data: ls /Volumes/BhavensUSB/CXR-Datasets/raw/nih-cxr14"
echo "2. Process images with Python scripts"
echo "3. USB can be safely ejected when not processing"
