# Firmware Offset Catalog

Addressing conventions: see `docs/CONVENTIONS.md`.

| File | Offset (hex) | Description | Evidence |
|------|--------------|-------------|----------|
| `ZK-INKJET-NANO-BOOT.bin` | `0x0` | Reset stub entering privileged modes and loading stack pointers for each CPU mode from literals at `0x40–0x54`. | `data/processed/boot_static_notes.md`, `docs/boot_analysis_methodology.md` |
| `ZK-INKJET-NANO-BOOT.bin` | `0x60` | Relocation helper that copies PC-relative vectors before branching to relocated entry (`bx r3`). | `data/processed/boot_static_notes.md`, `boot_disasm.txt` (methodology step 6) |
| `ZK-INKJET-NANO-BOOT.bin` | `0xF8` | Aligned memory copy routine (`memcpy`-style burst with residual handling). | `data/processed/boot_static_notes.md`, `boot_disasm.txt` (step 7) |
| `ZK-INKJET-NANO-BOOT.bin` | `0x210` | Unaligned memory copy variant using shifts to assemble words. | `data/processed/boot_static_notes.md` |
| `ZK-INKJET-NANO-BOOT.bin` | `0x348` | Division/modulo helper (`__aeabi_uidivmod` equivalent). | `data/processed/boot_static_notes.md` |
| `ZK-INKJET-NANO-BOOT.bin` | `0x52C` | Display command sequencer issuing T5L register writes (0x2A...0xE0). | `data/processed/boot_static_notes.md` |
| `ZK-INKJET-NANO-BOOT.bin` | `0x7C8` | Peripheral toggle: sets/clears bit 1 at `[base + 0x7C]` (likely watchdog/backlight). | `data/processed/boot_static_notes.md` |
| `VA 0x0021282C (file+0x0001282C)` | `VA 0x0021282C (file+0x0001282C)` | Format string for UI bitmap exports (`3:/inkjet-ui-%Y%m%d ... .bmp`). | `data/processed/app_strings_report.md` |
| `VA 0x0025D130 (file+0x0005D130)` | `VA 0x0025D130 (file+0x0005D130)` | Path reference to `0:/ZK-INKJET-RES-HW.zkml` (resource mount). | `data/processed/app_strings_report.md` |
| `VA 0x002688FC (file+0x000688FC)` | `VA 0x002688FC (file+0x000688FC)` | Reference to `3:/ZK-INKJET-NANO-BOOT.bin` (boot module load path). | `data/processed/app_strings_report.md` |
| `VA 0x003D3E00 (file+0x001D3E00)` | `VA 0x003D3E00 (file+0x001D3E00)` | Message handler table: `<handler_ptr, string_ptr, flag>` triples (12 bytes each). | `scripts/app_message_table.py` → `data/processed/app_message_table.json` |
| `ZK-INKJET-NANO-APP.bin` | `handler_ptr 0x2C2049 (Thumb) → VA 0x002C2048 (file+0x000C2048)` | Flag 2 status handler; decrements queue depth (`[base+0x144]`), writes the active index to `[base+0x14C]`, and loads the current display slot from `[base+idx*8+0x164]`. | `objdump --start-address=0xC1F60` (file+0x000C1F60), `docs/app_message_handlers.md` |
| `ZK-INKJET-NANO-APP.bin` | `handler_ptr 0x2C4525 (Thumb) → VA 0x002C4524 (file+0x000C4524)` | USB error handler; performs 8/16-byte memmoves to slide queue records, updates `[base]`/`[base+4]`, then copies the new entry into the freed slot. | `objdump --start-address=0xC4500` (file+0x000C4500), `docs/app_message_handlers.md` |
| `ZK-INKJET-NANO-APP.bin` | `handler_ptr 0x2C28D1 (Thumb) → VA 0x002C28D0 (file+0x000C28D0)` | Upgrade-found path; stages buffers through helpers at `0xC7018/0xC70F4/0xC7334`, then queues the notifier via `VA 0x002C61DC (file+0x000C61DC)`. | `objdump --start-address=0xC2880` (file+0x000C2880), `docs/app_message_handlers.md` |
| `VA 0x002C7018 (file+0x000C7018)` | `VA 0x002C7018 (file+0x000C7018)` | Part of bundled double-precision helper set (`__aeabi` style normalise/multiply) used by upgrade handler to compute glyph coordinates. | `objdump --start-address=0xC6FE0` (file+0x000C6FE0), `docs/app_message_handlers.md` |
| `VA 0x0028ACF0 (file+0x0008ACF0)` | `VA 0x0028ACF0 (file+0x0008ACF0)` | Resource selection routine: scans pointer tables, runs `memcmp` (`VA 0x0020E158 (file+0x0000E158)`) against file names, and prepares bitmap buffers before notifier runs. | `objdump --start-address=0x8AC80` (file+0x0008AC80), `docs/app_message_handlers.md` |
| `ZK-INKJET-NANO-APP.bin` | `handler_ptr handler_ptr 0x2C3A95 (Thumb) → VA 0x002C3A94 (file+0x000C3A94) → file 0xC3A94` | Flag 3 error handler (Thumb); rotates queue indices and calls helper `VA 0x00229D34 (file+0x00029D34)` before returning, used for “Openen mislukt...” strings. | `objdump --start-address=0xC3A80 -M force-thumb` (file+0x000C3A80), `docs/app_message_handlers.md` |
| `VA 0x0021138A (file+0x0001138A)` | `VA 0x0021138A (file+0x0001138A)` | Queue initialiser for the upgrade free-block list; allocates a 0x20-byte node when `[queue_ctrl]` is null and writes the head pointer back to the controller. | `objdump -M force-thumb --adjust-vma=0x211380 /tmp/queue_init.bin`, `docs/analysis_traceability.md` §19 |
| `VA 0x002113E4 (file+0x000113E4)` | `VA 0x002113E4 (file+0x000113E4)` | Accessor that returns the queue controller pointer (literal resolves to VA ≈ `VA 0x00244F8C (file+0x00044F8C)`). | `objdump -M force-thumb --adjust-vma=0x211380 /tmp/queue_init.bin`, `docs/analysis_traceability.md` §19 |
| `VA 0x00211A88 (file+0x00011A88)` | `VA 0x00211A88 (file+0x00011A88)` | Thumb routine that logs `\"direct: can't open\"` when SD/FAT access fails; wraps helper at `VA 0x00211A1E (file+0x00011A1E)`. | `objdump --start-address=0x11A80 -M force-thumb` (file+0x00011A80), `docs/storage_probe_notes.md` |
| `VA 0x00211AF8 (file+0x00011AF8)` | `VA 0x00211AF8 (file+0x00011AF8)` | Heap allocator helper (calls `VA 0x0020C798 (file+0x0000C798)`, zeroes new blocks) used by storage stack before issuing SD commands. | `objdump --start-address=0x11AF0 -M force-thumb` (file+0x00011AF0), `docs/storage_probe_notes.md` |
| `VA 0x00411AFC (file+0x00211AFC)` | `VA 0x00411AFC (file+0x00211AFC)` | Scratch-buffer allocator: reserves 0x88 bytes via `VA 0x0020C798 (file+0x0000C798)`, clears the first byte, and hands the buffer back to the queue node. | `objdump -M force-thumb --adjust-vma=0x211AF0 /tmp/queue_alloc.bin`, `docs/analysis_traceability.md` §19 |
| `VA 0x002BFC34 (file+0x000BFC34)` | `VA 0x002BFC34 (file+0x000BFC34)` | Flash writer reached only when caller `VA 0x002C1C10 (file+0x000C1C10)` sees a non-zero result from validator `VA 0x002BFDDC (file+0x000BFDDC)` (cmp at `VA 0x002C1C10 (file+0x000C1C10)`, call at `VA 0x002C1C1C (file+0x000C1C1C)`). | `objdump --adjust-vma=0x2C1B80 /tmp/flash_guard.bin`, `docs/analysis_traceability.md` §27 |
| `VA 0x00208592 (file+0x00008592)` | `VA 0x00208592 (file+0x00008592)` | Candidate queue-vtable callback (resolved from literal at `VA 0x004113CC (file+0x002113CC)`; stored pointer is `VA 0x00208593 (file+0x00008593)`, i.e., Thumb address). Exact behaviour unknown pending relocation/RAM dump. | `objdump -M force-thumb --adjust-vma=0x208580 /tmp/vtable_target.bin`, `docs/analysis_traceability.md` §19 |
| `VA 0x00444F8C (file+0x00244F8C)` | `VA 0x00444F8C (file+0x00244F8C)` | Queue controller block (`file+0x00044F8C`); first word stores the free-block head pointer returned by `VA 0x002113E4 (file+0x000113E4)`. | Thumb queue initialiser (`docs/analysis_traceability.md` §19) |
| `VA 0x002BFDDC (file+0x000BFDDC)` | `VA 0x002BFDDC (file+0x000BFDDC)` | Validator polled before flash writes; zero return skips the writer, non-zero lets caller `VA 0x002C1C10 (file+0x000C1C10)` drop into `VA 0x002BFC34 (file+0x000BFC34)`. | `objdump --adjust-vma=0x2C1B80 /tmp/flash_guard.bin`, `docs/analysis_traceability.md` §27, `docs/SESSION_HANDOFF.md` |
| `VA 0x00269385 (file+0x00069385)` | `queue_ctrl+0x8` | Controller slot patched at runtime with the default reader (`VA 0x00269385 (file+0x00069385)`, Thumb); invoked by `queue_prefill` whenever the one-shot override is empty. | `objdump -M force-thumb --adjust-vma=0x211356 /tmp/prefill.bin`, `objdump -M force-thumb --adjust-vma=0x269380 /tmp/default_prefill.bin`, `docs/SESSION_HANDOFF.md`, `docs/analysis_traceability.md` §26 |
| `ZK-INKJET-NANO-APP.bin` | `queue_ctrl+0x10` | One-shot prefill hook cleared during initialisation; writer still unknown and tracked in the open-issues list. | `objdump -M force-thumb --adjust-vma=0x211356 /tmp/prefill.bin`, `docs/SESSION_HANDOFF.md` |
| `VA 0x00429C80 (file+0x00229C80)` | `VA 0x00429C80 (file+0x00229C80)` | Reference-count helper for queue nodes; adjusts `[node+0x1C]` and returns the block to the allocator (`VA 0x00229D3C (file+0x00029D3C)`) when the count drops to zero. | `objdump -M force-thumb --adjust-vma=0x229C80 /tmp/queue_work.bin`, `docs/analysis_traceability.md` §19 |
| `VA 0x00429D78 (file+0x00229D78)` | `VA 0x00429D78 (file+0x00229D78)` | Bulk work/flush routine that prepares blocks, invokes user callbacks, and calls `queue_dispatch()` (`VA 0x00211366 (file+0x00011366)`). | `objdump -M force-thumb --adjust-vma=0x229C80 /tmp/queue_work.bin`, `docs/analysis_traceability.md` §19 |
| `ZK-INKJET-NANO-APP.bin` | `VA 0x0037E820 (file+0x0017E820)` | Literal table of upgrade filenames (`3:/ZK-INKJET-*.bin`); iterated by the filename matcher near `VA 0x00217DD0 (file+0x00017DD0)`. | `objdump --adjust-vma=0x37E820 /tmp/update_name_lit.bin`, `docs/update_file_rules.md` |
| `VA 0x0045A930 (file+0x0025A930)` | `VA 0x0045A930 (file+0x0025A930)` | memcmp loop over upgrade filename pool (`bl 0x20E158`); success drives upgrade-found path, failure falls toward `VA 0x002C47F0 (file+0x000C47F0)`. | `objdump --adjust-vma=0x25A900 /tmp/update_compare.bin`, `docs/update_file_rules.md` |
| `VA 0x0045A990 (file+0x0025A990)` | `VA 0x0045A990 (file+0x0025A990)` | Second memcmp loop (UI assets) referencing the same literal pool; same success/failure wiring as above. | `objdump --adjust-vma=0x25A900 /tmp/update_compare.bin`, `docs/update_file_rules.md` |
| `VA 0x0045A9F0 (file+0x0025A9F0)` | `VA 0x0045A9F0 (file+0x0025A9F0)` | Third memcmp loop (alternate UI package) tied into the upgrade-found / not-found handlers. | `objdump --adjust-vma=0x25A900 /tmp/update_compare.bin`, `docs/update_file_rules.md` |
| `VA 0x0027B61C (file+0x0007B61C)` | `VA 0x0027B61C (file+0x0007B61C)` | Filename classifier that lowercases the matched basename, checks the handler table, and selects the appropriate manifest builder. | `objdump --adjust-vma=0x27B61C /tmp/upgrade_classifier.bin`, `docs/analysis_traceability.md` §23 |
| `VA 0x0027BB80 (file+0x0007BB80)` | `VA 0x0027BB80 (file+0x0007BB80)` | Manifest builder enumerating per-component descriptors (offset/length/checksum slots) before queue dispatch. | `objdump --adjust-vma=0x27BB80 /tmp/manifest_builder.bin`, `docs/analysis_traceability.md` §23 |
| `VA 0x0027BCC0 (file+0x0007BCC0)` | `VA 0x0027BCC0 (file+0x0007BCC0)` | Callback installer writing reader/validator function pointers into the queue node. | `objdump --adjust-vma=0x27BCC0 /tmp/callback_installer.bin`, `docs/analysis_traceability.md` §23 |
| `VA 0x00416B78 (file+0x00216B78)` | `VA 0x00416B78 (file+0x00216B78)` | File I/O wrapper used by the queue worker and prospective RAM dump hook (open/write path). | traced via 0x25A930; candidate for dump_slice helper |
| `VA 0x00415C64 (file+0x00215C64)` | `VA 0x00415C64 (file+0x00215C64)` | Companion file wrapper (close/reset) used before queue dispatch and for dump finalisation. | traced via 0x25A930; candidate for dump_slice helper |
| `VA 0x0020EA7A (file+0x0000EA7A)` | `VA 0x0020EA7A (file+0x0000EA7A)` | Error stub: sets `r0=1`, calls the direct-open logger (`VA 0x002112F8 (file+0x000112F8)`), and returns. | `objdump --start-address=0xEA70 -M force-thumb` (file+0x0000EA70), `docs/storage_probe_notes.md` |
| `VA 0x0020EA5A (file+0x0000EA5A)` | `VA 0x0020EA5A (file+0x0000EA5A)` | Wrapper that prepares stack state, calls the buffered transfer routine, and propagates success/failure. | `objdump --start-address=0xEA58 -M force-thumb` (file+0x0000EA58), `docs/storage_probe_notes.md` |
| `VA 0x0020EA84 (file+0x0000EA84)` | `VA 0x0020EA84 (file+0x0000EA84)` | Buffered transfer routine; loops over `VA 0x00211356 (file+0x00011356)` buffer lookups, falls back to the error stub when resolution fails. | `objdump --start-address=0xEA80 -M force-thumb` (file+0x0000EA80), `docs/storage_probe_notes.md` |
| `VA 0x0020EAEC (file+0x0000EAEC)` | `VA 0x0020EAEC (file+0x0000EAEC)` | Upgrade orchestrator; walks the free-block list rooted at `[VA 0x00244F8C (file+0x00044F8C)]`, accumulates totals, bins block sizes by bit-width, calls `VA 0x00211B7C (file+0x00011B7C)` for the average, then dispatches the two logging callbacks with the `%d bytes ...` / `blocks 2^%d+1...` strings. | `data/processed/upgrade_orchestrator_disasm.txt`, `docs/analysis_traceability.md` §18 |
| `VA 0x0040EA5A (file+0x0020EA5A)` | `VA 0x0040EA5A (file+0x0020EA5A)` | Chunk prefetch loop that reserves buffer windows and copies spans delivered by the queue read callback. | `objdump -M force-thumb --adjust-vma=0x20EA5A /tmp/chunk_prefetch.bin`, `docs/analysis_traceability.md` §24 |
| `VA 0x002A17C8 (file+0x000A17C8)` | `VA 0x002A17C8 (file+0x000A17C8)` | Orchestrator callback that rebuilds the `"RR aA"` status banner, serialises `[ctx+0x18]`/`[ctx+0x1C]` into ASCII at `[ctx+0x228..0x22F]`, and pushes the line via the T5L helpers `VA 0x00248610 (file+0x00048610)` / `VA 0x00248504 (file+0x00048504)`; leaves `[ctx+3]` asserted when DMA fails. | `docs/analysis_traceability.md` §18, `docs/app_message_handlers.md` |
| `VA 0x004302EC (file+0x002302EC)` | `VA 0x004302EC (file+0x002302EC)` | Shared notifier routine invoked by handlers; allocates 0x200-byte buffer, clears flags at `[#0x1660]`, enqueues work via `bl 0x22714C (file+0x0002714C)` and other helpers for rendering. | `objdump --start-address=0x30200` (file+0x00030200) |
| `VA 0x00230E04 (file+0x00030E04)` | `VA 0x00230E04 (file+0x00030E04)` | Hardware update routine writing to registers at base `MMIO 0xB100D000` (via literal pool near `VA 0x00230F34 (file+0x00030F34)`); configures colour/geometry and toggles bit 0 to latch updates. | `objdump --start-address=0x30E00` |
| `VA 0x00411356 (file+0x00211356)` | `VA 0x00411356 (file+0x00211356)` | Queue prefill bridge; calls the controller vtable to pull the next sector before `memcpy` into the staging buffer. | `objdump -M force-thumb --adjust-vma=0x211356 /tmp/queue_prefill.bin`, `docs/analysis_traceability.md` §24 |
| `VA 0x0042C9E0 (file+0x0022C9E0)` | `VA 0x0042C9E0 (file+0x0022C9E0)` | Flash geometry/prolog routine invoked before programming validated upgrade chunks. | `objdump --adjust-vma=0x22C9E0 /tmp/flash_probe.bin`, `docs/analysis_traceability.md` §25 |
| `VA 0x0042CA18 (file+0x0022CA18)` | `VA 0x0042CA18 (file+0x0022CA18)` | Page-program loop that calls the SD/flash driver (`VA 0x002BC27C (file+0x000BC27C)`, `VA 0x002BFC34 (file+0x000BFC34)`) to commit the upgrade image (see guard at `VA 0x002C1C10 (file+0x000C1C10)`/`VA 0x002C1C1C (file+0x000C1C1C)`). | `objdump --adjust-vma=0x22CA18 /tmp/flash_program.bin`, `docs/analysis_traceability.md` §27 |
| `ZK-INKJET-RES-HW.zkml` | `file+0x000A3000` | Candidate header/chunk zone (entropy ≈5.71, ASCII≈21%). | `data/processed/reshw_probe_report.md`, sample `reshw_05_0xA3000.bin` |
| `ZK-INKJET-RES-HW.zkml` | `file+0x000B5000` | Candidate chunk region (similar statistics). | `data/processed/reshw_probe_report.md`, sample `reshw_04_0xB5000.bin` |
| `ZK-INKJET-RES-HW.zkml` | `file+0x000D7000` | Candidate chunk region (investigate for TOC entries). | `data/processed/reshw_probe_report.md`, sample `reshw_03_0xD7000.bin` |
| `ZK-INKJET-RES-HW.zkml` | `file+0x000EB000` | Candidate chunk region (aligned, medium entropy). | `data/processed/reshw_probe_report.md`, sample `reshw_02_0xEB000.bin` |
| `ZK-INKJET-RES-HW.zkml` | `file+0x0010A000` | Candidate chunk region (top-ranked by probe). | `data/processed/reshw_probe_report.md`, sample `reshw_01_0x10A000.bin` |
| `ZK-INKJET-RES-HW.zkml` | `file+0x00164000` | Candidate chunk region near end of file. | `data/processed/reshw_probe_report.md`, sample `reshw_06_0x164000.bin` |

### Evidence snippets

- **Queue controller – `VA 0x00244F8C (file+0x00044F8C)` (ARM)**  
  ```text
  00244f8c: e59d22e8  ldr r2, [sp, #744]
  00244f94: ebffb877  bl  0x233178
  00244fa0: e28d0fba  add r0, sp, #744
  00244fb8: ebffbdaf  bl  0x23467c
  ```

- **Shared notifier – `VA 0x002302EC (file+0x000302EC)` (ARM)**  
  ```text
  002302ec: e92d4fff  push {r0-r11, lr}
  002302f4: e59d02bc  ldr  r0, [sp, #700]
  00230304: e3500000  cmp  r0, #0
  00230318: eb023e74  bl   0x2bfcf0
  ```

- **Allocator helper – `VA 0x0020C798 (file+0x0000C798)` (Thumb)**  
  ```text
  0020c798: b570       push {r4, r5, r6, lr}
  0020c79c: f002 e94c  blx  0x20ea38
  0020c7a4: 300b       adds r0, #11
  0020c7aa: 42b4       cmp  r4, r6
  ```

_Add further offsets as soon as disassembly or probing reveals new actionable locations._
