# Kaggle API Setup Guide

## Quick Setup

Your `~/.kaggle/kaggle.json` file must have this exact format:

```json
{"username":"your_kaggle_username","key":"your_api_key"}
```

**Important**: Replace `your_kaggle_username` and `your_api_key` with your actual credentials.

## Getting Your Kaggle API Credentials

1. Go to https://www.kaggle.com/account
2. Scroll down to the "API" section
3. Click "Create New Token"
4. This downloads `kaggle.json` with your credentials

## Installing in Codespaces

```bash
# Upload the downloaded kaggle.json to Codespaces
# Then move it to the correct location:
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

## Verify It Works

```bash
# Activate virtual environment
source venv/bin/activate

# Test Kaggle API
kaggle datasets list

# If you see a list of datasets, it's working!
```

## Common Issues

**Error: "Missing username in configuration"**
- Your kaggle.json is malformed
- Make sure it's valid JSON with both "username" and "key" fields
- No extra commas, proper quotes around values

**Error: "401 Unauthorized"**
- Your API key is incorrect or expired
- Generate a new token from Kaggle

**Error: "403 Forbidden"**
- You need to accept the dataset's terms of service on Kaggle's website first
- Go to https://www.kaggle.com/datasets/nih-chest-xrays/data
- Click "Download" to accept terms
