from __future__ import annotations

import struct

from scripts.app_message_table import ENTRY_STRUCT, parse_message_table


def build_payload(entries: list[tuple[int, int, int]], strings: list[bytes], base_addr: int) -> bytes:
    table = bytearray()
    blob = bytearray()
    offsets = []
    current_offset = len(entries) * ENTRY_STRUCT.size + ENTRY_STRUCT.size  # space for sentinel

    for text in strings:
        offsets.append(current_offset)
        blob.extend(text + b"\x00")
        current_offset += len(text) + 1

    table_offset = 0
    table.extend(b"\x00" * (len(entries) * ENTRY_STRUCT.size + ENTRY_STRUCT.size))
    for idx, (handler_offset, string_index, flag) in enumerate(entries):
        handler_addr = base_addr + handler_offset
        string_addr = offsets[string_index]
        struct.pack_into("<III", table, idx * ENTRY_STRUCT.size, handler_addr, string_addr, flag)

    payload = bytearray(table)
    payload.extend(blob)

    max_handler_offset = max((handler_offset for handler_offset, _, _ in entries), default=0)
    required_length = max_handler_offset + 0x100  # give ample space beyond handler offsets
    if len(payload) <= required_length:
        payload.extend(b"\x00" * (required_length - len(payload) + 1))

    return bytes(payload)


def test_parse_message_table_round_trip() -> None:
    base_addr = 0x200000
    entries = [
        (0x100, 0, 1),
        (0x200, 1, 2),
    ]
    payload = build_payload(entries, [b"Ready", b"Upgrade complete"], base_addr)
    result = parse_message_table(payload, 0, base_addr)

    assert len(result) == 2
    assert result[0].handler_offset == 0x100
    assert result[0].text == "Ready"
    assert result[1].flag == 2
    assert result[1].handler_addr == base_addr + 0x200


def test_parse_message_table_stops_at_sentinel() -> None:
    base_addr = 0x200000
    entries = [
        (0x300, 0, 1),
    ]
    payload = build_payload(entries, [b"Only"], base_addr)
    # Inject sentinel (already zeroed) ensures only one entry parsed.
    result = parse_message_table(payload, 0, base_addr)
    assert len(result) == 1


def test_parse_message_table_invalid_string_pointer_raises() -> None:
    base_addr = 0x200000
    table = struct.pack("<III", base_addr, 0xFFFFFFF0, 1)
    payload = table + struct.pack("<III", 0, 0, 0)
    try:
        parse_message_table(payload, 0, base_addr)
        assert False, "expected ValueError"
    except ValueError:
        pass
