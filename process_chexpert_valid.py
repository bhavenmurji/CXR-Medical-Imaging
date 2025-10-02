#!/usr/bin/env python3
"""Process CheXpert validation images only."""

import sys
import os
sys.path.insert(0, '/Users/bhavenmurji/Development/MeData/Imaging/CXR/cxr_dataset_downloader')

from main import main

if __name__ == "__main__":
    # Set limit to validation images only
    sys.argv = ['main.py', 'download', '--source', 'chexpert', '--limit', '234']
    main()
