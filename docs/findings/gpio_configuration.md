---
title: GPIO Configuration
status: verified
status_display: "✅ VERIFIED"
confidence: "98%"
last_verified: 2025-11-03
provenance: sessions/session-2025-11-03-soc-identification.md
---

# GPIO Configuration


---

## Finding

**Port B Configuration:**
- ✅ GPB[0] - Configured (Function 2)
- ❌ GPB[2] - NOT configured
- ❌ GPB[3] - NOT configured
- ❌ GPB[4] - NOT configured
- ❌ GPB[5] - NOT configured
- ✅ GPB[6] - Configured (Function 5)

**Key Discovery:** GPB[2-5] are NOT configured in firmware (neither GPIO nor alternative functions)

---

## Evidence

### Pin-Mux Function
- **Address:** 0x00031f34
- **Size:** 600 bytes
- **Purpose:** Configure GPIO pin multiplexing via GPBFUN register
- **Register:** GPBFUN @ 0xB0000084 (GCR_BA + 0x84)

### Systematic Analysis
- **Total pin-mux calls:** 12
- **Port B configurations:** 3
  - GPB[0]: Function 2 @ 0x00031e4c, 0x00031ea4
  - GPB[6]: Function 5 @ 0x0005c210
- **GPB[2-5] configurations:** 0 (none found)

### Alternative Functions Checked
- ❌ UART: No configuration
- ❌ SPI: No configuration
- ❌ I2C: No configuration
- ❌ PWM: No configuration
- ❌ I2S: No configuration (0 hits for I2S_BA @ 0xB1001000)
- ❌ SD-Card: No configuration

---

## Hardware Context

**N32903K5DN LQFP-128 Pinout:**
- Pin 128 = GPB[2]: GPIO / I2S_MCLK / SDCLK1 / SHSYNC
- Pin 127 = GPB[3]: GPIO / I2S_BCLK / SDCMD1 / SVSYNC
- Pin 126 = GPB[4]: GPIO / I2S_WS / SDDAT1[3] / SFIELD
- Pin 125 = GPB[5]: GPIO / I2S_DOUT / SDDAT1[2] / SPDATA[0]

---

## Possible Explanations

1. **Default GPIO Mode** (most likely)
   - Pins remain in hardware reset state
   - No explicit configuration needed

2. **Unused in Hardware Design**
   - Pins may be unconnected (NC)
   - Other ports actively used (D, E)

3. **Boot ROM Pre-Configuration**
   - Internal Boot ROM may configure before app firmware

---

## Cross-References

- **Detailed Analysis:** `docs/gpio_pins_analysis.md`
- **Verification Status:** `docs/VERIFICATION_STATUS.md`
- **Hardware Reference:** `docs/N32903U5DN_K5DN_CheatCheet.txt`

---

**Discovery Method:** Systematic analysis of all pin-mux function calls  
**Verification:** All 12 callers analyzed, no GPB[2-5] configuration found  
**Session:** 2025-11-03
