#!/usr/bin/env python3
"""Generate master index and statistics for downloaded datasets."""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# Paths
BASE_DIR = Path("/Users/bhavenmurji/Development/MeData/Imaging/CXR")
IMAGES_DIR = BASE_DIR / "Images"
CAPTIONS_DIR = BASE_DIR / "captions"
METADATA_DIR = BASE_DIR / "metadata"

def generate_master_index():
    """Generate master index CSV with all image-caption pairs."""

    print("Generating master index...")

    # Get all images
    image_files = sorted(IMAGES_DIR.glob("*.jpg"))

    records = []
    for img_path in image_files:
        filename = img_path.name
        caption_path = CAPTIONS_DIR / f"{img_path.stem}.txt"

        # Determine source from filename
        if filename.startswith("radiopaedia_"):
            source = "Radiopaedia"
        elif filename.startswith("chexpert_"):
            source = "CheXpert"
        elif filename.startswith("nih_"):
            source = "NIH"
        elif filename.startswith("mimic_"):
            source = "MIMIC-CXR"
        else:
            source = "Unknown"

        # Get file stats
        file_size_mb = img_path.stat().st_size / (1024 * 1024)

        # Check if caption exists
        has_caption = caption_path.exists()

        record = {
            'filename': filename,
            'source': source,
            'image_path': str(img_path.relative_to(BASE_DIR)),
            'caption_path': str(caption_path.relative_to(BASE_DIR)) if has_caption else '',
            'has_caption': has_caption,
            'file_size_mb': round(file_size_mb, 3),
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        records.append(record)

    # Create DataFrame
    df = pd.DataFrame(records)

    # Save master index
    master_index_path = METADATA_DIR / "master_index.csv"
    df.to_csv(master_index_path, index=False)

    print(f"✅ Master index saved: {master_index_path}")
    print(f"   Total records: {len(df)}")

    return df

def generate_statistics(df):
    """Generate statistics report."""

    print("\n" + "="*60)
    print("DATASET STATISTICS REPORT")
    print("="*60)

    # Overall stats
    total_images = len(df)
    total_captions = df['has_caption'].sum()
    total_size_mb = df['file_size_mb'].sum()

    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total Images: {total_images:,}")
    print(f"   Total Captions: {total_captions:,}")
    print(f"   Total Size: {total_size_mb:.1f} MB ({total_size_mb/1024:.2f} GB)")
    print(f"   Average Image Size: {df['file_size_mb'].mean():.3f} MB")

    # By source
    print(f"\n📁 BREAKDOWN BY SOURCE:")
    source_stats = df.groupby('source').agg({
        'filename': 'count',
        'has_caption': 'sum',
        'file_size_mb': 'sum'
    }).rename(columns={
        'filename': 'images',
        'has_caption': 'captions',
        'file_size_mb': 'size_mb'
    })

    for source, row in source_stats.iterrows():
        print(f"\n   {source}:")
        print(f"      Images: {int(row['images']):,}")
        print(f"      Captions: {int(row['captions']):,}")
        print(f"      Size: {row['size_mb']:.1f} MB")
        print(f"      Avg Size: {row['size_mb']/row['images']:.3f} MB/image")

    # Save JSON report
    stats_dict = {
        'generated_at': datetime.now().isoformat(),
        'overall': {
            'total_images': int(total_images),
            'total_captions': int(total_captions),
            'total_size_mb': float(total_size_mb),
            'total_size_gb': float(total_size_mb / 1024),
            'avg_image_size_mb': float(df['file_size_mb'].mean())
        },
        'by_source': {}
    }

    for source, row in source_stats.iterrows():
        stats_dict['by_source'][source] = {
            'images': int(row['images']),
            'captions': int(row['captions']),
            'size_mb': float(row['size_mb']),
            'size_gb': float(row['size_mb'] / 1024),
            'avg_size_mb': float(row['size_mb'] / row['images'])
        }

    stats_path = METADATA_DIR / "dataset_statistics.json"
    with open(stats_path, 'w') as f:
        json.dump(stats_dict, f, indent=2)

    print(f"\n✅ Statistics saved: {stats_path}")

    return stats_dict

def check_integrity():
    """Check data integrity."""

    print("\n" + "="*60)
    print("DATA INTEGRITY CHECK")
    print("="*60)

    issues = []

    # Check for images without captions
    images = set(f.stem for f in IMAGES_DIR.glob("*.jpg"))
    captions = set(f.stem for f in CAPTIONS_DIR.glob("*.txt"))

    missing_captions = images - captions
    orphaned_captions = captions - images

    if missing_captions:
        print(f"\n⚠️  {len(missing_captions)} images without captions")
        issues.append(f"{len(missing_captions)} images without captions")
    else:
        print(f"\n✅ All images have captions")

    if orphaned_captions:
        print(f"⚠️  {len(orphaned_captions)} captions without images")
        issues.append(f"{len(orphaned_captions)} captions without images")
    else:
        print(f"✅ No orphaned captions")

    print(f"\n{'✅ Data integrity: PASSED' if not issues else '⚠️  Data integrity: ISSUES FOUND'}")

    return len(issues) == 0

if __name__ == "__main__":
    print("Starting master index generation...\n")

    # Ensure metadata directory exists
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # Generate master index
    df = generate_master_index()

    # Generate statistics
    stats = generate_statistics(df)

    # Check integrity
    integrity_ok = check_integrity()

    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print(f"\nDataset ready for AI training:")
    print(f"  • {len(df):,} image-caption pairs")
    print(f"  • {stats['overall']['total_size_gb']:.2f} GB total")
    print(f"  • Master index: {METADATA_DIR}/master_index.csv")
    print(f"  • Statistics: {METADATA_DIR}/dataset_statistics.json")
