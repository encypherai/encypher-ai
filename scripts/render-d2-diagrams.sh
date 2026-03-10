#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CHECK_ONLY="${1:-}"
mapfile -t SOURCES < <(find "$ROOT/docs/diagrams" "$ROOT/apps/dashboard/docs/diagrams" "$ROOT/integrations/chrome-extension/docs" "$ROOT/integrations/wordpress-provenance-plugin/docs" -type f -name '*.d2' | sort)

if [[ ${#SOURCES[@]} -eq 0 ]]; then
  echo "No D2 source files found."
  exit 1
fi

if [[ "$CHECK_ONLY" == "--check" ]]; then
  echo "Validated ${#SOURCES[@]} D2 source files:"
  for src in "${SOURCES[@]}"; do
    echo "- ${src#$ROOT/} -> ${src#$ROOT/}"
  done
  exit 0
fi

if ! command -v d2 >/dev/null 2>&1; then
  echo "d2 CLI not found. Install d2 and rerun this script, or use --check to validate sources only."
  exit 1
fi

for src in "${SOURCES[@]}"; do
  out="${src%.d2}.svg"
  d2 "$src" "$out"
  echo "Rendered ${src#$ROOT/} -> ${out#$ROOT/}"
done
