#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from collections import Counter

def parse_args():
    parser = argparse.ArgumentParser(
        description="Count files by extension in a folder and display a sorted table."
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Path to the folder to analyze."
    )
    return parser.parse_args()

def main():
    args = parse_args()
    folder = args.folder

    if not folder.exists() or not folder.is_dir():
        print(f"Error: '{folder}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    ext_counter = Counter()
    for entry in folder.iterdir():
        if entry.is_file():
            ext = entry.suffix.lower().lstrip('.')
            ext_counter[ext] += 1

    # Sort by count descending, then extension ascending
    sorted_items = sorted(ext_counter.items(), key=lambda x: (-x[1], x[0]))

    # Determine column widths
    ext_header = "Extension"
    count_header = "Count"
    ext_width = max(len(ext_header), *(len(ext) if ext else len("(none)") for ext, _ in sorted_items))
    count_width = max(len(count_header), *(len(str(cnt)) for _, cnt in sorted_items))

    # Print header
    print(f"{ext_header.ljust(ext_width)}  {count_header.rjust(count_width)}")
    print(f"{'-'*ext_width}  {'-'*count_width}")

    # Print rows
    for ext, cnt in sorted_items:
        ext_display = ext if ext else "(none)"
        print(f"{ext_display.ljust(ext_width)}  {str(cnt).rjust(count_width)}")

if __name__ == "__main__":
    main()
