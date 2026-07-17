"""InterSystems Employee Programming Challenge #1 — Gaia flux variability.

Reads the 20 Gaia DR3 epoch photometry files from data/in/.
"""

import csv
import gzip
from pathlib import Path


# Feedback: The 20 files were already provided in the template's data/in
# directory, which made getting started very smooth.
DATA_DIR: Path = Path("data/in")


def process_file(path: Path) -> int:
    """Return the number of data rows in a Gaia ECSV file."""
    row_count = 0

    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        # ECSV files begin with metadata lines starting with '#'. Skip them.
        non_metadata_lines = []
        for line in handle:
            if not line.startswith("#"):
                non_metadata_lines.append(line)

        reader = csv.reader(non_metadata_lines)

        # Skip the column-names header row.
        next(reader)

        # Count the actual data rows.
        row_count = sum(1 for _ in reader)

    return row_count


def skip_metadata_lines(handle):
    """Yield lines from the file that are not ECSV metadata."""
    for line in handle:
        if not line.startswith("#"):
            yield line


def main():
    files = sorted(DATA_DIR.glob("EpochPhotometry_*.csv.gz"))
    print(f"Found {len(files)} data files")

    total = 0
    for path in files:
        rows = process_file(path)
        print(f"  {path.name}: {rows} rows")
        total += rows

    print(f"Total sources: {total}")


if __name__ == "__main__":
    main()