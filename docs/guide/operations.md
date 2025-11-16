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
| Decode UI graphics | `python3 scripts/uiqvga_smart_decode.py --input data/raw/ZK-INKJET-UI-QVGA.bin --output data/processed/UI_QVGA_480x480.png` | Produces 480×480 PNG. |
| Explore decode parameters | `python3 scripts/uiqvga_autotune.py --input data/raw/ZK-INKJET-UI-QVGA.bin --log data/processed/autotune.csv` | Logs seam scores for later inspection. |
| Note on UI decode | — | Current scripts are brute-force and leave minor artifacts; precise offsets likely need firmware RE via Ghidra bridge. |
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

### 2. Decode the UI Blob

```bash
python3 scripts/uiqvga_smart_decode.py \
  --input data/raw/ZK-INKJET-UI-QVGA.bin \
  --output data/processed/UI_QVGA_480x480.png
```

- Inspect the resulting PNG for seam artifacts.
- Record the command in your session log.

### 3. Validate Parameters

```bash
python3 scripts/uiqvga_autotune.py \
  --input data/raw/ZK-INKJET-UI-QVGA.bin \
  --log data/processed/autotune.csv
```

- Review `autotune.csv` for parameter combinations with low error metrics.
- Update the front matter of [`docs/findings/firmware_functions.md`](../findings/firmware_functions.md) if new evidence improves confidence in display handlers.

### 4. Stage Firmware Changes

```bash
# Example: patch resource container (placeholder)
python3 scripts/zkml_replace_asset.py --input data/raw/ZK-INKJET-RES-HW.zkml --output data/processed/ZK-INKJET-RES-HW.patched.zkml --asset splash.png --replacement custom.png
```

- Ensure patched assets live in `data/processed/` with descriptive names.
- Capture hashes for any modified binaries.

### 5. Flash & Verify

```bash
# Copy patched files to SD card (example mount point)
sudo mount /dev/sdX1 /mnt/zk
sudo cp data/processed/ZK-INKJET-RES-HW.patched.zkml /mnt/zk/ZK-INKJET-RES-HW.zkml
sync
sudo umount /mnt/zk
```

- Record UART output during first boot after flashing.
- Compare behavior against expectations documented in [`docs/analysis/gpio_pins_analysis.md`](../analysis/gpio_pins_analysis.md) and [`docs/findings/mmio_map.md`](../findings/mmio_map.md).
- Update your session log with observed results and rerun the verification summary script if confidence levels changed.

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
