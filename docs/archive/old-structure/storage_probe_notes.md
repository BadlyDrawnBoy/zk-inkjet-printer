# Storage Probe Notes

> [⤴ Back to archive overview](../README.md)




This note captures the first pass at identifying where the firmware performs SD / FAT operations during the upgrade workflow.

## Direct-Open Error Handler (`VA 0x00211A88 (file+0x00011A88)`, Thumb)
- Emits `"direct: can't open: "` and heap diagnostics (strings at `VA 0x00211AA0 (file+0x00011AA0)` and `VA 0x00211AC0 (file+0x00011AC0)`).
- Structure:
- Entry at `VA 0x00211A88 (file+0x00011A88)` pushes `r4, lr`, checks an argument flag, and calls a helper at `VA 0x00211A1E (file+0x00011A1E)`.
  ```text
  # Prologue placeholder: run
  #   objdump -D -b binary -marm -M force-thumb --adjust-vma=0x211A1C /tmp/storage_helper.bin
  # to capture the push/mov sequence for `VA 0x00211A1E (file+0x00011A1E)`.
  ```
  - When invoked with a non-zero mode, it branches to the heap error strings.
  - Likely a thin wrapper around the low-level direct-open routine or log handler that reacts when FAT open fails.

## Heap Utility Helpers (`VA 0x00211AF8 (file+0x00011AF8)` onwards)
- `VA 0x00211AF8 (file+0x00011AF8)` (`Thumb`) returns heap blocks by calling `VA 0x0020C798 (file+0x0000C798)` (allocator) and zeroes the first byte.
- `VA 0x00211B1E (file+0x00011B1E)` and `VA 0x00211B26 (file+0x00011B26)` handle small byte-flag bookkeeping around heap blocks (mark allocated/free).
- These helpers appear inlined around the storage functions above, suggesting the storage stack manages its own pool before talking to the SD driver.

## Function Table Dispatcher (`VA 0x00211B5A (file+0x00011B5A)`)
- Table-driven call loop; loads a list of function pointers and executes them in sequence.
- Potentially the init routine for the storage subsystem (e.g., FS registration, mount).

## Open/File Operation Candidates
- ASCII `"direct: can't open"` strongly hints at FATFS-style direct sector access. No explicit `f_open`/`f_read` strings were found, so the firmware likely uses a custom SD stack.
- Code blocks around `VA 0x00211B40 (file+0x00011B40)` (Thumb) implement chunked callback calls (`blx r7`), which resemble scatter/gather reads where a caller passes a callback to consume sector data.
- The `VA 0x00211B58 (file+0x00011B58)` dispatcher walks a pointer table; this could be the set of direct storage handlers (mount, read, write).
- Callers observed so far:
  - `VA 0x0020EA7A (file+0x0000EA7A)` (Thumb) is a minimal stub that injects the error message (`r0=1; bl 0x112F8`) and unwinds. Likely used when an earlier sanity check fails before touching the SD card.
  - `VA 0x0020EA84 (file+0x0000EA84)` (Thumb) performs buffered reads/writes. It repeatedly calls `VA 0x00211356 (file+0x00011356)` to resolve buffer descriptors; if the helper returns zero it falls through to the error stub above. When `VA 0x00211356 (file+0x00011356)` succeeds, the routine copies data via `VA 0x00210464 (file+0x00010464)` and advances through the file window.
  - `VA 0x0020EA5A (file+0x0000EA5A)` (Thumb) is the wrapper that prepares stack space and invokes the buffered routine (`VA 0x0020EA84 (file+0x0000EA84)`). Whenever `VA 0x0020EA84 (file+0x0000EA84)` reports success it returns `1`; on failure it bubbles up the error.
  - `VA 0x0020EAEC (file+0x0000EAEC)` (Thumb) orchestrates the full transfer. It allocates descriptor tables on the stack, iterates through entries, and delegates block operations to a callback (through `blx`). It calls both the wrapper (`VA 0x0020EA5A (file+0x0000EA5A)`) and the error stub, revealing the control hub for upgrade I/O.

## Next Actions
1. Trace callers of the `VA 0x00211A88 (file+0x00011A88)` error routine to identify the higher-level upgrade logic that decides which file to open.
2. Instrument the callback-style helper at `VA 0x00211B3E (file+0x00011B3E)` to determine which routines it dispatches to under upgrade conditions.
3. Locate the SD-card driver entry points by searching for register accesses around MMIO base `0xB0000000` within the same module.

Addresses above list both VA and `file+0x...` offsets; the APP base remains `0x00200000`.
