# ZK‑INKJET Firmware Reverse Engineering

This repository contains resources and tooling for analysing the firmware of the **ZK‑INKJET** handheld inkjet printer. It aims to extract and document proprietary  file formats, decode the user interface graphics, and provide a  foundation for further research and automation with coding agents.

## Directory structure

- **data/raw/** – raw binary files extracted from the printer's SD card. These include the application module (`ZK-INKJET-NANO-APP.bin`), boot loader (`ZK-INKJET-NANO-BOOT.bin`), UI graphics (`ZK-INKJET-UI-QVGA.bin`), hardware resource container (`ZK-INKJET-RES-HW.zkml`) and the FAT/SD card images (`fat16.img`, `sdcard.work.img`). The large `.img` files are SD card dumps and may be excluded or stored via Git LFS if  not needed, as the ext4 rootfs they contain is not relevant to the  current firmware.
- **data/processed/** – outputs from the analysis, such as the reconstructed 480×480 UI image and the GUI font container (`ZK-INKJET-GUI-RES.zkml`).
- **docs/** – documentation files. `documentation.md` is a combined report containing the firmware analysis and the  UI/graphics reconstruction method. The original files are preserved for  reference.
- **scripts/** – python scripts used for carving resources, decoding the UI QVGA blob, tuning parameters, and re-extraction. Each script has a short  description.
- **DWIN/** – vendor documentation and demo files for the T5L display controller  (EKT043 kit). These are optional references for understanding the  hardware platform.

## Usage

To decode the user interface graphics:

```
sh# Install dependencies (Python 3, numpy, Pillow)
pip install numpy pillow

# Run the smart decode script on the UI QVGA binary
python3 scripts/uiqvga_smart_decode.py --input data/raw/ZK-INKJET-UI-QVGA.bin --output data/processed/UI_QVGA_480x480.png
```

Additional scripts such as `uiqvga_hypersearch.py` allow brute-force tuning of the odd-line shift, drift and column offsets to minimise seams and text misalignment.

## Coding agents

This repository is structured to be agent-friendly. A coding agent can:

- Load `docs/documentation.md` to understand the firmware structure, boot process, resource containers and the current state of the UI reconstruction.
- Inspect the raw binaries in `data/raw/` to implement custom decoders for proprietary formats.
- Use the provided Python scripts under `scripts/` as a starting point or reference for implementing new algorithms.

Please consult `docs/documentation.md` for a complete overview of the research, findings and next steps.
