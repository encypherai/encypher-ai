# TEAM_251 — Blog Writer Cron Wrapper Fix

## Status: COMPLETE

## Problem
The cron job (firing Tuesday 9 AM EST) referenced `cron-wrapper.sh` which did not exist.
Only `run.sh` existed. Cron exited 127 silently; no log file was written; no blog post
was produced for 2026-03-10.

## Root Cause
`cron-wrapper.sh` was never created. Cron's bare environment also lacks PATH entries for
`claude`, `uv`, and env vars (`ANTHROPIC_API_KEY`, `GH_TOKEN`, `ENCYPHER_API_KEY`).
Calling `run.sh` directly from cron would silently skip signing even if the file existed.

## Fix Applied

### Files Created
- `scripts/agents/blog-writer/cron-wrapper.sh` (chmod +x)
  - Sets PATH to include `/home/developer/.local/bin` (claude, uv) and `/usr/local/bin`
  - Sources `<repo-root>/.env.skills` via `set -a / source / set +a`
  - Execs `run.sh "$@" >> /var/log/encypher-blog-writer.log 2>&1`
  - Bash syntax verified: `bash -n cron-wrapper.sh` passes

### Files Modified
- `scripts/agents/blog-writer/README.md`
  - Cron setup section updated: references wrapper, explains why, shows correct crontab
  - Files table updated: `cron-wrapper.sh` added
  - Environment Variables section updated: explains `.env.skills` for cron use

## Verification Steps (manual, to be run by operator)
1. `bash -n cron-wrapper.sh` — syntax OK (done)
2. `crontab -l` — confirm existing entry points to cron-wrapper.sh
3. To catch up on today's missed post: `./scripts/agents/blog-writer/cron-wrapper.sh`
4. `tail -f /var/log/encypher-blog-writer.log` to monitor

## Crontab Entry (no change needed)
```
TZ=America/New_York
0 9 * * 2 /home/developer/code/encypherai-commercial/scripts/agents/blog-writer/cron-wrapper.sh
```

## Suggested Commit Message
```
fix(blog-writer): add cron-wrapper.sh to fix missing cron entry point

The cron job fired Tuesday 2026-03-10 09:00 EST but produced no output
because cron-wrapper.sh did not exist (exit 127). run.sh was the only
file present; it was never designed to be called directly from cron
(bare PATH, no API keys).

- Create cron-wrapper.sh: sets PATH, sources .env.skills, execs run.sh
- chmod +x cron-wrapper.sh
- Update README: cron setup section, files table, env vars section
```
