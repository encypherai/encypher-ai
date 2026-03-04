# PRD: Windsurf Terminal Integration Research

**Status**: Completed  
**Current Goal**: Validate whether Windsurf exposes callable local hooks for terminal-driven integration and document a practical bridge approach.

## Overview
This effort investigates the running Windsurf client/server environment to identify reverse-engineerable interfaces for programmatic interaction. The goal is to provide a minimal, reproducible terminal bridge that can query available local RPC functionality and validate feasibility for chat/session automation.

## Objectives
- Identify Windsurf runtime processes, local ports, and auth requirements.
- Enumerate extension command and local service surfaces.
- Validate terminal-callable endpoints and payload patterns.
- Provide a practical terminal bridge script with documented limitations.

## Tasks
- [x] 1.0 Runtime reconnaissance — ✅ terminal verification
  - [x] 1.1 Identify Windsurf runtime process topology — ✅ terminal verification
  - [x] 1.2 Identify local data/storage footprints relevant to sessions/history — ✅ terminal verification
- [x] 2.0 Interface mapping — ✅ terminal verification
  - [x] 2.1 Enumerate declared Windsurf commands from extension manifest — ✅ terminal verification
  - [x] 2.2 Enumerate internal extension service methods from bundled extension — ✅ terminal verification
- [x] 3.0 Terminal bridge implementation — ✅ terminal verification
  - [x] 3.1 Add helper script to discover CSRF token and extension server port at runtime — ✅ terminal verification
  - [x] 3.2 Add helper script commands to call selected RPC methods (check shell support, search query, read terminal) — ✅ terminal verification
  - [x] 3.3 Validate script end-to-end in current Windsurf runtime — ✅ terminal verification
- [x] 4.0 Findings and constraints summary — ✅ terminal verification
  - [x] 4.1 Document what is possible today (callable local RPC) — ✅ terminal verification
  - [x] 4.2 Document what remains blocked (full chat session history CRUD and push updates) — ✅ terminal verification

## Success Criteria
- A reproducible terminal flow can call at least one Windsurf extension server RPC endpoint using discovered runtime auth material.
- A script exists in-repo to automate port/token discovery and RPC invocation.
- Constraints are clearly documented for session history and chat-message control.

## Completion Notes
- Added terminal bridge script: `scripts/windsurf_terminal_bridge.sh`.
- Validated local Windsurf extension RPC calls over `127.0.0.1:<extension_server_port>` with `x-codeium-csrf-token`.
- Confirmed working terminal-driven methods include `CheckTerminalShellSupport`, `SearchQuery`, and generic `rpc` invocation.
- Confirmed no stable/public API discovered for full Cascade chat session CRUD, direct message injection, or session update streaming.
