# UART hook plan (draft)

Goal
- Reuse a benign UI button handler to accept simple UART2 commands and branch into the existing draw/print paths.
- No new driver; minimal patch (prolog hook + fallback to original code).

Assumptions (explicitly unconfirmed)
- SoC: marking “M5 (DWIN)”; behaviour likely T5L-class.
- UART pads: 4-pin testpad on cartridge adapter; idle ~3.3 V (pull-ups); likely UART2.

Where to hook
- Find the central message/dispatch (jump table or big switch).
- Pick a harmless handler (e.g. “About/Info” screen) that’s easy to trigger.
- Patch handler prolog:
  1) poll UART2 (non-blocking)
  2) if data: parse 1-byte cmd + ASCII payload
  3) jump into existing text/box draw functions
  4) else: run original handler

Test setup
- USB-UART or logic analyzer, 115200 8N1 (try 9600/38400/57600/230400 if silent).
- `stty -F /dev/ttyUSB0 115200 -icanon -echo`
- `printf '\x01HELLO\n' > /dev/ttyUSB0` → expect centered text via existing render path.

Artifacts to identify (and document)
- VA of chosen handler + prolog length (room for BL/NOP patch).
- Addresses used by text/box draw funcs (e.g., FUN_002bad5c / FUN_002be3ac / FUN_002bb07c).
- UART base (regs/clock) if needed for quick poll; prefer calling an existing uart_read() if present.

Non-destructive next steps
- Confirm TX/RX on testpad during first 0–5 s after power-on.
- During firmware update, sniff for transient serial activity.
- If no chatter: implement poll with timeout in the hook; keep original path as fallback.

Notes
- This is a personal research repo. SoC equivalence M5↔T5L is unconfirmed; validate on hardware.

# UART control notes (from DWIN “8283” sample)

**SoC note:** My unit’s SoC is marked **M5 (DWIN)**; no public M5 datasheet found. I tentatively reference **T5L** docs where behavior matches. M5↔T5L equivalence is **unconfirmed**.

## UARTs & baud
Vendor sample shows multiple UARTs (2/4/5) with init formulas:
- `Uart2_Init`: `i = 1024 - FOSC / 64 / baud`  
- `Uart4_Init` / `Uart5_Init`: `i = FOSC / 8 / baud`  
- `FOSC = 206,438,400` (seen in `Dwin_T5L1H.h`)

Comments indicate **UART4 = 115200** in sample code. Start probing at **115200 8N1, 3.3 V TTL**. (Verify on hardware.)

## Frame bytes observed (“8283 protocol”)
Sample code/comments (`1.txt`, `Uart.c`) show DGUS-like frames:

- **Write example**  
  `5A A5 07 82 10 00 00 01 00 02`
- **Read template**  
  `5A A5 06 83 ADDR LEN XX XX`
- **“OK” short**  
  `5A A5 03 82 4F 4B`

Where:
- `5A A5` = header
- `LEN` = payload length (vendor format; confirm exact semantics)
- `0x82` = write, `0x83` = read
- `ADDR` = 16-bit address (DGUS VP-style)
- Optional **CRC-16** is referenced (`crc16.c`) with per-UART flags (`CRC_CHECK_UARTx`). Confirm whether CRC is enabled on the target firmware.

Useful symbols in the sample:
- `deal_uart_data(...)`, `DATA_UPLOAD_UARTx`, `RESPONSE_UARTx`, `CRC_CHECK_UARTx`
- ISR stubs for `UART2/4/5` and public inits in `New_C_8283.M51`

## Practical next steps
1. Probe **UART4 @ 115200 8N1** first; if silent, try UART2/5.  
2. Send a minimal **read** frame (`0x83`) to a harmless VP address; watch for reply.  
3. If no reply, try enabling/adding **CRC-16** per `crc16.c` (same polynomial/table as in vendor sample).  
4. Record any working address/command pairs under `docs/analysis_traceability.md`.

## To confirm
- Exact **length field** meaning for 0x82/0x83
- Whether **CRC** is required on this firmware build
- Which UART(s) are actually **enabled** on the printer app

