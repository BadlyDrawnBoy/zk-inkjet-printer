#!/usr/bin/env python3
"""Decode the upgrade orchestrator routine and emit a simple call graph.

The script avoids Ghidra so we can recover call edges even when the
program database has zeroed memory blocks. It reads raw bytes from
`ZK-INKJET-NANO-APP.bin`, decodes the Thumb function rooted at
0x0020EAEC, and records every BL/BLX destination it encounters until the
function returns.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

try:
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB  # type: ignore
    from capstone.arm import ARM_INS_BL, ARM_INS_BLX, ARM_OP_IMM, ARM_OP_REG  # type: ignore
except ImportError as exc:  # pragma: no cover - prefer explicit hint
    raise SystemExit(
        "capstone module is required; install with `python3 -m pip install capstone`"
    ) from exc


APP_BASE_ADDR = 0x0020_0000
DEFAULT_ROOT = 0x0020_EAEC
DEFAULT_MAX_BYTES = 0x600


@dataclass(frozen=True)
class Instruction:
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


@dataclass(frozen=True)
class CallSite:
    address: int
    mnemonic: str
    target: str
    kind: str

    def to_dict(self) -> dict[str, str]:
        return {
            "site": f"0x{self.address:08X}",
            "mnemonic": self.mnemonic,
            "target": self.target,
            "kind": self.kind,
        }


def load_bytes(path: Path, file_offset: int, max_bytes: int) -> bytes:
    data = path.read_bytes()
    end_offset = min(len(data), file_offset + max_bytes)
    return data[file_offset:end_offset]


def disassemble_function(
    blob: bytes, start_addr: int, max_length: int
) -> Sequence[Instruction]:
    disassembler = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    disassembler.detail = True
    instructions: List[Instruction] = []
    consumed = 0
    for insn in disassembler.disasm(blob, start_addr):
        instructions.append(
            Instruction(
                address=insn.address,
                bytes_=insn.bytes,
                mnemonic=insn.mnemonic,
                op_str=insn.op_str,
            )
        )
        consumed += len(insn.bytes)
        if is_function_return(insn.mnemonic, insn.op_str):
            break
        if consumed >= max_length:
            break
    return instructions


def is_function_return(mnemonic: str, op_str: str) -> bool:
    if mnemonic == "bx" and op_str.strip().lower() == "lr":
        return True
    if mnemonic == "pop":
        cleaned = op_str.replace("{", "").replace("}", "")
        if "pc" in {p.strip().lower() for p in cleaned.split(",")}:
            return True
    return False


def extract_calls(instructions: Iterable[Instruction]) -> List[CallSite]:
    disassembler = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    disassembler.detail = True
    call_sites: List[CallSite] = []
    for inst in instructions:
        for decode in disassembler.disasm(inst.bytes_, inst.address):
            if decode.id not in {ARM_INS_BL, ARM_INS_BLX}:
                continue
            operand = decode.operands[0]
            if operand.type == ARM_OP_IMM:
                target = f"0x{operand.imm & 0xFFFFFFFF:08X}"
                kind = "direct"
            elif operand.type == ARM_OP_REG:
                reg_name = decode.reg_name(operand.value.reg)
                target = reg_name
                kind = "register"
            else:
                target = "unknown"
                kind = "other"
            call_sites.append(
                CallSite(
                    address=inst.address,
                    mnemonic=inst.mnemonic,
                    target=target,
                    kind=kind,
                )
            )
    return call_sites


def build_payload(
    instructions: Sequence[Instruction],
    call_sites: Sequence[CallSite],
    root_address: int,
    base_address: int,
) -> dict:
    return {
        "root_address": f"0x{root_address:08X}",
        "base_address": f"0x{base_address:08X}",
        "instruction_count": len(instructions),
        "instructions": [inst.to_dict() for inst in instructions],
        "calls": [call.to_dict() for call in call_sites],
    }


def write_outputs(
    payload: dict,
    json_path: Path,
    text_path: Path | None,
) -> None:
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if text_path is None:
        return
    lines = []
    for inst in payload["instructions"]:
        lines.append(
            f"{inst['address']}  {inst['bytes']:>8}  {inst['mnemonic']:<6} {inst['op_str']}"
        )
    lines.append("")
    if payload["calls"]:
        lines.append("# Call sites")
        for call in payload["calls"]:
            lines.append(
                f"{call['site']} -> {call['target']} ({call['mnemonic']}, {call['kind']})"
            )
    else:
        lines.append("# Call sites: none detected")
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recover call edges for the upgrade orchestrator."
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
        "--root-address",
        type=lambda value: int(value, 0),
        default=DEFAULT_ROOT,
        help="Thumb entry point of the upgrade orchestrator.",
    )
    parser.add_argument(
        "--max-bytes",
        type=lambda value: int(value, 0),
        default=DEFAULT_MAX_BYTES,
        help="Maximum byte window to decode from the binary.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("data/processed/upgrade_orchestrator_calls.json"),
        help="Destination for the JSON payload.",
    )
    parser.add_argument(
        "--output-text",
        type=Path,
        default=Path("data/processed/upgrade_orchestrator_disasm.txt"),
        help="Destination for a human-readable disassembly dump.",
    )
    parser.add_argument(
        "--no-text",
        action="store_true",
        help="Skip writing the plain-text disassembly companion file.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    file_offset = args.root_address - args.base_address
    if file_offset < 0:
        raise SystemExit("Root address must be greater than or equal to base address.")
    blob = load_bytes(args.input, file_offset, args.max_bytes)
    if not blob:
        raise SystemExit(
            f"No bytes read at offset 0x{file_offset:X}; check base/root addresses."
        )
    instructions = disassemble_function(blob, args.root_address, args.max_bytes)
    if not instructions:
        raise SystemExit("Failed to decode any instructions. Verify addresses and mode.")
    call_sites = extract_calls(instructions)
    payload = build_payload(
        instructions=instructions,
        call_sites=call_sites,
        root_address=args.root_address,
        base_address=args.base_address,
    )
    text_path = None if args.no_text else args.output_text
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    write_outputs(payload, args.output_json, text_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
