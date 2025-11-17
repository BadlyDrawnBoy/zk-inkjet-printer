# Documentation Index

**Last Updated:** 2025-11-03  
**Start Here:** Pick the guide that matches your intent.

## Audience Guides

| Role | Read First | Highlights |
| --- | --- | --- |
| New contributors | [`guide/orientation.md`](guide/orientation.md) | Repository tour, setup checklist, metadata workflow. |
| Operators & toolsmiths | [`guide/operations.md`](guide/operations.md) | Runbook for decoding UI assets, verification checklist, firmware flash cookbook. |
| Researchers & writers | [`guide/research_notebook.md`](guide/research_notebook.md) | Links to methodology, traceability, and improvement backlog. |

## Verification Snapshot

Auto-generated summary sourced from findings front matter. Regenerate via `python tools/generate_verification_summary.py`.

<!-- BEGIN AUTO-GENERATED TABLE -->
| Finding | Status | Confidence | Last Verified | Provenance |
| --- | --- | --- | --- | --- |
| [Chip Identification](findings/chip_identification.md) | ✅ VERIFIED | 98% | 2025-11-03 | [session-2025-11-03-soc-identification.md](sessions/session-2025-11-03-soc-identification.md) |
| [Firmware Functions](findings/firmware_functions.md) | ✅ PARTIALLY VERIFIED | 60-99% (per function) | 2025-11-03 | [session-2025-11-03-soc-identification.md](sessions/session-2025-11-03-soc-identification.md) |
| [GPIO Configuration](findings/gpio_configuration.md) | ✅ VERIFIED | 98% | 2025-11-03 | [session-2025-11-03-soc-identification.md](sessions/session-2025-11-03-soc-identification.md) |
| [MMIO Register Map](findings/mmio_map.md) | ✅ PARTIALLY VERIFIED | 90-99% (per register) | 2025-11-03 | [session-2025-11-03-soc-identification.md](sessions/session-2025-11-03-soc-identification.md) |
<!-- END AUTO-GENERATED TABLE -->

## Directory Map

- [`findings/`](findings/) – Canonical statements of what we know (chip ID, GPIO configuration, MMIO map, firmware functions).
- [`analysis/`](analysis/) – Long-form investigations backing those findings.
- [`methodology/`](methodology/) – Process documentation such as the MCP workflow.
- [`reference/`](reference/) – Cheat sheets, register fingerprints, offset catalogs, and conventions.
- [`sessions/`](sessions/) – Chronological research logs.
- [`hardware/`](hardware/) – Photo galleries and hardware notes.
- [`archive/`](archive/) – Historical documents and preserved automation artifacts.

## Keeping Docs in Sync

1. Update the relevant finding and its YAML front matter.
2. Record supporting evidence in a session log and reference it from `analysis_traceability.md`.
3. Run `python tools/generate_verification_summary.py` to refresh the verification snapshot here and in [`VERIFICATION_STATUS.md`](VERIFICATION_STATUS.md).
4. Mention any archival context or new workflows in the appropriate guide.

## Quick Links

- [`analysis_traceability.md`](analysis_traceability.md) – Command-level provenance index.
- [`archive/firmware_mod_plan_legacy.md`](archive/firmware_mod_plan_legacy.md) – Retired experimentation roadmap (pre-Nuvoton confirmation).
- [`uart_control_consolidated.md`](uart_control_consolidated.md) – UART interaction details.
- [`vendor_resources.md`](vendor_resources.md) – Official manuals and SDK references.
- [`archive/README.md`](archive/README.md) – Why and when to consult historical files.

Documentation improvements should now flow through the audience guides and findings metadata rather than duplicating status tables.
