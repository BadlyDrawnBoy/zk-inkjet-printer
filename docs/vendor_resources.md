# Vendor resources (links only)

I do **not** redistribute vendor SDKs/manuals in this repository. This page lists official sources/search terms so others can fetch the same files themselves and record versions/checksums. For UART-specific takeaways distilled from these references, see `docs/uart_control_consolidated.md`.

## SoC note
The SoC is now confirmed as **Nuvoton N32903K5DN** (see `docs/sessions/README.md` entry for 2025-01-25). Early work assumed a DWIN-branded “M5” package, so the DWIN links below are retained only as historical context or for comparison when vendor tooling overlaps. Treat them as legacy references unless you need to reconcile earlier notes.

## Where to look now (Nuvoton sources / tools)
Focus current research on official Nuvoton documentation:
- Search terms: **“N32903 datasheet”**, **“N32903 register reference”**, **“N32903 user manual”**, **“N32903 EVB schematic”**, **“N329 series software package”**.
- Monitor Nuvoton’s application note portal and forum threads that cover ARM9-based multimedia controllers.
- Capture SHA-256 hashes and download metadata the same way as with the DWIN material.

## Legacy DWIN references (kept for provenance)
These links trace the earlier “M5” hypothesis. Keep the metadata if you need to compare terminology or extract DGUS protocol hints:
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
| N32903 datasheet           | Nuvoton download center          |              |                         |         |       |
| N32903 programming manual  | Nuvoton download center          |              |                         |         |       |
| N32903 EVB package         | Nuvoton                          |              |                         |         |       |
| T5L family datasheet *(legacy)* | DWIN docs portal            |              |                         |         | kept for historical cross-checks |
| DGUS-II User Manual *(legacy)*  | DWIN docs portal            |              |                         |         | legacy hypothesis only |
| DGUS Tool (Windows) *(legacy)*  | DWIN downloads              |              |                         |         |       |
| Serial protocol reference *(legacy)* | DWIN forums            |              |                         |         | DGUS framing reference |

How to compute a checksum:
```bash
sha256sum <file.pdf> >> docs/vendor_checksums.txt
```

## Legal

Trademarks belong to their respective owners. This is a personal research project (interoperability). Do not upload vendor packages here; link to official sources instead.

## Direct links (official)
- *(Pending)* — add concrete Nuvoton download-center URLs once the public package IDs are confirmed. Record them here with hashes and mirror them in `docs/vendor_checksums.txt`.

### Legacy DWIN links (kept for context)
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
