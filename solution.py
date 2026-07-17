"""InterSystems Employee Programming Challenge #1 — Gaia flux variability.

Reads the 20 Gaia DR3 epoch photometry files from data/in/.
"""

from pathlib import Path


# Feedback: The 20 files were already provided in the template's data/in
# directory, which made getting started very smooth.
DATA_DIR: Path = Path("data/in")


def main():
    files = sorted(DATA_DIR.glob("EpochPhotometry_*.csv.gz"))
    print(f"Found {len(files)} data files")
    for path in files:
        print(f"  {path.name}")


if __name__ == "__main__":
    main()