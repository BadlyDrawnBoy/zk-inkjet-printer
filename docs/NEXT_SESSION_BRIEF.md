# Next Session Brief – Queue Prefill & Validator

## Goals
- **Goal A** – Resolve the writer that installs a non-null pointer into `queue_ctrl+0X10` (one-shot prefill hook).
- **Goal B** – Characterise validator `0X2BFDDC` and document both the non-zero success path and the zero/failure path feeding the guard at `0X2C1C10/0X2C1C1C`.

## Suggested Methods
- Extend the existing Capstone sweep to search for `str`/`stm` with `disp == 0X10` relative to the queue controller pointer inside `0X229D78` and the callback installer window `0X27BCC0 ± 0X400`.
- Confirm callers of `0X2113E4` to capture any routines that obtain the controller pointer before the write.
- Disassemble `0X2C1B80..0X2C1CC0` (guard loop) together with `0X2BFDDC`/`0X2BFE40` to note register usage and any MMIO writes the validator triggers.

## Definition of Done
- New VA recorded (with opcode snippet) for the store into `queue_ctrl+0X10` and referenced in `docs/offset_catalog.md`.
- Behaviour summary for `0X2BFDDC` (success/failure, side-effects) added to `docs/offset_catalog.md` and linked from `docs/SESSION_HANDOFF.md`.
- `docs/SESSION_HANDOFF.md`, `docs/analysis_traceability.md`, and `docs/update_file_rules.md` updated to reflect the findings.
