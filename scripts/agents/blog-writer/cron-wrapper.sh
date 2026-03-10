#!/usr/bin/env bash
# Thin cron wrapper for run.sh.
# Cron runs in a bare environment; this script sets PATH and sources credentials
# before handing off to the main pipeline.
#
# Crontab entry (already configured):
#   TZ=America/New_York
#   0 9 * * 2 /home/developer/code/encypherai-commercial/scripts/agents/blog-writer/cron-wrapper.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LOG=/var/log/encypher-blog-writer.log

# Extend PATH so cron's bare environment can find all required tools:
#   - /home/developer/.local/bin : claude, uv, uvx
#   - /usr/local/bin             : common local installs
#   - /usr/bin                   : node, gh, git (already present in most cron envs, but be explicit)
export PATH="/home/developer/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Source credentials file used by the image-generation and signing pipelines.
# Expected keys: ANTHROPIC_API_KEY, GEMINI_API_KEY, ENCYPHER_API_KEY, GH_TOKEN
if [ -f "$REPO_ROOT/.env.skills" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$REPO_ROOT/.env.skills"
  set +a
else
  echo "[cron-wrapper] WARNING: $REPO_ROOT/.env.skills not found — API keys may be missing." >&2
fi

exec "$SCRIPT_DIR/run.sh" "$@" >> "$LOG" 2>&1
