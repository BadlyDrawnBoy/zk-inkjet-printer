from __future__ import annotations

import struct

from scripts.reshw_parse import HEADER_STRUCT, ENTRY_PREFIX_STRUCT, parse_container, parse_entries, parse_header


def build_entry(name: str, part_count: int, values: list[int]) -> bytes:
    encoded = name.encode("utf-8") + b"\x00"
    payload = struct.pack("<2I", part_count, len(values)) + struct.pack(f"<{len(values)}H", *values)
    return encoded + payload


def test_parse_header_and_entries_roundtrip() -> None:
    header_bytes = struct.pack("<6I", 1, 0, 320, 240, 2, 2)
    entry_one = build_entry("A", 3, [1, 2, 3, 4])
    entry_two = build_entry("B", 5, [10, 20, 30, 40, 50, 60])
    container = header_bytes + entry_one + entry_two

    header = parse_header(container)
    assert header.version == 1
    assert header.entry_count == 2
    entries, consumed = parse_entries(container, HEADER_STRUCT.size, header.entry_count)
    assert consumed == len(container)
    assert len(entries) == 2
    assert entries[0].char == "A"
    assert entries[0].point_count == 2  # len(values) // 2
    assert entries[1].part_count == 5

    parsed_header, parsed_entries = parse_container(container)
    assert parsed_header == header
    assert [entry.char for entry in parsed_entries] == ["A", "B"]


def test_parse_entries_truncated_payload_raises() -> None:
    header_bytes = struct.pack("<6I", 1, 0, 320, 240, 1, 1)
    # Declare value_count=4 but only supply 3 words to trigger truncation.
    broken_entry = "C".encode("utf-8") + b"\x00" + struct.pack("<2I", 2, 4) + struct.pack("<3H", 1, 2, 3)
    container = header_bytes + broken_entry
    try:
        parse_entries(container, HEADER_STRUCT.size, expected_count=1)
        assert False, "expected ValueError"
    except ValueError:
        pass
