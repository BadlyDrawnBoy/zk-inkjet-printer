# MMIO Fingerprint (app.bin + boot.bin)

## Verification Status Legend

- ✅ **VERIFIED** - Direct evidence in disassembly with multiple confirmations
- ⚠️ **LIKELY** - Strong evidence but needs additional verification
- ❓ **HYPOTHESIS** - Inferred from patterns, needs verification

---

## Register Accesses (Mixed Verification Status)

### Clock/Bus Control (0xB0000xxx) - ✅ VERIFIED
**Evidence:** Multiple direct accesses in app.bin, GCR_BA confirmed at 0xB0000000  
**Confidence:** 98%

| Address      | Operation | Context | Evidence |
|--------------|-----------|---------|----------|
| 0xB0000204   | \|= 0x01000000 \| 0x20 | Bus/Clock enable | app.bin: 0x0026FC34 |
| 0xB0000204   | \|= 0x800 | Additional gate | app.bin: 0x0026FC58 |
| 0xB0000014   | toggle 0x10000 | Pulse/timing | app.bin: 0x0026FC40/4C |
| 0xB0000014   | toggle 0x8 | Pulse/timing | app.bin: 0x0026FC64/70 |
| 0xB0000208   | \|= 0x40 | Flag/IRQ enable | app.bin: 0x0026FCC0 |
| 0xB0000018   | toggle 0x1000 | Pulse/timing | app.bin: 0x0026FCCC/D4 |
| 0xB000008C   | \|= 0xF3000000 | High control bits | app.bin: 0x0026FCFC |
| 0xB0000090   | &= 0xFFFF000F | Mask clear | boot.bin: FUN_00251A64 |
| 0xB0000084   | Derived from 0x8C | Mode setup | boot.bin: FUN_00251A64 |

### Doorbell/Parameter Block (0xB800C000) - ✅ VERIFIED
**Evidence:** Direct disassembly showing poll-write-param pattern at 0x00270040  
**Confidence:** 95%  
**Verified:** Literal @ 0x00270188 = 0xB800C000

| Address      | Operation | Context | Evidence |
|--------------|-----------|---------|----------|
| base+0x0     | poll bit0 (busy) | Status check | app.bin: 0x00270098 (ldr/tst loop) |
| base+0x0     | write cmd | Doorbell/command | app.bin: 0x002700b8, 0x00270104 |
| base+0x10..0x1C | write params | Parameter registers | app.bin: 0x002700a8..0x002700b4 |
| base (ptr)   | [0x270188] | Register base literal | app.bin: 0x00270040 |

### Storage/SD Controller - ⚠️ LIKELY
**Evidence:** Function name "sd_write_blocks" in analysis  
**Confidence:** 80%  
**Needs verification:** Confirm register addresses

| Address      | Operation | Context | Evidence |
|--------------|-----------|---------|----------|
| DAT_00252504 | Status/doorbell | Block device driver | app.bin: sd_write_blocks |
| DAT_00252290 | Control word | Driver context | app.bin: sd_write_blocks |

## USB Evidence - ✅ VERIFIED
**Confidence:** 98%
- **String Descriptor @ 0x00475180:** "W55FA93 USB Card Reader 1.00"
- **Vendor String @ 0x00475140:** "Nuvoton" (UTF-16LE fragment)
- **No direct code xrefs** (likely SDK carry-over or indirect access via descriptor array)

## Architecture Confirmation - ✅ VERIFIED
**Confidence:** 99%
- **ARMv5TEJ (ARM926EJ-S)** confirmed via:
  - CP15 instructions: `mrc p15,0,pc,c7,c14,3` (barrier)
  - CP15 instructions: `mrc p15,0,rx,c1,c0,0` (SCTLR)
  - ARM/Thumb interworking: `ADD r12,pc,#1; BX r12`
  - Vector layout at 0x00000000 (code, not Cortex-M data table)

## Next Steps

### High Priority (Verify Hypotheses)
1. ✅ VERIFIED: Doorbell/Parameter Block at 0xB800C000
2. ⚠️ Verify SD controller register addresses

### Medium Priority
1. Search for CHIPID register reads (fixed address + magic constant compare)
2. Map complete GCR register set (beyond 0xB0000000 base)

### Low Priority
1. Compare MMIO map against N32903K5DN datasheet (if available)
2. Identify USB host controller registers (likely in 0xB8xxxxxx range)
