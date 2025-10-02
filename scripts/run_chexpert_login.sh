#!/bin/bash
# Wrapper script to run CheXpert URL retrieval with virtual environment

cd "$(dirname "$0")/.." || exit 1

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "🚀 Running CheXpert URL retrieval script..."
echo ""

# Run the Python script with all arguments passed through
python3 scripts/get_chexpert_urls.py "$@"

exit_code=$?

deactivate

exit $exit_code
