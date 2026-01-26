# Start-Dev Stripe Listener

**Status:** 🔄 In Progress
**Current Goal:** Task 3.1 — manual verification

## Overview
Local billing webhook testing requires running `stripe listen` manually. This PRD adds an optional Stripe CLI listener to the start-dev script and documents the workflow so local devs can receive billing webhooks without extra steps.

## Objectives

- Start Stripe CLI webhook forwarding when running start-dev.
- Provide a skip flag and configurable forward URL.
- Document the updated workflow in Stripe setup docs.

## Tasks

### 1.0 Start-Dev Workflow

- [x] 1.1 Add Stripe CLI listener support to start-dev script
- [x] 1.2 Add skip flag and env override

### 2.0 Documentation

- [x] 2.1 Update Stripe setup guide with start-dev behavior

### 3.0 Testing & Validation

- [ ] 3.1 Manual verification — ✅ stripe listen

## Success Criteria

- start-dev can launch Stripe CLI forwarding without manual steps.
- Developers can opt out via flag or override URL.
- Documentation reflects the new workflow.

## Completion Notes

( заполнить при завершении )
