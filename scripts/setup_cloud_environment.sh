#!/bin/bash

# Cloud Environment Setup Script for CXR Dataset Processing
# This script sets up the environment in GitHub Codespaces for processing large medical imaging datasets

set -e

echo "🚀 Setting up CXR Medical Imaging Environment..."

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data/{raw,processed,extracted}
mkdir -p data/datasets/{mimic-cxr,chexpert,nih-cxr14,padchest}
mkdir -p models
mkdir -p outputs/{logs,reports,visualizations}
mkdir -p temp

# Set up Python environment
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Configure Kaggle credentials if provided
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "⚠️  Kaggle credentials not found."
    echo "To download datasets, create ~/.kaggle/kaggle.json with your API credentials:"
    echo '{"username":"your_username","key":"your_key"}'
    mkdir -p ~/.kaggle
fi

# Check available disk space
echo "💾 Checking available disk space..."
df -h /workspace

echo "✅ Environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your Kaggle API credentials to ~/.kaggle/kaggle.json"
echo "2. Run dataset download scripts in scripts/download_datasets.sh"
echo "3. Process datasets using scripts in src/"
