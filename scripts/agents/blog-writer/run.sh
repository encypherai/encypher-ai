#!/usr/bin/env bash
# Encypher Automated Blog Writer
#
# Pipeline:
#   Phase 1   Sonnet research:  selects topic, formulates thesis, gathers verified sources
#   Phase 2   Opus writer:      reads research notes, writes post, commits markdown
#   Phase 3   Sonnet image:     generates blog header image via Gemini API at 2K resolution
#   Phase 4   Sonnet review:    structured approval covering post quality + visual image check
#   Phase 3b  Sonnet regen:     regenerates image if review flags visual issues (up to MAX_IMAGE_REGEN)
#   Phase 5   Opus revision:    revises post if review flags content issues (up to MAX_REVISIONS)
#   Phase 6   Push + PR:        regular PR if approved, draft PR if not (skipped in --test mode)
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
MAX_IMAGE_REGEN=2

log() { echo "[$(date -u +%H:%M:%S)] $*"; }

# Allow claude -p subprocesses when invoked from inside a Claude Code session
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
# Gitignored and deleted on exit.
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
# Phase 3 -- Sonnet image agent (function, called for initial gen + regen)
# =========================================================================
IMAGE_ABS=""
IMAGE_REGEN=0

generate_image() {
  local feedback="${1:-}"   # optional: feedback from reviewer for regen pass

  if [ ! -f "$REPO_ROOT/.env.skills" ]; then
    log "WARNING: .env.skills not found. Skipping image generation."
    return 0
  fi

  local image_field
  image_field=$(grep -m1 '^image:' "$NEW_POST_ABS" | sed 's/image:[[:space:]]*//' | tr -d '"'"'" | tr -d '[:space:]')

  if [ -z "$image_field" ]; then
    log "WARNING: No image field in post frontmatter. Skipping image generation."
    return 0
  fi

  local image_rel="${image_field#/}"
  IMAGE_ABS="$REPO_ROOT/apps/marketing-site/public/$image_rel"
  local image_dir
  image_dir="$(dirname "$IMAGE_ABS")"

  # Derive a short display title (text before first colon, max 40 chars)
  local full_title
  full_title=$(grep -m1 '^title:' "$NEW_POST_ABS" | sed 's/title:[[:space:]]*//' | tr -d '"')
  local short_title
  short_title=$(echo "$full_title" | cut -d: -f1 | cut -c1-40)

  log "Phase 3: Sonnet image agent -> $IMAGE_ABS (title: '$short_title')"

  local regen_note=""
  if [ -n "$feedback" ]; then
    regen_note="

IMPORTANT: The previous image was rejected. Here is the reviewer's feedback:
$feedback

Fix every issue described above. Pay special attention to the title text."
  fi

  local image_prompt="Read the blog post at $NEW_POST_ABS and the generate-image skill at $REPO_ROOT/.windsurf/workflows/generate-image.md.

Generate a blog-header image for this post:
1. Read the post frontmatter to get the excerpt (use as subtitle, truncated to ~12 words).
2. Use this SHORT display title in the image (not the full article title):
   \"$short_title\"
   This shorter title prevents text rendering errors. Do not use the full article title.
3. Derive IMAGE_DESCRIPTION from the Visual Metaphor Guide in the skill doc based on the article topic.
4. Create the output directory (Linux bash only): mkdir -p $image_dir
5. Write the generation script to $REPO_ROOT/generate-image-temp.mjs. Substitute ALL placeholders:
   - TITLE: \"$short_title\" (the short title above, not the full title)
   - SUBTITLE: excerpt truncated to ~12 words
   - IMAGE_DESCRIPTION: from the Visual Metaphor Guide
   - ASPECT_RATIO: 16:9
   - IMAGE_SIZE: 2K
   - LAYOUT_INSTRUCTIONS: blog-header preset from the skill doc
   - OUTPUT_PATH: $IMAGE_ABS
   No placeholder text may remain in the script.
6. Run: node --env-file=$REPO_ROOT/.env.skills $REPO_ROOT/generate-image-temp.mjs
7. Remove the temp script: rm $REPO_ROOT/generate-image-temp.mjs
8. Commit: git add $IMAGE_ABS && git commit -m 'feat(blog): add header image $TODAY'

Use Linux bash only. No PowerShell.$regen_note"

  claude -p "$image_prompt" \
    --allowedTools "Read,Write,Bash(mkdir *),Bash(node *),Bash(rm *),Bash(git add *),Bash(git commit *),Bash(git status *),Bash(ls *)" \
    --output-format json > /dev/null || {
    log "WARNING: Image generation failed. Continuing without image."
    IMAGE_ABS=""
    return 0
  }

  if [ -n "$IMAGE_ABS" ] && [ ! -s "$IMAGE_ABS" ]; then
    log "WARNING: Image file missing or empty after generation."
    IMAGE_ABS=""
  fi
}

generate_image ""

# =========================================================================
# Phase 4 + 3b + 5 -- Sonnet review, image regen, Opus revision loop
# =========================================================================
REVIEW_SCHEMA='{"type":"object","required":["approved","image_ok","feedback","image_feedback","ascii_violations","fabricated_claims","word_count_ok","source_count_ok"],"properties":{"approved":{"type":"boolean"},"image_ok":{"type":"boolean"},"feedback":{"type":"string"},"image_feedback":{"type":"string"},"ascii_violations":{"type":"array","items":{"type":"string"}},"fabricated_claims":{"type":"array","items":{"type":"string"}},"word_count_ok":{"type":"boolean"},"source_count_ok":{"type":"boolean"}}}'

REVIEW_BASE="$(sed "s/CURRENT_DATE/$TODAY/g" "$REVIEW_PROMPT_FILE")"

build_review_prompt() {
  local prompt="$REVIEW_BASE

Blog post to review: $NEW_POST_ABS"
  [ -n "$IMAGE_ABS" ] && prompt="$prompt
Header image to review (use the Read tool to open and visually inspect it): $IMAGE_ABS"
  echo "$prompt"
}

APPROVED=false
REVISION=0

while true; do
  log "Phase 4: Sonnet review (revision=$REVISION, image_regen=$IMAGE_REGEN)..."

  REVIEW_JSON=$(build_review_prompt | claude -p - \
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
  IMAGE_OK=$(echo "$REVIEW_DATA" | jq -r '.image_ok // true')
  FEEDBACK=$(echo "$REVIEW_DATA" | jq -r '.feedback // ""')
  IMAGE_FEEDBACK=$(echo "$REVIEW_DATA" | jq -r '.image_feedback // ""')
  ASCII_ISSUES=$(echo "$REVIEW_DATA" | jq -r '(.ascii_violations // []) | join("; ")')
  FAKE_CLAIMS=$(echo "$REVIEW_DATA" | jq -r '(.fabricated_claims // []) | join("; ")')

  log "Review: approved=$APPROVED_VAL  image_ok=$IMAGE_OK"
  log "Post feedback: $FEEDBACK"
  [ "$IMAGE_OK" != "true" ] && log "Image feedback: $IMAGE_FEEDBACK"
  [ -n "$ASCII_ISSUES" ] && log "ASCII violations: $ASCII_ISSUES"
  [ -n "$FAKE_CLAIMS" ]  && log "Suspicious claims: $FAKE_CLAIMS"

  if [ "$APPROVED_VAL" = "true" ]; then
    APPROVED=true
    log "Approved."
    break
  fi

  # Phase 3b: regenerate image if reviewer flagged it
  if [ "$IMAGE_OK" = "false" ] && [ -n "$IMAGE_ABS" ] && [ "$IMAGE_REGEN" -lt "$MAX_IMAGE_REGEN" ]; then
    IMAGE_REGEN=$((IMAGE_REGEN + 1))
    log "Phase 3b: Image regeneration $IMAGE_REGEN/$MAX_IMAGE_REGEN..."
    generate_image "$IMAGE_FEEDBACK"
  fi

  # Phase 5: revise post if writer session available and content issues remain
  if [ -z "$WRITER_SESSION" ] || [ "$REVISION" -ge "$MAX_REVISIONS" ]; then
    log "Max revisions reached or no writer session. Opening draft PR."
    break
  fi

  # Only do a writer revision if the post itself has issues (not just the image)
  POST_ONLY_FEEDBACK=$(echo "$FEEDBACK" | grep -v -i "image" || true)
  if [ -z "$POST_ONLY_FEEDBACK" ] && [ "$IMAGE_OK" = "false" ]; then
    # Only image issues; if regen is also maxed, give up
    if [ "$IMAGE_REGEN" -ge "$MAX_IMAGE_REGEN" ]; then
      log "Only image issues remain and max regen reached. Opening draft PR."
      break
    fi
    # Otherwise loop back and re-review after regen
    continue
  fi

  REVISION=$((REVISION + 1))
  log "Phase 5: Opus revision $REVISION/$MAX_REVISIONS..."

  REVISION_PROMPT="The Encypher editorial reviewer has rejected your draft. Fix all issues listed below.

Reviewer feedback:
$FEEDBACK

Dash rule: Never use -- in prose. Replace every double-hyphen with a single hyphen - with spaces around it.
ASCII violations to fix: ${ASCII_ISSUES:-None listed - but re-scan for any codepoint above 127}
Unverifiable claims to remove or source: ${FAKE_CLAIMS:-None listed}

Instructions:
1. Open $NEW_POST_ABS and fix every issue listed above.
2. If the content provenance connection is missing or weak, add a substantive section explaining
   how C2PA content authentication addresses the problem described in the post.
3. Save the file.
4. Run: git add $NEW_POST_ABS && git commit -m 'fix(blog): revision $REVISION - address review feedback'

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
  log "Test mode complete on branch '$CURRENT_BRANCH'."
  log "  approved=$APPROVED"
  log "  post:  $NEW_POST"
  [ -n "$IMAGE_ABS" ] && log "  image: $IMAGE_ABS"
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
  REVIEW_STATUS="Not approved - human review required before merging"
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
- [ ] Content provenance connection is substantive

---
*Generated by \`scripts/agents/blog-writer/run.sh\`*
EOF
)" \
  --base main \
  --head "$BRANCH_NAME" \
  $DRAFT_FLAG

log "Done."
