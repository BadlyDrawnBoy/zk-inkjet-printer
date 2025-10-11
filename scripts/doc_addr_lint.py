#!/usr/bin/env python3
"""
Scan documentation for ambiguous short hex addresses (likely file offsets) that
should be rewritten as full VAs with optional file-offset annotations.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PATTERNS = [
    re.compile(r"0x0[0-9a-fA-F]{5,7}(?![0-9a-fA-F])\\b"),
    re.compile(r"0x[0-9a-fA-F]{5}(?![0-9a-fA-F])\\b"),
]


def iter_doc_files() -> list[Path]:
    for path in DOCS.rglob("*.md"):
        if path.is_relative_to(DOCS / "archive"):
            continue
        yield path


def main() -> int:
    hits = []
    for path in iter_doc_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            low_line = line.lower()
            if "file+0x" in low_line:
                continue
            for pattern in PATTERNS:
                for match in pattern.finditer(line):
                    snippet = line.strip()
                    hits.append((path.relative_to(ROOT), lineno, match.group(0), snippet))
    if hits:
        for rel_path, lineno, addr, snippet in hits:
            print(f"{rel_path}:{lineno}: ambiguous address {addr} -> {snippet}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
