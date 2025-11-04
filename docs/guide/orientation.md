# Orientation Guide

> Start here if you are new to the project or need a refresher on where things live.

## Project Snapshot

- **Goal:** Reverse engineer the ZK-INKJET handheld printer firmware and document reproducible tooling for working with the platform.
- **Hardware Focus:** Nuvoton N32903K5DN SoC ("DWIN M5" marking) paired with HP45(SI) cartridges.
- **Current Status:** Core documentation restructure completed on 2025-11-03. Verification data now lives in front matter within the findings.

## First-Day Checklist

1. **Read the repository overview:** [`README.md`](../README.md) explains the dataset layout, tooling, and licensing.
2. **Confirm your environment:**
   - Python 3.10+
   - `pip install -r requirements-dev.txt`
   - Optional: set `GHIDRA_HOME` to enable callgraph generation targets.
3. **Skim recent sessions:** [`docs/sessions/`](../sessions/) captures chronological research updates. Start with the latest entry for context.
4. **Review verification summary:** [`docs/VERIFICATION_STATUS.md`](../VERIFICATION_STATUS.md) now embeds an auto-generated table sourced from findings front matter.

## Documentation Map

| Audience | Where to Go | Why |
| --- | --- | --- |
| Operators & toolsmiths | [`guide/operations.md`](operations.md) | Runbook for decoding UI assets, verifying outputs, and flashing firmware.
| Deep-dive researchers | [`guide/research_notebook.md`](research_notebook.md) | Pointers to methodology, traceability logs, and curated findings.
| Archivists | [`archive/README.md`](../archive/README.md) | Narrative for historical files and superseded plans.

## How Findings Stay in Sync

- Every document inside [`docs/findings/`](../findings/) carries YAML front matter that tracks status, confidence, provenance session, and last verification date.
- The helper script [`tools/generate_verification_summary.py`](../../tools/generate_verification_summary.py) regenerates summary tables inside `docs/VERIFICATION_STATUS.md` and `docs/README.md`.
- After editing a finding, run:
  ```bash
  python tools/generate_verification_summary.py
  ```
  Commit both the updated finding and regenerated tables together.

## Contributing Safely

- Log each investigation step in the relevant [`docs/sessions/`](../sessions/) entry to preserve traceability.
- Treat raw binaries as untrusted; follow the safety notes in [`scripts/`](../../scripts/) and the repository root `AGENTS.md`.
- When in doubt about terminology or address formatting, consult [`docs/CONVENTIONS.md`](../CONVENTIONS.md).

Happy hacking! The guides in this directory are lightweight by design—feel free to extend them as workflows evolve.
