# Verification Status – ZK-INKJET Firmware Analysis

**Last Updated:** 2025-11-03  
**Project:** ZK-INKJET Printer Reverse Engineering  
**Chip:** Nuvoton N32903K5DN ("DWIN M5" branding)

> This page is driven by the YAML front matter embedded in each file under [`docs/findings/`](findings/). Regenerate the summary after modifying a finding by running `python tools/generate_verification_summary.py`.

## Summary of Findings

<!-- BEGIN AUTO-GENERATED TABLE -->
| Finding | Status | Confidence | Last Verified | Provenance |
| --- | --- | --- | --- | --- |
| [Chip Identification](findings/chip_identification.md) | ✅ VERIFIED | 98% | 2025-11-03 | [session-2025-11-03-soc-identification.md](sessions/session-2025-11-03-soc-identification.md) |
| [Firmware Functions](findings/firmware_functions.md) | ✅ PARTIALLY VERIFIED | 60-99% (per function) | 2025-11-03 | [session-2025-11-03-soc-identification.md](sessions/session-2025-11-03-soc-identification.md) |
| [GPIO Configuration](findings/gpio_configuration.md) | ✅ VERIFIED | 98% | 2025-11-03 | [session-2025-11-03-soc-identification.md](sessions/session-2025-11-03-soc-identification.md) |
| [MMIO Register Map](findings/mmio_map.md) | ✅ PARTIALLY VERIFIED | 90-99% (per register) | 2025-11-03 | [session-2025-11-03-soc-identification.md](sessions/session-2025-11-03-soc-identification.md) |
<!-- END AUTO-GENERATED TABLE -->

## Status Legend

| Symbol | Meaning |
| --- | --- |
| ✅ VERIFIED | High confidence, independently reproduced. |
| ✅ PARTIALLY VERIFIED | Mixed confidence across subsections; see the document body for details. |
| ⚠️ LIKELY | Strong evidence but missing direct hardware confirmation. |
| ❓ HYPOTHESIS | Needs additional verification or supporting data. |

## Update Workflow

1. Edit the relevant finding in [`docs/findings/`](findings/), updating both the narrative and its front matter keys.
2. Log supporting evidence in [`docs/sessions/`](sessions/) and summarize commands in [`docs/analysis_traceability.md`](analysis_traceability.md).
3. Run `python tools/generate_verification_summary.py` to refresh the table above and the quick index in [`docs/README.md`](README.md).
4. Commit the updated finding, regenerated tables, and session notes together.

## Deep Dives

- Operational walkthroughs live in [`docs/guide/operations.md`](guide/operations.md).
- Research context and improvement ideas are tracked in [`docs/guide/research_notebook.md`](guide/research_notebook.md).
- For historic decisions, consult the archive overview at [`docs/archive/README.md`](archive/README.md).

This status page should remain lean—treat the linked findings as the source of truth for evidence, disassembly snippets, and outstanding questions.
