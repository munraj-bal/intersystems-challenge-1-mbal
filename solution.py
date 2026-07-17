"""InterSystems Employee Programming Challenge #1 — Gaia flux variability.

Reads the 20 Gaia DR3 epoch photometry files from data/in/ and parses
BP/RP flux arrays into per-source min/max values.
"""

import csv
import gzip
from pathlib import Path


# Feedback: The 20 files were already provided in the template's data/in
# directory, which made getting started very smooth.
DATA_DIR: Path = Path("data/in")

# Column positions in the Gaia epoch photometry ECSV files.
COL_SOURCE_ID: int = 1
COL_BP_FLUX: int = 11
COL_RP_FLUX: int = 16


def scan_flux_array(cell: str):
    """Return (min, max) of valid positive fluxes from a bracketed array cell.

    Gaia stores each band's per-transit flux measurements as a bracketed
    comma-separated array, for example ``[1.5,NaN,2.7]``. Values that are
    missing, NaN, non-numeric, or non-positive are skipped so they cannot
    corrupt the min/max calculation.
    """
    # Return early if the cell is not a valid bracketed array.
    start_bracket = cell.find("[")
    end_bracket = cell.rfind("]")
    if start_bracket < 0 or end_bracket <= start_bracket + 1:
        return None, None

    inner_text = cell[start_bracket + 1:end_bracket]

    # Track the running min and max across the array.
    minimum = float("inf")
    maximum = -float("inf")

    for piece in inner_text.split(","):
        stripped = piece.strip()
        if stripped == "":
            continue

        # Skip NaN, null, or None entries. These start with 'N' or 'n',
        # so they can be rejected cheaply before calling float().
        first_char = stripped[0]
        if first_char == "N" or first_char == "n":
            continue

        try:
            value = float(stripped)
        except ValueError:
            continue

        # Skip NaN if float() produced one, and skip
        # non-positive fluxes (the percentage-change formula divides by
        # the minimum, so zero or negative would be invalid).
        is_nan = value != value
        if is_nan or value <= 0.0:
            continue

        if value < minimum:
            minimum = value
        if value > maximum:
            maximum = value

    # If nothing valid was found, minimum will still be infinity.
    if minimum == float("inf"):
        return None, None
    return minimum, maximum


def skip_metadata_lines(handle):
    """Yield lines from the file that are not ECSV metadata."""
    for line in handle:
        if not line.startswith("#"):
            yield line


def process_file(path: Path):
    """Return the number of data rows in a Gaia ECSV file."""
    row_count = 0

    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        # Feed only the non-metadata lines into the CSV parser.
        data_lines = skip_metadata_lines(handle)
        reader = csv.reader(data_lines)

        # Skip the column-names header row.
        next(reader)

        # Grab the first data row separately to print a sample of it.
        first_row = next(reader, None)
        if first_row is not None:
            source_id = first_row[COL_SOURCE_ID]
            bp_min, bp_max = scan_flux_array(first_row[COL_BP_FLUX])
            rp_min, rp_max = scan_flux_array(first_row[COL_RP_FLUX])
            print(f"    first source {source_id}, "
                f"bp=[{bp_min}, {bp_max}], rp=[{rp_min}, {rp_max}]")
            row_count = 1

        # Count the remaining data rows.
        for _ in reader:
            row_count += 1

    return row_count


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