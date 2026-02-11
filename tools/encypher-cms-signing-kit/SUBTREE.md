# Git Subtree Workflow

This directory (`tools/encypher-cms-signing-kit/`) is designed to be split into a standalone private repository that can be shared with CMS customers.

## Initial Split (one-time setup)

From the monorepo root:

```bash
# 1. Create the private repo on GitHub first (e.g. encypherai/encypher-cms-signing-kit)

# 2. Split this subtree into a new branch
git subtree split --prefix=tools/encypher-cms-signing-kit -b cms-signing-kit-split

# 3. Push to the private repo
git remote add cms-signing-kit git@github.com:encypherai/encypher-cms-signing-kit.git
git push cms-signing-kit cms-signing-kit-split:main

# 4. Clean up the temporary branch
git branch -D cms-signing-kit-split
```

## Pushing Updates

After making changes in the monorepo:

```bash
# Push changes from monorepo to the private repo
git subtree push --prefix=tools/encypher-cms-signing-kit cms-signing-kit git@github.com:encypherai/encypher-cms-signing-kit.git main
```

## Pulling Changes (if edits are made in the private repo)

```bash
git subtree pull --prefix=tools/encypher-cms-signing-kit cms-signing-kit git@github.com:encypherai/encypher-cms-signing-kit.git main --squash
```

## Inviting Customers

1. Add the customer's GitHub user as a collaborator on the private repo
2. Grant **read-only** access (or use GitHub's fine-grained permissions)
3. The customer clones and follows the README:

```bash
git clone git@github.com:encypherai/encypher-cms-signing-kit.git
cd encypher-cms-signing-kit
cp .env.example .env
# Edit .env with their API key
uv sync
uv run python encypher_sign_html.py page.html page_signed.html
```

## Notes

- The `SUBTREE.md` file itself should be excluded from the private repo if desired (add to `.gitignore` in the private repo, or remove after split)
- The `.env.example` ships with the repo; actual `.env` files are gitignored
- The `LICENSE` is proprietary — customers use it under their API license agreement
