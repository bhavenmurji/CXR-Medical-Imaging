# Chest X-Ray Dataset Downloader

A professional-grade Python system for downloading and organizing chest X-ray datasets from multiple open-source medical imaging databases. This system prepares standardized training data for AI models that read chest X-rays from phone photos.

## 🩺 Supported Datasets

| Dataset | Images | Patients | Features | Access |
|---------|--------|----------|----------|---------|
| **NIH ChestX-ray14** | 112,120 | 30,805 | 14 disease labels, 1024×1024 resolution | Kaggle API |
| **MIMIC-CXR-JPG** | 377,110 | 65,379 | 14 structured labels, free-text reports | PhysioNet + CITI |
| **CheXpert** | 224,316 | 65,240 | 14 observations, uncertainty labels | Stanford AIMI |
| **Radiopaedia** | ~3,000 | ~3,000 | Educational cases, expert annotations | Kaggle API |

**Total: ~716,000+ images from ~164,000+ unique patients**

## 🏗️ System Architecture

```
cxr_dataset_downloader/
├── config/
│   ├── config.yaml                 # Main configuration
│   └── dataset_sources.yaml        # Dataset source definitions
├── downloaders/
│   ├── base_downloader.py          # Abstract base class
│   ├── nih_downloader.py           # NIH ChestX-ray14
│   ├── mimic_downloader.py         # MIMIC-CXR (TODO)
│   ├── chexpert_downloader.py      # CheXpert (TODO)
│   └── radiopaedia_downloader.py   # Radiopaedia (TODO)
├── processors/
│   ├── caption_extractor.py        # Report/caption processing
│   ├── image_validator.py          # Image quality validation
│   └── metadata_manager.py         # SQLite + CSV metadata
├── utils/
│   ├── auth_manager.py             # Secure credential management
│   ├── file_utils.py               # File operations
│   └── logging_utils.py            # Structured logging
├── main.py                         # CLI interface
├── setup_credentials.py           # Interactive credential setup
└── requirements.txt               # Python dependencies
```

## 📁 Output Directory Structure

```
/MeData/Radiology/CXR/
├── Images/
│   ├── nih_00000001_001_00000001.jpg
│   ├── mimic_p10000032_s50000001_d1.jpg
│   └── chexpert_patient00001_study1.jpg
├── captions/
│   ├── nih_00000001_001_00000001.txt
│   ├── mimic_p10000032_s50000001_d1.txt
│   └── chexpert_patient00001_study1.txt
├── metadata/
│   ├── master_index.csv            # Complete metadata
│   ├── master_index.db             # SQLite database
│   ├── download_log.json           # Download tracking
│   └── download_stats.json         # Statistics
└── logs/
    ├── cxr_downloader.log          # Main log
    ├── cxr_downloader.json         # Structured logs
    └── cxr_downloader_errors.log   # Error logs only
```

## 📋 Caption Format

All datasets use a standardized caption format:

```
SOURCE: NIH ChestX-ray14
PATIENT_ID: 00000001
STUDY_ID: study_001
VIEW_POSITION: PA
IMAGE_ID: 00000001_001

=== FINDINGS ===
Chest radiograph demonstrates findings consistent with cardiomegaly, pleural effusion.

=== IMPRESSION ===
Radiographic findings consistent with cardiomegaly, pleural effusion. Clinical correlation recommended.

=== STRUCTURED LABELS ===
Atelectasis: negative
Cardiomegaly: positive
Effusion: positive
Infiltration: negative
Mass: negative
Nodule: negative
Pneumonia: negative
Pneumothorax: negative
Consolidation: negative
Edema: negative
Emphysema: negative
Fibrosis: negative
Pleural_Thickening: negative
Hernia: negative

=== METADATA ===
Patient Age: 58
Patient Sex: M
Image Date: unknown
Image Quality: unknown
Dataset: NIH ChestX-ray14 (112,120 images from 30,805 patients)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or extract the system
cd /Users/bhavenmurji/Development/MeData/Imaging/CXR/cxr_dataset_downloader

# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x main.py setup_credentials.py
```

### 2. Setup Credentials

```bash
# Interactive credential setup
python setup_credentials.py

# Test existing credentials
python setup_credentials.py --test-only
```

### 3. Download Datasets

```bash
# Test with small sample (recommended first)
python main.py download --source nih --limit 10

# Validate downloaded files
python main.py validate --source nih

# Download specific dataset
python main.py download --source nih

# Download all available datasets
python main.py download --source all

# Resume interrupted download
python main.py download --source mimic --resume
```

### 4. Monitor Progress

```bash
# Show statistics
python main.py stats

# Check access to all sources
python main.py check-access

# Clean up temp files
python main.py cleanup
```

## 🔐 Authentication Setup

### NIH ChestX-ray14 & Radiopaedia (Kaggle API)

1. Create Kaggle account: https://www.kaggle.com/account
2. Go to Account → API → Create New API Token
3. Download `kaggle.json` to `~/.kaggle/kaggle.json`
4. Or set environment variables:
   ```bash
   export KAGGLE_USERNAME=your_username
   export KAGGLE_KEY=your_api_key
   ```

### MIMIC-CXR (PhysioNet)

1. **Create PhysioNet account**: https://physionet.org/register/
2. **Complete CITI Training**: https://www.citiprogram.org/
   - Select "Data or Specimens Only Research" course
   - Takes 3-7 days for approval
3. **Request MIMIC-CXR access**: https://physionet.org/content/mimic-cxr-jpg/
4. **Set credentials** in setup script

### MIMIC-CXR Alternative (Google Cloud - $120 USD)

1. **Create GCP project** with billing enabled
2. **Setup service account** with Storage Object Viewer role
3. **Download service account JSON key**
4. **Set environment variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

### CheXpert (Stanford AIMI)

1. **Register** at Stanford AIMI: https://stanfordaimi.azurewebsites.net/
2. **Request CheXpert access**: Approval required
3. **Direct download** - no API key needed

## 💻 CLI Commands

### Download Commands
```bash
# Download specific dataset
python main.py download --source nih
python main.py download --source mimic
python main.py download --source chexpert
python main.py download --source radiopaedia

# Download all available datasets
python main.py download --source all

# Limit for testing (download only N files)
python main.py download --source nih --limit 100

# Resume interrupted download
python main.py download --source mimic --resume
```

### Validation Commands
```bash
# Validate specific dataset
python main.py validate --source nih

# Validate all datasets
python main.py validate --source all
```

### Utility Commands
```bash
# Show comprehensive statistics
python main.py stats

# Check authentication status
python main.py check-access

# Clean up temporary files
python main.py cleanup --hours 24
```

## 📊 Expected Download Statistics

| Dataset | Size | Time (Kaggle) | Time (PhysioNet) | Time (GCP) |
|---------|------|---------------|-------------------|------------|
| NIH ChestX-ray14 | ~45 GB | 4-8 hours | N/A | N/A |
| MIMIC-CXR | ~420 GB | N/A | 12-24 hours | 2-4 hours |
| CheXpert | ~440 GB | N/A | 8-16 hours | N/A |
| Radiopaedia | ~2 GB | 1-2 hours | N/A | N/A |
| **Total** | **~907 GB** | **Variable** | **20-48 hours** | **6-12 hours** |

## 🔧 Configuration

### Main Configuration (`config/config.yaml`)

```yaml
paths:
  base_dir: "/MeData/Radiology/CXR"
  images_dir: "Images"
  captions_dir: "captions"
  metadata_dir: "metadata"
  temp_dir: "temp"

download:
  concurrent_downloads: 5
  retry_attempts: 3
  retry_delay: 5
  timeout: 300
  verify_checksums: true

datasets:
  nih:
    enabled: true
    source: "kaggle"
    limit: null  # null = download all
  mimic:
    enabled: true
    source: "physionet"  # or "google_cloud"
    limit: null
  chexpert:
    enabled: true
    source: "stanford"
    limit: null
  radiopaedia:
    enabled: true
    source: "kaggle"
    limit: null
```

### Environment Variables (`.env`)

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# Kaggle API
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key

# PhysioNet
PHYSIONET_USERNAME=your_email
PHYSIONET_PASSWORD=your_password

# Google Cloud (optional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your_project_id
```

## 🔍 Data Validation

The system performs comprehensive validation:

### Image Validation
- ✅ File format (JPEG, PNG)
- ✅ Resolution (minimum 512px)
- ✅ File size (50KB - 5MB)
- ✅ Image corruption detection
- ✅ Quality metrics (contrast, noise, dynamic range)
- ✅ Medical imaging artifacts detection

### Caption Validation
- ✅ Required sections present
- ✅ UTF-8 encoding
- ✅ Reasonable length (>100 characters)
- ✅ Structured label format
- ✅ Error/placeholder detection

### Metadata Validation
- ✅ SHA256 checksums
- ✅ Image-caption pairing
- ✅ Database consistency
- ✅ Duplicate detection

## 📈 Progress Tracking

### Real-time Progress
```bash
# Monitor log file
tail -f /MeData/Radiology/CXR/logs/cxr_downloader.log

# Check statistics
python main.py stats
```

### Download Statistics
The system tracks:
- Files downloaded/failed/skipped
- Download rates (files/minute)
- Data sizes and checksums
- Elapsed time and ETA
- Validation results
- Error summaries

## ⚠️ Troubleshooting

### Common Issues

**1. Kaggle Authentication Failed**
```bash
# Check credentials
ls ~/.kaggle/kaggle.json
python setup_credentials.py --test-only
```

**2. PhysioNet Access Denied**
- Ensure CITI training is completed
- Wait 3-7 days for approval
- Check dataset-specific access requests

**3. Download Timeout**
```bash
# Resume interrupted download
python main.py download --source nih --resume
```

**4. Disk Space**
```bash
# Check available space (need ~1TB)
df -h /MeData

# Clean up temp files
python main.py cleanup
```

**5. Memory Issues**
```bash
# Reduce concurrent downloads in config.yaml
concurrent_downloads: 2
```

### Log Analysis

```bash
# Check main log
tail -100 /MeData/Radiology/CXR/logs/cxr_downloader.log

# Check errors only
cat /MeData/Radiology/CXR/logs/cxr_downloader_errors.log

# Check JSON structured logs
jq '.level == "ERROR"' /MeData/Radiology/CXR/logs/cxr_downloader.json
```

## 🔬 Data Usage Recommendations

### Training Split
- **Training**: 80% (~571,000 images)
- **Validation**: 10% (~71,000 images)
- **Test**: 10% (~71,000 images)

### Important Considerations
1. **Patient-level split**: Ensure same patient doesn't appear in multiple splits
2. **Stratification**: Balance disease distribution across splits
3. **View positions**: Include both frontal (PA/AP) and lateral views
4. **Quality filtering**: Remove poor quality images before training

### Example Split Code
```python
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

# Load metadata
df = pd.read_csv('/MeData/Radiology/CXR/metadata/master_index.csv')

# Patient-level split
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(df, groups=df['patient_id']))

train_df = df.iloc[train_idx]
test_df = df.iloc[test_idx]
```

## 📜 Dataset Citations

If you use these datasets, please cite the original papers:

### NIH ChestX-ray14
```
Wang, Xiaosong, et al. "ChestX-ray8: Hospital-scale chest X-ray database and benchmarks on weakly-supervised classification and localization of common thorax diseases." Proceedings of the IEEE conference on computer vision and pattern recognition. 2017.
```

### MIMIC-CXR
```
Johnson, Alistair EW, et al. "MIMIC-CXR-JPG, a large publicly available database of labeled chest radiographs." arXiv preprint arXiv:1901.07042 (2019).
```

### CheXpert
```
Irvin, Jeremy, et al. "CheXpert: A large chest radiograph dataset with uncertainty labels and expert comparison." Proceedings of the AAAI Conference on Artificial Intelligence. Vol. 33. 2019.
```

### Radiopaedia
```
Please cite individual cases as per Radiopaedia's citation requirements.
```

## 🤝 Contributing

This system was generated by Claude Code. To extend functionality:

1. **Add new downloaders**: Inherit from `BaseDownloader`
2. **Enhance validation**: Extend `ImageValidator`
3. **Improve captions**: Modify `CaptionExtractor`
4. **Add datasets**: Update configuration files

## 📄 License

MIT License - See individual dataset licenses for usage restrictions.

## 🆘 Support

For issues with this downloader system:
1. Check the troubleshooting section above
2. Review log files for error details
3. Verify credentials and network connectivity

For dataset-specific issues:
- **NIH**: Contact NIH Clinical Center
- **MIMIC-CXR**: Contact MIT-LCP via PhysioNet
- **CheXpert**: Contact Stanford AIMI
- **Radiopaedia**: Contact Radiopaedia support

---

**Generated by Claude Code** 🤖

This system provides a robust foundation for downloading and organizing chest X-ray datasets. The modular architecture allows for easy extension to additional datasets and processing workflows.

**Happy dataset building!** 🩺📊