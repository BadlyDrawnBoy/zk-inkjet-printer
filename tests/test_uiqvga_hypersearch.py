import numpy as np

from scripts.uiqvga_hypersearch import (
    ParameterSet,
    combine_score,
    compute_metrics,
    iter_parameter_sets,
    render_candidate,
    sobel_magnitude,
)


def test_sobel_magnitude_zero_for_uniform_image():
    gray = np.full((4, 4), 42.0, dtype=np.float32)
    magnitude = sobel_magnitude(gray)
    assert np.allclose(magnitude, 0.0)


def test_iter_parameter_sets_skips_invalid_drift():
    params = list(iter_parameter_sets([0], [1], [0], [0], 3))
    # Drift step 1 with period 0 should be skipped.
    assert params == []


def test_render_and_metrics_no_penalty_on_flat_canvas():
    tile_size = 2
    grid = 3
    base_canvas = np.zeros((tile_size * grid, tile_size * grid), dtype=np.uint16)
    params = ParameterSet(odd_shift=0, drift_step=0, drift_period=0, col_offsets=(0, 0, 0))

    rgb = render_candidate(base_canvas, tile_size, 0, params)
    metrics = compute_metrics(rgb, tile_size, grid)
    score = combine_score(metrics)

    assert np.allclose(rgb, 0)
    assert metrics["seam_rgb"] == 0.0
    assert metrics["odd_even"] == 0.0
    assert score == 0.0
