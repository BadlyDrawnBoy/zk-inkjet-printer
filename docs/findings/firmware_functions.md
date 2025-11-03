# Firmware Functions

**Status:** ✅ PARTIALLY VERIFIED  
**Last Updated:** 2025-11-03

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
