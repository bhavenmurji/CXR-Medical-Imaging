#!/bin/bash
# Simple Codespaces Setup Script - Run this if automatic setup fails

set -e

echo "🚀 Setting up Python environment in Codespaces..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Create directories
echo "📁 Creating directories..."
mkdir -p data/{raw,processed,extracted}
mkdir -p data/datasets/{mimic-cxr,chexpert,nih-cxr14,padchest}
mkdir -p models outputs/{logs,reports,visualizations} temp

# Install requirements
echo "📚 Installing Python packages (this may take a few minutes)..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "💾 Available disk space:"
df -h /workspaces

echo ""
echo "⚡ IMPORTANT: Activate the virtual environment before running Python:"
echo "   source venv/bin/activate"
echo ""
echo "🎯 Next steps:"
echo "   1. Activate venv: source venv/bin/activate"
echo "   2. Configure Kaggle credentials: mkdir -p ~/.kaggle && nano ~/.kaggle/kaggle.json"
echo "   3. Run dataset downloads: ./scripts/download_datasets.sh nih-cxr14"
echo "   4. Process datasets with Python scripts"
