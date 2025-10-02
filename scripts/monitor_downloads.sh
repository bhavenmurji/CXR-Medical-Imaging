#!/bin/bash
# Monitor CheXpert download progress

PROGRESS_FILE="temp/chexpert_azure/download_progress.json"
OUTPUT_DIR="temp/chexpert_azure"

echo "CheXpert Download Monitor"
echo "========================"
echo ""

while true; do
    clear
    echo "CheXpert Download Monitor - $(date)"
    echo "========================================"
    echo ""

    # Check if progress file exists
    if [ -f "$PROGRESS_FILE" ]; then
        echo "📊 Current Progress:"
        echo ""

        # Parse JSON and display status
        python3 -c "
import json
import sys
from pathlib import Path

try:
    with open('$PROGRESS_FILE', 'r') as f:
        progress = json.load(f)

    completed = [k for k, v in progress.items() if v.get('status') == 'completed']
    in_progress = [k for k, v in progress.items() if v.get('status') == 'in_progress']
    failed = [k for k, v in progress.items() if v.get('status') == 'failed']

    total = 11
    print(f'Summary: {len(completed)}/{total} completed, {len(in_progress)} in progress, {len(failed)} failed')
    print()

    if in_progress:
        print('In Progress:')
        for batch in in_progress:
            info = progress[batch]
            downloaded = info.get('downloaded_bytes', 0) / (1024**3)
            total_size = info.get('total_bytes', 1) / (1024**3)
            pct = (info.get('downloaded_bytes', 0) / info.get('total_bytes', 1)) * 100 if info.get('total_bytes') else 0
            print(f'  {batch}: {downloaded:.2f} GB / {total_size:.2f} GB ({pct:.1f}%)')
        print()

    if completed:
        print('Completed:')
        for batch in completed:
            info = progress[batch]
            size = info.get('downloaded_bytes', 0) / (1024**3)
            duration = info.get('duration_seconds', 0) / 60
            print(f'  {batch}: {size:.2f} GB (took {duration:.1f} min)')
        print()

    if failed:
        print('Failed:')
        for batch in failed:
            print(f'  {batch}: {progress[batch].get(\"error\", \"Unknown error\")}')
        print()

except Exception as e:
    print(f'Error reading progress: {e}')
" 2>/dev/null || echo "Unable to parse progress file"

    else
        echo "⏳ Waiting for download to start..."
        echo ""
        echo "Progress file not found: $PROGRESS_FILE"
    fi

    echo ""
    echo "========================================"

    # Check disk usage
    if [ -d "$OUTPUT_DIR" ]; then
        echo ""
        echo "💾 Disk Usage:"
        du -sh "$OUTPUT_DIR" 2>/dev/null || echo "  Directory not accessible"
        df -h "$OUTPUT_DIR" | tail -1 | awk '{print "  Available: " $4 " (" $5 " used)"}'
    fi

    echo ""
    echo "Press Ctrl+C to stop monitoring (downloads will continue)"
    echo "Refreshing in 30 seconds..."

    sleep 30
done
