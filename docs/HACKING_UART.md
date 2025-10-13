# UART hook plan

This file now serves as a light-weight index that points to the consolidated UART reference. All actionable guidance, hardware context, protocol framing, and firmware hook strategy have been merged into `docs/uart_control_consolidated.md`.

If you need UART-specific planning details, including baud-rate hypotheses, handler hook procedures, and vendor reference links, consult the consolidated note instead of this legacy draft.

## Maintaining historical context

- Retain any **new** experimental notes here only when they are still rough. Once validated, migrate the findings into the consolidated reference and replace the temporary section with a pointer.
- Keep hardware captures and command transcripts logged under `docs/analysis_traceability.md`; link to those entries from the consolidated note when promoting the content.

This approach keeps the working plan tidy while preserving a scratchpad for in-progress experiments.
