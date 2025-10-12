# ZK-INKJET Firmware Reverse Engineering

> Photo gallery: see **docs/hardware/zk-dp20/photos/index.md**  
> Example image: ![DP20 front](docs/hardware/zk-dp20/photos/processed/dp20_printer_front_display.jpg)

## License
- Code: MIT (see `LICENSE`)
- Images/Docs: CC BY 4.0 (see `docs/IMAGE_LICENSE.md`)

This repository contains resources and tooling for analyzing the firmware of the **ZK-INKJET** (Chiky Tech / “ZK1696”-class) handheld inkjet printers. Goals: document proprietary file formats, decode UI graphics, and build a foundation for scripted / remote printing experiments (e.g., via UART).

These printers typically sell for ~€50–60 under various brands (e.g., **Luqeeg**). They use **HP45(SI)** cartridges.

---

## Directory structure

* **data/raw/** – raw binaries from the device / SD card  
  - `ZK-INKJET-NANO-APP.bin`, `ZK-INKJET-NANO-BOOT.bin` (main app + bootloader)  
  - `ZK-INKJET-UI-QVGA.bin` (UI graphics blob)  
  - `ZK-INKJET-RES-HW.zkml` (hardware resource container)  
  - `fat16.img` (FAT partition image)  
  - `sdcard.work.img` (full SD image, **not tracked in git**)  
  - Checksums for repo-tracked files: `CHECKSUMS.repo.txt`  
  - Checksums for SD-image release: `CHECKSUMS.sd.txt`

* **data/processed/** – analysis outputs (e.g., reconstructed 480×480 UI image `UI_QVGA_480x480.png`, parsed resources, callgraph JSONs).

* **docs/** – documentation & notes (analysis methods, offset catalogs, update rules, etc.).

* **docs/hardware/zk-dp20/photos/** – **project photos**  
  - `processed/` (max 2560 px JPEGs)  
  - `thumbs/` (512 px thumbnails)  
  - `index.md` (lightweight gallery)

* **scripts/** – Python tools for carving resources, decoding UI blobs, string scans, callgraph helpers, etc.  
  > Vendor SDKs (e.g., DWIN) are **not** redistributed. See `docs/vendor_resources.md` for links.

---

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
make test   # quick smoke test
# optional:
# export GHIDRA_HOME=/path/to/ghidra
# make gh
````

### Downloads & verification

* Compressed SD image is published under **Releases** (e.g., `v0.1.0-alpha1`).

```bash
sha256sum -c data/raw/CHECKSUMS.sd.txt      # expects sdcard.work.img.xz: OK
sha256sum -c data/raw/CHECKSUMS.repo.txt    # verifies repo-tracked artifacts
```

> The raw `sdcard.work.img` (and its `.xz`) are **ignored** by git to keep the repo lean. Use the Release asset instead.

---

## Usage (UI decode example)

```bash
pip install numpy pillow

# Decode UI QVGA blob → 480×480 PNG
python3 scripts/uiqvga_smart_decode.py \
  --input  data/raw/ZK-INKJET-UI-QVGA.bin \
  --output data/processed/UI_QVGA_480x480.png

# Optional: parameter search to minimize seams/text drift
python3 scripts/uiqvga_hypersearch.py --input data/raw/ZK-INKJET-UI-QVGA.bin
```

More helpers: `uiqvga_autotune.py`, `uiqvga_decode_sweep.py`, resource carvers, string scanners, callgraph generators.

---

## Tests & export

```bash
source .venv/bin/activate
make test
make lint-docaddrs
make export   # builds export/zk-inkjet-export-<UTCSTAMP>.tgz
```

If `GHIDRA_HOME` is set, `make gh` regenerates `data/processed/io_callgraph.json`. Without Ghidra, the target is skipped.

---

## Legal / vendors

* Trademarks belong to their respective owners.
* Files here are for research & interoperability. No vendor SDKs are redistributed; see `docs/vendor_resources.md`.

---

## Disclaimer

This is a **personal research** repository using **AI-assisted analysis**. Findings may be **wrong or incomplete**. Use at your own risk; corrections and PRs are welcome.

**SoC note:** My unit’s main chip is marked **M5 (DWIN)**. I reference **T5L** family docs where behavior matches observations, but any M5↔T5L equivalence is **unconfirmed**.
