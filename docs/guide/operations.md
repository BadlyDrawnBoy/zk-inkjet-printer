# Operations Runbook

> Consolidated procedures for reproducing results, verifying artifacts, and safely interacting with the printer firmware.

## Prerequisites

- Python 3.10+, virtual environment recommended.
- Install tooling: `pip install -r requirements-dev.txt`.
- Optional: attach a running Ghidra MCP/bridge session when you need interactive disassembly support.
- Download the SD card release asset if you need raw binaries beyond what is tracked in `data/raw/`.

## Quick Commands

| Task | Command | Notes |
| --- | --- | --- |
| Run smoke tests | `make test` | Uses vendored pytest configuration. |
| Decode UI graphics (legacy) | `python3 scripts/legacy/uiqvga/uiqvga_smart_decode.py --input data/raw/ZK-INKJET-UI-QVGA.bin --output data/processed/UI_QVGA_480x480.png` | Produces 480×480 PNG with residual artifacts (brute-force). |
| Explore decode parameters (legacy) | `python3 scripts/legacy/uiqvga/uiqvga_autotune.py --input data/raw/ZK-INKJET-UI-QVGA.bin --log data/processed/autotune.csv` | Logs seam scores; still brute-force. |
| Note on UI decode | — | Remaining artifacts likely require extracting the decode routine via Ghidra bridge. |
| Run verification summary script | `python tools/generate_verification_summary.py` | Updates documentation tables. |

## Verification Checklist

1. Confirm decoded assets (PNG, CSV) have deterministic filenames under `data/processed/`.
2. Cross-reference findings with the auto-generated table in [`docs/VERIFICATION_STATUS.md`](../VERIFICATION_STATUS.md).
3. Document any new evidence or command invocations in [`docs/analysis_traceability.md`](../analysis_traceability.md).
4. Update relevant finding front matter and regenerate summary tables.
5. When flashing firmware, capture the UART log and attach hashes for binaries involved.

## Cookbook: UI Decode → Firmware Flash

This workflow chains the common tasks required to inspect graphics, validate findings, and deploy a modified firmware image.

### 1. Prepare Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Decode the UI Blob (legacy brute-force)

```bash
python3 scripts/legacy/uiqvga/uiqvga_smart_decode.py \
  --input data/raw/ZK-INKJET-UI-QVGA.bin \
  --output data/processed/UI_QVGA_480x480.png
```

- Output still shows minor artifacts; a firmware-derived decoder is pending.
- Record the command in your session log and link it from `docs/analysis_traceability.md`.

### 3. Optional Parameter Sweep (legacy)

```bash
python3 scripts/legacy/uiqvga/uiqvga_autotune.py \
  --input data/raw/ZK-INKJET-UI-QVGA.bin \
  --log data/processed/autotune.csv
```

- Useful for comparing brute-force candidates; not a final decode.

### 4. Stage Firmware Changes (when available)

- Store any patched binaries/resources under `data/processed/` with deterministic names.
- Capture SHA-256 hashes alongside the files you intend to deploy.
- Patch tooling for `.zkml`/APP is not bundled here; when you use external tools, document the exact commands in `docs/analysis_traceability.md`.

### 5. Deploy & Verify (USB “MINI” mass storage)

1. Connect the printer via USB; it exposes a mass-storage device labelled “MINI”.
2. Copy the patched file(s) (e.g., APP.bin or `ZK-INKJET-RES-HW.zkml`) onto that volume.
3. Use the printer’s on-device Update menu to apply the files.
4. Record console/UART output during the update and first boot.
5. Compare behavior against expectations documented in [`docs/findings/mmio_map.md`](../findings/mmio_map.md) and update your session log plus verification tables if confidence changes.

## Incident Response

If a run deviates from expectations (e.g., firmware fails to boot):

1. Revert to a known-good SD card image.
2. Document the failure mode in `docs/sessions/` and link to relevant findings.
3. Flag the affected finding by updating its `status` in the front matter (e.g., downgrade to `needs_review`).
4. Regenerate the verification tables to surface the change prominently.

## Related References

- [`docs/CONVENTIONS.md`](../CONVENTIONS.md) for naming and address formatting.
- [`docs/vendor_resources.md`](../vendor_resources.md) for official manuals.
- [`docs/update_file_rules.md`](../update_file_rules.md) before distributing modified firmware.
