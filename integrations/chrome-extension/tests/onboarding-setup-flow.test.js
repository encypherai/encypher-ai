import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const EXTENSION_ROOT = path.resolve(__dirname, '..');

describe('Optional login onboarding + setup tracking', () => {
  it('shows optional login benefit copy in popup sign no-key state', () => {
    const popupHtmlPath = path.join(EXTENSION_ROOT, 'popup', 'popup.html');
    const popupHtml = fs.readFileSync(popupHtmlPath, 'utf8');

    assert.match(
      popupHtml,
      /id="onboarding-setup"/,
      'Popup should include a dedicated onboarding setup block'
    );

    assert.match(
      popupHtml,
      /Log in to track your signed content and get notified when it's found on the web/i,
      'Popup should clearly explain the benefit of optional login'
    );

    assert.match(
      popupHtml,
      /id="onboarding-dashboard-login"/,
      'Popup should provide a dashboard login CTA for extension onboarding'
    );

    assert.match(
      popupHtml,
      /id="onboarding-dashboard-signup"/,
      'Popup should provide a dashboard signup CTA for extension onboarding'
    );

    assert.match(
      popupHtml,
      /id="onboarding-dashboard-google"/,
      'Popup should expose a Google dashboard auth quick action'
    );

    assert.match(
      popupHtml,
      /id="onboarding-dashboard-github"/,
      'Popup should expose a GitHub dashboard auth quick action'
    );

    assert.match(
      popupHtml,
      /id="onboarding-dashboard-passkey"/,
      'Popup should expose a passkey dashboard auth quick action'
    );

    assert.match(
      popupHtml,
      /Choose a sign-in method/i,
      'Popup should guide users through choosing an auth method first'
    );
  });

  it('wires popup onboarding auth actions to dashboard redirect and credential sync handlers', () => {
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');

    assert.match(
      popupJs,
      /openDashboardAuth\('login'\)/,
      'Popup should route login onboarding CTA through dashboard auth redirect helper'
    );

    assert.match(
      popupJs,
      /openDashboardAuth\('signup'\)/,
      'Popup should route signup onboarding CTA through dashboard auth redirect helper'
    );

    assert.match(
      popupJs,
      /openDashboardAuth\('login',\s*'google'\)/,
      'Popup should support dashboard Google auth redirects'
    );

    assert.match(
      popupJs,
      /openDashboardAuth\('login',\s*'github'\)/,
      'Popup should support dashboard GitHub auth redirects'
    );

    assert.match(
      popupJs,
      /openDashboardAuth\('login',\s*'passkey'\)/,
      'Popup should support dashboard passkey auth redirects'
    );

  });

  it('implements background auto-provisioning message handler for extension users', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /AUTO_PROVISION_EXTENSION_USER/,
      'Service worker should support onboarding provisioning message'
    );

    assert.match(
      workerCode,
      /\/api\/v1\/provisioning\/auto-provision/,
      'Service worker should call the auto-provisioning endpoint'
    );

    assert.match(
      workerCode,
      /source\s*:\s*'api'/,
      'Provisioning request should use a valid API provisioning source'
    );

    assert.match(
      workerCode,
      /integration\s*:\s*'chrome_extension'/,
      'Provisioning request metadata should identify chrome extension attribution'
    );

    assert.match(
      workerCode,
      /OPEN_DASHBOARD_AUTH/,
      'Service worker should support opening dashboard auth routes from popup onboarding'
    );

    assert.match(
      workerCode,
      /chrome\.tabs\.create\(/,
      'Service worker should open dashboard auth flows in a browser tab'
    );
  });

  it('tracks extension setup status in settings defaults and manual API-key override path', () => {
    const optionsPath = path.join(EXTENSION_ROOT, 'options', 'options.js');
    const optionsCode = fs.readFileSync(optionsPath, 'utf8');

    assert.match(
      optionsCode,
      /extensionSetupStatus/,
      'Options settings should include extension setup status tracking key'
    );

    assert.match(
      optionsCode,
      /saveSetting\('extensionSetupStatus',\s*'completed'\)/,
      'Saving a manual API key should mark setup as completed'
    );

    const optionsHtmlPath = path.join(EXTENSION_ROOT, 'options', 'options.html');
    const optionsHtml = fs.readFileSync(optionsHtmlPath, 'utf8');

    assert.match(
      optionsHtml,
      /id="extensionSetupStatus"/,
      'Options page should expose setup status control for overrides'
    );
  });

  it('shows signer identity in popup sign state using publisher display name when available', () => {
    const popupHtmlPath = path.join(EXTENSION_ROOT, 'popup', 'popup.html');
    const popupHtml = fs.readFileSync(popupHtmlPath, 'utf8');
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');

    assert.match(
      popupHtml,
      /id="sign-identity"/,
      'Popup sign tab should include a signer identity element'
    );

    assert.match(
      popupJs,
      /publisherDisplayName\s*\|\|\s*info\?\.organizationName/,
      'Popup should prefer publisher display name and fall back to organization name'
    );
  });

  it('surfaces publisher identity in extension settings after API key validation', () => {
    const optionsHtmlPath = path.join(EXTENSION_ROOT, 'options', 'options.html');
    const optionsHtml = fs.readFileSync(optionsHtmlPath, 'utf8');
    const optionsJsPath = path.join(EXTENSION_ROOT, 'options', 'options.js');
    const optionsJs = fs.readFileSync(optionsJsPath, 'utf8');

    assert.match(
      optionsHtml,
      /id="publisherIdentity"/,
      'Options page should show who content will be signed as'
    );

    assert.match(
      optionsJs,
      /type:\s*'GET_ACCOUNT_INFO'/,
      'Options should query account identity from the extension worker'
    );

    assert.match(
      optionsJs,
      /publisherDisplayName\s*\|\|\s*account\.organizationName/,
      'Options identity should prioritize publisher display name with organization fallback'
    );

    assert.match(
      optionsJs,
      /data\?\.data\s*\|\|\s*data/,
      'Options account parsing should support wrapped success/data payloads from enterprise API'
    );

    assert.match(
      optionsJs,
      /organization_name\s*\|\|\s*accountPayload\.name/,
      'Options account parsing should fall back to account name when organization_name is absent'
    );
  });

  it('supports localhost API origins for local superadmin API keys', () => {
    const manifestPath = path.join(EXTENSION_ROOT, 'manifest.json');
    const manifestRaw = fs.readFileSync(manifestPath, 'utf8');
    const manifest = JSON.parse(manifestRaw);
    const hostPermissions = manifest.host_permissions || [];

    assert.ok(
      hostPermissions.includes('http://localhost/*'),
      'Manifest should permit localhost API origins for local development accounts'
    );

    assert.ok(
      hostPermissions.includes('http://127.0.0.1/*'),
      'Manifest should permit 127.0.0.1 API origins for local development accounts'
    );
  });

  it('supports secure dashboard callback handoff into extension credentials', () => {
    const manifestPath = path.join(EXTENSION_ROOT, 'manifest.json');
    const manifestRaw = fs.readFileSync(manifestPath, 'utf8');
    const manifest = JSON.parse(manifestRaw);
    const externalMatches = manifest.externally_connectable?.matches || [];

    assert.ok(
      externalMatches.includes('https://dashboard.encypherai.com/*'),
      'Manifest should explicitly allow dashboard.encypherai.com to send extension handoff messages'
    );

    assert.ok(
      externalMatches.includes('https://*.encypherai.com/*'),
      'Manifest should allow secure dashboard subdomains for extension handoff'
    );

    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /chrome\.runtime\.onMessageExternal\.addListener\(/,
      'Service worker should accept trusted external dashboard messages for callback handoff'
    );

    assert.match(
      workerCode,
      /DASHBOARD_API_KEY_HANDOFF/,
      'Service worker should handle dashboard API key handoff messages'
    );

    assert.match(
      workerCode,
      /source\s*:\s*'dashboard_handoff'/,
      'Handoff path should mark setup source as dashboard_handoff for onboarding analytics'
    );

    assert.match(
      workerCode,
      /callbackUrl/,
      'Dashboard auth URL builder should include callbackUrl metadata for post-login handoff'
    );

    assert.match(
      workerCode,
      /extension-handoff/,
      'Dashboard auth callback should target the extension handoff route'
    );
  });

  it('wires dashboard auth screens to extension handoff callback route', () => {
    const dashboardRoot = path.resolve(EXTENSION_ROOT, '..', '..', 'apps', 'dashboard', 'src', 'app');
    const loginPath = path.join(dashboardRoot, 'login', 'page.tsx');
    const signupPath = path.join(dashboardRoot, 'signup', 'page.tsx');
    const handoffPath = path.join(dashboardRoot, 'extension-handoff', 'page.tsx');

    const loginCode = fs.readFileSync(loginPath, 'utf8');
    const signupCode = fs.readFileSync(signupPath, 'utf8');
    const handoffCode = fs.readFileSync(handoffPath, 'utf8');

    assert.match(
      loginCode,
      /callbackUrl/,
      'Login page should preserve callbackUrl so extension onboarding can continue after auth'
    );

    assert.match(
      loginCode,
      /useSearchParams/,
      'Login page should read extension handoff query params'
    );

    assert.match(
      signupCode,
      /callbackUrl/,
      'Signup page should carry callbackUrl for OAuth-based extension onboarding'
    );

    assert.match(
      handoffCode,
      /DASHBOARD_API_KEY_HANDOFF/,
      'Extension handoff page should post generated API keys to the extension via external messaging'
    );

    assert.match(
      handoffCode,
      /runtime\.sendMessage/,
      'Extension handoff page should call chrome.runtime.sendMessage for callback handoff'
    );
  });

  it('supports selecting default signing method in settings and popup sign tab', () => {
    const popupHtmlPath = path.join(EXTENSION_ROOT, 'popup', 'popup.html');
    const popupHtml = fs.readFileSync(popupHtmlPath, 'utf8');
    const popupJsPath = path.join(EXTENSION_ROOT, 'popup', 'popup.js');
    const popupJs = fs.readFileSync(popupJsPath, 'utf8');
    const optionsHtmlPath = path.join(EXTENSION_ROOT, 'options', 'options.html');
    const optionsHtml = fs.readFileSync(optionsHtmlPath, 'utf8');
    const optionsJsPath = path.join(EXTENSION_ROOT, 'options', 'options.js');
    const optionsJs = fs.readFileSync(optionsJsPath, 'utf8');

    assert.match(
      popupHtml,
      /id="sign-embedding-technique"/,
      'Popup sign tab should expose an embedding technique dropdown'
    );

    assert.match(
      popupHtml,
      /id="sign-segmentation-level"/,
      'Popup sign tab should expose a segmentation level dropdown'
    );

    assert.match(
      popupJs,
      /manifestMode/,
      'Popup signing payload should include manifestMode metadata'
    );

    assert.match(
      popupJs,
      /chrome\.storage\.sync\.get\([\s\S]*defaultEmbeddingTechnique/s,
      'Popup should load defaultEmbeddingTechnique from sync settings'
    );

    assert.match(
      optionsHtml,
      /id="defaultEmbeddingTechnique"/,
      'Options should expose default embedding technique control'
    );

    assert.match(
      optionsJs,
      /defaultEmbeddingTechnique/,
      'Options defaults should include defaultEmbeddingTechnique and save handler wiring'
    );
  });

  it('keeps content script iframe injection settings ready for LinkedIn composer preload frames', () => {
    const manifestPath = path.join(EXTENSION_ROOT, 'manifest.json');
    const manifestRaw = fs.readFileSync(manifestPath, 'utf8');
    const manifest = JSON.parse(manifestRaw);
    const contentScript = (manifest.content_scripts || [])[0] || {};

    assert.strictEqual(
      contentScript.all_frames,
      true,
      'Content script should inject into all frames so LinkedIn preload composers are covered'
    );

    assert.strictEqual(
      contentScript.match_origin_as_fallback,
      true,
      'Content script should enable match_origin_as_fallback for iframe-origin fallback matching'
    );

    assert.strictEqual(
      contentScript.run_at,
      'document_start',
      'Content script should inject early enough for dynamic preload frame editors'
    );
  });
});
