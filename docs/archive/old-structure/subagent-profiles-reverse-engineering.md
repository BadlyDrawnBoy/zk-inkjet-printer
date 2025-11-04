# Subagent Profiles for Reverse Engineering

> [⤴ Back to archive overview](../README.md)




This document defines specialized subagent profiles for the ZK-INKJET firmware reverse engineering project.

---

## Profile: `ghidra-jt-slot-processor`

### Purpose
Process individual Jump-Table slots in parallel to materialize dispatcher handlers.

### Model
`gpt-4o-mini` (fast, cheap, repetitive task)

### Input Schema
```json
{
  "slot_index": 0,
  "jt_base_candidate": "0x002000A0",
  "binary": "app.bin",
  "context": {
    "architecture": "ARMv5T (ARM926EJ-S)",
    "soc": "Nuvoton N3290X",
    "thumb_bit_rule": "If (value & 1) == 1, test Thumb at (value-1)"
  }
}
```

### Task Description
```
Analyze Jump-Table slot {slot_index} in app.bin using Ghidra MCP tools.

Steps:
1. Calculate slot address: jt_base + (slot_index * 4)
2. read_dword(slot_addr) → get raw 32-bit value
3. Check if value is valid pointer:
   - NOT an ARM instruction (e.g., 0xe12fff1c = BX ip)
   - Within valid code range (0x00200000-0x00475000)
4. If valid pointer:
   a. Test ARM mode: disassemble_function(value)
   b. Test Thumb mode: disassemble_function(value-1)
   c. If function found:
      - rename_function_by_address(addr, "dispatch_handler_{slot_index:02d}_tbd")
      - set_decompiler_comment(addr, "JT slot {slot_index} handler")
      - Verify via get_function_by_address
5. Return JSON result

Use only ghidra-bridge MCP tools. Follow Write→Verify pattern.
```

### Output Schema
```json
{
  "slot": 0,
  "slot_addr": "0x002000A0",
  "raw_value": "0xe12fff1c",
  "is_valid_pointer": false,
  "target_addr": null,
  "mode": "INVALID",
  "reason": "Value is ARM instruction BX ip, not a pointer",
  "function_renamed": false,
  "verification_status": "N/A"
}
```

### Success Criteria
- JSON output is valid
- If function found: `function_renamed: true` AND `verification_status: "OK"`
- If invalid: clear `reason` provided

### Cost Estimate
~$0.0005 per slot

---

## Profile: `ghidra-mmio-annotator`

### Purpose
Annotate MMIO register accesses in functions with EOL comments.

### Model
`gpt-4o-mini` (fast, cheap, repetitive task)

### Input Schema
```json
{
  "function_addr": "0x0026FC20",
  "mmio_registers": [
    {"addr": "0xB0000204", "name": "CLK_GATE", "description": "Clock/Bus enable"},
    {"addr": "0xB0000014", "name": "PULSE_CTRL", "description": "Timing pulse"},
    {"addr": "0xB0000208", "name": "IRQ_ENABLE", "description": "IRQ enable"}
  ],
  "binary": "app.bin"
}
```

### Task Description
```
Annotate MMIO accesses in function at {function_addr} using Ghidra MCP tools.

Steps:
1. disassemble_function(function_addr) → get instruction list
2. For each LDR/STR instruction accessing mmio_registers:
   a. Identify operation (READ/WRITE, mask/OR/AND)
   b. set_disassembly_comment(instr_addr, "// {reg_name}: {operation} ({description})")
   c. Verify via disassemble_function
3. Count successful annotations
4. Return JSON result

Use only ghidra-bridge MCP tools. Follow Write→Verify pattern.
```

### Output Schema
```json
{
  "function_addr": "0x0026FC20",
  "comments_added": 7,
  "comments_failed": 0,
  "verification_status": "OK",
  "details": [
    {"addr": "0x0026FC34", "comment": "// CLK_GATE: WRITE |= 0x01000020", "status": "OK"},
    {"addr": "0x0026FC58", "comment": "// CLK_GATE: WRITE |= 0x800", "status": "OK"}
  ]
}
```

### Success Criteria
- `comments_failed == 0`
- `verification_status == "OK"`

### Cost Estimate
~$0.001 per function

---

## Profile: `ghidra-string-xref-hunter`

### Purpose
Find all callers of a string and suggest function names based on context.

### Model
`gpt-4o` (needs semantic understanding for naming suggestions)

### Input Schema
```json
{
  "string_addr": "0x0026891C",
  "string_content": "3:/ZK-INKJET-NANO-APP.bin",
  "binary": "app.bin"
}
```

### Task Description
```
Find all callers of string at {string_addr} and analyze context.

Steps:
1. get_xrefs_to(string_addr) → get caller list
2. For each caller:
   a. decompile_function_by_address(caller_addr)
   b. Extract context:
      - Function arguments (what's passed with the string?)
      - Return value usage
      - Nearby function calls
   c. Suggest descriptive function name based on context
3. Return JSON result

Use only ghidra-bridge MCP tools.
```

### Output Schema
```json
{
  "string_addr": "0x0026891C",
  "string_content": "3:/ZK-INKJET-NANO-APP.bin",
  "callers": [
    {
      "addr": "0x0026887C",
      "current_name": "FUN_0026887C",
      "suggested_name": "maybe_update_from_udisk",
      "confidence": "HIGH",
      "reasoning": "Calls update_copy_or_flash with dst=0x03000000, path='3:/...APP.bin', post_action=1",
      "context": {
        "arguments": ["dry_run=0", "dst=0x03000000", "path=string_addr", "ui_mode=1"],
        "calls": ["update_copy_or_flash"]
      }
    }
  ]
}
```

### Success Criteria
- All callers analyzed
- Naming suggestions have clear `reasoning`

### Cost Estimate
~$0.01 per string (depends on caller count)

---

## Profile: `ghidra-resource-parser`

### Purpose
Parse .zkml resource block structure and identify payload type.

### Model
`gpt-4o` (needs pattern recognition for format analysis)

### Input Schema
```json
{
  "block_addr": "0x000A3000",
  "block_size": 4096,
  "binary": "ZK-INKJET-RES-HW.zkml"
}
```

### Task Description
```
Parse resource block at {block_addr} and identify structure.

Steps:
1. read_bytes(block_addr, 256) → get header
2. Analyze header:
   - Look for: bLength, bType, checksum, magic numbers
   - Identify: TTF signature (0x00010000), BMP header (0x424D), etc.
3. If structure identified:
   - Extract payload offset and size
   - Compute checksum (if present)
   - Validate structure
4. Return JSON result

Use ghidra-bridge MCP tools for memory access.
```

### Output Schema
```json
{
  "block_addr": "0x000A3000",
  "header": {
    "bLength": 19,
    "bType": 3,
    "magic": "0x00010000"
  },
  "payload_type": "TTF_FONT",
  "payload_offset": 32,
  "payload_size": 3840,
  "checksum": "0x12345678",
  "valid": true,
  "confidence": "HIGH"
}
```

### Success Criteria
- `payload_type` identified OR `valid: false` with clear reason
- If `valid: true`, checksum matches (if applicable)

### Cost Estimate
~$0.01 per block

---

## Profile: `ghidra-function-classifier`

### Purpose
Classify unknown functions based on code patterns (e.g., CRC, memcpy, crypto).

### Model
`claude-3-5-sonnet-20241022` (best for pattern recognition)

### Input Schema
```json
{
  "function_addr": "0x0020EAEC",
  "binary": "app.bin",
  "context": "Found in update path, called before flash write"
}
```

### Task Description
```
Classify function at {function_addr} based on code patterns.

Steps:
1. decompile_function_by_address(function_addr)
2. Analyze patterns:
   - CRC: XOR loops, polynomial constants (0x04C11DB7, 0xEDB88320, 0x1021)
   - Crypto: S-boxes, key schedules, rounds
   - Memory: Simple loops with LDR/STR
   - String: Character comparisons, null-termination checks
3. Suggest function category and name
4. Return JSON result

Use ghidra-bridge MCP tools.
```

### Output Schema
```json
{
  "function_addr": "0x0020EAEC",
  "category": "MEMORY_ALLOCATOR",
  "suggested_name": "heap_block_iterator",
  "confidence": "MEDIUM",
  "evidence": [
    "Loops over linked list (node+4 = next pointer)",
    "Reads block size from node+0",
    "No XOR/polynomial constants (not CRC)",
    "No S-boxes (not crypto)"
  ],
  "similar_patterns": ["malloc", "free", "heap_walk"]
}
```

### Success Criteria
- `category` assigned with clear `evidence`
- `confidence` level justified

### Cost Estimate
~$0.02 per function

---

## Usage Guidelines

### When to use which profile:

1. **`ghidra-jt-slot-processor`** - Parallel processing of 20+ JT slots
2. **`ghidra-mmio-annotator`** - Batch annotation of 10+ functions with MMIO
3. **`ghidra-string-xref-hunter`** - Finding update/protocol handlers via strings
4. **`ghidra-resource-parser`** - Understanding .zkml/.bin resource formats
5. **`ghidra-function-classifier`** - Identifying crypto/CRC/protocol functions

### Orchestration Pattern:

```typescript
// Example: Process all JT slots in parallel
const results = await Promise.all(
  Array.from({length: 20}, (_, i) => 
    runSubagent({
      profile: "ghidra-jt-slot-processor",
      input: {slot_index: i, jt_base_candidate: "0x002000A0", ...}
    })
  )
);

// Aggregate results
const validSlots = results.filter(r => r.is_valid_pointer);
const invalidSlots = results.filter(r => !r.is_valid_pointer);
```

### Cost Optimization:

- Use `gpt-4o-mini` for repetitive tasks (JT-slots, MMIO-annotation)
- Use `gpt-4o` for semantic tasks (string-xref, resource-parsing)
- Use `claude-sonnet` for complex analysis (function-classification)

### Expected Savings:

- **Without subagents:** 20 JT slots × $0.015 = **$0.30** (20 min sequential)
- **With subagents:** 1 orchestrator × $0.015 + 20 × $0.0005 = **$0.025** (2 min parallel)
- **Savings:** 12× cheaper, 10× faster


---

## Profile: `ghidra-batch-loop-agent` ⭐ NEW

### Purpose
**Token-efficient batch executor**: Runs N subagent tasks, aggregates results to compact JSON, returns summary only (no transcripts).

### Model
`gpt-4o-mini` (cheap, sufficient for orchestration logic)

### Input Schema
```json
{
  "batch_type": "jt-scan",
  "tasks": [
    {"id": "slot_0", "slot_index": 0},
    {"id": "slot_1", "slot_index": 1},
    ...
  ],
  "config": {
    "jt_base_candidate": "0x002000A0",
    "binary": "app.bin",
    "architecture": "ARMv5T"
  }
}
```

### Task Description
```
Execute batch of {batch_type} tasks and return COMPACT summary.

CRITICAL RULES:
1. For each task in tasks[]:
   - Call appropriate subagent (e.g., ghidra-jt-slot-processor)
   - Extract ONLY result JSON (discard conversation)
   - Append to results[]
2. After all tasks complete:
   - Aggregate results to summary
   - Return ONLY: {summary, valid_items, invalid_items}
   - DO NOT include full subagent transcripts
3. Token budget: Keep output <2000 tokens

Example output:
{
  "batch_type": "jt-scan",
  "summary": {
    "total": 20,
    "valid": 3,
    "invalid": 17,
    "renamed": 3
  },
  "valid_items": [
    {"slot": 5, "target": "0x00268ABC", "mode": "Thumb"},
    {"slot": 12, "target": "0x0026FC20", "mode": "ARM"}
  ],
  "invalid_items": [
    {"slot": 0, "reason": "ARM instruction BX ip"},
    {"slot": 1, "reason": "Outside code range"}
  ]
}
```

### Output Schema
```json
{
  "batch_type": "jt-scan",
  "summary": {
    "total": 20,
    "valid": 3,
    "invalid": 17,
    "renamed": 3,
    "errors": 0
  },
  "valid_items": [...],
  "invalid_items": [...],
  "errors": []
}
```

### Success Criteria
- Output is <2000 tokens
- All task results aggregated
- No subagent transcripts included

### Cost Estimate
~$0.002 orchestration + (N × subagent_cost)

### Usage Example
```typescript
// Claude calls Loop-Agent once
const result = await runSubagent({
  profile: "ghidra-batch-loop-agent",
  input: {
    batch_type: "jt-scan",
    tasks: Array.from({length: 20}, (_, i) => ({
      id: `slot_${i}`,
      slot_index: i
    })),
    config: {
      jt_base_candidate: "0x002000A0",
      binary: "app.bin"
    }
  }
});

// Claude receives compact JSON (~500 tokens)
console.log(result.summary);
// { total: 20, valid: 3, invalid: 17 }
```

### Token Savings
- **Without Loop-Agent:** 20 subagent calls × 2500 tokens = **50,000 tokens**
- **With Loop-Agent:** 1 call × 500 tokens = **500 tokens**
- **Savings:** 100× reduction
