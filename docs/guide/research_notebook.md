# Research Notebook Index

> Use this guide to dive into detailed analysis, methodology, and traceability records.

## Core Pillars

| Theme | Primary Document | Why it matters |
| --- | --- | --- |
| Findings | [`docs/findings/`](../findings/) | Each file now exposes status metadata in YAML front matter; sections capture evidence and open questions. |
| Methodology | [`docs/methodology/mcp_workflow.md`](../methodology/mcp_workflow.md) | Step-by-step outline of the multi-agent MCP workflow used to analyze firmware artifacts. |
| Traceability | [`docs/analysis_traceability.md`](../analysis_traceability.md) | High-level index of reproducible command sequences with links into session logs. |

## Working with Metadata

- Front matter keys: `title`, `status`, `status_display`, `confidence`, `last_verified`, `provenance`.
- `provenance` should point to a session log in [`docs/sessions/`](../sessions/).
- When updating findings, adjust both the narrative body and metadata fields. Run `python tools/generate_verification_summary.py` afterwards.

## Navigating Detailed Analysis

- **Hardware deep dives:** [`docs/analysis/gpio_pins_analysis.md`](../analysis/gpio_pins_analysis.md), [`docs/findings/chip_identification.md`](../findings/chip_identification.md)
- **Boot process & loaders:** [`docs/analysis/boot_analysis_methodology.md`](../analysis/boot_analysis_methodology.md)
- **Message handling:** [`docs/analysis/app_message_handlers.md`](../analysis/app_message_handlers.md)

Each analysis document should reference supporting sessions and, where possible, cross-link back to the relevant finding.

## Maintaining Traceability

1. Log every investigative command in a session file (`docs/sessions/session-*.md`).
2. Summaries in `docs/analysis_traceability.md` should reference those sessions by filename and timestamp.
3. If evidence changes a finding's confidence, update the front matter and regenerate the verification summary.

## Suggested Enhancements

- Add more granular methodology pages (e.g., "Ghidra project setup", "UART capture pipeline").
- Convert long disassembly listings into referenced code blocks stored under `data/processed/` when possible.
- Expand the sessions index with tags for quick filtering (hardware vs firmware vs UI).

This notebook view keeps the historical research narrative discoverable without overwhelming the operational guides.
