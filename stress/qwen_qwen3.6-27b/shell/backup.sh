#!/bin/sh
set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <source_folder> <destination_folder>" >&2
    exit 1
fi

src="$1"
dst_base="$2"
datestamp="$(date +%Y%m%d_%H%M%S)"
dst="$dst_base/$datestamp"

mkdir -p "$dst"
cp -R "$src" "$dst/"
