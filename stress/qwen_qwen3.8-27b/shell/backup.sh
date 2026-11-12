#!/bin/sh
set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <source_folder> <destination_folder>" >&2
    exit 1
fi

source_folder="$1"
destination_folder="$2"

if [ ! -d "$source_folder" ]; then
    echo "Error: Source folder '$source_folder' does not exist." >&2
    exit 1
fi

mkdir -p "$destination_folder"

date_str=$(date +"%Y-%m-%d_%H-%M-%S")
basename_source=$(basename "$source_folder")
target_folder="${destination_folder}/${basename_source}_backup_${date_str}"

cp -r "$source_folder" "$target_folder"

echo "Backup completed: $target_folder"
