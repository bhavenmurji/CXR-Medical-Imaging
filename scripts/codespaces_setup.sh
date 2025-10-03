#!/bin/bash
# Simple Codespaces Setup Script - Run this if automatic setup fails

set -e

echo "🚀 Setting up Python environment in Codespaces..."

# Download and install pip
echo "📦 Installing pip..."
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py --user
rm /tmp/get-pip.py

# Add pip to PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Upgrade pip
echo "⬆️  Upgrading pip..."
python3 -m pip install --upgrade pip --user

# Create directories
echo "📁 Creating directories..."
mkdir -p data/{raw,processed,extracted}
mkdir -p data/datasets/{mimic-cxr,chexpert,nih-cxr14,padchest}
mkdir -p models outputs/{logs,reports,visualizations} temp

# Install requirements
echo "📚 Installing Python packages (this may take a few minutes)..."
python3 -m pip install -r requirements.txt --user

echo ""
echo "✅ Setup complete!"
echo ""
echo "💾 Available disk space:"
df -h /workspaces

echo ""
echo "🎯 Next steps:"
echo "   1. Configure Kaggle credentials: mkdir -p ~/.kaggle && nano ~/.kaggle/kaggle.json"
echo "   2. Run dataset downloads: ./scripts/download_datasets.sh nih-cxr14"
echo "   3. Process datasets with Python scripts"
