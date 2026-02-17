import { describe, it, expect, vi, beforeEach } from 'vitest';
import express from 'express';
import { WebhookHandler } from '../src/webhook-handler';
import { Config } from '../src/config';
import { Signer, SignResult } from '../src/signer';

// Minimal config for testing
function makeConfig(overrides: Partial<Config> = {}): Config {
  return {
    ghost: { url: 'http://localhost:2368', adminApiKey: 'test-key', apiVersion: 'v5.0' },
    encypher: { apiBaseUrl: 'http://localhost:8000/api/v1', apiKey: 'test-key' },
    server: { port: 3000, logLevel: 'silent' },
    signing: {
      autoSignOnPublish: true,
      autoSignOnUpdate: true,
      tier: 'free',
      organizationName: '',
      signingMode: 'managed',
      manifestMode: 'micro',
      segmentationLevel: 'sentence',
      ecc: true,
      embedC2pa: true,
    },
    webhookSecret: '',
    dbPath: ':memory:',
    badge: { enabled: false, verifyBaseUrl: 'https://verify.encypherai.com' },
    ...overrides,
  };
}

// Mock signer
function makeMockSigner(): Signer {
  return {
    signPost: vi.fn().mockResolvedValue({
      success: true,
      documentId: 'doc_123',
      instanceId: 'inst_123',
      totalSegments: 5,
      actionType: 'c2pa.created',
    } as SignResult),
  } as unknown as Signer;
}

// Helper to make a supertest-like request
async function postJson(app: express.Express, path: string, body: unknown): Promise<{ status: number; body: unknown }> {
  return new Promise((resolve) => {
    const server = app.listen(0, () => {
      const addr = server.address();
      const port = typeof addr === 'object' && addr ? addr.port : 0;
      fetch(`http://localhost:${port}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
        .then(async (res) => {
          const json = await res.json();
          server.close();
          resolve({ status: res.status, body: json });
        })
        .catch(() => {
          server.close();
          resolve({ status: 500, body: {} });
        });
    });
  });
}

async function getJson(app: express.Express, path: string): Promise<{ status: number; body: unknown }> {
  return new Promise((resolve) => {
    const server = app.listen(0, () => {
      const addr = server.address();
      const port = typeof addr === 'object' && addr ? addr.port : 0;
      fetch(`http://localhost:${port}${path}`)
        .then(async (res) => {
          const json = await res.json();
          server.close();
          resolve({ status: res.status, body: json });
        })
        .catch(() => {
          server.close();
          resolve({ status: 500, body: {} });
        });
    });
  });
}

describe('WebhookHandler', () => {
  let config: Config;
  let mockSigner: Signer;
  let handler: WebhookHandler;
  let app: express.Express;

  beforeEach(() => {
    config = makeConfig();
    mockSigner = makeMockSigner();
    handler = new WebhookHandler(config, mockSigner);
    app = express();
    app.use(express.json());
    app.use('/api', handler.getRouter());
  });

  describe('health endpoint', () => {
    it('returns ok status', async () => {
      const res = await getJson(app, '/api/health');
      expect(res.status).toBe(200);
      expect((res.body as Record<string, unknown>).status).toBe('ok');
    });
  });

  describe('post.published webhook', () => {
    it('accepts valid post.published webhook', async () => {
      const payload = {
        post: {
          current: {
            id: 'abc123',
            title: 'Test Post',
            status: 'published',
            updated_at: '2025-01-01T00:00:00.000Z',
          },
        },
      };

      const res = await postJson(app, '/api/ghost/post-published', payload);
      expect(res.status).toBe(200);
      expect((res.body as Record<string, unknown>).status).toBe('accepted');
      expect((res.body as Record<string, unknown>).postId).toBe('abc123');

      // Give async signing a moment to fire
      await new Promise(r => setTimeout(r, 100));
      expect(mockSigner.signPost).toHaveBeenCalledWith('abc123', 'post');
    });

    it('returns 400 when no post ID in payload', async () => {
      const res = await postJson(app, '/api/ghost/post-published', {});
      expect(res.status).toBe(400);
    });

    it('skips when auto_sign_on_publish is disabled', async () => {
      config = makeConfig({ signing: { ...makeConfig().signing, autoSignOnPublish: false } });
      handler = new WebhookHandler(config, mockSigner);
      app = express();
      app.use(express.json());
      app.use('/api', handler.getRouter());

      const payload = {
        post: { current: { id: 'abc123', title: 'Test', status: 'published', updated_at: '2025-01-01T00:00:00.000Z' } },
      };

      const res = await postJson(app, '/api/ghost/post-published', payload);
      expect(res.status).toBe(200);
      expect((res.body as Record<string, unknown>).status).toBe('skipped');
    });
  });

  describe('generic webhook', () => {
    it('auto-detects post type from payload', async () => {
      const payload = {
        post: {
          current: { id: 'post_456', title: 'Generic Post', status: 'published', updated_at: '2025-01-01T00:00:00.000Z' },
        },
      };

      const res = await postJson(app, '/api/ghost/webhook', payload);
      expect(res.status).toBe(200);
      expect((res.body as Record<string, unknown>).type).toBe('post');

      await new Promise(r => setTimeout(r, 100));
      expect(mockSigner.signPost).toHaveBeenCalledWith('post_456', 'post');
    });

    it('auto-detects page type from payload', async () => {
      const payload = {
        page: {
          current: { id: 'page_789', title: 'Generic Page', status: 'published', updated_at: '2025-01-01T00:00:00.000Z' },
        },
      };

      const res = await postJson(app, '/api/ghost/webhook', payload);
      expect(res.status).toBe(200);
      expect((res.body as Record<string, unknown>).type).toBe('page');

      await new Promise(r => setTimeout(r, 100));
      expect(mockSigner.signPost).toHaveBeenCalledWith('page_789', 'page');
    });

    it('ignores non-published content', async () => {
      const payload = {
        post: {
          current: { id: 'draft_123', title: 'Draft', status: 'draft', updated_at: '2025-01-01T00:00:00.000Z' },
        },
      };

      const res = await postJson(app, '/api/ghost/webhook', payload);
      expect(res.status).toBe(200);
      expect((res.body as Record<string, unknown>).status).toBe('ignored');
    });
  });

  describe('manual sign endpoint', () => {
    it('triggers signing for a specific post', async () => {
      const res = await postJson(app, '/api/sign', { postId: 'manual_123', postType: 'post' });
      expect(res.status).toBe(200);
      expect((res.body as Record<string, unknown>).success).toBe(true);
      expect(mockSigner.signPost).toHaveBeenCalledWith('manual_123', 'post');
    });

    it('returns 400 when postId is missing', async () => {
      const res = await postJson(app, '/api/sign', {});
      expect(res.status).toBe(400);
    });

    it('defaults to post type when postType not specified', async () => {
      const res = await postJson(app, '/api/sign', { postId: 'default_type' });
      expect(res.status).toBe(200);
      expect(mockSigner.signPost).toHaveBeenCalledWith('default_type', 'post');
    });
  });

  describe('loop prevention', () => {
    it('prevents concurrent signing of the same post', async () => {
      // Make signer slow
      (mockSigner.signPost as ReturnType<typeof vi.fn>).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          success: true, documentId: 'doc', instanceId: 'inst', totalSegments: 1, actionType: 'c2pa.created',
        }), 500))
      );

      const payload = {
        post: { current: { id: 'concurrent_123', title: 'Test', status: 'published', updated_at: '2025-01-01T00:00:00.000Z' } },
      };

      // Fire two webhooks rapidly
      const [res1, res2] = await Promise.all([
        postJson(app, '/api/ghost/post-published', payload),
        postJson(app, '/api/ghost/post-published', payload),
      ]);

      // Both should return accepted (webhook responds immediately)
      expect(res1.status).toBe(200);
      expect(res2.status).toBe(200);

      // Wait for async processing
      await new Promise(r => setTimeout(r, 700));

      // Signer should only be called once (second was skipped by loop prevention)
      expect(mockSigner.signPost).toHaveBeenCalledTimes(1);
    });
  });
});
