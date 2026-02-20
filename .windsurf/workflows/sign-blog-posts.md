---
description: Sign one or more blog markdown posts in publish-date order using micro mode with ECC and embedded C2PA via Enterprise API.
---

## Prerequisites
- `.env.skills` exists at repo root.
- `.env.skills` defines:
  - `ENYCPHER_API_KEY=...` (preferred variable name for this workflow)
  - `ENCYPHER_BASE_URL=api.encypherai.com`
- Python dependencies are synced (`uv sync --all-packages`).

---

## How to invoke this skill

Tell Cascade:
> "Sign blog posts using /sign-blog-posts for [file, folder, or glob]."

Examples:
- "Sign one blog file: `apps/marketing-site/src/content/blog/My_Post.md`"
- "Sign all blog posts in `apps/marketing-site/src/content/blog`"
- "Sign posts between 2026-01-01 and 2026-02-15"

---

## Steps

1. Ensure credentials exist in `.env.skills`:
```bash
grep -E '^(ENYCPHER_API_KEY|ENCYPHER_BASE_URL)=' .env.skills
```

2. Run the signer script with `.env.skills`:
```bash
uv run python enterprise_api/scripts/sign_blog_posts.py \
  apps/marketing-site/src/content/blog \
  --env-file .env.skills
```

3. Optional filters:
```bash
uv run python enterprise_api/scripts/sign_blog_posts.py \
  apps/marketing-site/src/content/blog \
  --env-file .env.skills \
  --from-date 2026-01-01 \
  --to-date 2026-02-28
```

4. Optional glob-based selection:
```bash
uv run python enterprise_api/scripts/sign_blog_posts.py \
  --glob 'apps/marketing-site/src/content/blog/*.md' \
  --env-file .env.skills
```

5. Verify outputs:
- Source markdown files are updated in place with signed body content (frontmatter preserved).
- Signing report is written to: `enterprise_api/output/signed_blog_posts/signing_report.json`

6. If needed, run dry-run mode first:
```bash
uv run python enterprise_api/scripts/sign_blog_posts.py \
  apps/marketing-site/src/content/blog \
  --env-file .env.skills \
  --dry-run
```

---

## Notes
- The script explicitly signs with `manifest_mode=micro`, `ecc=true`, and `embed_c2pa=true`.
- Posts are processed in ascending frontmatter `date` order.
- If a post has no frontmatter `date`, it is processed last.
- The workflow prefers `ENYCPHER_API_KEY`, but supports fallback `ENCYPHER_API_KEY` for compatibility.
- The workflow does not create `.signed.txt` files; it replaces the original `.md` file content.
