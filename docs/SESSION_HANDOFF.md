# Session Handoff – Queue Vtable & Flash Guard

## Summary
- `queue_ctrl+0X8` now resolves to the default prefill callback at `0X269385` (Thumb) consumed by `queue_prefill` when no override is pending.
- The one-shot slot `queue_ctrl+0X10` is still cleared during initialisation; the concrete writer has not yet been located.
- Flash programming is guarded: caller `0X2C1C10` (cmp) only invokes `0X2BFC34` at `0X2C1C1C` after validator `0X2BFDDC` reports success.

## Evidence Quick Reference

| Address / Offset | Role | Reference |
|------------------|------|-----------|
| `VA 0X217E820 (file+0X17E820)` | Literal table of upgrade filenames feeding the matcher. | `docs/update_file_rules.md`, `docs/analysis_traceability.md` §21 |
| `VA 0X25A930 / 0X25A990 / 0X25A9F0 (file+0X5A930 / 0X5A990 / 0X5A9F0)` | `memcmp` sweeps that enqueue upgrade jobs or the “not found” handler. | `docs/update_file_rules.md`, `docs/analysis_traceability.md` §21 |
| `VA 0X244F8C (file+0X44F8C)` | Queue controller block returned by `VA 0X2113E4 (file+0X113E4)`. | `docs/offset_catalog.md`, `docs/analysis_traceability.md` §21 |
| `queue_ctrl+0X8 → 0X269385 (Thumb)` | Default prefill callback consumed by `queue_prefill` (`VA 0X269384 (file+0X69384)`). | `docs/offset_catalog.md`, `docs/analysis_traceability.md` §26 |
| `queue_ctrl+0X10` | One-shot prefill slot (currently cleared; writer unknown). | `docs/SESSION_HANDOFF.md`, `docs/offset_catalog.md` |
| `VA 0X211356 (file+0X11356)` | Prefill bridge that dispatches the callbacks above. | `docs/analysis_traceability.md` §24 |
| `VA 0X2C1C10 / 0X2C1C1C (file+0XC1C10 / 0XC1C1C)` | Caller/branch that gates flash programming on the validator result (`cmp` then `bl`). | `docs/analysis_traceability.md` §27 |
| `VA 0X2BFDDC (file+0XBFDDC)` | Validator invoked before `VA 0X2BFC34 (file+0XBFC34)`; zero return aborts the write. | `docs/offset_catalog.md`, `docs/analysis_traceability.md` §27 |
| `VA 0X2BFC34 (file+0XBFC34)` | Flash writer reached only after the validator succeeds. | `docs/offset_catalog.md`, `docs/analysis_traceability.md` §27 |

## What We Tried / Blockers
- Disassembled `0X27BCC0±0X300` and scanned for `str`/`stm` to `queue_ctrl+0X10` – writes appear indirect; base register not identified (likely set in another module).
- Attempted Capstone-based search for stores with `mem.disp==0X10` across `0X229C00–0X22A200` (queue worker) – no direct hit.

## Repro Breadcrumbs
- Queue slot init:
  ```bash
  BASE=0X200000
  START=0X211350
  LEN=$((0XD0))
  dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/prefill_region.bin \
      bs=1 skip=$((START-BASE)) count=$LEN status=none
  objdump -D -b binary -marm -M force-thumb \
      --adjust-vma=$START /tmp/prefill_region.bin | sed -n '1,120p'
  ```
- Flash guard window:
  ```bash
  BASE=0X200000
  START=0X2C1B80
  dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/flash_guard.bin \
      bs=1 skip=$((START-BASE)) count=$((0X120)) status=none
  objdump -D -b binary -marm --adjust-vma=$START \
      /tmp/flash_guard.bin | sed -n '1,120p'
  ```

## Open Questions
- **Who populates `queue_ctrl+0X10`?**  
  *Next probe:* Extend the Capstone scan to include stores with `disp==0X10` relative to the controller pointer inside `0X229D78` and neighbouring builders (`0X27BCC0 ± 0X400`).
- **Does validator `0X2BFDDC` touch more than the return code?**  
  *Next probe:* Disassemble `0X2BFDDC`/`0X2BFE40` window and log any side-effect writes (especially to flash controller bases) before/after the compare at `0X2C1C10` (and the subsequent call at `0X2C1C1C`).

## Next-Session Success Criteria
- Concrete VA recorded for the routine that writes a non-null pointer into `queue_ctrl+0X10`, with the store opcode captured.
- Behaviour summary for validator `0X2BFDDC`, including its failure path and any state it mutates, entered into the canonical docs.
- (Stretch) Updated field diagram for the queue controller reflecting the newly identified writer/validator interactions.

## Guardrails / Reminders
- Always mask ARM/Thumb targets with `& ~1` when comparing; record Thumb pointers with the LSB set.
- Queue controller lives at file offset `0X44F8C`.
- Documentation-only changes; no binary patching or device flashing. For UI tests stick to the dry-run recipe in `tests/UPGRADE_POC.md`.
