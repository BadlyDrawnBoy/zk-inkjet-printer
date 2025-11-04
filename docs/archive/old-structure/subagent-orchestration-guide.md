# Subagent Orchestration Guide

> [⤴ Back to archive overview](../README.md)




## Overview
This guide explains how to use subagents for parallel firmware analysis tasks.

---

## Quick Start

### 1. Single Subagent Test
```typescript
// Test with JT-Slot 0
const result = await runSubagent({
  profile: "code-verification",  // Use gpt-4o-mini
  prompt: `
    Analyze Jump-Table slot 0 in app.bin (Ghidra MCP).
    
    Context:
    - Binary: app.bin (ARMv5T, Nuvoton N3290X)
    - JT_BASE candidate: 0x002000A0
    - Slot 0 address: 0x002000A0
    
    Steps:
    1. read_dword(0x002000A0)
    2. Check if value is valid pointer (not instruction)
    3. If valid: test ARM(value) and Thumb(value-1)
    4. If function found: rename + comment
    5. Return JSON with status
    
    Use ghidra-bridge MCP tools only.
  `
});

console.log(result);
```

### 2. Parallel Batch Processing
```typescript
// Process JT slots 0-19 in parallel
const slots = Array.from({length: 20}, (_, i) => i);

const results = await Promise.all(
  slots.map(slot => runSubagent({
    profile: "code-verification",
    prompt: generateJTSlotPrompt(slot)  // See templates below
  }))
);

// Aggregate results
const valid = results.filter(r => r.is_valid_pointer);
const invalid = results.filter(r => !r.is_valid_pointer);

console.log(`Valid: ${valid.length}, Invalid: ${invalid.length}`);
```

---

## Prompt Templates

### Template: JT-Slot-Processor
```typescript
function generateJTSlotPrompt(slotIndex: number): string {
  return `
Analyze Jump-Table slot ${slotIndex} in app.bin (Ghidra MCP).

Context:
- Binary: app.bin (ARMv5T, Nuvoton N3290X)
- JT_BASE: 0x002000A0
- Slot ${slotIndex} address: ${toHex(0x002000A0 + slotIndex * 4)}

Steps:
1. read_dword(${toHex(0x002000A0 + slotIndex * 4)})
2. Validate pointer (not instruction, in range 0x00200000-0x00475000)
3. If valid:
   - Test ARM: disassemble_function(value)
   - Test Thumb: disassemble_function(value-1)
4. If function found:
   - rename_function_by_address(addr, "dispatch_handler_${slotIndex.toString().padStart(2, '0')}_tbd")
   - set_decompiler_comment(addr, "JT slot ${slotIndex} handler")
   - Verify via get_function_by_address
5. Return JSON:
   {
     "slot": ${slotIndex},
     "slot_addr": "0x...",
     "raw_value": "0x...",
     "is_valid_pointer": true|false,
     "target_addr": "0x..." | null,
     "mode": "ARM"|"Thumb"|"INVALID",
     "reason": "..." | null,
     "function_renamed": true|false,
     "verification_status": "OK"|"FAILED"|"N/A"
   }

Use only ghidra-bridge MCP tools. Follow Write→Verify pattern.
  `.trim();
}
```

### Template: MMIO-Annotator
```typescript
function generateMMIOAnnotatorPrompt(
  functionAddr: string,
  registers: Array<{addr: string, name: string, desc: string}>
): string {
  const regList = registers.map(r => 
    `- ${r.addr}: ${r.name} (${r.desc})`
  ).join('\n');

  return `
Annotate MMIO accesses in function at ${functionAddr} (Ghidra MCP).

MMIO Registers:
${regList}

Steps:
1. disassemble_function(${functionAddr})
2. For each LDR/STR to MMIO addresses:
   - Identify operation (READ/WRITE, |=, &=, toggle)
   - set_disassembly_comment(addr, "// {reg_name}: {operation}")
3. Verify via disassemble_function
4. Return JSON:
   {
     "function_addr": "${functionAddr}",
     "comments_added": N,
     "comments_failed": 0,
     "verification_status": "OK",
     "details": [...]
   }

Use only ghidra-bridge MCP tools.
  `.trim();
}
```

---

## Orchestration Patterns

### Pattern 1: Sequential with Dependencies
```typescript
// Step 1: Find JT_BASE
const jtBase = await runSubagent({
  profile: "codebase-analysis",
  prompt: "Scan literal pool 0x00200090-0x002000B0 for valid pointers"
});

// Step 2: Process slots (depends on Step 1)
const slots = await Promise.all(
  Array.from({length: 20}, (_, i) => 
    runSubagent({
      profile: "code-verification",
      prompt: generateJTSlotPrompt(i, jtBase.result)
    })
  )
);
```

### Pattern 2: Parallel Independent Tasks
```typescript
// All tasks can run in parallel
const [jtResults, mmioResults, stringResults] = await Promise.all([
  // JT slots 0-19
  Promise.all(slots.map(i => runSubagent({...}))),
  
  // MMIO annotation for 10 functions
  Promise.all(functions.map(f => runSubagent({...}))),
  
  // String xref hunting for 50 strings
  Promise.all(strings.map(s => runSubagent({...})))
]);
```

### Pattern 3: Retry on Failure
```typescript
async function runWithRetry(config, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const result = await runSubagent(config);
      if (result.verification_status === "OK") {
        return result;
      }
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(1000 * (i + 1));  // Exponential backoff
    }
  }
}
```

---

## Result Aggregation

### Aggregate JT-Slot Results
```typescript
function aggregateJTResults(results: JTSlotResult[]) {
  const summary = {
    total: results.length,
    valid: results.filter(r => r.is_valid_pointer).length,
    invalid: results.filter(r => !r.is_valid_pointer).length,
    arm: results.filter(r => r.mode === "ARM").length,
    thumb: results.filter(r => r.mode === "Thumb").length,
    renamed: results.filter(r => r.function_renamed).length
  };

  const validSlots = results
    .filter(r => r.is_valid_pointer)
    .map(r => ({
      slot: r.slot,
      target: r.target_addr,
      mode: r.mode
    }));

  return { summary, validSlots };
}
```

### Generate Report
```typescript
function generateReport(results: JTSlotResult[]): string {
  const agg = aggregateJTResults(results);
  
  return `
# Jump-Table Analysis Report

## Summary
- Total slots: ${agg.summary.total}
- Valid pointers: ${agg.summary.valid}
- Invalid: ${agg.summary.invalid}
- ARM mode: ${agg.summary.arm}
- Thumb mode: ${agg.summary.thumb}
- Functions renamed: ${agg.summary.renamed}

## Valid Slots
${agg.validSlots.map(s => 
  `- Slot ${s.slot}: ${s.target} (${s.mode})`
).join('\n')}
  `.trim();
}
```

---

## Cost Optimization

### Model Selection
```typescript
const PROFILES = {
  // Cheap & fast for repetitive tasks
  repetitive: {
    model: "gpt-4o-mini",
    cost_per_call: 0.0005,
    use_for: ["JT-slots", "MMIO-annotation"]
  },
  
  // Medium cost for semantic tasks
  semantic: {
    model: "gpt-4o",
    cost_per_call: 0.01,
    use_for: ["string-xref", "resource-parsing"]
  },
  
  // Expensive for complex analysis
  complex: {
    model: "claude-3-5-sonnet",
    cost_per_call: 0.02,
    use_for: ["function-classification", "protocol-analysis"]
  }
};
```

### Cost Estimation
```typescript
function estimateCost(tasks: Task[]): number {
  return tasks.reduce((total, task) => {
    const profile = PROFILES[task.complexity];
    return total + (profile.cost_per_call * task.count);
  }, 0);
}

// Example
const cost = estimateCost([
  { complexity: "repetitive", count: 20 },  // JT slots
  { complexity: "repetitive", count: 10 },  // MMIO functions
  { complexity: "semantic", count: 5 }      // String xrefs
]);

console.log(`Estimated cost: $${cost.toFixed(3)}`);
// Output: Estimated cost: $0.065
```

---

## Error Handling

### Validation
```typescript
function validateResult(result: any, schema: any): boolean {
  // Check required fields
  for (const field of schema.required) {
    if (!(field in result)) {
      console.error(`Missing required field: ${field}`);
      return false;
    }
  }
  
  // Check types
  for (const [field, type] of Object.entries(schema.types)) {
    if (typeof result[field] !== type) {
      console.error(`Invalid type for ${field}: expected ${type}`);
      return false;
    }
  }
  
  return true;
}
```

### Recovery
```typescript
async function runWithFallback(config: SubagentConfig) {
  try {
    return await runSubagent(config);
  } catch (error) {
    console.warn(`Subagent failed: ${error.message}`);
    
    // Fallback: Run with main agent
    return await runMainAgent(config.prompt);
  }
}
```

---

## Best Practices

### 1. Start Small
- Test with 1 subagent first
- Verify output format
- Then scale to parallel batch

### 2. Clear Prompts
- Include full context (binary, architecture, SoC)
- Specify exact steps
- Define output format (JSON schema)

### 3. Verify Results
- Check `verification_status` field
- Validate JSON schema
- Spot-check random samples

### 4. Monitor Costs
- Track API calls per task
- Compare estimated vs. actual costs
- Optimize model selection

### 5. Document Findings
- Save subagent results to files
- Generate human-readable reports
- Update analysis_traceability.md

---

## Example: Complete JT-Scan Workflow

```typescript
async function scanJumpTable() {
  console.log("Starting Jump-Table scan...");
  
  // Step 1: Process all slots in parallel
  const slots = Array.from({length: 20}, (_, i) => i);
  const results = await Promise.all(
    slots.map(slot => runSubagent({
      profile: "code-verification",
      prompt: generateJTSlotPrompt(slot)
    }))
  );
  
  // Step 2: Validate results
  const valid = results.filter(r => 
    validateResult(r, JT_SLOT_SCHEMA)
  );
  
  if (valid.length !== results.length) {
    console.warn(`${results.length - valid.length} invalid results`);
  }
  
  // Step 3: Aggregate
  const summary = aggregateJTResults(valid);
  
  // Step 4: Generate report
  const report = generateReport(valid);
  await fs.writeFile("docs/jt-scan-report.md", report);
  
  // Step 5: Update traceability
  await updateTraceability({
    task: "Jump-Table Scan",
    date: new Date().toISOString(),
    results: summary
  });
  
  console.log("Jump-Table scan complete!");
  console.log(summary);
}
```

---

## Next Steps

1. **Test single subagent** with JT-Slot 0
2. **Validate output format** matches schema
3. **Scale to 5 slots** (small batch test)
4. **Full parallel scan** (20 slots)
5. **Repeat for MMIO** annotation
6. **Document results** in repository
