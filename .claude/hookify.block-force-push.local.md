---
name: block-force-push
enabled: true
event: bash
action: block
pattern: "git push.*(--force\\b|-f\\b|--force-with-lease)"
---

Force push blocked. This can overwrite remote history permanently and is not reversible.

To proceed, the user must explicitly request a force push. Do not retry without their confirmation. If you need to reconcile a rebased branch, explain the situation to the user and let them decide.
