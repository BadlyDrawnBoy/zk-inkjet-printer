# scripts/gh.sh
#!/usr/bin/env bash
set -euo pipefail

# Repo-local dirs (safe in Codex sandboxes)
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="${ROOT}/ghidra_cfg"
CACHE="${ROOT}/ghidra_cache"
TMP="${ROOT}/ghidra_tmp"

mkdir -p "$CFG" "$CACHE" "$TMP"

# Make Ghidra store config under the repo (prevents JDK prompt + HOME/.config writes)
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$CFG}"

# Optional but nice: XDG cache points at our repo-local cache too
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$CACHE}"

# Ensure we run with the JDK you already have
export GHIDRA_JAVA_HOME="${GHIDRA_JAVA_HOME:-/usr/lib/jvm/jdk-21.0.8-oracle-x64}"

# Critical: override Ghidra's cache/temp locations (NOT ghidra.cache.dir)
# Also set java.io.tmpdir as belt-and-suspenders for JNA/other libs.
export GHIDRA_JVM_ARGS="${GHIDRA_JVM_ARGS:-} \
  -Dapplication.cachedir=${CACHE} \
  -Dapplication.tempdir=${TMP} \
  -Djava.io.tmpdir=${TMP}
"

# Hand off to the real headless launcher with all user args
exec ghidraHeadless "$@"

