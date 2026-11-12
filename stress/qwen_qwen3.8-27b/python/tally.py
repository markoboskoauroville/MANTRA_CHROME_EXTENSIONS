import argparse
import sys
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Count files by extension in a directory.")
    parser.add_argument("folder", help="Path to the directory to scan")
    args = parser.parse_args()

    folder_path = Path(args.folder)
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: The specified folder does not exist or is not a directory: {folder_path}")
        sys.exit(1)

    counts = Counter()
    try:
        for p in folder_path.iterdir():
            if p.is_file():
                ext = p.suffix.lower()
                if ext:
                    counts[ext] += 1
    except PermissionError as e:
        print(f"Error: Permission denied while scanning folder: {e}")
        sys.exit(1)

    if not counts:
        print("No files with extensions found in the specified folder.")
        sys.exit(0)

    # Sort by count descending, then by extension name ascending
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    print(f"\nFile Extension Tally: {folder_path}")
    print("-" * 30)
    print(f"{'Extension':<15} Count")
    print("-" * 30)
    for ext, num in sorted_counts:
        print(f"{ext:<15} {num}")
    print("-" * 30)
    print(f"{'Total':<15} {sum(counts.values())}")


if __name__ == "__main__":
    main()
