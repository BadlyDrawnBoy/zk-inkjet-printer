# APP Message Handler Notes

This memo captures the current disassembly notes for the handler routines referenced by the message table (`data/processed/app_message_table.json`). File offsets are shown as raw positions inside `data/raw/ZK-INKJET-NANO-APP.bin`; the corresponding load addresses can be recovered by adding `0x20_0000`. Treat this as an analysis log; verified summaries belong in the findings.

## Observed Handlers

| Handler (file) | Flag | Message text (truncated) | Behaviour highlights |
|----------------|------|---------------------------|----------------------|
| `VA 0x002C2048 (file+0x000C2048)` | 2 | “De update is voltooid en start automatisch opnieuw!” | Queue maintenance and banner display for “update complete”; clamps queue indices and forces the status banner to show the record’s VRAM pointer. |
| `VA 0x002C47F0 (file+0x000C47F0)` | 1 | “Geen upgradebestand gevonden, probeer het opnieuw!” | Compacts 0x14-byte queue records, recomputes the head pointer, and cleans up the message queue when no upgrade file is present. |
| `VA 0x002C4524 (file+0x000C4524)` | 1 | “U disk of U disk format error!” (and string fragments) | Slides queue entries down in 8-/16-byte strides, shrinks the active window, and bubbles USB errors to the front of the queue. |
| `VA 0x002C28D0 (file+0x000C28D0)` | 1 | “upgradebestand gevonden, probeer het opnieuw!” | Stages UI state and metadata after an upgrade name match; calls formatter helpers and the notifier (`VA 0x002302EC`). No checksum/hash logic observed here. |
| `VA 0x002C3A94 (file+0x000C3A94)` | 3 | “Openen mislukt, probeer het opnieuw!” | Thin wrapper calling the shared error helper when file open fails. |

Additional flag 2 entries (`VA 0x002C4118 (file+0x000C4118)`, `VA 0x002C3D04 (file+0x000C3D04)`, etc.) share the same structural code as `VA 0x002C2048 (file+0x000C2048)`, reusing the queue-maintenance helpers to prioritise their status messages.

### Support Routines

- `VA 0x002A17C8 (file+0x000A17C8)` (ARM) – primary upgrade-status formatter invoked by the orchestrator callbacks. Treats `r0` as a 0x240-byte UI buffer, clears `[base+3]` when capacity checks pass, writes the `"RR"`/`"aA"` banner prefix, serialises the 32-bit counters from `[base+0x18]`/`[base+0x1C]` into ASCII bytes at `[base+0x228..0x22F]`, bumps `[base+0x3C]`, and calls `VA 0x00248610 (file+0x00048610)` / `VA 0x00248504 (file+0x00048504)` to push the line to the display controller (N32903 @ `0xB100D000`). When those helpers fail it leaves `[base+3]` asserted so the UI can retry.
- `VA 0x00208592 (file+0x00008592)` (Thumb pointer stored via literal at `VA 0x002113CC (file+0x000113CC)`) – **relocation placeholder / unresolved**. In the raw image the literal pool entries at `0x2113CC/0x2113D0` are zero; the loader patches them at runtime. Without a RAM dump this vtable slot remains unknown; likely a queue-processing callback that eventually invokes `VA 0x00211430 (file+0x00011430)`.

### Upgrade Helper Chain

When handler `VA 0x002C28D0 (file+0x000C28D0)` detects a valid upgrade file it cascades through several shared helpers before the shared notifier runs:

- `VA 0x002C7018 (file+0x000C7018)`, `VA 0x002C70F4 (file+0x000C70F4)`, `VA 0x002C7334 (file+0x000C7334)`, `VA 0x002C61DC (file+0x000C61DC)` — these are the firmware’s bundled `__aeabi` double helpers (normalisation, multiply, compare, floor). They are used to scale image-space coordinates and clamp iteration counts while rebuilding the message bitmap.
- `VA 0x002C6CA0 (file+0x000C6CA0)` / `VA 0x002C6D04 (file+0x000C6D04)` — convert intermediate double values back into integer indices for the glyph bitmaps that back the on-screen status banner.
- `VA 0x0028ACF0 (file+0x0008ACF0)` — large formatter that walks resource tables (`VA 0x00244664 (file+0x00044664)`, `VA 0x002471C0 (file+0x000471C0)`, `VA 0x002474B8 (file+0x000474B8)`) and performs repeated `memcmp` (`VA 0x0020E158 (file+0x0000E158)`) lookups; this aligns icon/text assets with the detected upgrade file name before the screen update.
- `VA 0x0025E92C (file+0x0005E92C)` — bitplane blitter that flips per-pixel flags in the UI buffer (observed writes to `[base+0x678..0x684]` and `0x67C`).

The chain confirms that the “upgrade found” path does not immediately talk to storage; instead it prepares UI state and defers actual file access to downstream code that reuses these buffers.

## Command Snippets

Decode any handler with:
```bash
objdump -b binary -m armv7 -D \
  --start-address=0xC2000 --stop-address=0xC2140 data/raw/ZK-INKJET-NANO-APP.bin | less  # file+0x000C2000..0xC2140
```
Switch to Thumb when ARM output looks nonsensical:
```bash
objdump -b binary -m armv7 -M force-thumb -D \
  --start-address=0xC3A80 --stop-address=0xC3AF0 data/raw/ZK-INKJET-NANO-APP.bin  # file+0x000C3A80..0xC3AF0
```

## Next Focus

1. Follow the helper routines invoked by `VA 0x002C28D0 (file+0x000C28D0)` (`VA 0x002C7018 (file+0x000C7018)`, `VA 0x002C70F4 (file+0x000C70F4)`, `VA 0x002C7334 (file+0x000C7334)`, `VA 0x002C61DC (file+0x000C61DC)`) to identify the actual file I/O strategy used for upgrades (so far this path is UI/metadata only; no hash checks seen).
2. Instrument the notifier at `VA 0x002302EC (file+0x000302EC)` to confirm when flag 2 vs flag 3 entries are displayed and whether additional status bytes are toggled.
3. Cross-reference the queue offsets (`0x144`, `0x14C`, `0x164`, `0x7D8`) with runtime RAM dumps to map the full structure for message injection.
