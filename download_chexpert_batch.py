#!/usr/bin/env python3
"""Download CheXpert batch with retry logic and resume capability."""

import requests
import time
from pathlib import Path
import sys

def download_with_retry(url, output_file, max_retries=10, chunk_size=1024*1024):
    """Download file with retry logic and resume capability.

    Args:
        url: Download URL
        output_file: Output file path
        max_retries: Maximum number of retry attempts
        chunk_size: Download chunk size in bytes (default 1MB)
    """
    output_path = Path(output_file)

    # Get existing file size for resume
    if output_path.exists():
        downloaded = output_path.stat().st_size
        print(f"Resuming from {downloaded / (1024*1024):.1f} MB")
    else:
        downloaded = 0

    retry_count = 0
    backoff_delay = 5  # Start with 5 second delay

    while retry_count < max_retries:
        try:
            # Set resume header
            headers = {'Range': f'bytes={downloaded}-'} if downloaded > 0 else {}

            # Make request with timeout
            response = requests.get(url, headers=headers, stream=True, timeout=30)

            # Get total file size
            if 'content-length' in response.headers:
                total_size = int(response.headers['content-length'])
                if downloaded > 0:
                    total_size += downloaded
            elif 'content-range' in response.headers:
                # Parse: bytes 26214400-534429165/534429166
                total_size = int(response.headers['content-range'].split('/')[1])
            else:
                total_size = None

            # Check if resume worked
            if response.status_code not in (200, 206):
                print(f"HTTP {response.status_code}: {response.reason}")
                retry_count += 1
                time.sleep(backoff_delay)
                backoff_delay *= 2
                continue

            # Open file in append mode
            mode = 'ab' if downloaded > 0 else 'wb'

            print(f"Starting download (attempt {retry_count + 1}/{max_retries})...")
            if total_size:
                print(f"Target size: {total_size / (1024*1024):.1f} MB")

            with open(output_path, mode) as f:
                last_update = time.time()
                last_downloaded = downloaded

                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Print progress every 5 seconds
                        now = time.time()
                        if now - last_update >= 5:
                            elapsed = now - last_update
                            speed = (downloaded - last_downloaded) / elapsed / 1024  # KB/s

                            if total_size:
                                progress = (downloaded / total_size) * 100
                                print(f"  {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({progress:.1f}%) - {speed:.1f} KB/s")
                            else:
                                print(f"  {downloaded / (1024*1024):.1f} MB - {speed:.1f} KB/s")

                            last_update = now
                            last_downloaded = downloaded

            # Download completed successfully
            print(f"\n✅ Download complete: {output_path}")
            print(f"Final size: {downloaded / (1024*1024):.1f} MB")
            return True

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Network error: {e}")
            retry_count += 1

            if retry_count < max_retries:
                print(f"Retrying in {backoff_delay} seconds...")
                time.sleep(backoff_delay)
                backoff_delay = min(backoff_delay * 2, 300)  # Max 5 min delay
            else:
                print(f"\n❌ Failed after {max_retries} attempts")
                return False

        except KeyboardInterrupt:
            print("\n\n⏸️  Download interrupted by user")
            print(f"Progress saved at {downloaded / (1024*1024):.1f} MB")
            print("Run script again to resume")
            return False

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            retry_count += 1
            time.sleep(backoff_delay)
            backoff_delay = min(backoff_delay * 2, 300)

    return False


if __name__ == "__main__":
    # CheXpert batch 1 URL
    url = "https://aimistanforddatasets01.blob.core.windows.net/chexpertchestxrays-u20210408/CheXpert-v1.0%20batch%201%20%28validate%20%26%20csv%29.zip?sv=2019-02-02&sr=c&sig=9DPasveoV2G3NEDFnMFasOQG3r2HwmavlwzAInpf17s%3D&st=2025-10-01T14%3A40%3A57Z&se=2025-10-31T14%3A45%3A57Z&sp=rl"

    output_file = "/Users/bhavenmurji/Development/MeData/Imaging/CXR/temp/chexpert_azure/batch1.zip"

    # Create output directory
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CheXpert Batch 1 Downloader")
    print("=" * 60)
    print(f"Output: {output_file}")
    print(f"Expected size: ~509 MB")
    print("=" * 60)
    print()

    success = download_with_retry(url, output_file, max_retries=10, chunk_size=512*1024)

    sys.exit(0 if success else 1)
