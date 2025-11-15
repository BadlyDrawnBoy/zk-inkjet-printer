# ZK-INKJET Firmware Analysis – Status (as of 2025-10-09)

> [⤴ Back to archive overview](README.md)

## Context and Goal

This document captures the historic investigation work on the ZK-INKJET handheld printer. The primary goal was to understand how the firmware boots, how resources are packaged, and how UI graphics can be reconstructed. For the current roadmap and reproducible command sets, refer to the quick navigation below.

## Quick Navigation (Firmware Control First)

- Legacy roadmap and open items: `docs/archive/firmware_mod_plan_legacy.md`
- Reproducible procedures for every finding: `docs/analysis_traceability.md`
- Offset catalogue for follow-up work: `docs/offset_catalog.md`
- Bootloader methodology (command-level evidence): `docs/boot_analysis_methodology.md`

The remainder of this document preserves prior research as background information. Treat it as an archive rather than the canonical source for next steps.

## Data Structure and Boot Path

- **SD card as boot medium**: The firmware resides on a removable SD card without a classic partition table. A stage-1 loader (signature “ZBWp1WBZ”) is located at the beginning, followed by a larger stage-2 loader. The device does not boot without the SD card.
- **Truncated ext4 rootfs**: The SD image contains remnants of a 7.4 GB ext4 filesystem, although the physical card is 3.75 GB. Recovery attempts failed; carved fragments include ELF libraries and Android APKs. This legacy rootfs appears unrelated to the current firmware.
- **ZK-INKJET-NANO-BOOT.bin (~12.7 KB)**: Low entropy (~5.8 bit/byte), almost exclusively ARM instructions with hardly any ASCII strings. Likely the stage-2 bootloader that copies the APP module and GUI resources into RAM. Offset hints suggest it loads `APP.bin` and the GUI blobs into memory.

## Application Module (ZK-INKJET-NANO-APP.bin)

- **Structure**: Approximately 2.6 MB, a mix of binary payloads and human-readable strings. No standard container signatures (SquashFS, ZIP, ELF) were detected; instead, numerous file paths and resource names (e.g., `0:/simhei.ttf`, `3:/inkjet-ui-%04d%02d%02d %02d%02d%02d.bmp`) appear. Conclusion: `APP.bin` is a proprietary resource container loaded into RAM by the bootloader.
- **Carving results**: Signature scanning recovered partial resources — OpenType/TrueType fonts (Montserrat, OpenSans, etc.) and BMP images. Some BMPs were extracted successfully by honouring the `bfSize` header field. JPEG/PNG headers surfaced but were often incomplete.
- **Referenced fonts**: `arial.ttf`, `DroidSansFallback.ttf`, `DZPMYD.ttf`, `FZFSJW.ttf`, `FZKTJW.ttf`, `Montserrat-Regular.otf`, `OpenSans-Regular.ttf`, `simfang.ttf`, `simhei.ttf`, `simkai.ttf`, `times.ttf`, plus both resource containers `ZK-INKJET-RES-HW.zkml` and `ZK-INKJET-GUI-RES.zkml`.
- **Summary**: `APP.bin` is a consolidated resource store (fonts, bitmaps). No embedded filesystem; bespoke parsers are required.

## UI Graphics Module (ZK-INKJET-UI-QVGA.bin)

- Contains background graphics encoded as 16-bit words with additional obfuscation.
- **Tile layout**: Nine tiles of 160×160, arranged as a 3×3 matrix → final frame 480×480.
- **Colour space and XOR**: Pixels are stored in BGR565 and XORed with `0xAAAA`. Removing the XOR and converting to BGR565 yields plausible colours.
- **Line and column shifts**: Remaining artefacts (misaligned text) arise from odd-line shifts, optional drift, and per-column offsets. Parameters `s0`, drift `(k,L)`, and offsets `(d0,d1,d2)` influence seam quality.
- **Hyper-search tooling**: Automated scripts explore parameter combinations and score seams based on even/odd line differences and tile boundaries.

## Resource Containers (ZK-INKJET-RES-HW.zkml, ZK-INKJET-GUI-RES.zkml)

- `ZK-INKJET-RES-HW.zkml`: Contains hardware resources for the display controller. Structure still under investigation; heuristic probes highlight block boundaries with notable ASCII content and alignment.
- `ZK-INKJET-GUI-RES.zkml`: A full Leelawadee UI TrueType font (confirmed via `maxp`, `cmap`, and `name` tables). No custom wrapping beyond the `.zkml` file name.

## Boot Procedure and Update Mechanism (Historic Notes)

- While detailed reverse engineering is captured elsewhere (`data/processed/boot_static_notes.md`), key takeaways include:
  - Stage-2 bootloader sets up mode-specific stacks, disables caches, and relocates function tables.
  - Dedicated copy routines handle aligned and unaligned transfers into RAM.
  - A long division helper mirrors the ARM EABI routine.
  - CP15 configuration enables caches/MPU before handing control to the application module.
  - The bootloader issues a long sequence of display controller commands (consistent with DWIN/T5L documentation) and streams UI data into VRAM.

## Summary and Outlook (Historic Perspective)

Earlier recommendations were to:
1. Continue static analysis of BOOT.bin and APP.bin to identify loader and decoder functions.
2. Enhance the UI reconstruction pipeline with additional permutations (serpentine scans, nibble swaps).
3. Explore RES-HW.zkml for further resource formats.
4. Preserve a detailed log of test parameters for future automation.

These recommendations have since been superseded by later findings; see `docs/findings/` for current priorities. The older roadmap remains available at `docs/archive/firmware_mod_plan_legacy.md` for context.

## Appendix: ZK-INKJET UI/Graphics – Status & Method (2025-10-06)

> Note: Archived tuning report on UI reconstruction. For active tasks, consult the current findings or the legacy roadmap at `docs/archive/firmware_mod_plan_legacy.md`.

### Context

Goal: reconstruct graphics from `ZK-INKJET-UI-QVGA.bin`. Raw data appeared scrambled; the procedure below achieved correct colour output and tile placement but left minor text misalignment.

### Files & Artifacts

- `ZK-INKJET-UI-QVGA.bin` → 480×480 pixels, 16 bpp; nine sequential tiles (160×160 each).
- `ZK-INKJET-GUI-RES.zkml` → TrueType font (Leelawadee UI).
- `ZK-INKJET-NANO-APP.bin` → Resource container; XOR scrambling not generally applicable here.
- `ZK-INKJET-NANO-BOOT.bin` → Boot code; indirectly relevant for graphics decoding.

### Findings

1. Tile structure: 3×3 tiles (160×160) combined into a 480×480 canvas.
2. Colours: BGR565 with XOR `0xAAAA`.
3. Tile order: best results with column-major placement.
4. Line-phase errors: odd rows require horizontal shift (`s0`), optionally drift `(k,L)`.
5. Column offsets per tile column (`d0,d1,d2`) reduce seams.
6. Remaining issues: fonts still show minor misalignment, suggesting additional phase rules.
7. Ineffective strategies: global XOR masks other than `0xAAAA`, byte swap, alternative colour formats.
8. XOR appears specific to graphics; not useful for APP/BOOT binaries.

### Reconstruction Pipeline

1. Load raw data as `uint16`.
2. Extract nine tiles of 160×160.
3. Assemble tiles in column-major order.
4. XOR each 16-bit word with `0xAAAA`.
5. Apply odd-line shift with optional drift (`s0`, `k`, `L`).
6. Apply per-column offsets (`d0,d1,d2`).
7. Convert from BGR565 to RGB8.
8. Evaluate seams visually and via heuristics (tile boundary differences; even/odd artefacts).

### Best Parameters (historic)

- XOR: `0xAAAA`
- Colour: BGR565, no byte swap
- Tile order: column-major
- Odd-line base shift: `s0` ≈ +1…+2 pixels
- Drift: often `k=0`; occasional hits with `k=+1`, `L=32`
- Column offsets: typically `(−2, −1, 0)` with ±1 tuning

Background reconstructions remain actionable but are secondary to UART/update investigations.
