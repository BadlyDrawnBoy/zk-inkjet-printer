# Firmware Modification Roadmap

This roadmap tracks the critical paths toward gaining control over the ZK-INKJET firmware (UART access, resource injection, update interception). Each item references supporting analyses and links to executable commands where applicable.

## Current Objective
> Establish reliable control over the device via UART or remote interface to enable firmware modification.

## High-Priority Targets

### Boot Path & Loader Control
- **Stage-2 Loader (`ZK-INKJET-NANO-BOOT.bin`)**
  - Evidence: `data/processed/boot_static_notes.md`, `docs/boot_analysis_methodology.md`
  - Status: ✅ entry, stack setup, relocation, display init mapped.
  - Next actions:
    - [ ] Lift relocation table references (`0X60` block) and cross-map into APP.bin to locate the main entry function.
    - [ ] Identify where SRAM buffers are populated (possible patch points for injected code).

- **Stage-1 Boot (ROM/SD)**  
  - Evidence: Data absent; requires hardware capture or ROM dump.
  - Next actions:
    - [ ] Plan ROM sniff or intercept to determine how BOOT.bin is loaded (needed if Stage-2 patching fails).

### Application Module (`ZK-INKJET-NANO-APP.bin`)
- **Resource/Update Strings**
  - Evidence: `data/processed/app_strings_report.md`, `data/processed/app_message_table.json`, `docs/app_message_handlers.md`
  - Key offsets to investigate:
    - `0X1282C`: Dynamic bitmap naming (`3:/inkjet-ui-%Y%m%d ...`)
    - `0X5D134`: Paths referencing `ZK-INKJET-RES-HW.zkml`
    - UART hints (`baud`, `TTY`, etc.) – none found yet; requires deeper scan.
    - Message handler table at `0X1D3E00` (triples `<handler_ptr, string_ptr, flag>`). Pointers are linked at base `0X20_0000`; e.g., “update complete” → handler `0X2C2049 (Thumb) → VA 0X2C2048 (file+0XC2048)`, “Geen upgradebestand…” → `0X2C47F1 (Thumb) → VA 0X2C47F0 (file+0XC47F0)`. All paths eventually call the shared notifier at `VA 0X2302EC (file+0X302EC)`, which prepares a 0X200-byte buffer and drives helper routines at `0X22714C`, `0X2C64FC`, etc.
    - Hardware commit routine at `0X30E04` (writes to `0XB100D000` registers) finalises display updates.
  - Next actions:
    - [ ] Disassemble handlers referencing these strings to confirm file-load routines.
    - [ ] Hook update-related strings to identify OTA or SD-based upgrade flow.
    - [ ] Combine with `reshw_probe_report` findings to map GUI resource loading.

- **UART/Protocol Discovery**
  - Evidence: pending correlation of strings with code.
  - Tasks (tied to agent_tasks.yaml):
    - [ ] Implement `scripts/proto_skeleton.py` once string offsets and handler functions are known (Task P2-1).
    - [ ] Document serial hypotheses in `docs/protocol_hypotheses.md` with concrete baud-rate evidence.

### Resource Containers
- **GUI Font (`ZK-INKJET-GUI-RES.zkml`)**
  - Evidence: `data/processed/gui_res_font_report.md`
  - Status: ✅ Verified as full Leelawadee UI TTF.
  - Next actions:
    - [ ] Determine how APP.bin loads this font (track usage to potential rendering pipeline for patching text).

- **Hardware Resources (`ZK-INKJET-RES-HW.zkml`)**
  - Evidence: `data/processed/reshw_probe_report.md`, sample extracts under `data/processed/samples/`
  - Next actions:
    - [ ] Parse candidate headers at offsets `file+0XA3000`, `file+0XB5000`, `file+0XD7000`, `file+0XEB000`, `file+0X10A000`, `file+0X164000`.
    - [ ] Identify chunk descriptors (length, checksum) and confirm if assets are raw / compressed.
    - [ ] Once TOC is mapped, attempt controlled replacement of a resource block.

## Supporting Resources
- `docs/analysis_traceability.md` — step-by-step command index for reproducing current findings.
- `docs/archive/documentation-20251009.md` — historic background (boot → APP → resource flow); update when a refreshed deep-dive is ready.
- Vendor manuals under `DWIN/` — cross-reference hardware register ranges used in bootloader (`0XB0000000` base).

## Documentation Actions
- [ ] Produce an updated end-to-end analysis to supersede `docs/archive/documentation-20251009.md`.
- [ ] Maintain `docs/analysis_traceability.md` with each new investigation.
- [ ] Archive experimental detours (e.g., UI aspect ratio) in appendices to keep focus on firmware control.

## Open Questions
- Can we hijack the display init sequence to run custom code before APP.bin executes?
- Where is the UART initialised (Stage-1, Stage-2, or APP)? No direct evidence in BOOT.bin; must confirm within APP.bin.
- Does RES-HW contain executable scripts or only data assets?

Keep this roadmap updated as findings mature and new patch points emerge.
