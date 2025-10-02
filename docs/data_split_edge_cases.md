# Data Splitting Edge Cases and Handling Strategy

## Overview
This document details the edge cases identified during data splitting strategy design and the solutions implemented to handle them.

## Dataset Characteristics Summary

### Patient Distribution
- **Total Images**: 3,783
- **Total Unique Patients**: 3,749
- **CheXpert**: 200 patients, 234 images (1.17 images/patient)
- **Radiopaedia**: 3,549 patients, 3,549 images (1.0 images/patient)

### Multi-Image Patient Analysis
**CheXpert Patients with Multiple Images:**
```
3 images: patient64616, patient64581, patient64547
2 images: patient64705, patient64676, patient64640, patient64625,
          patient64618, patient64615, patient64613, and ~20 others
```

**Total**: Approximately 34 patients (~17% of CheXpert) have multiple images

**Clinical Reason**: Different views (frontal/lateral) or follow-up studies

## Edge Cases

### 1. Multi-Image Patients

**Problem Statement:**
Some patients have 2-3 X-ray images representing different views or time points. Splitting at the image level would cause data leakage where the model sees similar images from the same patient in both train and test sets.

**Solution Implemented:**
```python
# Group all images by patient_id BEFORE splitting
patient_data = defaultdict(list)
for row in master_df.iterrows():
    patient_id = extract_patient_id(row['filename'], row['source'])
    patient_data[patient_id].append(row)

# Split at patient level
train_patients, val_patients, test_patients = stratified_split(patient_data.keys())

# Then expand patients to images
for patient in train_patients:
    train_images.extend(patient_data[patient])
```

**Impact:**
- Ensures clinical validity (no patient in multiple splits)
- Image ratios may deviate slightly from 80/10/10 due to multi-image patients
- Example: If a 3-image patient is assigned to train, train gets +3 images vs expected +1

**Validation:**
- Assert zero patient overlap between splits
- Log actual image ratios vs target ratios
- Acceptable deviation: ±5%

### 2. Rare Patient IDs or Malformed Filenames

**Problem Statement:**
Regex pattern matching may fail for edge cases:
- Non-standard filename formats
- Corrupted or truncated filenames
- Missing patient ID segments

**Examples of Potential Failures:**
```
# Expected: chexpert_patient64541_study1_view1_frontal.jpg
# Edge case: chexpert_study1_view1_frontal.jpg (missing patient ID)
```

**Solution Implemented:**
```python
def extract_patient_id(filename: str, source: str) -> str:
    if source == "CheXpert":
        match = re.search(r'patient(\d+)', filename)
        if match:
            return f"chexpert_patient{match.group(1)}"
        else:
            # Fallback to unique hash
            logger.warning(f"Could not parse patient ID: {filename}")
            return f"chexpert_unknown_{hash(filename)}"
    # Similar for Radiopaedia...
```

**Fallback Strategy:**
- Generate deterministic hash-based patient ID
- Log warnings for manual review
- Treat as single-image "patient"
- Track unparseable files in metadata

**Validation:**
- Log all unparseable filenames
- Check if unparseable count < 1% of total
- Manual review if count exceeds threshold

### 3. Rare Diseases (Long-Tail Distribution)

**Problem Statement:**
Some diseases may have very few patients (<5), making stratification challenging:
- Not enough patients to split across train/val/test
- Risk of test set having zero examples of rare disease
- Stratification algorithms may fail with small groups

**Expected Distribution:**
```
Common: pneumonia, pleural_effusion, cardiomegaly (>100 patients each)
Uncommon: pneumothorax, nodule, fracture (10-50 patients)
Rare: specific fracture types, rare masses (<5 patients)
```

**Solution Implemented:**
```python
# 1. Group rare diseases into "other" category
def get_stratification_key(patient_id):
    diseases = disease_labels[patient_id]

    # Priority list of common diseases
    priority_diseases = [
        "pneumonia", "pleural_effusion", "cardiomegaly",
        "edema", "atelectasis", "pneumothorax"
    ]

    for disease in priority_diseases:
        if disease in diseases:
            return disease

    # All other diseases grouped as "other"
    return "other"

# 2. Minimum split size check
for disease, patients in disease_groups.items():
    if len(patients) < 3:
        logger.warning(f"Disease {disease} has only {len(patients)} patients")
        # Ensure at least 1 goes to train
        train_patients.extend(patients[:max(1, len(patients)-1)])
        if len(patients) > 1:
            test_patients.append(patients[-1])
```

**Validation:**
- Log disease distribution for each split
- Flag diseases with <5 patients
- Ensure train set has at least 1 example of each disease
- Accept that val/test may have zero examples of very rare diseases

### 4. Class Imbalance (Normal vs Abnormal)

**Problem Statement:**
Medical imaging datasets often have severe imbalance:
- Abnormal cases may be 95%+ of dataset
- Normal cases under-represented
- Risk of model bias toward abnormal predictions

**Solution Implemented:**
```python
# Two-level stratification
def stratified_split_patients(patient_ids):
    # Level 1: Stratify by normal/abnormal
    normal_patients = [p for p in patient_ids if "normal" in disease_labels[p]]
    abnormal_patients = [p for p in patient_ids if "normal" not in disease_labels[p]]

    # Level 2: Within abnormal, stratify by specific disease
    normal_splits = proportional_split(normal_patients)
    abnormal_splits = stratified_split_by_disease(abnormal_patients)

    # Combine
    return combine_splits(normal_splits, abnormal_splits)
```

**Alternative (for multi-label):**
```python
# Use iterative stratification (skmultilearn)
from skmultilearn.model_selection import iterative_train_test_split

# Create binary disease matrix
y_matrix = create_multilabel_matrix(patient_ids, disease_labels)

# Iterative stratification maintains proportions for each label
train_idx, test_idx = iterative_train_test_split(X, y_matrix, test_size=0.2)
```

**Validation:**
- Chi-squared test: p > 0.05 for class proportions across splits
- Jensen-Shannon divergence < 0.1 between split distributions

### 5. Caption Quality and Format Variations

**Problem Statement:**
Captions come from different sources with varying formats:
- CheXpert: Clinical radiology reports (structured)
- Radiopaedia: Educational descriptions (free-form)
- Different terminology for same conditions
- Varying levels of detail

**Examples:**
```
CheXpert: "Frontal and lateral views show cardiomegaly. No acute infiltrate."
Radiopaedia: "The heart is enlarged. Lung fields are clear bilaterally."
```

**Solution Implemented:**
```python
disease_keywords = {
    "cardiomegaly": [
        "cardiomegaly",
        "enlarged heart",
        "cardiac enlargement",
        "heart is enlarged",
        "increased cardiac silhouette"
    ],
    "pneumonia": [
        "pneumonia",
        "consolidation",
        "infiltrate",
        "airspace opacity"
    ],
    # ...comprehensive synonym mappings
}

# Fuzzy matching for robustness
def extract_diseases(caption_text):
    caption_lower = caption_text.lower()
    diseases = []

    for disease, keyword_list in disease_keywords.items():
        for keyword in keyword_list:
            if keyword in caption_lower:
                diseases.append(disease)
                break

    # Default category if nothing matches
    if not diseases:
        diseases.append("unspecified")

    return diseases
```

**Validation:**
- Sample manual review of 100 random captions
- Check parsing accuracy > 90%
- Log "unspecified" rate (should be <5%)

### 6. Missing or Corrupt Caption Files

**Problem Statement:**
Some caption files may be:
- Missing (file path exists but file not found)
- Corrupt (unreadable encoding)
- Empty (zero bytes)

**Solution Implemented:**
```python
def extract_diseases_from_caption(caption_path):
    try:
        with open(caption_path, 'r', encoding='utf-8') as f:
            caption_text = f.read()

        if not caption_text.strip():
            logger.warning(f"Empty caption: {caption_path}")
            return ["unspecified"]

        # Normal parsing...
        return extract_diseases(caption_text)

    except FileNotFoundError:
        logger.error(f"Caption file not found: {caption_path}")
        return ["unspecified"]

    except UnicodeDecodeError:
        logger.error(f"Caption encoding error: {caption_path}")
        # Try alternative encodings
        try:
            with open(caption_path, 'r', encoding='latin-1') as f:
                caption_text = f.read()
            return extract_diseases(caption_text)
        except:
            return ["unspecified"]

    except Exception as e:
        logger.error(f"Unexpected error reading {caption_path}: {e}")
        return ["unspecified"]
```

**Validation:**
- Log all caption read errors
- Error rate should be <1%
- Manual review of problematic files

### 7. Source Imbalance

**Problem Statement:**
- CheXpert: 234 images (6.2% of dataset)
- Radiopaedia: 3,549 images (93.8% of dataset)

Risk: Test set might be 100% Radiopaedia, limiting generalization assessment

**Solution Implemented:**
```python
# Split each source separately then combine
chexpert_patients = [p for p in patient_data if p.startswith("chexpert_")]
radiopaedia_patients = [p for p in patient_data if p.startswith("radiopaedia_")]

chexpert_splits = stratified_split(chexpert_patients, 0.8, 0.1, 0.1)
radiopaedia_splits = stratified_split(radiopaedia_patients, 0.8, 0.1, 0.1)

# Combine to ensure both sources in all splits
train = chexpert_splits.train + radiopaedia_splits.train
val = chexpert_splits.val + radiopaedia_splits.val
test = chexpert_splits.test + radiopaedia_splits.test
```

**Validation:**
```python
for split_name in ['train', 'val', 'test']:
    sources = splits[split_name]['source'].unique()
    assert len(sources) == 2, f"{split_name} missing a source!"

    # Log source distribution
    source_dist = splits[split_name]['source'].value_counts()
    logger.info(f"{split_name} sources: {source_dist.to_dict()}")
```

## Testing Strategy

### Unit Tests
```python
def test_multi_image_patient_grouping():
    """Ensure patient64616 (3 images) all go to same split"""
    assert split_assignment['patient64616_image1'] == split_assignment['patient64616_image2']

def test_no_patient_overlap():
    """Critical: Zero patient overlap between splits"""
    assert len(train_patients.intersection(val_patients)) == 0
    assert len(train_patients.intersection(test_patients)) == 0

def test_rare_disease_handling():
    """Diseases with <3 patients still processed correctly"""
    rare_disease_patients = get_patients_with_disease("rare_condition")
    if len(rare_disease_patients) > 0:
        assert train has at least one rare_disease_patient

def test_caption_error_handling():
    """Missing/corrupt captions don't crash pipeline"""
    result = extract_diseases_from_caption("nonexistent.txt")
    assert result == ["unspecified"]
```

### Integration Tests
```python
def test_full_pipeline():
    """End-to-end pipeline execution"""
    splitter = PatientLevelDataSplitter("test_data/master_index.csv")
    splits = splitter.run_full_pipeline()

    # Validate all checks pass
    validation = splitter.validate_splits()
    assert validation['overall_valid'] == True
```

## Monitoring and Alerts

### Pre-Split Checks
- ✓ All filenames parsed successfully (warn if >1% fail)
- ✓ All captions readable (warn if >1% fail)
- ✓ Disease labels extracted for >95% of images

### Post-Split Checks
- ✓ Zero patient overlap (CRITICAL - fail if any)
- ✓ Ratios within ±5% of target (warn if outside)
- ✓ Both sources in all splits (CRITICAL)
- ✓ Disease distributions similar (warn if JS divergence >0.15)

### Outputs for Manual Review
- `split_metadata.json` - Complete statistics
- `patient_mapping.json` - Patient -> split assignments
- `validation_report.txt` - Human-readable validation summary
- `edge_cases_log.txt` - All warnings and edge case handling

## Recommendations for Future Improvements

1. **Multi-Label Stratification**: Implement iterative stratification for complex multi-disease cases
2. **NLP-Based Disease Extraction**: Use transformer models for more accurate caption parsing
3. **Active Learning**: Identify uncertain cases for manual review
4. **Version Control**: Track split versions for reproducibility across experiments
5. **Real-time Validation**: Add unit tests that run on every split generation

## References
- Sechidis et al. (2011) - Stratification in multi-label classification
- CheXpert paper - Patient-level splitting methodology
- Medical AI best practices - Preventing data leakage in clinical ML
