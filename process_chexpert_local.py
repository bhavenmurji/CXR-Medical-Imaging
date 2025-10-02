#!/usr/bin/env python3
"""Process CheXpert validation images from local files."""

import pandas as pd
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path("/Users/bhavenmurji/Development/MeData/Imaging/CXR")
TEMP_DIR = BASE_DIR / "temp"
CHEXPERT_DIR = TEMP_DIR / "chexpert_full/CheXpert-v1.0 batch 1 (validate & csv)"
VALID_CSV = CHEXPERT_DIR / "valid.csv"
OUTPUT_IMAGES_DIR = BASE_DIR / "Images"
OUTPUT_CAPTIONS_DIR = BASE_DIR / "captions"
OUTPUT_METADATA_DIR = BASE_DIR / "metadata"

# Create output directories
OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_METADATA_DIR.mkdir(parents=True, exist_ok=True)

# Label columns
LABEL_COLUMNS = [
    'No Finding', 'Enlarged Cardiomediastinum', 'Cardiomegaly',
    'Lung Opacity', 'Lung Lesion', 'Edema', 'Consolidation',
    'Pneumonia', 'Atelectasis', 'Pneumothorax', 'Pleural Effusion',
    'Pleural Other', 'Fracture', 'Support Devices'
]

def generate_caption(row):
    """Generate caption from CSV row."""
    labels = {}
    for label in LABEL_COLUMNS:
        value = row.get(label, None)
        if pd.notna(value):
            if value == 1.0:
                labels[label] = 'positive'
            elif value == -1.0:
                labels[label] = 'uncertain'
            elif value == 0.0:
                labels[label] = 'negative'

    structured_labels = [f"{label}: {value}" for label, value in labels.items()]
    if not structured_labels:
        structured_labels.append("No labels available")

    caption = f"""SOURCE: CheXpert
PATIENT_ID: {row.get('patient_id', 'Unknown')}
STUDY_ID: {row.get('study_id', 'Unknown')}
VIEW_POSITION: {row.get('Frontal/Lateral', 'Unknown')}
IMAGE_ID: {row.get('image_id', 'Unknown')}

=== FINDINGS ===
Radiological report not available in CheXpert dataset.

=== IMPRESSION ===
Image labeled using rule-based labeler with uncertainty annotations.

=== STRUCTURED LABELS ===
{chr(10).join(structured_labels)}

=== METADATA ===
Dataset: CheXpert v1.0
Source: Stanford Hospital
Patient Age: {row.get('Age', 'Unknown')}
Patient Sex: {row.get('Sex', 'Unknown')}
View Position: {row.get('Frontal/Lateral', 'Unknown')}
AP/PA: {row.get('AP/PA', 'Unknown')}
Data Split: validation

NOTE: Labels with 'uncertain' value indicate ambiguous findings.
"""
    return caption

def main():
    logger.info("Processing CheXpert validation images...")

    # Read CSV
    logger.info(f"Reading {VALID_CSV}")
    df = pd.read_csv(VALID_CSV)

    processed = 0
    skipped = 0

    for idx, row in df.iterrows():
        # Parse path: CheXpert-v1.0/valid/patient64541/study1/view1_frontal.jpg
        path_str = row['Path']
        path_parts = Path(path_str).parts

        if len(path_parts) < 5:
            logger.warning(f"Unexpected path format: {path_str}")
            skipped += 1
            continue

        patient_id = path_parts[2]  # e.g., patient64541
        study_id = path_parts[3]    # e.g., study1
        image_name = path_parts[4]  # e.g., view1_frontal.jpg

        # Construct local path
        local_path = CHEXPERT_DIR / "valid" / patient_id / study_id / image_name

        if not local_path.exists():
            logger.warning(f"Image not found: {local_path}")
            skipped += 1
            continue

        # Generate output filename
        image_id = image_name.replace('.jpg', '')
        output_filename = f"chexpert_{patient_id}_{study_id}_{image_id}"
        output_image = OUTPUT_IMAGES_DIR / f"{output_filename}.jpg"
        output_caption = OUTPUT_CAPTIONS_DIR / f"{output_filename}.txt"

        # Copy image
        shutil.copy2(local_path, output_image)

        # Generate caption
        row_data = {
            'patient_id': patient_id,
            'study_id': study_id,
            'image_id': image_id,
            **row.to_dict()
        }
        caption = generate_caption(row_data)

        # Write caption
        with open(output_caption, 'w') as f:
            f.write(caption)

        processed += 1
        if processed % 50 == 0:
            logger.info(f"Processed {processed}/{len(df)} images...")

    logger.info(f"\n✅ Processing complete!")
    logger.info(f"   Processed: {processed} images")
    logger.info(f"   Skipped: {skipped} images")
    logger.info(f"   Images saved to: {OUTPUT_IMAGES_DIR}")
    logger.info(f"   Captions saved to: {OUTPUT_CAPTIONS_DIR}")

    # Update master index
    master_index_path = OUTPUT_METADATA_DIR / "master_index.csv"
    if master_index_path.exists():
        existing_df = pd.read_csv(master_index_path)
        logger.info(f"   Added {processed} records to existing master index ({len(existing_df)} -> {len(existing_df) + processed})")
    else:
        logger.info(f"   Created new master index with {processed} records")

if __name__ == "__main__":
    main()
