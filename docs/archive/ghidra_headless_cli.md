# Legacy Ghidra Headless CLI Workflow

This note preserves the first-generation Ghidra automation that lived under `scripts/gh.sh` before migrating to the MCP-based tooling. The archived shell wrapper still exists at `docs/archive/tools/ghidra_headless.sh`.

## Background

Early sessions orchestrated Ghidra entirely through `analyzeHeadless`, using a local wrapper to pin cache/config/tmp paths and to invoke bespoke post-scripts such as `export_io_callgraph.py` and `export_upgrade_orchestrator_disasm.py` [docs/archive/2025-10-10-session-notes.md:7-44]. The script imported `data/raw/ZK-INKJET-NANO-APP.bin` via the `BinaryLoader`, created a throwaway project under `.ghidra_tmp`, and wrote outputs into `data/processed/`.

## Workflow Snapshot

```
./scripts/gh.sh ghidra_projects inkjet_project \
    -import data/raw/ZK-INKJET-NANO-APP.bin \
    -loader BinaryLoader -processor ARM:LE:32:v5
```
```
./scripts/gh.sh ghidra_projects inkjet_project \
    -process ZK-INKJET-NANO-APP.bin \
    -scriptPath "$(pwd)/ghidra_scripts" \
    -postscript export_io_callgraph.py "$(pwd)/data/processed/io_callgraph.json"
```

These invocations (mirrored in the October 2025 session notes) illustrate how the wrapper chained auto-analysis with custom exporters [docs/archive/2025-10-10-session-notes.md:26-44].

## Known Limitations

- Context handling: the call-graph export routinely stalled because mixed ARM/Thumb regions were not re-tagged before analysis, causing the exporter to emit only the root node [docs/archive/2025-10-10-session-notes.md:17-24].
- Operational fragility: the wrapper required `GHIDRA_HOME` plus manually managed cache directories, producing brittle runs when invoked outside the repo root [docs/archive/2025-10-10-session-notes.md:9-15].

These shortcomings made it difficult to keep automation reproducible once broader decoding tasks ramped up.

## Migration & Current Guidance

The MCP-based Ghidra bridge now exposes search/disassembly APIs directly inside the assisted workflow, eliminating the need for the headless wrapper. See `AGENTS.md` and the session logs dated 2025-11-03 onward for the supported tooling surface [docs/sessions/README.md:5-18]. The archived shell script is retained only for historical reference; new automations should prefer the live MCP integration.

## Discovery Timeline (Quick Reference)

- 2025-01-25 – First reliable SoC identification (N32903K5DN) captured in the sessions index [docs/sessions/README.md:12-15].
- 2025-10-10 – Headless wrapper documented with upgrade I/O mapping research, highlighting the Thumb/ARM call-graph blocker [docs/archive/2025-10-10-session-notes.md:7-44].
- 2025-11-03 – GPIO/MMIO-focused session kicked off the structured, MCP-backed documentation process [docs/sessions/README.md:5-11].

If more granular provenance is needed, extend this list by linking to specific entries inside `docs/sessions/` or by annotating future artifacts with the `analysis_traceability.md` workflow.
