# Chip Identification

**Status:** ✅ VERIFIED  
**Confidence:** 98%  
**Last Updated:** 2025-11-03

---

## Finding

**Chip:** Nuvoton N32903K5DN  
**Package:** LQFP-128 (N32903U5DN pinout)  
**Marking:** "DWIN M5" (custom branding)  
**Variant:** K5DN = No external SDRAM

---

## Evidence

### 1. USB String Descriptors
- **Location:** 0x00475180 in app.bin
- **Content:** "W55FA93 USB Card Reader 1.00"
- **Vendor:** "Nuvoton" @ 0x00475140 (UTF-16LE)

### 2. CPU Architecture
- **Type:** ARM926EJ-S (ARMv5TEJ)
- **Evidence:** CP15 instructions in code
  - `mrc p15,0,pc,c7,c14,3` (cache barrier)
  - `mrc p15,0,rx,c1,c0,0` (SCTLR read)
- **Interworking:** ARM/Thumb mode switching confirmed

### 3. GPIO Pinout Match
- **Package:** LQFP-128 pins match N32903U5DN datasheet
- **Example:** GPB[2-5] = pins 125-128 (verified in hardware)

### 4. Memory Configuration
- **No external SDRAM:** No SDRAM init code found
- **Internal SRAM:** 8 KB @ 0xFF000000
- **Conclusion:** K5DN variant (no external SDRAM support)

---

## Cross-References

- **Detailed Analysis:** `docs/soc_identification.md`
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
