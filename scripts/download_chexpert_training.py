#!/usr/bin/env python3
"""Download all CheXpert training batches with parallel downloads and resume capability.

This script downloads approximately 470GB of CheXpert training data across 11 batches.
Estimated time: 2-8 hours depending on connection speed.
"""

import requests
import time
import json
import sys
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

# Output directory
OUTPUT_DIR = Path("/Users/bhavenmurji/Development/MeData/Imaging/CXR/temp/chexpert_azure")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Progress tracking file
PROGRESS_FILE = OUTPUT_DIR / "download_progress.json"

# CheXpert training batch URLs (valid until 2025-10-31)
# Base container URL with new SAS token
BASE_URL = "https://aimistanforddatasets01.blob.core.windows.net/chexpertchestxrays-u20210408"
SAS_TOKEN = "?sv=2019-02-02&sr=c&sig=osnjWCYGFTUQ4JtLCxpEA6gAxPoSW%2B9ZVa43jEF4khc%3D&st=2025-10-01T19%3A09%3A01Z&se=2025-10-31T19%3A14%3A01Z&sp=rl"

BATCH_URLS = {
    "batch1": {
        "url": f"{BASE_URL}/CheXpert-v1.0%20batch%201%20%28validate%20%26%20csv%29.zip{SAS_TOKEN}",
        "size_mb": 486,
        "filename": "batch1_validate.zip"
    },
    "batch2": {
        "url": f"{BASE_URL}/CheXpert-v1.0%20batch%202%20%28train%201%29.zip{SAS_TOKEN}",
        "size_mb": 166000,  # 174 GB
        "filename": "batch2_train1.zip"
    },
    "batch3": {
        "url": f"{BASE_URL}/CheXpert-v1.0%20batch%203%20%28train%202%29.zip{SAS_TOKEN}",
        "size_mb": 189000,  # 198 GB
        "filename": "batch3_train2.zip"
    },
    "batch4": {
        "url": f"{BASE_URL}/CheXpert-v1.0%20batch%204%20%28train%203%29.zip{SAS_TOKEN}",
        "size_mb": 93000,   # 97 GB
        "filename": "batch4_train3.zip"
    }
}


def load_progress() -> Dict:
    """Load download progress from file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_progress(progress: Dict):
    """Save download progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def download_batch(batch_name: str, batch_info: Dict, max_retries: int = 10) -> bool:
    """Download a single batch with retry logic and resume capability.

    Args:
        batch_name: Batch identifier (e.g., 'batch2')
        batch_info: Batch information dictionary
        max_retries: Maximum retry attempts

    Returns:
        True if successful, False otherwise
    """
    url = batch_info['url']
    output_file = OUTPUT_DIR / batch_info['filename']
    expected_size_mb = batch_info['size_mb']

    # Check if already completed
    progress = load_progress()
    if progress.get(batch_name, {}).get('status') == 'completed':
        print(f"✓ {batch_name} already downloaded")
        return True

    # Get existing file size for resume
    if output_file.exists():
        downloaded = output_file.stat().st_size
        print(f"📥 Resuming {batch_name} from {downloaded / (1024*1024):.1f} MB")
    else:
        downloaded = 0
        print(f"🆕 Starting fresh download of {batch_name}")

    retry_count = 0
    backoff_delay = 5

    while retry_count < max_retries:
        try:
            # Set resume header
            headers = {'Range': f'bytes={downloaded}-'} if downloaded > 0 else {}

            # Make request with timeout
            response = requests.get(url, headers=headers, stream=True, timeout=60)

            # Get total file size
            if 'content-length' in response.headers:
                total_size = int(response.headers['content-length'])
                if downloaded > 0:
                    total_size += downloaded
            elif 'content-range' in response.headers:
                total_size = int(response.headers['content-range'].split('/')[1])
            else:
                total_size = expected_size_mb * 1024 * 1024

            # Check if resume worked
            if response.status_code not in (200, 206):
                print(f"❌ {batch_name}: HTTP {response.status_code}")
                retry_count += 1
                time.sleep(backoff_delay)
                backoff_delay = min(backoff_delay * 2, 300)
                continue

            # Download with progress tracking
            mode = 'ab' if downloaded > 0 else 'wb'
            chunk_size = 1024 * 1024  # 1MB chunks

            print(f"⬇️  Downloading {batch_name} (attempt {retry_count + 1}/{max_retries})")
            print(f"   Target: {total_size / (1024*1024):.1f} MB")

            start_time = time.time()
            last_update = start_time
            last_downloaded = downloaded

            with open(output_file, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Print progress every 10 seconds
                        now = time.time()
                        if now - last_update >= 10:
                            elapsed = now - last_update
                            speed = (downloaded - last_downloaded) / elapsed / 1024  # KB/s
                            progress_pct = (downloaded / total_size) * 100
                            eta_seconds = (total_size - downloaded) / (speed * 1024) if speed > 0 else 0
                            eta_minutes = eta_seconds / 60

                            print(f"   {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB "
                                  f"({progress_pct:.1f}%) - {speed:.1f} KB/s - ETA: {eta_minutes:.1f} min")

                            last_update = now
                            last_downloaded = downloaded

                            # Update progress file
                            progress = load_progress()
                            progress[batch_name] = {
                                'status': 'in_progress',
                                'downloaded_bytes': downloaded,
                                'total_bytes': total_size,
                                'last_update': datetime.now().isoformat()
                            }
                            save_progress(progress)

            # Download completed
            total_time = time.time() - start_time
            avg_speed = downloaded / total_time / 1024 if total_time > 0 else 0

            print(f"\n✅ {batch_name} complete!")
            print(f"   Size: {downloaded / (1024*1024):.1f} MB")
            print(f"   Time: {total_time / 60:.1f} minutes")
            print(f"   Avg speed: {avg_speed:.1f} KB/s\n")

            # Mark as completed
            progress = load_progress()
            progress[batch_name] = {
                'status': 'completed',
                'downloaded_bytes': downloaded,
                'total_bytes': total_size,
                'completed_at': datetime.now().isoformat(),
                'duration_seconds': total_time
            }
            save_progress(progress)

            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ {batch_name}: Network error - {e}")
            retry_count += 1

            if retry_count < max_retries:
                print(f"   Retrying in {backoff_delay} seconds...")
                time.sleep(backoff_delay)
                backoff_delay = min(backoff_delay * 2, 300)
            else:
                print(f"❌ {batch_name}: Failed after {max_retries} attempts")

                # Save failure status
                progress = load_progress()
                progress[batch_name] = {
                    'status': 'failed',
                    'downloaded_bytes': downloaded,
                    'error': str(e),
                    'failed_at': datetime.now().isoformat()
                }
                save_progress(progress)
                return False

        except KeyboardInterrupt:
            print(f"\n⏸️  {batch_name}: Interrupted by user")
            print(f"   Progress saved at {downloaded / (1024*1024):.1f} MB")

            # Save interrupted status
            progress = load_progress()
            progress[batch_name] = {
                'status': 'interrupted',
                'downloaded_bytes': downloaded,
                'interrupted_at': datetime.now().isoformat()
            }
            save_progress(progress)
            raise

        except Exception as e:
            print(f"❌ {batch_name}: Unexpected error - {e}")
            retry_count += 1
            time.sleep(backoff_delay)
            backoff_delay = min(backoff_delay * 2, 300)

    return False


def main():
    """Main entry point for batch downloader."""
    import argparse

    parser = argparse.ArgumentParser(description='Download CheXpert training batches')
    parser.add_argument('--parallel', type=int, default=1, choices=[1, 2, 3],
                        help='Number of parallel downloads (1=sequential, 2-3=parallel)')
    parser.add_argument('--skip-check', action='store_true',
                        help='Skip disk space check')
    args = parser.parse_args()

    print("=" * 80)
    print("CheXpert Training Batches Downloader")
    print("=" * 80)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Total batches: {len(BATCH_URLS)}")
    print(f"Estimated total size: ~448 GB (174 + 198 + 97 GB)")
    print(f"Estimated time: 3-12 hours (depending on connection)")
    print(f"Parallel downloads: {args.parallel}")
    print("=" * 80)
    print()

    # Check disk space
    if not args.skip_check:
        import shutil
        total, used, free = shutil.disk_usage(OUTPUT_DIR.parent)
        free_gb = free / (1024**3)

        print(f"💾 Available disk space: {free_gb:.1f} GB")
        if free_gb < 500:
            print(f"⚠️  Warning: Less than 500GB available!")
            print("   Continuing anyway (use --skip-check to suppress this warning)")
        print()

    # Load existing progress
    progress = load_progress()
    completed = [k for k, v in progress.items() if v.get('status') == 'completed']
    pending = [k for k in BATCH_URLS.keys() if k not in completed]

    print(f"📊 Status: {len(completed)}/{len(BATCH_URLS)} batches completed")
    if completed:
        print(f"   Completed: {', '.join(completed)}")
    if pending:
        print(f"   Pending: {', '.join(pending)}")
    print()

    parallel_count = args.parallel

    start_time = time.time()

    if parallel_count == 1:
        # Sequential download
        print("🚀 Starting sequential downloads...\n")
        for batch_name in pending:
            batch_info = BATCH_URLS[batch_name]
            success = download_batch(batch_name, batch_info)
            if not success:
                print(f"\n⚠️  {batch_name} failed. Continuing with next batch...\n")
    else:
        # Parallel download
        print(f"🚀 Starting parallel downloads ({parallel_count} concurrent)...\n")

        with ThreadPoolExecutor(max_workers=parallel_count) as executor:
            futures = {
                executor.submit(download_batch, batch_name, BATCH_URLS[batch_name]): batch_name
                for batch_name in pending
            }

            for future in as_completed(futures):
                batch_name = futures[future]
                try:
                    success = future.result()
                    if not success:
                        print(f"⚠️  {batch_name} failed")
                except Exception as e:
                    print(f"❌ {batch_name} crashed: {e}")

    # Final summary
    total_time = time.time() - start_time
    progress = load_progress()
    completed = [k for k, v in progress.items() if v.get('status') == 'completed']
    failed = [k for k, v in progress.items() if v.get('status') == 'failed']

    print("\n" + "=" * 80)
    print("Download Summary")
    print("=" * 80)
    print(f"Total time: {total_time / 3600:.2f} hours")
    print(f"Completed: {len(completed)}/{len(BATCH_URLS)} batches")

    if completed:
        print(f"\n✅ Successfully downloaded:")
        for batch in completed:
            size = progress[batch].get('downloaded_bytes', 0) / (1024**3)
            print(f"   - {batch}: {size:.2f} GB")

    if failed:
        print(f"\n❌ Failed downloads:")
        for batch in failed:
            print(f"   - {batch}")
        print("\nRun this script again to retry failed downloads.")

    if len(completed) == len(BATCH_URLS):
        print("\n🎉 All batches downloaded successfully!")
        print("\nNext steps:")
        print("1. Verify integrity of downloaded files")
        print("2. Extract archives")
        print("3. Process training images")

    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Download interrupted by user")
        print("Progress has been saved. Run this script again to resume.")
        sys.exit(0)
