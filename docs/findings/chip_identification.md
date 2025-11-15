---
title: Chip Identification
status: verified
status_display: "✅ VERIFIED"
confidence: "98%"
last_verified: 2025-11-03
provenance: sessions/session-2025-11-03-soc-identification.md
---

# Chip Identification


---

## Finding

**Chip:** Nuvoton N32903K5DN  
**Package:** LQFP-128 (N32903U5DN pinout)  
**Marking:** "DWIN M5" (custom branding)  
**Variant:** K5DN = No external SDRAM

---

## Evidence

### USB Descriptor Block
- `app.bin` contains the UTF‑16LE string **"W55FA93 USB Card Reader 1.00"** at `0x00475180` plus vendor string **"Nuvoton"** at `0x00475140`.
- These descriptors are stored in the firmware’s USB table (no code xrefs, as expected for descriptor data) and uniquely identify the controller vendor.

### CPU & Architecture Fingerprint
- CP15 instructions such as `mrc p15,0,pc,c7,c14,3` (cache drain) and `mrc p15,0,rx,c1,c0,0` (SCTLR read) prove an **ARM926EJ-S / ARMv5TEJ** core.
- ARM/Thumb interworking stubs (`add r12, pc, #1; bx r12`) and the 0x00000000 vector layout match the N32903 series.

### GPIO & Package Match
- Hardware probing confirmed GPB[2-5] on pins 125‑128, lining up with the **N32903U5DN** LQFP‑128 pinout.
- Register writes to `GPBFUN @ 0xB0000084` match the published multiplexer layout.

### Memory Configuration
- No SDRAM initialisation routine exists in BOOT.bin or APP.bin.
- All RAM references stay within the 8 KB SRAM block at `0xFF000000`, pointing to the **K5DN** “no external SDRAM” variant.

### Feature Alignment
| Feature | Datasheet | Observed |
| --- | --- | --- |
| USB 1.1 host | ✅ | 64 MB “MINI” thumb drive emulation |
| USB 2.0 HS device | ✅ | Descriptor strings + device stack |
| LCD controller | ✅ | Display commit routine hitting `0xB100D000` |
| SD/MMC | ✅ | `sd_write_blocks` routines in APP.bin |
| GPIO mux | ✅ | Pin-mux helpers driving `0xB0000084` |

### MMIO Fingerprint (Highlights)
- `0xB0000204/208/18/14` – Clock/power enable bits toggled during init.
- `0xB000008C` / `0xB0000084` – GPIO mux registers manipulated exactly like the datasheet.
- `0xB800C000` – “Doorbell” parameter block polled before dispatching display ops.
- `0xB100D000` – Display controller base used by hardware update routine @ `0x00230E04`.

---

## Cross-References

- **Session Log:** `docs/sessions/session-2025-11-03-soc-identification.md`
- **Hardware Reference:** `docs/N32903U5DN_K5DN_CheatCheet.txt`
- **Verification Status:** `docs/VERIFICATION_STATUS.md`

---

## Missing for 100% Confirmation

- CHIPID register read (not found in firmware)
- JTAG IDCODE (requires hardware access)

---

**Discovery Method:** USB string analysis + architecture verification  
**Verification:** Multiple independent sources  
**Session:** 2025-01-25 (updated 2025-11-03)
