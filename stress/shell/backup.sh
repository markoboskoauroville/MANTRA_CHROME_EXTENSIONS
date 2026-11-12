#!/bin/sh
set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <source_folder> <destination_base>" >&2
    exit 1
fi

SOURCE="$1"
DEST_BASE="$2"

if [ ! -d "$SOURCE" ]; then
    echo "Error: Source folder '$SOURCE' does not exist." >&2
    exit 1
fi

DATE=$(date +%Y%m%d_%H%M%S)
DEST_DIR="$DEST_BASE/backup_${DATE}"

cp -R "$SOURCE" "$DEST_DIR"
echo "Backup created at: $DEST_DIR"
