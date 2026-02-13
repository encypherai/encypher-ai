import { Config } from './config';

/**
 * Generate the verification badge code injection snippet.
 *
 * This JavaScript snippet is injected into a Ghost post's `codeinjection_foot`
 * field. It renders a small verification badge on the published page that
 * readers can click to verify the content's C2PA provenance.
 */
export function generateBadgeScript(
  config: Config,
  documentId: string,
  instanceId: string,
): string {
  const verifyUrl = config.badge.verifyBaseUrl;
  const verificationId = instanceId || documentId;

  return `
<script data-encypher-badge="true">
(function() {
  var VERIFY_URL = ${JSON.stringify(verifyUrl)};
  var VERIFICATION_ID = ${JSON.stringify(verificationId)};

  function createBadge() {
    if (document.querySelector('.encypher-provenance-badge')) return;

    var badge = document.createElement('div');
    badge.className = 'encypher-provenance-badge';
    badge.innerHTML = '<a href="' + VERIFY_URL + '/' + encodeURIComponent(VERIFICATION_ID) +
      '" target="_blank" rel="noopener noreferrer" ' +
      'style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;' +
      'background:#f0fdf4;border:1px solid #86efac;border-radius:6px;' +
      'font-size:13px;color:#166534;text-decoration:none;font-family:system-ui,sans-serif;">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
      '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>' +
      '<path d="M9 12l2 2 4-4"/></svg>' +
      '<span>C2PA Verified</span></a>';

    badge.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;';

    document.body.appendChild(badge);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createBadge);
  } else {
    createBadge();
  }
})();
</script>`.trim();
}

/**
 * Merge new badge script into existing codeinjection_foot content.
 * Removes any previous Encypher badge script before adding the new one.
 */
export function mergeBadgeInjection(
  existingCodeinjection: string | null,
  newBadgeScript: string,
): string {
  let base = existingCodeinjection || '';

  // Remove any existing Encypher badge script
  base = base.replace(/<script data-encypher-badge="true">[\s\S]*?<\/script>/g, '').trim();

  if (base) {
    return base + '\n' + newBadgeScript;
  }
  return newBadgeScript;
}
