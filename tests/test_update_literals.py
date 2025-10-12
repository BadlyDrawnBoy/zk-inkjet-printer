from pathlib import Path

from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
from capstone.arm import ARM_INS_BL
from capstone.arm_const import ARM_OP_IMM


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_BIN = REPO_ROOT / "data" / "raw" / "ZK-INKJET-NANO-APP.bin"


def test_upgrade_literal_offsets_present():
    """Smoke-check that documented upgrade filenames are still in place."""
    payload = APP_BIN.read_bytes()
    literals = {
        0x000688FC: "3:/ZK-INKJET-NANO-BOOT.bin",
        0x0006891C: "3:/ZK-INKJET-NANO-APP.bin",
        0x0006CAD8: "3:/ZK-INKJET-UI-QVGA.bin",
        0x0006CFE0: "3:/ZK-INKJET-TINY-BOOT.bin",
        0x0006CFFC: "3:/ZK-INKJET-PUNY-BOOT.bin",
        0x0006D034: "3:/ZK-INKJET-UI.bin",
        0x0006D048: "3:/ZK-INKJET-UI-QVGA.bin",
        0x0006D064: "3:/ZK-TIJSPS-800x480-UI.bin",
    }
    for offset, literal in literals.items():
        chunk = payload[offset : offset + len(literal)]
        assert chunk == literal.encode("ascii"), f"Literal {literal} missing at 0x{offset:06X}"


def test_memcmp_loops_call_helper():
    """Ensure the documented memcmp loops still branch to the helper at 0x0020E158."""
    payload = APP_BIN.read_bytes()
    base = 0x0020_0000
    helper = 0x0020_E158
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    md.detail = True

    regions = (0x0025A930, 0x0025A990, 0x0025A9F0)
    for start in regions:
        span = payload[start - base : start - base + 0x60]
        hits = [
            insn
            for insn in md.disasm(span, start)
            if insn.id == ARM_INS_BL
            and insn.operands
            and insn.operands[0].type == ARM_OP_IMM
            and (insn.operands[0].imm & ~1) == helper
        ]
        assert hits, f"No bl to 0x{helper:08X} in loop at 0x{start:08X}"
