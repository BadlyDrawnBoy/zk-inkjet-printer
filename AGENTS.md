# Repository Guidelines

## Project Structure & Module Organization
Source material lives in `data/raw/` (printer binaries, SD-card images) and decoded artifacts go to `data/processed/`. The automation entry points are the Python scripts under `scripts/`; each focuses on a specific phase of UI reconstruction or resource extraction. Reference documentation is consolidated in `docs/archive/documentation-20251009.md`, while `DWIN/` holds vendor manuals useful for understanding the T5L display controller. Keep large intermediate outputs out of version control or store them under `data/processed/` with descriptive names.

## Build, Test, and Development Commands
Install runtime dependencies with `python3 -m pip install numpy pillow`. Scripts assume execution from the repository root. Typical workflows include:
```
python3 scripts/uiqvga_smart_decode.py --input data/raw/ZK-INKJET-UI-QVGA.bin --output data/processed/UI_QVGA_480x480.png
python3 scripts/uiqvga_autotune.py --input data/raw/ZK-INKJET-UI-QVGA.bin --log data/processed/autotune.csv
bash scripts/re_extract.sh
```
Use the smart decode script for high-quality renders, the autotuner to explore parameter sweeps, and the shell helper to carve FAT filesystem contents.

## Coding Style & Naming Conventions
Python scripts target Python 3.10+ and follow PEP 8 defaults: 4-space indentation, snake_case functions, and uppercase module constants. Prefer small, pure functions that accept file-like objects to ease reuse. Shell helpers should start with `#!/bin/bash` and `set -euo pipefail`, keep environment variables uppercase (`IMG`, `SECTOR_OFFSET`), and echo key steps so logs stay readable. Commit any generated assets using deterministic filenames (`UI_QVGA_480x480.png`, `autotune.csv`) under `data/processed/`.

## Testing Guidelines
Use the vendored pytest shim to exercise unit-style coverage: `python3 -m pytest -q`. Before publishing changes, re-run the primary decode pipeline and confirm expected outputs in `data/processed/` (e.g., visually diff regenerated PNGs and ensure logs show minimal seam scores). When touching extraction logic, spot-check slices with `hexdump` or `binwalk`, and document new offsets or parameters in `docs/archive/documentation-20251009.md` (or its future replacement).

## Analysis Traceability
Every investigation or reverse-engineering pass must be recorded with reproducible commands. Append new procedures or links to `docs/analysis_traceability.md` (or a dedicated methodology file) whenever you derive findings. Treat the documented commands as the source of truth; avoid conclusions that are not backed by verifiable evidence. Review `docs/boot_analysis_methodology.md` for the expected level of detail.

## Commit & Pull Request Guidelines
Existing history uses concise, capitalized subjects (`Enable Git LFS for large binaries`). Follow that format, optionally adding a short qualifier (`Verb: detail`). Pull requests should include: overview of the change, affected binaries or generated artifacts, reproduction commands, and any new documentation sections. Attach small preview images or checksums when outputs change so reviewers can verify updates without re-running full pipelines.

## Security & Data Handling
Treat raw binaries as untrusted: avoid executing them directly and work inside disposable virtual environments. Large disk images should remain in `.gitignore`; if temporary mounts are required, document mount points and unmount steps in your PR description.
