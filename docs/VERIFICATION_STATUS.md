# Verification Status - ZK-INKJET Firmware Analysis

**Last Updated:** 2025-11-03  
**Project:** ZK-INKJET Printer Reverse Engineering  
**Chip:** Nuvoton N32903K5DN in N32903U5DN package (LQFP-128)

---

## Purpose

This document tracks the verification status of all major findings in the repository. It helps distinguish between:
- ✅ **Verified facts** (high confidence, reproducible)
- ⚠️ **Likely findings** (strong evidence, needs confirmation)
- ❓ **Hypotheses** (inferred, needs verification)
- 🔄 **Corrected** (previously incorrect, now fixed)

---

## Hardware Identification

### SoC / Microcontroller

| Finding | Status | Confidence | Evidence | Document |
|---------|--------|------------|----------|----------|
| Nuvoton N32903K5DN | ✅ VERIFIED | 98% | USB strings, ARM926EJ-S arch, pinout | `docs/soc_identification.md` |
| LQFP-128 package (N32903U5DN pinout) | ✅ VERIFIED | 98% | GPIO pin analysis | `docs/gpio_pins_analysis.md` |
| No external SDRAM (K5DN variant) | ✅ VERIFIED | 95% | No SDRAM init code | Analysis |
| "DWIN M5" marking | ✅ VERIFIED | 100% | Physical chip marking | Hardware |
| ARM926EJ-S @ 200MHz | ✅ VERIFIED | 99% | CP15 instructions | `docs/soc_identification.md` |

**Missing for 100%:**
- CHIPID register read (not found in firmware)
- JTAG IDCODE (requires hardware access)

---

## Memory Map

### Verified Registers

| Address | Function | Status | Confidence | Evidence |
|---------|----------|--------|------------|----------|
| 0xB0000000 | GCR_BA (Global Control) | ✅ VERIFIED | 98% | 54 direct accesses | 
| 0xB0000084 | GPBFUN (Port B Pin-Mux) | ✅ VERIFIED | 99% | Disassembly + systematic analysis |
| 0xB8001000 | GP_BA (GPIO Base) | ✅ VERIFIED | 95% | Indirect addressing pattern |
| 0xB800101C | GPIOB_PIN (Port B Input) | ✅ VERIFIED | 95% | Read function @ 0x00031ec4 |
| 0xB8001018 | GPIOB_DOUT (Port B Output) | ✅ VERIFIED | 95% | Write function @ 0x0003224c |
| 0xB800C000 | Doorbell/Parameter Block | ✅ VERIFIED | 95% | Poll-write pattern @ 0x00270040, literal @ 0x00270188 |

### Likely Registers

| Address | Function | Status | Confidence | Evidence |
|---------|----------|--------|------------|----------|
| 0xB100D000 | Display Controller | ⚠️ LIKELY | 80% | Hardware update routine |

### Hypotheses

| Address | Function | Status | Confidence | Needs |
|---------|----------|--------|------------|-------|

---

## GPIO Configuration

### Verified Pin Configurations

| Pin | Port | Function | Status | Confidence | Evidence |
|-----|------|----------|--------|------------|----------|
| GPB[0] | B | Function 2 | ✅ VERIFIED | 99% | 2 config calls @ 0x00031e4c, 0x00031ea4 |
| GPB[6] | B | Function 5 | ✅ VERIFIED | 99% | 1 config call @ 0x0005c210 |
| GPD[0] | D | Function 5 | ✅ VERIFIED | 95% | Config call @ 0x000322ec |
| GPD[3] | D | Function 5 | ✅ VERIFIED | 95% | Config call @ 0x0005c1e4 |
| GPE[8-11] | E | Various | ✅ VERIFIED | 95% | Multiple config calls |

### Unconfigured Pins

| Pin | Port | Status | Confidence | Notes |
|-----|------|--------|------------|-------|
| GPB[2] | B | 🔄 NOT CONFIGURED | 98% | Previously assumed "used as GPIO" - CORRECTED |
| GPB[3] | B | 🔄 NOT CONFIGURED | 98% | Previously assumed "used as GPIO" - CORRECTED |
| GPB[4] | B | 🔄 NOT CONFIGURED | 98% | Previously assumed "used as GPIO" - CORRECTED |
| GPB[5] | B | 🔄 NOT CONFIGURED | 98% | Previously assumed "used as GPIO" - CORRECTED |

**Analysis:** Systematic review of all 12 pin-mux function calls found NO configuration for GPB[2-5].

---

## Firmware Functions

### High Confidence (>90%)

| Address | Function | Status | Confidence | Evidence |
|---------|----------|--------|------------|----------|
| 0x00031f34 | Pin-Mux Configuration | ✅ VERIFIED | 99% | 12 callers analyzed |
| 0x00031ec4 | GPIO Read Pin | ✅ VERIFIED | 98% | Disassembly + pattern |
| 0x0003224c | GPIO Write Pin | ✅ VERIFIED | 98% | Disassembly + pattern |
| 0x0020EAEC | Upgrade Orchestrator | ✅ VERIFIED | 95% | Call graph analysis |
| 0x003D3E00 | Message Handler Table | ✅ VERIFIED | 95% | Structure verified |

### Medium Confidence (70-90%)

| Address | Function | Status | Confidence | Needs |
|---------|----------|--------|------------|-------|
| 0x002302EC | Shared Notifier | ⚠️ LIKELY | 85% | More call-site analysis |
| 0x002BFC34 | Flash Writer | ⚠️ LIKELY | 80% | Verify guard conditions |
| 0x00244F8C | Queue Controller | ⚠️ LIKELY | 80% | RAM dump for runtime state |

### Low Confidence (<70%)

| Address | Function | Status | Confidence | Needs |
|---------|----------|--------|------------|-------|
| 0x00208592 | Queue Vtable Callback | ❓ HYPOTHESIS | 60% | RAM dump required |
| 0x00230E04 | Hardware Update | ❓ HYPOTHESIS | 65% | Identify peripheral type |

---

## Alternative Functions Analysis

### Checked for GPB[2-5]

| Function Type | Status | Confidence | Evidence |
|---------------|--------|------------|----------|
| UART | ❌ NOT USED | 99% | No UART base access, no strings |
| SPI | ❌ NOT USED | 99% | No SPI config for these pins |
| I2C | ❌ NOT USED | 99% | No I2C config for these pins |
| PWM | ❌ NOT USED | 99% | No PWM config for these pins |
| I2S | ❌ NOT USED | 99% | 0 hits for I2S_BA (0xB1001000) |
| SD-Card | ❌ NOT USED | 99% | No SD config for these pins |

**Conclusion:** GPB[2-5] remain in default state (likely GPIO mode) or are unused.

---

## Corrected Findings

### Major Corrections

| Original Finding | Corrected Finding | Date | Document |
|------------------|-------------------|------|----------|
| "GPB[2-5] used as standard GPIOs" | "GPB[2-5] NOT configured in firmware" | 2025-11-03 | `docs/gpio_pins_analysis.md` |
| "N3290X SoC" | "N32903K5DN in N32903U5DN package" | 2025-11-03 | `docs/soc_identification.md` |
| "0xB1006800 = Doorbell/Parameter Block" | "0xB800C000 = Doorbell/Parameter Block" | 2025-11-03 | `docs/mmio_fingerprint.md` |
| "0xB800C000 = FIFO/Status" | "0xB800C000 = Doorbell/Parameter Block" | 2025-11-03 | `docs/mmio_fingerprint.md` |

---

## Verification Methodology

### Evidence Hierarchy

1. **Direct Disassembly** (highest confidence)
   - Instruction-by-instruction analysis
   - Multiple cross-references
   - Reproducible commands

2. **Pattern Matching** (medium confidence)
   - Consistent access patterns
   - Single confirmation
   - Needs additional verification

3. **Inference** (lowest confidence)
   - Derived from context
   - No direct evidence
   - Requires verification

### Confidence Levels

- **99%:** Multiple independent confirmations, direct evidence
- **95%:** Strong direct evidence, single confirmation
- **90%:** Pattern-based with supporting evidence
- **80%:** Likely but needs verification
- **70%:** Hypothesis with some evidence
- **<70%:** Speculation, needs verification

---

## Next Steps

### High Priority Verifications

1. ✅ VERIFIED: Doorbell/Parameter Block at 0xB800C000
2. ⚠️ Identify peripheral type for 0xB800C000 (Display-related? DMA?)
3. ❓ Verify vtable callback at 0x00208592 (needs RAM dump)

### Medium Priority

1. Complete GPIO port mapping (all ports A-F)
2. Verify flash writer guard conditions
3. Map complete GCR register set

### Low Priority

1. JTAG probe for CHIPID confirmation
2. Compare with N32903K5DN datasheet (if available)
3. Document all MMIO register accesses

---

## Document Cross-References

- **SoC Identification:** `docs/soc_identification.md`
- **GPIO Analysis:** `docs/gpio_pins_analysis.md`
- **MMIO Map:** `docs/mmio_fingerprint.md`
- **Offset Catalog:** `docs/offset_catalog.md`
- **Traceability:** `docs/analysis_traceability.md`
- **Chip Reference:** `docs/N32903U5DN_K5DN_CheatCheet.txt`

---

**Audit Completed:** 2025-11-03  
**Auditor:** Systematic firmware analysis  
**Method:** Cross-verification of all major findings
