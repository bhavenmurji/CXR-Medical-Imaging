# GitHub Codespaces Quick Start

## Problem: Setup script not working?

If the automatic setup fails, follow these manual steps:

### Option 1: Simple Setup Script

```bash
./scripts/codespaces_setup.sh
```

This will:
- Install pip
- Create necessary directories
- Install all Python dependencies
- Show you next steps

### Option 2: Manual Setup

If even that doesn't work, run these commands one by one:

```bash
# 1. Install pip
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py --user
rm /tmp/get-pip.py

# 2. Add pip to PATH
export PATH="$HOME/.local/bin:$PATH"

# 3. Upgrade pip
python3 -m pip install --upgrade pip --user

# 4. Install dependencies (takes 5-10 minutes)
python3 -m pip install -r requirements.txt --user

# 5. Create directories
mkdir -p data/{raw,processed,extracted}
mkdir -p models outputs temp
```

### Verify Installation

```bash
# Check Python
python3 --version

# Check pip
python3 -m pip --version

# Check installed packages
python3 -m pip list | grep -E "(pydicom|SimpleITK|numpy|pandas)"
```

### Configure Dataset Access

#### For Kaggle datasets:
```bash
mkdir -p ~/.kaggle
nano ~/.kaggle/kaggle.json
```

Paste your credentials:
```json
{"username":"your_kaggle_username","key":"your_api_key"}
```

Save (Ctrl+O, Enter, Ctrl+X) and set permissions:
```bash
chmod 600 ~/.kaggle/kaggle.json
```

### Download Datasets

```bash
# NIH CXR-14 (45GB)
./scripts/download_datasets.sh nih-cxr14

# CheXpert (requires manual download from Stanford)
./scripts/download_datasets.sh chexpert
```

### Check Disk Space

```bash
df -h /workspaces
du -sh data/*
```

### Troubleshooting

**Problem: "command not found: pip"**
- Solution: Use `python3 -m pip` instead of `pip`

**Problem: "No module named pip"**
- Solution: Run the pip installation from Option 2 above

**Problem: "Permission denied"**
- Solution: Add `--user` flag to pip commands

**Problem: "Out of disk space"**
- Solution: Codespaces free tier has 32GB. Delete temp files or upgrade.

**Problem: Package installation fails**
- Solution: Install packages individually:
  ```bash
  python3 -m pip install --user pydicom numpy pandas requests tqdm
  ```

### What Got Backed Up?

All your code is safe at: https://github.com/bhavenmurji/CXR-Medical-Imaging

**Backed up files:**
- ✅ All Python scripts
- ✅ Configuration files
- ✅ Documentation
- ✅ Setup scripts
- ✅ .gitignore (prevents large files from being committed)

**NOT in GitHub (by design):**
- Large dataset files (temp/, data/, models/)
- Virtual environments (venv/)
- API keys and credentials

These should only exist in Codespaces where you have storage space!
