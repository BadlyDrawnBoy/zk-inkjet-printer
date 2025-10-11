# Project Status – ZK-INKJET Firmware Recon

_Last updated: 2025-10-11_

## High-Level Progress
- ✅ **UI decoding pipeline**: `scripts/uiqvga_smart_decode.py` refactored with deterministic CLI defaults; hyper-search (`scripts/uiqvga_hypersearch.py`) now exports `data/processed/uiqvga_params.json` + `UI_QVGA_best.png`.
- ✅ **Resource reconnaissance**: `scripts/scan_strings.py` catalogs `APP.bin` strings; `data/processed/app_strings_report.md` highlights paths, fonts, and update hints with offsets/context.
- ✅ **Bootloader mapping**: `data/processed/boot_static_notes.md` documents stack setup, relocation routines, memory copy helpers, and display init in `ZK-INKJET-NANO-BOOT.bin`.
- ✅ **Font verification**: `data/processed/gui_res_font_report.md` confirms `ZK-INKJET-GUI-RES.zkml` is the full Leelawadee UI TTF (1,023 glyphs, SE-Asian coverage).
- ✅ **RES-HW probing**: `scripts/reshw_probe.py` surfaced structured offsets; `data/processed/reshw_probe_report.md` + `data/processed/samples/` provide entropy-based snippets.
- ✅ **Documentation coherence**: archived the legacy deep-dive (`docs/archive/documentation-20251009.md`), refreshed `docs/analysis_traceability.md`, `docs/offset_catalog.md`, `docs/update_file_rules.md`, and `docs/SESSION_HANDOFF.md` for the queue/flash findings.

## P0 Task Tracker
| Task ID | Title | Status | Notes |
|---------|-------|--------|-------|
| P0-1 | UI-QVGA decoder pipeline | ✅ Done | CLI refactor, unit tests, deliverable PNG in `data/processed/UI_QVGA_480x480.png`. |
| P0-2 | Parameter search stabilisation | ✅ Done | Hyper-search refactored, JSON export with top parameter sets. |
| P0-3 | APP strings scan | ✅ Done | Report at `data/processed/app_strings_report.md`. |
| P0-4 | BOOT code locator | ✅ Done | Findings logged in `data/processed/boot_static_notes.md`. |

## P1 Task Tracker
| Task ID | Title | Status | Notes |
|---------|-------|--------|-------|
| P1-1 | GUI-RES -> TTF analysis | ✅ Done | Report at `data/processed/gui_res_font_report.md`. |
| P1-2 | RES-HW container layout | ✅ Done (first pass) | Heuristic probe outlines candidate TOC/data zones; parser now generates `data/processed/reshw_index.json` for glyph metadata. |

## P2 and Beyond
| Task ID | Title | Status | Notes |
|---------|-------|--------|-------|
| P2-1 | Protocol hypotheses | ⏳ Pending | To use outputs from APP strings + future disassembly; stub not yet created. |

## Next Focus Areas
1. Identify the routine that writes a non-null pointer into `queue_ctrl+0x10` and document it alongside the existing prefill entry (`docs/SESSION_HANDOFF.md`, `docs/offset_catalog.md`).
2. Characterise validator `0x002BFDDC` (behaviour, failure path, side-effects) before the flash writer `0x002BFC34` runs; update canonical docs with the findings.
3. Continue RES-HW structure work (TOC headers, entry descriptors) using `data/processed/samples/`, once queue/flash gating tasks land.

See `docs/NEXT_SESSION_BRIEF.md` for the detailed kickoff checklist covering items 1 and 2.

## Notes & Open Questions
- `.zkml` appears to be a generic vendor extension for resource blobs (font TTF included); classification documented in session notes.
- No UART initialisation observed in BOOT; focus shifts to APP for serial protocol details.
- Testing is handled via the lightweight pytest shim (`python3 -m pytest -q`) until real pytest can be installed.

_Prepared by: osboxes_
