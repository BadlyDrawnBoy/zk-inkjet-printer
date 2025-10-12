#!/usr/bin/env bash
set -euo pipefail

OUTDIR="export"
PREFIX="zk-inkjet-export"
WITH_BINARIES=0
INCLUDE_DWIN=0
DRY_RUN=0

usage() {
  cat <<USAGE
Usage: $0 [--with-binaries] [--include-dwin] [--outdir DIR] [--prefix NAME] [--dry-run]
  --with-binaries   Nimmt die Firmware/Assets aus data/raw/ ins Paket auf.
  --include-dwin    Nimmt den kompletten DWIN/-Baum mit (groß; NBSP-Namen!).
  --outdir DIR      Zielverzeichnis (Default: export).
  --prefix NAME     Dateiname-Präfix (Default: zk-inkjet-export).
  --dry-run         Nur anzeigen, was gepackt würde.
USAGE
}

# Argumente parsen
while (( $# )); do
  case "$1" in
    --with-binaries) WITH_BINARIES=1 ;;
    --include-dwin)  INCLUDE_DWIN=1 ;;
    --outdir)        OUTDIR="${2:?}"; shift ;;
    --prefix)        PREFIX="${2:?}"; shift ;;
    --dry-run)       DRY_RUN=1 ;;
    -h|--help)       usage; exit 0 ;;
    *) echo "Unbekannte Option: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

mkdir -p "$OUTDIR"

# Zeitstempel für reproduzierbare Namen
TS="$(date -u +%Y%m%d-%H%M%S)"
ARCHIVE="$OUTDIR/${PREFIX}-${TS}.tgz"

# Dateien sammeln (als Bash-Array; später null-terminiert an tar)
files=()

add_if_exists() {
  local f
  for f in "$@"; do
    if [[ -e "$f" ]]; then
      files+=("$f")
    fi
  done
}

# Kern-Dokumentation & Metadaten
add_if_exists \
  AGENTS.md PROJECT_STATUS.md README.md .gitattributes .gitignore \
  requirements-dev.txt tools/VERSIONS.md tools/make_export.sh

# Docs
while IFS= read -r -d '' f; do files+=("$f"); done < <(find docs -type f -name '*.md' -print0 2>/dev/null || true)

# Scripts & Tests
while IFS= read -r -d '' f; do files+=("$f"); done < <(find scripts -type f -name '*.py' -print0 2>/dev/null || true)
while IFS= read -r -d '' f; do files+=("$f"); done < <(find tests -type f -print0 2>/dev/null || true)

# Rohdaten – immer die Checksummen
add_if_exists data/raw/CHECKSUMS.txt

# Optional: Binaries
if [[ $WITH_BINARIES -eq 1 ]]; then
  add_if_exists \
    data/raw/ZK-INKJET-NANO-APP.bin \
    data/raw/ZK-INKJET-NANO-BOOT.bin \
    data/raw/ZK-INKJET-RES-HW.zkml \
    data/raw/ZK-INKJET-UI-QVGA.bin
fi

# Optional: DWIN (NBSP-tauglich, via null-terminierte Liste)
TMPLIST="$(mktemp)"
trap 'rm -f "$TMPLIST"' EXIT
# Eigene Liste (files[]) zuerst null-terminiert ablegen
printf '%s\0' "${files[@]}" > "$TMPLIST"

if [[ $INCLUDE_DWIN -eq 1 && -d DWIN ]]; then
  # Alle Dateien unter DWIN anhängen (null-terminiert)
  find DWIN -type f -print0 >> "$TMPLIST"
fi

if [[ $DRY_RUN -eq 1 ]]; then
  echo "=== DRY RUN: Dateien, die in $ARCHIVE landen würden ==="
  # Schön ausgeben (eine pro Zeile), ohne an den Bytes rumzudoktern
  tr '\0' '\n' < "$TMPLIST"
  exit 0
fi

# Archiv erstellen (null-terminiert, robust gegen Leerzeichen/NBSP)
# -z: gzip, -c: create, -f: filename, --null: files-from ist null-terminiert
# --owner/--group für deterministischere Tarballs
tar --null --files-from="$TMPLIST" \
    --owner=0 --group=0 \
    -czf "$ARCHIVE"

echo "OK: $ARCHIVE erstellt ($(wc -c < "$ARCHIVE") Bytes)"
