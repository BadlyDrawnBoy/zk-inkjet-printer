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
