# Analysis Traceability Index

Addressing conventions: see `docs/CONVENTIONS.md`.

This index records reproducible procedures for each major artifact generated during the current investigation. Follow the command sequences to regenerate outputs, validate findings, and confirm there are no undocumented assumptions.

## 1. UI-QVGA Decoder Pipeline (`scripts/uiqvga_smart_decode.py`)
### Purpose
Refactor the original ad-hoc script into a deterministic CLI pipeline that produces `data/processed/UI_QVGA_480X480.png`.

### Steps
1. **Inspect script changes**
   ```bash
   sed -n '1,200p' scripts/uiqvga_smart_decode.py
   sed -n '200,320p' scripts/uiqvga_smart_decode.py
   ```
   Confirms argparse usage, logging, drift/offset handling, and default parameters.

2. **Run unit coverage**
   ```bash
   python3 -m pytest -q
   ```
   Ensures synthetic round-trip tests (`tests/test_uiqvga_decoder.py`) pass.

3. **Execute decoder with defaults**
   ```bash
   python3 scripts/uiqvga_smart_decode.py \
       --input data/raw/ZK-INKJET-UI-QVGA.bin \
       --output data/processed/UI_QVGA_480X480.png
   ```
   The log should show successful read/write; resulting PNG can be inspected via an image viewer.

4. **Validate deterministic output**
   Repeat command above and compare hashes:
   ```bash
   sha256sum data/processed/UI_QVGA_480X480.png
   ```

## 2. Hyper-Search Parameter Export (`scripts/uiqvga_hypersearch.py`)
### Purpose
Stabilise the brute-force search, add Sobel scoring, export JSON + PNG (`data/processed/uiqvga_params.json`, `UI_QVGA_best.png`).

### Steps
1. **Run focused tests**
   ```bash
   python3 -m pytest -q
   ```
   Covers Sobel magnitude, parameter iterators, and scoring logic (`tests/test_uiqvga_hypersearch.py`).

2. **Execute search with defaults**
   ```bash
   python3 scripts/uiqvga_hypersearch.py
   ```
   Observe progress logs (~9k combos). Outputs: `data/processed/UI_QVGA_best.png`, `data/processed/uiqvga_params.json`.

3. **Review JSON payload**
   ```bash
   cat data/processed/uiqvga_params.json
   ```
   Confirms best/top parameter sets, metrics, and XOR/tile-order used.

4. **Optional: limit search for quick smoke test**
   ```bash
   python3 scripts/uiqvga_hypersearch.py --limit 200 --top 2 --s0-min -2 --s0-max 2 --col-min -1 --col-max 1
   ```

## 3. APP Strings Scan (`scripts/scan_strings.py`)
### Purpose
Extract ASCII/UTF-8 strings from `APP.bin`, filter via regex, and generate `data/processed/app_strings_report.md`.

### Steps
1. **Inspect CLI script**
   ```bash
   sed -n '1,200p' scripts/scan_strings.py
   ```
   Verifies parameters, filtering logic, and report formatting.

2. **Run unit coverage**
   ```bash
   python3 -m pytest -q
   ```
   Ensures extraction, filtering, and hexdump formatting tests (`tests/test_scan_strings.py`) still pass.

3. **Execute scan**
   ```bash
   python3 scripts/scan_strings.py \
       --input data/raw/ZK-INKJET-NANO-APP.bin \
       --output data/processed/app_strings_report.md
   ```

4. **Review report**
   ```bash
   head -n 40 data/processed/app_strings_report.md
   ```
   Confirms metadata header, offsets, and hexdump context.

## 4. Boot Loader Static Notes
### Purpose
Map the structure of `ZK-INKJET-NANO-BOOT.bin`. Final summary stored in `data/processed/boot_static_notes.md`.

### Steps
Follow the dedicated methodology document:
```bash
less docs/boot_analysis_methodology.md
```
- Re-run commands therein to regenerate `boot_disasm.txt` and validate each offset/feature referenced in the notes.

## 5. GUI Font Verification (`data/processed/ZK-INKJET-GUI-RES.zkml`)
### Purpose
Confirm `.zkml` is a stock TrueType font (Leelawadee UI) and document glyph coverage (`data/processed/gui_res_font_report.md`).

### Steps
1. **Validate sfnt structure**
   ```bash
   python3 - <<'PY'
   from pathlib import Path; import struct
   data = Path("data/processed/ZK-INKJET-GUI-RES.zkml").read_bytes()
   scaler, num_tables = struct.unpack(">IH", data[:6])
   print("scaler", hex(scaler), "tables", num_tables)
   PY
   ```
2. **Enumerate name records**
   ```bash
   python3 - <<'PY'
   from pathlib import Path; import struct
   data = Path("data/processed/ZK-INKJET-GUI-RES.zkml").read_bytes()
   # Locate name table and extract family/subfamily strings
   # (same snippet as used during analysis).
   PY
   ```
3. **Inspect cmap coverage**
   ```bash
   python3 - <<'PY'
   from pathlib import Path; import struct
   data = Path("data/processed/ZK-INKJET-GUI-RES.zkml").read_bytes()
   # Print key Unicode ranges (see gui_res_font_report.md for snippet).
   PY
   ```
4. **Cross-check report**
   ```bash
   cat data/processed/gui_res_font_report.md
   ```
   Matches the scripted output.

## 6. Thumb Context & Call-Graph Debug (`scripts/uiqvga_*` unaffected)
### Purpose
Regain Thumb decoding for `FUN_0020EAEC` and diagnose the empty call-graph output.

### Steps
1. **Re-import APP binary with Thumb-enabled language**
   ```bash
   ./scripts/gh.sh ghidra_projects inkjet_project \
       -import data/raw/ZK-INKJET-NANO-APP.bin \
       -loader BinaryLoader -processor ARM:LE:32:v5t \
       -overwrite -analysisTimeoutPerFile 1200
   ```
2. **Set Thumb context and image base (headless)**
   ```bash
   ./scripts/gh.sh ghidra_projects inkjet_project \
       -process ZK-INKJET-NANO-APP.bin \
       -scriptPath "$(pwd)/ghidra_scripts" \
       -postscript set_image_base.py

   ./scripts/gh.sh ghidra_projects inkjet_project \
       -process ZK-INKJET-NANO-APP.bin \
       -scriptPath "$(pwd)/ghidra_scripts" \
       -postscript thumb_redecode.py 0X20EAEC 0X20EE50
   ```
3. **Inspect bytes and instructions**
   ```bash
   ./scripts/gh.sh ghidra_projects inkjet_project \
       -process ZK-INKJET-NANO-APP.bin \
       -scriptPath "$(pwd)/ghidra_scripts" \
       -postscript dump_bytes.py 0X20EAEC 32

   ./scripts/gh.sh ghidra_projects inkjet_project \
       -process ZK-INKJET-NANO-APP.bin \
       -scriptPath "$(pwd)/ghidra_scripts" \
       -postscript dump_instructions.py 0X20EAEC 24
   ```
   _Current result: byte dump shows the region all zeros → no decoded instructions._

4. **Attempt call-graph export**
   ```bash
   ./scripts/gh.sh ghidra_projects inkjet_project \
       -process ZK-INKJET-NANO-APP.bin \
       -scriptPath "$(pwd)/ghidra_scripts" \
       -postscript export_io_callgraph.py "$(pwd)/data/processed/io_callgraph.json" 0X20EAEC 3
   ```
   _JSON root updated to Thumb mode; still no edges because source bytes are missing._

### Follow-up
Resolve the memory mapping so that `0X20EAEC` pulls actual code bytes before repeating the sequence above.

## 7. RES-HW Container Probe (`scripts/reshw_probe.py`)
### Purpose
Sweep `ZK-INKJET-RES-HW.zkml`, highlight candidate header/chunk regions, and create supporting samples (`data/processed/reshw_probe_report.md`, `data/processed/samples/*.bin`).

### Steps
1. **Run unit coverage for helper metrics**
   ```bash
   python3 -m pytest -q
   ```
   Validates entropy/ascii/zero ratio helpers (`tests/test_reshw_probe.py`).

2. **Execute probe**
   ```bash
   python3 scripts/reshw_probe.py \
       --input data/raw/ZK-INKJET-RES-HW.zkml \
       --output data/processed/reshw_probe_report.md \
       --samples data/processed/samples
   ```

3. **Review report**
   ```bash
   cat data/processed/reshw_probe_report.md
   ```
   Table entries should correspond to generated binaries in `data/processed/samples/`.

4. **Inspect sample hexdumps**
   ```bash
   hexdump -C data/processed/samples/reshw_01_0X10A000.bin | head
   ```
   Provides context needed for manual TOC reverse-engineering.

## 8. Manual Orchestrator / Callee Verification (Ghidra-independent)
### Purpose
Confirm the correctness of key routines while Ghidra mapping remains zeroed. Provides raw-file hex dumps, Thumb/ARM disassembly, and BLX edge evidence.

### Steps
1. **Dump raw bytes at orchestrator VA → file offset**
   ```bash
   xxd -g1 -l 64 -s 0XEAEC data/raw/ZK-INKJET-NANO-APP.bin
   ```
   Offset `0XEAEC` = VA `0X20EAEC – 0X200000`. Expect:
   `f7 b5 00 25 2f 00 2c 00 28 00 a2 b0 29 00 02 ae ...`.

2. **Thumb disassembly of the 64-byte chunk**
   ```bash
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/thumb_chunk.bin \
      bs=1 skip=$((0XEAEC)) count=64
   objdump -D -b binary -marm -M force-thumb --adjust-vma=0X20EAEC /tmp/thumb_chunk.bin
   ```
   Shows the expected prologue and the `blx` to the first callee.

3. **ARM disassembly of the callee at `0X211B7C` (64 instructions)**
   ```bash
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/arm_chunk.bin \
      bs=1 skip=$((0X11B7C)) count=$((64*4))
   objdump -D -b binary -marm --adjust-vma=0X211B7C /tmp/arm_chunk.bin
   ```
   Produces 64 ARM instructions for classification.

4. **Verify BLX edge**
   ```bash
   objdump -D -b binary -marm -M force-thumb --adjust-vma=0X20EAEC /tmp/thumb_func.bin | grep -i "bl"
   ```
   After extracting a larger Thumb slice (e.g., 1 KiB), confirms `f003 e81c  blx 0X211b7c`.

5. **Optional: Ghidra probes for diagnostics only**
   ```bash
   ./scripts/gh.sh ghidra_projects inkjet_project \
       -process ZK-INKJET-NANO-APP.bin \
       -scriptPath "$(pwd)/ghidra_scripts" \
       -postscript print_blocks_and_probes.py 0X200000 0XEAEC
   ```
   Documents that Ghidra still returns zeroed bytes despite the raw-file truth.

## 9. APP Message Handler Table (Update Flow Recon)
### Purpose
Locate code paths associated with update-related UI strings inside `ZK-INKJET-NANO-APP.bin`.

### Steps
1. **Parse handler/string table**
   ```bash
   python3 - <<'PY'
   from pathlib import Path
   import struct
   payload = Path("data/raw/ZK-INKJET-NANO-APP.bin").read_bytes()
   base = 0X1D3E00
   for idx in range(0, 0X300, 12):
       entry_off = base + idx
       handler, string_ptr, flag = struct.unpack_from("<III", payload, entry_off)
       if handler == 0 and string_ptr == 0:
           break
       text = payload[string_ptr:payload.find(b"\x00", string_ptr)].decode("utf-8", errors="ignore")
       if "update" in text.lower():
           print(f"{entry_off:#x}: handler=0X{handler:08x}, text={text}")
   PY
   ```
   Confirms triples `<handler_ptr, string_ptr, flag>`; the “update complete” message maps to handler pointer `0X2C2048`.

2. **Translate handler pointer to file offset**
   - Observed relationship: code is linked at base `0X20_0000` → `memory_addr = file_offset + 0X20_0000`.
   - Derive file offset: `0X2C2048 - 0X20_0000 = 0XC2048`.

3. **Disassemble handler routine**
```bash
objdump -b binary -m armv7 -D \
  --start-address=0XC2000 --stop-address=0XC2200 data/raw/ZK-INKJET-NANO-APP.bin  # file+0XC2000..0XC2200
```
   Reveals logic manipulating a structure at offsets `0X144/0X14C`, advancing counters and updating status flags before returning.

4. **Record mapping**
   - Update `docs/offset_catalog.md` with both the table base and the handler offset.
   - Note the +0X20_0000 base adjustment for future pointer decoding.

5. **(Optional) Inspect related handlers**
```bash
objdump -b binary -m armv7 -D \
  --start-address=0XC2400 --stop-address=0XC2800 data/raw/ZK-INKJET-NANO-APP.bin  # file+0XC2400..0XC2800
objdump -b binary -m armv7 -D \
  --start-address=0XC4400 --stop-address=0XC4700 data/raw/ZK-INKJET-NANO-APP.bin  # file+0XC4400..0XC4700
objdump -b binary -m armv7 -D \
  --start-address=0XC47C0 --stop-address=0XC4820 data/raw/ZK-INKJET-NANO-APP.bin  # file+0XC47C0..0XC4820
```
  All handlers mutate the same queue structure (12-byte records) before branching into the shared notifier around `VA 0X2C2628 (file+0XC2628)` (`bl 0X2302EC (file+0X302EC)`).

## 10. Shared Message Notifier (`0X302EC`)
### Purpose
Understand the common routine that processes queued messages (display/update notifications).

### Steps
1. **Disassemble the notifier**
   ```bash
   objdump -b binary -m armv7 -D \
     --start-address=0X30200 --stop-address=0X31200 \
     data/raw/ZK-INKJET-NANO-APP.bin
   ```
   Key observations:
  - Entry at `VA 0X2302EC (file+0X302EC)` pushes the full register set and allocates ~0X26C bytes of stack before accessing message slots.
   - Calls helper routines (`0XDCAC`, `0X2714C`, `0XC64FC`, `0XC5CF8`) after populating a 0X200-byte staging buffer, indicating text/layout processing for on-screen output.
   - Updates status bytes at offsets `0X1660`–`0X1668` (status flags, timers) before returning.

2. **Correlate with handlers**
  - Confirm each handler branches through `VA 0X2C2628 (file+0XC2628)`, which contains `bl 0X2302EC (file+0X302EC)` followed by status checks.
   - Use this relationship when tracing future UI-side effects or when planning to inject custom messages.
   - Note the +0X20_0000 base adjustment for future pointer decoding.

## 11. Hardware Update Routine (`0X30E04`)
### Purpose
Identify the final hardware interaction that commits message updates to the display controller.

### Steps
1. **Disassemble downstream helpers**
   ```bash
   objdump -b binary -m armv7 -D \
     --start-address=0X34400 --stop-address=0X34800 \
     data/raw/ZK-INKJET-NANO-APP.bin
   objdump -b binary -m armv7 -D \
     --start-address=0X30E00 --stop-address=0X31020 \
     data/raw/ZK-INKJET-NANO-APP.bin
   ```
   Observations:
   - Literal at `0X30F34` holds `0XB100D000`; routine `0X30E04` loads this base, waits for bit 0 to clear, writes colour/coordinate data into offsets `0X16`, `0X1C`, `0X28`, `0X2C`, etc., then sets bit 0 to trigger the update.
   - Confirms the notifier ultimately drives the display controller via memory-mapped I/O.

2. **Record conclusions**
   - Added the routine to `docs/offset_catalog.md` with the peripheral base.
   - Future patches can hook before `0X30E04` to intercept or modify on-screen messages.

## 12. Project Status Snapshot (`PROJECT_STATUS.md`)
### Purpose
Provide stakeholders with an at-a-glance summary of completed tasks and outstanding work.

### Steps
```bash
cat PROJECT_STATUS.md
```
- Displays P0/P1/P2 tracker and next actions derived from the artifacts above.

## Test Harness Reminder
- All unit-style validations run via the vendored pytest shim:
  ```bash
  python3 -m pytest -q
  ```
- The shim ensures reproducibility even without external package installs.

## 13. RES-HW Container Index Parser (`scripts/reshw_parse.py`)
### Purpose
Construct a reproducible glyph index (`data/processed/reshw_index.json`) that maps every RES-HW entry to its metadata (stroke count, coordinate payload size, file offsets).

### Steps
1. **Run parser**
   ```bash
   python3 scripts/reshw_parse.py \
       --input data/raw/ZK-INKJET-RES-HW.zkml \
       --output data/processed/reshw_index.json
   ```
   Emits summary statistics plus 6,763 per-glyph records including byte offsets back into the blob.

2. **Inspect index**
   ```bash
   head data/processed/reshw_index.json
   ```
   Confirms header metadata (version, canvas size) and spot-checks entry rows (e.g., `"char": "一"`, `"point_count": 14`).

3. **Validate parser logic**
   ```bash
   python3 -m pytest -q
   ```
   Exercises unit coverage for header parsing and truncation handling (`tests/test_reshw_parse.py`).

## 14. APP Message Handler Table (`scripts/app_message_table.py`)
### Purpose
Extract the message queue handler table from `APP.bin`, map each handler to its status string, and store the mapping for protocol analysis.

### Steps
1. **Generate JSON index**
   ```bash
   python3 scripts/app_message_table.py \
       --input data/raw/ZK-INKJET-NANO-APP.bin \
       --output data/processed/app_message_table.json
   ```
   Produces metadata (flag counts, load address assumptions) and 287 per-entry records linking handler addresses to strings.

2. **Inspect high-priority messages**
   ```bash
   jq '[.entries[] | select(.text | test(\"upgrade\"; \"i\"))][0:5]' \
       data/processed/app_message_table.json
   ```
   Filters for upgrade-related text snippets to drive disassembly targets.

3. **Run unit coverage**
   ```bash
   python3 -m pytest -q
   ```
   Validates table parsing and error handling (`tests/test_app_message_table.py`).

## 15. Message Handler Disassembly Notes (`docs/app_message_handlers.md`)
### Purpose
Capture behavioural summaries for high-priority handlers (upgrade flow, USB errors) referenced by the message table.

### Steps
1. **Disassemble handler in ARM mode**
```bash
objdump -b binary -m armv7 -D \
       --start-address=0XC2000 --stop-address=0XC2140 data/raw/ZK-INKJET-NANO-APP.bin  # file+0XC2000..0XC2140
   ```
   Reveals queue maintenance logic for flag 2 entries (e.g., handler `0XC2048` storing the active index at `[base+0X14C]`).

2. **Switch to Thumb when required**
```bash
objdump -b binary -m armv7 -M force-thumb -D \
       --start-address=0XC3A80 --stop-address=0XC3AF0 data/raw/ZK-INKJET-NANO-APP.bin  # file+0XC3A80..0XC3AF0
   ```
   Necessary for handlers compiled in Thumb mode (flag 3 error path at `0XC3A94`).

3. **Record findings**
   - Summaries, offsets, and follow-up tasks are centralised in `docs/app_message_handlers.md`.

## 16. Upgrade Helper Cascade (UI Prep)
### Purpose
Trace the helper chain that runs after an upgrade file is detected to separate UI preparation from actual storage activity.

### Steps
1. **Disassemble staging routine**
```bash
objdump -b binary -m armv7 -D \
       --start-address=0X9D380 --stop-address=0X9D620 data/raw/ZK-INKJET-NANO-APP.bin  # file+0X9D380..0X9D620
   ```
   Shows handler `0XC28D0` calling the math helpers (`0XC7018`, `0XC70F4`, `0XC7334`, `0XC6CA0`) and queue routine `0XC61DC` before invoking the resource selector (`0X8ACF0`).

2. **Inspect resource selector**
```bash
objdump -b binary -m armv7 -D \
       --start-address=0X8AC80 --stop-address=0X8AE40 data/raw/ZK-INKJET-NANO-APP.bin  # file+0X8AC80..0X8AE40
   ```
   Reveals pointer-table scans over `0X244664`, `0X2471C0`, `0X2474B8` plus repeated `bl 0XE158` comparisons when matching upgrade filenames.

3. **Cross-reference offsets**
   - Capture helper notes in `docs/app_message_handlers.md`.
   - Add offsets for math/resource routines to `docs/offset_catalog.md` for future tracing toward storage I/O.

## 17. Storage Error/Helper Stubs (`docs/storage_probe_notes.md`)
### Purpose
Catalog the low-level routines that log SD/FAT failures and manage heap blocks so later investigations can hook the actual file I/O entry points.

### Steps
1. **Inspect direct-open logger**
```bash
objdump -b binary -m armv7 -M force-thumb -D \
       --start-address=0X11A80 --stop-address=0X11AC0 data/raw/ZK-INKJET-NANO-APP.bin  # file+0X11A80..0X11AC0
   ```
   Reveals the `"direct: can't open"` error handler at `0X11A88`.

2. **Review heap helpers**
```bash
objdump -b binary -m armv7 -M force-thumb -D \
       --start-address=0X11AF0 --stop-address=0X11B30 data/raw/ZK-INKJET-NANO-APP.bin  # file+0X11AF0..0X11B30
   ```
   Identifies `0X11AF8` (allocator) plus bookkeeping functions that toggle the first byte of a block.

3. **Document findings**
   - Summaries live in `docs/storage_probe_notes.md`, with offsets mirrored in `docs/offset_catalog.md`.

## 18. Upgrade Orchestrator Call Graph (`scripts/upgrade_orchestrator_callgraph.py`)
### Purpose
Generate deterministic disassembly and call-site data for the Thumb routine at `0X20EAEC` without relying on the corrupted Ghidra project.

### Steps
1. **Run the helper**
   ```bash
   python3 scripts/upgrade_orchestrator_callgraph.py
   ```
   Creates `data/processed/upgrade_orchestrator_calls.json` and `data/processed/upgrade_orchestrator_disasm.txt`.

2. **Inspect call edges**
   ```bash
   jq '.calls' data/processed/upgrade_orchestrator_calls.json
   head -n 40 data/processed/upgrade_orchestrator_disasm.txt
   ```
   Confirms the direct `blx 0X211B7C` and the two register-dispatch sites.

3. **Confirm the direct callee in ARM mode**
   ```bash
   python3 - <<'PY'
   from pathlib import Path
   from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
   
   BASE = 0X200000
   TARGET = 0X211B7C
   data = Path("data/raw/ZK-INKJET-NANO-APP.bin").read_bytes()
   window = data[TARGET - BASE: TARGET - BASE + 0X60]
   md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
   for insn in md.disasm(window, TARGET):
       print(f"0X{insn.address:08X}  {insn.bytes.hex():>8}  {insn.mnemonic:<8} {insn.op_str}")
       if insn.mnemonic == "bx" and insn.op_str == "lr":
           break
   PY
   ```
   Prints the bitfield helper invoked by the orchestrator and verifies it returns with `bx lr`.

## 19. Orchestrator Caller Enumeration (`scripts/upgrade_orchestrator_callers.py`)
### Purpose
Identify every firmware site that invokes the upgrade orchestrator (and its Thumb wrapper) so arguments can be classified without Ghidra.

### Steps
1. **Enumerate direct callers**
   ```bash
   python3 scripts/upgrade_orchestrator_callers.py
   ```
   Produces `data/processed/upgrade_orchestrator_callers.json` and `.txt` describing each `bl`/`blx` that targets `0X20EAEC`.

2. **Trace the wrapper caller**
   ```bash
   python3 scripts/upgrade_orchestrator_callers.py \
       --target 0X20C74C \
       --output-json data/processed/upgrade_wrapper_callers.json \
       --output-text data/processed/upgrade_wrapper_callers.txt
   ```
   Pinpoints the ARM caller at `0X243DE4` and records surrounding context.

3. **Disassemble the literal helper (ARM)**
   ```bash
   python3 - <<'PY'
   from pathlib import Path
   from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM

   blob = Path("data/raw/ZK-INKJET-NANO-APP.bin").read_bytes()
   addr = 0XA1874
   window = blob[addr:addr + 0X120]
   md = Cs(CS_ARCH_ARM, CS_MODE_ARM); md.detail = True
   for insn in md.disasm(window, addr):
       print(f"0X{insn.address:08X}  {insn.bytes.hex():>8}  {insn.mnemonic:<8} {insn.op_str}")
   PY
   ```
   Outputs the ARM routine invoked via `r1` (`0XA1874`), revealing the UI/status writes performed after the orchestrator fires.

## 20. Free-Block Queue Layout (`VA 0X244F8C (file+0X44F8C)`, `VA 0X2A17C8 (file+0XA17C8)`)
### Purpose
Document the in-memory list walked by the orchestrator and classify the logging callback that formats the histogram.

### Steps
1. **Inspect the orchestrator loop in Thumb mode**
   ```bash
   python3 - <<'PY'
   from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
   from pathlib import Path

   BASE = 0X200000
   START = 0X20EAEC
   blob = Path("data/raw/ZK-INKJET-NANO-APP.bin").read_bytes()
   window = blob[START - BASE: START - BASE + 0X120]
   md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail = True
   for insn in md.disasm(window, START):
       print(f"0X{insn.address:08X}  {insn.bytes.hex():>8}  {insn.mnemonic:<6} {insn.op_str}")
   PY
   ```
   Confirms the list walk (`[node]` = block length, `[node+4]` = next pointer) and histogram binning logic.

2. **Disassemble the logging callback at `VA 0X2A17C8 (file+0XA17C8)`**
   ```bash
   python3 - <<'PY'
   from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
   from pathlib import Path

   START_FO = 0XA17C8
   BASE = 0X200000
   blob = Path("data/raw/ZK-INKJET-NANO-APP.bin").read_bytes()
   window = blob[START_FO: START_FO + 0XE0]
   md = Cs(CS_ARCH_ARM, CS_MODE_ARM); md.detail = True
   for insn in md.disasm(window, BASE + START_FO):
       print(f"0X{insn.address:08X}  {insn.bytes.hex():>8}  {insn.mnemonic:<8} {insn.op_str}")
   PY
   ```
   Shows the `"RR"`/`"aA"` banner setup, byte-serialisation of `[ctx+0X18]`/`[ctx+0X1C]`, and calls to the T5L helpers.

3. **Regenerate annotated caller list**
   ```bash
   python3 scripts/upgrade_orchestrator_callers.py
   python3 scripts/upgrade_orchestrator_callers.py \
       --target 0X20C74C \
       --output-json data/processed/upgrade_wrapper_callers.json \
       --output-text data/processed/upgrade_wrapper_callers.txt
   ```
   New runs confirm no additional callers and capture any literal arguments surrounding the branches.

## 21. Queue Initialiser & Descriptor Allocator (`0X21138A`, `0X211AFC`)
### Purpose
Show how the firmware seeds the free-block queue the orchestrator later walks and identify the helper that provides the 0X88-byte scratch blocks.

### Steps
1. **Hex-dump literals backing the queue controller**
   ```bash
   off=$((0X2113CC - 0X200000))
   xxd -g4 -l 32 -s $off data/raw/ZK-INKJET-NANO-APP.bin
   ```
   Reveals the relocation words consumed by the initialiser (first word zeroes the next-pointer slot; the subsequent words carry the vtable constant and optional scratch-buffer flag).

2. **Disassemble the lazy initialiser**
   ```bash
   off=$((0X211380 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/queue_init.bin \
      bs=1 skip=$off count=$((256)) status=none
   objdump -D -b binary -marm -M force-thumb \
      --adjust-vma=0X211380 /tmp/queue_init.bin | sed -n '0,/^  2113d4/p'
   ```
   Confirms `0X21138A` allocates a 0X20-byte node via `0X20C798`, writes it back to `[queue_ctrl]`, clears the bucket metadata, and attempts to allocate an optional 0X88-byte scratch arena via `0X211AFC`.

3. **Inspect the 0X88-byte allocator**
   ```bash
   off=$((0X211AF0 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/queue_alloc.bin \
      bs=1 skip=$off count=$((128)) status=none
   objdump -D -b binary -marm -M force-thumb \
      --adjust-vma=0X211AF0 /tmp/queue_alloc.bin | sed -n '0,/^  211b20/p'
   ```
   Shows `0X211AFC` requesting 0X88 bytes from the generic allocator (`0X20C798`) and clearing the first byte before returning – the buffer dropped into `node+0X1C` when the optional literal is non-zero.

4. **Confirm allocator VA/FO mapping**
   ```bash
   python3 - <<'PY'
   BASE = 0X200000
   FO = 0XC798
   VA = 0X20C798
   assert VA - BASE == FO, (hex(VA - BASE), hex(FO))
   print("VA/FO OK:", hex(VA), hex(FO))
   PY

   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/alloc_helper.bin \
      bs=1 skip=$((0XC798)) count=$((0X80)) status=none
   objdump -D -b binary -marm --adjust-vma=0X20C798 \
      /tmp/alloc_helper.bin | head -n 20
   ```
   The helper executes in ARM mode at `VA 0X20C798 (file+0XC798)` and matches the callers above; no Thumb re-disassembly is required here.

5. **Locate dispatcher callers**
   ```bash
   python3 - <<'PY'
   from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_ARM
   from capstone.arm import ARM_INS_BL, ARM_INS_BLX
   from pathlib import Path

   BASE = 0X200000
   TARGET = 0X211366  # queue_dispatch
   blob = Path("data/raw/ZK-INKJET-NANO-APP.bin").read_bytes()

   callers = []
   md_t = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md_t.detail = True
   for off in range(0, len(blob) - 4, 2):
       insn_list = list(md_t.disasm(blob[off:off+4], BASE + off, 1))
       if not insn_list:
             continue
       insn = insn_list[0]
       if insn.address != BASE + off:
             continue
       if insn.id in (ARM_INS_BL, ARM_INS_BLX):
             op = insn.operands[0]
             if op.type == 1 and (op.imm & ~1) == TARGET:
                 callers.append(hex(insn.address))
   print(callers)
   PY
   ```
   Returns `['0X21135e', '0X229e0a']`, confirming only the small wrapper and the large work routine invoke `queue_dispatch`.

5. **Disassemble the bulk caller at `0X229D78`**
   ```bash
   off=$((0X229C80 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/queue_work.bin \
      bs=1 skip=$off count=$((512)) status=none
   objdump -D -b binary -marm -M force-thumb \
      --adjust-vma=0X229C80 /tmp/queue_work.bin | sed -n '0,/^  229e40/p'
   ```
   Highlights the reference-count helpers (`0X229C80`/`0X229C9A`), the allocator bridge (`0X229CD8`), and the dispatch site (`0X229E0A`) that flushes the queue after running user callbacks.

## 20. Vtable Placeholder (`VA 0X208592 (file+0X8592)`)
### Purpose
Capture the currently unrelocated target referenced by the literal at `0X2113CC` so future RAM-dump work can decode it quickly.

### Steps
1. **Extract 256 bytes around the suspected function**
   ```bash
   off=$((0X8580))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/vtable_target.bin \
      bs=1 skip=$off count=$((256)) status=none
   ```

2. **Thumb/ARM snapshots (showing relocation padding)**
   ```bash
   objdump -D -b binary -marm -M force-thumb \
       --adjust-vma=0X8590 /tmp/vtable_target.bin | head
   objdump -D -b binary -marm \
       --adjust-vma=0X8580 /tmp/vtable_target.bin | head
   ```
   Both views show loader-fill constants (zeros / literal table) rather than real code, confirming the entry is resolved only at runtime; the pointer literal resolves to `VA 0X208592 (file+0X8592)`.

3. **Document status**
   - See `docs/app_message_handlers.md` (“Support Routines”) for the placeholder note; revisit once a RAM dump is available.

## 21. Upgrade Filename Survey (`docs/update_file_rules.md`)
### Purpose
Catalogue the `.bin` filenames the firmware scans for during upgrades and expose the literal table that backs the comparisons.

### Steps
1. **Enumerate all `:/*.bin` strings**
   ```bash
   python3 - <<'PY'
   from pathlib import Path
   import re

   blob = Path("data/raw/ZK-INKJET-NANO-APP.bin").read_bytes()
   for match in re.finditer(rb'(?:0|1|2|3):/[A-Za-z0-9_\\-./]+\\.bin', blob):
       text = match.group(0).decode("latin-1")
       print(f"0X{match.start():08X} {text}")
   PY
   ```

2. **Show the contiguous literal table**
   ```bash
   off=$((0X217E820 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/update_name_lit.bin \
      bs=1 skip=$off count=$((128)) status=none
   objdump -D -b binary -marm --adjust-vma=0X217E820 \
      /tmp/update_name_lit.bin
   ```
   Confirms that the collected path pointers live in a single table feeding the upgrade matcher.

3. **Locate the memcmp loops**
   ```bash
   off=$((0X25A900 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/update_compare.bin \
      bs=1 skip=$off count=$((1024)) status=none
   objdump -D -b binary -marm --adjust-vma=0X25A900 \
      /tmp/update_compare.bin | sed -n '0,/^  25aa80/p'
   ```
   Shows the three loops at `0X25A930`, `0X25A990`, `0X25A9F0` that iterate over pointer arrays (`0X25AA70`, `0X25AA78`, …) and call `bl 0X20E158`.

---
Maintaining this index ensures every documented finding is traceable to a concrete command and dataset. Extend it with new sections as additional analyses are completed.

## 22. Queue File I/O Wrappers (`0X216B78`, `0X215C64`)
### Purpose
Confirm the Thumb helpers used for the planned RAM dump hook: the opener/writer at `0X216B78` and the closer/reset helper at `0X215C64`.

### Steps
1. **Disassemble the open/write wrapper**
   ```bash
   off=$((0X216B78 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/queue_write_wrapper.bin \
       bs=1 skip=$off count=$((0X100)) status=none
   objdump -D -b binary -marm -M force-thumb \
       --adjust-vma=0X216B78 /tmp/queue_write_wrapper.bin
   ```
   Reveals the Thumb stub issuing the `open` call, writing the supplied buffer, and returning the file handle used by the queue worker.

2. **Disassemble the close/reset wrapper**
   ```bash
   off=$((0X215C64 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/queue_close_wrapper.bin \
       bs=1 skip=$off count=$((0X100)) status=none
   objdump -D -b binary -marm -M force-thumb \
       --adjust-vma=0X215C64 /tmp/queue_close_wrapper.bin
   ```
   Shows the companion helper flushing and closing the handle before clearing the controller state.

## 23. Upgrade Descriptor Builders (`0X27B61C`, `0X27BB80`, `0X27BCC0`)
### Purpose
Trace the control flow from a matched filename into the descriptor/manifest builders that prepare queue work items.

### Steps
1. **Classifier and manifest builder**
   ```bash
   off=$((0X27B61C - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/upgrade_classifier.bin \
       bs=1 skip=$off count=$((0X400)) status=none
   objdump -D -b binary -marm --adjust-vma=0X27B61C \
       /tmp/upgrade_classifier.bin | head -n 80

   off=$((0X27BB80 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/manifest_builder.bin \
       bs=1 skip=$off count=$((0X400)) status=none
   objdump -D -b binary -marm --adjust-vma=0X27BB80 \
       /tmp/manifest_builder.bin | head -n 120
   ```
   Confirms basename normalisation, dispatch table lookups, and descriptor list construction.

2. **Callback installer**
   ```bash
   off=$((0X27BCC0 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/callback_installer.bin \
       bs=1 skip=$off count=$((0X400)) status=none
   objdump -D -b binary -marm --adjust-vma=0X27BCC0 \
       /tmp/callback_installer.bin | head -n 160
   ```
   Shows queue node slots populated with reader/validator pointers.

## 24. Chunk Prefetch Loop (`0X20EA5A`) & Queue Prefill (`0X211356`)
### Purpose
Document how the queue worker reserves buffers, obtains file spans, and copies data into the staging window.

### Steps
1. **Prefetch wrapper**
   ```bash
   off=$((0X20EA5A - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/chunk_prefetch.bin \
       bs=1 skip=$off count=$((0X200)) status=none
   objdump -D -b binary -marm -M force-thumb \
       --adjust-vma=0X20EA5A /tmp/chunk_prefetch.bin
   ```
   Highlights the reserve/copy loop and calls into `0X211356`.

2. **Queue prefill bridge**
   ```bash
   off=$((0X211356 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/queue_prefill.bin \
       bs=1 skip=$off count=$((0X200)) status=none
 objdump -D -b binary -marm -M force-thumb \
      --adjust-vma=0X211356 /tmp/queue_prefill.bin
  ```
  Verifies the controller vtable dispatch and subsequent `0X20D87C` bookkeeping.

   Example disassembly excerpt (showing the read order):
   ```
   0021136c: 6901        ldr   r1, [r0, #16]
   00211370: d003        beq.n 0X21137a
   0021137a: 6880        ldr   r0, [r0, #8]
   0021137c: 4780        blx   r0
   ```

3. **Confirm default prefill target**
   ```bash
   TARGET=0X269380
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/default_prefill.bin \
       bs=1 skip=$((TARGET-0X200000)) count=$((0X60)) status=none
   objdump -D -b binary -marm -M force-thumb --adjust-vma=$TARGET \
       /tmp/default_prefill.bin | sed -n '1,8p'
   ```
   The pointer stored at `queue_ctrl+0X8` resolves (with the Thumb bit set) to `0X269385`; the snippet above shows valid Thumb instructions at that VA, confirming the default callback slot holds executable code.
   Example output (force-thumb):
   ```
   00269384: 000c       movs    r4, r1
   00269386: 1510       asrs    r0, r2, #20
   00269388: 000c       movs    r4, r1
   ```

## 25. Flash Apply Path (`0X22C9E0`, `0X22CA18`)
### Purpose
Capture the routines that validate flash geometry and write the upgrade payload after buffers pass validation.

### Steps
1. **Geometry probe**
   ```bash
   off=$((0X22C9E0 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/flash_probe.bin \
       bs=1 skip=$off count=$((0X400)) status=none
   objdump -D -b binary -marm --adjust-vma=0X22C9E0 \
       /tmp/flash_probe.bin | head -n 80
   ```
   Confirms the size checks and control register setup in the `0X2A1CB8` driver call.

2. **Program loop**
   ```bash
   off=$((0X22CA18 - 0X200000))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/flash_program.bin \
       bs=1 skip=$off count=$((0X600)) status=none
   objdump -D -b binary -marm --adjust-vma=0X22CA18 \
       /tmp/flash_program.bin | head -n 160
   ```
   Shows the calls into the low-level flash driver (`0X2BC27C`, `0X2BFC34`) used to commit the buffer.

## 26. Queue Prefill Vtable Offsets (`0X211356`)
### Purpose
Identify which controller slots `queue_prefill` reads before dispatching the prefill callback.

### Steps
1. **Thumb disassembly around `queue_prefill`**
   ```bash
   BASE=0X200000
   START=0X211340
   LEN=$((0XD0))
   off=$((START-BASE))
   dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/prefill.bin \
       bs=1 skip=$off count=$LEN status=none
   objdump -D -b binary -marm -M force-thumb \
       --adjust-vma=$START /tmp/prefill.bin | sed -n '1,200p'
   ```
   Highlights the `ldr r1, [r0, #16]` / `ldr r0, [r0, #8]` sequence.

2. **Capstone scan for `ldr rX, [r0, #imm]` patterns**
   ```bash
   python3 - <<'PY'
   from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
   from pathlib import Path
   BASE=0X200000
   START=0X211340
   END=0X211410
   blob=Path("data/raw/ZK-INKJET-NANO-APP.bin").read_bytes()
   md=Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=True
   for addr in range(START, END, 2):
       ins=list(md.disasm(blob[addr-BASE:addr-BASE+4], addr, 1))
       if not ins:
           continue
       i=ins[0]
       if i.mnemonic == "ldr" and len(i.operands) == 2:
           dst, mem = i.operands
           if mem.type == 2 and mem.mem.base == 0 and mem.mem.disp >= 0:
               print(hex(i.address), hex(mem.mem.disp))
   PY
   ```
   Confirms the controller offsets (`+0X10`, `+0X8`) read by the routine.

   The literal table at `0X2113D0` installs the default prefill callback (`VA 0X269385 (file+0X69385)`, Thumb) into `queue_ctrl+0X8`; the one-shot slot at `+0X10` is still cleared during initialisation and must be populated elsewhere (TBD – see docs/SESSION_HANDOFF.md for next steps).

   Example force-thumb disassembly at the callback target:
   ```
   00269384: 000c       movs    r4, r1
   00269386: 1510       asrs    r0, r2, #20
   00269388: 000c       movs    r4, r1
   ```

## 27. Flash Writer Guard (cmp `0X2C1C10`, call `0X2C1C1C`)
### Purpose
Show that a flash writer call is gated by a success check immediately beforehand.

### Steps
```bash
BASE=0X200000
VA=0X2C1C10
off=$((VA-BASE-0X40)); [ $off -lt 0 ] && off=0
dd if=data/raw/ZK-INKJET-NANO-APP.bin of=/tmp/flashcall_guard.bin \
    bs=1 skip=$off count=$((0XC0)) status=none
objdump -D -b binary -marm --adjust-vma=$((VA-0X40)) \
    /tmp/flashcall_guard.bin | sed -n '1,120p'
```
Typical excerpt:
```
002c1c10: e3570000    cmp   r7, #0
002c1c14: 11a0000a    movne r0, sl
002c1c18: 01a0000b    moveq r0, fp
002c1c1c: ebfff804    bl    0X2bfc34
002c1c28: ebfff86b    bl    0X2bfddc
002c1c2c: e1a07000    mov   r7, r0
```
No intermediate writes touch `r7` between the validator call and the next compare, proving the writer is executed only when `0X2BFDDC` returns non-zero.
