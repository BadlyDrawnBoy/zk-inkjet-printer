# Storage Probe Notes

This note captures the first pass at identifying where the firmware performs SD / FAT operations during the upgrade workflow.

## Direct-Open Error Handler (`0X11A88`, Thumb)
- Emits `"direct: can't open: "` and heap diagnostics (strings at `0X11AA0` and `0X11AC0`).
- Structure:
- Entry at `0X11A88` pushes `r4, lr`, checks an argument flag, and calls a helper at `VA 0X211A1E (file+0X11A1E)`.
  - When invoked with a non-zero mode, it branches to the heap error strings.
  - Likely a thin wrapper around the low-level direct-open routine or log handler that reacts when FAT open fails.

## Heap Utility Helpers (`0X11AF8` onwards)
- `0X11AF8` (`Thumb`) returns heap blocks by calling `VA 0X20C798 (file+0XC798)` (allocator) and zeroes the first byte.
- `0X11B1E` and `0X11B26` handle small byte-flag bookkeeping around heap blocks (mark allocated/free).
- These helpers appear inlined around the storage functions above, suggesting the storage stack manages its own pool before talking to the SD driver.

## Function Table Dispatcher (`0X11B5A`)
- Table-driven call loop; loads a list of function pointers and executes them in sequence.
- Potentially the init routine for the storage subsystem (e.g., FS registration, mount).

## Open/File Operation Candidates
- ASCII `"direct: can't open"` strongly hints at FATFS-style direct sector access. No explicit `f_open`/`f_read` strings were found, so the firmware likely uses a custom SD stack.
- Code blocks around `0X11B40` (Thumb) implement chunked callback calls (`blx r7`), which resemble scatter/gather reads where a caller passes a callback to consume sector data.
- The `0X11B58` dispatcher walks a pointer table; this could be the set of direct storage handlers (mount, read, write).
- Callers observed so far:
  - `0XEA7A` (Thumb) is a minimal stub that injects the error message (`r0=1; bl 0X112F8`) and unwinds. Likely used when an earlier sanity check fails before touching the SD card.
  - `0XEA84` (Thumb) performs buffered reads/writes. It repeatedly calls `0X11356` to resolve buffer descriptors; if the helper returns zero it falls through to the error stub above. When `0X11356` succeeds, the routine copies data via `0X10464` and advances through the file window.
  - `0XEA5A` (Thumb) is the wrapper that prepares stack space and invokes the buffered routine (`0XEA84`). Whenever `0XEA84` reports success it returns `1`; on failure it bubbles up the error.
  - `0XEAEC` (Thumb) orchestrates the full transfer. It allocates descriptor tables on the stack, iterates through entries, and delegates block operations to a callback (through `blx`). It calls both the wrapper (`0XEA5A`) and the error stub, revealing the control hub for upgrade I/O.

## Next Actions
1. Trace callers of the `0X11A88` error routine to identify the higher-level upgrade logic that decides which file to open.
2. Instrument the callback-style helper at `0X11B3E` to determine which routines it dispatches to under upgrade conditions.
3. Locate the SD-card driver entry points by searching for register accesses around base `0XB0000000` within the same module.

All addresses above are file offsets; add `0X20_0000` to convert to load addresses.
