# Encypher Microsoft Office Add-in

Native Microsoft Office integration for **Word, Excel, and PowerPoint** using Office.js task pane architecture, with C2PA-aligned cryptographic proof-of-origin workflows.

Brand messaging and visual treatment are aligned with:
- `docs/company_internal_strategy/Encypher_Marketing_Guidelines.md`

## Current Host Coverage

- **Word**: selection sign/verify, full-document sign/verify, in-place replacement
- **Excel**: selection sign/verify, in-place replacement
- **PowerPoint**: selection sign/verify, in-place replacement

> Full-document operations are intentionally limited to Word in this version.

## Features

- Encypher sign and verify integration (`/api/v1/sign`, `/api/v1/verify`)
- Provenance chain extraction from embedded bytes (VS/ZWNBSP)
- Provenance persistence in `Office.context.roamingSettings`
- Re-sign support with `previous_embeddings`
- Host capability matrix with safe fallbacks for unsupported actions
- API base URL validation (`https://*.encypherai.com`)

## Brand & Design Conformance

- Uses Encypher official palette: Deep Navy `#1B2F50`, Azure Blue `#2A87C4`, Light Sky Blue `#B7D5ED`, Cyber Teal `#00CED1`, Neutral Gray `#A7AFBC`, White `#FFFFFF`.
- Typography is Roboto-first, with Roboto Mono style for technical/result displays.
- UI copy emphasizes standards authority, proof of origin, and collaborative infrastructure positioning.
- Manifest display metadata and ribbon labels use C2PA/provenance-aligned product language.

## Project Layout

```
integrations/microsoft-office-addin/
├── manifest.xml
├── package.json
├── taskpane/
│   ├── taskpane.html
│   └── taskpane.css
├── src/
│   ├── app.js
│   ├── api-client.js
│   ├── host-adapters.js
│   ├── host-capabilities.js
│   ├── provenance-utils.js
│   └── storage.js
└── tests/
    ├── api-client.test.js
    ├── host-capabilities.test.js
    └── provenance-utils.test.js
```

## Local Tests

```bash
cd integrations/microsoft-office-addin
npm test
```

## Run Task Pane Locally

Serve the `integrations/microsoft-office-addin` directory over HTTPS (Office requires HTTPS for sideloaded web assets).

Example with local HTTPS tooling (recommended):

1. Start a local HTTPS server at `https://localhost:4000`
2. Ensure `taskpane/taskpane.html` is reachable
3. Keep `manifest.xml` `SourceLocation` set to `https://localhost:4000/taskpane/taskpane.html`

## Sideload in Office

### Word / Excel / PowerPoint Desktop

1. Open Office app (Word/Excel/PowerPoint)
2. Go to **Insert > My Add-ins > Manage My Add-ins > Upload My Add-in**
3. Select `manifest.xml`
4. Open Encypher task pane from ribbon button

### Office on the web

1. Open Word/Excel/PowerPoint on the web
2. Insert > Add-ins > Upload My Add-in
3. Upload `manifest.xml`
4. Launch Encypher task pane

## AppSource Readiness Checklist

- [ ] Replace temporary icon URLs with production assets (16/32/80)
- [ ] Validate manifest with Microsoft 365 App Compliance tooling
- [ ] Complete privacy policy, terms, and support URLs
- [ ] Add telemetry and user-facing consent language
- [ ] Validate host behavior on Windows, Mac, and web clients
- [ ] Capture review artifacts (screenshots/video) for AppSource submission

## Security Notes

- API key is stored in Office roaming settings (per user)
- API host is restricted to `https://*.encypherai.com`
- Add-in uses `ReadWriteDocument` permission to support replacement flows
