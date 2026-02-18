/**
 * Verification helpers shared by service-worker and tests.
 */

const MAX_DETAILS = 25;

function isOpaqueIdentity(value) {
  if (!value) return false;
  return /^(org_|usr_|user_)[a-z0-9-]+$/i.test(String(value).trim());
}

export function resolveSigningIdentity({ data, accountInfo } = {}) {
  const payload = data || {};

  const publisherName = String(payload.publisher_name || '').trim();
  if (publisherName && !isOpaqueIdentity(publisherName)) {
    return publisherName;
  }

  const explicitIdentity = String(
    payload.signing_identity || payload.publisher_display_name || payload.publisherDisplayName || ''
  ).trim();
  if (explicitIdentity && !isOpaqueIdentity(explicitIdentity)) {
    return explicitIdentity;
  }

  const signerName = String(payload.signer_name || '').trim();
  if (signerName && !isOpaqueIdentity(signerName)) {
    return signerName;
  }

  const organizationName = String(payload.organization_name || '').trim();
  if (organizationName && !isOpaqueIdentity(organizationName)) {
    return organizationName;
  }

  const account = accountInfo || {};
  const accountOrgId = String(account.organizationId || '').trim();
  const signerId = String(payload.signer_id || '').trim();
  const organizationId = String(payload.organization_id || '').trim();
  const sameOrg = Boolean(
    accountOrgId && (accountOrgId === signerId || accountOrgId === organizationId)
  );

  if (sameOrg) {
    const accountPublisher = String(account.publisherDisplayName || '').trim();
    if (accountPublisher) {
      return accountPublisher;
    }

    const accountOrgName = String(account.organizationName || '').trim();
    if (accountOrgName && !isOpaqueIdentity(accountOrgName)) {
      return accountOrgName;
    }
  }

  return null;
}

export function shouldRetryVerification(result) {
  if (!result || typeof result !== 'object') {
    return false;
  }

  const status = typeof result.status === 'number' ? result.status : null;
  if (status === 429) {
    return true;
  }
  if (status !== null && status >= 500) {
    return true;
  }

  const msg = String(result.error || '').toLowerCase();
  return msg.includes('timed out') || msg.includes('network error') || msg.includes('temporarily unavailable');
}

export function buildVerificationDetail({ markerType, result, detectionId = null }) {
  const data = result?.data || {};
  const isRevoked = !!result?.revoked;
  const isValid = result?.success === true;
  const signingIdentity = resolveSigningIdentity({ data });
  const signerName = String(data.signer_name || '').trim();
  const organizationName = String(data.organization_name || '').trim();
  const signer = (signerName && !isOpaqueIdentity(signerName))
    ? signerName
    : ((organizationName && !isOpaqueIdentity(organizationName)) ? organizationName : (signingIdentity || 'Unknown signer'));

  return {
    valid: isValid,
    revoked: isRevoked,
    detectionId,
    signingIdentity,
    signer,
    date: data.signed_at || data.revoked_at || null,
    markerType: markerType || 'unknown',
    documentId: data.document_id || null,
    verificationUrl: data.verification_url || null,
    reason: result?.error || null,
  };
}

export function appendVerificationDetail(details, detail) {
  const current = Array.isArray(details) ? details : [];
  return [detail, ...current].slice(0, MAX_DETAILS);
}

export function updateTabStateWithVerification(state, result) {
  const next = {
    ...state,
    verified: state?.verified || 0,
    invalid: state?.invalid || 0,
    revoked: state?.revoked || 0,
    pending: state?.pending || 0,
  };

  next.pending = Math.max(0, next.pending - 1);

  if (result?.success) {
    next.verified += 1;
  } else if (result?.revoked) {
    next.revoked += 1;
  } else {
    next.invalid += 1;
  }

  return next;
}

export function getIconStateForTab(state) {
  const invalid = state?.invalid || 0;
  const verified = state?.verified || 0;
  const revoked = state?.revoked || 0;

  if (invalid > 0) {
    return 'invalid';
  }
  if (verified > 0 && revoked > 0) {
    return 'mixed';
  }
  if (verified > 0) {
    return 'verified';
  }
  if (revoked > 0) {
    return 'revoked';
  }
  return 'found';
}
