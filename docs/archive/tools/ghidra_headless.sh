#!/usr/bin/env bash
set -euo pipefail

# NOTE: Archived legacy headless workflow.
#       Superseded by the ghidraMCP tooling documented in docs/archive/ghidra_headless_cli.md.

# Kurze Log-Funktion
msg() { echo "[gh] $*"; }

# Repo-Root und Standardpfade (alles absolut, damit Aufruf-Ort egal ist)
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
OUTDIR="${ROOT}/data/processed"
PROJROOT="${ROOT}/.ghidra_tmp"
PROJDIR="${PROJROOT}/project"
PROJNAME="zk_inkjet_headless"
SCRIPT_PATH="${ROOT}/ghidra_scripts"

# Ghidra-Postscripts (optional)
CALLGRAPH_SCRIPT="export_io_callgraph.py"
UPGRADE_SCRIPT="export_upgrade_orchestrator_disasm.py"

# --- Auto-Detect von GHIDRA_HOME ---
autodetect_ghidra() {
  local ah ah_path cand

  # 1) Bereits gesetztes GHIDRA_HOME gültig?
  if [[ -n "${GHIDRA_HOME:-}" ]]; then
    ah="${GHIDRA_HOME%/}/support/analyzeHeadless"
    if [[ -x "$ah" ]]; then
      return 0
    fi
  fi

  # 2) analyzeHeadless im PATH?
  if command -v analyzeHeadless >/dev/null 2>&1; then
    ah_path="$(command -v analyzeHeadless)"
    # GHIDRA_HOME = zwei Ebenen über dem Launcher
    export GHIDRA_HOME="$(cd "$(dirname "$ah_path")/.." && pwd)"
    return 0
  fi

  # 3) Übliche Installationsorte testen (inkl. /opt/ghidra Symlink)
  shopt -s nullglob
  local cands=(/opt/ghidra /opt/ghidra_* "$HOME"/ghidra "$HOME"/ghidra_*)
  shopt -u nullglob
  for cand in "${cands[@]}"; do
    [[ -e "$cand" ]] || continue
    # Falls Symlink, realen Pfad auflösen (sofern verfügbar)
    if command -v readlink >/dev/null 2>&1; then
      cand="$(readlink -f "$cand" 2>/dev/null || printf '%s' "$cand")"
    fi
    ah="${cand%/}/support/analyzeHeadless"
    if [[ -x "$ah" ]]; then
      export GHIDRA_HOME="$cand"
      msg "Auto-detected GHIDRA_HOME=${GHIDRA_HOME}"
      return 0
    fi
  done

  return 1
}

# --- GHIDRA_HOME sicherstellen (oder soft-skip) ---
if ! autodetect_ghidra; then
  msg "GHIDRA_HOME not set and no Ghidra found; skipping (exit 0)."
  exit 0
fi

ANALYZE="${GHIDRA_HOME%/}/support/analyzeHeadless"
if [[ ! -x "$ANALYZE" ]]; then
  msg "analyzeHeadless not found at $ANALYZE; skipping (exit 0)."
  exit 0
fi

# --- Eingabebinary ermitteln ---
DEFAULT_BIN="${ROOT}/data/raw/ZK-INKJET-NANO-APP.bin"
BIN_INPUT="${1:-$DEFAULT_BIN}"
if [[ "$BIN_INPUT" != /* ]]; then
  BIN_INPUT="${ROOT}/${BIN_INPUT}"
fi
if command -v realpath >/dev/null 2>&1; then
  BIN="$(realpath "$BIN_INPUT" 2>/dev/null || printf '%s' "$BIN_INPUT")"
else
  BIN="$BIN_INPUT"
fi

if [[ ! -f "$BIN" ]]; then
  msg "Input binary not found: $BIN"
  exit 1
fi

# --- Laufzeitumgebung vorbereiten (keine Commits, nur lokale Caches) ---
CFG="${ROOT}/ghidra_cfg"
CACHE="${ROOT}/ghidra_cache"
TMP="${ROOT}/ghidra_tmp"
mkdir -p "$CFG" "$CACHE" "$TMP" "$OUTDIR" "$PROJDIR"

export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$CFG}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$CACHE}"
# Falls GHIDRA_JAVA_HOME gesetzt, aber ungültig → ignorieren
if [[ -n "${GHIDRA_JAVA_HOME:-}" && ! -d "$GHIDRA_JAVA_HOME" ]]; then
  unset GHIDRA_JAVA_HOME
fi
export GHIDRA_JVM_ARGS="${GHIDRA_JVM_ARGS:-} -Dapplication.cachedir=${CACHE} -Dapplication.tempdir=${TMP} -Djava.io.tmpdir=${TMP}"

# --- analyzeHeadless Argumente bauen ---
ARGS=(
  "$ANALYZE" "$PROJDIR" "$PROJNAME"
  -import "$BIN"
  -loader BinaryLoader
  -scriptPath "$SCRIPT_PATH"
)

# Callgraph-Export (wenn Script existiert)
CALLGRAPH_SOURCE="${SCRIPT_PATH}/${CALLGRAPH_SCRIPT}"
CALLGRAPH_PATH="${OUTDIR}/io_callgraph.json"
if [[ -f "$CALLGRAPH_SOURCE" ]]; then
  ARGS+=( -postScript "$CALLGRAPH_SCRIPT" "out=$CALLGRAPH_PATH" )
else
  msg "Warning: ${CALLGRAPH_SOURCE#$ROOT/} missing; callgraph will not refresh."
fi

# Optional: Disassembly-Export (wenn Script existiert)
UPGRADE_SOURCE="${SCRIPT_PATH}/${UPGRADE_SCRIPT}"
UPGRADE_PATH="${OUTDIR}/upgrade_orchestrator_disasm.txt"
if [[ -f "$UPGRADE_SOURCE" ]]; then
  # Hinweis: PostScript darf fehlen; dann einfach weglassen
  ARGS+=( -postScript "$UPGRADE_SCRIPT" "out=${OUTDIR}/upgrade_orchestrator_disasm.txt" )
fi

# --- Start ---
"${ARGS[@]}"

msg "Done. Artifacts should be under ${OUTDIR#$ROOT/}/."
