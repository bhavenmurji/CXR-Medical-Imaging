#!/bin/bash

# Dataset Download Script for Cloud Environment
# Downloads and extracts medical imaging datasets in GitHub Codespaces

set -e

DATASET=$1
DATA_DIR="data/raw"

if [ -z "$DATASET" ]; then
    echo "Usage: ./download_datasets.sh [mimic-cxr|chexpert|nih-cxr14|all]"
    exit 1
fi

download_chexpert() {
    echo "📥 Downloading CheXpert dataset..."
    mkdir -p $DATA_DIR/chexpert

    # Note: CheXpert requires manual download from Stanford
    echo "⚠️  CheXpert requires registration at:"
    echo "https://stanfordaimi.azurewebsites.net/datasets/8cbd9ed4-2eb9-4565-affc-111cf4f7ebe2"
    echo ""
    echo "After downloading, place files in: $DATA_DIR/chexpert/"
}

download_nih_cxr14() {
    echo "📥 Downloading NIH Chest X-ray14 dataset..."
    mkdir -p $DATA_DIR/nih-cxr14

    # Download from NIH (requires wget)
    cd $DATA_DIR/nih-cxr14

    # Download metadata
    wget https://nihcc.app.box.com/shared/static/vfk49d74nhbxq3nqjg0900w5nvkorp5c.gz -O Data_Entry_2017.csv.gz
    gunzip Data_Entry_2017.csv.gz

    # Download images (12 archives)
    for i in {1..12}; do
        echo "Downloading archive $i of 12..."
        wget https://nihcc.app.box.com/shared/static/$(printf "images_%02d.tar.gz" $i)
    done

    echo "✅ NIH CXR-14 download complete"
    cd -
}

download_mimic_cxr() {
    echo "📥 MIMIC-CXR dataset..."
    echo "⚠️  MIMIC-CXR requires credentialed access from PhysioNet:"
    echo "https://physionet.org/content/mimic-cxr/2.0.0/"
    echo ""
    echo "After approval, use the provided download script."
}

extract_archives() {
    echo "📦 Extracting archives in $DATA_DIR..."

    # Extract all tar.gz files
    find $DATA_DIR -name "*.tar.gz" -exec tar -xzf {} -C $(dirname {}) \;

    # Extract all zip files
    find $DATA_DIR -name "*.zip" -exec unzip -q {} -d $(dirname {}) \;

    echo "✅ Extraction complete"
}

case $DATASET in
    chexpert)
        download_chexpert
        ;;
    nih-cxr14)
        download_nih_cxr14
        extract_archives
        ;;
    mimic-cxr)
        download_mimic_cxr
        ;;
    all)
        download_chexpert
        download_nih_cxr14
        download_mimic_cxr
        extract_archives
        ;;
    *)
        echo "Unknown dataset: $DATASET"
        echo "Available options: chexpert, nih-cxr14, mimic-cxr, all"
        exit 1
        ;;
esac

echo "📊 Current disk usage:"
du -sh $DATA_DIR/*
