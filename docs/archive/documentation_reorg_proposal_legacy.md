# Documentation Reorganization Proposal (2025-11) *(Archived)*

> Archived: this proposal was implemented during the 2025-11 restructure. Current improvement ideas live in `docs/guide/research_notebook.md#suggested-enhancements`.

## 1. Current Observations

### 1.1 Competing structural narratives
- `docs/CLEANUP_PLAN.md` still reads as an unapproved draft describing a future restructure, while `docs/RESTRUCTURE_COMPLETE.md` claims the exact plan was finished. The coexistence of both makes it unclear whether the current layout is final or still in flux.
- Contributors reading the top of `docs/CLEANUP_PLAN.md` are instructed to await approval before executing the plan, yet the completion report states that the moves already happened and even lists post-completion TODO items. This tension can confuse newcomers who are trying to decide which document is authoritative.

### 1.2 Navigation gaps for different audiences
- The root `README.md` provides a solid repository overview but delegates all documentation specifics to the docs tree without guiding different audience types (reverse engineers, hardware tinkerers, firmware builders) toward the most relevant subsections.
- `docs/README.md` is an exhaustive index of everything under `docs/`, but it reads linearly and does not help readers jump directly into workflows (e.g., "I want to reproduce the UI decode pipeline" or "I only need the verified memory map").

### 1.3 Evidence and status metadata are scattered
- Confidence levels, verification states, and provenance live in `docs/VERIFICATION_STATUS.md`, individual findings (e.g., `docs/findings/firmware_functions.md`), and the traceability log. Because each file maintains its own tables, contributors must edit multiple places after a single discovery. This makes it easy to drift out of sync.
- Long-form methodology (e.g., `docs/methodology/mcp_workflow.md`) and practical "how do I run the scripts?" guidance in the root `README.md` overlap partially but live far apart. Operational contributors still need a unified "runbook".

### 1.4 Archives are preserved but difficult to mine
- `docs/archive/old-structure/` successfully retains the pre-2025 layout; however, it mixes historically important artifacts (e.g., full traceability dump) with superseded navigation files. There is no summary explaining what a reader might learn from the archive or when to consult it.

## 2. Proposed Information Architecture

### 2.1 Audience-based entry points
Create three top-level navigation lenses:
1. **Orientation** – For new contributors. A concise "Start here" guide that combines the existing repository quick start, a documentation primer, and links to the most recent session summaries.
2. **Operations** – For people running tools or reproducing results. Aggregate quick commands, data dependencies, and verification checklists into a single runbook.
3. **Research Notebook** – For deep-dive analysis. Surface findings, methodology, and traceability with consistent metadata panels and cross-links.

Implementation detail: Keep the physical directory layout but add new markdown stubs that reframe the existing content (e.g., `docs/guide/orientation.md`, `docs/guide/operations.md`, `docs/guide/research_notebook.md`). Each stub can curate links into the existing sections rather than moving files again.

### 2.2 Metadata consolidation
Introduce a lightweight YAML front matter block across findings that captures status, confidence, provenance session, and last verification date. Add a script (or markdown include) that auto-renders a summary table in `docs/VERIFICATION_STATUS.md` and `docs/README.md` so that the information stays synchronized.

### 2.3 Archive signposting
Add an `archive/README.md` that categorizes legacy content (e.g., "historical planning", "raw logs", "deprecated prompts") and notes why each subgroup matters. Link this summary from both the orientation guide and the documentation index.

### 2.4 Workflow unification
Draft a "UI Decode to Firmware Flash" cookbook that chains the examples now spread between the root `README.md`, `docs/methodology/mcp_workflow.md`, and findings. Highlight prerequisites, commands, and expected artifacts. This can live under the Operations lens and reference specific scripts.

## 3. Suggested Implementation Plan

1. **Resolve structural ambiguity**
   - Archive or rewrite `docs/CLEANUP_PLAN.md` to acknowledge completion and point readers to `docs/RESTRUCTURE_COMPLETE.md`.
   - Update `docs/RESTRUCTURE_COMPLETE.md` with a short status banner summarizing the current steady-state and linking to ongoing improvement tasks.

2. **Create audience guides**
   - Add a `docs/guide/` folder containing the orientation, operations runbook, and research notebook index.
   - Update the root `README.md` and `docs/README.md` to link to these guides in their first section.

3. **Standardize metadata**
   - Agree on a front-matter schema, retrofit it into priority findings, and add a helper script to regenerate status tables.
   - Refactor `docs/VERIFICATION_STATUS.md` to consume the generated table instead of maintaining its own copy.

4. **Enhance archive discoverability**
   - Write `docs/archive/README.md` describing each archived subtree and when to consult it.
   - Add breadcrumb links from archived documents back to the archive index for context.

5. **Document primary workflows**
   - Author the UI decode → verification cookbook in the operations guide.
   - Capture reproducible command blocks and reference outputs to keep analysis traceability intact.

## 4. Expected Outcomes

- **Lower onboarding friction**: newcomers can self-select into the guide that matches their intent.
- **Consistent verification data**: status tables are generated from a single source of truth.
- **Traceable history without clutter**: archives remain accessible while clearly separated from active documentation.
- **Reproducible operations**: core workflows are described in one place, reducing guesswork during future analyses.
