import numpy as np

from scripts.uiqvga_smart_decode import (
    DriftSpec,
    bgr565_to_rgb,
    compute_row_shifts,
    decode_words,
    iter_tile_positions,
)


def _build_raw_payload(
    base_canvas: np.ndarray,
    tile_size: int,
    grid: int,
    order: str,
    xor_value: int,
    odd_shift: int,
    drift: DriftSpec,
    col_offsets,
) -> np.ndarray:
    misaligned = base_canvas.copy()

    # Undo column alignment (inverse rolls).
    for idx, offset in enumerate(col_offsets):
        if offset:
            x0 = idx * tile_size
            x1 = x0 + tile_size
            misaligned[:, x0:x1] = np.roll(misaligned[:, x0:x1], -offset, axis=1)

    # Undo per-row shifts.
    shifts = compute_row_shifts(base_canvas.shape[0], tile_size, odd_shift, drift)
    for row_idx, shift in enumerate(shifts):
        if shift:
            misaligned[row_idx] = np.roll(misaligned[row_idx], -shift)

    scrambled = np.bitwise_xor(misaligned, np.uint16(xor_value))

    tiles = []
    tile_area = tile_size * tile_size
    for ty, tx in iter_tile_positions(order, grid):
        tile = scrambled[
            ty * tile_size : (ty + 1) * tile_size, tx * tile_size : (tx + 1) * tile_size
        ]
        tiles.append(tile.reshape(tile_area))

    return np.concatenate(tiles)


def test_decode_words_round_trip_no_offsets():
    tile_size = 2
    grid = 3
    order = "col"
    xor_value = 0xAAAA
    odd_shift = 0
    drift = DriftSpec(step=0, period=0)
    col_offsets = (0, 0, 0)

    side = tile_size * grid
    base_canvas = np.arange(side * side, dtype=np.uint16).reshape(side, side)

    payload = _build_raw_payload(
        base_canvas, tile_size, grid, order, xor_value, odd_shift, drift, col_offsets
    )

    decoded = decode_words(
        payload, tile_size, grid, order, xor_value, odd_shift, drift, col_offsets
    )
    expected = bgr565_to_rgb(base_canvas)

    np.testing.assert_array_equal(decoded, expected)


def test_decode_words_with_offsets_and_drift():
    tile_size = 4
    grid = 3
    order = "row"
    xor_value = 0x0F0F
    odd_shift = 3
    drift = DriftSpec(step=1, period=2)
    col_offsets = (1, -2, 2)

    side = tile_size * grid
    base_canvas = (np.arange(side * side, dtype=np.uint16) * 13) & 0xFFFF
    base_canvas = base_canvas.reshape(side, side)

    payload = _build_raw_payload(
        base_canvas, tile_size, grid, order, xor_value, odd_shift, drift, col_offsets
    )

    decoded = decode_words(
        payload, tile_size, grid, order, xor_value, odd_shift, drift, col_offsets
    )
    expected = bgr565_to_rgb(base_canvas)

    np.testing.assert_array_equal(decoded, expected)
