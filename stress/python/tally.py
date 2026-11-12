#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from collections import Counter


def main():
    parser = argparse.ArgumentParser(
        description="Count files by extension in a folder."
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Path to the folder to analyze."
    )
    args = parser.parse_args()

    path = Path(args.folder)

    if not path.exists():
        print(f"Error: Folder does not exist: {args.folder}")
        sys.exit(1)
    
    if not path.is_dir():
        print(f"Error: Path is not a directory: {args.folder}")
        sys.exit(1)

    extensions = []
    for file in path.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            if ext:
                extensions.append(ext)
            else:
                extensions.append("(none)")

    counts = Counter(extensions)
    
    if not counts:
        print("No files with extensions found.")
        return

    formatted_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    
    max_ext_len = max(len(ext) for ext, _ in formatted_counts) if formatted_counts else 0
    max_count_len = len(str(max(counts.values()))) if counts else 0
    
    header_ext = "Extension"
    header_count = "Count"
    
    print(f"{header_ext.ljust(max_ext_len)} {header_count.rjust(max_count_len)}")
    print("-" * (max_ext_len + max_count_len + 2))
    
    for ext, count in formatted_counts:
        print(f"{ext.ljust(max_ext_len)} {str(count).rjust(max_count_len)}")


if __name__ == "__main__":
    main()
