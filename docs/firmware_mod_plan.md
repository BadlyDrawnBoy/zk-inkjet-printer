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
    - [ ] Lift relocation table references (`0x60` block) and cross-map into APP.bin to locate the main entry function.
    - [ ] Identify where SRAM buffers are populated (possible patch points for injected code).

- **Stage-1 Boot (ROM/SD)**  
  - Evidence: Data absent; requires hardware capture or ROM dump.
  - Next actions:
    - [ ] Plan ROM sniff or intercept to determine how BOOT.bin is loaded (needed if Stage-2 patching fails).

### Application Module (`ZK-INKJET-NANO-APP.bin`)
- **Resource/Update Strings**
  - Evidence: `data/processed/app_strings_report.md`, `data/processed/app_message_table.json`, `docs/app_message_handlers.md`
  - Key offsets to investigate:
    - `VA 0x0021282C (file+0x0001282C)`: Dynamic bitmap naming (`3:/inkjet-ui-%Y%m%d ...`)
    - `VA 0x0025D134 (file+0x0005D134)`: Paths referencing `ZK-INKJET-RES-HW.zkml`
    - UART hints (`baud`, `TTY`, etc.) – none found yet; requires deeper scan.
    - Message handler table at `VA 0x003D3E00 (file+0x001D3E00)` (triples `<handler_ptr, string_ptr, flag>`). Pointers are linked at base `0x20_0000`; e.g., “update complete” → handler `0x2C2049 (Thumb) → VA 0x002C2048 (file+0x000C2048)`, “Geen upgradebestand…” → `0x2C47F1 (Thumb) → VA 0x002C47F0 (file+0x000C47F0)`. All paths eventually call the shared notifier at `VA 0x002302EC (file+0x000302EC)`, which prepares a 0x200-byte buffer and drives helper routines at `VA 0x0022714C (file+0x0002714C)`, `VA 0x002C64FC (file+0x000C64FC)`, etc.
    - Hardware commit routine at `VA 0x00230E04 (file+0x00030E04)` (writes to `MMIO 0xB100D000` registers) finalises display updates.
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
    - [ ] Parse candidate headers at offsets `file+0x000A3000`, `file+0x000B5000`, `file+0x000D7000`, `file+0x000EB000`, `file+0x0010A000`, `file+0x00164000`.
    - [ ] Identify chunk descriptors (length, checksum) and confirm if assets are raw / compressed.
    - [ ] Once TOC is mapped, attempt controlled replacement of a resource block.

## Supporting Resources
- `docs/analysis_traceability.md` — step-by-step command index for reproducing current findings.
- `docs/archive/documentation-20251009.md` — historic background (boot → APP → resource flow); update when a refreshed deep-dive is ready.
- Vendor manuals under `DWIN/` — cross-reference hardware register ranges used in bootloader (MMIO base `0xB0000000`).

## Documentation Actions
- [ ] Produce an updated end-to-end analysis to supersede `docs/archive/documentation-20251009.md`.
- [ ] Maintain `docs/analysis_traceability.md` with each new investigation.
- [ ] Archive experimental detours (e.g., UI aspect ratio) in appendices to keep focus on firmware control.

## Open Questions
- Can we hijack the display init sequence to run custom code before APP.bin executes?
- Where is the UART initialised (Stage-1, Stage-2, or APP)? No direct evidence in BOOT.bin; must confirm within APP.bin.
- Does RES-HW contain executable scripts or only data assets?

Keep this roadmap updated as findings mature and new patch points emerge.
