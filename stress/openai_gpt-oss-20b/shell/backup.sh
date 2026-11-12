#!/bin/sh
set -e

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <source_folder> <destination_root>" >&2
  exit 1
fi

SRC="$1"
DEST_ROOT="$2"

if [ ! -d "$SRC" ]; then
  echo "Error: source folder \"$SRC\" does not exist or is not a directory." >&2
  exit 1
fi

DATE=$(date +"%Y%m%d_%H%M%S")
DEST_DIR="${DEST_ROOT}/${DATE}"

mkdir -p "$DEST_DIR"

cp -a "$SRC" "$DEST_DIR"

echo "Backup of \"$SRC\" completed at \"$DEST_DIR\"."
