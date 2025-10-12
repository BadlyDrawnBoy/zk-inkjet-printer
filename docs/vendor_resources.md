# Vendor resources (links only)

I do **not** redistribute vendor SDKs/manuals in this repository. This page lists official sources/search terms so others can fetch the same files themselves and record versions/checksums.

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
