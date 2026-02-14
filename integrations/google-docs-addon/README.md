# Encypher Google Docs Add-on

Google Workspace Add-on for Google Docs with native sign/verify workflows, C2PA-aligned proof-of-origin messaging, and provenance-chain support.

Brand messaging and visual treatment are aligned with:
- `docs/company_internal_strategy/Encypher_Marketing_Guidelines.md`

## Features

- Sign selected text in-place in Google Docs
- Sign full document in-place
- Verify selected text or full document
- Persist provenance embeddings per document hash
- Re-sign with `previous_embeddings` chain support
- Secure per-user API settings (API key + API base URL)

## Brand & Design Conformance

- Uses Encypher official palette: Deep Navy `#1B2F50`, Azure Blue `#2A87C4`, Light Sky Blue `#B7D5ED`, Cyber Teal `#00CED1`, Neutral Gray `#A7AFBC`, White `#FFFFFF`.
- Typography is Roboto-first, with Roboto Mono style for technical/result displays.
- Sidebar copy emphasizes standards authority, proof of origin, and collaborative infrastructure positioning.
- Add-on manifest name and universal action labels use C2PA/provenance-aligned product language.

## Project Structure

```
integrations/google-docs-addon/
├── appsscript.json            # Apps Script manifest (scopes + add-on config)
├── Code.gs                    # Add-on entrypoints, menu, sidebar launch
├── Config.gs                  # Configuration + API URL policy
├── Api.gs                     # Encypher sign/verify HTTP integration
├── DocsService.gs             # Docs extraction/replacement + sign/verify flows
├── Provenance.gs              # Embedding extraction and provenance persistence
├── SidebarActions.gs          # Sidebar server actions
├── Sidebar.html               # Sidebar UI
├── provenance-utils.js        # Shared local utility (Node-tested)
├── tests/
│   └── provenance-utils.test.js
└── .claspignore               # Excludes local-only files from push
```

## Google Requirements Covered

1. **Workspace Add-on Manifest**: `appsscript.json` includes `addOns.common` + `addOns.docs`.
2. **Least-privilege scopes**:
   - `documents.currentonly`
   - `script.container.ui`
   - `script.external_request`
   - `userinfo.email`
3. **HTTPS-only API access** with host restriction policy (`encypherai.com`) in `Config.gs`.
4. **User-facing menu + sidebar UX** (`onOpen`, add-on menu, homepage card).
5. **Error handling** for API and parsing failures.
6. **No hardcoded secrets**: API key is stored in User Properties.

## Local Test

```bash
cd integrations/google-docs-addon
npm test
```

## Deploy with clasp

### 1) Install clasp

```bash
npm install -g @google/clasp
clasp login
```

### 2) Create Apps Script project

From the `integrations/google-docs-addon` directory:

```bash
clasp create --type docs --title "Encypher Provenance Docs Add-on"
```

This creates `.clasp.json`. Or copy `.clasp.json.example` and set your `scriptId`.

### 3) Push code

```bash
clasp push
```

### 4) Open Apps Script editor

```bash
clasp open
```

### 5) Test in Google Docs

- In Apps Script editor: **Deploy > Test deployments**
- Choose **Editor add-on**
- Open a Google Doc and run:
  - **Extensions > Encypher C2PA Provenance > Open C2PA Sidebar**
- Configure API key in the sidebar settings

## Marketplace Submission Checklist

- [ ] Add production logo URL and branding assets
- [ ] Verify privacy policy and terms URLs in Cloud project OAuth consent screen
- [ ] Verify all scopes are justified in submission notes
- [ ] Add support contact email and documentation links
- [ ] Record test video showing sign/verify flows
- [ ] Complete Google Workspace Marketplace SDK listing fields

## Notes

- Provenance data is stored in **Document Properties**, keyed by visible text hash.
- Settings are stored in **User Properties** (per-user per-script).
- URL policy currently only allows `https://*.encypherai.com` endpoints.
