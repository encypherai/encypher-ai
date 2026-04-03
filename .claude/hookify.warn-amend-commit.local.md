---
name: warn-amend-commit
enabled: true
event: bash
action: warn
pattern: "git commit.*--amend"
---

Amending a commit. If this commit has already been pushed to a remote branch, amending will diverge local and remote history and require a force push to reconcile.

Only amend unpushed commits, or when the user has explicitly requested it.
