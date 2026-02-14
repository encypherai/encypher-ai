# Encypher Microsoft Office Add-in

Native Microsoft Office integration for **Word, Excel, and PowerPoint** using Office.js task pane architecture.

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

1. Start a local HTTPS server at `https://localhost:3000`
2. Ensure `taskpane/taskpane.html` is reachable
3. Keep `manifest.xml` `SourceLocation` set to `https://localhost:3000/taskpane/taskpane.html`

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
