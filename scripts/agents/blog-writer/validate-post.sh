#!/usr/bin/env bash
# Validates a blog post markdown file against Encypher editorial standards.
# Complements the AI reviewer with fast, deterministic structural checks.
#
# Usage:  validate-post.sh <path-to-post.md>
# Exit 0: all checks pass
# Exit 1: one or more checks fail

set -uo pipefail

FILE="${1:-}"
if [ -z "$FILE" ]; then
  echo "Usage: validate-post.sh <path-to-post.md>" >&2
  exit 1
fi

# Resolve to absolute path
if [[ "$FILE" != /* ]]; then
  FILE="$(pwd)/$FILE"
fi

if [ ! -f "$FILE" ]; then
  echo "ERROR: file not found: $FILE" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FAILED=false

pass() { printf "  PASS  %s\n" "$1"; }
fail() { printf "  FAIL  %s: %s\n" "$1" "$2"; FAILED=true; }

# ---------------------------------------------------------------------------
# Parse frontmatter and body
# ---------------------------------------------------------------------------
# Frontmatter: lines between first and second '---'
# Body: lines after second '---'
FRONTMATTER=$(awk '/^---/{if(++n==2)exit; next} n==1' "$FILE")
BODY=$(awk '/^---/{n++; next} n>=2' "$FILE")

get_field() {
  printf '%s' "$FRONTMATTER" | grep -m1 "^${1}:" | sed "s/^${1}:[[:space:]]*//" | tr -d "\"'"
}

get_field_raw() {
  printf '%s' "$FRONTMATTER" | grep -m1 "^${1}:" | sed "s/^${1}:[[:space:]]*//"
}

TITLE=$(get_field title)
DATE=$(get_field date)
EXCERPT=$(get_field excerpt)
AUTHOR=$(get_field author)
IMAGE=$(get_field image)
TAGS=$(get_field tags)
TAGS_RAW=$(get_field_raw tags)

# ---------------------------------------------------------------------------
printf "\nBlog post validation: %s\n" "$FILE"
printf "%s\n" "========================================"

# 1. Required fields present
for field_name in TITLE DATE EXCERPT AUTHOR IMAGE TAGS; do
  val="${!field_name}"
  if [ -n "$val" ]; then
    pass "frontmatter.$field_name present"
  else
    fail "frontmatter.$field_name present" "missing or empty"
  fi
done

# 2. Title length (55-70 chars per review criteria; allow 40-80 in CI to tolerate edge cases)
if [ -n "$TITLE" ]; then
  LEN=${#TITLE}
  if [ "$LEN" -ge 40 ] && [ "$LEN" -le 80 ]; then
    pass "title length (${LEN} chars)"
  else
    fail "title length (${LEN} chars)" "expected 55-70 chars (review criteria)"
  fi
fi

# 3. Excerpt length (150-180 chars per review criteria; allow 100-220 in CI)
if [ -n "$EXCERPT" ]; then
  LEN=${#EXCERPT}
  if [ "$LEN" -ge 100 ] && [ "$LEN" -le 220 ]; then
    pass "excerpt length (${LEN} chars)"
  else
    fail "excerpt length (${LEN} chars)" "expected 150-180 chars (review criteria)"
  fi
fi

# 4. Date format YYYY-MM-DD
if [ -n "$DATE" ]; then
  if printf '%s' "$DATE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
    pass "date format ($DATE)"
  else
    fail "date format" "expected YYYY-MM-DD, got: $DATE"
  fi
fi

# 5. Image file exists and is non-empty
# (body may have watermark chars from signing; image path is frontmatter)
if [ -n "$IMAGE" ]; then
  IMAGE_PATH="$REPO_ROOT/apps/marketing-site/public${IMAGE}"
  if [ -s "$IMAGE_PATH" ]; then
    pass "image file exists"
  else
    fail "image file exists" "not found or empty: $IMAGE_PATH"
  fi
fi

# 6. Tag count >= 2
# Tags are in ["tag1","tag2",...] format; use raw value (with quotes) for counting
if [ -n "$TAGS_RAW" ]; then
  TAG_COUNT=$(printf '%s' "$TAGS_RAW" | grep -o '"[^"]*"' | wc -l | tr -d ' ')
  if [ "$TAG_COUNT" -ge 2 ]; then
    pass "tag count ($TAG_COUNT tags)"
  else
    fail "tag count ($TAG_COUNT tags)" "need at least 2 tags"
  fi
fi

# 7. Word count >= 1400
# Strip non-ASCII chars before counting to ignore Encypher watermark characters
# that are embedded in body text by the signing step.
WORD_COUNT=$(printf '%s' "$BODY" | tr -cd '[:alpha:] \n\t' | wc -w | tr -d ' ')
if [ "$WORD_COUNT" -ge 1400 ]; then
  pass "word count (~$WORD_COUNT words)"
else
  fail "word count (~$WORD_COUNT words)" "body needs >= 1400 words"
fi

# 8. Link count >= 3
LINK_COUNT=$(printf '%s' "$BODY" | grep -oE '\]\(https?://' | wc -l | tr -d ' ')
if [ "$LINK_COUNT" -ge 3 ]; then
  pass "link count ($LINK_COUNT links)"
else
  fail "link count ($LINK_COUNT links)" "need at least 3 linked sources"
fi

# 9. No double-dash (--) used as a dash in prose
# Strip fenced code blocks first to avoid flagging shell command examples.
PROSE=$(printf '%s' "$BODY" | awk '/^```/{in_block=!in_block; next} !in_block')
if printf '%s' "$PROSE" | grep -q ' -- \|^-- \| --$'; then
  EXAMPLES=$(printf '%s' "$PROSE" | grep -n ' -- \|^-- \| --$' | head -3 | sed 's/^/    /')
  fail "no double-dash (--) in prose" $'\n'"$EXAMPLES"
else
  pass "no double-dash (--) in prose"
fi

# 10. Frontmatter is ASCII-only
# (body intentionally contains Encypher watermark chars after signing)
NON_ASCII=$(printf '%s' "$FRONTMATTER" | LC_ALL=C grep -Pn '[^\x00-\x7F]' || true)
if [ -z "$NON_ASCII" ]; then
  pass "frontmatter ASCII-only"
else
  fail "frontmatter ASCII-only" $'\n'"$(printf '%s' "$NON_ASCII" | head -3 | sed 's/^/    /')"
fi

# ---------------------------------------------------------------------------
printf "%s\n" "========================================"
if [ "$FAILED" = true ]; then
  printf "VALIDATION FAILED\n\n"
  exit 1
else
  printf "VALIDATION PASSED\n\n"
  exit 0
fi
