import assert from 'node:assert';
import { describe, it } from 'node:test';

import { PLAYGROUND_ENDPOINTS } from '../../src/lib/playgroundEndpoints.mjs';

const findById = (id) => PLAYGROUND_ENDPOINTS.find((endpoint) => endpoint.id === id);

describe('Playground endpoint catalog (contract)', () => {
  it('includes revocation status endpoints with correct metadata', () => {
    const statusDocument = findById('status-document');
    assert.ok(statusDocument, 'status-document endpoint missing');
    assert.equal(statusDocument.method, 'GET');
    assert.equal(statusDocument.path, '/status/documents/{document_id}');
    assert.equal(statusDocument.requiresAuth, true);
    assert.equal(statusDocument.minTier, 'professional');
    assert.equal(statusDocument.category, 'Status & Revocation');

    const revoke = findById('status-revoke');
    assert.ok(revoke, 'status-revoke endpoint missing');
    assert.equal(revoke.method, 'POST');
    assert.equal(revoke.path, '/status/documents/{document_id}/revoke');
    assert.equal(revoke.requiresAuth, true);
    assert.equal(revoke.minTier, 'professional');
    assert.equal(revoke.category, 'Status & Revocation');
    assert.ok(revoke.sampleBody, 'status-revoke sample body missing');
    const revokeSample = JSON.parse(revoke.sampleBody);
    assert.ok(revokeSample.reason, 'status-revoke sample body missing reason');

    const reinstate = findById('status-reinstate');
    assert.ok(reinstate, 'status-reinstate endpoint missing');
    assert.equal(reinstate.method, 'POST');
    assert.equal(reinstate.path, '/status/documents/{document_id}/reinstate');
    assert.equal(reinstate.requiresAuth, true);
    assert.equal(reinstate.minTier, 'professional');
    assert.equal(reinstate.category, 'Status & Revocation');

    const statusList = findById('status-list');
    assert.ok(statusList, 'status-list endpoint missing');
    assert.equal(statusList.method, 'GET');
    assert.equal(statusList.path, '/status/list/{organization_id}/{list_index}');
    assert.equal(statusList.requiresAuth, false);
    assert.equal(statusList.category, 'Status & Revocation');
  });

  it('includes verify-advanced endpoint with auth + tier metadata', () => {
    const verifyAdvanced = findById('verify-advanced');
    assert.ok(verifyAdvanced, 'verify-advanced endpoint missing');
    assert.equal(verifyAdvanced.method, 'POST');
    assert.equal(verifyAdvanced.path, '/verify/advanced');
    assert.equal(verifyAdvanced.requiresAuth, true);
    assert.equal(verifyAdvanced.authType, 'apikey');
    assert.equal(verifyAdvanced.category, 'Verification');
    assert.equal(verifyAdvanced.minTier, 'professional');
    assert.ok(verifyAdvanced.sampleBody, 'verify-advanced sample body missing');
    const sample = JSON.parse(verifyAdvanced.sampleBody);
    assert.ok(sample.text, 'verify-advanced sample body missing text');
  });

  it('includes streaming endpoints with tier metadata', () => {
    const streamSign = findById('stream-sign');
    assert.ok(streamSign, 'stream-sign endpoint missing');
    assert.equal(streamSign.method, 'POST');
    assert.equal(streamSign.path, '/sign/stream');
    assert.equal(streamSign.requiresAuth, true);
    assert.equal(streamSign.minTier, 'professional');
    assert.equal(streamSign.category, 'Streaming');
    assert.ok(streamSign.sampleBody, 'stream-sign sample body missing');

    const streamChatOpenai = findById('stream-chat-openai');
    assert.ok(streamChatOpenai, 'stream-chat-openai endpoint missing');
    assert.equal(streamChatOpenai.method, 'POST');
    assert.equal(streamChatOpenai.path, '/chat/completions');
    assert.equal(streamChatOpenai.requiresAuth, true);
    assert.equal(streamChatOpenai.minTier, 'professional');
    assert.equal(streamChatOpenai.category, 'Streaming');

    const streamChatHealth = findById('stream-chat-health');
    assert.ok(streamChatHealth, 'stream-chat-health endpoint missing');
    assert.equal(streamChatHealth.method, 'GET');
    assert.equal(streamChatHealth.path, '/chat/health');
    assert.equal(streamChatHealth.requiresAuth, false);
    assert.equal(streamChatHealth.category, 'Streaming');

    const streamSessionCreate = findById('stream-session-create');
    assert.ok(streamSessionCreate, 'stream-session-create endpoint missing');
    assert.equal(streamSessionCreate.method, 'POST');
    assert.equal(streamSessionCreate.path, '/sign/stream/sessions');
    assert.equal(streamSessionCreate.requiresAuth, true);
    assert.equal(streamSessionCreate.minTier, 'professional');
    assert.equal(streamSessionCreate.category, 'Streaming');
  });
});
