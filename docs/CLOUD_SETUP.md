# Cloud Setup Guide - GitHub Codespaces

## Overview

This project processes large medical imaging datasets (CheXpert, NIH CXR-14, MIMIC-CXR). Due to storage constraints on local machines, all dataset processing should be done in GitHub Codespaces.

## Quick Start

### 1. Open in Codespaces

Click the green "Code" button on GitHub → Select "Codespaces" tab → Click "Create codespace on main"

GitHub will automatically:
- Set up a Python 3.11 environment
- Install all dependencies from `requirements.txt`
- Configure 8GB RAM and 4 CPUs
- Mount necessary directories

### 2. Initial Setup

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run environment setup
./scripts/setup_cloud_environment.sh
```

### 3. Configure Dataset Access

#### For Kaggle Datasets:
```bash
mkdir -p ~/.kaggle
nano ~/.kaggle/kaggle.json
```

Add your Kaggle API credentials:
```json
{
  "username": "your_username",
  "key": "your_api_key"
}
```

Set permissions:
```bash
chmod 600 ~/.kaggle/kaggle.json
```

#### For PhysioNet (MIMIC-CXR):
1. Complete credentialing at https://physionet.org/
2. Accept data use agreement
3. Use provided download credentials

#### For Stanford (CheXpert):
1. Register at https://stanfordaimi.azurewebsites.net/datasets/8cbd9ed4-2eb9-4565-affc-111cf4f7ebe2
2. Download manually and upload to Codespaces

### 4. Download Datasets

```bash
# Download specific dataset
./scripts/download_datasets.sh nih-cxr14

# Download all available datasets
./scripts/download_datasets.sh all
```

### 5. Process Datasets

```bash
# Process CheXpert
python src/process_chexpert.py

# Extract and index datasets
python src/generate_master_index.py
```

## Directory Structure

```
/workspace/
├── .devcontainer/          # Codespaces configuration
├── data/
│   ├── raw/               # Downloaded datasets (gitignored)
│   ├── processed/         # Processed data
│   └── extracted/         # Extracted images
├── scripts/               # Setup and download scripts
├── src/                   # Processing scripts
├── models/                # Trained models
└── outputs/               # Results and reports
```

## Storage Management

### Check Disk Usage
```bash
df -h
du -sh data/*
```

### Clean Up Old Data
```bash
# Remove raw archives after extraction
rm -rf data/raw/*.tar.gz data/raw/*.zip

# Clean temporary files
rm -rf temp/*
```

## Available Datasets

| Dataset | Size | Registration Required | Download Method |
|---------|------|----------------------|-----------------|
| NIH CXR-14 | ~45GB | No | Script automated |
| CheXpert | ~11GB | Yes (Stanford) | Manual download |
| MIMIC-CXR | ~470GB | Yes (PhysioNet) | Credential-based |
| PadChest | ~1TB | Yes | Manual download |

## Codespace Specifications

- **Image**: Python 3.11 on Debian Bullseye
- **Memory**: 8GB RAM
- **CPUs**: 4 cores
- **Storage**: Up to 32GB (expandable)
- **GPU**: Not included (use CPU-only inference)

## Tips for Large Datasets

1. **Process in Batches**: Don't extract everything at once
2. **Stream Processing**: Use generators for large files
3. **Delete After Processing**: Remove raw data after extraction
4. **Use External Storage**: Consider Azure/AWS for long-term storage
5. **Incremental Commits**: Commit processed data in chunks

## Troubleshooting

### Out of Disk Space
```bash
# Check what's using space
du -sh * | sort -h

# Clean Docker cache
docker system prune -a

# Increase Codespace storage (Settings → Codespaces)
```

### Slow Download Speeds
- Use parallel downloads when possible
- Consider downloading during off-peak hours
- Use `aria2c` for multi-threaded downloads

### Memory Issues
```bash
# Monitor memory usage
htop

# Reduce batch size in processing scripts
# Close unused tabs and extensions
```

## Migrating from Local to Cloud

If you have data locally that needs to move to Codespaces:

1. **Don't commit large files to git**
2. **Use git-lfs** for files < 2GB
3. **Upload directly** to cloud storage (S3, Azure Blob)
4. **Download in Codespace** from cloud storage

## Cost Considerations

- Free tier: 120 core-hours/month
- Pro plan: Unlimited with rate limits
- Storage: First 15GB free, then $0.07/GB-month
- Compute: $0.18/hour (2-core) to $0.72/hour (8-core)

For heavy processing, consider using:
- GitHub Actions for scheduled jobs
- Azure ML / AWS SageMaker for GPU workloads
- Colab Pro+ for interactive GPU development

## Security

- Never commit API keys or credentials
- Use GitHub Secrets for sensitive data
- Enable 2FA on all dataset provider accounts
- Review data use agreements before processing

## Support

- GitHub Codespaces docs: https://docs.github.com/codespaces
- Issues: File in this repository
- Dataset-specific: Contact respective providers
