#!/usr/bin/env python3
"""Parse the APP.bin message handler table and emit a JSON index."""

from __future__ import annotations

import argparse
import json
import logging
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

LOGGER = logging.getLogger("app_message_table")

DEFAULT_INPUT = Path("data/raw/ZK-INKJET-NANO-APP.bin")
DEFAULT_OUTPUT = Path("data/processed/app_message_table.json")
DEFAULT_OFFSET = 0x001D3E00
DEFAULT_BASE_ADDR = 0x0020_0000
ENTRY_STRUCT = struct.Struct("<III")


@dataclass(frozen=True)
class MessageEntry:
    """A single entry in the APP.bin message handler table."""

    index: int
    handler_addr: int
    handler_offset: int
    string_addr: int
    string_offset: int
    flag: int
    text: str


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(levelname)s %(message)s")


def decode_c_string(payload: bytes, offset: int) -> Tuple[str, int]:
    end = payload.find(b"\x00", offset)
    if end == -1:
        raise ValueError(f"Missing NUL terminator for string at 0x{offset:X}.")
    raw = payload[offset:end]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1", errors="replace")
    return text, end + 1  # next offset (including NUL)


def parse_message_table(
    payload: bytes,
    offset: int,
    base_addr: int,
    limit_entries: int | None = None,
) -> List[MessageEntry]:
    entries: List[MessageEntry] = []
    total = len(payload)
    cursor = offset

    while cursor + ENTRY_STRUCT.size <= total:
        handler_addr, string_addr, flag = ENTRY_STRUCT.unpack_from(payload, cursor)
        cursor += ENTRY_STRUCT.size

        if handler_addr == 0 and string_addr == 0 and flag == 0:
            break

        string_offset = string_addr
        handler_offset = handler_addr - base_addr
        if not (0 <= handler_offset < total):
            LOGGER.warning(
                "Entry %d handler offset 0x%X out of range (addr=0x%X).",
                len(entries),
                handler_offset,
                handler_addr,
            )
        if not (0 <= string_offset < total):
            raise ValueError(f"Entry {len(entries)} string pointer 0x{string_addr:X} outside payload.")

        text, _ = decode_c_string(payload, string_offset)

        entries.append(
            MessageEntry(
                index=len(entries),
                handler_addr=handler_addr,
                handler_offset=handler_offset,
                string_addr=string_addr,
                string_offset=string_offset,
                flag=flag,
                text=text,
            )
        )

        if limit_entries is not None and len(entries) >= limit_entries:
            break

    return entries


def build_summary(entries: Sequence[MessageEntry]) -> dict:
    by_flag: dict[int, int] = {}
    for entry in entries:
        by_flag[entry.flag] = by_flag.get(entry.flag, 0) + 1

    return {
        "total_entries": len(entries),
        "flags": [
            {"flag": flag, "count": count} for flag, count in sorted(by_flag.items())
        ],
        "sample_text": [entry.text for entry in entries[:5]],
    }


def write_index(path: Path, header: dict, entries: Sequence[MessageEntry]) -> None:
    payload = {
        "metadata": header,
        "entries": [asdict(entry) for entry in entries],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT, help="APP.bin path.")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path.")
    parser.add_argument("--offset", type=lambda value: int(value, 0), default=DEFAULT_OFFSET, help="Table offset in file.")
    parser.add_argument(
        "--base-addr",
        type=lambda value: int(value, 0),
        default=DEFAULT_BASE_ADDR,
        help="Load address base used to convert handler addresses to file offsets.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for the number of entries to parse.")
    parser.add_argument("--log-level", choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), default="INFO")
    args = parser.parse_args()

    configure_logging(args.log_level)
    LOGGER.info("Reading %s", args.input)
    payload = args.input.read_bytes()

    LOGGER.info("Parsing message table at 0x%X", args.offset)
    entries = parse_message_table(payload, args.offset, args.base_addr, limit_entries=args.limit)
    LOGGER.info("Recovered %d entries", len(entries))

    header = {
        "input": str(args.input),
        "offset": args.offset,
        "base_addr": args.base_addr,
        "summary": build_summary(entries),
    }

    LOGGER.info("Writing index to %s", args.output)
    write_index(args.output, header, entries)


if __name__ == "__main__":
    main()
