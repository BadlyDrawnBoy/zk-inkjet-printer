# ZK‑INKJET Firmware Reverse Engineering

This repository contains resources and tooling for analyzing the firmware of the **ZK‑INKJET** (CHIKY/ZK1696‑class) handheld inkjet printer. The goal is to document proprietary file formats, decode UI graphics, and provide a foundation for scripted/remote printing experiments (e.g., via UART).

> **Project language:** English

---

## Directory structure

* **data/raw/** – raw binaries from the device/SD card:

  * `ZK-INKJET-NANO-APP.bin`, `ZK-INKJET-NANO-BOOT.bin` (main app + bootloader)
  * `ZK-INKJET-UI-QVGA.bin` (UI graphics blob)
  * `ZK-INKJET-RES-HW.zkml` (hardware resource container)
  * `fat16.img` (FAT partition image)
  * `sdcard.work.img` (full SD image, **not tracked in git**)
  * Checksums for repo-tracked files: `CHECKSUMS.repo.txt`
  * Checksums for SD image (release asset): `CHECKSUMS.sd.txt`

* **data/processed/** – analysis outputs (e.g., reconstructed 480×480 UI image `UI_QVGA_480x480.png`, `ZK-INKJET-GUI-RES.zkml`, callgraph JSONs).

* **docs/** – documentation and notes (analysis methods, offset catalogs, update pipeline rules, etc.).

* **scripts/** – Python tools for carving resources, decoding the UI QVGA blob, tuning parameters, scanning strings, generating callgraphs, etc.

> Vendor SDKs (e.g., DWIN) are **not** redistributed here. See `docs/vendor_resources.md` for links.

---

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
make test   # quick smoke test
# optional: set GHIDRA_HOME and try to refresh callgraph outputs
# export GHIDRA_HOME=/path/to/ghidra
# make gh
```

### Downloads & verification

* Compressed SD image is published under **Releases** (e.g., `v0.1.0-alpha1`).
* Verify the release asset locally:

```bash
sha256sum -c data/raw/CHECKSUMS.sd.txt
# expects: data/raw/sdcard.work.img.xz: OK
```

* Verify repo‑tracked artifacts:

```bash
sha256sum -c data/raw/CHECKSUMS.repo.txt
```

> The raw `sdcard.work.img` and its compressed form are **ignored** by git to keep the repo lean. Use the Release download instead.

---

## Usage (UI decode example)

```bash
# Install minimal dependencies
pip install numpy pillow

# Decode UI QVGA blob → 480×480 PNG
python3 scripts/uiqvga_smart_decode.py \
  --input  data/raw/ZK-INKJET-UI-QVGA.bin \
  --output data/processed/UI_QVGA_480x480.png

# Optional: brute-force parameter search to minimize seams/text drift
python3 scripts/uiqvga_hypersearch.py --input data/raw/ZK-INKJET-UI-QVGA.bin
```

Additional helpers: `uiqvga_autotune.py`, `uiqvga_decode_sweep.py`, resource carvers, string scanners, and callgraph generators.

---

## Tests & export

Activate your venv (e.g., `source .venv/bin/activate`), then:

```bash
make test            # wraps pytest -q
make lint-docaddrs   # verify VA/file address references in docs
make export          # builds export/zk-inkjet-export-<UTCSTAMP>.tgz (caches filtered)
```

If `GHIDRA_HOME` is set, `make gh` regenerates `data/processed/io_callgraph.json`. When Ghidra is absent, the target is skipped.

> **Ghidra notes:** Headless analysis is optional; some environments produce 0‑byte projects due to DB/version mismatches. Prefer the GUI project and exporting analysis outputs (JSON/MD) rather than committing `.gpr`.

---

## For coding agents

* Start with `docs/` (analysis methodology, update rules, offset catalogs) and `data/processed/` outputs.
* Use `scripts/` as reference implementations for UI decoding & resource parsing.
* Planned next step: a minimal **UART hook** by repurposing a benign UI handler (see `docs/HACKING_UART.md`).

---

## Legal / vendors

* Trademarks belong to their respective owners.
* Files here are provided for research and interoperability. No vendor SDKs are redistributed; see `docs/vendor_resources.md` for official sources.

---

## Screenshot

![UI QVGA](data/processed/UI_QVGA_best.png)
