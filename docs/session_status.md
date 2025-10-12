# Session Status – Upgrade I/O Mapping (2025-10-10)

Addressing conventions: see `docs/CONVENTIONS.md`.

This note records the exact state of the Ghidra-based investigation so the next
agent can continue without rediscovering the setup.

## Environment Summary

* **Repo tooling**
  * `./scripts/gh.sh` wraps `ghidraHeadless`, forcing all config/cache/temp
    directories into the workspace (`ghidra_cfg/`, `ghidra_cache/`,
    `ghidra_tmp/`). This avoids the usual `~/.config` and `/var/tmp`
    permission issues.
  * README now documents this wrapper under the new **Tooling** section.
* **Ghidra project**
  * Created at `ghidra_projects/inkjet_project`.
  * Binary `data/raw/ZK-INKJET-NANO-APP.bin` was successfully imported with
    `-loader BinaryLoader -processor ARM:LE:32:v5`.
  * Auto-analysis ran (≈3–4 minutes per invocation). Expect lots of PNG and
    constructor-resolution warnings; they are harmless but slow.
* **Helper scripts added under `ghidra_scripts/`**
  * `export_io_callgraph.py` – emits a depth-limited call graph from a given
    entry point (current root: `VA 0x0020EAEC (file+0x0000EAEC)`, the upgrade orchestrator). Output
    path: `data/processed/io_callgraph.json`. The script forces `TMode=1`
    before creating functions but the graph still has zero edges (see
    “Open Issues” below).
  * `dump_instructions.py` – dumps the first N instructions of a function to
    stdout (for headless verification).
  * `list_context_registers.py` – diagnostic helper to inspect context
    registers (used to confirm `TMode` handling).

## Current Findings & Data

* `ghidra_scripts/export_io_callgraph.py` invoked successfully but the
  resulting `io_callgraph.json` only contains the root node
  (`VA 0x0020EAEC (file+0x0000EAEC)`). No outgoing edges were recorded.
* Manual headless dump of `FUN_0020EAEC` currently shows a sequence of
  instructions like:
  ```
  0020eaec: addeqs [r11, sp, r11, ror #0x11]
  0020eaf0: addeqs [r11, sp, r12, ror #0x11]
  ...
  ```
  This is a clear sign the function is still being decoded as **ARM** rather
  than **Thumb** (the real instructions should be prologue/BL/BLX patterns,
  not `addeqs`). Consequently:
  * Branch destinations were never recognized, so the call graph is empty.
  * Our analysis scripts run, but they operate on garbage decoding.

## Next Steps for the Next Agent

1. **Fix the disassembly mode around `VA 0x0020EAEC (file+0x0000EAEC)`**
   * Set the `TMode` context bit to `1` (Thumb) for this region and re-run
     auto-disassembly. In the Ghidra GUI, place a flow override or context
     value at `VA 0x0020EAEC (file+0x0000EAEC)`. Headless-only option: write a script that applies a
     `DisassembleCommand` with `ARMTHUMB` context; the current helper only sets
     the bit before function creation, which does not retroactively fix blocks
     already interpreted as ARM.
   * Once instructions look sane (push/pop, BL calls, etc.), re-run
     `export_io_callgraph.py` – the JSON should populate with edges.

2. **Explore immediate callees**
   * After the call graph works, investigate the first-order callees to
     classify them (sd_read, sd_write, memcpy, logger, retry, unknown).
   * Use `dump_instructions.py` or the GUI to capture opcode evidence for
     each callee for inclusion in `docs/io_funcs.md`.

3. **Descriptor table reconstruction**
   * With correct disassembly, trace how `FUN_0020EAEC` walks descriptor
     tables (`sp+0x??` offsets). Record field sizes and produce hex samples
     for `docs/descriptor_probe.md`.

4. **MMIO write inventory**
   * Once real code flow is visible, search the subgraph for translated
     `STR/STM` operations that access bases ≥ `0xB0000000` (MMIO). Document these in
     `docs/mmio_writes.md` (address, width, expression).

## Key Paths & Commands

* Re-run import (already done):
  ```bash
  ./scripts/gh.sh ghidra_projects inkjet_project \
      -import data/raw/ZK-INKJET-NANO-APP.bin \
      -loader BinaryLoader -processor ARM:LE:32:v5 \
      -analysisTimeoutPerFile 1200
  ```
* Re-run call graph export (after fixing Thumb decoding):
  ```bash
  ./scripts/gh.sh ghidra_projects inkjet_project \
      -process ZK-INKJET-NANO-APP.bin \
      -scriptPath "$(pwd)/ghidra_scripts" \
      -postscript export_io_callgraph.py "$(pwd)/data/processed/io_callgraph.json" \
      0x20EAEC 3
  ```
* Quick instruction dump for sanity checks:
  ```bash
  ./scripts/gh.sh ghidra_projects inkjet_project \
      -process ZK-INKJET-NANO-APP.bin \
      -scriptPath "$(pwd)/ghidra_scripts" \
      -postscript dump_instructions.py 0x20EAEC 32
  ```

## Open Issues

* **Thumb context** – the orchestrator is still decoded as ARM (incorrect). Fix
  this before trusting any addresses or call graphs.
* **Call graph JSON** – currently root-only due to the issue above.
* **MMIO logging & descriptor docs** – not started yet; dependent on correct
  call graph coverage.
* **Analysis time** – each headless re-run takes ~3–4 minutes. If you create
  additional scripts, try to reuse the project instead of re-importing.

Feel free to continue working from these notes; once the call graph produces
real edges, proceed with the classification/MMIO/descriptor deliverables
described in `docs/session_status.md`.

---

## Update – 2025-10-10 (late session)

### Actions Performed
- Imported `ZK-INKJET-NANO-APP.bin` into the same project with the Thumb-capable language `ARM:LE:32:v5t` to expose the `TMode` context register.
- Added and exercised the helper scripts:
  - `ghidra_scripts/thumb_redecode.py` – enforces Thumb context over a range and clears/re-disassembles.
  - `ghidra_scripts/set_image_base.py` – ensures the image base is locked to `0x20_0000` after re-imports.
  - `ghidra_scripts/dump_bytes.py` – quick hexdump utility for headless sanity checks.
  - Updated `dump_instructions.py` / `export_io_callgraph.py` to use the three-argument `getValue` API and fall back to integer comparison.
- Repeated headless passes of `thumb_redecode.py` on `0x20EAEC–0x20EE50`; Ghidra reports the region as Thumb, but `dump_bytes.py` shows the underlying bytes are `0x0`.
- Re-ran `export_io_callgraph.py`; the JSON now records the root node in Thumb mode, but edges remain empty because the disassembler still sees zeroed data at the orchestrator.

### Current Findings
- The address range `VA 0x0020EAEC (file+0x0000EAEC)`–`VA 0x0020EB0C (file+0x0000EB0C)` is all zero after the `v5t` re-import (`dump_bytes.py 0x20EAEC 32`). This indicates the bytes were not mapped from the raw image when the new program was created.
- Because the backing memory is zero, both the instruction dumper and call-graph exporter cannot recover any flow information – hence the empty edge set.

### Suggested Next Moves
1. **Verify mapping for the orchestrator block**  
   - Re-import just the APP binary into a *fresh* project with language `ARM:LE:32:v5t` and confirm the loader’s base/length.  
   - If the address space truncates before `VA 0x0020EAEC (file+0x0000EAEC)`, adjust the raw binary loader options (start offset / length) or use “Memory Map” to add the missing bytes manually.
2. **Once bytes are present**, re-run `thumb_redecode.py`, `dump_instructions.py`, and `export_io_callgraph.py` – expect a valid Thumb prologue and populated edges.
3. **Document any remapping** in this file and append exact headless commands to `docs/analysis_traceability.md`.

### Open Issues
- `data/processed/io_callgraph.json` still lacks edges; root node mode now shows `Thumb`, confirming context is correct but bytes are missing.
- Need to revisit descriptor/MMIO tasks after the orchestrator range is restored.
- Auto-analysis throws repeated “function entryPoint may not be created on defined data” warnings due to aggressive ARM analyzers; once the mapping issue is fixed, consider disabling `ARM Symbol` during headless runs to speed up iterations.

---

## Update – 2025-10-11 (manual verification, Ghidra mapping still zero)

### Actions Performed
- Re-imported `ZK-INKJET-NANO-APP.bin` into both `inkjet_project` and a clean `inkjet_scratch` project with `-noanalysis` to avoid legacy analysis artefacts.
- Created helper probes (`print_blocks_and_probes.py`, `remap_via_filebytes.py`) to inspect block metadata and retry zero-free remaps in transactions.
- Confirmed via raw file tooling (outside Ghidra) that the orchestrator region is valid Thumb:
  - `xxd -g1 -l 64 -s 0xEAEC data/raw/ZK-INKJET-NANO-APP.bin`
  - `objdump -D -b binary -marm -M force-thumb --adjust-vma=0x20EAEC` on the 64‑byte chunk.
- Disassembled the ARM callee at `VA 0x00211B7C (file+0x00011B7C)` by extracting 256 bytes and running:
  - `objdump -D -b binary -marm --adjust-vma=0x211B7C /tmp/arm_chunk.bin`
- Verified the orchestrator issues a direct `blx 0x211b7c`, proving the call edge independently of Ghidra.

### Current Findings
- Despite fresh imports, explicit `set_image_base.py`, and chunk/FileBytes remapping scripts, every headless `getBytes` in Ghidra still reports zeros for `VA 0x0020EAEC (file+0x0000EAEC)`. The new diagnostics confirm only a single `ram` block exists and is marked initialised/readable, so the failure is likely a program-database quirk rather than missing file data.
- Manual tooling provides reliable Thumb/ARM listings and the critical BLX edge, so call-graph work can proceed outside Ghidra if needed.

### Suggested Next Moves
1. **Documented pipeline:** Keep using raw-file + `objdump`/Capstone scripts to enumerate additional callees while Ghidra is offline.
2. **Fresh Ghidra program if required:** If GUI analysis is still desired, generate a brand-new program database (e.g., via a minimal `create_program_from_raw.py`) and confirm writes stick before investing more time.
3. **Record commands/results:** Ensure `docs/analysis_traceability.md` reflects the manual hexdump/disassembly steps so the next session can reproduce them quickly.

---

## Update – 2025-10-11 (capstone call graph extraction)

### Actions Performed
- Added `scripts/upgrade_orchestrator_callgraph.py`, a Capstone-based helper that decodes the Thumb routine at `VA 0x0020EAEC (file+0x0000EAEC)` straight from the raw APP image and emits both JSON (`data/processed/upgrade_orchestrator_calls.json`) and a text listing (`data/processed/upgrade_orchestrator_disasm.txt`).
- Ran the helper from the repository root; it recovered 71 instructions and three call-sites (one direct `blx 0x211B7C`, two register-dispatch sites fed from the stack).
- Spot-checked the direct callee at `VA 0x00211B7C (file+0x00011B7C)` with Capstone in ARM mode to confirm it terminates with `bx lr` and contains the expected bitfield math used by prior notes.

### Current Findings
- The JSON artifact captures the orchestrator loop that seeds a 0x20-entry table on the stack before invoking the staging helpers. Register calls at `VA 0x0020EB52 (file+0x0000EB52)` (`blx r4`) and `VA 0x0020EB68 (file+0x0000EB68)` (`blx r7`) pull their targets from `[sp, #0x8c]`, proving the runtime supplies a function pointer table rather than fixed ROM addresses.
- `data/processed/upgrade_orchestrator_disasm.txt` is now the ground-truth disassembly for this routine while the Ghidra project remains corrupted; it matches the manual `objdump` snippets logged earlier and can be diffed across runs.
- The ARM helper at `VA 0x00211B7C (file+0x00011B7C)` is confirmed live and should be catalogued in the descriptor/MMIO notes once the pointer table decoding is complete.

### Suggested Next Moves
1. Derive the actual callees behind `r4`/`r7` by decoding the stack slots populated before the dispatch loop (likely `sp+0x8c`/`sp+0x90`); extend the new script or add a companion to resolve those pointers automatically.
2. Correlate the recovered call targets with existing TODOs in `docs/descriptor_probe.md` and `docs/mmio_writes.md` so follow-on work can document descriptor layouts and MMIO traffic.
3. Once Ghidra is healthy again, import the JSON/text outputs to cross-check against headless scripts and retire the temporary Capstone pipeline.

---

## Update – 2025-10-11 (orchestrator caller mapping)

### Actions Performed
- Authored `scripts/upgrade_orchestrator_callers.py` to scan the raw APP binary with Capstone and enumerate `bl`/`blx` instructions that land on the Thumb orchestrator at `VA 0x0020EAEC (file+0x0000EAEC)`.
- Ran the scanner (default target) to confirm only one direct call site exists: `VA 0x0020C75C (file+0x0000C75C)` (`bl #0x20eaec`) inside the Thumb wrapper at `VA 0x0020C74C (file+0x0000C74C)`.
- Re-ran the scanner with `--target 0x20C74C` to trace the upstream ARM caller. This identified `0x243DE4 (blx #0x20c74c)`, allowing inspection of its literal arguments.
- Disassembled the ARM routine referenced by the literal (`VA 0x002A1874 (file+0x000A1874)`) and captured its behaviour: it populates offsets `0x40–0x43` and `0x224–0x22f` with ASCII markers and splits fields from `[r4+0x18]`/`[r4+0x1c]`, hinting at a UI/status preparation step.

### Current Findings
- The orchestrator wrapper (`VA 0x0020C74C (file+0x0000C74C)`) is invoked from `VA 0x00243DD0 (file+0x00043DD0)`, which seeds `r0` with the literal at `VA 0x00243DF0 (file+0x00043DF0)` (`VA 0x002A1874 (file+0x000A1874)`) and passes `sp` in `r1`. Consequently, the orchestrator receives:
  * `r0` – dereferenced pointer returned by the global stub at `VA 0x0020EA38 (file+0x0000EA38)` (still sourced from `VA 0x00244F8C (file+0x00044F8C)`).
  * `r1` – function pointer `VA 0x002A1874 (file+0x000A1874)` (ARM mode), reused for both `blx r4` and `blx r7`.
  * `r2` – scratch pointer into the caller’s stack frame.
- ARM routine `VA 0x002A1874 (file+0x000A1874)` appears to stage UI text/metadata, writing `"RR"`/`"aA"` pairs and unpacking two 32-bit fields into byte slices before invoking helper calls at `VA 0x00248610 (file+0x00048610)` and `VA 0x00248504 (file+0x00048504)`.
- The new artifacts `data/processed/upgrade_orchestrator_callers.json` and `.txt` now record the reproducible call-tree evidence independent of the Ghidra database.

### Suggested Next Moves
1. Decode the structure at `VA 0x00244F8C (file+0x00044F8C)` (the pointer returned by `VA 0x0020EA38 (file+0x0000EA38)`) so we know which table the orchestrator walks before issuing the scripted callbacks.
2. Classify the ARM helper at `VA 0x002A1874 (file+0x000A1874)` and its callees (`VA 0x00248610 (file+0x00048610)`, `VA 0x00248504 (file+0x00048504)`) in `docs/app_message_handlers.md`, noting how they transform the UI/state buffer passed via `r1=sp`.
3. Extend `scripts/upgrade_orchestrator_callers.py` (or a companion) to emit the literal arguments observed at each call site, easing future resolution of additional callers if the firmware changes.

---

## Update – 2025-10-11 (queue layout + helper classification)

### Actions Performed
- Reverse-engineered the data structure referenced via `VA 0x0020EA38 (file+0x0000EA38)`/`VA 0x00244F8C (file+0x00044F8C)`. The stub returns a pointer to a singly linked list of *free-block descriptors* that lives in RAM (first word = block size in bytes, `+0x4` = next node, `+0xC` feeds the tail pointer used later). The orchestrator iterates this list, bins block lengths by bit-width, and tallies total free bytes before feeding the results to its callbacks.
- Disassembled the Thumb orchestrator into structured pseudo-code: initial loop seeds a 32-entry histogram, `blx 0x211B7C` computes the average block size, the first callback logs `"%d bytes in %d free blocks (avge size %d)\n"`, and the second callback walks each non-zero histogram bucket to emit `" blocks 2^%d+1 to 2^%d\n"` ranges.
- Analysed the callback target at file offset `VA 0x002A17C8 (file+0x000A17C8)` (load address `VA 0x002A17C8 (file+0x000A17C8)`). It treats `r0` as a 0x240-byte UI/status buffer, writes the `"RR"` / `"aA"` banner prefix, serialises the 32-bit counters from `[base+0x18]`/`[base+0x1C]` into ASCII bytes at `[base+0x228..0x22F]`, increments `[base+0x3C]` (block counter), and then invokes the hardware helpers at `VA 0x00248610 (file+0x00048610)` / `VA 0x00248504 (file+0x00048504)` to push the formatted line to the screen. Failure in the T5L helper keeps the status flag (`[base+3]`) asserted so the UI can retry.
- Extended `scripts/upgrade_orchestrator_callers.py` to annotate each call-site with any literal argument loads (PC-relative `ldr`, `adr`, `movw/movt`, etc.). The new JSON/Text outputs now highlight argument immediates whenever the firmware seeds them near the branch.

### Current Findings
- The global at `VA 0x00244F8C (file+0x00044F8C)` is a pointer slot that the runtime populates with the head of the free-block list (`struct list_node { uint32_t length; struct list_node *next; uint32_t payload; uint32_t tail; }`). The orchestrator stores `head + 0xC` on the stack but does not dereference it yet; companion routines likely use the tail pointer to append new nodes.
- Callback #1 (`VA 0x002A17C8 (file+0x000A17C8)`) clears and rebuilds the status blink buffer, ensuring the `"RR aA"` prefix and the packed byte counters reflect the latest histogram totals before issuing the display DMA transfers.
- Callback #2 (same function, reached in the loop) relies on the fifth argument (stored on the stack) to receive the bucket index; this matches the format string requesting both the lower and upper power-of-two bounds.
- No additional callers were found beyond the wrapper at `VA 0x0020C74C (file+0x0000C74C)`, confirming the orchestrator list is exclusively consumed by the upgrade status path.

### Suggested Next Moves
1. Observe the runtime initialisation that seeds `VA 0x00244F8C (file+0x00044F8C)` to confirm when the free-block list is allocated and whether `+0xC` truly holds the tail pointer (instrumenting the headless project or emulating the linked list builder would help).
2. Capture the data pumped into `VA 0x00248610 (file+0x00048610)`/`VA 0x00248504 (file+0x00048504)` to determine the exact hardware protocol (likely T5L DMA descriptors) and cross-link the offsets with `docs/mmio_writes.md`.
3. Extend the histogram analysis with a script that walks a RAM dump, re-creating the `list_node` chain to validate the inferred layout against real data.

---

## Update – 2025-10-11 (queue users and dispatch path)

### Actions Performed
- Searched for `bl`/`blx` calls into the queue dispatcher (`VA 0x00211366 (file+0x00011366)`). Found only two direct callers: the tiny wrapper at `VA 0x0021135E (file+0x0001135E)` and a large Thumb routine at `VA 0x00229D78 (file+0x00029D78)`.
- Disassembled the wrapper (`VA 0x0021135E (file+0x0001135E)`), confirming it is just `queue_init_and_dispatch()`—it invokes the lazy initialiser (`VA 0x0021138A (file+0x0001138A)`) and then falls straight through to the dispatcher. No additional state is mutated here.
- Examined the 0x229D78 caller. The function sets up work descriptors on the stack, generates output chunks via callback pointers held in `[sp+0x10]`/`[sp+0x16]`, and when a “flush” flag at `[sp]` is non-zero it:
  * Runs a user-supplied completion hook (`blx r2`) with `(total_bytes, base_ptr + stride, context)` parameters.
  * Calls `queue_dispatch()` to publish the freshly prepared blocks.
  * Immediately invokes `VA 0x00211AD8 (file+0x00011AD8)`, which appears to reset the optional tail buffer acquired earlier (it issues `VA 0x0020C804 (file+0x0000C804)`, the same Thumb helper used when recycling nodes).
- Mapped the auxiliary helpers in the same region:
  * `VA 0x00229C80 (file+0x00029C80)`/`VA 0x00229C9A (file+0x00029C9A)` bump and drop the 0x1C-byte reference counter stored in each node; when that counter hits zero they call `VA 0x002278D0 (file+0x000278D0)` followed by `VA 0x00229D3C (file+0x00029D3C)` to return the block to the pool.
  * `VA 0x00229CD8 (file+0x00029CD8)` offsets the descriptor by 0x10 and forwards to `VA 0x0022987C (file+0x0002987C)`, showing that the first 16 bytes of the queue node form a header preceding the data payload.

### Current Findings
- The queue dispatch sequence is only triggered from the large work routine at `VA 0x00229D78 (file+0x00029D78)`, which packages variable-length data and writes stride/callback metadata into the tail of the node before flushing it through `queue_dispatch()`. This routine also populates the auxiliary fields at offsets `0x78/0x7C` and iterates `*(node+0x16)` to stream multi-block updates.
- Reference counting for queue nodes is tracked at offset `0x1C`; the helper pair at `VA 0x00229C80 (file+0x00029C80)`/`VA 0x00229C9A (file+0x00029C9A)` increments the new owner’s count and decrements the previous owner, returning the block to the allocator via `VA 0x00229D3C (file+0x00029D3C)` when the count reaches zero.
- Still no direct calls to the heavy processor at `VA 0x00211430 (file+0x00011430)`; the address is almost certainly stored in the vtable slot seeded by the literal `VA 0x002113CC (file+0x000113CC)`, so the function is reached via function-pointer dispatch rather than a static `bl`.

#### Producer API one-pager (0x229D78 → queue_dispatch)

```
flush_flag = *(sp+0x0); block_count = *(sp+0x4)
stride_bytes = *(sp+0x8); node_base = *(sp+0xC)
producer_cb = *(sp+0x10); telemetry_cb = *(sp+0x28)
prefill_cb = *(sp+0x2C); flush_cb = *(sp+0x30); ctx_arg = *(sp+0x34)
ptr0 = prefill_cb ? prefill_cb(node_tail(node_base)) : default_prefill(node_base)
if (!ptr0) goto exit
ptr = ptr0
if (producer_cb) for i in range(block_count): ptr = producer_cb(ptr)
tail[-0x80+0x78] = stride_bytes; tail[-0x80+0x7C] = block_count
if (telemetry_cb) telemetry_cb(ptr0, block_count, stride_bytes)
if (flush_flag && flush_cb) flush_cb(ptr - ptr0, ptr0 + stride_bytes, ctx_arg)
queue_dispatch()
reset_scratch()  # 0x211AD8
```

| Location | Meaning | Notes |
|----------|---------|-------|
| `[sp+0x0]` | Flush gate | Set to `1` before final dispatch. |
| `[sp+0x4]` | Block count | Copied into `tail[-0x80+0x7C]`. |
| `[sp+0x8]` | Stride bytes | Copied into `tail[-0x80+0x78]`. |
| `[sp+0xC]` | Node base pointer | Start of the queue node payload. |
| `[sp+0x10]` | Producer callback | `blx` per block when non-null. |
| `[sp+0x28]` | Telemetry hook | Invoked just before flush. |
| `[sp+0x2C]` | Prefill callback | Supplies initial write pointer (`VA 0x00211356 (file+0x00011356)` path). |
| `[sp+0x30]` | Flush completion | Receives `(total_bytes, next_ptr, ctx)`. |
| `[sp+0x34]` | Flush context | Third argument passed to `flush_cb`. |
| `tail[-0x80+0x78]` | Stride cache | Persisted for reader side. |
| `tail[-0x80+0x7C]` | Block cache | Persisted for reader side. |

Current slot contents (mirrored in `docs/offset_catalog.md`): `queue_ctrl+0x8` carries the default prefill callback at `VA 0x00269385 (file+0x00069385)` (Thumb) that `queue_prefill` falls back to, while the one-shot hook at `queue_ctrl+0x10` is still cleared during initialisation – the concrete writer remains TBD.

`queue_prefill` (`VA 0x00211356 (file+0x00011356)`) fetches its callbacks directly from the controller block: it first probes `queue_ctrl+0x10` (optional prefill handler) and, when that slot is null, falls back to the default pointer stored at `queue_ctrl+0x8`.

*Optional RAM hook plan (not yet implemented):* patch tail of `VA 0x0021135E (file+0x0001135E)` (`queue_init_and_dispatch`) to check for `3:/DUMP.MRK`; when present, emit `0x244F00–0x245000` as `ram_qctrl.bin` and `0x217E800–0x217EC00` as `ram_lit.bin`. The helper would reuse the queue’s installed read callback (reachable via `VA 0x00211356 (file+0x00011356)`) to dump the controller state, then flush the artefacts through the existing file wrappers (`VA 0x00216B78 (file+0x00016B78)` open/write, `VA 0x00215C64 (file+0x00015C64)` close/reset). Remember the controller block lives at `VA 0x00244F8C (file+0x00044F8C)`.

### Suggested Next Moves
1. Resolve the vtable literal at `VA 0x002113CC (file+0x000113CC)` and locate who installs actual handlers into `[queue_ctrl+0x10]`/`[queue_ctrl+0x18]` so we can trace where `VA 0x00211430 (file+0x00011430)` is invoked.
2. Analyse `VA 0x00229D78 (file+0x00029D78)`’s parameters (stack layout around `[sp+0x0]...[sp+0x48]`) to document the API that produces queue entries—this will make it easier to recreate or patch the free-block data path.
3. Investigate `VA 0x00211AD8 (file+0x00011AD8)` to confirm whether it clears the scratch buffer or performs additional bookkeeping after each dispatch; note any MMIO writes it emits.
4. Optional RAM dump scaffold: add a `BL maybe_dump` at the tail of `queue_init_and_dispatch` (`VA 0x0021135E (file+0x0001135E)`) guarded by a marker file (`3:/DUMP.MRK`). The helper would call the existing file I/O wrappers around `VA 0x00216B78 (file+0x00016B78)`/`VA 0x00215C64 (file+0x00015C64)` to emit two slices – `0x244F00..0x245000` (`ram_qctrl.bin`) and `0x217E800..0x217EC00` (`ram_lit.bin`) – then disable itself via a static `dump_done` flag.

---

## Update – 2025-10-11 (free-block queue seeding)

### Actions Performed
- Identified the queue-control accessor at `VA 0x002113E4 (file+0x000113E4)` (ARM stub). It returns a pointer to the controller block located at `VA 0x00244F8C (file+0x00044F8C)`. The first word of that block acts as the free-list head pointer consumed by the orchestrator.
- Disassembled the Thumb helper at `VA 0x0021138A (file+0x0001138A)`. On first use it allocates a 0x20-byte node via `VA 0x0020C798 (file+0x0000C798)`, writes the new node back into `[queue_ctrl+0x0]`, zeroes the bookkeeping fields, and populates a vtable slot with the relocation literal stored alongside the function. The optional scratch buffer lives at `[node+0x1C]` and is only allocated when the literal at `VA 0x002113D4 (file+0x000113D4)` is non-zero (currently it is zero, so the tail pointer is initialised to `NULL`).
- Examined the descriptor allocator `VA 0x00211AFC (file+0x00011AFC)` (Thumb). It reserves 0x88 bytes, clears the first byte, and returns the pointer; this is the helper invoked when the queue requires a scratch arena.
- Followed the immediate caller `VA 0x00211366 (file+0x00011366)`, confirming it defers to `VA 0x0021138A (file+0x0001138A)` for lazy initialisation before invoking the callback table stored at offsets `0x10/0x18/0x1C`.

### Current Findings
- The orchestrator’s “free-block queue” is backed by a small controller structure whose head pointer sits at `queue_ctrl[0]`. The initial node includes a vtable pointer (literal at `VA 0x002113CC (file+0x000113CC)` resolves to Thumb target `VA 0x00208592 (file+0x00008592)`) and a constant `0x6` bucket count at offset `0x8`, matching the 32 histogram bins used by `VA 0x0020EAEC (file+0x0000EAEC)`.
- Node initialisation clears the status byte at offset `0xC` and the three pointer slots at offsets `0x8/0xC/0x10`. A secondary buffer (offset `0x1C`) is provisioned via `VA 0x00211AFC (file+0x00011AFC)` when the optional literal is set—currently the firmware ships with this literal cleared, so the list starts empty beyond the head node.
- The accessor `VA 0x00211366 (file+0x00011366)` repeatedly calls function pointers stored at `queue_ctrl+0x10` and `queue_ctrl+0x18`, which aligns with the orchestrator’s later `blx r4` / `blx r7` dispatch; those registers are loaded from the stack slots the accessor fills.

### Suggested Next Moves
1. Track the callers of `VA 0x00211366 (file+0x00011366)` / `VA 0x00211430 (file+0x00011430)` to see where new blocks are appended to the free list, and document how `[node+0x4]` and `[node+0x1C]` evolve at runtime.
2. Resolve the relocation literal at `VA 0x002113CC (file+0x000113CC)` once we have relocation data (or a RAM dump) to confirm which routine is being registered as the node vtable.
3. Map the remaining fields inside `queue_ctrl` (offsets `0x4`, `0x8`, `0x10`, etc.) by instrumenting their readers in `VA 0x00211430 (file+0x00011430)` so the histogram output in the orchestrator can be tied back to concrete queue state.
4. Optional: plan a “display tap” around `VA 0x00248610 (file+0x00048610)` / `VA 0x00248504 (file+0x00048504)` – either a NOP stub (mute DMA) or a RAM copy of the `(ptr,len)` arguments before tail-calling the original helper – so we can inspect UI payloads without JTAG once function ownership is confirmed.

## Findings

**Verified:**
- VA 0x0037E820 (file+0x0017E820) pointer pool drives matcher; see evidence in docs/update_file_rules.md.
- VA 0x0025A930 / 0x0025A990 / 0x0025A9F0 loops branch to VA 0x0020E158 (file+0x0000E158) before queue install (evidence in docs/update_file_rules.md, docs/analysis_traceability.md).
- VA 0x0020EAEC (file+0x0000EAEC) orchestrator plus Thumb helpers at VA 0x0020EA5A and VA 0x00211356 confirmed via objdump snippets.
- VA 0x00244F8C (file+0x00044F8C) queue controller usage captured in docs/offset_catalog.md evidence block.
- VA 0x002BFDDC (file+0x000BFDDC) validator and guard pair VA 0x002C1C10/VA 0x002C1C1C verified (docs/update_file_rules.md, docs/analysis_traceability.md).
- VA 0x0022C9E0 (file+0x0002C9E0) and VA 0x0022CA18 (file+0x0002CA18) flash writer stages observed in ARM windows.

**Needs follow-up:**
- queue_ctrl+0x10 writer still unknown; evidence block pending despite queue_ctrl+0x8 default being confirmed.
- VA 0x00208592 (file+0x00008592) remains relocation placeholder (no executable bytes in binary dump).
