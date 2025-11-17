---
title: MMIO Register Map
status: partially_verified
status_display: "✅ PARTIALLY VERIFIED"
confidence: "90-99% (per register)"
last_verified: 2025-11-03
provenance: sessions/session-2025-11-03-soc-identification.md
---

# MMIO Register Map


---

## Verified Registers

### 0xB0000000 - GCR_BA (Global Control Register)
**Status:** ✅ VERIFIED  
**Confidence:** 99%  
**Evidence:** 54 direct accesses in firmware

**Key Registers:**
- `0xB0000084` - GPBFUN (Port B Pin Multiplexing)
- `0xB0000204` - Clock/Bus/Gate Control

**Usage Example @ 0x0006fc24:**
```asm
mov r4,#0xb0000000      ; Load GCR_BA
ldr r0,[r4,#0x204]      ; Read clock control
orr r0,r0,#0x1000000    ; Set bit
str r0,[r4,#0x204]      ; Write back
```

---

### 0xB800C000 - Doorbell/Parameter Block
**Status:** ✅ VERIFIED  
**Confidence:** 95%  
**Evidence:** Literal @ 0x00270188, pattern @ 0x00270040

**Register Layout:**
- `+0x00` - Command/Status (bit 0 = busy)
- `+0x10` - Parameter 1
- `+0x14` - Parameter 2
- `+0x18` - Parameter 3
- `+0x1C` - Parameter 4

**Usage Pattern:**
```asm
ldr r12,[0x270188]      ; Load base = 0xB800C000
ldr r10,[r12,#0x0]      ; Read status
tst r10,#0x1            ; Test busy bit
bne <wait_loop>         ; Wait if busy
str r9,[r12,#0x10]      ; Write param1
str r8,[r12,#0x14]      ; Write param2
str r7,[r12,#0x18]      ; Write param3
str r6,[r12,#0x1c]      ; Write param4
str r5,[r12,#0x0]       ; Write command (trigger)
```

**Purpose:** Display-related command/parameter interface

---

### 0xB100D000 - Display Controller
**Status:** ✅ VERIFIED  
**Confidence:** 90%  
**Evidence:** Literal @ 0x00230F34, used @ 0x00230E04

**Operations:**
- Wait for bit 0 to clear
- Write color/coordinate data
- Set bit 0 to trigger update

**Usage:** Hardware display update routine

---

### 0xB8001000 - GP_BA (GPIO Base)
**Status:** ✅ VERIFIED  
**Confidence:** 95%  
**Evidence:** Indirect addressing pattern

**Port Offsets:**
- Port A: +0x00
- Port B: +0x40
- Port C: +0x80
- Port D: +0xC0

**Register Offsets (per port):**
- `+0x10` - OMD (Output Mode)
- `+0x14` - PUEN (Pull-Up Enable)
- `+0x18` - DOUT (Data Output)
- `+0x1C` - PIN (Pin Input)

---

## Corrected False Positives

### ❌ 0xB1006800 - Does NOT exist
**Previous claim:** Doorbell/Parameter Block  
**Correction:** No references found in firmware (0 hits)  
**Actual address:** 0xB800C000 (see above)

---

## Hypotheses (Needs Verification)

### 0xB8008000 - UART Controller (likely)
**Status:** ❓ HYPOTHESIS  
**Confidence:** 70%  
**Evidence:** Expected location per N32903 architecture
**Needs:** Direct register access verification

---

## Cross-References

- **Detailed Analysis:** `docs/mmio_fingerprint.md`
- **SoC Overview:** `docs/findings/chip_identification.md`
- **Hardware Reference:** `docs/N32903U5DN_K5DN_CheatCheet.txt`
- **Verification Status:** `docs/VERIFICATION_STATUS.md`

---

**Discovery Method:** Literal pool analysis + pattern matching  
**Verification:** Multiple cross-checks, disassembly analysis  
**Sessions:** 2025-01-25, 2025-11-03
