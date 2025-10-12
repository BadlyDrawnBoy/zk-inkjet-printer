#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
OUTDIR="${ROOT}/data/processed"
PROJROOT="${ROOT}/.ghidra_tmp"
PROJDIR="${PROJROOT}/project"
PROJNAME="zk_inkjet_headless"
CALLGRAPH_SCRIPT="export_io_callgraph.py"
UPGRADE_SCRIPT="export_upgrade_orchestrator_disasm.py"
SCRIPT_PATH="${ROOT}/ghidra_scripts"

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

msg() { echo "[gh] $*"; }

if [[ -z "${GHIDRA_HOME:-}" ]]; then
	msg "GHIDRA_HOME not set; skipping (exit 0)."
	exit 0
fi

ANALYZE="${GHIDRA_HOME%/}/support/analyzeHeadless"
if [[ ! -x "$ANALYZE" ]]; then
	msg "analyzeHeadless not found at $ANALYZE; skipping (exit 0)."
	exit 0
fi

if [[ ! -f "$BIN" ]]; then
	msg "Input binary not found: $BIN"
	exit 1
fi

CFG="${ROOT}/ghidra_cfg"
CACHE="${ROOT}/ghidra_cache"
TMP="${ROOT}/ghidra_tmp"
mkdir -p "$CFG" "$CACHE" "$TMP"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$CFG}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$CACHE}"
export GHIDRA_JAVA_HOME="${GHIDRA_JAVA_HOME:-/usr/lib/jvm/jdk-21.0.8-oracle-x64}"
export GHIDRA_JVM_ARGS="${GHIDRA_JVM_ARGS:-} -Dapplication.cachedir=${CACHE} -Dapplication.tempdir=${TMP} -Djava.io.tmpdir=${TMP}"

mkdir -p "$OUTDIR" "$PROJDIR"

ARGS=(
	"$ANALYZE" "$PROJDIR" "$PROJNAME"
	-import "$BIN"
	-scriptPath "$SCRIPT_PATH"
)

CALLGRAPH_PATH="${OUTDIR}/io_callgraph.json"
CALLGRAPH_SOURCE="${SCRIPT_PATH}/${CALLGRAPH_SCRIPT}"
if [[ -f "$CALLGRAPH_SOURCE" ]]; then
	ARGS+=( -postScript "$CALLGRAPH_SCRIPT" "out=$CALLGRAPH_PATH" )
else
	msg "Warning: ${CALLGRAPH_SOURCE#$ROOT/} missing; callgraph will not refresh."
fi

UPGRADE_PATH="${OUTDIR}/upgrade_orchestrator_disasm.txt"
UPGRADE_SOURCE="${SCRIPT_PATH}/${UPGRADE_SCRIPT}"
if [[ -f "$UPGRADE_SOURCE" ]]; then
	ARGS+=( -postScript "$UPGRADE_SCRIPT" "out=$UPGRADE_PATH" )
fi

"${ARGS[@]}"

msg "Done. Artifacts should be under ${OUTDIR#$ROOT/}/."
