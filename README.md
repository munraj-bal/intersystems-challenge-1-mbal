# Gaia Flux Variability — InterSystems Employee Programming Challenge #1

A Python solution that analyses [Gaia DR3](https://www.cosmosb/gaia/dr3 epoch photometry data to identify highly variable astronomical sources — those whose brightness fluctuated by more than 100% across all valid observations.

Submitted for the https://openexchange.intersystems.com/contest/47.

## What It Does

The program processes 20 Gaia DR3 epoch photometry files and produces a CSV listing every source whose BP or RP band flux varied by more than 100% between its minimum and maximum valid observations.

For each source in the input:

1. Extracts the `bp_flux` and `rp_flux` arrays (per-observation brightness measurements in Gaia's blue and red photometer bands).
2. Filters out invalid values — missing, null, `NaN`, and non-positive fluxes.
3. Computes the percentage change for each band:  `((max − min) / min) × 100`.
4. Takes the larger of the two percentages as the source's variability score.
5. Emits the source to `output.csv` if the score exceeds 100%.

## Prerequisites

- https://git-scm.com/downloads
- [Docker Desktop](https://www.ts/docker-desktop/

## Installation

Clone the repository:

```bash
git clone https://github.com/munraj-bal/intersystems-challenge-1-mbal.git
cd intersystems-challenge-1-mbal