# APP Message Handler Notes

This memo captures the first round of disassembly notes for the handler routines referenced by the message table (`data/processed/app_message_table.json`). File offsets are shown as raw positions inside `data/raw/ZK-INKJET-NANO-APP.bin`; the corresponding load addresses can be recovered by adding `0X20_0000`.

## Observed Handlers

| Handler (file) | Flag | Message text (truncated) | Behaviour highlights |
|----------------|------|---------------------------|----------------------|
| `0XC2048` | 2 | “De update is voltooid en start automatisch opnieuw!” | Treats `[base+0X144]` as the queue depth (max 12 records). Uses a 0X66 666 667 multiply to recompute table indices, writes the new head index to `[base+0X14C]`, then pulls the target record pointer from `[base+index*8+0X164]`. Also clamps `[r7]` (current display slot) to the record’s VRAM pointer, guaranteeing the status banner shows the “update complete” message before exit. |
| `0XC47F0` | 1 | “Geen upgradebestand gevonden, probeer het opnieuw!” | Iterates over 0X14-byte records stored in the message queue, copying them into a contiguous run via `str/ldr` pairs. After compaction it recomputes the head pointer using the same divide-by-10 trick, updates `[r7,#4]` with the next slot pointer, and leaves the structure clean for the notifier. This routine effectively collapses duplicate/expired entries when no upgrade file is present. |
| `0XC4524` | 1 | “U disk of U disk format error!” (and string fragments) | Performs block moves in 8- and 16-byte strides to slide queue entries down. After the move it adjusts `[base]`/`[base+4]` to shrink the active window and copies one 8-byte record into the vacated slot (mirrors the routine used by `0XC47F0` but without the wider re-indexing). Flag 2 variants of the same text fall through this path, meaning USB errors bubble to the front of the queue immediately. |
| `0XC28D0` | 1 | “upgradebestand gevonden, probeer het opnieuw!” | Launches a deeper call chain through helper routines at `0XC7018`, `0XC70F4`, `0XC7334`, and `0XC61DC`. The sequence allocates a temporary work buffer, feeds two struct copies into `0X8ACF0`, and revisits the notifier `0X2302EC (file+0X302EC)`. This path appears to initialise the upgrade job: it stages the USB metadata and schedules the rendering pipeline once a valid update file is detected. |
| `0XC3A94` | 3 | “Openen mislukt, probeer het opnieuw!” | Marked with flag 3 (the rarest bucket). Disassembly (Thumb mode) shows this is a thin wrapper that calls a shared error helper before returning. It is reached after the deeper upgrade handler fails to open a file descriptor. |

Additional flag 2 entries (`0XC4118`, `0XC3D04`, etc.) share the same structural code as `0XC2048`, reusing the queue-maintenance helpers to prioritise their status messages.

### Support Routines

- `0XA17C8` (ARM) – primary upgrade-status formatter invoked by the orchestrator callbacks. Treats `r0` as a 0X240-byte UI buffer, clears `[base+3]` when capacity checks pass, writes the `"RR"`/`"aA"` banner prefix, serialises the 32-bit counters from `[base+0X18]`/`[base+0X1C]` into ASCII bytes at `[base+0X228..0X22F]`, bumps `[base+0X3C]`, and calls `0X48610` / `0X48504` to push the line to the T5L display. When those helpers fail it leaves `[base+3]` asserted so the UI can retry.
- `VA 0X208592 (file+0X8592)` (Thumb pointer stored via literal at `0X2113CC`) – **relocation placeholder**. In the raw image the literal pool entries at `0X2113CC/0X2113D0` are zero; the loader patches them at runtime. A 256-byte dump around this VA shows only relocation padding, so the actual instructions and calling convention remain unknown until we can capture a RAM image. Expect this vtable slot to point at the queue-processing callback that eventually invokes `0X211430`.

### Upgrade Helper Chain

When handler `0XC28D0` detects a valid upgrade file it cascades through several shared helpers before the shared notifier runs:

- `0XC7018`, `0XC70F4`, `0XC7334`, `0XC61DC` — these are the firmware’s bundled `__aeabi` double helpers (normalisation, multiply, compare, floor). They are used to scale image-space coordinates and clamp iteration counts while rebuilding the message bitmap.
- `0XC6CA0` / `0XC6D04` — convert intermediate double values back into integer indices for the glyph bitmaps that back the on-screen status banner.
- `0X8ACF0` — large formatter that walks resource tables (`0X244664`, `0X2471C0`, `0X2474B8`) and performs repeated `memcmp` (`0XE158`) lookups; this aligns icon/text assets with the detected upgrade file name before the screen update.
- `0X5E92C` — bitplane blitter that flips per-pixel flags in the UI buffer (observed writes to `[base+0X678..0X684]` and `0X67C`).

The chain confirms that the “upgrade found” path does not immediately talk to storage; instead it prepares UI state and defers actual file access to downstream code that reuses these buffers.

## Command Snippets

Decode any handler with:
```bash
objdump -b binary -m armv7 -D \
  --start-address=0XC2000 --stop-address=0XC2140 data/raw/ZK-INKJET-NANO-APP.bin | less  # file+0XC2000..0XC2140
```
Switch to Thumb when ARM output looks nonsensical:
```bash
objdump -b binary -m armv7 -M force-thumb -D \
  --start-address=0XC3A80 --stop-address=0XC3AF0 data/raw/ZK-INKJET-NANO-APP.bin  # file+0XC3A80..0XC3AF0
```

## Next Focus

1. Follow the helper routines invoked by `0XC28D0` (`0XC7018`, `0XC70F4`, `0XC7334`, `0XC61DC`) to identify the file I/O strategy used for upgrades.
2. Instrument the notifier at `VA 0X2302EC (file+0X302EC)` to confirm when flag 2 vs flag 3 entries are displayed and whether additional status bytes are toggled.
3. Cross-reference the queue offsets (`0X144`, `0X14C`, `0X164`, `0X7D8`) with runtime RAM dumps to map the full structure for message injection.
