#!/bin/bash
# Download NIH Chest X-ray14 from Kaggle (easier than Box.com)
# Requires: Kaggle credentials in ~/.kaggle/kaggle.json

set -e

echo "📥 Downloading NIH Chest X-ray14 dataset from Kaggle..."
echo "⚠️  This is 42GB and will take some time..."
echo ""

# Create directory
mkdir -p data/raw/nih-cxr14
cd data/raw/nih-cxr14

# Download using Kaggle API
echo "Starting download..."
kaggle datasets download -d nih-chest-xrays/data

echo ""
echo "📦 Extracting archive..."
unzip -q data.zip

echo ""
echo "🧹 Cleaning up..."
rm data.zip

echo ""
echo "✅ Download complete!"
echo ""
echo "📊 Dataset contents:"
ls -lh

echo ""
echo "💾 Disk usage:"
du -sh .

cd -
