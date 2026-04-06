# TEAM_289 -- NPR Meeting Follow-Up, Segment Rights, Audio Soft-Binding

**Created:** 2026-03-30
**Updated:** 2026-04-04
**Status:** Active (PRDs in progress)
**Scope:** Update internal strategy docs with Erica/NPR intro meeting outcomes; draft follow-up email; implement segment-level rights and audio soft-binding features.

## Completed Tasks
- [x] Update Relationship Tracker (NPR row, SC portfolio, action queue, changelog)
- [x] Update SC Application (checklist, adoption section, Track 3 table)
- [x] Update SC Outreach Emails (NPR section)
- [x] Draft follow-up email to Erica
- [x] Maturity assessment for NPR use case (identified 3 gaps)
- [x] PRD: Segment-Level Rights (PRDs/CURRENT/PRD_Segment_Level_Rights.md) -- core implementation complete
- [x] PRD: Audio Soft-Binding (PRDs/CURRENT/PRD_Audio_Soft_Binding.md) -- core implementation complete

## Audio Soft-Binding Implementation Summary (Session 2)
- Rewrote spread-spectrum core from STFT to time-domain approach (STFT magnitude modification roundtrip is unreliable)
- Removed scipy dependency (time-domain approach needs only numpy)
- 12/12 microservice tests passing (embed/detect roundtrip, SNR, audio I/O)
- Created audio_watermark_client.py mirroring trustmark_client.py (13/13 tests)
- Signing pipeline: _sign_audio() in media_signing.py and audio_signing_executor.py apply watermark after C2PA signing
- c2pa.soft_binding.v1 assertion added as custom assertion when enable_audio_watermark=True
- Verification pipeline: verify_audio_with_watermark() combines C2PA + watermark detection
- Tier gating: audio_watermark feature flag in tier_config.py (7/7 tests)
- 369/369 enterprise_api unit tests passing, zero regressions

## Meeting Summary (2026-03-30)
- **Contact:** Erica, NPR (BD/Licensing), based outside Baltimore
- **Intro via:** Scott Cunningham (publisher/ad tech circles)
- **NPR status:** Testing TollBit, working with CDN, legal frameworks for content licensing with outside counsel. Rights management is complex (lots of unowned content on site). C2PA members but resource-constrained. 240+ member stations.
- **Key interests:** Sentence-level granularity, audio provenance, rights-aware marking, verification tools for investigations team, interoperability across specs
- **What landed:** Sentence-level marking, rights-aware content tagging, innocent infringement framing, audio coverage, low/no cost + co-marketing
- **Agreed next steps:** Erica scheduling follow-up (~April 13) with CMS/publishing tools, distribution, content ops, and RAD (archives) teams
- **SC ask:** Not made during call. To be included in follow-up email.
- **Erica's closing:** "I very strongly believe in the work that you're doing, so we're very aligned."

## Remaining Work

### Segment-Level Rights PRD
- Task 3.5: Validate segment_rights indices against segmentation output count
- Task 4.2-4.3: Verification logic and public rights API for v2 assertion
- Task 5.1: Consolidate duplicate RightsMetadata definitions
- Tasks 6.3-6.9: Integration tests

### Audio Soft-Binding PRD
- Task 1.7: MP3/M4A format support (requires ffmpeg integration)
- Task 4.2: DB lookup of audio_id/org_id from watermark payload
- Task 5.2: Tier validation in media signing router (reject if free tier)
- Task 5.3: DB migration for watermark tracking columns
- Tasks 6.2, 6.4-6.12: MP3 roundtrip, robustness tests, integration tests

## Suggested Commit Messages

```
feat(audio-watermark): add spread-spectrum audio watermarking microservice

Time-domain spread-spectrum watermarking embeds a 64-bit payload into audio
signals using pseudo-noise sequences. Survives signal-domain transformations
that strip container metadata. Architecture mirrors TrustMark image service.

New files:
- services/audio-watermark-service/ (FastAPI microservice, spread_spectrum.py core)
- enterprise_api/app/services/audio_watermark_client.py (async httpx client)

Modified:
- enterprise_api/app/config.py (audio_watermark_service_url setting)
- enterprise_api/app/core/tier_config.py (audio_watermark feature flag)
- enterprise_api/app/routers/media_signing.py (enable_audio_watermark form field)
- enterprise_api/app/services/audio_signing_executor.py (watermark after C2PA)
- enterprise_api/app/services/audio_verification_service.py (combined C2PA+watermark)
- enterprise_api/app/api/v1/audio_verify.py (watermark fields in response)

Tests: 12/12 microservice, 13/13 client, 7/7 tier, 369/369 unit (zero regressions)
```
