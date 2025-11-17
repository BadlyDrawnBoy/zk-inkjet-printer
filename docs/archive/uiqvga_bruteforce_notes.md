# UI-QVGA Brute-Force Decoding Notes (Archived)

> Status: partial success only. Brute-force scripts generate a usable 480×480 image with residual artifacts (misaligned text/seams). The remaining fixes require firmware-level understanding (tile offsets/phase) via Ghidra/MCP. Keep this file for historical context; do not treat the heuristics as the final decode path.

## What the scripts do
- **`scripts/uiqvga_smart_decode.py`** – grid search over XOR modes (0xAAAA variants), tile order, byte-swap, BGR toggle, odd-line shifts; scores seam/comb artifacts.
- **`scripts/uiqvga_hypersearch.py`** / **`scripts/uiqvga_decode_sweep.py`** – higher-dimensional sweeps of drift/offset parameters; export candidate parameter logs.
- **`scripts/detile_ui_qvga.py`** / **`scripts/render_ui_qvga.py`** – helpers to assemble tiles or render intermediate candidates.
- **Artifacts generated**: best-effort PNGs under `data/processed/` (e.g., `UI_QVGA_480x480.png`) but with visible drift on text and seams.

## Why this is archived
- The brute-force approach stalls short of perfect alignment; remaining drift likely depends on decode rules embedded in `ZK-INKJET-NANO-APP.bin`/`BOOT.bin`.
- Evidence suggests a firmware-driven tile/line phase adjustment that brute-force heuristics haven’t captured.
- Next phase should extract the exact copy/decode routine via Ghidra (e.g., locate the UI blob reader and lift its offset/stride math).

## Suggested next steps (for future work)
1. Use the Ghidra bridge to find UI blob load routines in APP.bin (search for constants around `0xAAAA`, tile sizes 160/480, or writes into framebuffers).
2. Mirror those offsets into the Python pipeline instead of expanding the brute-force parameter space.
3. Once confirmed, deprecate the brute-force scripts or annotate them with the derived constants.

If you refine the decode based on firmware analysis, capture the commands in `docs/analysis_traceability.md` and update the canonical decode script (or add a new one) in `scripts/` (leaving these legacy helpers under `scripts/legacy/uiqvga/`).
