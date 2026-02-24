#!/usr/bin/env bash
# Cron wrapper for the blog-writer pipeline.
#
# Scheduled via crontab (TZ=America/New_York):
#   0 9 * * 2  /home/developer/code/encypherai-commercial/scripts/agents/blog-writer/cron-wrapper.sh
#
# Secrets: ~/.config/encypher/blog-writer.env (chmod 600)
# Logs:    /home/developer/code/encypherai-commercial/logs/blog-writer.log

set -euo pipefail

REPO_ROOT="/home/developer/code/encypherai-commercial"
ENV_FILE="/home/developer/.config/encypher/blog-writer.env"
LOG_FILE="$REPO_ROOT/logs/blog-writer.log"
SCRIPT_DIR="$REPO_ROOT/scripts/agents/blog-writer"

# --- logging ---
exec >> "$LOG_FILE" 2>&1
echo ""
echo "========================================"
echo "Blog writer started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "========================================"

# --- load secrets ---
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found. Create it and fill in credentials."
  exit 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

if [ -z "${GH_TOKEN:-}" ]; then
  echo "ERROR: GH_TOKEN must be set in $ENV_FILE"
  exit 1
fi

# --- PATH: include claude CLI location ---
export PATH="/home/developer/.local/bin:/usr/bin:/usr/local/bin:$PATH"

# --- authenticate git over HTTPS using GH_TOKEN for the duration of this script ---
# Embeds the token in the remote URL; restored to the clean URL on exit.
CLEAN_GIT_URL="https://github.com/encypherai/encypherai-commercial.git"
AUTH_GIT_URL="https://x-access-token:${GH_TOKEN}@github.com/encypherai/encypherai-commercial.git"
git -C "$REPO_ROOT" remote set-url origin "$AUTH_GIT_URL"

# --- Gemini image generation ---
if [ -n "${GEMINI_API_KEY:-}" ]; then
  echo "GEMINI_API_KEY=$GEMINI_API_KEY" > "$REPO_ROOT/.env.skills"
  echo "Image generation enabled."
else
  echo "GEMINI_API_KEY not set - image generation will be skipped."
fi

# --- fake GITHUB_OUTPUT so run.sh can signal draft PR URL ---
GITHUB_OUTPUT=$(mktemp)
export GITHUB_OUTPUT

cleanup() {
  git -C "$REPO_ROOT" remote set-url origin "$CLEAN_GIT_URL"
  rm -f "$GITHUB_OUTPUT" "$REPO_ROOT/.env.skills"
}
trap cleanup EXIT

# --- run the pipeline ---
bash "$SCRIPT_DIR/run.sh"
PIPELINE_EXIT=$?

if [ "$PIPELINE_EXIT" -ne 0 ]; then
  echo "Pipeline exited with code $PIPELINE_EXIT"
fi

# --- notify reviewer if a draft PR was created ---
DRAFT_PR_URL=$(grep "^draft_pr_url=" "$GITHUB_OUTPUT" 2>/dev/null | cut -d= -f2- | head -1)
if [ -n "${DRAFT_PR_URL:-}" ]; then
  echo "Draft PR detected - sending reviewer notification..."
  PR_URL="$DRAFT_PR_URL" python3 "$SCRIPT_DIR/notify-reviewer.py"
fi

echo "Blog writer finished: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
