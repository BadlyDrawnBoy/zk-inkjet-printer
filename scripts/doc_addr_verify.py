#!/usr/bin/env python3
import re, sys
from pathlib import Path

BASE = 0x00200000  # APP base
DOCS = Path("docs")
APP  = Path("data/raw/ZK-INKJET-NANO-APP.bin")
APP_SIZE = APP.stat().st_size if APP.exists() else None

PAIR = re.compile(r'VA 0x([0-9A-Fa-f]{7,8})\s*\(file\+0x([0-9A-Fa-f]{6,8})\)')
BAD_ADJUST = re.compile(r'--adjust-vma\s*=\s*VA\s', re.IGNORECASE)
NUM_ADJUST = re.compile(r'--adjust-vma\s*=\s*0x([0-9A-Fa-f]+)')

pairs = 0
mismatches = []
oversize = []
bad_adjust = []

doc_files = sorted(DOCS.glob("*.md"))
for p in doc_files:
    text = p.read_text(encoding="utf-8", errors="ignore")
    # 1) verbotene Schreibweise '--adjust-vma=VA ...'
    for i, line in enumerate(text.splitlines(), 1):
        if BAD_ADJUST.search(line):
            bad_adjust.append((str(p), i, line.strip()))
    # 2) VA/FO-Paare prüfen
    for m in PAIR.finditer(text):
        pairs += 1
        va = int(m.group(1), 16)
        fo = int(m.group(2), 16)
        ok_math = (va - BASE == fo) or (((va & ~1) - BASE) == (fo & ~1))  # Thumb erlaubt
        if not ok_math:
            line_no = text.count("\n", 0, m.start()) + 1
            expected = (va - BASE) & 0xFFFFFFFF
            mismatches.append((str(p), line_no, m.group(0), va, fo, expected))
        if APP_SIZE is not None and fo >= APP_SIZE:
            line_no = text.count("\n", 0, m.start()) + 1
            oversize.append((str(p), line_no, m.group(0), fo, APP_SIZE))

print(f"Checked {pairs} VA/file pairs across {len(doc_files)} docs.")

# Meldungen
exit_code = 0

if bad_adjust:
    print("\nFound suspicious '--adjust-vma=VA ...' usages (must be numeric):")
    for f, i, line in bad_adjust:
        print(f"  {f}:{i}: {line}")
    exit_code = 1

if mismatches:
    print(f"\nMISMATCHES ({len(mismatches)}) with BASE=0x{BASE:08X}:")
    for f, i, entry, va, fo, exp in mismatches:
        print(f"  {f}:{i}: {entry}")
        print(f"    -> VA-BASE = 0x{exp:08X}, but doc has file+0x{fo:08X}")
    exit_code = 1

if oversize:
    print(f"\nOUT-OF-RANGE file+ offsets ({len(oversize)}) vs {APP} size {APP_SIZE} bytes:")
    for f, i, entry, fo, size in oversize:
        print(f"  {f}:{i}: {entry}")
        print(f"    -> file+0x{fo:08X} >= file_size 0x{size:08X}")
    exit_code = 1

if exit_code == 0:
    print("All VA/file pairs are mathematically consistent and within file size.")

sys.exit(exit_code)
