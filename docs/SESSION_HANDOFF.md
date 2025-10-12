# Session Handoff – Queue Vtable & Flash Guard

## Summary
- `queue_ctrl+0x8` now resolves to the default prefill callback at `VA 0x00269385 (file+0x00069385)` (Thumb) consumed by `queue_prefill` when no override is pending.
- The one-shot slot `queue_ctrl+0x10` is still cleared during initialisation; the concrete writer has not yet been located.
- Flash programming is guarded: caller `VA 0x002C1C10 (file+0x000C1C10)` (cmp) only invokes `VA 0x002BFC34 (file+0x000BFC34)` at `VA 0x002C1C1C (file+0x000C1C1C)` after validator `VA 0x002BFDDC (file+0x000BFDDC)` reports success.

## Evidence Quick Reference

| Address / Offset | Role | Reference |
|------------------|------|-----------|
| `VA 0x0037E820 (file+0x0017E820)` | Literal table of upgrade filenames feeding the matcher. | `docs/update_file_rules.md`, `docs/analysis_traceability.md` §21 |
| `VA 0x0025A930 (file+0x0005A930)` / `VA 0x0025A990 (file+0x0005A990)` / `VA 0x0025A9F0 (file+0x0005A9F0)` | `memcmp` sweeps that enqueue upgrade jobs or the “not found” handler. | `docs/update_file_rules.md`, `docs/analysis_traceability.md` §21 |
| `VA 0x00244F8C (file+0x00044F8C)` | Queue controller block returned by `VA 0x002113E4 (file+0x000113E4)`. | `docs/offset_catalog.md`, `docs/analysis_traceability.md` §21 |
| `queue_ctrl+0x8 → VA 0x00269385 (file+0x00069385)` (Thumb) | Default prefill callback consumed by `queue_prefill` (`VA 0x00269384 (file+0x00069384)`). | `docs/offset_catalog.md`, `docs/analysis_traceability.md` §26 |
| `queue_ctrl+0x10` | One-shot prefill slot (currently cleared; writer unknown). | `docs/SESSION_HANDOFF.md`, `docs/offset_catalog.md` |
| `VA 0x00211356 (file+0x00011356)` | Prefill bridge that dispatches the callbacks above. | `docs/analysis_traceability.md` §24 |
| `VA 0x002C1C10 / 0x2C1C1C (file+0x000C1C10 / 0xC1C1C)` | Caller/branch that gates flash programming on the validator result (`cmp` then `bl`). | `docs/analysis_traceability.md` §27 |
| `VA 0x002BFDDC (file+0x000BFDDC)` | Validator invoked before `VA 0x002BFC34 (file+0x000BFC34)`; zero return aborts the write. | `docs/offset_catalog.md`, `docs/analysis_traceability.md` §27 |
| `VA 0x002BFC34 (file+0x000BFC34)` | Flash writer reached only after the validator succeeds. | `docs/offset_catalog.md`, `docs/analysis_traceability.md` §27 |

## What We Tried / Blockers
- Disassembled `0x27BCC0±0x300` and scanned for `str`/`stm` to `queue_ctrl+0x10` – writes appear indirect; base register not identified (likely set in another module).
- Attempted Capstone-based search for stores with `mem.disp==0x10` across `0x229C00–0x22A200` (queue worker) – no direct hit.

## Repro Breadcrumbs
- Queue slot init:
  ```bash
  BASE=0x200000
  START=0x211350
  LEN=$((0xD0))
  dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/prefill_region.bin \
      bs=1 skip=$((START-BASE)) count=$LEN status=none
  objdump -D -b binary -marm -M force-thumb \
      --adjust-vma=$START /tmp/prefill_region.bin | sed -n '1,120p'
  ```
- Flash guard window:
  ```bash
  BASE=0x200000
  START=0x2C1B80
  dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/flash_guard.bin \
      bs=1 skip=$((START-BASE)) count=$((0x120)) status=none
  objdump -D -b binary -marm --adjust-vma=$START \
      /tmp/flash_guard.bin | sed -n '1,120p'
  ```

## Open Questions
- **Who populates `queue_ctrl+0x10`?**  
  *Next probe:* Extend the Capstone scan to include stores with `disp==0x10` relative to the controller pointer inside `VA 0x00229D78 (file+0x00029D78)` and neighbouring builders (`VA 0x0027BCC0 (file+0x0007BCC0) ± 0x400`).
- **Does validator `VA 0x002BFDDC (file+0x000BFDDC)` touch more than the return code?**  
  *Next probe:* Disassemble `VA 0x002BFDDC (file+0x000BFDDC)`/`VA 0x002BFE40 (file+0x000BFE40)` window and log any side-effect writes (especially to flash controller bases) before/after the compare at `VA 0x002C1C10 (file+0x000C1C10)` (and the subsequent call at `VA 0x002C1C1C (file+0x000C1C1C)`).

## Next-Session Success Criteria
- Concrete VA recorded for the routine that writes a non-null pointer into `queue_ctrl+0x10`, with the store opcode captured.
- Behaviour summary for validator `VA 0x002BFDDC (file+0x000BFDDC)`, including its failure path and any state it mutates, entered into the canonical docs.
- (Stretch) Updated field diagram for the queue controller reflecting the newly identified writer/validator interactions.

## Guardrails / Reminders
- Always mask ARM/Thumb targets with `& ~1` when comparing; record Thumb pointers with the LSB set.
- Queue controller lives at file offset `VA 0x00244F8C (file+0x00044F8C)`.
- Documentation-only changes; no binary patching or device flashing. For UI tests stick to the dry-run recipe in `tests/UPGRADE_POC.md`.
