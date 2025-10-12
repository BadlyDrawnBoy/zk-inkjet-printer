#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/make_export.sh [--dry-run] [--with-binaries] [--include-dwin] [--outdir <dir>]

Erzeugt ein teilbares .tgz des Repos mit sauberen Filtern:
- Standard: ohne große Binaries (data/raw/*), ohne DWIN/.
- --with-binaries   : nimmt data/raw/* auf (Firmware/Assets).
- --include-dwin    : nimmt DWIN/ mit (sehr groß).
- --dry-run         : zeigt die Dateiliste, packt aber nicht.
- --outdir <dir>    : Zielordner (Default: export).

NBSP/Unicode in Dateinamen werden mit -print0/--null korrekt behandelt.
EOF
}

DRY_RUN=false
WITH_BIN=false
INCLUDE_DWIN=false
OUTDIR="export"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --with-binaries) WITH_BIN=true ;;
    --include-dwin) INCLUDE_DWIN=true ;;
    --outdir) shift; OUTDIR="${1:-export}" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unbekannte Option: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

mkdir -p "$OUTDIR"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
OUTFILE="$OUTDIR/zk-inkjet-export-$STAMP.tgz"
MANIFEST_PATH="$OUTDIR/EXPORT_MANIFEST.txt"

tmp_list="$(mktemp)"
cleanup() { rm -f "$tmp_list"; }
trap cleanup EXIT

# ---------- find-Argumente aufbauen ----------
FIND_ARGS=(
  -path './.git' -prune -o
  -path './.venv' -prune -o
  -path './.pytest_cache' -prune -o
  -type d -name '__pycache__' -prune -o
  -path './export' -prune -o
  -path './.codex' -prune -o
  -path './.idea' -prune -o
  # Ghidra-Artefakte
  -path './ghidra_cfg' -prune -o
  -path './ghidra_cache' -prune -o
  -path './ghidra_projects' -prune -o
  -path './ghidra_scripts' -prune -o
  # UI-Autotune/Sweep-Outputs
  -path './uiqvga_out' -prune -o
  -path './uiqvga_sweep' -prune -o
  -path './uiqvga_autotune_out' -prune -o
)

# DWIN optional ausschließen
if ! $INCLUDE_DWIN; then
  FIND_ARGS+=(-path './DWIN' -prune -o)
fi

# data/raw: CHECKSUMS.txt immer erlauben; Rest nur falls --with-binaries
if ! $WITH_BIN; then
  if [[ -f ./data/raw/CHECKSUMS.txt ]]; then
    printf '%s\0' "./data/raw/CHECKSUMS.txt" > "$tmp_list"
  fi
  FIND_ARGS+=(-path './data/raw' -prune -o)
fi

# Restliche Datei-Filter
FIND_ARGS+=(
  -type f
  -not -name '*.pyc'
  -not -name '*.pyo'
  -not -name '*.log'
  -print0
)

# ---------- Liste erzeugen ----------
# Anhängen, da CHECKSUMS.txt ggf. bereits geschrieben wurde
find . "${FIND_ARGS[@]}" >> "$tmp_list"

if $DRY_RUN; then
  echo "=== DRY RUN: Dateien, die in $OUTFILE landen würden ==="
  tr '\0' '\n' < "$tmp_list" | sed 's|^\./||' | sort
  exit 0
fi

tar --null -czf "$OUTFILE" --files-from "$tmp_list"

COUNT_FILES="$(tr -cd '\0' < "$tmp_list" | wc -c | awk '{print $1}')"
if command -v sha256sum >/dev/null 2>&1; then
  SHA256="$(sha256sum "$OUTFILE" | awk '{print $1}')"
else
  SHA256=""
fi
if stat -c%s "$OUTFILE" >/dev/null 2>&1; then
  SIZE_BYTES="$(stat -c%s "$OUTFILE")"
else
  SIZE_BYTES="$(wc -c < "$OUTFILE")"
fi

{
  echo "Export:        $OUTFILE"
  echo "UTC:           $STAMP"
  echo "Dateien:       $COUNT_FILES"
  echo "Größe (Bytes): $SIZE_BYTES"
  [[ -n "$SHA256" ]] && echo "SHA256:        $SHA256"
  echo
  echo "Schalter:"
  echo "  WITH_BIN=$WITH_BIN"
  echo "  INCLUDE_DWIN=$INCLUDE_DWIN"
  echo
  echo "Enthaltene Dateien:"
  tr '\0' '\n' < "$tmp_list" | sed 's|^\./||' | sort
} > "$MANIFEST_PATH"

echo "✔ Export erstellt: $OUTFILE"
echo "ℹ Manifest:        $MANIFEST_PATH"
