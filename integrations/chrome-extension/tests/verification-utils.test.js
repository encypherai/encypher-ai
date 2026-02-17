import { describe, it } from 'node:test';
import assert from 'node:assert';

import {
  appendVerificationDetail,
  buildVerificationDetail,
  getIconStateForTab,
  resolveSigningIdentity,
  shouldRetryVerification,
  updateTabStateWithVerification,
} from '../background/verification-utils.js';

describe('shouldRetryVerification', () => {
  it('retries timeout and transient network failures', () => {
    assert.strictEqual(shouldRetryVerification({ error: 'Request timed out' }), true);
    assert.strictEqual(shouldRetryVerification({ error: 'Network error' }), true);
  });

  it('retries HTTP 429 and 5xx responses', () => {
    assert.strictEqual(shouldRetryVerification({ status: 429 }), true);
    assert.strictEqual(shouldRetryVerification({ status: 500 }), true);
    assert.strictEqual(shouldRetryVerification({ status: 503 }), true);
  });

  it('does not retry non-transient failures', () => {
    assert.strictEqual(shouldRetryVerification({ status: 400 }), false);
    assert.strictEqual(shouldRetryVerification({ status: 403 }), false);
    assert.strictEqual(shouldRetryVerification({ status: 404 }), false);
  });

  it('prefers explicit signing identity in verification details', () => {
    const detail = buildVerificationDetail({
      markerType: 'c2pa',
      result: {
        success: true,
        data: {
          signing_identity: 'Test User at Encypher',
          signer_name: 'org_07dd7ff77fa7e949',
          organization_name: 'org_07dd7ff77fa7e949',
        },
      },
    });

    assert.strictEqual(detail.signingIdentity, 'Test User at Encypher');
  });
});

describe('resolveSigningIdentity', () => {
  it('uses account publisher identity when signer belongs to same org and payload names are opaque', () => {
    const identity = resolveSigningIdentity({
      data: {
        signer_id: 'org_07dd7ff77fa7e949',
        organization_id: 'org_07dd7ff77fa7e949',
        signer_name: 'org_07dd7ff77fa7e949',
        organization_name: 'org_07dd7ff77fa7e949',
      },
      accountInfo: {
        organizationId: 'org_07dd7ff77fa7e949',
        publisherDisplayName: 'Test User at Encypher',
        organizationName: 'Encypher',
      },
    });

    assert.strictEqual(identity, 'Test User at Encypher');
  });
});

describe('buildVerificationDetail', () => {
  it('maps successful verification data for popup details', () => {
    const detail = buildVerificationDetail({
      markerType: 'c2pa',
      result: {
        success: true,
        data: {
          signer_name: 'Acme News',
          signed_at: '2026-02-15T10:20:30Z',
          document_id: 'doc_123',
        },
      },
    });

    assert.strictEqual(detail.valid, true);
    assert.strictEqual(detail.revoked, false);
    assert.strictEqual(detail.signer, 'Acme News');
    assert.strictEqual(detail.documentId, 'doc_123');
    assert.strictEqual(detail.markerType, 'c2pa');
  });

  it('marks revoked verification distinctly', () => {
    const detail = buildVerificationDetail({
      markerType: 'micro',
      result: {
        success: false,
        revoked: true,
        data: {
          organization_name: 'Acme Org',
          revoked_at: '2026-02-15T10:20:30Z',
        },
      },
    });

    assert.strictEqual(detail.valid, false);
    assert.strictEqual(detail.revoked, true);
    assert.strictEqual(detail.signer, 'Acme Org');
    assert.strictEqual(detail.markerType, 'micro');
  });
});

describe('updateTabStateWithVerification', () => {
  it('increments revoked counter without incrementing invalid', () => {
    const state = { count: 2, verified: 0, pending: 2, invalid: 0, revoked: 0 };
    const next = updateTabStateWithVerification(state, { success: false, revoked: true });

    assert.strictEqual(next.pending, 1);
    assert.strictEqual(next.revoked, 1);
    assert.strictEqual(next.invalid, 0);
  });

  it('increments invalid counter for non-revoked failures', () => {
    const state = { count: 2, verified: 0, pending: 2, invalid: 0, revoked: 0 };
    const next = updateTabStateWithVerification(state, { success: false, revoked: false });

    assert.strictEqual(next.pending, 1);
    assert.strictEqual(next.invalid, 1);
    assert.strictEqual(next.revoked, 0);
  });
});

describe('appendVerificationDetail', () => {
  it('prepends latest details and caps length', () => {
    const details = Array.from({ length: 25 }, (_, i) => ({ signer: `Signer ${i}` }));
    const next = appendVerificationDetail(details, { signer: 'Newest' });

    assert.strictEqual(next.length, 25);
    assert.strictEqual(next[0].signer, 'Newest');
  });
});

describe('getIconStateForTab', () => {
  it('returns revoked when only revoked content is present', () => {
    const state = getIconStateForTab({ verified: 0, invalid: 0, revoked: 2, pending: 0 });
    assert.strictEqual(state, 'revoked');
  });

  it('returns mixed when revoked and verified are both present', () => {
    const state = getIconStateForTab({ verified: 1, invalid: 0, revoked: 1, pending: 0 });
    assert.strictEqual(state, 'mixed');
  });

  it('keeps invalid highest priority', () => {
    const state = getIconStateForTab({ verified: 3, invalid: 1, revoked: 2, pending: 0 });
    assert.strictEqual(state, 'invalid');
  });
});
