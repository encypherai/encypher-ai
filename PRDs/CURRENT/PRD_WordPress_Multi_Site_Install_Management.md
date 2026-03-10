# PRD: WordPress Multi-Site Install Management

**Status:** In Progress
**Current Goal:** Expand the WordPress integration from a single-site telemetry flow into a multi-property install management system with queued remote actions and verification telemetry.
**Team:** TEAM_052

## Overview

Large publishers and enterprise clients often operate multiple WordPress properties across brands, regions, business units, staging environments, and multisite networks. The current Encypher integration only tracks a single WordPress install per organization, which is insufficient for customers who need centralized operational visibility and guidance across multiple sites.

This initiative upgrades the WordPress integration to support:

- per-site install registration
- multiple WordPress installs per organization
- install-level connection and signing status
- verification event telemetry
- dashboard-triggered remote actions delivered safely through plugin polling
- a dashboard UX that lets teams manage multiple WordPress properties from one guided workspace

## Objectives

- [ ] Support multiple WordPress installs per organization without requiring a new database migration
- [ ] Register each WordPress site as a distinct install with stable install identity
- [ ] Track install-level status, connection health, signing activity, and verification activity
- [ ] Allow dashboard users to queue safe remote actions for a specific install
- [ ] Let the plugin poll for and acknowledge remote actions securely using its existing API key
- [ ] Expand the dashboard guided flow to surface all connected WordPress installs and their state
- [ ] Preserve backward compatibility for the current single-site status consumers

## Work Breakdown Structure

### 1.0 Product and Data Model
- [ ] 1.1 Define the multi-install WordPress data model inside `organization.add_ons.wordpress`
- [ ] 1.2 Define install identity fields: `install_id`, `site_url`, `admin_url`, `site_name`, `environment`, `network_id`, `blog_id`
- [ ] 1.3 Define install-level telemetry fields for connection, signing, and verification
- [ ] 1.4 Define queued remote action schema and lifecycle: `queued`, `acknowledged`, `completed`, `failed`
- [ ] 1.5 Define verification event schema and retention policy for recent events

### 2.0 Enterprise API
- [ ] 2.1 Add install registration endpoint for WordPress plugin onboarding
- [ ] 2.2 Expand status sync endpoint to upsert install-level state
- [ ] 2.3 Add endpoint to ingest verification telemetry events
- [ ] 2.4 Add dashboard endpoint to queue remote actions for a specific install
- [ ] 2.5 Add plugin endpoint to pull pending actions for one install
- [ ] 2.6 Add plugin endpoint to acknowledge action execution results
- [ ] 2.7 Keep `GET /integrations/wordpress/status` backward compatible while returning multi-install summary data

### 3.0 WordPress Plugin
- [ ] 3.1 Persist a stable local `install_id` in plugin settings
- [ ] 3.2 Register the install after quick connect or first successful connection test
- [ ] 3.3 Include install identity on all status sync calls
- [ ] 3.4 Send verification telemetry after successful verification checks
- [ ] 3.5 Poll remote actions after sync-capable operations and execute supported safe actions
- [ ] 3.6 Acknowledge remote action completion or failure back to the backend
- [ ] 3.7 Include multisite-aware metadata when available

### 4.0 Dashboard
- [ ] 4.1 Expand API client types and methods for multi-install WordPress management
- [ ] 4.2 Update guided WordPress workspace to show install count and install cards
- [ ] 4.3 Surface per-install connection, signing, and verification state
- [ ] 4.4 Add remote action controls for status refresh and connection retest
- [ ] 4.5 Highlight primary install and most recent verified/signed activity
- [ ] 4.6 Preserve current guided setup messaging for first-time single-site users

### 5.0 Validation
- [ ] 5.1 Type-check dashboard changes
- [ ] 5.2 Run targeted enterprise API validation for the integrations router
- [ ] 5.3 Run WordPress plugin contract coverage
- [ ] 5.4 Manually confirm backward compatibility for existing status consumers

## Functional Requirements

### Install Registration
- The plugin must register each site as a distinct install record.
- If the plugin already has an `install_id`, registration must be idempotent.
- An install record must be scoped to the authenticated organization derived from the API key.
- Install registration must capture site metadata needed for multi-property operations.

### Install-Level Status
- The backend must store multiple installs under the WordPress integration record.
- Each install must track:
  - connection state
  - connection tested state
  - last connection check time
  - plugin version
  - last sign time
  - signed post count
  - last verification time
  - verification counters and last verification outcome
- The backend must also return a summary view suitable for the current dashboard guide.

### Verification Telemetry
- The plugin must emit verification events after verification runs.
- Verification events must include install identity and basic result state.
- The backend must store recent verification telemetry without requiring a new table.

### Remote Actions
- Dashboard users must be able to queue safe remote actions for a specific install.
- Initial supported actions:
  - `refresh_status`
  - `test_connection`
- The plugin must poll for pending actions using its existing outbound API-key-authenticated channel.
- The plugin must acknowledge action completion with success/failure state and an optional result message.
- Remote actions must never require the backend to call directly into the customer’s WordPress instance.

### Dashboard UX
- The dashboard must show all connected WordPress installs for the active organization.
- Users must be able to identify which install is primary and which one most recently synced.
- The dashboard must show queued and recently completed remote actions.
- The dashboard must remain understandable for a single-install customer.

## Non-Goals

- Creating a dedicated `wordpress_installs` database table in this iteration
- Supporting arbitrary remote execution beyond the two safe actions above
- Building a full fleet-management dashboard outside the existing guided WordPress workspace
- Introducing inbound webhooks from the backend into customer WordPress environments

## Technical Approach

- Store the WordPress integration as a versioned object inside `organizations.add_ons.wordpress`
- Represent installs as an array keyed by stable `install_id`
- Represent pending/completed remote actions as a bounded array within the same structure
- Represent recent verification events as a bounded array within the same structure
- Keep the current status endpoint but return both summary fields and install collections
- Use plugin polling plus API-key auth for remote action delivery to avoid inbound connectivity/security risk

## Success Criteria

- [ ] One organization can register and manage multiple WordPress installs
- [ ] The dashboard shows more than one install without breaking current single-install flows
- [ ] Dashboard users can queue safe remote actions for a specific install
- [ ] The plugin picks up queued actions and acknowledges results
- [ ] Verification telemetry appears in backend state and dashboard summaries
- [ ] Existing type checks and WordPress contract tests remain green

## Rollout Notes

- Preserve backward compatibility by continuing to expose top-level WordPress summary fields
- Prefer the primary install, or the most recently updated install, when deriving summary fields
- Bound action/event history arrays to avoid unbounded growth in `add_ons`
