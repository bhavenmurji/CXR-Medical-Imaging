# Patient-Level Data Splitting Strategy

## Executive Summary
This document outlines the patient-level data splitting algorithm for the chest X-ray dataset, ensuring no data leakage between train/validation/test sets while maintaining disease distribution balance.

## Dataset Statistics

### Overall
- **Total Images**: 3,783
- **Total Size**: 960.91 MB (0.94 GB)
- **Average Image Size**: 0.25 MB

### By Source
- **CheXpert**: 234 images, 200 unique patients (1.17 images/patient)
- **Radiopaedia**: 3,549 images, 3,549 unique cases (1.0 images/patient)

### Multi-Image Analysis
- **CheXpert Patients with Multiple Images**:
  - 3 images: patients 64616, 64581, 64547
  - 2 images: patients 64705, 64676, 64640, 64625, 64618, 64615, 64613, and others
  - Approximately 34 patients (~17%) have multiple images

## Data Splitting Requirements

### Target Split Ratios
- **Training**: 80% of patients
- **Validation**: 10% of patients
- **Test**: 10% of patients

### Critical Constraints
1. **Patient-Level Splitting**: ALL images from a single patient must be in the same split
2. **No Data Leakage**: Zero overlap between train/val/test patient IDs
3. **Disease Distribution Balance**: Maintain similar disease prevalence across splits
4. **Source Handling**: Handle CheXpert and Radiopaedia separately then combine

## Patient ID Extraction Pattern

### CheXpert Format
```
Filename: chexpert_patient64541_study1_view1_frontal.jpg
Pattern: patient(\d+)
Patient ID: chexpert_patient64541
```

### Radiopaedia Format
```
Filename: radiopaedia_chest_xrays_radiopaedia_003544_study_01_9c5e0971c1a249b0e4daadc3ed55a2_jumbo.jpg
Pattern: radiopaedia_(\d+)
Patient ID: radiopaedia_003544
```

## Splitting Algorithm Pseudocode

```pseudocode
FUNCTION stratified_patient_split(master_index_df, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, random_seed=42):

    // Step 1: Extract patient IDs and group images
    FOR each row in master_index_df:
        patient_id = extract_patient_id(filename, source)
        patient_data[patient_id].append(row)

    // Step 2: Parse captions to extract disease labels
    disease_labels = {}
    FOR each patient_id in patient_data:
        diseases = []
        FOR each image in patient_data[patient_id]:
            caption = read_caption(image.caption_path)
            diseases.extend(extract_diseases_from_caption(caption))
        disease_labels[patient_id] = unique(diseases)

    // Step 3: Create stratification key (multi-hot disease vector)
    FOR each patient_id in disease_labels:
        # Create binary vector for primary disease(s)
        primary_disease = get_most_prominent_disease(disease_labels[patient_id])
        stratification_key[patient_id] = primary_disease

    // Step 4: Stratified split by source
    chexpert_patients = [p for p in patient_data if p.startswith("chexpert_")]
    radiopaedia_patients = [p for p in patient_data if p.startswith("radiopaedia_")]

    chexpert_splits = stratified_split_patients(
        chexpert_patients,
        stratification_key,
        train_ratio, val_ratio, test_ratio,
        random_seed
    )

    radiopaedia_splits = stratified_split_patients(
        radiopaedia_patients,
        stratification_key,
        train_ratio, val_ratio, test_ratio,
        random_seed
    )

    // Step 5: Combine splits
    train_patients = chexpert_splits.train + radiopaedia_splits.train
    val_patients = chexpert_splits.val + radiopaedia_splits.val
    test_patients = chexpert_splits.test + radiopaedia_splits.test

    // Step 6: Expand patients to images
    train_images = []
    FOR patient in train_patients:
        train_images.extend(patient_data[patient])

    val_images = []
    FOR patient in val_patients:
        val_images.extend(patient_data[patient])

    test_images = []
    FOR patient in test_patients:
        test_images.extend(patient_data[patient])

    // Step 7: Validate splits
    ASSERT no_overlap(train_patients, val_patients, test_patients)
    ASSERT ratio_check(len(train_patients), len(val_patients), len(test_patients))
    ASSERT disease_distribution_similarity(train_images, val_images, test_images)

    RETURN train_images, val_images, test_images, split_metadata


FUNCTION stratified_split_patients(patients, stratification_key, train_r, val_r, test_r, seed):
    """
    Use sklearn's StratifiedKFold or iterative stratification
    to maintain disease distribution balance
    """

    // Group patients by disease label
    disease_groups = {}
    FOR patient in patients:
        disease = stratification_key[patient]
        disease_groups[disease].append(patient)

    // Proportional split from each disease group
    train_split = []
    val_split = []
    test_split = []

    SET random_seed(seed)

    FOR disease in disease_groups:
        patients_in_group = shuffle(disease_groups[disease])
        n_total = len(patients_in_group)

        n_train = int(n_total * train_r)
        n_val = int(n_total * val_r)

        train_split.extend(patients_in_group[0:n_train])
        val_split.extend(patients_in_group[n_train:n_train+n_val])
        test_split.extend(patients_in_group[n_train+n_val:])

    RETURN {train: train_split, val: val_split, test: test_split}


FUNCTION extract_diseases_from_caption(caption_text):
    """
    Parse caption to identify disease labels
    """
    diseases = []

    // Common CXR findings
    disease_keywords = {
        "pneumonia": ["pneumonia", "consolidation", "infiltrate"],
        "pleural_effusion": ["pleural effusion", "effusion"],
        "cardiomegaly": ["cardiomegaly", "enlarged heart"],
        "edema": ["edema", "pulmonary edema"],
        "atelectasis": ["atelectasis", "collapse"],
        "pneumothorax": ["pneumothorax"],
        "nodule": ["nodule", "mass", "lesion"],
        "fracture": ["fracture", "rib fracture"],
        "normal": ["no acute", "normal", "clear lungs"]
    }

    caption_lower = caption_text.lower()

    FOR disease, keywords in disease_keywords:
        FOR keyword in keywords:
            IF keyword in caption_lower:
                diseases.append(disease)
                BREAK

    IF len(diseases) == 0:
        diseases.append("unspecified")

    RETURN diseases


FUNCTION validate_splits(train_df, val_df, test_df):
    """
    Comprehensive validation checks
    """

    // 1. Patient ID overlap check
    train_patients = get_unique_patients(train_df)
    val_patients = get_unique_patients(val_df)
    test_patients = get_unique_patients(test_df)

    ASSERT len(train_patients.intersection(val_patients)) == 0
    ASSERT len(train_patients.intersection(test_patients)) == 0
    ASSERT len(val_patients.intersection(test_patients)) == 0

    // 2. Ratio validation
    total_patients = len(train_patients) + len(val_patients) + len(test_patients)
    train_ratio = len(train_patients) / total_patients
    val_ratio = len(val_patients) / total_patients
    test_ratio = len(test_patients) / total_patients

    ASSERT abs(train_ratio - 0.80) < 0.05  # Within 5% tolerance
    ASSERT abs(val_ratio - 0.10) < 0.05
    ASSERT abs(test_ratio - 0.10) < 0.05

    // 3. Disease distribution check
    train_disease_dist = get_disease_distribution(train_df)
    val_disease_dist = get_disease_distribution(val_df)
    test_disease_dist = get_disease_distribution(test_df)

    FOR disease in train_disease_dist:
        train_pct = train_disease_dist[disease]
        val_pct = val_disease_dist[disease]
        test_pct = test_disease_dist[disease]

        // Check distributions are within 10% of each other
        ASSERT abs(train_pct - val_pct) < 0.10
        ASSERT abs(train_pct - test_pct) < 0.10

    // 4. Source balance check
    ASSERT train_df contains both CheXpert and Radiopaedia
    ASSERT val_df contains both CheXpert and Radiopaedia
    ASSERT test_df contains both CheXpert and Radiopaedia

    RETURN validation_report
```

## Edge Cases and Handling

### 1. Multi-Image Patients (CheXpert)
**Issue**: Some patients have 2-3 images (different views/studies)
**Solution**: ALL images from the same patient go to the same split
**Impact**: Slight deviation from exact 80/10/10 image ratio, but maintains patient-level integrity

### 2. Missing or Malformed Patient IDs
**Issue**: Rare cases where regex fails to extract patient ID
**Solution**:
- Log warnings for unparseable filenames
- Assign unique fallback IDs (e.g., `unknown_<hash>`)
- Treat as single-image "patients"

### 3. Rare Diseases (Long-tail Distribution)
**Issue**: Some diseases may have very few patients (<10)
**Solution**:
- Group rare diseases into "other" category for stratification
- Ensure at least 1 patient per disease in train set
- Val/test may not have all rare diseases (acceptable for small N)

### 4. Normal vs Abnormal Imbalance
**Issue**: Dataset may be heavily skewed toward abnormal cases
**Solution**:
- Stratify by normal/abnormal first
- Then sub-stratify by specific disease within abnormal group
- Use iterative stratification for multi-label cases

### 5. Caption Quality Variations
**Issue**: Captions may vary in detail/format between sources
**Solution**:
- Use NLP-based disease extraction with fuzzy matching
- Maintain manual mapping of synonyms
- Fall back to "unspecified" category if parsing fails

## Output Files

### 1. Split Indices
```
metadata/splits/train_index.csv
metadata/splits/val_index.csv
metadata/splits/test_index.csv
```

Each file contains: `filename,source,image_path,caption_path,patient_id,split`

### 2. Split Metadata
```
metadata/splits/split_metadata.json
```

Contains:
```json
{
  "generated_at": "2025-10-01T...",
  "random_seed": 42,
  "train": {
    "n_patients": 3000,
    "n_images": 3026,
    "disease_distribution": {...},
    "source_distribution": {"CheXpert": 187, "Radiopaedia": 2839}
  },
  "val": {...},
  "test": {...},
  "validation_checks": {
    "no_patient_overlap": true,
    "ratio_validation": true,
    "disease_balance": true
  }
}
```

### 3. Patient Mapping
```
metadata/splits/patient_mapping.json
```

Maps patient_id to split assignment for debugging:
```json
{
  "chexpert_patient64541": "train",
  "chexpert_patient64542": "train",
  "radiopaedia_003544": "test",
  ...
}
```

## Validation Metrics

### Pre-Split Validation
- ✓ All filenames successfully parsed for patient IDs
- ✓ All captions readable and parsed
- ✓ Disease labels extracted for all images

### Post-Split Validation
- ✓ Zero patient overlap between splits
- ✓ Train/val/test ratios within 5% tolerance
- ✓ Disease distribution within 10% across splits
- ✓ Both sources present in all splits
- ✓ Multi-image patients kept together

### Distribution Similarity Metrics
- **Chi-squared test**: p > 0.05 for disease distribution across splits
- **Jensen-Shannon divergence**: < 0.1 between train/val and train/test distributions
- **Per-disease prevalence delta**: < 10% between any two splits

## Implementation Considerations

### Libraries Required
```python
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0  # For StratifiedKFold
scipy>=1.11.0  # For statistical tests
```

### Performance
- Expected runtime: <10 seconds for 3,783 images
- Memory usage: <100 MB
- Can be run on local machine

### Reproducibility
- **Fixed random seed**: 42
- **Deterministic sorting**: Sort patient IDs before shuffling
- **Version tracking**: Log library versions in metadata

## Next Steps

1. **Implementation**: Convert pseudocode to Python implementation
2. **Caption Analysis**: Create disease label extraction module
3. **Testing**: Unit tests for each function
4. **Validation**: Run validation suite on generated splits
5. **Documentation**: Generate split statistics report

## References
- CheXpert paper: Stratified sampling by disease prevalence
- Medical imaging best practices: Patient-level splitting critical for clinical ML
- scikit-learn StratifiedKFold: Multi-label stratification approach
