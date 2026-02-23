# Encypher Automated Blog Writer

A Claude agent that runs weekly to research and draft a new blog post, then opens a draft PR for human review before publishing.

## How It Works

1. Agent checks `TOPICS.md` for the highest-priority uncovered topic
2. Uses WebSearch to find current statistics, sources, and news hooks
3. Writes a 1,400-2,200 word post matching the blog's format and voice
4. Commits the markdown file and opens a **draft PR** for review
5. A human reviews and merges when satisfied - the post goes live on the next deploy

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

```bash
# Edit crontab
crontab -e

# Add this line (Tuesday 14:00 UTC = 9:00 AM EST):
0 14 * * 2 /path/to/encypherai-commercial/scripts/agents/blog-writer/run.sh >> /var/log/encypher-blog-writer.log 2>&1
```

Verify the job is registered:
```bash
crontab -l
```

### 4. Monitor logs

```bash
tail -f /var/log/encypher-blog-writer.log
```

## Workflow

```
Cron fires (Tuesday 9am EST)
  -> run.sh pulls main, creates branch blog/auto-YYYY-MM-DD
  -> Launches claude agent with AGENT_PROMPT.md
  -> Agent researches topic, writes post, commits to branch
  -> run.sh pushes branch and opens draft PR
  -> Human reviewer gets notified
  -> Reviewer merges PR when satisfied
  -> Next deploy publishes the post
```

## Files

| File | Purpose |
|------|---------|
| `run.sh` | Entry point, called by cron. Handles git, launches agent, creates PR. |
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

## Environment Variables (optional)

Set in your shell or cron environment:
```bash
# Anthropic API key (if claude CLI needs it)
export ANTHROPIC_API_KEY=sk-ant-...

# GitHub token (if gh CLI needs it)
export GITHUB_TOKEN=ghp_...
```

## Troubleshooting

**"No new blog post file detected"** - The agent failed to save the file to the right path. Check the agent output log for errors. Re-run manually with the same date.

**"Branch already exists"** - The script is idempotent: it skips if today's branch already exists. To force a re-run on the same day, delete the branch first: `git push origin --delete blog/auto-YYYY-MM-DD`

**Post quality issues** - Update `AGENT_PROMPT.md` to add stronger guardrails. The quality checklist at the bottom of the prompt is the key control point.
