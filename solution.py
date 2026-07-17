"""InterSystems Employee Programming Challenge #1 — Gaia flux variability.

Reads the 20 Gaia DR3 epoch photometry files from data/in/ and writes
output.csv listing every source whose BP or RP flux varied by more than
100% across all valid observations.
"""

import csv
import gzip
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


# Feedback: The 20 files were already provided in the template's data/in
# directory, which made getting started very smooth.
DATA_DIR: Path = Path("data/in")
OUTPUT_CSV: Path = Path("output.csv")

# Column positions in the Gaia epoch photometry ECSV files.
COL_SOURCE_ID: int = 1
COL_BP_FLUX: int = 11
COL_RP_FLUX: int = 16

# Minimum percentage change for a source to be included in the output.
THRESHOLD: float = 100.0

# Output column names required by the challenge specification.
OUTPUT_HEADER: list[str] = [
    "source_id",
    "bp_min_flux",
    "bp_max_flux",
    "rp_min_flux",
    "rp_max_flux",
    "percentage_change",
]


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
    """Return a list of qualifying-source rows from a Gaia ECSV file.

    Each returned row is a tuple ordered per OUTPUT_HEADER.
    """
    results = []

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
                results.append((
                    row[COL_SOURCE_ID],
                    bp_min,
                    bp_max,
                    rp_min,
                    rp_max,
                    best_pct,
                ))

    return results


def write_output(rows, path: Path):
    """Write rows to a CSV file with the challenge-required header."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(OUTPUT_HEADER)
        writer.writerows(rows)


def main():
    files = sorted(DATA_DIR.glob("EpochPhotometry_*.csv.gz"))
    print(f"Found {len(files)} data files")

    all_results = []
    # Feedback: Parallelising per-file was the biggest speed win.
    with ProcessPoolExecutor() as pool:
        for file_results in pool.map(process_file, files):
            all_results.extend(file_results)

    write_output(all_results, OUTPUT_CSV)

    print(f"Sources with >100% variability: {len(all_results)}")
    print(f"Output written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()