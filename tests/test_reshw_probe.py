import math

from scripts.reshw_probe import ascii_ratio, shannon_entropy, zero_ratio


def test_shannon_entropy_bounds():
    assert shannon_entropy(b"") == 0.0
    assert math.isclose(shannon_entropy(bytes([0] * 32)), 0.0, abs_tol=1e-6)
    assert shannon_entropy(bytes(range(256))) > 7.0


def test_ascii_ratio_counts_printables():
    data = b"ABCD\x00\x01"
    ratio = ascii_ratio(data)
    assert math.isclose(ratio, 4 / 6, rel_tol=1e-6)


def test_zero_ratio_detects_padding():
    data = b"\x00\x00\x01\x02"
    assert math.isclose(zero_ratio(data), 0.5, rel_tol=1e-6)
