#!/usr/bin/env python3
"""Heuristic probe for ZK-INKJET RES-HW container layout."""

from __future__ import annotations

import argparse
import logging
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

LOGGER = logging.getLogger("reshw_probe")

DEFAULT_INPUT = Path("data/raw/ZK-INKJET-RES-HW.zkml")
DEFAULT_REPORT = Path("data/processed/reshw_probe_report.md")
DEFAULT_SAMPLE_DIR = Path("data/processed/samples")


@dataclass
class WindowStats:
    offset: int
    entropy: float
    ascii_ratio: float
    zero_ratio: float
    word_counts: Counter

    @property
    def word_summary(self) -> str:
        if not self.word_counts:
            return "-"
        most_common = self.word_counts.most_common(2)
        return ", ".join(f"0x{word:08X}×{count}" for word, count in most_common)


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(levelname)s %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT, help="Container blob to probe.")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_REPORT, help="Markdown report path.")
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLE_DIR, help="Directory for context dumps.")
    parser.add_argument("--window", type=int, default=4096, help="Sliding window size (bytes).")
    parser.add_argument("--step", type=int, default=512, help="Sliding window stride (bytes).")
    parser.add_argument("--top", type=int, default=6, help="Number of candidate offsets to highlight.")
    parser.add_argument("--log-level", choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), default="INFO")
    return parser.parse_args()


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def ascii_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    printable = sum(32 <= byte <= 126 for byte in data)
    return printable / len(data)


def zero_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    zeros = data.count(0)
    return zeros / len(data)


def word_histogram(data: bytes) -> Counter:
    words = Counter()
    for i in range(0, len(data) - 3, 4):
        word = int.from_bytes(data[i : i + 4], "little")
        words[word] += 1
    return words


def compute_windows(payload: bytes, window: int, step: int) -> List[WindowStats]:
    stats: List[WindowStats] = []
    for offset in range(0, len(payload), step):
        chunk = payload[offset : offset + window]
        if len(chunk) < window:
            break
        stats.append(
            WindowStats(
                offset=offset,
                entropy=shannon_entropy(chunk),
                ascii_ratio=ascii_ratio(chunk),
                zero_ratio=zero_ratio(chunk),
                word_counts=word_histogram(chunk[: 64]),
            )
        )
    return stats


def score_window(stat: WindowStats) -> float:
    ascii_boost = stat.ascii_ratio * 2.0
    zeros_penalty = stat.zero_ratio * 3.0
    alignment_bonus = 0.5 if stat.offset % 0x200 == 0 else 0.0
    alignment_bonus += 0.5 if stat.offset % 0x1000 == 0 else 0.0
    score = ascii_boost - zeros_penalty + alignment_bonus - abs(stat.entropy - 6.5) / 2.5
    return score


def select_candidates(stats: Sequence[WindowStats], top: int) -> List[WindowStats]:
    ranked = sorted(stats, key=score_window, reverse=True)
    return ranked[:top]


def write_samples(payload: bytes, candidates: Sequence[WindowStats], samples_dir: Path, size: int = 2048) -> List[Path]:
    samples_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for idx, stat in enumerate(candidates, start=1):
        chunk = payload[stat.offset : stat.offset + size]
        dest = samples_dir / f"reshw_{idx:02d}_0x{stat.offset:06X}.bin"
        dest.write_bytes(chunk)
        written.append(dest)
    return written


def build_report(
    input_path: Path,
    payload: bytes,
    stats: Sequence[WindowStats],
    candidates: Sequence[WindowStats],
    sample_paths: Sequence[Path],
    window: int,
    step: int,
) -> str:
    lines: List[str] = [
        "# RES-HW Container Probe",
        "",
        f"- Source: `{input_path}`",
        f"- Size: {len(payload):,} bytes",
        f"- Sliding window: {window} bytes (step {step})",
        "",
        "## Candidate regions",
        "",
        "| Offset | Entropy | ASCII% | Zero% | Common little-endian words | Sample |",
        "|--------|---------|--------|-------|-----------------------------|--------|",
    ]
    for stat, sample in zip(candidates, sample_paths):
        lines.append(
            f"| `0x{stat.offset:06X}` | {stat.entropy:4.2f} | {stat.ascii_ratio*100:5.1f} | "
            f"{stat.zero_ratio*100:5.1f} | {stat.word_summary} | `{sample.name}` |"
        )

    lines.extend(
        [
            "",
            "## Observations",
            "",
        ]
    )

    for stat in candidates:
        notes = []
        if stat.ascii_ratio > 0.3:
            notes.append("significant ASCII text")
        if stat.entropy < 5.0:
            notes.append("low entropy (possible header/table)")
        if stat.entropy > 7.2:
            notes.append("high entropy (compressed/bitmap region)")
        if stat.zero_ratio > 0.1:
            notes.append("padding present")
        alignment = []
        if stat.offset % 0x200 == 0:
            alignment.append("0x200")
        if stat.offset % 0x1000 == 0:
            alignment.append("0x1000")
        if alignment:
            notes.append(f"aligned to {'/'.join(alignment)} boundary")
        description = ", ".join(notes) if notes else "mixed entropy, review manually"
        lines.append(f"- `0x{stat.offset:06X}`: {description}.")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level)

    LOGGER.info("Reading %s", args.input)
    payload = args.input.read_bytes()

    LOGGER.info("Computing sliding-window statistics")
    windows = compute_windows(payload, args.window, args.step)
    if not windows:
        raise SystemExit("No windows computed; adjust window/step sizes.")

    LOGGER.info("Ranking candidate offsets")
    candidates = select_candidates(windows, args.top)
    if not candidates:
        raise SystemExit("Could not identify candidate regions.")

    LOGGER.info("Writing sample snippets")
    samples = write_samples(payload, candidates, args.samples)

    LOGGER.info("Building report")
    report = build_report(args.input, payload, windows, candidates, samples, args.window, args.step)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")

    LOGGER.info("Wrote %s", args.output)


if __name__ == "__main__":
    main()
