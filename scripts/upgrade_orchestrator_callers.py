#!/usr/bin/env python3
"""Enumerate firmware call-sites that target the upgrade orchestrator.

The Ghidra project for this binary is currently unstable, so this helper
scans the raw `ZK-INKJET-NANO-APP.bin` image with Capstone and recovers
every `bl`/`blx` that lands on the orchestrator entry point
(`0x0020EAEC`).  For each call-site it records:

* The address, mode (ARM/Thumb), and mnemonic of the branch.
* A disassembly window centred on the call for quick context.
* Literal arguments loaded into `r0`–`r3` immediately before the call,
  extracted from nearby `mov{,w,t}` / `ldr pc-relative` / `adr`
  instructions.

Outputs are written in both JSON (structured data for automation) and a
human-readable text dump so analysts can triage callers without opening
the GUI database.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

try:
    from capstone import (  # type: ignore
        CS_OP_IMM,
        CS_OP_MEM,
        CS_OP_REG,
        Cs,
        CS_ARCH_ARM,
        CS_MODE_ARM,
        CS_MODE_THUMB,
    )
    from capstone.arm import ARM_INS_BL, ARM_INS_BLX, ARM_OP_IMM  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "capstone module is required; install with `python3 -m pip install capstone`."
    ) from exc


TARGET_ADDR = 0x0020_EAEC
APP_BASE_ADDR = 0x0020_0000
ARG_REGS = ("r0", "r1", "r2", "r3")


@dataclass(frozen=True)
class CallSite:
    address: int
    mode: str
    mnemonic: str
    op_str: str

    def to_dict(self) -> dict[str, str]:
        payload = asdict(self)
        payload["address"] = f"0x{self.address:08X}"
        return payload


@dataclass(frozen=True)
class InstructionRecord:
    address: int
    bytes_: bytes
    mnemonic: str
    op_str: str

    def to_dict(self) -> dict[str, str]:
        return {
            "address": f"0x{self.address:08X}",
            "bytes": self.bytes_.hex(),
            "mnemonic": self.mnemonic,
            "op_str": self.op_str,
        }


def _find_thumb_calls(blob: bytes, base_addr: int, target: int) -> Iterable[CallSite]:
    dis = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    dis.detail = True
    length = len(blob)
    for offset in range(0, length - 4, 2):
        insns = list(dis.disasm(blob[offset : offset + 4], base_addr + offset, 1))
        if not insns:
            continue
        insn = insns[0]
        if insn.address != base_addr + offset:
            continue
        if insn.id not in (ARM_INS_BL, ARM_INS_BLX):
            continue
        if not insn.operands:
            continue
        op = insn.operands[0]
        if op.type != ARM_OP_IMM:
            continue
        if (op.imm & ~1) != target:
            continue
        yield CallSite(
            address=insn.address,
            mode="thumb",
            mnemonic=insn.mnemonic,
            op_str=insn.op_str,
        )


def _find_arm_calls(blob: bytes, base_addr: int, target: int) -> Iterable[CallSite]:
    dis = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    dis.detail = True
    length = len(blob)
    for offset in range(0, length - 4, 4):
        insns = list(dis.disasm(blob[offset : offset + 4], base_addr + offset, 1))
        if not insns:
            continue
        insn = insns[0]
        if insn.address != base_addr + offset:
            continue
        if insn.id not in (ARM_INS_BL, ARM_INS_BLX):
            continue
        if not insn.operands:
            continue
        op = insn.operands[0]
        if op.type != ARM_OP_IMM:
            continue
        if (op.imm & ~1) != target:
            continue
        yield CallSite(
            address=insn.address,
            mode="arm",
            mnemonic=insn.mnemonic,
            op_str=insn.op_str,
        )


def _read_u32(blob: bytes, base_addr: int, address: int) -> int | None:
    offset = address - base_addr
    if offset < 0 or offset + 4 > len(blob):
        return None
    return int.from_bytes(blob[offset : offset + 4], "little")


def _update_reg_literals(
    insn,
    regs: Dict[str, int],
    blob: bytes,
    base_addr: int,
    mode: str,
) -> None:
    if not insn.operands:
        return
    dest_op = insn.operands[0]
    if dest_op.type != CS_OP_REG:
        return
    dest = insn.reg_name(dest_op.reg)
    mnemonic = insn.mnemonic

    if len(insn.operands) >= 2 and insn.operands[1].type == CS_OP_IMM:
        imm = insn.operands[1].imm & 0xFFFFFFFF
        if mnemonic in ("mov", "movs"):
            regs[dest] = imm
        elif mnemonic == "movw":
            prev = regs.get(dest, 0)
            regs[dest] = (prev & 0xFFFF0000) | (imm & 0xFFFF)
        elif mnemonic == "movt":
            prev = regs.get(dest, 0)
            regs[dest] = ((imm & 0xFFFF) << 16) | (prev & 0xFFFF)
        elif mnemonic == "adr":
            pc = insn.address + (4 if mode == "thumb" else 8)
            regs[dest] = (pc + imm) & 0xFFFFFFFF
        return

    if (
        mnemonic == "ldr"
        and len(insn.operands) >= 2
        and insn.operands[1].type == CS_OP_MEM
        and insn.operands[1].mem.base != 0
    ):
        base_reg = insn.reg_name(insn.operands[1].mem.base)
        if base_reg != "pc":
            return
        disp = insn.operands[1].mem.disp
        pc = insn.address + (4 if mode == "thumb" else 8)
        literal_addr = pc + disp
        value = _read_u32(blob, base_addr, literal_addr)
        if value is not None:
            regs[dest] = value & 0xFFFFFFFF


def _analyse_context(
    blob: bytes,
    base_addr: int,
    call: CallSite,
    byte_count: int,
) -> Tuple[List[InstructionRecord], Dict[str, int]]:
    if call.mode == "thumb":
        dis = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        align = 2
    else:
        dis = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        align = 4
    dis.detail = True

    half_window = byte_count // 2
    start_addr = max(base_addr, call.address - half_window)
    start_offset = start_addr - base_addr
    start_offset -= start_offset % align
    window = blob[start_offset : start_offset + byte_count]

    listing: List[InstructionRecord] = []
    reg_literals: Dict[str, int] = {}
    snapshot: Dict[str, int] = {}

    for insn in dis.disasm(window, base_addr + start_offset):
        listing.append(
            InstructionRecord(
                address=insn.address,
                bytes_=insn.bytes,
                mnemonic=insn.mnemonic,
                op_str=insn.op_str,
            )
        )
        if insn.address < call.address:
            _update_reg_literals(insn, reg_literals, blob, base_addr, call.mode)
        elif insn.address == call.address:
            snapshot = {
                reg: value
                for reg, value in reg_literals.items()
                if reg in ARG_REGS
            }
            # We do not break: continue collecting instructions after the call

    return listing, snapshot


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Locate BL/BLX sites that target the upgrade orchestrator."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/ZK-INKJET-NANO-APP.bin"),
        help="Path to the APP firmware blob.",
    )
    parser.add_argument(
        "--base-address",
        type=lambda value: int(value, 0),
        default=APP_BASE_ADDR,
        help="Load address assumed for the raw image (default: 0x00200000).",
    )
    parser.add_argument(
        "--target",
        type=lambda value: int(value, 0),
        default=TARGET_ADDR,
        help="Thumb entry point of the orchestrator (default: 0x0020EAEC).",
    )
    parser.add_argument(
        "--context-bytes",
        type=int,
        default=0x40,
        help="Number of bytes to disassemble around each call (default: 0x40).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("data/processed/upgrade_orchestrator_callers.json"),
        help="Destination for structured call-site metadata.",
    )
    parser.add_argument(
        "--output-text",
        type=Path,
        default=Path("data/processed/upgrade_orchestrator_callers.txt"),
        help="Destination for the human-readable context dump.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    blob = args.input.read_bytes()

    calls = (
        list(_find_thumb_calls(blob, args.base_address, args.target))
        + list(_find_arm_calls(blob, args.base_address, args.target))
    )
    calls.sort(key=lambda call: call.address)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)

    json_calls: List[dict[str, str]] = []
    text_lines: List[str] = []

    for call in calls:
        listing, arg_literals = _analyse_context(
            blob, args.base_address, call, args.context_bytes
        )

        call_entry = call.to_dict()
        if arg_literals:
            call_entry["arg_literals"] = {
                reg: f"0x{value:08X}" for reg, value in sorted(arg_literals.items())
            }
        json_calls.append(call_entry)

        text_lines.append(
            f"{call.address:#010x} [{call.mode}] {call.mnemonic} {call.op_str}"
        )
        if arg_literals:
            formatted = ", ".join(
                f"{reg}=0x{value:08X}" for reg, value in sorted(arg_literals.items())
            )
            text_lines.append(f"  # args {formatted}")
        for inst in listing:
            marker = ">>" if inst.address == call.address else "  "
            text_lines.append(
                f"{marker} 0x{inst.address:08X}  {inst.bytes_.hex():>8}  {inst.mnemonic:<8} {inst.op_str}"
            )
        text_lines.append("")

    payload = {
        "target": f"0x{args.target:08X}",
        "base_address": f"0x{args.base_address:08X}",
        "callsite_count": len(json_calls),
        "calls": json_calls,
    }
    args.output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.output_text.write_text("\n".join(text_lines).rstrip() + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

