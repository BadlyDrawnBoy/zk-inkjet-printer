#!/usr/bin/env python3
"""Parse ZK-INKJET RES-HW container metadata and emit an index."""

from __future__ import annotations

import argparse
import json
import logging
import statistics
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

LOGGER = logging.getLogger("reshw_parse")

DEFAULT_INPUT = Path("data/raw/ZK-INKJET-RES-HW.zkml")
DEFAULT_OUTPUT = Path("data/processed/reshw_index.json")
HEADER_STRUCT = struct.Struct("<6I")
ENTRY_PREFIX_STRUCT = struct.Struct("<2I")


@dataclass(frozen=True)
class ResHwHeader:
    """Top-level container header."""

    version: int
    flags: int
    canvas_width: int
    canvas_height: int
    grouping_hint: int
    entry_count: int


@dataclass(frozen=True)
class ResHwEntry:
    """Metadata describing a single RES-HW glyph entry."""

    index: int
    char: str
    codepoint: int
    part_count: int
    value_count: int
    point_count: int
    name_offset: int
    values_offset: int
    values_length: int


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(levelname)s %(message)s")


def parse_header(payload: bytes) -> ResHwHeader:
    if len(payload) < HEADER_STRUCT.size:
        raise ValueError("Payload too small to contain header.")
    version, flags, width, height, grouping_hint, entry_count = HEADER_STRUCT.unpack_from(payload, 0)
    return ResHwHeader(version, flags, width, height, grouping_hint, entry_count)


def parse_entries(payload: bytes, start_offset: int, expected_count: int) -> Tuple[List[ResHwEntry], int]:
    entries: List[ResHwEntry] = []
    offset = start_offset
    total = len(payload)

    while offset < total:
        if expected_count and len(entries) >= expected_count:
            break
        if payload[offset] == 0:
            break

        name_end = payload.find(b"\x00", offset)
        if name_end == -1:
            raise ValueError(f"Missing NUL terminator for entry {len(entries)} (offset 0x{offset:X}).")
        name_bytes = payload[offset:name_end]
        try:
            name = name_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Entry {len(entries)} has non-UTF-8 name at 0x{offset:X}.") from exc
        if not name:
            raise ValueError(f"Entry {len(entries)} contains empty name at 0x{offset:X}.")

        entry_start = offset
        offset = name_end + 1
        if offset + ENTRY_PREFIX_STRUCT.size > total:
            raise ValueError(f"Entry {len(entries)} truncated before counts at 0x{offset:X}.")

        part_count, value_count = ENTRY_PREFIX_STRUCT.unpack_from(payload, offset)
        offset += ENTRY_PREFIX_STRUCT.size

        value_bytes = value_count * 2
        values_offset = offset
        end = offset + value_bytes
        if end > total:
            raise ValueError(f"Entry {len(entries)} payload overruns container: need {value_bytes} bytes.")

        entries.append(
            ResHwEntry(
                index=len(entries),
                char=name,
                codepoint=ord(name),
                part_count=part_count,
                value_count=value_count,
                point_count=value_count // 2,
                name_offset=entry_start,
                values_offset=values_offset,
                values_length=value_bytes,
            )
        )
        offset = end

    return entries, offset


def compute_stats(entries: Sequence[ResHwEntry]) -> dict:
    if not entries:
        return {"entries": 0}

    part_counts = [entry.part_count for entry in entries]
    points = [entry.point_count for entry in entries]
    values = [entry.value_count for entry in entries]

    largest_by_points = sorted(entries, key=lambda entry: entry.point_count, reverse=True)[:5]

    return {
        "entries": len(entries),
        "part_count": {
            "min": min(part_counts),
            "max": max(part_counts),
            "mean": statistics.mean(part_counts),
        },
        "point_count": {
            "min": min(points),
            "max": max(points),
            "mean": statistics.mean(points),
        },
        "value_count": {
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
        },
        "largest_point_entries": [
            {
                "index": entry.index,
                "char": entry.char,
                "codepoint": entry.codepoint,
                "point_count": entry.point_count,
                "part_count": entry.part_count,
            }
            for entry in largest_by_points
        ],
    }


def build_output(header: ResHwHeader, entries: Sequence[ResHwEntry]) -> dict:
    return {
        "header": asdict(header),
        "stats": compute_stats(entries),
        "entries": [
            {
                "index": entry.index,
                "char": entry.char,
                "codepoint": entry.codepoint,
                "part_count": entry.part_count,
                "value_count": entry.value_count,
                "point_count": entry.point_count,
                "name_offset": entry.name_offset,
                "values_offset": entry.values_offset,
                "values_length": entry.values_length,
            }
            for entry in entries
        ],
    }


def parse_container(payload: bytes) -> Tuple[ResHwHeader, List[ResHwEntry]]:
    header = parse_header(payload)
    entries, consumed = parse_entries(payload, HEADER_STRUCT.size, header.entry_count)
    if header.entry_count and len(entries) != header.entry_count:
        LOGGER.warning(
            "Header promised %d entries but parser recovered %d (consumed 0x%X bytes).",
            header.entry_count,
            len(entries),
            consumed,
        )
    return header, entries


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT, help="RES-HW container path.")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT, help="Destination JSON index path.")
    parser.add_argument("--log-level", choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), default="INFO")
    args = parser.parse_args()

    configure_logging(args.log_level)

    LOGGER.info("Reading %s", args.input)
    payload = args.input.read_bytes()

    LOGGER.info("Parsing header + entries")
    header, entries = parse_container(payload)
    LOGGER.info("Recovered %d entries", len(entries))

    LOGGER.info("Writing index to %s", args.output)
    write_json(args.output, build_output(header, entries))


if __name__ == "__main__":
    main()
