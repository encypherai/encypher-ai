# Integrations Local Test + Release Runbook

## Scope
This runbook covers release-readiness steps for:
- `integrations/outlook-email-addin`
- `integrations/microsoft-office-addin`
- `integrations/google-docs-addon`

Date executed: 2026-02-14

## 1) Preflight Checks (Completed Locally)

### Automated tests
- [x] Outlook add-in: `npm test` -> 14/14 pass
- [x] Microsoft Office add-in: `npm test` -> 13/13 pass
- [x] Google Docs add-on: `npm test` -> 6/6 pass
- [x] Email survivability integration tests: `uv run pytest enterprise_api/tests/test_email_embedding_survivability.py -q` -> 5/5 pass

### Manifest/config validation
- [x] Outlook manifest XML parses successfully
- [x] Microsoft Office manifest XML parses successfully
- [x] Google Docs `appsscript.json` parses successfully

### Packaging sanity
- [x] `npm pack --dry-run` succeeds for all three integrations
- [x] Tarball contents include expected source + manifest files

## 2) Local Manual Testing (What to run)

### Portable Installer Helper (new)
Use the installer helper to run a consistent preflight plan across multiple machines.

```bash
# Preview local-test plan for all integrations (default all)
uv run python scripts/integrations_installer.py --mode local-test

# Execute local preflight checks for all integrations and write report
uv run python scripts/integrations_installer.py --mode local-test --execute --report-file .tmp/integrations_installer_report.md

# Run only selected targets
uv run python scripts/integrations_installer.py --mode local-test --outlook --google-docs

# Generate deployment-only checklist plan
uv run python scripts/integrations_installer.py --mode deploy-plan --all
```

Portable notes:
- Requires only `uv`, `python`, and existing repo toolchain dependencies.
- Use `--repo-root /path/to/encypherai-commercial` when running outside the repository root.
- By design, installer output avoids machine-specific assumptions and emits explicit cwd per command.

### Practical forwarded-port HTTPS setup (Office/Outlook)
Use this when Office apps run on a host test machine but add-in assets are served from this machine.

Target ports used by manifests:
- Microsoft Office add-in: `https://localhost:4000/taskpane/taskpane.html`
- Outlook add-in: `https://localhost:4001/taskpane/taskpane.html`

On the serving machine (this repo machine):

```bash
# 1) Create trusted localhost certs (one-time)
mkcert -install
mkcert localhost 127.0.0.1 ::1

# 2) Serve Office add-in assets over HTTPS:4000
npx http-server integrations/microsoft-office-addin \
  -p 4000 -a 127.0.0.1 \
  -S -C localhost+2.pem -K localhost+2-key.pem

# 3) Serve Outlook add-in assets over HTTPS:4001
npx http-server integrations/outlook-email-addin \
  -p 4001 -a 127.0.0.1 \
  -S -C localhost+2.pem -K localhost+2-key.pem
```

If `localhost+2.pem` naming differs on your machine, use the filenames emitted by `mkcert`.

On the host test machine:
- Ensure forwarded `localhost:4000` and `localhost:4001` map to this machine.
- Trust the generated local CA/certificate on the host machine if certificate warnings appear.
- Sideload the manifest XML files only; web assets can remain on the serving machine.

### Outlook add-in
1. Serve `integrations/outlook-email-addin` over HTTPS at `https://localhost:4001`.
2. Upload `manifest.xml` as a custom add-in in Outlook desktop/web.
3. In compose and read modes:
   - save API settings
   - run sign and verify
   - confirm provenance summary updates

### Microsoft Office add-in (Word/Excel/PowerPoint)
1. Serve `integrations/microsoft-office-addin` over HTTPS at `https://localhost:4000`.
2. Upload `manifest.xml` in each host app.
3. Test:
   - selection sign/verify in Word, Excel, PowerPoint
   - full-document sign/verify in Word
   - host capability indicators and settings persistence

### Google Docs add-on
1. In `integrations/google-docs-addon`:
   - `clasp login`
   - `clasp create --type docs --title "Encypher C2PA Provenance Docs Add-on"` (or use `.clasp.json`)
   - `clasp push`
2. In Apps Script editor: Deploy -> Test deployments -> Editor add-on.
3. In Google Docs:
   - Extensions -> Encypher C2PA Provenance -> Open C2PA Sidebar
   - test selection/full-document sign + verify
   - verify settings persistence and provenance summary updates

## 3) Release Readiness Status

### Completed in-repo and local
- [x] Branding/design conformance applied across all three integrations
- [x] Unit/integration tests passing
- [x] Core manifests/configs validated for syntax
- [x] Local packaging dry-run validated
- [x] PRD and team handoff docs updated

### External/manual blockers (cannot be completed from repository only)
- [ ] Microsoft 365 tenant deployment (admin permissions required)
- [ ] Outlook/Office production asset hosting and cert setup
- [ ] Google Workspace domain deployment + OAuth consent configuration
- [ ] AppSource submission in Partner Center
- [ ] Google Workspace Marketplace submission and review artifacts
- [ ] Legal/privacy/support URLs finalized in marketplace consoles

## 4) Publish Paths

### Microsoft ecosystem (Outlook + Office add-ins)
1. Internal rollout first (M365 Admin Center -> Integrated apps -> upload manifest)
2. Validate behavior on web/Windows/Mac Office clients
3. Public distribution via AppSource after compliance package is complete

### Google Docs add-on
1. Internal test deployment in Apps Script
2. Domain rollout via Google Workspace admin controls
3. Public listing via Google Workspace Marketplace SDK + review process

## 5) Evidence Snapshot
- Outlook tests: pass (14/14)
- Office tests: pass (13/13)
- Google Docs tests: pass (6/6)
- Enterprise survivability tests: pass (5/5)
- UI brand checks: Puppeteer screenshots + DOM token checks completed for Outlook, Office, and Google Docs integrations
