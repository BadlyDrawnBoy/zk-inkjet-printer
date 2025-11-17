# Status Dashboard – ZK-INKJET Firmware Recon

> [⤴ Back to archive overview](../README.md)




_Last updated: 2025-10-11_

This dashboard consolidates the "what happened", "what's next", and "where to find it" notes that were previously split
across multiple session documents. Treat it as the single entry point for live status; historical notes remain under
`docs/archive/`.

## 1. Current Snapshot

### Recent Progress
- Queue controller structure documented with callback slots at `queue_ctrl+0x8` and `queue_ctrl+0x10`.
- Flash programming guard mapped: caller `0x002C1C10` only branches to writer `0x002BFC34` after validator
  `0x002BFDDC` returns non-zero.
- Ghidra headless workflow stabilised via `./scripts/gh.sh`, keeping cache/temp paths inside the repository.

### Active Focus
1. Identify the routine that stores a non-null pointer into `queue_ctrl+0x10` (one-shot prefill hook).
2. Characterise validator `0x002BFDDC` (return paths, side-effects) before `0x002BFC34` writes flash.
3. Continue RES-HW structure work (TOC headers, entry descriptors) once queue/flash gating tasks land.

### Known Blockers
- The orchestrator around `0x0020EAEC` still disassembles as ARM instead of Thumb, leaving the call graph empty.
- `queue_ctrl+0x10` store likely occurs via an indirect write; existing Capstone sweeps have not yet captured it.

## 2. Evidence Digest

| Topic | Key Addresses / Artifacts | Notes |
|-------|---------------------------|-------|
| Queue Prefill | `queue_ctrl+0x8 → 0x00269385` (Thumb) | Default prefill callback consumed by `queue_prefill`. |
| Queue One-Shot | `queue_ctrl+0x10` | Slot cleared during init; writer still unknown. |
| Flash Guard | `0x002C1C10` → `0x002BFC34` gated by `0x002BFDDC` | Compare at `0x002C1C10`; call at `0x002C1C1C` fires only on non-zero return. |
| Upgrade Filename Table | `0x0037E820` literal table | Feeds upgrade matcher (see `docs/update_file_rules.md`). |

## 3. Next Actions & Definition of Done

| Action | What to do | Done when |
|--------|------------|-----------|
| Recover Thumb context | Re-run import or apply context override so `0x0020EAEC` disassembles as Thumb. | `export_io_callgraph.py` emits edges for the orchestrator. |
| Trace queue writer | Extend store search around builders (`0x229D78`, `0x27BCC0±0x400`) for `str/stm` with displacement `0x10`. | VA + opcode snippet captured and logged in `docs/offset_catalog.md`. |
| Audit validator | Disassemble `0x2C1B80..0x2C1CC0` and `0x2BFDDC/0x2BFE40`; record side-effects. | Behaviour summary added to canonical docs and cross-linked here. |

## 4. Operational Notes

- **Environment**: Use `./scripts/gh.sh` to wrap `ghidraHeadless` so cache/config directories stay inside the repo
  (`ghidra_cfg/`, `ghidra_cache/`, `ghidra_tmp/`).
- **Sample commands**:
  ```bash
  ./scripts/gh.sh ghidra_projects inkjet_project \
      -process ZK-INKJET-NANO-APP.bin \
      -scriptPath "$(pwd)/ghidra_scripts" \
      -postscript dump_instructions.py 0x20EAEC 32
  ```
  ```bash
  BASE=0x200000
  START=0x2C1B80
  dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/flash_guard.bin \
      bs=1 skip=$((START-BASE)) count=$((0x120)) status=none
  objdump -D -b binary -marm --adjust-vma=$START \
      /tmp/flash_guard.bin | sed -n '1,120p'
  ```

## 5. Reference Index

| Document | Purpose |
|----------|---------|
| `docs/analysis_traceability.md` | Reproducible command recipes for every artifact and experiment. |
| `docs/offset_catalog.md` | Canonical offsets, field layouts, and pointer destinations. |
| `docs/update_file_rules.md` | Upgrade file matcher logic and literal tables. |
| `docs/archive/firmware_mod_plan_legacy.md` | Strategy for safe experimentation (patching, flashing, guard rails) — legacy. |
| `docs/HACKING_UART.md` | Hardware-level UART probing notes and pinouts. |
| `docs/archive/2025-10-10-session-notes.md` | Historical session handoff, brief, and status details preserved for context. |

## 6. How to Contribute Next

1. Review the "Next Actions" table above and pick the task that matches your bandwidth.
2. Follow the relevant commands from `docs/analysis_traceability.md` to reproduce the baseline outputs.
3. When you uncover new evidence, append the findings to the canonical doc (`docs/offset_catalog.md`,
   `docs/update_file_rules.md`, etc.) and summarise the change here.
4. Move any session-specific minutiae into `docs/archive/` once incorporated into the structured docs, keeping
   this dashboard concise and current.

---

For historical logs predating this dashboard, see `docs/archive/2025-10-10-session-notes.md`.
