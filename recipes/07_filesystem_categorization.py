"""
Recipe 07: Multi-Dimensional Counting (CategoryCounter)

This recipe demonstrates how to use `CategoryCounter` to aggregate
data into multiple distinct categories simultaneously with a single pass.

We will traverse a filesystem directory and count files by extension,
by size category (Small, Medium, Large), and by their hidden status.
Instead of maintaining three separate `collections.Counter` objects,
we use one `CategoryCounter`.
"""

import os
from pathlib import Path

from mappingtools.collectors import CategoryCounter


def get_size_bucket(size_bytes: int) -> str:
    """Categorize file size into buckets."""
    if size_bytes < 1024 * 10:       # < 10 KB
        return "Small (<10KB)"
    elif size_bytes < 1024 * 1024:   # < 1 MB
        return "Medium (<1MB)"
    else:
        return "Large (>1MB)"

def main():
    # 1. Initialize the CategoryCounter
    # It will automatically create and manage sub-counters for any category we give it.
    file_stats = CategoryCounter()
    total_files = 0

    # 2. Traverse a directory (let's use the parent directory of this script as an example)
    # Note: We use `Path(__file__).parents[2]` to point to the root of `mappingtools`
    target_dir = Path(__file__).parents[2]

    print(f"Scanning directory: {target_dir}")

    for root, dirs, files in os.walk(target_dir):
        # Skip standard hidden/cache directories for cleaner output
        if '.git' in root or '__pycache__' in root or '.pytest_cache' in root:
            continue

        for file_name in files:
            file_path = Path(root) / file_name

            # Extract metadata
            ext = file_path.suffix.lower() or "no_extension"
            is_hidden = "Yes" if file_name.startswith('.') else "No"

            try:
                size = file_path.stat().st_size
                size_bucket = get_size_bucket(size)
            except FileNotFoundError:
                continue # Skip broken symlinks

            total_files += 1

            # 3. Update the CategoryCounter
            # We provide the item we are counting (the file itself, or just `{"file": 1}`)
            # And then provide keyword arguments for the categories we want to track.
            file_stats.add(
                "file",
                extension=ext,
                size_bucket=size_bucket,
                hidden=is_hidden
            )

    # 4. Display the aggregated results
    print(f"\n--- Total Files Scanned: {total_files} ---")

    # Because file_stats acts as a dictionary of MappingCollectors,
    # we access the underlying `mapping` dict, and then the specific bucket's Counter.

    print("\n--- By Extension (Top 5) ---")
    # For a CategoryCounter, accessing the category key gives you a MappingCollector.
    # It holds a mapping of `category_value -> Counter(items)`.
    # Since we always added the string "file", we want the sum of counts for each category value.

    # Wait, `CategoryCounter` maps `CategoryName -> MappingCollector(category_value -> Counter(items))`.
    # So `file_stats['extension'].mapping` looks like `{"_py": Counter({"file": 100}), ".md": Counter({"file": 10})}`.
    # To find the most common extensions, we just need to get the count of "file" in each bucket.

    # Let's cleanly extract just the totals for each bucket:
    def get_bucket_counts(category_name):
        mapping_collector = file_stats[category_name]
        # Return a list of (bucket_name, count) sorted by count descending
        counts = [(bucket, counter["file"]) for bucket, counter in mapping_collector.mapping.items()]
        return sorted(counts, key=lambda x: x[1], reverse=True)

    for ext, count in get_bucket_counts('extension')[:5]:
        print(f"{ext:<15} : {count}")

    print("\n--- By Size Category ---")
    for size, count in get_bucket_counts('size_bucket'):
        print(f"{size:<15} : {count}")

    print("\n--- Hidden Files ---")
    for hidden, count in get_bucket_counts('hidden'):
        print(f"{hidden:<15} : {count}")


if __name__ == "__main__":
    main()
