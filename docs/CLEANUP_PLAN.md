# Documentation Cleanup Plan

**Created:** 2025-11-03  
**Status:** DRAFT - Needs approval before execution

---

## Current Problems

1. **Multiple "main" documents** (README.md, documentation.md, README_NEW_STRUCTURE.md)
2. **Outdated documents** (session_status.md, status_dashboard.md, documentation.md)
3. **Unclear structure** (new findings/ vs old root docs/)
4. **Language mix** (mostly English, some German)
5. **Redundant information** across multiple files

---

## Proposed Structure

```
/
├── README.md                          # Main entry point (keep, update)
│
├── docs/
│   ├── README.md                      # NEW: Navigation hub
│   │
│   ├── findings/                      # ✅ What was found
│   │   ├── chip_identification.md
│   │   ├── gpio_configuration.md
│   │   ├── mmio_map.md
│   │   └── firmware_functions.md
│   │
│   ├── methodology/                   # ✅ How to analyze
│   │   ├── mcp_workflow.md
│   │   ├── ghidra_setup.md           # TODO
│   │   └── verification_checklist.md # TODO
│   │
│   ├── reference/                     # NEW: Technical references
│   │   ├── N32903_cheat_sheet.md     # Rename from CheatCheet.txt
│   │   ├── mmio_fingerprint.md       # Move here
│   │   ├── offset_catalog.md         # Move here
│   │   └── CONVENTIONS.md            # Keep here
│   │
│   ├── analysis/                      # NEW: Detailed analysis docs
│   │   ├── soc_identification.md     # Move here
│   │   ├── gpio_pins_analysis.md     # Move here
│   │   ├── boot_analysis_methodology.md  # Move here
│   │   └── app_message_handlers.md   # Move here
│   │
│   ├── sessions/                      # ✅ Chronological logs
│   │   ├── README.md
│   │   └── session-*.md
│   │
│   ├── archive/                       # ✅ Old/deprecated docs
│   │   ├── documentation-20251009.md # Already there
│   │   ├── documentation.md          # MOVE HERE (German, outdated)
│   │   ├── session_status.md         # MOVE HERE
│   │   ├── status_dashboard.md       # MOVE HERE
│   │   └── storage_probe_notes.md    # MOVE HERE
│   │
│   ├── hardware/                      # ✅ Hardware docs (keep as-is)
│   │   └── zk-dp20/
│   │
│   ├── subagent-prompts/              # ✅ Keep if still used
│   │
│   ├── analysis_traceability.md       # ✅ Compact overview
│   ├── VERIFICATION_STATUS.md         # ✅ Current status
│   ├── firmware_mod_plan.md           # Keep (planning doc)
│   ├── uart_control_consolidated.md   # Keep (technical doc)
│   ├── IMAGE_LICENSE.md               # Keep (legal)
│   └── vendor_resources.md            # Check if empty → archive
```

---

## Actions Required

### Phase 1: Archive Old/Redundant Docs

**Move to docs/archive/:**
- [ ] `docs/documentation.md` (German, outdated "Stand 09.10.2025")
- [ ] `docs/session_status.md` (superseded by VERIFICATION_STATUS.md)
- [ ] `docs/status_dashboard.md` (superseded by VERIFICATION_STATUS.md)
- [ ] `docs/storage_probe_notes.md` (old notes)
- [ ] `docs/README_NEW_STRUCTURE.md` (temporary meta-doc)
- [ ] `docs/analysis_traceability_FULL_ARCHIVE.md` (already archived)

### Phase 2: Create New Structure

**Create docs/reference/:**
- [ ] Move `mmio_fingerprint.md` → `docs/reference/`
- [ ] Move `offset_catalog.md` → `docs/reference/`
- [ ] Rename `N32903U5DN_K5DN_CheatCheet.txt` → `docs/reference/N32903_cheat_sheet.md`

**Create docs/analysis/:**
- [ ] Move `soc_identification.md` → `docs/analysis/`
- [ ] Move `gpio_pins_analysis.md` → `docs/analysis/`
- [ ] Move `boot_analysis_methodology.md` → `docs/analysis/`
- [ ] Move `app_message_handlers.md` → `docs/analysis/`

### Phase 3: Create Navigation Hub

**Create docs/README.md:**
```markdown
# Documentation Index

## Quick Start
- **New to the project?** Start with `/README.md`
- **Looking for findings?** Check `findings/`
- **Want to reproduce?** Check `methodology/`

## Structure
- `findings/` - What we discovered
- `methodology/` - How to analyze
- `reference/` - Technical references
- `analysis/` - Detailed analysis documents
- `sessions/` - Chronological logs
- `hardware/` - Hardware documentation
- `archive/` - Old/deprecated documents

## Key Documents
- [Chip Identification](findings/chip_identification.md) - N32903K5DN, 98% confidence
- [GPIO Configuration](findings/gpio_configuration.md) - Pin configuration status
- [MMIO Map](findings/mmio_map.md) - Memory-mapped registers
- [Verification Status](VERIFICATION_STATUS.md) - Current confidence levels
```

### Phase 4: Update Root README.md

**Update sections:**
- [ ] Add link to `docs/README.md` for navigation
- [ ] Update "Directory structure" section
- [ ] Add "Documentation" section pointing to key docs

### Phase 5: Check/Clean Subagent Docs

**Evaluate:**
- [ ] `subagent-orchestration-guide.md` - Still relevant?
- [ ] `subagent-profiles-reverse-engineering.md` - Still relevant?
- [ ] `subagent-prompts/` - Still used?

**Decision:** Keep or move to archive?

### Phase 6: Language Consistency

**German documents:**
- [ ] `docs/documentation.md` → Archive (already planned)
- [ ] `N32903U5DN_K5DN_CheatCheet.txt` → Keep but note it's German

**Decision:** Keep German technical references, but main docs in English

---

## Verification Checklist

After cleanup:
- [ ] All links in README.md work
- [ ] All cross-references in docs/ work
- [ ] No broken links
- [ ] No duplicate information
- [ ] Clear navigation path for new users
- [ ] Archive is clearly marked as "old"

---

## Rollback Plan

Before starting:
1. Create git branch: `git checkout -b docs-cleanup`
2. Commit current state: `git commit -am "Before cleanup"`
3. If something breaks: `git checkout main`

---

## Approval Needed

**This is a DRAFT plan. Please review and approve before execution.**

Questions:
1. Keep subagent docs or archive?
2. Keep German cheat sheet or translate?
3. Any other docs to preserve?
