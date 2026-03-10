# Encypher Automated Blog Writer

A Claude agent that runs weekly to research and draft a new blog post, then opens a draft PR for human review before publishing.

## How It Works

> **The full publication sequence is in `.windsurf/workflows/blog-publish.md` — follow it for every post without exception.**

1. **Research** — agent gathers sources, stats, and news hooks
2. **First Draft** — agent writes post, opens draft PR
3. **Review & Approval** — human reviews and approves (no publishing without this)
4. **Generate Header Image** — after approval, before any commit
5. **Sign Content** — sign markdown with live Encypher API key
6. **Commit & Push** — image + signed post committed together
7. **Merge PR** — deploy

## Timing

**Tuesday 9:00 AM EST (14:00 UTC)** is the optimal publish window for B2B tech content:
- LinkedIn B2B engagement peaks Tuesday-Thursday 8-10am EST
- Google indexes faster when social signals spike at publication
- Fresh content on Tuesday gets indexed before mid-week search peaks
- Avoids Monday (inbox recovery) and Friday (pre-weekend drop-off)

## Setup

### 1. Install prerequisites

```bash
# Claude CLI
npm install -g @anthropic-ai/claude-code

# GitHub CLI
# https://cli.github.com/
gh auth login
```

### 2. Test the agent manually

```bash
# Auto-select from TOPICS.md
./scripts/agents/blog-writer/run.sh

# Override with specific topic
./scripts/agents/blog-writer/run.sh "EU AI Act Article 50 compliance guide"
```

### 3. Set up the cron job

Cron runs in a bare environment (no shell profile, minimal PATH, no API keys).
`cron-wrapper.sh` handles this: it extends PATH and sources `.env.skills` before
calling `run.sh`. The wrapper also redirects stdout+stderr to the log file.

```bash
# Edit crontab
crontab -e

# Add these two lines (Tuesday 9:00 AM EST):
TZ=America/New_York
0 9 * * 2 /home/developer/code/encypherai-commercial/scripts/agents/blog-writer/cron-wrapper.sh
```

Verify the job is registered:
```bash
crontab -l
```

**Do not call `run.sh` directly from cron** — it relies on PATH and env vars that
cron does not provide. Always go through `cron-wrapper.sh`.

### 4. Monitor logs

```bash
tail -f /var/log/encypher-blog-writer.log
```

## Workflow

```
1. Research        cron fires -> agent researches topic, commits research output
2. First Draft     agent writes post, commits to blog/auto-YYYY-MM-DD, opens draft PR
3. Review/Approval human reviews draft PR — NO publishing without explicit approval
4. Header Image    generate image AFTER approval — file must exist before commit
5. Sign Content    sign markdown with live Encypher API (ENYCPHER_API_KEY in .env.skills)
6. Commit & Push   image + signed post committed together, branch pushed
7. Merge PR        mark ready, merge, deploy
```

See `.windsurf/workflows/blog-publish.md` for the full checklist and commands.

## Files

| File | Purpose |
|------|---------|
| `cron-wrapper.sh` | Cron entry point. Sets PATH, sources `.env.skills`, execs `run.sh`. |
| `run.sh` | Main pipeline. Handles git, launches agent, creates PR. |
| `AGENT_PROMPT.md` | Full instructions for the Claude agent |
| `TOPICS.md` | Prioritized topic backlog. Check off `[x]` when published. |
| `README.md` | This file |

## Maintaining the Topic Backlog

Update `TOPICS.md` regularly:
- Add topics when you see relevant news or identify keyword gaps
- Check off `[x]` topics after the post is published
- Move time-sensitive topics to the top of their section
- The agent reads this file and picks the highest-priority unchecked item

## Customizing the Agent

Edit `AGENT_PROMPT.md` to:
- Update Encypher's positioning or recent milestones
- Change word count targets
- Add/remove approved tags
- Adjust tone guidelines

## Environment Variables

When running manually, export these in your shell before calling `run.sh`:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export GH_TOKEN=ghp_...
export ENCYPHER_API_KEY=...
```

When running via cron, place them in `<repo-root>/.env.skills` (one `KEY=value`
per line, no `export` prefix). `cron-wrapper.sh` sources that file automatically
via `set -a / source / set +a`.

## Troubleshooting

**"No new blog post file detected"** - The agent failed to save the file to the right path. Check the agent output log for errors. Re-run manually with the same date.

**"Branch already exists"** - The script is idempotent: it skips if today's branch already exists. To force a re-run on the same day, delete the branch first: `git push origin --delete blog/auto-YYYY-MM-DD`

**Post quality issues** - Update `AGENT_PROMPT.md` to add stronger guardrails. The quality checklist at the bottom of the prompt is the key control point.
