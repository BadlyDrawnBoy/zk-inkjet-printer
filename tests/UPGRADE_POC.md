# Upgrade Dry-Run Checklist

This procedure exercises the “found / not-found” UI paths and the early validation routines without flashing new contents. Run all commands from the repository root.

## 1. Prepare media
- Format a spare USB stick with FAT32.
- Copy the reference binaries from `data/raw/` using the exact names (lowercase, root of `3:/`):
  - `ZK-INKJET-NANO-BOOT.bin`
  - `ZK-INKJET-NANO-APP.bin`
  - `ZK-INKJET-UI.bin`
  - `ZK-INKJET-UI-QVGA.bin`
  - `ZK-TIJSPS-800x480-UI.bin`
- Optional legacy triggers: add `ZK-INKJET-TINY-BOOT.bin` and `ZK-INKJET-PUNY-BOOT.bin`.

## 2. Benign test payloads
- Copy an **unaltered** UI image (e.g. `ZK-INKJET-UI-QVGA.bin`) and a **header-tampered** clone (change a few bytes outside the payload) with a different filename to confirm rejection.
- Keep SHA-256 hashes of both versions for later comparison.

## 3. Device-side dry run
1. Insert the stick, trigger the firmware scan, and note:
   - Success message (`0x000C28D0` handler) when expected names are present.
   - Failure message (`0x000C47F0`) after removing/renaming files.
2. With untouched binaries, allow the device to reach the validation phase but cancel before flashing (power-cycle or exit at the prompt).
3. Repeat with the tampered clone: observe if the validator emits an error string before any flash writes.

## 4. Observation points
- Photograph or log any UI text produced by the notifier so we can cross-reference `0x0027B61C`/`0x0027BB80` state.
- If available, capture serial/UART output for additional clues around the validator.

## 5. Post-run sanity
- Reboot the device without the stick to ensure no unintended updates were applied.
- Compare file hashes on the stick to confirm they were not modified by the device.
- Record the steps and observations in `docs/session_status.md` for future sessions.
