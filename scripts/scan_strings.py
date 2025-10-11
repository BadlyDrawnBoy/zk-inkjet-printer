#!/usr/bin/env python3
"""Extract targeted strings from the ZK-INKJET APP binary with context hexdumps."""

from __future__ import annotations

import argparse
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

LOGGER = logging.getLogger("scan_strings")

DEFAULT_INPUT = Path("data/raw/ZK-INKJET-NANO-APP.bin")
DEFAULT_OUTPUT = Path("data/processed/app_strings_report.md")
DEFAULT_MIN_LENGTH = 5
DEFAULT_PATTERN = r"/dev/tty.*|baud|115200|UART|update|BIN|ZK-INKJET|\.zkml|\.ttf|\.bmp|\.png"
CONTEXT_RADIUS = 64


@dataclass(frozen=True)
class StringMatch:
    offset: int
    text: str
    raw: bytes


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Binary file to scan (default: %(default)s).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Markdown report path (default: %(default)s).",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=DEFAULT_MIN_LENGTH,
        help="Minimum string length to consider (default: %(default)s).",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help="Regex used to filter strings of interest (default: %(default)s).",
    )
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        default="INFO",
        help="Logging verbosity.",
    )
    return parser.parse_args()


def extract_strings(payload: bytes, min_length: int) -> List[StringMatch]:
    matches: List[StringMatch] = []
    start = None
    buffer = bytearray()

    for idx, byte in enumerate(payload):
        if is_printable(byte):
            if start is None:
                start = idx
            buffer.append(byte)
            continue

        if start is not None and len(buffer) >= min_length:
            text = decode_string(bytes(buffer))
            matches.append(StringMatch(offset=start, text=text, raw=bytes(buffer)))
        start = None
        buffer.clear()

    if start is not None and len(buffer) >= min_length:
        text = decode_string(bytes(buffer))
        matches.append(StringMatch(offset=start, text=text, raw=bytes(buffer)))

    return matches


def is_printable(byte: int) -> bool:
    return 32 <= byte <= 126 or byte >= 0x80


def decode_string(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def filter_matches(matches: Iterable[StringMatch], pattern: str) -> List[StringMatch]:
    regex = re.compile(pattern, re.IGNORECASE)
    filtered = [match for match in matches if regex.search(match.text)]
    filtered.sort(key=lambda item: item.offset)
    return filtered


def hexdump(data: bytes, base_offset: int, width: int = 16) -> str:
    lines: List[str] = []
    for idx in range(0, len(data), width):
        chunk = data[idx : idx + width]
        hex_part = " ".join(f"{byte:02X}" for byte in chunk)
        ascii_part = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in chunk)
        lines.append(f"{base_offset + idx:08X}: {hex_part:<{width*3-1}}  {ascii_part}")
    return "\n".join(lines)


def build_report(
    matches: Sequence[StringMatch],
    payload: bytes,
    source: Path,
    pattern: str,
    min_length: int,
) -> str:
    lines: List[str] = [
        "# APP Strings Report",
        "",
        f"- Source file: `{source}`",
        f"- Pattern: `{pattern}`",
        f"- Minimum length: {min_length}",
        f"- Matches found: {len(matches)}",
        "",
    ]

    for entry in matches:
        start = max(0, entry.offset - CONTEXT_RADIUS)
        end = min(len(payload), entry.offset + len(entry.raw) + CONTEXT_RADIUS)
        context = payload[start:end]
        lines.extend(
            [
                f"## Offset 0x{entry.offset:08X}",
                "",
                f"- Text: `{entry.text}`",
                f"- Length: {len(entry.text)} characters",
                f"- File position: {entry.offset} (decimal)",
                "",
                "```text",
                hexdump(context, start),
                "```",
                "",
            ]
        )

    if not matches:
        lines.append("_No matches for the selected pattern._")

    return "\n".join(lines)


def write_report(report: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level)

    LOGGER.info("Reading binary %s", args.input)
    payload = args.input.read_bytes()
    LOGGER.info("Scanning %s bytes", len(payload))

    all_matches = extract_strings(payload, args.min_length)
    LOGGER.info("Found %s candidate strings", len(all_matches))
    filtered = filter_matches(all_matches, args.pattern)
    LOGGER.info("Filtered down to %s matches", len(filtered))

    report = build_report(filtered, payload, args.input, args.pattern, args.min_length)
    write_report(report, args.output)
    LOGGER.info("Wrote %s", args.output)


if __name__ == "__main__":
    main()
