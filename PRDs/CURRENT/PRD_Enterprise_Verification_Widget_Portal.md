# Consumer Verification: Embed Widget + Public Verification Portal

**Status:** 📋 Planning  
**Current Goal:** Task 1.1 — Define the minimal verification UI experience required for publisher adoption.

## Overview

Publishers need an easy way to show readers that content is signed and verifiable. This PRD defines a lightweight JS embed widget and a public verification portal that displays signer identity, manifest details, and revocation status.

## Objectives

- Provide a simple embeddable badge that links to verification details
- Provide a public portal for paste-and-verify and shareable results
- Ensure privacy, caching, and performance constraints are respected

## Tasks

### 1.0 Verification Widget

- [ ] 1.1 Define widget UX variants (inline, floating, minimal)
- [ ] 1.2 Implement widget detection (find signed blocks)
- [ ] 1.3 Implement verification calls and caching
- [ ] 1.4 Provide customization options
- [ ] 1.5 Create embed code generator in dashboard
- [ ] 1.6 Provide CDN distribution

### 2.0 Public Verification Portal

- [ ] 2.1 Implement paste/upload flow
- [ ] 2.2 Render verification verdict
- [ ] 2.3 Render signer + trust anchor
- [ ] 2.4 Render revocation state
- [ ] 2.5 Provide shareable results URLs

### 3.0 SEO + Trust

- [ ] 3.1 SEO-friendly result pages
- [ ] 3.2 Publisher branding options (enterprise)

### 4.0 Testing & Validation

- [ ] 4.1 Unit tests passing — ✅ pytest
- [ ] 4.2 Frontend verification — ✅ puppeteer

## Success Criteria

- Publishers can embed a badge and readers can verify easily
- Public portal handles high traffic safely
- Shareable verification results work reliably

## Completion Notes

(Filled when PRD is complete.)
