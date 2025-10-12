# Firmware Update File Rules

This note captures the current evidence for how the firmware discovers upgrade images on the removable volume. File offsets refer to `data/raw/ZK-INKJET-NANO-APP.bin`.

## Enumerated `.bin` strings

| Offset | Volume | Text |
|--------|--------|------|
| `file+0X688FC` | `3:/` | `3:/ZK-INKJET-NANO-BOOT.bin` |
| `file+0X6891C` | `3:/` | `3:/ZK-INKJET-NANO-APP.bin` |
| `file+0X6CAD8` | `3:/` | `3:/ZK-INKJET-UI-QVGA.bin` |
| `file+0X6CFE0` | `3:/` | `3:/ZK-INKJET-TINY-BOOT.bin` |
| `file+0X6CFFC` | `3:/` | `3:/ZK-INKJET-PUNY-BOOT.bin` |
| `file+0X6D018` | `3:/` | `3:/ZK-INKJET-NANO-BOOT.bin` (duplicate literal) |
| `file+0X6D034` | `3:/` | `3:/ZK-INKJET-UI.bin` |
| `file+0X6D048` | `3:/` | `3:/ZK-INKJET-UI-QVGA.bin` (secondary copy) |
| `file+0X6D064` | `3:/` | `3:/ZK-TIJSPS-800X480-UI.bin` |

All upgrade literals live on `3:/` (the U-disk). No upgrade `.bin` strings are present under `0:/`; that tree is reserved for fonts/resources (`*.ttf`, `*.zkml`).

## Literal tables and compare loops

* **Pointer pool – `VA 0X217E820 (file+0X17E820)`**  
  The addresses above are collated into a literal table starting at this VA. The helper at `VA 0X217DD0 (file+0X17DD0)` iterates this pool and pushes candidate pointers into the worker routines.

* **memcmp helper – `VA 0X20E158 (file+0XE158)`**  
  Relevant callers (all ARM mode) loop over the pointer pool and compare against device-generated filenames:
  * `VA 0X25A930 (file+0X5A930)` → success path falls through to the upgrade-found chain; failure branches to `VA 0X25AA54 (file+0X5AA54)`, eventually triggering handler `VA 0X2C47F0 (file+0XC47F0)` (“Geen upgradebestand…”).
  * `VA 0X25A990 (file+0X5A990)` and `VA 0X25A9F0 (file+0X5A9F0)` → second/third loops for UI assets. Their failure exits (`VA 0X25AA5C (file+0X5AA5C)`, `VA 0X25AA64 (file+0X5AA64)`) also roll into the not-found handler.
  * Each loop indexes a pointer array near `VA 0X25AA70 (file+0X5AA70)`. Those arrays contain little-endian VAs that point back into the literal pool (e.g. entry `VA 0X37E830 (file+0X17E830)` → `VA 0X2688FC (file+0X688FC)` → `"3:/ZK-INKJET-NANO-BOOT.bin"`).

* **Handler linkages**  
  * Matches from the loops feed the queue node consumed by handler `VA 0X2C28D0 (file+0XC28D0)` (upgrade-found path).
  * Exhausting every entry without a match enqueues the “not found” message via handler `VA 0X2C47F0 (file+0XC47F0)`.

## Practical rule

* **Volume:** `3:/` (external U-disk). The device never consults `0:/` for firmware binaries.
* **Directory:** root of the volume. Comparisons are performed on bare filenames; subdirectories are not considered.
* **Case sensitivity:** filenames are stored in lower case and compared byte-for-byte via `memcmp` – keep exact casing.
* **Accepted filenames:**
  * `ZK-INKJET-NANO-BOOT.bin`
  * `ZK-INKJET-NANO-APP.bin`
  * `ZK-INKJET-UI.bin`
  * `ZK-INKJET-UI-QVGA.bin`
  * `ZK-TIJSPS-800X480-UI.bin` (alternate UI package)
  * Legacy names `ZK-INKJET-TINY-BOOT.bin`, `ZK-INKJET-PUNY-BOOT.bin` remain in the list for backward compatibility.

### Example stick layout

```
3:/
 ├─ ZK-INKJET-NANO-BOOT.bin
 ├─ ZK-INKJET-NANO-APP.bin
 ├─ ZK-INKJET-UI.bin
 ├─ ZK-INKJET-UI-QVGA.bin
 └─ (optional) ZK-TIJSPS-800X480-UI.bin
```

## Cross-reference trail

* `grep -n "\.bin" data/processed/app_strings_report.md` – reproduces the offsets above.
* `objdump -D -b binary -marm --adjust-vma=0X217E820 /tmp/update_name_lit.bin` – shows the literal pool of filename pointers.
* `objdump -D -b binary -marm --adjust-vma=0X25A900 /tmp/update_compare.bin` – displays the memcmp loops at `VA 0X25A930 / 0X25A990 / 0X25A9F0`.
* `objdump -D -b binary -marm --adjust-vma=0X2C2800 /tmp/found_handler.bin` – verifies that the successful branch ultimately drives handler `VA 0X2C28D0 (file+0XC28D0)`.
* `objdump -D -b binary -marm --adjust-vma=0X2C4700 /tmp/notfound_handler.bin` – confirms the failure branch ends in handler `VA 0X2C47F0 (file+0XC47F0)`.

Keep these references in sync as additional filenames or directories surface.

## Upgrade pipeline (match → apply)

Observed control flow after a filename matches the literal pool:

```
match = scan_update_candidates()        # VA 0X25A930 / 0X25A990 / 0X25A9F0
descriptor = classify_basename(match)   # VA 0X27B61C normalises name, picks handler
chunks    = build_manifest(descriptor)  # VA 0X27BB80 flattens pointer tables
slots     = install_callbacks(chunks)   # VA 0X27BCC0 fills queue node with readers
queue_dispatch()                        # VA 0X229D78 packages work items
for block in orchestrate(queue):        # VA 0X20EAEC histogram/dispatch loop
    buf = reserve_window(block)         # VA 0X20EA5A prefetch via queue prefill
    while buf.has_room():
        span = dequeue_sector(buf)      # VA 0X211356 → callback in queue vtable
        copy_into(buf, span)            # VA 0X210464 memcpy-style mover
    if validator(buf):                  # VA 0X27B61C / 0X27BB80 CRC & size guards
        program_target(buf)             # VA 0X22C9E0 / 0X22CA18 flash writer
```

* `scan_update_candidates()` – the three `memcmp` loops at `VA 0X25A930`, `0X25A990`, `0X25A9F0` walk the literal pool and capture hits into temporary pointer arrays.
* `classify_basename()` – `VA 0X27B61C` lowercases the match, checks dispatch tables, and selects the correct manifest builder (UI vs firmware).
* `build_manifest()` – `VA 0X27BB80` emits the per-component descriptor list (file offsets, lengths, checksum slots) expected by the queue worker.
* `install_callbacks()` – `VA 0X27BCC0` writes reader/validator entry points into the queue node so that later stages can call through the controller vtable.
* `reserve_window()` / `dequeue_sector()` – the prefill loop at `VA 0X20EA5A` pulls scratch buffers from `queue_prefill()` (`VA 0X211356`) which in turn invokes the installed open/read helper. When the helper exhausts the file it triggers the error stub at `VA 0X20EA7A`.
* `program_target()` – once a buffer passes the validator, the worker hands it to the flash writer family rooted at `VA 0X22C9E0` (`geometry probe`) and `VA 0X22CA18` (`page program loop`) before releasing the queue node.

**Flash programming is reached only when caller `0X2C1C10` (cmp) / `0X2C1C1C` (bl) sees a non-zero result from validator `0X2BFDDC` (docs/analysis_traceability.md §27).**

These observations are derived from linear disassembly (see `docs/analysis_traceability.md` §22+ for exact reproduction commands).
