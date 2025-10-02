#!/bin/bash

# Local Storage Cleanup Script
# IMPORTANT: Run this ONLY after confirming code is committed to git
# This will delete large dataset files that should only be processed in the cloud

set -e

echo "⚠️  WARNING: This will delete large local files to free up storage"
echo "Make sure your code is committed to git first!"
echo ""
echo "This will delete:"
echo "  - temp/ (760GB)"
echo "  - venv/ (146MB)"
echo "  - Images/ (968MB)"
echo "  - NIH/ (505MB)"
echo "  - captions/ (15MB)"
echo "  - metadata/ (25MB)"
echo "  - logs/ (92KB)"
echo ""
echo "Total space to be freed: ~761.6GB"
echo ""

read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "🗑️  Starting cleanup..."

# Remove temp directory (760GB)
if [ -d "temp" ]; then
    echo "Removing temp/ directory..."
    rm -rf temp/
    echo "✅ Removed temp/"
fi

# Remove Python virtual environment (146MB)
if [ -d "venv" ]; then
    echo "Removing venv/ directory..."
    rm -rf venv/
    echo "✅ Removed venv/"
fi

# Remove downloaded images (968MB)
if [ -d "Images" ]; then
    echo "Removing Images/ directory..."
    rm -rf Images/
    echo "✅ Removed Images/"
fi

# Remove NIH dataset (505MB)
if [ -d "NIH" ]; then
    echo "Removing NIH/ directory..."
    rm -rf NIH/
    echo "✅ Removed NIH/"
fi

# Remove captions (15MB)
if [ -d "captions" ]; then
    echo "Removing captions/ directory..."
    rm -rf captions/
    echo "✅ Removed captions/"
fi

# Remove metadata (25MB)
if [ -d "metadata" ]; then
    echo "Removing metadata/ directory..."
    rm -rf metadata/
    echo "✅ Removed metadata/"
fi

# Remove logs (92KB)
if [ -d "logs" ]; then
    echo "Removing logs/ directory..."
    rm -rf logs/
    echo "✅ Removed logs/"
fi

# Remove dataset downloader cache
if [ -d "cxr_dataset_downloader" ]; then
    echo "Removing cxr_dataset_downloader/ cache..."
    rm -rf cxr_dataset_downloader/
    echo "✅ Removed cxr_dataset_downloader/"
fi

# Clean Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Removed Python cache"

echo ""
echo "🎉 Cleanup complete!"
echo ""
echo "Checking remaining disk usage:"
du -sh . 2>/dev/null

echo ""
echo "📦 Next steps:"
echo "1. Push this repository to GitHub"
echo "2. Open in GitHub Codespaces"
echo "3. Run ./scripts/setup_cloud_environment.sh"
echo "4. Download and process datasets in the cloud"
