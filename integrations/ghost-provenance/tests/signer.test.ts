import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Signer } from '../src/signer';
import { Config } from '../src/config';
import { GhostClient, GhostPost } from '../src/ghost-client';
import { EncypherClient } from '../src/encypher-client';
import { MetadataStore } from '../src/metadata-store';

function makeConfig(): Config {
  return {
    ghost: { url: 'http://localhost:2368', adminApiKey: 'ghost-key', apiVersion: 'v5.0' },
    encypher: { apiBaseUrl: 'http://localhost:8000/api/v1', apiKey: 'ency-key' },
    server: { port: 3000, logLevel: 'silent' },
    signing: {
      autoSignOnPublish: true,
      autoSignOnUpdate: true,
      tier: 'free',
      organizationName: 'Test Org',
      signingMode: 'managed',
      manifestMode: 'micro',
      segmentationLevel: 'sentence',
      ecc: true,
      embedC2pa: true,
    },
    webhookSecret: '',
    dbPath: ':memory:',
    badge: { enabled: false, verifyBaseUrl: 'https://verify.encypherai.com' },
  };
}

function c2paMagicMarker(): string {
  const magicBytes = [0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00];
  return magicBytes
    .map((b) => (b < 16 ? String.fromCodePoint(0xfe00 + b) : String.fromCodePoint(0xe0100 + (b - 16))))
    .join('');
}

function makePost(overrides: Partial<GhostPost> = {}): GhostPost {
  return {
    id: 'post_123',
    uuid: 'uuid_123',
    title: 'Test Post',
    slug: 'test-post',
    html: '<p>Hello world.</p>',
    status: 'published',
    visibility: 'public',
    created_at: '2026-01-01T00:00:00.000Z',
    updated_at: '2026-01-01T00:00:00.000Z',
    published_at: '2026-01-01T00:00:00.000Z',
    url: 'http://localhost:2368/test-post/',
    excerpt: 'Excerpt',
    codeinjection_head: null,
    codeinjection_foot: null,
    tags: [],
    authors: [],
    primary_author: null,
    primary_tag: null,
    ...overrides,
  };
}

describe('Signer embedding plan flow', () => {
  let ghostClient: GhostClient;
  let encypherClient: EncypherClient;
  let metadataStore: MetadataStore;
  let signer: Signer;

  beforeEach(() => {
    ghostClient = {
      readPost: vi.fn(),
      readPage: vi.fn(),
      updatePostHtml: vi.fn(),
      updatePageHtml: vi.fn(),
    } as unknown as GhostClient;

    encypherClient = {
      sign: vi.fn(),
    } as unknown as EncypherClient;

    metadataStore = {
      hasContentChanged: vi.fn().mockReturnValue(true),
      getLatestRecord: vi.fn().mockReturnValue(null),
      recordSigning: vi.fn(),
    } as unknown as MetadataStore;

    signer = new Signer(makeConfig(), ghostClient, encypherClient, metadataStore);
  });

  it('requests return_embedding_plan=true and uses embedding plan when signed_text is absent', async () => {
    const initialPost = makePost();
    (ghostClient.readPost as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(initialPost)
      .mockResolvedValueOnce(initialPost);

    const marker = c2paMagicMarker();
    (encypherClient.sign as ReturnType<typeof vi.fn>).mockResolvedValue({
      success: true,
      data: {
        document: {
          document_id: 'doc_1',
          instance_id: 'inst_1',
          total_segments: 1,
          embedding_plan: {
            index_unit: 'codepoint',
            operations: [{ insert_after_index: 4, marker }],
          },
        },
      },
    });

    const result = await signer.signPost('post_123', 'post');

    expect(result.success).toBe(true);
    expect(encypherClient.sign).toHaveBeenCalledTimes(1);
    const signPayload = (encypherClient.sign as ReturnType<typeof vi.fn>).mock.calls[0][0];
    expect(signPayload.options.manifest_mode).toBe('micro');
    expect(signPayload.options.segmentation_level).toBe('sentence');
    expect(signPayload.options.ecc).toBe(true);
    expect(signPayload.options.embed_c2pa).toBe(true);
    expect(signPayload.options.return_embedding_plan).toBe(true);

    expect(ghostClient.updatePostHtml).toHaveBeenCalledTimes(1);
    const updatedHtml = (ghostClient.updatePostHtml as ReturnType<typeof vi.fn>).mock.calls[0][1] as string;
    expect(updatedHtml).toContain(marker);
  });

  it('falls back to signed_text when embedding plan is invalid', async () => {
    const initialPost = makePost();
    (ghostClient.readPost as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(initialPost)
      .mockResolvedValueOnce(initialPost);

    const fallbackSignedText = `Hello ${c2paMagicMarker()}world.`;
    (encypherClient.sign as ReturnType<typeof vi.fn>).mockResolvedValue({
      success: true,
      data: {
        document: {
          document_id: 'doc_2',
          instance_id: 'inst_2',
          total_segments: 1,
          signed_text: fallbackSignedText,
          embedding_plan: {
            index_unit: 'codepoint',
            operations: [{ insert_after_index: 9999, marker: c2paMagicMarker() }],
          },
        },
      },
    });

    const result = await signer.signPost('post_123', 'post');

    expect(result.success).toBe(true);
    expect(ghostClient.updatePostHtml).toHaveBeenCalledTimes(1);
    const updatedHtml = (ghostClient.updatePostHtml as ReturnType<typeof vi.fn>).mock.calls[0][1] as string;
    expect(updatedHtml).toContain(c2paMagicMarker());
  });

  it('normalizes legacy micro_ecc_c2pa manifest mode to canonical micro options', async () => {
    signer = new Signer(
      makeConfig({
        signing: {
          ...makeConfig().signing,
          manifestMode: 'micro_ecc_c2pa',
          ecc: false,
          embedC2pa: false,
        },
      }),
      ghostClient,
      encypherClient,
      metadataStore
    );

    const initialPost = makePost();
    (ghostClient.readPost as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(initialPost)
      .mockResolvedValueOnce(initialPost);

    (encypherClient.sign as ReturnType<typeof vi.fn>).mockResolvedValue({
      success: true,
      data: {
        document: {
          document_id: 'doc_legacy',
          instance_id: 'inst_legacy',
          total_segments: 1,
          signed_text: `Hello ${c2paMagicMarker()}world.`,
        },
      },
    });

    const result = await signer.signPost('post_123', 'post');

    expect(result.success).toBe(true);
    const signPayload = (encypherClient.sign as ReturnType<typeof vi.fn>).mock.calls[0][0];
    expect(signPayload.options.manifest_mode).toBe('micro');
    expect(signPayload.options.ecc).toBe(true);
    expect(signPayload.options.embed_c2pa).toBe(true);
  });
});
