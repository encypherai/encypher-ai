import { describe, it, expect } from 'vitest';
import { loadConfig } from '../src/config';
import { GhostClient } from '../src/ghost-client';
import { detectC2paEmbeddings, extractTextForVerify } from '../src/html-utils';

const shouldRun = process.env.RUN_LOCAL_GHOST_REPLAY === '1';

const describeLocal = shouldRun ? describe : describe.skip;

const htmlCardWrapperRe = /<!--\s*kg-card-begin:\s*html\s*-->[\s\S]*?<!--\s*kg-card-end:\s*html\s*-->/giu;

function normalizeMarkupForContainment(html: string): string {
  return html.replace(/\s+/g, '');
}

interface ReplayFixture {
  name: string;
  html: string;
}

const fixtures: ReplayFixture[] = [
  {
    name: 'duplicate text with source=html wrapper',
    html:
      '<!--kg-card-begin: html--><p>Hello world.</p><!--kg-card-end: html-->'
      + '<p>Hello world.</p>',
  },
  {
    name: 'entity-heavy paragraph split',
    html: '<p>As Co-Chair &mdash; proof.</p><p>Next sentence.</p>',
  },
  {
    name: 'skip-card + visible duplicate',
    html: '<div class="kg-card kg-code-card"><pre><code>Hello world.</code></pre></div><p>Hello world.</p>',
  },
  {
    name: 'lexical-mobiledoc migrated wrappers',
    html:
      '<!--kg-card-begin: markdown--><p>Rendered markdown text survives migration.</p><!--kg-card-end: markdown-->'
      + '<div class="kg-card kg-callout-card"><div class="kg-callout-text"><span data-lexical-text="true">Lexical callout text.</span></div></div>'
      + '<div class="kg-card kg-html-card"><div>Raw html-card source must be skipped.</div></div>',
  },
  {
    name: 'malformed html recovery',
    html: '<div><p>Start <strong>bold<p>Next line &amp; trailing',
  },
  {
    name: 'unicode grapheme zwj sequence',
    html: '<p>Emoji family 👨‍👩‍👧‍👦 stays intact.</p>',
  },
];

async function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function resolveReplayPostId(ghost: GhostClient): Promise<string> {
  const explicitPostId = process.env.LOCAL_GHOST_REPLAY_POST_ID;
  if (explicitPostId) return explicitPostId;

  const seeded = await ghost.createPostHtml(
    `[replay] ${new Date().toISOString()}`,
    '<p>Replay seed post.</p>',
    'published'
  );
  return seeded.id;
}

describeLocal('local Ghost replay hardening', () => {
  it('replays edge-case fixtures through local Ghost + integration service', async () => {
    const signerBaseUrl = process.env.LOCAL_GHOST_PROVENANCE_URL || 'http://localhost:3100';

    const config = loadConfig();
    if (!config.ghost.adminApiKey) {
      throw new Error('GHOST_ADMIN_API_KEY is required when RUN_LOCAL_GHOST_REPLAY=1');
    }

    expect(config.signing.manifestMode).toBe('micro');
    expect(config.signing.segmentationLevel).toBe('sentence');
    expect(config.signing.ecc).toBe(true);
    expect(config.signing.embedC2pa).toBe(true);

    const ghost = new GhostClient(config);
    const postId = await resolveReplayPostId(ghost);

    for (const fixture of fixtures) {
      const before = await ghost.readPost(postId);
      await ghost.updatePostHtml(postId, fixture.html, before.updated_at, {
        tags: before.tags.map((t) => ({ id: t.id, name: t.name, slug: t.slug })),
      });

      const signResp = await fetch(`${signerBaseUrl}/api/sign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ postId, postType: 'post' }),
      });

      expect(signResp.ok, `manual sign failed for fixture: ${fixture.name}`).toBe(true);
      const signData = await signResp.json() as { success?: boolean; error?: string };
      expect(signData.success, `${fixture.name}: ${signData.error || 'sign response reported failure'}`).toBe(true);

      await wait(300);
      const after = await ghost.readPost(postId);

      const verifyText = extractTextForVerify(after.html || '');
      const markerInfo = detectC2paEmbeddings(verifyText);
      expect(markerInfo.count, `no C2PA markers found for fixture: ${fixture.name}`).toBeGreaterThan(0);

      const wrapperMatches = (fixture.html.match(htmlCardWrapperRe) || []);
      const normalizedAfterHtml = normalizeMarkupForContainment(after.html);
      for (const wrapper of wrapperMatches) {
        const normalizedWrapper = normalizeMarkupForContainment(wrapper);
        expect(normalizedAfterHtml).toContain(normalizedWrapper);
      }
    }
  }, 45_000);
});
