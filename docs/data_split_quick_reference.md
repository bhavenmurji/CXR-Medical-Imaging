# Data Splitting Quick Reference Guide

## TL;DR
**Patient-level stratified splitting to prevent data leakage. All images from same patient stay together. 80/10/10 train/val/test split with disease distribution balance.**

## Key Statistics
```
Total: 3,783 images, 3,749 unique patients
CheXpert: 200 patients, 234 images (17% have 2-3 images)
Radiopaedia: 3,549 patients, 3,549 images (1:1 ratio)
```

## Critical Design Decisions

### 1. Patient-Level Splitting ✓
**Why**: Prevents data leakage where model sees same patient in train and test
**Implementation**: Group images by patient_id BEFORE splitting
**Trade-off**: Image ratios may deviate from 80/10/10 due to multi-image patients

### 2. Stratification by Disease ✓
**Why**: Maintain similar disease prevalence across train/val/test
**Implementation**: Extract diseases from captions, stratify by primary disease
**Fallback**: Rare diseases (<3 patients) grouped as "other"

### 3. Source-Specific Splitting ✓
**Why**: Ensure both CheXpert and Radiopaedia in all splits despite imbalance
**Implementation**: Split each source separately, then combine
**Validation**: Assert both sources present in each split

## Algorithm Overview

```
1. Load master_index.csv
2. Extract patient_id from filename
3. Group images by patient_id
4. Parse captions → extract disease labels
5. Separate CheXpert and Radiopaedia patients
6. Stratified split each source (80/10/10)
7. Combine splits
8. Validate:
   - Zero patient overlap ✓
   - Ratio within ±5% ✓
   - Both sources in all splits ✓
   - Disease distributions similar ✓
9. Save to metadata/splits/
```

## Patient ID Extraction

### CheXpert
```
Input:  chexpert_patient64541_study1_view1_frontal.jpg
Regex:  patient(\d+)
Output: chexpert_patient64541
```

### Radiopaedia
```
Input:  radiopaedia_chest_xrays_radiopaedia_003544_study_01_*.jpg
Regex:  radiopaedia_(\d+)
Output: radiopaedia_003544
```

## Disease Extraction from Captions

**Keyword Matching with Synonyms:**
```python
disease_keywords = {
    "pneumonia": ["pneumonia", "consolidation", "infiltrate"],
    "pleural_effusion": ["pleural effusion", "effusion"],
    "cardiomegaly": ["cardiomegaly", "enlarged heart"],
    "edema": ["edema", "pulmonary edema"],
    "atelectasis": ["atelectasis", "collapse"],
    "pneumothorax": ["pneumothorax"],
    "nodule": ["nodule", "mass", "lesion"],
    "fracture": ["fracture"],
    "normal": ["no acute", "normal", "clear lungs"]
}
```

**Stratification Priority (most clinically significant first):**
1. pneumonia
2. pneumothorax
3. pleural_effusion
4. cardiomegaly
5. edema
6. atelectasis
7. nodule
8. fracture
9. normal
10. unspecified

## Edge Cases Handled

| Edge Case | Solution |
|-----------|----------|
| Multi-image patients | Group by patient_id, split at patient level |
| Malformed filenames | Fallback to hash-based patient ID |
| Rare diseases (<3 patients) | Group as "other" for stratification |
| Caption parsing failures | Default to "unspecified" category |
| Missing caption files | Log warning, assign "unspecified" |
| Source imbalance (6% vs 94%) | Split sources separately, then combine |

## Validation Checks

### CRITICAL (Must Pass)
- [ ] Zero patient overlap between splits
- [ ] Both sources in all splits
- [ ] All patients assigned to exactly one split

### WARNING (Should Pass)
- [ ] Ratios within ±5% of target (80/10/10)
- [ ] Disease distributions similar (JS divergence <0.15)
- [ ] Caption parsing success >95%
- [ ] Patient ID extraction success >99%

## Output Files

```
metadata/splits/
├── train_index.csv          # Train split (filename, source, paths, patient_id)
├── val_index.csv            # Validation split
├── test_index.csv           # Test split
├── split_metadata.json      # Statistics and distributions
└── patient_mapping.json     # patient_id → split assignment
```

## Usage

### Command Line
```bash
# Default (80/10/10 split)
python src/data_splitting_algorithm.py

# Custom ratios
python src/data_splitting_algorithm.py \
    --train-ratio 0.7 \
    --val-ratio 0.15 \
    --test-ratio 0.15 \
    --random-seed 42
```

### Python API
```python
from data_splitting_algorithm import PatientLevelDataSplitter

splitter = PatientLevelDataSplitter('metadata/master_index.csv', random_seed=42)
splits = splitter.run_full_pipeline(output_dir='metadata/splits')

# Access splits
train_df = splits['train']
val_df = splits['val']
test_df = splits['test']
```

## Expected Results

### Split Sizes (Approximate)
```
Train:      3,000 patients, ~3,026 images (80%)
Validation:   375 patients,   ~378 images (10%)
Test:         374 patients,   ~379 images (10%)
```

### Disease Distribution Example
```
             Train    Val     Test
pneumonia    22%      21%     23%
effusion     18%      19%     17%
cardiomegaly 15%      14%     16%
normal       12%      13%     11%
...
```

### Source Distribution
```
             Train    Val     Test
CheXpert     187      24      23
Radiopaedia  2,839    351     359
```

## Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
scipy>=1.11.0
```

## Testing

```bash
# Run unit tests
pytest tests/test_data_splitting.py -v

# Run with coverage
pytest tests/test_data_splitting.py --cov=src.data_splitting_algorithm

# Integration test
python src/data_splitting_algorithm.py --master-index test_data/master_index.csv
```

## Troubleshooting

### "Patient overlap detected!"
- **Cause**: Bug in split assignment logic
- **Fix**: Check patient_data grouping, ensure deterministic random seed

### "Validation ratio check failed"
- **Cause**: Multi-image patients causing imbalance
- **Expected**: Minor deviations (<5%) are acceptable
- **Fix**: Review if deviation >10%, may need to rebalance

### "Missing captions for >1% of images"
- **Cause**: Caption files not generated or corrupt
- **Fix**: Re-run caption generation, check file permissions

### "Rare disease has 0 patients in test set"
- **Expected**: Diseases with <3 patients may not appear in all splits
- **Acceptable**: As long as train has at least 1 example

## Performance

- **Runtime**: ~5-10 seconds for 3,783 images
- **Memory**: <100 MB
- **I/O**: Reads master_index.csv + all caption files

## Next Steps After Splitting

1. **Data Loaders**: Create PyTorch/TensorFlow dataloaders using split CSVs
2. **Augmentation**: Apply transforms during training only
3. **Monitoring**: Track train/val metrics during training
4. **Evaluation**: Final test set evaluation after model selection
5. **Version Control**: Commit split files to ensure reproducibility

## Contact
Data Processing Agent - Swarm Coordination System
Generated: 2025-10-01
