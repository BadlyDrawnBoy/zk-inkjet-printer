# UART Control Consolidated Notes

This note consolidates the actionable conclusions that were previously split across `docs/HACKING_UART.md`, `docs/vendor_resources.md`, and the legacy `docs/archive/firmware_mod_plan_legacy.md`. It keeps the UART-specific plan, supporting vendor context, and firmware integration steps in one place.

## Hardware Context
- **Platform**: The installed SoC is marked **M5 (DWIN)**. No primary datasheet is available, so the working assumption is functional similarity with the **T5L** family. Treat this as *unconfirmed* until proven on hardware.
- **Test Pads**: A four-pin header on the cartridge adapter exposes UART signals. Idle level around **3.3 V** suggests direct TTL access without additional level shifting.

## UART Interfaces
- **Probe Order**: Start with **UART4 @ 115200 8N1** based on DWIN sample projects. If silent, cycle through UART2 and UART5 at the same settings. Capture first-boot activity for 0–5 seconds to confirm line usage.
- **Baud Calculation**: Vendor sample code defines `FOSC = 206_438_400` and initialises UART2/4/5 with divisors:
  - `Uart2_Init`: `i = 1024 - FOSC / 64 / baud`
  - `Uart4_Init` / `Uart5_Init`: `i = FOSC / 8 / baud`
- **Host Setup**: Configure a USB-UART bridge with `stty -F /dev/ttyUSB0 115200 -icanon -echo`. Use simple payloads like `printf '\x01HELLO\n' > /dev/ttyUSB0` when testing patched handlers.

## DGUS Serial Protocol Snapshot
- **Frame Structure** (per vendor documentation and sample sources):
  - Header `5A A5`
  - Command length byte (`LEN`) covering payload; confirm semantics experimentally.
  - Operation byte: `0x82` for write, `0x83` for read.
  - 16-bit VP address field followed by data payload.
  - Optional **CRC-16** enabled per UART via `CRC_CHECK_UARTx` definitions.
- **Example Frames**:
  - Write: `5A A5 07 82 10 00 00 01 00 02`
  - Read: `5A A5 06 83 <ADDR> <LEN> ...`
  - Short "OK": `5A A5 03 82 4F 4B`
- **Reference Symbols**: Look for `deal_uart_data`, `DATA_UPLOAD_UARTx`, `RESPONSE_UARTx`, and ISR stubs in kernel or sample kits (`New_C_8283.*`).

## Firmware Hook Strategy
- **Hook Target**: Identify the application message dispatcher (jump table or switch). Repurpose a benign UI handler (e.g., About/Info screen) as the trigger point.
- **Patch Plan**:
  1. Inject a prologue that polls UART2/4 non-blockingly.
  2. On receiving a command, parse a one-byte opcode plus ASCII payload.
  3. Reuse existing text/box drawing routines (`FUN_002bad5c`, `FUN_002be3ac`, `FUN_002bb07c`, etc.) to render feedback.
  4. Fall through to the original handler when no data is available.
- **Artifacts to Catalogue**:
  - Virtual addresses and file offsets for the chosen handler and its prologue length.
  - Entry points of reused drawing functions.
  - Base address of any existing UART read helpers before writing new pollers.

## Integration with Firmware Roadmap
- **Bootloader Mapping**: Continue lifting relocation tables in `ZK-INKJET-NANO-BOOT.bin` to locate the APP entry point. Understanding SRAM buffer usage will highlight safe patch areas.
- **Application Offsets**: Track strings and handler pointers around `VA 0x003D3E00` in `ZK-INKJET-NANO-APP.bin` to find update-related flows and potential UART initialisation.
- **Resource Containers**: While focusing on UART, maintain awareness of `ZK-INKJET-RES-HW.zkml` parsing tasks—resource replacement may serve as an alternate injection vector.
- **Documentation Hygiene**: Mirror any experimental UART findings into `docs/analysis_traceability.md` and prepare to supersede `docs/archive/documentation-20251009.md` once the end-to-end path is validated.

## Immediate Next Actions
- Instrument hardware to confirm which UART is active and whether CRC is required.
- Log all verified frame exchanges and register interactions.
- Prototype a handler hook using the identified dispatcher entry, ensuring the original UI flow remains intact.
- Tie results back into the broader firmware modification roadmap (update control, resource injection, loader interception).

## Vendor Resource Checklist
Maintain a provenance log of any downloaded vendor packages. Record source URLs, version strings, filenames, and SHA-256 hashes when consulting:
- T5L family datasheet and DGUS-II user manuals.
- DGUS Tool releases and associated utilities (font generator, drivers).
- Serial protocol references or dev board documentation (e.g., EKT043B kits).
- Kernel upgrade kits that expose `STARTUP_M5.*`, `T5L51.bin`, or UART-focused source files.

Re-evaluate these references whenever new UART behaviour is observed so the consolidated plan stays aligned with official documentation.
