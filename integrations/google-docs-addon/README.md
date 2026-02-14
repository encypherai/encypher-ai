# Encypher Google Docs Add-on

Google Workspace Add-on for Google Docs with native sign/verify workflows and provenance-chain support.

## Features

- Sign selected text in-place in Google Docs
- Sign full document in-place
- Verify selected text or full document
- Persist provenance embeddings per document hash
- Re-sign with `previous_embeddings` chain support
- Secure per-user API settings (API key + API base URL)

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
  - **Extensions > Encypher Provenance > Open Sidebar**
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
