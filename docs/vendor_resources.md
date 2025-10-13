# Vendor resources (links only)

I do **not** redistribute vendor SDKs/manuals in this repository. This page lists official sources/search terms so others can fetch the same files themselves and record versions/checksums. For UART-specific takeaways distilled from these references, see `docs/uart_control_consolidated.md`.

## SoC note
The main SoC on my unit is marked **M5 (DWIN)**. I could not find an M5 datasheet; I reference **T5L** family documentation where it matches observed behaviour. Any M5↔T5L equivalence is **unconfirmed**.

## Where to look (official docs / tools)
Use the vendor’s site (support/downloads/docs) and search terms like:
- **“DWIN T5L datasheet”**, **“DGUS-II user manual”**, **“DWIN HMI development guide”**
- **“DGUS Tool”**, **“DWIN font generator”**, **“DWINOS / DWINSET”**
- **“DGUS serial protocol”**, **“DGUS command set”**, **“UART parameters DGUS”**

> Tip: record exact filenames, version strings, and dates when you download.

## Related product family (examples)
Firmware strings reference **“ZK1696”**, suggesting an OEM family with multiple rebrands/shells. This unit itself is labeled **DP20** and carries no CHIKYTECH branding.
- Example vendor page (for reference only): CHIKYTECH handheld inkjet (ZK1696-class).

## Provenance log (what I actually used)
Add rows via PR when you consult a new document/tool.

| Resource (title)           | Source (homepage or docs index) | Version/Date | Filename                | SHA-256 | Notes |
|----------------------------|----------------------------------|--------------|-------------------------|---------|-------|
| T5L family datasheet       | DWIN docs portal                 |              |                         |         |       |
| DGUS-II User Manual        | DWIN docs portal                 |              |                         |         |       |
| DGUS Tool (Windows)        | DWIN downloads                   |              |                         |         |       |
| Serial protocol reference  | DWIN docs                        |              |                         |         |       |
| (optional) Dev board docs  | DWIN                             |              |                         |         |       |
| (example) CHIKYTECH page   | Vendor site                      |              |                         |         | link only |

How to compute a checksum:
```bash
sha256sum <file.pdf> >> docs/vendor_checksums.txt
```

## Legal

Trademarks belong to their respective owners. This is a personal research project (interoperability). Do not upload vendor packages here; link to official sources instead.

## Direct links (official)
- [DWIN Tool page (DGUS, drivers, etc.)](https://dwin-global.com/tool-page/) — DGUS downloads and related tools. <!-- official tool hub -->
- DWIN development guides:
  - [Primary index](https://dwin-global.com/development-guide/) — assorted T5/T5L documentation.
  - [German mirror](https://de.dwin-global.com/development-guide/) — same content, alternate locale.
- [DGUSII serial protocol (T5/T5L)](https://forums.dwin-global.com/index.php/forums/topic/application-instructions%EF%BC%9At5t5l-dgusii-serial-communication-protocol/) — forum topic with attachment covering 0x82/0x83 commands.
- [Example dev board (EKT043B)](https://www.dwin.com.cn/product_detail_4948245.html) — product page that often links a resource pack.
- [Kernel upgrade kits](https://de.dwin-global.com/kernel-upgrade/) — official upgrade packages for DGUS platforms.

### Kernel upgrade kits: interesting files to inspect (names seen in vendor kit)
- `STARTUP_M5.A51` / `STARTUP_M5.zip` — 8051 startup code labeled **M5** (helpful for reset/interrupt model).
- `T5L51.bin` — small binary built via `srec_cat` from `New_C_8283.hex` in the sample.
- Source highlights: `Uart.c`, `Parameter_Config.h`, `Dwin_T5L1H.h` (`FOSC = 206438400UL`), `crc16.c`.
- Protocol bytes in sample comments: header `5A A5`, ops `0x82` (write) / `0x83` (read), optional CRC per-UART.

### Panel candidate (unconfirmed)
- EKT035B (3.5", **480×320**, IPS, TA/DGUS-II): https://ecdn6.globalso.com/upload/p/1355/source/2025-09/EKT035B.pdf  
  *Note:* Matches our observed 480×… class; not confirmed for this exact unit.

