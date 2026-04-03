---
name: block-co-authored-by
enabled: true
event: bash
action: block
pattern: "Co-Authored-By:"
---

Blocked: Co-Authored-By trailers are not permitted in this project.

Per commit hygiene rules, commits are attributed to the human developer only. Remove the Co-Authored-By line and commit without it.
