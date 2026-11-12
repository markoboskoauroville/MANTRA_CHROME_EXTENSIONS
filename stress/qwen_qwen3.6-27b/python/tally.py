#!/usr/bin/env python3
"""Count files by extension in a given folder."""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Count files by extension in a folder.")
    parser.add_argument("folder", help="Path to the folder to tally")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: folder does not exist: {folder}", file=sys.stderr)
        sys.exit(1)
    if not folder.is_dir():
        print(f"Error: not a directory: {folder}", file=sys.stderr)
        sys.exit(1)

    counts = {}
    for p in folder.iterdir():
        if p.is_file():
            ext = p.suffix.lower() or "(no extension)"
            counts[ext] = counts.get(ext, 0) + 1

    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    if not sorted_items:
        print("No files found.")
        return

    ext_width = max(len("EXTENSION"), max(len(ext) for ext, _ in sorted_items))
    cnt_width = 5  # width of "COUNT"

    print(f"{'EXTENSION':<{ext_width}}  {'COUNT':>{cnt_width}}")
    print(f"{'-' * ext_width}  {'-' * cnt_width}")
    for ext, cnt in sorted_items:
        print(f"{ext:<{ext_width}}  {cnt:>{cnt_width}}")


if __name__ == "__main__":
    main()
