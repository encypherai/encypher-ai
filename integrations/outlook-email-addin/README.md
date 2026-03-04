# Encypher Outlook Email Add-in

Outlook Mailbox add-in for signing and verifying email body content with **cryptographic proof of origin** aligned to C2PA text provenance standards.

Brand messaging and visual treatment are aligned with internal standards in:
- `docs/company_internal_strategy/Encypher_Marketing_Guidelines.md`

## What this add-in supports

- **Compose / Read task pane** in Outlook Mail host
- Sign current email body text via `POST /api/v1/sign`
- Verify current email body text via `POST /api/v1/verify`
- Provenance chain persistence in `Office.context.roamingSettings`
- API base URL enforcement (`https://*.encypherai.com`)
- C2PA-aligned trust messaging and proof-of-origin workflow language in UI

## Brand & Design Conformance

- Palette uses Encypher official colors (Deep Navy `#1B2F50`, Azure `#2A87C4`, Light Sky Blue `#B7D5ED`, Cyber Teal `#00CED1`, Neutral Gray `#A7AFBC`, White `#FFFFFF`).
- Typography defaults to Roboto-first stack, with monospace for technical outputs.
- Messaging avoids adversarial framing and emphasizes collaborative standards infrastructure.
- UX language highlights:
  - "proof of origin"
  - "C2PA text provenance"
  - "collaborative infrastructure"

## Structure

```
integrations/outlook-email-addin/
├── manifest.xml
├── package.json
├── taskpane/
│   ├── taskpane.html
│   └── taskpane.css
├── src/
│   ├── app.js
│   ├── api-client.js
│   ├── outlook-adapter.js
│   ├── provenance-utils.js
│   ├── storage.js
│   └── survivability-harness.js
└── tests/
    ├── api-client.test.js
    ├── provenance-utils.test.js
    └── survivability-harness.test.js
```

## Local tests

```bash
cd integrations/outlook-email-addin
npm test
```

## Sideload in Outlook

1. Host this folder over HTTPS so `taskpane/taskpane.html` is available (manifest points to `https://localhost:4001/taskpane/taskpane.html`).
2. In Outlook web or desktop, upload `manifest.xml` as a custom add-in.
3. Open a message in compose/read mode.
4. Launch **Encypher Email Provenance** task pane.
5. Save API settings and run Sign/Verify actions.

## Important implementation notes

- This scaffold currently reads/writes **plain text body** using `Office.context.mailbox.item.body.getAsync/setAsync` with `CoercionType.Text`.
- Email gateways and client conversions may strip specific invisible Unicode classes.
- Use the survivability harness and Python tests to compare embedding durability before deciding default mode.

## Recommended default for email

- Start with `micro` (ecc=true, embed_c2pa=true) for compact payload + RS recovery in moderate corruption paths.
- Use `legacy_safe=true` flag for environments known to strip supplementary variation selectors (ZWNJ/ZWJ base-6 encoding).
- Capture processor-specific telemetry before hard-coding one universal default.

## Positioning Notes (for product/marketing consistency)

- Lead with standards authority and interoperability, not vendor lock-in.
- Emphasize cryptographic certainty over probabilistic detection.
- Frame verification as infrastructure for licensing/governance workflows.
