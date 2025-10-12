# Addressing Conventions

- Virtual addresses (VA) are listed by default, for example `0X20C798`.
- Optional file offsets may be provided in parentheses, e.g. `VA 0X20C798 (file+0XC798)`.
- Conversion rule: `VA = BASE (0X200000) + file_offset`.
- Thumb targets keep the least-significant bit set; compare or mask with `(addr & ~1)` when needed.
- Memory-mapped I/O ranges (such as `0XB100D000`) are neither VA nor file offsets—label them explicitly as MMIO.
