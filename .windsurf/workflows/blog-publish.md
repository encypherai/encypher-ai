---
description: End-to-end blog post publication workflow. Follow ALL steps in order — no step may be skipped or reordered. This is the canonical sequence for every blog post.
---

# Blog Post Publication Workflow

**Every blog post must follow this exact sequence before being committed and pushed.**

---

## Step 1 — Research

Run the research phase first. No writing begins until research is complete.

```bash
# Agent auto-selects highest-priority topic from TOPICS.md
./scripts/agents/blog-writer/run.sh

# Or specify a topic explicitly
./scripts/agents/blog-writer/run.sh "your topic here"
```

The agent uses `RESEARCH_PROMPT.md` to gather current statistics, sources, legal citations, and news hooks. Research output is saved to `scripts/agents/blog-writer/research/`.

**Do not proceed to Step 2 until research is committed.**

---

## Step 2 — First Draft

The agent writes the draft using `AGENT_PROMPT.md` against the research output. The draft is committed to a `blog/auto-YYYY-MM-DD` branch and a **draft PR** is opened automatically.

Requirements:
- 1,400–2,200 words
- Frontmatter complete: `title`, `date`, `excerpt`, `author`, `image`, `tags`
- `image` field set to the correct output path (even though the file doesn't exist yet — it will be generated in Step 3)
- Voice and format match existing posts

**Do not proceed to Step 3 until the draft markdown file is saved.**

---

## Step 3 — Review & Approval

A human reviewer reads the draft PR and approves or requests changes.

- Reviewer checks: accuracy, voice, sourcing, frontmatter, word count
- If changes are requested: agent revises and re-commits to the same branch
- **The post is NOT published until the reviewer explicitly approves**

**Do not proceed to Step 4 until the reviewer has approved the draft.**

---

## Step 4 — Generate Header Image

Generate the blog header image using the Gemini image generation workflow **after approval, before final commit**.

```bash
# See .windsurf/workflows/generate-image.md for full instructions
node --env-file=.env.skills generate-image-temp.mjs
```

Requirements:
- Output path must match the `image` field in the post frontmatter exactly
- Image must be verified to exist on disk before proceeding
- Use the `blog-header` preset (16:9, 1K)
- Derive scene from post title and excerpt using the Visual Metaphor Guide in `generate-image.md`

> **RULE: The image file must exist on disk before the blog post is committed.**

---

## Step 5 — Sign Content with Live Key

Sign the blog post markdown with the live Encypher API to embed provenance markers.

```bash
uv run python enterprise_api/scripts/sign_blog_posts.py \
  --glob 'apps/marketing-site/src/content/blog/YOUR_POST.md' \
  --env-file .env.skills
```

Requirements:
- `.env.skills` must contain a valid `ENYCPHER_API_KEY` and `ENCYPHER_BASE_URL=api.encypherai.com`
- Signing must complete with exit code 0 and "Done. Signed 1 posts."
- Report written to `enterprise_api/output/signed_blog_posts/signing_report.json`

> **RULE: Signing must happen after the final approved content is written, and before committing.**

---

## Step 6 — Commit & Push

Stage and commit the image and signed post together, then push.

```bash
git add apps/marketing-site/public/images/blog/YOUR_IMAGE.png
git add apps/marketing-site/src/content/blog/YOUR_POST.md
git commit -m "feat(blog): <post title>"
git push origin blog/auto-YYYY-MM-DD
```

---

## Step 7 — Merge PR

Once the branch is pushed with image + signed content, mark the draft PR as ready for review and merge.

---

## Summary Checklist

Before pushing, verify every item:

- [ ] Research committed to branch
- [ ] Draft written and reviewed/approved by human
- [ ] Header image generated and file exists on disk
- [ ] Image path matches `image` field in frontmatter exactly
- [ ] Content signed with live Encypher API key (exit 0)
- [ ] Both image and signed `.md` staged in same commit
- [ ] Branch pushed to remote
