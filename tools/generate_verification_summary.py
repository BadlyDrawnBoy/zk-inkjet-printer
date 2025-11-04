#!/usr/bin/env python3
"""Generate verification summary tables from findings front matter."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FINDINGS_DIR = REPO_ROOT / "docs" / "findings"
TARGET_FILES = [
    REPO_ROOT / "docs" / "VERIFICATION_STATUS.md",
    REPO_ROOT / "docs" / "README.md",
]
BEGIN_MARKER = "<!-- BEGIN AUTO-GENERATED TABLE -->"
END_MARKER = "<!-- END AUTO-GENERATED TABLE -->"


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path} is missing YAML front matter")
    metadata: dict[str, str] = {}
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("\"") and value.endswith("\""):
            value = value[1:-1]
        metadata[key] = value
    return metadata


def build_table(rows: list[tuple[str, str, str, str, str]]) -> str:
    table_lines = [
        "| Finding | Status | Confidence | Last Verified | Provenance |",
        "| --- | --- | --- | --- | --- |",
    ]
    for finding, status, confidence, last_verified, provenance in rows:
        table_lines.append(
            f"| {finding} | {status} | {confidence} | {last_verified} | {provenance} |"
        )
    return "\n".join(table_lines)


def collect_rows() -> list[tuple[str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str]] = []
    for path in sorted(FINDINGS_DIR.glob("*.md")):
        metadata = parse_front_matter(path)
        title = metadata.get("title", path.stem.replace("_", " ").title())
        link = path.relative_to(REPO_ROOT / "docs")
        finding = f"[{title}]({link.as_posix()})"
        status = metadata.get("status_display") or metadata.get("status", "—")
        confidence = metadata.get("confidence", "—")
        last_verified = metadata.get("last_verified", "—")
        provenance_value = metadata.get("provenance", "")
        if provenance_value:
            label = Path(provenance_value).name
            provenance = f"[{label}]({provenance_value})"
        else:
            provenance = "—"
        rows.append((finding, status, confidence, last_verified, provenance))
    return rows


def update_file(path: Path, table: str) -> None:
    content = path.read_text(encoding="utf-8")
    if BEGIN_MARKER not in content or END_MARKER not in content:
        raise ValueError(f"Missing table markers in {path}")
    start = content.index(BEGIN_MARKER) + len(BEGIN_MARKER)
    end = content.index(END_MARKER, start)
    replacement = f"\n{table}\n"
    updated = content[:start] + replacement + content[end:]
    path.write_text(updated, encoding="utf-8")


def main() -> int:
    if not FINDINGS_DIR.exists():
        print("Findings directory not found", file=sys.stderr)
        return 1
    rows = collect_rows()
    table = build_table(rows)
    for target in TARGET_FILES:
        update_file(target, table)
    print(f"Updated verification summary for {len(rows)} findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
