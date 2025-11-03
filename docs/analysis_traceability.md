# Analysis Traceability

**Purpose:** Quick reference for how findings were discovered and verified.

**Note:** This document uses MCP (Model Context Protocol) tool calls, not shell commands.
For detailed methodology, see `docs/methodology/mcp_workflow.md`.

**Full Archive:** See `docs/analysis_traceability_FULL_ARCHIVE.md` for complete session logs.

---

## Quick Reference

| Finding | Confidence | Discovery Method | Session |
|---------|------------|------------------|---------|
| N32903K5DN chip | 98% | USB strings + architecture | 2025-01-25 |
| GPB[2-5] not configured | 98% | Systematic pin-mux analysis | 2025-11-03 |
| 0xB800C000 = Doorbell | 95% | Literal pool + pattern | 2025-11-03 |
| 0xB0000204 = Clock/Bus | 99% | Direct disassembly | 2025-11-03 |
| Pin-Mux @ 0x31f34 | 99% | Function analysis | 2025-11-03 |

**Detailed findings:** See `docs/findings/`

---

## Recent Sessions (2025-11-03)

### GPIO Pin Analysis
**Finding:** GPB[2-5] are NOT configured in firmware  
**Method:** Analyzed all 12 callers of pin-mux function  
**Confidence:** 98%  
**Details:** `docs/findings/gpio_configuration.md`

### MMIO Address Correction
**Finding:** 0xB1006800 does not exist; 0xB800C000 is Doorbell  
**Method:** Literal pool analysis + pattern matching  
**Confidence:** 95%  
**Details:** `docs/findings/mmio_map.md`

### Repository Audit
**Action:** Added verification status to all documents  
**Result:** Clear distinction between facts and hypotheses  
**Details:** `docs/VERIFICATION_STATUS.md`

---

## Session Index

**Complete session logs:** `docs/sessions/`

- 2025-11-03: GPIO Pin Analysis
- 2025-11-03: Alternative Functions Analysis
- 2025-11-03: MMIO Address Correction
- 2025-11-03: Repository Audit
- 2025-01-25: SoC Identification

---

## Reproducibility

### For AI-Assisted Analysis
1. Load Ghidra project with MCP bridge
2. Use tool calls from session files
3. Cross-verify with multiple approaches

### For Manual Analysis
1. Use standard tools: `objdump`, `hexdump`, `grep`
2. Follow methodology in `docs/methodology/`
3. See `docs/boot_analysis_methodology.md` for examples

### For Verification
1. Check `docs/VERIFICATION_STATUS.md`
2. Cross-reference multiple findings
3. Use verification checklist (TBD)

---

## Tool Reference

**MCP Tools:**
- `search_scalars` - Find values in binary
- `disassemble_at` - Disassemble at address
- `search_xrefs_to` - Find cross-references
- `read_bytes` - Read raw bytes

**Manual Equivalents:**
- `objdump -D binary | grep <value>`
- `objdump -D --start-address=<addr> binary`
- `objdump -D binary | grep "call.*<addr>"`
- `xxd -s <offset> -l <len> binary`

**Full workflow:** `docs/methodology/mcp_workflow.md`

---

**Last Updated:** 2025-11-03
