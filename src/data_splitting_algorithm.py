"""
Patient-Level Data Splitting Algorithm
Implements stratified patient-level splitting for medical imaging datasets
ensuring no data leakage between train/validation/test sets.

Author: Data Processing Agent
Date: 2025-10-01
"""

import pandas as pd
import numpy as np
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
from sklearn.model_selection import StratifiedKFold
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatientLevelDataSplitter:
    """
    Handles patient-level stratified splitting of medical imaging datasets.

    Key Features:
    - Patient-level splitting (all images from one patient in same split)
    - Stratified by disease distribution
    - Handles multi-image patients
    - Validates no patient overlap
    - Generates comprehensive metadata
    """

    def __init__(self, master_index_path: str, random_seed: int = 42):
        """
        Initialize the data splitter.

        Args:
            master_index_path: Path to master_index.csv
            random_seed: Random seed for reproducibility
        """
        self.master_index_path = Path(master_index_path)
        self.random_seed = random_seed
        self.master_df = None
        self.patient_data = defaultdict(list)
        self.disease_labels = {}
        self.splits = {}

        np.random.seed(random_seed)

    def load_master_index(self) -> pd.DataFrame:
        """Load and validate master index file."""
        logger.info(f"Loading master index from {self.master_index_path}")
        self.master_df = pd.read_csv(self.master_index_path)

        required_columns = ['filename', 'source', 'image_path', 'caption_path', 'has_caption']
        missing_cols = set(required_columns) - set(self.master_df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        logger.info(f"Loaded {len(self.master_df)} images")
        return self.master_df

    def extract_patient_id(self, filename: str, source: str) -> str:
        """
        Extract patient ID from filename based on source.

        Args:
            filename: Image filename
            source: Data source (CheXpert or Radiopaedia)

        Returns:
            patient_id: Unique patient identifier
        """
        if source == "CheXpert":
            match = re.search(r'patient(\d+)', filename)
            if match:
                return f"chexpert_patient{match.group(1)}"
            else:
                # Fallback for unparseable filenames
                logger.warning(f"Could not extract patient ID from: {filename}")
                return f"chexpert_unknown_{hash(filename)}"

        elif source == "Radiopaedia":
            match = re.search(r'radiopaedia_(\d+)', filename)
            if match:
                return f"radiopaedia_{match.group(1)}"
            else:
                logger.warning(f"Could not extract case ID from: {filename}")
                return f"radiopaedia_unknown_{hash(filename)}"

        else:
            raise ValueError(f"Unknown source: {source}")

    def group_by_patient(self) -> Dict[str, List[Dict]]:
        """
        Group all images by patient ID.

        Returns:
            patient_data: Dictionary mapping patient_id to list of image records
        """
        logger.info("Grouping images by patient...")

        for idx, row in self.master_df.iterrows():
            patient_id = self.extract_patient_id(row['filename'], row['source'])
            row_dict = row.to_dict()
            row_dict['patient_id'] = patient_id
            self.patient_data[patient_id].append(row_dict)

        logger.info(f"Found {len(self.patient_data)} unique patients")

        # Log multi-image patients
        multi_image = {pid: len(images) for pid, images in self.patient_data.items() if len(images) > 1}
        if multi_image:
            logger.info(f"{len(multi_image)} patients have multiple images")
            logger.info(f"Max images per patient: {max(multi_image.values())}")

        return self.patient_data

    def extract_diseases_from_caption(self, caption_path: str) -> List[str]:
        """
        Parse caption file to extract disease labels.

        Args:
            caption_path: Path to caption text file

        Returns:
            diseases: List of disease labels found in caption
        """
        disease_keywords = {
            "pneumonia": ["pneumonia", "consolidation", "infiltrate"],
            "pleural_effusion": ["pleural effusion", "effusion"],
            "cardiomegaly": ["cardiomegaly", "enlarged heart", "cardiac enlargement"],
            "edema": ["edema", "pulmonary edema"],
            "atelectasis": ["atelectasis", "collapse"],
            "pneumothorax": ["pneumothorax"],
            "nodule": ["nodule", "mass", "lesion"],
            "fracture": ["fracture", "rib fracture"],
            "normal": ["no acute", "normal", "clear lungs", "unremarkable"],
        }

        try:
            with open(caption_path, 'r', encoding='utf-8') as f:
                caption_text = f.read().lower()
        except Exception as e:
            logger.warning(f"Could not read caption {caption_path}: {e}")
            return ["unspecified"]

        diseases = []
        for disease, keywords in disease_keywords.items():
            for keyword in keywords:
                if keyword in caption_text:
                    diseases.append(disease)
                    break

        # Default to unspecified if no diseases found
        if not diseases:
            diseases.append("unspecified")

        return diseases

    def extract_patient_disease_labels(self) -> Dict[str, List[str]]:
        """
        Extract disease labels for all patients by analyzing their captions.

        Returns:
            disease_labels: Dictionary mapping patient_id to list of diseases
        """
        logger.info("Extracting disease labels from captions...")

        for patient_id, images in self.patient_data.items():
            all_diseases = []
            for image in images:
                caption_path = image['caption_path']
                diseases = self.extract_diseases_from_caption(caption_path)
                all_diseases.extend(diseases)

            # Get unique diseases for this patient
            self.disease_labels[patient_id] = list(set(all_diseases))

        logger.info(f"Extracted disease labels for {len(self.disease_labels)} patients")
        return self.disease_labels

    def get_stratification_key(self, patient_id: str) -> str:
        """
        Create stratification key for patient based on primary disease.

        Args:
            patient_id: Patient identifier

        Returns:
            stratification_key: Primary disease label for stratification
        """
        diseases = self.disease_labels.get(patient_id, ["unspecified"])

        # Priority order for stratification (most clinically significant first)
        priority_diseases = [
            "pneumonia", "pneumothorax", "pleural_effusion",
            "cardiomegaly", "edema", "atelectasis",
            "nodule", "fracture", "normal", "unspecified"
        ]

        for disease in priority_diseases:
            if disease in diseases:
                return disease

        return diseases[0] if diseases else "unspecified"

    def stratified_split_patients(
        self,
        patient_ids: List[str],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1
    ) -> Dict[str, List[str]]:
        """
        Perform stratified split of patients maintaining disease distribution.

        Args:
            patient_ids: List of patient IDs to split
            train_ratio: Proportion for training set (default 0.8)
            val_ratio: Proportion for validation set (default 0.1)
            test_ratio: Proportion for test set (default 0.1)

        Returns:
            splits: Dictionary with 'train', 'val', 'test' patient lists
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, "Ratios must sum to 1.0"

        # Get stratification labels for each patient
        stratification_labels = [self.get_stratification_key(pid) for pid in patient_ids]

        # Group patients by disease for proportional sampling
        disease_groups = defaultdict(list)
        for pid, label in zip(patient_ids, stratification_labels):
            disease_groups[label].append(pid)

        train_patients = []
        val_patients = []
        test_patients = []

        # Split each disease group proportionally
        for disease, patients in disease_groups.items():
            n_total = len(patients)

            # Shuffle patients
            np.random.shuffle(patients)

            # Calculate split sizes
            n_train = int(n_total * train_ratio)
            n_val = int(n_total * val_ratio)
            # Test gets remainder to ensure all patients are assigned

            train_patients.extend(patients[:n_train])
            val_patients.extend(patients[n_train:n_train + n_val])
            test_patients.extend(patients[n_train + n_val:])

        logger.info(f"Split {len(patient_ids)} patients: "
                   f"train={len(train_patients)}, val={len(val_patients)}, test={len(test_patients)}")

        return {
            'train': train_patients,
            'val': val_patients,
            'test': test_patients
        }

    def create_splits(
        self,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1
    ) -> Dict[str, pd.DataFrame]:
        """
        Main method to create train/val/test splits.

        Args:
            train_ratio: Training set proportion
            val_ratio: Validation set proportion
            test_ratio: Test set proportion

        Returns:
            splits: Dictionary with 'train', 'val', 'test' DataFrames
        """
        logger.info("Creating patient-level stratified splits...")

        # Split by source separately to maintain source balance
        chexpert_patients = [pid for pid in self.patient_data.keys() if pid.startswith("chexpert_")]
        radiopaedia_patients = [pid for pid in self.patient_data.keys() if pid.startswith("radiopaedia_")]

        logger.info(f"CheXpert patients: {len(chexpert_patients)}")
        logger.info(f"Radiopaedia patients: {len(radiopaedia_patients)}")

        # Stratified split for each source
        chexpert_splits = self.stratified_split_patients(chexpert_patients, train_ratio, val_ratio, test_ratio)
        radiopaedia_splits = self.stratified_split_patients(radiopaedia_patients, train_ratio, val_ratio, test_ratio)

        # Combine splits
        train_patients = chexpert_splits['train'] + radiopaedia_splits['train']
        val_patients = chexpert_splits['val'] + radiopaedia_splits['val']
        test_patients = chexpert_splits['test'] + radiopaedia_splits['test']

        # Expand patients to images
        def patients_to_dataframe(patient_list: List[str], split_name: str) -> pd.DataFrame:
            records = []
            for patient_id in patient_list:
                for image in self.patient_data[patient_id]:
                    image['split'] = split_name
                    records.append(image)
            return pd.DataFrame(records)

        train_df = patients_to_dataframe(train_patients, 'train')
        val_df = patients_to_dataframe(val_patients, 'val')
        test_df = patients_to_dataframe(test_patients, 'test')

        logger.info(f"Final split sizes (images): train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")

        self.splits = {
            'train': train_df,
            'val': val_df,
            'test': test_df,
            'train_patients': train_patients,
            'val_patients': val_patients,
            'test_patients': test_patients
        }

        return self.splits

    def validate_splits(self) -> Dict[str, bool]:
        """
        Comprehensive validation of data splits.

        Returns:
            validation_results: Dictionary of validation checks and their status
        """
        logger.info("Validating splits...")

        train_patients = set(self.splits['train_patients'])
        val_patients = set(self.splits['val_patients'])
        test_patients = set(self.splits['test_patients'])

        validation_results = {}

        # 1. No patient overlap
        train_val_overlap = train_patients.intersection(val_patients)
        train_test_overlap = train_patients.intersection(test_patients)
        val_test_overlap = val_patients.intersection(test_patients)

        validation_results['no_patient_overlap'] = (
            len(train_val_overlap) == 0 and
            len(train_test_overlap) == 0 and
            len(val_test_overlap) == 0
        )

        if not validation_results['no_patient_overlap']:
            logger.error(f"Patient overlap detected! "
                        f"train-val: {len(train_val_overlap)}, "
                        f"train-test: {len(train_test_overlap)}, "
                        f"val-test: {len(val_test_overlap)}")

        # 2. Ratio validation
        total_patients = len(train_patients) + len(val_patients) + len(test_patients)
        train_ratio = len(train_patients) / total_patients
        val_ratio = len(val_patients) / total_patients
        test_ratio = len(test_patients) / total_patients

        validation_results['ratio_validation'] = (
            abs(train_ratio - 0.80) < 0.05 and
            abs(val_ratio - 0.10) < 0.05 and
            abs(test_ratio - 0.10) < 0.05
        )

        logger.info(f"Patient ratios: train={train_ratio:.3f}, val={val_ratio:.3f}, test={test_ratio:.3f}")

        # 3. Source balance check
        for split_name in ['train', 'val', 'test']:
            split_df = self.splits[split_name]
            sources = split_df['source'].unique()
            validation_results[f'{split_name}_has_both_sources'] = len(sources) == 2
            logger.info(f"{split_name} sources: {list(sources)}")

        # 4. All patients assigned
        all_patients = set(self.patient_data.keys())
        assigned_patients = train_patients.union(val_patients).union(test_patients)
        validation_results['all_patients_assigned'] = all_patients == assigned_patients

        if not validation_results['all_patients_assigned']:
            missing = all_patients - assigned_patients
            logger.warning(f"{len(missing)} patients not assigned to any split")

        # Overall validation
        validation_results['overall_valid'] = all(
            v for k, v in validation_results.items() if k != 'overall_valid'
        )

        logger.info(f"Validation complete. Overall valid: {validation_results['overall_valid']}")
        return validation_results

    def get_disease_distribution(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate disease prevalence in a split."""
        patient_ids = df['patient_id'].unique()
        disease_counts = Counter()

        for pid in patient_ids:
            diseases = self.disease_labels.get(pid, [])
            disease_counts.update(diseases)

        total = len(patient_ids)
        return {disease: count / total for disease, count in disease_counts.items()}

    def save_splits(self, output_dir: str):
        """
        Save splits to CSV files and generate metadata.

        Args:
            output_dir: Directory to save split files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving splits to {output_path}")

        # Save split CSVs
        self.splits['train'].to_csv(output_path / 'train_index.csv', index=False)
        self.splits['val'].to_csv(output_path / 'val_index.csv', index=False)
        self.splits['test'].to_csv(output_path / 'test_index.csv', index=False)

        # Generate metadata
        metadata = {
            "generated_at": pd.Timestamp.now().isoformat(),
            "random_seed": self.random_seed,
            "train": {
                "n_patients": len(self.splits['train_patients']),
                "n_images": len(self.splits['train']),
                "disease_distribution": self.get_disease_distribution(self.splits['train']),
                "source_distribution": self.splits['train']['source'].value_counts().to_dict()
            },
            "val": {
                "n_patients": len(self.splits['val_patients']),
                "n_images": len(self.splits['val']),
                "disease_distribution": self.get_disease_distribution(self.splits['val']),
                "source_distribution": self.splits['val']['source'].value_counts().to_dict()
            },
            "test": {
                "n_patients": len(self.splits['test_patients']),
                "n_images": len(self.splits['test']),
                "disease_distribution": self.get_disease_distribution(self.splits['test']),
                "source_distribution": self.splits['test']['source'].value_counts().to_dict()
            },
            "validation_checks": self.validate_splits()
        }

        with open(output_path / 'split_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        # Save patient mapping for debugging
        patient_mapping = {}
        for split_name in ['train', 'val', 'test']:
            for patient_id in self.splits[f'{split_name}_patients']:
                patient_mapping[patient_id] = split_name

        with open(output_path / 'patient_mapping.json', 'w') as f:
            json.dump(patient_mapping, f, indent=2)

        logger.info("Splits saved successfully!")

    def run_full_pipeline(self, output_dir: str = 'metadata/splits') -> Dict[str, pd.DataFrame]:
        """
        Execute the complete splitting pipeline.

        Args:
            output_dir: Directory to save output files

        Returns:
            splits: Dictionary with train/val/test DataFrames
        """
        logger.info("=" * 60)
        logger.info("PATIENT-LEVEL DATA SPLITTING PIPELINE")
        logger.info("=" * 60)

        # Step 1: Load data
        self.load_master_index()

        # Step 2: Group by patient
        self.group_by_patient()

        # Step 3: Extract disease labels
        self.extract_patient_disease_labels()

        # Step 4: Create stratified splits
        splits = self.create_splits()

        # Step 5: Validate splits
        validation_results = self.validate_splits()

        if not validation_results['overall_valid']:
            logger.warning("Validation failed! Review logs for details.")

        # Step 6: Save results
        self.save_splits(output_dir)

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)

        return splits


def main():
    """Command-line interface for data splitting."""
    import argparse

    parser = argparse.ArgumentParser(description='Patient-level data splitting for medical imaging')
    parser.add_argument('--master-index', type=str, default='metadata/master_index.csv',
                       help='Path to master index CSV')
    parser.add_argument('--output-dir', type=str, default='metadata/splits',
                       help='Output directory for splits')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                       help='Training set proportion')
    parser.add_argument('--val-ratio', type=float, default=0.1,
                       help='Validation set proportion')
    parser.add_argument('--test-ratio', type=float, default=0.1,
                       help='Test set proportion')
    parser.add_argument('--random-seed', type=int, default=42,
                       help='Random seed for reproducibility')

    args = parser.parse_args()

    # Create splitter and run pipeline
    splitter = PatientLevelDataSplitter(args.master_index, args.random_seed)
    splitter.run_full_pipeline(args.output_dir)


if __name__ == '__main__':
    main()
