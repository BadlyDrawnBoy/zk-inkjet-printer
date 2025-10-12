from scripts.scan_strings import DEFAULT_PATTERN, extract_strings, filter_matches, hexdump


def test_extract_strings_detects_ascii_sequences():
    payload = b"\x00/dev/ttyS0\x00abcd\x00UART_PORT\x00"
    results = extract_strings(payload, min_length=4)
    texts = [match.text for match in results]
    assert "/dev/ttyS0" in texts
    assert "UART_PORT" in texts
    assert "abcd" in texts  # meets min length


def test_filter_matches_applies_regex():
    payload = b"/dev/ttyACM0\x00IGNORED\x00baud=115200\x00"
    matches = extract_strings(payload, min_length=4)
    filtered = filter_matches(matches, DEFAULT_PATTERN)
    assert any("ttyACM0" in item.text for item in filtered)
    assert any("115200" in item.text for item in filtered)
    assert all("IGNORED" not in item.text for item in filtered)


def test_hexdump_formats_rows():
    sample = bytes(range(1, 33))
    dump = hexdump(sample, base_offset=0)
    lines = dump.splitlines()
    assert lines[0].startswith("00000000")
    assert lines[1].startswith("00000010")
    assert len(lines) == 2
