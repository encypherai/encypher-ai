#!/usr/bin/env bash
# Encypher Automated Blog Writer
#
# Pipeline:
#   Phase 1 -- Sonnet research:  selects topic, formulates thesis, gathers verified sources
#   Phase 2 -- Opus writer:      reads research notes, writes post, commits markdown
#   Phase 3 -- Sonnet image:     generates blog header image via Gemini API, commits PNG
#   Phase 4 -- Sonnet review:    structured approval/rejection against quality criteria
#   Phase 5 -- Revision loop:    Opus revises (--resume), Sonnet re-reviews (up to MAX_REVISIONS)
#   Phase 6 -- Push + PR:        regular PR if approved, draft PR if not (skipped in --test mode)
#
# Cron schedule (Tuesday 9:00 AM EST = 14:00 UTC):
#   0 14 * * 2 /path/to/repo/scripts/agents/blog-writer/run.sh >> /var/log/encypher-blog-writer.log 2>&1
#
# Usage:
#   ./run.sh                    # auto-select topic from TOPICS.md
#   ./run.sh "custom topic"     # override with a specific topic hint
#   ./run.sh --test             # run all phases on current branch, no push/PR
#   ./run.sh --test "topic"     # test mode with a specific topic hint
#
# Requirements:
#   - claude CLI installed and authenticated
#   - jq installed (for JSON parsing)
#   - gh CLI installed and authenticated (not required in --test mode)
#   - .env.skills at repo root with GEMINI_API_KEY (for image generation)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
BLOG_DIR="apps/marketing-site/src/content/blog"
RESEARCH_PROMPT_FILE="$REPO_ROOT/scripts/agents/blog-writer/RESEARCH_PROMPT.md"
AGENT_PROMPT_FILE="$REPO_ROOT/scripts/agents/blog-writer/AGENT_PROMPT.md"
REVIEW_PROMPT_FILE="$REPO_ROOT/scripts/agents/blog-writer/REVIEW_PROMPT.md"
BRANCH_PREFIX="blog/auto"
TODAY="$(date +%Y-%m-%d)"
BRANCH_NAME="$BRANCH_PREFIX-$TODAY"
CUSTOM_TOPIC=""
TEST_MODE=false
MAX_REVISIONS=2

log() { echo "[$(date -u +%H:%M:%S)] $*"; }

# Allow claude -p subprocesses when this script is invoked from inside a Claude Code session
unset CLAUDECODE

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --test) TEST_MODE=true ;;
    *) CUSTOM_TOPIC="$arg" ;;
  esac
done

# ----- pre-flight checks -----
log "Starting blog writer pipeline for $TODAY (test=$TEST_MODE)"

for cmd in claude jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: '$cmd' not found." >&2
    exit 1
  fi
done

if [ "$TEST_MODE" = false ] && ! gh auth status &>/dev/null; then
  echo "ERROR: gh CLI not authenticated. Run 'gh auth login'" >&2
  exit 1
fi

# ----- git setup (skipped in test mode) -----
cd "$REPO_ROOT"

if [ "$TEST_MODE" = false ]; then
  log "Checking out main and pulling latest..."
  git checkout main
  git pull origin main

  # Idempotent: skip if today's branch already exists on remote
  if git ls-remote --exit-code --heads origin "$BRANCH_NAME" &>/dev/null; then
    log "Branch $BRANCH_NAME already exists on remote. Skipping."
    exit 0
  fi

  git checkout -b "$BRANCH_NAME"
  log "Created branch: $BRANCH_NAME"
else
  log "Test mode: running on branch $(git rev-parse --abbrev-ref HEAD)"
fi

# Research notes written inside the repo so the Write tool can reach them.
# The file is deleted on exit and is .gitignored.
RESEARCH_NOTES="$REPO_ROOT/.blog-research-temp.md"
cleanup() { rm -f "$RESEARCH_NOTES"; }
trap cleanup EXIT

# =========================================================================
# Phase 1 -- Sonnet research agent
# =========================================================================
log "Phase 1: Sonnet research agent..."

RESEARCH_PROMPT="$(sed \
  -e "s|CURRENT_DATE|$TODAY|g" \
  -e "s|RESEARCH_OUTPUT_PATH|$RESEARCH_NOTES|g" \
  "$RESEARCH_PROMPT_FILE")"

if [ -n "$CUSTOM_TOPIC" ]; then
  RESEARCH_PROMPT="$RESEARCH_PROMPT

## OVERRIDE: Requested Topic
The operator has requested research on: \"$CUSTOM_TOPIC\"
Select this topic instead of consulting TOPICS.md, but still follow all other steps."
fi

claude -p "$RESEARCH_PROMPT" \
  --allowedTools "Read,Glob,Grep,WebSearch,Write,Bash(ls *),Bash(mkdir *)" \
  --output-format json > /dev/null || {
  log "ERROR: Research agent failed."
  exit 1
}

if [ ! -s "$RESEARCH_NOTES" ]; then
  log "ERROR: Research agent did not produce output at $RESEARCH_NOTES"
  exit 1
fi

log "Research notes saved. Topic: $(grep -m1 '^## Topic' -A1 "$RESEARCH_NOTES" | tail -1 | tr -d '[:space:]')"

# =========================================================================
# Phase 2 -- Opus writer
# =========================================================================
log "Phase 2: Opus writer agent..."

WRITER_PROMPT="$(sed \
  -e "s|CURRENT_DATE|$TODAY|g" \
  -e "s|RESEARCH_NOTES_PATH|$RESEARCH_NOTES|g" \
  "$AGENT_PROMPT_FILE")"

WRITER_JSON=$(claude -p "$WRITER_PROMPT" \
  --model claude-opus-4-6 \
  --allowedTools "Read,Write,Glob,Bash(git add *),Bash(git commit *),Bash(git diff *),Bash(git status *),Bash(ls *)" \
  --output-format json) || {
  log "ERROR: Writer agent failed."
  exit 1
}

WRITER_SESSION=$(echo "$WRITER_JSON" | jq -r '.session_id // empty')
log "Writer session ID: ${WRITER_SESSION:-<none>}"

# Stage anything the agent left unstaged
git add "$BLOG_DIR" 2>/dev/null || true
if ! git diff --cached --quiet; then
  git commit -m "chore(blog): auto-stage writer output $TODAY"
fi

# Find the new post added since the last common ancestor with main
MERGE_BASE=$(git merge-base HEAD main 2>/dev/null || git rev-parse HEAD~1 2>/dev/null || echo "")
if [ -n "$MERGE_BASE" ]; then
  NEW_POST=$(git diff --diff-filter=A --name-only "$MERGE_BASE"..HEAD -- "$BLOG_DIR" | head -1 | tr -d '[:space:]')
else
  NEW_POST=$(git diff --diff-filter=A --name-only HEAD~1..HEAD -- "$BLOG_DIR" 2>/dev/null | head -1 | tr -d '[:space:]')
fi

# Fallback: look at all commits on this branch vs main
if [ -z "$NEW_POST" ]; then
  NEW_POST=$(git log --diff-filter=A --name-only --pretty=format: main..HEAD -- "$BLOG_DIR" 2>/dev/null | grep -v '^$' | head -1 | tr -d '[:space:]')
fi

if [ -z "$NEW_POST" ]; then
  log "ERROR: No new blog post detected in $BLOG_DIR after writer phase."
  exit 1
fi

log "New post: $NEW_POST"
NEW_POST_ABS="$REPO_ROOT/$NEW_POST"

# =========================================================================
# Phase 3 -- Sonnet image agent
# =========================================================================
IMAGE_ABS=""

if [ ! -f "$REPO_ROOT/.env.skills" ]; then
  log "WARNING: .env.skills not found. Skipping image generation."
else
  IMAGE_FIELD=$(grep -m1 '^image:' "$NEW_POST_ABS" | sed 's/image:[[:space:]]*//' | tr -d '"'"'" | tr -d '[:space:]')

  if [ -z "$IMAGE_FIELD" ]; then
    log "WARNING: No image field in post frontmatter. Skipping image generation."
  else
    IMAGE_REL="${IMAGE_FIELD#/}"
    IMAGE_ABS="$REPO_ROOT/apps/marketing-site/public/$IMAGE_REL"
    IMAGE_DIR="$(dirname "$IMAGE_ABS")"

    log "Phase 3: Sonnet image agent -> $IMAGE_ABS"

    IMAGE_PROMPT="Read the blog post at $NEW_POST_ABS and the generate-image skill at $REPO_ROOT/.windsurf/workflows/generate-image.md.

Generate a blog-header image for this post:
1. Read the post frontmatter to get the exact title and excerpt.
2. Derive IMAGE_DESCRIPTION from the Visual Metaphor Guide in the skill doc based on the article topic.
3. Create the output directory (Linux bash only): mkdir -p $IMAGE_DIR
4. Write the generation script to $REPO_ROOT/generate-image-temp.mjs. Substitute ALL placeholders -- TITLE, SUBTITLE (excerpt truncated to ~12 words), IMAGE_DESCRIPTION, ASPECT_RATIO (16:9), IMAGE_SIZE (1K), LAYOUT_INSTRUCTIONS (blog-header preset from skill doc), and OUTPUT_PATH ($IMAGE_ABS) -- with actual values. No placeholder text may remain in the script.
5. Run: node --env-file=$REPO_ROOT/.env.skills $REPO_ROOT/generate-image-temp.mjs
6. Remove the temp script: rm $REPO_ROOT/generate-image-temp.mjs
7. Commit: git add $IMAGE_ABS && git commit -m 'feat(blog): add header image $TODAY'

Use Linux bash only. No PowerShell."

    claude -p "$IMAGE_PROMPT" \
      --allowedTools "Read,Write,Bash(mkdir *),Bash(node *),Bash(rm *),Bash(git add *),Bash(git commit *),Bash(git status *),Bash(ls *)" \
      --output-format json > /dev/null || {
      log "WARNING: Image generation failed. Continuing without image."
      IMAGE_ABS=""
    }

    if [ -n "$IMAGE_ABS" ] && [ ! -s "$IMAGE_ABS" ]; then
      log "WARNING: Image file missing or empty after generation. Continuing without image."
      IMAGE_ABS=""
    fi
  fi
fi

# =========================================================================
# Phase 4 + 5 -- Sonnet review, Opus revision loop
# =========================================================================
REVIEW_SCHEMA='{"type":"object","required":["approved","feedback","ascii_violations","fabricated_claims","word_count_ok","source_count_ok"],"properties":{"approved":{"type":"boolean"},"feedback":{"type":"string"},"ascii_violations":{"type":"array","items":{"type":"string"}},"fabricated_claims":{"type":"array","items":{"type":"string"}},"word_count_ok":{"type":"boolean"},"source_count_ok":{"type":"boolean"}}}'

REVIEW_BASE="$(sed "s/CURRENT_DATE/$TODAY/g" "$REVIEW_PROMPT_FILE")"

REVIEW_PROMPT_TEXT="$REVIEW_BASE

Blog post to review: $NEW_POST_ABS"
[ -n "$IMAGE_ABS" ] && REVIEW_PROMPT_TEXT="$REVIEW_PROMPT_TEXT
Header image to check: $IMAGE_ABS"

APPROVED=false
REVISION=0

while true; do
  log "Phase 4/5: Sonnet review (revision=$REVISION)..."

  REVIEW_JSON=$(echo "$REVIEW_PROMPT_TEXT" | claude -p - \
    --allowedTools "Read,Bash(ls *),Bash(wc *)" \
    --output-format json \
    --json-schema "$REVIEW_SCHEMA") || {
    log "WARNING: Review agent failed. Opening draft PR without review verdict."
    break
  }

  REVIEW_DATA=$(echo "$REVIEW_JSON" | jq -r '.structured_output // empty')

  if [ -z "$REVIEW_DATA" ]; then
    log "WARNING: Review returned no structured output. Opening draft PR."
    break
  fi

  APPROVED_VAL=$(echo "$REVIEW_DATA" | jq -r '.approved // false')
  FEEDBACK=$(echo "$REVIEW_DATA" | jq -r '.feedback // ""')
  ASCII_ISSUES=$(echo "$REVIEW_DATA" | jq -r '(.ascii_violations // []) | join("; ")')
  FAKE_CLAIMS=$(echo "$REVIEW_DATA" | jq -r '(.fabricated_claims // []) | join("; ")')

  log "Review verdict: approved=$APPROVED_VAL"
  log "Feedback: $FEEDBACK"
  [ -n "$ASCII_ISSUES" ] && log "ASCII violations: $ASCII_ISSUES"
  [ -n "$FAKE_CLAIMS" ]  && log "Suspicious claims: $FAKE_CLAIMS"

  if [ "$APPROVED_VAL" = "true" ]; then
    APPROVED=true
    log "Post approved by reviewer."
    break
  fi

  if [ -z "$WRITER_SESSION" ] || [ "$REVISION" -ge "$MAX_REVISIONS" ]; then
    log "Max revisions reached or no writer session. Opening draft PR."
    break
  fi

  REVISION=$((REVISION + 1))
  log "Phase 5: Opus revision $REVISION/$MAX_REVISIONS..."

  REVISION_PROMPT="The Encypher editorial reviewer has rejected your draft. Fix all issues listed below.

Reviewer feedback:
$FEEDBACK

ASCII violations to fix (replace each with ASCII equivalent):
${ASCII_ISSUES:-None listed -- re-scan the full text for any character with codepoint above 127}

Unverifiable claims to remove or source:
${FAKE_CLAIMS:-None listed}

Instructions:
1. Open $NEW_POST_ABS and fix every issue listed above.
2. Dash rule: never use -- in prose. Replace every -- with a single hyphen - (with spaces around it). Unicode em-dash must also become -. Quotes must be straight \", apostrophe must be straight ', ellipsis must be ...
3. For any claim flagged as unverifiable: add the real source URL from the original research notes, or remove the claim.
4. Save the file.
5. Run: git add $NEW_POST_ABS && git commit -m 'fix(blog): revision $REVISION -- address review feedback'

Do not change the filename, slug, or frontmatter date."

  claude -p "$REVISION_PROMPT" \
    --resume "$WRITER_SESSION" \
    --allowedTools "Read,Write,Bash(git add *),Bash(git commit *),Bash(git diff *),Bash(git status *)" \
    --output-format json > /dev/null || {
    log "WARNING: Revision pass $REVISION failed. Opening draft PR with current state."
    break
  }
done

# =========================================================================
# Phase 6 -- Push and open PR (skipped in test mode)
# =========================================================================
if [ "$TEST_MODE" = true ]; then
  CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  log "Test mode: all phases complete. Post committed to branch '$CURRENT_BRANCH'."
  log "Approved: $APPROVED"
  log "Post file: $NEW_POST"
  [ -n "$IMAGE_ABS" ] && log "Image file: $IMAGE_ABS"
  log "To review: open $NEW_POST_ABS"
  log "No push or PR created in test mode."
  exit 0
fi

log "Phase 6: Pushing branch and opening PR..."
git push origin "$BRANCH_NAME"

POST_TITLE="$(git log --oneline -1 | sed 's/^[a-f0-9]* //')"

if [ "$APPROVED" = true ]; then
  REVIEW_STATUS="Approved by reviewer"
  DRAFT_FLAG=""
  log "Opening regular PR."
else
  REVIEW_STATUS="Not approved -- human review required before merging"
  DRAFT_FLAG="--draft"
  log "Opening draft PR."
fi

gh pr create \
  --title "Blog: $POST_TITLE" \
  --body "$(cat <<EOF
## Automated Weekly Blog Post

Generated by the blog-writer pipeline on $TODAY.

**Review status:** $REVIEW_STATUS

**Review checklist before merging:**
- [ ] Title and excerpt are accurate and SEO-optimized
- [ ] All cited sources load correctly
- [ ] Encypher positioning is accurate (no patent claim counts or filing dates)
- [ ] No fabricated statistics or quotes
- [ ] Word count is 1,400+
- [ ] Tags are relevant
- [ ] Blog header image looks correct

---
*Generated by \`scripts/agents/blog-writer/run.sh\`*
EOF
)" \
  --base main \
  --head "$BRANCH_NAME" \
  $DRAFT_FLAG

log "Done."
