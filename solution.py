"""InterSystems Employee Programming Challenge #1 — Gaia flux variability.

Reads the 20 Gaia DR3 epoch photometry files from data/in/ and computes
per-source BP/RP flux percentage change, counting sources whose flux
varied by more than 100%.
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


# Minimum percentage change for a source to be included in the output.
THRESHOLD: float = 100.0


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

        # Skip NaN if float() produced one, and skip non-positive fluxes
        # (the percentage-change formula divides by the minimum, so zero
        # or negative would be invalid).
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


def percentage_change(min_flux, max_flux):
    """Return ((max - min) / min) * 100, or 0.0 if inputs are invalid.

    Returning 0.0 for invalid inputs lets callers compare against the
    threshold without extra None-checks.
    """
    if min_flux is None or max_flux is None or min_flux <= 0.0:
        return 0.0
    return (max_flux - min_flux) / min_flux * 100.0


def skip_metadata_lines(handle):
    """Yield lines from the file that are not ECSV metadata."""
    for line in handle:
        if not line.startswith("#"):
            yield line


def process_file(path: Path):
    """Return the count of sources whose BP or RP flux varied by more than 100%."""
    qualifying_sources = 0

    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        # Feed only the non-metadata lines into the CSV parser.
        data_lines = skip_metadata_lines(handle)
        reader = csv.reader(data_lines)

        # Skip the column-names header row.
        next(reader)

        for row in reader:
            bp_min, bp_max = scan_flux_array(row[COL_BP_FLUX])
            rp_min, rp_max = scan_flux_array(row[COL_RP_FLUX])

            # Take the larger of the two bands' percentage changes.
            bp_pct = percentage_change(bp_min, bp_max)
            rp_pct = percentage_change(rp_min, rp_max)
            best_pct = max(bp_pct, rp_pct)

            if best_pct > THRESHOLD:
                qualifying_sources += 1

    return qualifying_sources


def main():
    files = sorted(DATA_DIR.glob("EpochPhotometry_*.csv.gz"))
    print(f"Found {len(files)} data files")

    total = 0
    for path in files:
        qualifying = process_file(path)
        print(f"  {path.name}: {qualifying} sources with >100% variability")
        total += qualifying

    print(f"Sources with >100% variability: {total}")


if __name__ == "__main__":
    main()