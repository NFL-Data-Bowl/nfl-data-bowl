#!/bin/bash
echo 'is this running' run
# Set competition name and local download directory
COMPETITION_NAME="nfl-big-data-bowl-2025"
DOWNLOAD_DIR="./nfl_data"

# Ensure the download directory exists
mkdir -p "$DOWNLOAD_DIR"

# Check if Kaggle API is installed
if ! command -v kaggle &> /dev/null
then
    echo "Kaggle API is not installed. Install it using: pip install kaggle"
    exit 1
fi

# Authenticate with Kaggle (Ensure kaggle.json is set up in ~/.kaggle/)
echo "Downloading dataset for $COMPETITION_NAME..."
kaggle competitions download -c "$COMPETITION_NAME" -p "$DOWNLOAD_DIR"

# Extract files
cd "$DOWNLOAD_DIR" || exit
unzip "${COMPETITION_NAME}.zip" && rm "${COMPETITION_NAME}.zip"

echo "Dataset downloaded and extracted to $DOWNLOAD_DIR"
