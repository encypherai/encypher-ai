# Encypher Outlook Email Add-in

Outlook Mailbox add-in scaffold for signing and verifying email body content with Encypher provenance.

## What this add-in supports

- **Compose / Read task pane** in Outlook Mail host
- Sign current email body text via `POST /api/v1/sign`
- Verify current email body text via `POST /api/v1/verify`
- Provenance chain persistence in `Office.context.roamingSettings`
- API base URL enforcement (`https://*.encypherai.com`)

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

1. Host this folder over HTTPS so `taskpane/taskpane.html` is available (manifest points to `https://localhost:3000/taskpane/taskpane.html`).
2. In Outlook web or desktop, upload `manifest.xml` as a custom add-in.
3. Open a message in compose/read mode.
4. Launch **Encypher Email Provenance** task pane.
5. Save API settings and run Sign/Verify actions.

## Important implementation notes

- This scaffold currently reads/writes **plain text body** using `Office.context.mailbox.item.body.getAsync/setAsync` with `CoercionType.Text`.
- Email gateways and client conversions may strip specific invisible Unicode classes.
- Use the survivability harness and Python tests to compare embedding durability before deciding default mode.

## Recommended default for email

- Start with `micro_ecc_c2pa` for compact payload + RS recovery in moderate corruption paths.
- Add fallback routing to `zw_embedding` for environments known to strip supplementary variation selectors.
- Capture processor-specific telemetry before hard-coding one universal default.
