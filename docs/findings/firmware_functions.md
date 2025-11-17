---
title: Firmware Functions
status: partially_verified
status_display: "✅ PARTIALLY VERIFIED"
confidence: "60-99% (per function)"
last_verified: 2025-11-03
provenance: sessions/session-2025-11-03-soc-identification.md
---

# Firmware Functions


---

## High Confidence Functions (>90%)

### Pin-Mux Configuration @ 0x00031f34
**Status:** ✅ VERIFIED  
**Confidence:** 99%  
**Size:** 600 bytes

**Purpose:** Configure GPIO pin multiplexing

**Parameters:**
- `r0` = Port number (1=A, 2=B, 4=C, 8=D, 16=E)
- `r1` = Pin number (0-15)
- `r2` = Function code (0=GPIO, 1-5=alternate functions)

**Evidence:**
- 12 callers analyzed
- Manipulates GPBFUN @ 0xB0000084
- Clear read-modify-write pattern

---

### GPIO Read Pin @ 0x00031ec4
**Status:** ✅ VERIFIED  
**Confidence:** 98%  
**Size:** 96 bytes

**Purpose:** Read GPIO pin state

**Parameters:**
- `r0` = Port number
- `r1` = Pin number

**Returns:**
- `r0` = Pin state (0 or 1)

**Register:** Reads from GPIOX_PIN (offset 0x1C from port base)

---

### GPIO Write Pin @ 0x0003224c
**Status:** ✅ VERIFIED  
**Confidence:** 98%  
**Size:** 100 bytes

**Purpose:** Set or clear GPIO pin

**Parameters:**
- `r0` = Port number
- `r1` = Pin number
- `r2` = Value (0=clear, non-zero=set)

**Register:** Reads/writes GPIOX_DOUT (offset 0x18 from port base)

---

### Upgrade Orchestrator @ 0x0020EAEC
**Status:** ✅ VERIFIED  
**Confidence:** 95%  
**Size:** ~1500 bytes (Thumb mode)

**Purpose:** Manage firmware upgrade process

**Operations:**
- Walks free-block list
- Accumulates memory statistics
- Bins block sizes by bit-width
- Dispatches logging callbacks

**Evidence:** Call graph analysis, systematic disassembly

---

### Message Handler Table @ 0x003D3E00
**Status:** ✅ VERIFIED  
**Confidence:** 95%  
**Structure:** Array of 12-byte entries

**Entry Format:**
```c
struct MessageEntry {
    uint32_t handler_addr;
    uint32_t string_addr;
    uint32_t flag;
};
```

**Evidence:** Structure verified, 287 entries parsed

---

## Medium Confidence Functions (70-90%)

### Shared Notifier @ 0x002302EC
**Status:** ⚠️ LIKELY  
**Confidence:** 85%

**Purpose:** Process queued messages for display

**Operations:**
- Allocates 0x200-byte buffer
- Calls text/layout helpers
- Updates status flags
- Invoked by multiple message handlers

**Needs:** More call-site analysis

---

### Flash Writer @ 0x002BFC34
**Status:** ⚠️ LIKELY  
**Confidence:** 80%

**Purpose:** Write firmware to flash

**Guard:** Only called when validator @ 0x002BFDDC returns non-zero

**Needs:** Verify guard conditions

---

### Queue Controller @ 0x00244F8C
**Status:** ⚠️ LIKELY  
**Confidence:** 80%

**Purpose:** Manage upgrade queue

**Structure:** Free-block list head pointer

**Needs:** RAM dump for runtime state verification

---

## Low Confidence Functions (<70%)

### Queue Vtable Callback @ 0x00208592
**Status:** ❓ HYPOTHESIS  
**Confidence:** 60%

**Evidence:** Literal @ 0x002113CC resolves to this address (Thumb)

**Needs:** RAM dump to verify runtime behavior

### Upgrade UI Handlers (queue maintenance)
**Status:** ⚠️ LIKELY  
**Confidence:** 85–90%

- **Update complete @ 0x002C2048 (file+0x000C2048)** — clamps queue depth `[base+0x144]`, updates head `[base+0x14C]` via the 0x66_666_667 multiply, and forces the status banner to the record’s VRAM pointer before exiting.
- **No upgrade found @ 0x002C47F0 (file+0x000C47F0)** — compacts 0x14-byte queue records, recomputes the head pointer (divide-by-10 pattern), and cleans the queue when nothing matches.
- **USB/U-disk error @ 0x002C4524 (file+0x000C4524)** — slides records down in 8/16-byte strides, shrinks the active window, and bubbles USB errors to the front.
- **Upgrade found (staging) @ 0x002C28D0 (file+0x000C28D0)** — chains through UI/formatter helpers (`0x2C70F4`, `0x2C7334`, `0x2C6CA0`, `0x2C61DC`, `0x28ACF0`), then the notifier. Stages metadata/UI only; no checksum/hash logic observed.
- **File-open failed @ 0x002C3A94 (file+0x000C3A94)** — thin error wrapper reached when the deeper handler cannot open a descriptor.

**Note:** No checksum/CRC routines are invoked along this handler/validator path; filename matching and queue maintenance drive the upgrade UI.

---

### Hardware Update @ 0x00230E04
**Status:** ❓ HYPOTHESIS  
**Confidence:** 65%

**Purpose:** Commit display updates to hardware

**Register Base:** 0xB100D000 (via literal @ 0x00230F34)

**Needs:** Identify exact peripheral type

---

## Cross-References

- **Offset Catalog:** `docs/offset_catalog.md`
- **Verification Status:** `docs/VERIFICATION_STATUS.md`
- **Analysis Traceability:** `docs/analysis_traceability.md`

---

**Discovery Method:** Systematic disassembly + cross-reference analysis  
**Verification:** Multiple independent confirmations  
**Sessions:** Various (2025-01-25 through 2025-11-03)
