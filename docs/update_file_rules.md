# Firmware Update File Rules

This note captures the current evidence for how the firmware discovers upgrade images on the removable volume. File offsets refer to `data/raw/ZK-INKJET-NANO-APP.bin`.

## Enumerated `.bin` strings

| Offset | Volume | Text |
|--------|--------|------|
| `file+0x000688FC` | `3:/` | `3:/ZK-INKJET-NANO-BOOT.bin` |
| `file+0x0006891C` | `3:/` | `3:/ZK-INKJET-NANO-APP.bin` |
| `file+0x0006CAD8` | `3:/` | `3:/ZK-INKJET-UI-QVGA.bin` |
| `file+0x0006CFE0` | `3:/` | `3:/ZK-INKJET-TINY-BOOT.bin` |
| `file+0x0006CFFC` | `3:/` | `3:/ZK-INKJET-PUNY-BOOT.bin` |
| `file+0x0006D018` | `3:/` | `3:/ZK-INKJET-NANO-BOOT.bin` (duplicate literal) |
| `file+0x0006D034` | `3:/` | `3:/ZK-INKJET-UI.bin` |
| `file+0x0006D048` | `3:/` | `3:/ZK-INKJET-UI-QVGA.bin` (secondary copy) |
| `file+0x0006D064` | `3:/` | `3:/ZK-TIJSPS-800x480-UI.bin` |

All upgrade literals live on `3:/` (the U-disk). No upgrade `.bin` strings are present under `0:/`; that tree is reserved for fonts/resources (`*.ttf`, `*.zkml`).

## Literal tables and compare loops

* **Pointer pool – `VA 0x0037E820 (file+0x0017E820)`**  
  The addresses above are collated into a literal table starting at this VA. The helper at `VA 0x00217DD0 (file+0x00017DD0)` iterates this pool and pushes candidate pointers into the worker routines. Updated per objdump evidence below.

  *Evidence (objdump, ARM)*:

  ```text
  0037e820: 00267e1c
  0037e824: 002680d4
  0037e828: 0026838c
  0037e82c: 00268644
  0037e830: 002688fc
  0037e834: 00268bb4
  0037e838: 00268e6c
  0037e83c: 00269124
  ```

* **memcmp helper – `VA 0x0020E158 (file+0x0000E158)`**  
  Relevant callers (all ARM mode) loop over the pointer pool and compare against device-generated filenames. The windows below show each loop calling `VA 0x0020E158 (file+0x0000E158)` then branching to the success/failure handlers.

  *Evidence (objdump, ARM)*:

  ```text
  0025a930: ebfece08  bl  0x20e158
  0025a934: e3500000  cmp r0, #0
  0025a938: 0a000045  beq 0x25aa54
  0025a990: ebfecdf0  bl  0x20e158
  0025a994: e3500000  cmp r0, #0
  0025a998: 0a00002f  beq 0x25aa5c
  0025a9f0: ebfecdd8  bl  0x20e158
  0025a9f4: e3500000  cmp r0, #0
  0025a9f8: 0a000019  beq 0x25aa64
  ```
  * `VA 0x0025A930 (file+0x0005A930)` → success path falls through to the upgrade-found chain; failure branches to `VA 0x0025AA54 (file+0x0005AA54)`, eventually triggering handler `VA 0x002C47F0 (file+0x000C47F0)` (“Geen upgradebestand...”).
  * `VA 0x0025A990 (file+0x0005A990)` and `VA 0x0025A9F0 (file+0x0005A9F0)` → second/third loops for UI assets. Their failure exits (`VA 0x0025AA5C (file+0x0005AA5C)`, `VA 0x0025AA64 (file+0x0005AA64)`) also roll into the not-found handler.
  * Each loop indexes a pointer array near `VA 0x0025AA70 (file+0x0005AA70)`. Those arrays contain little-endian VAs that point back into the literal pool (e.g. entry `VA 0x0037E830 (file+0x0017E830)` → `VA 0x002688FC (file+0x000688FC)` → `"3:/ZK-INKJET-NANO-BOOT.bin"`).

* **Handler linkages**  
  * Matches from the loops feed the queue node consumed by handler `VA 0x002C28D0 (file+0x000C28D0)` (upgrade-found path).
  * Exhausting every entry without a match enqueues the “not found” message via handler `VA 0x002C47F0 (file+0x000C47F0)`.

## Practical rule

* **Volume:** `3:/` (external U-disk). The device never consults `0:/` for firmware binaries.
* **Directory:** root of the volume. Comparisons are performed on bare filenames; subdirectories are not considered.
* **Case sensitivity:** filenames are stored in lower case and compared byte-for-byte via `memcmp` – keep exact casing.
* **Accepted filenames:**
  * `ZK-INKJET-NANO-BOOT.bin`
  * `ZK-INKJET-NANO-APP.bin`
  * `ZK-INKJET-UI.bin`
  * `ZK-INKJET-UI-QVGA.bin`
  * `ZK-TIJSPS-800x480-UI.bin` (alternate UI package)
  * Legacy names `ZK-INKJET-TINY-BOOT.bin`, `ZK-INKJET-PUNY-BOOT.bin` remain in the list for backward compatibility.

### Example stick layout

```
3:/
 ├─ ZK-INKJET-NANO-BOOT.bin
 ├─ ZK-INKJET-NANO-APP.bin
 ├─ ZK-INKJET-UI.bin
 ├─ ZK-INKJET-UI-QVGA.bin
 └─ (optional) ZK-TIJSPS-800x480-UI.bin
```

## Cross-reference trail

* `grep -n "\.bin" data/processed/app_strings_report.md` – reproduces the offsets above.
* `objdump -D -b binary -marm --adjust-vma=0x37E820 /tmp/update_name_lit.bin` – shows the literal pool of filename pointers.
* `objdump -D -b binary -marm --adjust-vma=0x25A900 /tmp/update_compare.bin` – displays the memcmp loops at `VA 0x0025A930 (file+0x0005A930)`, `VA 0x0025A990 (file+0x0005A990)`, and `VA 0x0025A9F0 (file+0x0005A9F0)`.
* `objdump -D -b binary -marm --adjust-vma=0x2C2800 /tmp/found_handler.bin` – verifies that the successful branch ultimately drives handler `VA 0x002C28D0 (file+0x000C28D0)`.
* `objdump -D -b binary -marm --adjust-vma=0x2C4700 /tmp/notfound_handler.bin` – confirms the failure branch ends in handler `VA 0x002C47F0 (file+0x000C47F0)`.

Keep these references in sync as additional filenames or directories surface.

## Upgrade pipeline (match → apply)

Observed control flow after a filename matches the literal pool:

```
match = scan_update_candidates()        # VA 0x0025A930 (file+0x0005A930) / VA 0x0025A990 (file+0x0005A990) / VA 0x0025A9F0 (file+0x0005A9F0)
descriptor = classify_basename(match)   # VA 0x0027B61C (file+0x0007B61C) normalises name, picks handler
chunks    = build_manifest(descriptor)  # VA 0x0027BB80 (file+0x0007BB80) flattens pointer tables
slots     = install_callbacks(chunks)   # VA 0x0027BCC0 (file+0x0007BCC0) fills queue node with readers
queue_dispatch()                        # VA 0x00229D78 (file+0x00029D78) packages work items
for block in orchestrate(queue):        # VA 0x0020EAEC (file+0x0000EAEC) histogram/dispatch loop
    buf = reserve_window(block)         # VA 0x0020EA5A (file+0x0000EA5A) prefetch via queue prefill
    while buf.has_room():
        span = dequeue_sector(buf)      # VA 0x00211356 (file+0x00011356) → callback in queue vtable
        copy_into(buf, span)            # VA 0x00210464 (file+0x00010464) memcpy-style mover
    if validator(buf):                  # VA 0x0027B61C (file+0x0007B61C) / VA 0x0027BB80 (file+0x0007BB80) CRC & size guards
        program_target(buf)             # VA 0x0022C9E0 (file+0x0002C9E0) / VA 0x0022CA18 (file+0x0002CA18) flash writer
```

* `scan_update_candidates()` – the three `memcmp` loops at `VA 0x0025A930 (file+0x0005A930)`, `VA 0x0025A990 (file+0x0005A990)`, and `VA 0x0025A9F0 (file+0x0005A9F0)` walk the literal pool and capture hits into temporary pointer arrays.
* `classify_basename()` – `VA 0x0027B61C (file+0x0007B61C)` lowercases the match, checks dispatch tables, and selects the correct manifest builder (UI vs firmware).
* `build_manifest()` – `VA 0x0027BB80 (file+0x0007BB80)` emits the per-component descriptor list (file offsets, lengths, checksum slots) expected by the queue worker.
* `install_callbacks()` – `VA 0x0027BCC0 (file+0x0007BCC0)` writes reader/validator entry points into the queue node so that later stages can call through the controller vtable.
* `reserve_window()` / `dequeue_sector()` – the prefill loop at `VA 0x0020EA5A (file+0x0000EA5A)` pulls scratch buffers from `queue_prefill()` (`VA 0x00211356 (file+0x00011356)`) which in turn invokes the installed open/read helper. When the helper exhausts the file it triggers the error stub at `VA 0x0020EA7A (file+0x0000EA7A)`.
* `program_target()` – once a buffer passes the validator, the worker hands it to the flash writer family rooted at `VA 0x0022C9E0 (file+0x0002C9E0)` (`geometry probe`) and `VA 0x0022CA18 (file+0x0002CA18)` (`page program loop`) before releasing the queue node.

**Flash programming is reached only when caller `VA 0x002C1C10 (file+0x000C1C10)` (cmp) / `VA 0x002C1C1C (file+0x000C1C1C)` (bl) sees a non-zero result from validator `VA 0x002BFDDC (file+0x000BFDDC)` (docs/analysis_traceability.md §27).**

These observations are derived from linear disassembly (see `docs/analysis_traceability.md` §22+ for exact reproduction commands).

### Evidence windows

- **Orchestrator – `VA 0x0020EAEC (file+0x0000EAEC)` (Thumb)** – loop initialises slot table before iterating queue blocks.

  ```text
  0020eaec: b5f7  push {r0, r1, r2, r4, r5, r6, r7, lr}
  0020eaee: 2500  movs r5, #0
  0020eaf0: 002f  movs r7, r5
  0020eaf4: 0028  movs r0, r5
  0020eaf6: b0a2  sub  sp, #136
  0020eafa: ae02  add  r6, sp, #8
  0020eafe: 1c40  adds r0, r0, #1
  0020eb00: 2820  cmp  r0, #32
  ```

- **Prefetch loop – `VA 0x0020EA5A (file+0x0000EA5A)` (Thumb)** – pulls sectors via queue callback then copies spans.

  ```text
  0020ea5a: 0004  movs r4, r0
  0020ea5e: 4669  mov  r1, sp
  0020ea62: f002 fc78  bl  0x211356
  0020ea68: d005  beq.n 0x20ea76
  0020ea70: f001 fcf8  bl  0x210464
  0020ea74: 2001  movs r0, #1
  ```

- **Queue prefill bridge – `VA 0x00211356 (file+0x00011356)` (Thumb)** – dispatches vtable callback and ensures node initialisation.

  ```text
  00211356: b510       push {r4, lr}
  00211358: f01b eb42  blx  0x22c9e0
  0021135e: b510       push {r4, lr}
  00211360: f000 f801  bl   0x211366
  0021136c: 6901       ldr  r1, [r0, #16]
  00211370: d003       beq.n 0x21137a
  ```

- **Memcpy-style mover – `VA 0x00210464 (file+0x00010464)` (Thumb)** – walks descriptor list and copies spans when the callback succeeds.

  ```text
  00210464: b510  push {r4, lr}
  00210468: 6840  ldr  r0, [r0, #4]
  00210470: 2800  cmp  r0, #0
  00210474: d001  beq.n 0x210478
  00210478: 6818  ldr  r0, [r3, #0]
  0021047c: 428b  cmp  r3, r1
  ```

- **Queue dispatch – `VA 0x00229D78 (file+0x00029D78)` (Thumb)** – multiplies slot count, optional callback via BLX.

  ```text
  00229d78: 2001  movs r0, #1
  00229d7e: 9802  ldr  r0, [sp, #8]
  00229d82: 4346  muls r6, r0
  00229d88: 9c03  ldr  r4, [sp, #12]
  00229d8e: d003  beq.n 0x229d98
  00229d92: 4788  blx  r1
  ```

- **Validator – `VA 0x002BFDDC (file+0x000BFDDC)` (ARM)** – stores last-success pointer and compares status bytes.

  ```text
  002bfddc: e59f1034  ldr r1, [pc, #52]
  002bfde4: e5913020  ldr r3, [r1, #32]
  002bfdec: e5810020  str r0, [r1, #32]
  002bfdf4: e35c0000  cmp ip, #0
  002bfe04: e1520000  cmp r2, r0
  ```

- **Flash writer probe – `VA 0x0022C9E0 (file+0x0002C9E0)` (ARM)** – checks geometry before arming the writer buffers.

  ```text
  0022c9e0: e92d4070  push {r4, r5, r6, lr}
  0022c9ec: eb01d4b1  bl   0x2a1cb8
  0022c9f4: 1a000005  bne  0x22ca10
  0022c9f8: e3540506  cmp  r4, #0x1800000
  0022ca04: e5850000  str  r0, [r5]
  ```

- **Flash page program – `VA 0x0022CA18 (file+0x0002CA18)` (ARM)** – validates buffers before branching into the write loop.

  ```text
  0022ca18: e92d4ff0  push {r4, r5, r6, r7, r8, r9, sl, fp, lr}
  0022ca24: e24dd014  sub  sp, sp, #20
  0022ca2c: 13500000  cmpne r0, #0
  0022ca38: e3510000  cmp  r1, #0
  0022ca40: e5940044  ldr  r0, [r4, #68]
  ```

- **Writer guard – `VA 0x002C1C10 (file+0x000C1C10)` (ARM)** – `cmp` of validator result and `bl` into the flash writer.

  ```text
  002c1c10: e3570000  cmp r7, #0
  002c1c18: 01a0000b  moveq r0, fp
  002c1c1c: ebfff804  bl  0x2bfc34
  002c1c28: ebfff86b  bl  0x2bfddc
  002c1c30: e5940020  ldr r0, [r4, #32]
  ```
