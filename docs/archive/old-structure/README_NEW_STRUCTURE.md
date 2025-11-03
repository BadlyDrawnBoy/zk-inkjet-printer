# Documentation Structure (Updated 2025-11-03)

## New Organization

### docs/findings/ - What was found
- `chip_identification.md` - N32903K5DN, 98% confidence
- `gpio_configuration.md` - GPB[0], GPB[6] configured; GPB[2-5] NOT configured
- `mmio_map.md` - Verified MMIO addresses
- `firmware_functions.md` - Key functions with confidence levels

### docs/methodology/ - How to analyze
- `mcp_workflow.md` - MCP-based analysis workflow
- (More to be added: ghidra_setup.md, verification_checklist.md)

### docs/sessions/ - Chronological logs
- `README.md` - Index of all sessions
- Individual session files with detailed logs

### Root docs/ - Reference documents
- `analysis_traceability.md` - Quick reference + session index
- `VERIFICATION_STATUS.md` - Current verification status
- `soc_identification.md` - Detailed SoC analysis
- `gpio_pins_analysis.md` - Detailed GPIO analysis
- etc.

## Migration Status

✅ Created: findings/ directory with 4 documents
✅ Created: methodology/ directory with 1 document
✅ Created: sessions/README.md
⏳ TODO: Restructure analysis_traceability.md
⏳ TODO: Add more methodology documents

## Usage

- **Quick lookup:** Check `docs/findings/`
- **How to reproduce:** Check `docs/methodology/`
- **Historical context:** Check `docs/sessions/`
- **Detailed analysis:** Check root `docs/` files
