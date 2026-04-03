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
REPO_ROOT_ORIG="$REPO_ROOT"  # preserved for accessing research archives from worktree
BLOG_DIR="apps/marketing-site/src/content/blog"
RESEARCH_PROMPT_FILE="$REPO_ROOT/scripts/agents/blog-writer/RESEARCH_PROMPT.md"
AGENT_PROMPT_FILE="$REPO_ROOT/scripts/agents/blog-writer/AGENT_PROMPT.md"
REVIEW_PROMPT_FILE="$REPO_ROOT/scripts/agents/blog-writer/REVIEW_PROMPT.md"
TRENDS_PROMPT_FILE="$REPO_ROOT/scripts/agents/blog-writer/TRENDS_PROMPT.md"
BRANCH_PREFIX="blog/auto"
TODAY="${TODAY:-$(date +%Y-%m-%d)}"
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

# Embed GH_TOKEN in remote URL for local runs (GHA handles auth automatically via GITHUB_TOKEN)
CLEAN_GIT_URL=$(git remote get-url origin)
if [ -n "${GH_TOKEN:-}" ] && [[ "$CLEAN_GIT_URL" != *"@"* ]]; then
  AUTH_GIT_URL="${CLEAN_GIT_URL/https:\/\//https://x-access-token:${GH_TOKEN}@}"
  git remote set-url origin "$AUTH_GIT_URL"
fi

# Clean up stale local blog branches from previous runs
git branch --list 'blog/auto-*' | xargs -r git branch -D 2>/dev/null || true
# Prune worktrees left behind by crashed runs
git worktree prune 2>/dev/null || true

WORKTREE_DIR="$REPO_ROOT/.blog-worktree"

cleanup_worktree() {
  cd "$REPO_ROOT"
  if [ -d "$WORKTREE_DIR" ]; then
    git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || rm -rf "$WORKTREE_DIR"
    git worktree prune 2>/dev/null || true
  fi
  git branch -D "$BRANCH_NAME" 2>/dev/null || true
  # Restore original remote URL if we changed it
  if [ -n "${CLEAN_GIT_URL:-}" ]; then
    git remote set-url origin "$CLEAN_GIT_URL" 2>/dev/null || true
  fi
}

if [ "$TEST_MODE" = false ]; then
  log "Ensuring main is up to date..."
  git -C "$REPO_ROOT" checkout main 2>/dev/null || true
  git -C "$REPO_ROOT" pull origin main

  if git ls-remote --exit-code --heads origin "$BRANCH_NAME" &>/dev/null; then
    log "Branch $BRANCH_NAME already exists on remote. Skipping."
    exit 0
  fi

  # Create an isolated worktree for the blog work
  rm -rf "$WORKTREE_DIR"
  git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" main
  trap cleanup_worktree EXIT
  cd "$WORKTREE_DIR"
  # Update REPO_ROOT to point to the worktree for all subsequent phases
  REPO_ROOT="$WORKTREE_DIR"
  log "Created worktree: $WORKTREE_DIR (branch: $BRANCH_NAME)"
else
  log "Test mode: running on branch $(git rev-parse --abbrev-ref HEAD)"
fi

RESEARCH_NOTES="$REPO_ROOT/.blog-research-temp.md"
RESEARCH_ARCHIVE_DIR="$REPO_ROOT/scripts/agents/blog-writer/research"
# Research temp file cleanup is handled by cleanup_worktree (worktree removal
# deletes it) or naturally in test mode. No separate trap needed.

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

TOPIC_SLUG=$(grep -m1 '^## Topic' -A1 "$RESEARCH_NOTES" | tail -1 | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-\|-$//g')
log "Research notes saved. Topic: $TOPIC_SLUG"

# Archive research notes for longitudinal tracking
mkdir -p "$RESEARCH_ARCHIVE_DIR"
RESEARCH_ARCHIVE="$RESEARCH_ARCHIVE_DIR/$TODAY-${TOPIC_SLUG:-research}.md"
cp "$RESEARCH_NOTES" "$RESEARCH_ARCHIVE"
git add "$RESEARCH_ARCHIVE"
git commit -m "research($TODAY): $TOPIC_SLUG" || true
log "Research archived: $RESEARCH_ARCHIVE"

# =========================================================================
# Phase 1.5 -- Trend analysis (includes this week's research)
# =========================================================================
# Trends file lives in the original repo's research dir (persists across worktrees)
TRENDS_FILE="$REPO_ROOT_ORIG/scripts/agents/blog-writer/research/trends.md"
RESEARCH_ARCHIVE_FOR_TRENDS="$REPO_ROOT_ORIG/scripts/agents/blog-writer/research"

# In worktree mode, this week's archive was written to $REPO_ROOT (the worktree).
# Copy it to the original research dir so the trend agent can see all weeks together.
if [ "$TEST_MODE" = false ] && [ "$REPO_ROOT" != "$REPO_ROOT_ORIG" ]; then
  cp "$RESEARCH_ARCHIVE" "$RESEARCH_ARCHIVE_FOR_TRENDS/" 2>/dev/null || true
fi

ARCHIVE_COUNT=$(find "$RESEARCH_ARCHIVE_FOR_TRENDS" -maxdepth 1 -name '20*.md' 2>/dev/null | wc -l)
if [ "$ARCHIVE_COUNT" -ge 2 ]; then
  log "Phase 1.5: Updating trend tracker ($ARCHIVE_COUNT research weeks archived)..."

  TRENDS_PROMPT="$(sed \
    -e "s|CURRENT_DATE|$TODAY|g" \
    -e "s|RESEARCH_ARCHIVE_DIR|$RESEARCH_ARCHIVE_FOR_TRENDS|g" \
    -e "s|TRENDS_FILE|$TRENDS_FILE|g" \
    "$TRENDS_PROMPT_FILE")"

  claude -p "$TRENDS_PROMPT" \
    --allowedTools "Read,Glob,Write,Bash(ls *)" \
    --output-format json > /dev/null || {
    log "WARNING: Trend analysis failed. Continuing without update."
  }

  if [ -f "$TRENDS_FILE" ]; then
    # Copy into worktree for committing on the blog branch
    if [ "$REPO_ROOT" != "$REPO_ROOT_ORIG" ]; then
      mkdir -p "$REPO_ROOT/scripts/agents/blog-writer/research"
      cp "$TRENDS_FILE" "$REPO_ROOT/scripts/agents/blog-writer/research/trends.md"
    fi
    git add scripts/agents/blog-writer/research/trends.md
    git commit -m "research($TODAY): update industry trend tracker" || true
    log "Trend tracker updated."
  fi
else
  log "Phase 1.5: Skipping trend analysis (need 2+ archived weeks, have $ARCHIVE_COUNT)"
fi

# =========================================================================
# Phase 2 -- Opus writer
# =========================================================================
log "Phase 2: Opus writer agent..."

# Snapshot HEAD before the writer runs so we can find exactly what it adds
PRE_WRITER_COMMIT=$(git rev-parse HEAD)

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

# Find exactly what the writer added (diff from the snapshot we took before it ran)
NEW_POST=$(git diff --diff-filter=A --name-only "$PRE_WRITER_COMMIT"..HEAD -- "$BLOG_DIR" | tail -1 | tr -d '[:space:]')

if [ -z "$NEW_POST" ]; then
  log "ERROR: No new blog post detected in $BLOG_DIR after writer phase."
  exit 1
fi

log "New post: $NEW_POST"
NEW_POST_ABS="$REPO_ROOT/$NEW_POST"

# =========================================================================
# Phase 3 -- Image generation (function, called for initial gen + regen)
# =========================================================================
# Architecture: Sonnet derives SUBTITLE + IMAGE_DESCRIPTION (creative work).
# Bash does mechanical substitution on a template and runs the Gemini API call.
# This ensures the full Protocol Modernism system prompt is always byte-for-byte
# correct - no AI transcription of the 100+ line prompt.
IMAGE_ABS=""
IMAGE_REGEN=0
IMAGE_TEMPLATE="$REPO_ROOT/scripts/agents/blog-writer/generate-image-template.mjs"

generate_image() {
  local feedback="${1:-}"   # optional: feedback from reviewer for regen pass

  if [ ! -f "$REPO_ROOT/.env.skills" ]; then
    log "WARNING: .env.skills not found. Skipping image generation."
    return 0
  fi

  if [ ! -f "$IMAGE_TEMPLATE" ]; then
    log "WARNING: Image template not found at $IMAGE_TEMPLATE. Skipping."
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

  # Use the full post title as the image display title.
  local full_title
  full_title=$(grep -m1 '^title:' "$NEW_POST_ABS" | sed 's/title:[[:space:]]*//' | tr -d '"')

  log "Phase 3: generating image -> $IMAGE_ABS (title: '$full_title')"

  # --- Step 1: Sonnet derives SUBTITLE and IMAGE_DESCRIPTION only ---
  local regen_note=""
  if [ -n "$feedback" ]; then
    regen_note="

IMPORTANT: The previous image was rejected by the reviewer. Incorporate this feedback into your IMAGE_DESCRIPTION:
$feedback"
  fi

  local DESCRIBE_SCHEMA='{"type":"object","required":["subtitle","image_description"],"properties":{"subtitle":{"type":"string","description":"Blog excerpt truncated to 10-12 words, suitable as image subtitle"},"image_description":{"type":"string","description":"Detailed scene description for Gemini image generation, following the Visual Metaphor Guide"}}}'

  local describe_prompt="Read the blog post at $NEW_POST_ABS and the Visual Metaphor Guide in $REPO_ROOT/.windsurf/workflows/generate-image.md (the table under '## Visual Metaphor Guide' and the '## Proven Style' section).

Return a JSON object with two fields:
1. subtitle: The blog excerpt from frontmatter, truncated to ~10-12 words. Must be a complete thought.
2. image_description: A detailed scene description for a blog header image. Follow these rules:
   - Match the article topic to the Visual Metaphor Guide table to select the right scene type.
   - Prefer the Proven Style (2-3 stage left-to-right pipeline) for any article with a process or mechanism.
   - Describe specific labeled nodes, arrows, badges, and monospace labels - not abstract concepts.
   - Use Muted Coral (#E07A5F) badges for problem/failure states, Cyber Teal (#00CED1) for verified states.
   - Keep to 3-5 visual elements maximum with generous spacing.
   - The description must be specific to THIS article's thesis, not a generic tech image.
   - Do NOT include any text styling instructions (font names, colors, sizes) - those are handled by the template.
$regen_note

Return ONLY the JSON object, no other text."

  local describe_json
  describe_json=$(claude -p "$describe_prompt" \
    --allowedTools "Read" \
    --output-format json \
    --json-schema "$DESCRIBE_SCHEMA") || {
    log "WARNING: Image description agent failed. Skipping image generation."
    IMAGE_ABS=""
    return 0
  }

  local describe_data
  describe_data=$(echo "$describe_json" | jq -r '.structured_output // empty')
  if [ -z "$describe_data" ]; then
    log "WARNING: No structured output from describe agent. Skipping image generation."
    IMAGE_ABS=""
    return 0
  fi

  local subtitle
  subtitle=$(echo "$describe_data" | jq -r '.subtitle // ""')
  local image_description
  image_description=$(echo "$describe_data" | jq -r '.image_description // ""')

  if [ -z "$subtitle" ] || [ -z "$image_description" ]; then
    log "WARNING: Missing subtitle or image_description from agent. Skipping."
    IMAGE_ABS=""
    return 0
  fi

  log "  Subtitle: $subtitle"
  log "  Image description: ${image_description:0:120}..."

  # --- Step 2: Bash substitutes template and runs Gemini ---
  mkdir -p "$image_dir"

  # Use awk for substitution to avoid sed delimiter issues with special chars
  awk -v title="$full_title" \
      -v subtitle="$subtitle" \
      -v desc="$image_description" \
      -v outpath="$IMAGE_ABS" \
    '{
      gsub(/__TITLE__/, title)
      gsub(/__SUBTITLE__/, subtitle)
      gsub(/__IMAGE_DESCRIPTION__/, desc)
      gsub(/__OUTPUT_PATH__/, outpath)
      print
    }' "$IMAGE_TEMPLATE" > "$REPO_ROOT/generate-image-temp.mjs"

  node --env-file="$REPO_ROOT/.env.skills" "$REPO_ROOT/generate-image-temp.mjs" || {
    log "WARNING: Gemini image generation failed. Continuing without image."
    rm -f "$REPO_ROOT/generate-image-temp.mjs"
    IMAGE_ABS=""
    return 0
  }

  rm -f "$REPO_ROOT/generate-image-temp.mjs"

  if [ -n "$IMAGE_ABS" ] && [ ! -s "$IMAGE_ABS" ]; then
    log "WARNING: Image file missing or empty after generation."
    IMAGE_ABS=""
    return 0
  fi

  # --- Step 3: Commit the image ---
  git add "$IMAGE_ABS" && git commit -m "feat(blog): add header image $TODAY"
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

  # Check whether the post content itself has issues (separate from image)
  POST_WORD_OK=$(echo "$REVIEW_DATA" | jq -r '.word_count_ok // true')
  POST_SRC_OK=$(echo "$REVIEW_DATA" | jq -r '.source_count_ok // true')
  POST_ASCII_COUNT=$(echo "$REVIEW_DATA" | jq -r '(.ascii_violations // []) | length')
  POST_FAKE_COUNT=$(echo "$REVIEW_DATA" | jq -r '(.fabricated_claims // []) | length')
  POST_HAS_ISSUES=false
  { [ "$POST_WORD_OK" = "false" ] || [ "$POST_SRC_OK" = "false" ] || \
    [ "$POST_ASCII_COUNT" -gt 0 ] || [ "$POST_FAKE_COUNT" -gt 0 ]; } && POST_HAS_ISSUES=true
  # Also treat feedback mentioning thought-leadership or provenance failures as a post issue
  echo "$FEEDBACK" | grep -qi "criterion 1\|criterion 7\|thought-leadership\|provenance" && POST_HAS_ISSUES=true

  # If only the image failed, skip Opus revision and just loop back for re-review
  if [ "$POST_HAS_ISSUES" = "false" ]; then
    if [ "$IMAGE_REGEN" -ge "$MAX_IMAGE_REGEN" ]; then
      log "Only image issues remain and max regen reached. Opening draft PR."
      break
    fi
    log "Post content is fine; only image issues. Skipping Opus revision, re-reviewing after regen."
    continue
  fi

  # Phase 5: revise post content
  if [ -z "$WRITER_SESSION" ] || [ "$REVISION" -ge "$MAX_REVISIONS" ]; then
    log "Max revisions reached or no writer session. Opening draft PR."
    break
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
# Phase 5.5 -- Sign final post with Encypher (micro + ECC, no C2PA embed)
# =========================================================================
log "Phase 5.5: Signing post with Encypher provenance markers..."

ENCYPHER_API_KEY="${ENCYPHER_API_KEY:-${ENYCPHER_API_KEY:-}}"
if [ -z "$ENCYPHER_API_KEY" ]; then
  log "WARNING: ENCYPHER_API_KEY not set - skipping signing."
else
  cd "$REPO_ROOT_ORIG"
  if uv run python enterprise_api/scripts/sign_blog_posts.py \
      "$NEW_POST_ABS" \
      --api-key "$ENCYPHER_API_KEY" \
      --manifest-mode micro \
      --output-dir "$REPO_ROOT/enterprise_api/output/signed_blog_posts"; then
    git add "$NEW_POST_ABS"
    if ! git diff --cached --quiet; then
      git commit -m "feat(blog): sign post with Encypher provenance markers $TODAY"
    fi
    log "Post signed and committed."
  else
    log "WARNING: Signing failed - continuing with unsigned post."
  fi
fi

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

# Run structural validation before push. Failures force a draft PR so a human
# can review rather than blocking the push entirely.
VALIDATE_SCRIPT="$REPO_ROOT/scripts/agents/blog-writer/validate-post.sh"
if bash "$VALIDATE_SCRIPT" "$NEW_POST_ABS"; then
  log "Post validation passed."
else
  log "WARNING: Post validation failed. Forcing draft PR for human review."
  APPROVED=false
fi

# Clean .next caches so the pre-push build hook doesn't hit permission errors
(sudo rm -rf "$REPO_ROOT/apps/marketing-site/.next" || rm -rf "$REPO_ROOT/apps/marketing-site/.next") 2>/dev/null

# Symlink node_modules and .venv into the worktree so pre-push hooks
# (Next.js builds, ruff, pytest) can find dependencies without a full install
if [ "$REPO_ROOT" != "$REPO_ROOT_ORIG" ]; then
  for app in marketing-site dashboard ap-demo; do
    if [ -d "$REPO_ROOT_ORIG/apps/$app/node_modules" ] && [ ! -d "$REPO_ROOT/apps/$app/node_modules" ]; then
      ln -sfn "$REPO_ROOT_ORIG/apps/$app/node_modules" "$REPO_ROOT/apps/$app/node_modules"
    fi
  done
  if [ -d "$REPO_ROOT_ORIG/.venv" ] && [ ! -d "$REPO_ROOT/.venv" ]; then
    ln -sfn "$REPO_ROOT_ORIG/.venv" "$REPO_ROOT/.venv"
  fi
  if [ -d "$REPO_ROOT_ORIG/node_modules" ] && [ ! -d "$REPO_ROOT/node_modules" ]; then
    ln -sfn "$REPO_ROOT_ORIG/node_modules" "$REPO_ROOT/node_modules"
  fi
fi

git push origin "$BRANCH_NAME"

POST_TITLE="$(grep -m1 '^title:' "$NEW_POST_ABS" | sed 's/title:[[:space:]]*//' | tr -d '"')"
POST_EXCERPT="$(grep -m1 '^excerpt:' "$NEW_POST_ABS" | sed 's/excerpt:[[:space:]]*//' | tr -d '"')"
SQUASH_SUBJECT="blog: ${POST_TITLE:-$(git log --oneline -1 | sed 's/^[a-f0-9]* //')}"

if [ "$APPROVED" = true ]; then
  REVIEW_STATUS="Approved by reviewer"
  DRAFT_FLAG=""
  log "Opening regular PR."
else
  REVIEW_STATUS="Not approved - human review required before merging"
  DRAFT_FLAG="--draft"
  log "Opening draft PR."
fi

PR_URL=$(gh pr create \
  --title "$SQUASH_SUBJECT" \
  --body "$(cat <<EOF
## Automated Weekly Blog Post

**Review status:** $REVIEW_STATUS

> **Merge with squash.** The PR title is the commit message:
> \`$SQUASH_SUBJECT\`
>
> Commit body: $POST_EXCERPT

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
*Generated by \`scripts/agents/blog-writer/run.sh\` on $TODAY*
EOF
)" \
  --base main \
  --head "$BRANCH_NAME" \
  $DRAFT_FLAG)

log "PR: $PR_URL"

if [ "$APPROVED" = true ]; then
  # Auto-merge once CI checks pass, then delete remote branch
  gh pr merge "$PR_URL" --squash --auto --delete-branch
  log "Auto-merge enabled: will squash-merge when checks pass and delete remote branch."
else
  # Signal the workflow notify step to email the reviewer
  if [ -n "${GITHUB_OUTPUT:-}" ]; then
    echo "draft_pr_url=$PR_URL" >> "$GITHUB_OUTPUT"
  fi
fi

# Worktree and local branch cleanup happens automatically via EXIT trap
log "Done. Main worktree remains on main branch."
