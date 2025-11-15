# Nuvoton N32903K5DN Microcontroller - Quick Reference

**Chip:** Nuvoton N32903K5DN  
**Package:** LQFP-128 (N32903U5DN pinout)  
**Marking:** "DWIN M5" (custom branding)  
**Verification:** USB strings, ARM926EJ-S architecture, GPIO pinout  
**Confidence:** 98%

---

## CPU & Memory

**CPU:**
- 32-bit ARM926EJ-S RISC
- 8 KB I-Cache + 8 KB D-Cache
- Up to 200 MHz @ 1.8V

**On-Chip Memory:**
- 8 KB internal SRAM
- 16 KB Internal Boot ROM (IBR)

**Variant:**
- K5DN = No external SDRAM support
- U5DN = With external SDRAM support (up to 512 MB)

---

## System Memory Map

| Region | Address | Description |
|--------|---------|-------------|
| SDRAM | 0x0000_0000–0x7FFF_FFFF | Main memory (up to 512 MB) |
| GCR_BA | 0xB000_0000 | System & Global Control Registers |
| CLK_BA | 0xB000_0200 | Clock Controller |
| SDIC_BA | 0xB000_3000 | SDRAM Interface Controller |
| EDMA_BA | 0xB000_8000 | Enhanced DMA (5 channels) |
| AHB2 | 0xB100_0000–0xB100_DFFF | SPU, I2S, LCD, USB, JPEG, etc. |
| APB | 0xB800_0000–0xB800_EFFF | Interrupt, GPIO, Timer, UART, SPI, ADC |
| SRAM_BA | 0xFF00_0000–0xFF00_1FFF | On-Chip SRAM (8 KB) |
| IBR_BA | 0xFFFF_0000–0xFFFF_FFFF | Internal Boot ROM (16 KB) |

---

## Key Peripherals (APB Region)

| Peripheral | Base Address | Description |
|------------|--------------|-------------|
| AIC_BA | 0xB800_0000 | Interrupt Controller |
| GP_BA | 0xB800_1000 | GPIO Ports A-D |
| TMR_BA | 0xB800_2000 | Timer & Watchdog |
| RTC_BA | 0xB800_3000 | Real-Time Clock |
| I2C_BA | 0xB800_4000 | I²C Controller |
| KPI_BA | 0xB800_5000 | Keypad Interface |
| PWM_BA | 0xB800_7000 | PWM Controller |
| UA_BA | 0xB800_8000 | UART Controller (UART0/1) |
| SPIMS0_BA | 0xB800_C000 | SPI Master 0 |
| SPIMS1_BA | 0xB800_C400 | SPI Master 1 |
| ADC_BA | 0xB800_E000 | 10-bit SAR ADC |

---

## Global Control Register (GCR_BA + offsets)

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00 | PDID | Product ID |
| 0x04 | ARBCON | Arbitration Control |
| 0x80 | GPAFUN | Port A Multi-Function Pin Control |
| 0x84 | GPBFUN | Port B Multi-Function Pin Control |
| 0x88 | GPCFUN | Port C Multi-Function Pin Control |
| 0x8C | GPDFUN | Port D Multi-Function Pin Control |
| 0x90 | GPEFUN | Port E Multi-Function Pin Control |

---

## GPIO Ports (GP_BA + offsets)

**Port Offsets:**
- Port A: +0x00
- Port B: +0x40
- Port C: +0x80
- Port D: +0xC0

**Register Offsets (per port):**
- +0x10: OMD (Output Mode)
- +0x14: PUEN (Pull-Up Enable)
- +0x18: DOUT (Data Output)
- +0x1C: PIN (Pin Input)

**Example:** GPIOB_DOUT = 0xB8001058 (GP_BA + 0x40 + 0x18)

---

## UART Registers (UA_BA + offsets)

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00 | RBR/THR | Receive/Transmit Buffer |
| 0x04 | IER | Interrupt Enable |
| 0x08 | FCR | FIFO Control |
| 0x0C | LCR | Line Control (data format) |
| 0x10 | MCR | Modem Control |
| 0x14 | MSR | Modem Status |
| 0x18 | FSR | FIFO Status |
| 0x1C | ISR | Interrupt Status |
| 0x20 | TOR | Time-Out Register |
| 0x24 | BAUD | Baud Rate Divisor |

---

## Boot Configuration

**Boot Sources:**
- SD Card
- NAND Flash
- SPI Flash
- USB (recovery mode)

**Power-On Configuration:**
- Loaded via pull-ups/pull-downs on LVDATA/ND pins
- Stored in CHIPCFG register

**Boot Mode Selection (ND[3:0]):**
- 0x1011: Boot from IBR normal mode @ 12 MHz
- 0x1111: Boot from IBR normal mode @ 27 MHz

**USB Recovery:**
- If no boot medium found, IBR switches to USB recovery mode

---

## Interrupt Controller (AIC)

**Features:**
- 8 priority levels
- FIQ/IRQ support
- Level or edge trigger

**Key IRQ Sources:**
- Channel 1: WDT
- Channels 2-5: GPIO interrupts
- USB Device, USB Host
- UART, SPI, I2C
- Timer, ADC
- DMA, SD Controller

---

## Clock Controller (CLK_BA)

**Features:**
- PLL control
- Clock source selection
- Clock gating per peripheral
- Idle and power-down modes

---

## Pin Multiplexing

**Multi-Function Pins:**
- Configured via GPAFUN, GPBFUN, GPCFUN, GPDFUN registers
- Each pin can have multiple functions (GPIO, UART, SPI, I2C, etc.)
- 2 bits per pin in function registers

**Example GPB[2] Functions:**
- 00: GPIO
- 01: I2S_MCLK
- 10: SDCLK1
- 11: SHSYNC

---

## References

- **Detailed Analysis:** `docs/findings/chip_identification.md`
- **MMIO Map:** `docs/findings/mmio_map.md`
- **GPIO Analysis:** `docs/findings/gpio_configuration.md`
- **Verification Status:** `docs/VERIFICATION_STATUS.md`

---

**Note:** This is a quick reference extracted from the N32903 series documentation.
For complete details, refer to the official Nuvoton N32903 datasheet.

**Original German version:** `docs/archive/old-structure/N32903U5DN_K5DN_CheatCheet.txt`
