---
name: Provenance capability limits
description: What Encypher can and cannot prove -- critical distinction for all copy and claims
type: feedback
---

Encypher CANNOT prove or detect that AI has outputted your original content. We can only:
- Check for markers as content enters systems (ingestion detection)
- Mark content as it leaves systems (signing at creation)

**Why:** With current technology, there is no way to prove an AI model used your content to generate its output. Markers survive in raw text (copy-paste, datasets, redistribution) but AI-generated text based on ingested content will NOT contain the original markers.

**How to apply:** Never write copy that implies we can detect our content in AI outputs. Claims about "proof of origin travels with it" are valid for copy-paste and redistribution scenarios. Claims about AI training are valid only in the sense that markers are detectable in training datasets at the ingestion point -- not that we can trace AI outputs back to our signed content. With major AI company integrations, we could create a chain of provenance (detect at ingestion + mark at output), but that's the ceiling of current technology.
