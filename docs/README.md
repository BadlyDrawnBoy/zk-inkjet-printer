# Documentation Index

**Last Updated:** 2025-11-03

---

## 🚀 Quick Start

- **New to the project?** Start with [`/README.md`](../README.md)
- **Looking for findings?** Check [`findings/`](findings/)
- **Want to reproduce analysis?** Check [`methodology/`](methodology/)
- **Need technical reference?** Check [`reference/`](reference/)

---

## 📁 Documentation Structure

### [`findings/`](findings/) - What We Discovered
Verified findings with confidence levels:
- [Chip Identification](findings/chip_identification.md) - N32903K5DN, 98% confidence
- [GPIO Configuration](findings/gpio_configuration.md) - Pin configuration status
- [MMIO Map](findings/mmio_map.md) - Memory-mapped registers
- [Firmware Functions](findings/firmware_functions.md) - Key functions identified

### [`methodology/`](methodology/) - How to Analyze
Analysis workflows and procedures:
- [MCP Workflow](methodology/mcp_workflow.md) - AI-assisted analysis workflow
- *(More to be added: Ghidra setup, verification checklist)*

### [`reference/`](reference/) - Technical References
Quick reference documents:
- [N32903 Cheat Sheet](reference/N32903_cheat_sheet.md) - SoC quick reference
- [MMIO Fingerprint](reference/mmio_fingerprint.md) - Register access patterns
- [Offset Catalog](reference/offset_catalog.md) - Important addresses
- [Conventions](CONVENTIONS.md) - Addressing conventions

### [`analysis/`](analysis/) - Detailed Analysis
In-depth analysis documents:
- [SoC Identification](analysis/soc_identification.md) - Complete chip identification
- [GPIO Pins Analysis](analysis/gpio_pins_analysis.md) - Detailed GPIO analysis
- [Boot Analysis Methodology](analysis/boot_analysis_methodology.md) - Boot process
- [App Message Handlers](analysis/app_message_handlers.md) - Message handling

### [`sessions/`](sessions/) - Chronological Logs
Session-by-session analysis logs:
- [Sessions Index](sessions/README.md) - Complete chronological list

### [`hardware/`](hardware/) - Hardware Documentation
Physical hardware documentation:
- [ZK-DP20 Photos](hardware/zk-dp20/photos/index.md) - Hardware photos

### [`archive/`](archive/) - Old/Deprecated Documents
Historical documents and old structure:
- [Old Structure](archive/old-structure/) - Pre-2025-11-03 organization
- [Documentation Archive](archive/documentation-20251009.md) - Old German docs

---

## 📊 Key Documents

### Current Status
- [**Verification Status**](VERIFICATION_STATUS.md) - Current confidence levels for all findings
- [**Analysis Traceability**](analysis_traceability.md) - How findings were discovered

### Planning & Procedures
- [Firmware Mod Plan](firmware_mod_plan.md) - Planned modifications
- [UART Control](uart_control_consolidated.md) - UART interface documentation
- [Update File Rules](update_file_rules.md) - Firmware update mechanism
- [Vendor Resources](vendor_resources.md) - Official documentation links

### Legal
- [Image License](IMAGE_LICENSE.md) - CC BY 4.0 for images/docs

---

## 🔍 Finding Something Specific?

### By Topic
- **Chip/SoC:** [`findings/chip_identification.md`](findings/chip_identification.md)
- **GPIO Pins:** [`findings/gpio_configuration.md`](findings/gpio_configuration.md)
- **Memory Map:** [`findings/mmio_map.md`](findings/mmio_map.md)
- **Functions:** [`findings/firmware_functions.md`](findings/firmware_functions.md)

### By Confidence Level
- **High (>90%):** See [Verification Status](VERIFICATION_STATUS.md#high-confidence-90)
- **Medium (70-90%):** See [Verification Status](VERIFICATION_STATUS.md#medium-confidence-70-90)
- **Low (<70%):** See [Verification Status](VERIFICATION_STATUS.md#low-confidence-70)

### By Date
- **Recent Sessions:** See [Sessions Index](sessions/README.md)
- **Historical:** See [Archive](archive/)

---

## 🛠️ For Contributors

### Adding New Findings
1. Document in appropriate `findings/*.md` file
2. Update `VERIFICATION_STATUS.md` with confidence level
3. Add session log to `sessions/`
4. Update cross-references

### Analysis Workflow
1. Follow [MCP Workflow](methodology/mcp_workflow.md)
2. Document all steps in session log
3. Cross-verify findings
4. Update verification status

### Documentation Standards
- Use Markdown format
- Include confidence levels
- Add cross-references
- Follow [Conventions](CONVENTIONS.md)

---

## 📝 Recent Updates

**2025-11-03:**
- ✅ Restructured documentation (findings, methodology, reference, analysis)
- ✅ Archived old structure
- ✅ Translated German cheat sheet to English
- ✅ Created navigation hub (this file)
- ✅ Verified MMIO addresses (corrected 0xB1006800 → 0xB800C000)

---

## 🔗 External Resources

- [Vendor Resources](vendor_resources.md) - Links to official documentation
- [Project Repository](https://github.com/...) - *(Add if public)*

---

**For the main project README, see [`/README.md`](../README.md)**
