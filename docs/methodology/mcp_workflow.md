# MCP-Based Analysis Workflow

**Last Updated:** 2025-11-03

---

## Overview

This project uses **Model Context Protocol (MCP)** tools to interact with Ghidra programmatically through an AI assistant. This enables:

- ✅ Systematic exploration of large binaries
- ✅ Reproducible analysis steps
- ✅ AI-assisted pattern recognition
- ✅ Iterative refinement of findings
- ✅ Cross-verification of hypotheses

---

## MCP Tools Available

### Ghidra-Bridge Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `search_scalars` | Find scalar values in binary | Find base addresses |
| `search_strings` | Find text strings | Locate debug messages |
| `search_functions` | Find functions by name pattern | Locate GPIO functions |
| `search_xrefs_to` | Find cross-references | Find all callers |
| `disassemble_at` | Disassemble at address | Analyze function |
| `read_bytes` | Read raw bytes | Check literal pools |
| `list_functions_in_range` | List functions in range | Map code regions |

### Power Tools (File System)

| Tool | Purpose | Example |
|------|---------|---------|
| `file_read` | Read file content | Inspect source |
| `file_write` | Write file content | Create documentation |
| `file_edit` | Edit file (find/replace) | Update findings |
| `bash` | Execute shell command | Run objdump |
| `grep` | Search in files | Find patterns |
| `glob` | Find files by pattern | Locate all .md files |

---

## Typical Workflow

### Phase 1: Initial Exploration

**Goal:** Find interesting code regions

**Tools:**
- `search_strings` - Find debug strings, file paths
- `search_functions` - Find functions by name pattern
- `search_scalars` - Find known addresses/constants

**Output:** List of candidate addresses

**Example:**
```
search_strings(query="GPIO")
→ Found 0 hits (no debug strings)

search_scalars(value=0xB0000000)
→ Found 54 hits (GCR_BA confirmed)
```

---

### Phase 2: Detailed Analysis

**Goal:** Understand specific functions

**Tools:**
- `disassemble_at` - Disassemble function
- `read_bytes` - Check literal pools
- `search_xrefs_to` - Find callers

**Output:** Function behavior, parameters, call graph

**Example:**
```
disassemble_at(address=0x31f34, count=60)
→ Pin-mux function identified

search_xrefs_to(address=0x31f34)
→ 12 callers found
```

---

### Phase 3: Systematic Verification

**Goal:** Confirm hypotheses

**Tools:**
- `list_functions_in_range` - Map all functions
- `search_xrefs_to` - Analyze ALL callers
- `disassemble_at` - Check each caller

**Output:** Verified findings with confidence level

**Example:**
```
For each of 12 callers:
  disassemble_at(address=<caller>)
  → Extract parameters
  → Verify Port B configurations

Result: Only GPB[0] and GPB[6] configured
Confidence: 98% (systematic analysis)
```

---

### Phase 4: Documentation

**Goal:** Record findings

**Tools:**
- `file_write` - Create new documents
- `file_edit` - Update existing documents

**Output:** Traceable, verifiable documentation

**Example:**
```
file_write("docs/findings/gpio_configuration.md")
→ Document created with evidence

file_edit("docs/VERIFICATION_STATUS.md")
→ Confidence level updated
```

---

## Example: Complete Analysis Flow

### Finding GPIO Configuration

**Step 1: Find GPIO base address**
```
Tool: search_scalars(value=0xB0000000)
Result: 54 hits → GCR_BA confirmed
Confidence: 99%
```

**Step 2: Find pin-mux function**
```
Tool: disassemble_at(address=0x31f34, count=60)
Result: Function manipulates GPBFUN @ GCR_BA+0x84
Confidence: 99%
```

**Step 3: Find all callers**
```
Tool: search_xrefs_to(address=0x31f34, query="*")
Result: 12 callers found
Confidence: 100% (exhaustive)
```

**Step 4: Analyze each caller**
```
For i in range(12):
  Tool: disassemble_at(address=<caller[i]>, count=64)
  Extract: Port, Pin, Function parameters
  
Result: 
  - GPB[0]: Function 2 (2 locations)
  - GPB[6]: Function 5 (1 location)
  - GPB[2-5]: No configuration (0 locations)
  
Confidence: 98% (systematic)
```

**Step 5: Document**
```
Tool: file_write("docs/findings/gpio_configuration.md")
Content: Evidence, confidence, cross-references

Tool: file_edit("docs/VERIFICATION_STATUS.md")
Update: Confidence levels, corrected findings
```

---

## Reproducibility

### For AI-Assisted Analysis
1. Load Ghidra project with MCP bridge
2. Use tool calls documented in session files
3. Cross-verify with multiple approaches
4. Document findings with confidence levels

### For Manual Analysis
1. Use standard tools: `objdump`, `hexdump`, `grep`
2. Follow equivalent procedures (see below)
3. Cross-check results with documented findings

### For Verification
1. Check `docs/VERIFICATION_STATUS.md` for current confidence
2. Use verification checklist (see `verification_checklist.md`)
3. Cross-reference multiple findings

---

## Manual Equivalents

### MCP Tool → Shell Command Mapping

| MCP Tool | Shell Equivalent |
|----------|------------------|
| `search_scalars(0xB0000000)` | `objdump -D app.bin \| grep -i "b0000000"` |
| `disassemble_at(0x31f34, 60)` | `objdump -D --start-address=0x231f34 --stop-address=0x231f70 app.bin --adjust-vma=0x200000` |
| `search_xrefs_to(0x31f34)` | `objdump -D app.bin --adjust-vma=0x200000 \| grep "bl.*31f34"` |
| `read_bytes(0x270188, 4)` | `xxd -s 0x70188 -l 4 app.bin` |
| `search_strings("GPIO")` | `strings app.bin \| grep -i gpio` |

**Note:** Add `--adjust-vma=0x200000` for virtual addresses (APP base)

---

## Best Practices

### 1. Always Verify
- Cross-check findings with multiple methods
- Use different tools to confirm same result
- Document confidence levels

### 2. Document Everything
- Record tool calls in session files
- Note assumptions and hypotheses
- Update verification status

### 3. Iterate Carefully
- One step at a time
- Verify before proceeding
- Correct false positives immediately

### 4. Preserve Context
- Keep all session logs
- Don't delete old findings (mark as corrected)
- Maintain traceability

---

## Cross-References

- **Verification Checklist:** `docs/methodology/verification_checklist.md`
- **Ghidra Setup:** `docs/methodology/ghidra_setup.md`
- **Session Logs:** `docs/sessions/`
- **Findings:** `docs/findings/`

---

**This workflow is continuously refined based on experience.**
