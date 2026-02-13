import crypto from 'crypto';
import pino from 'pino';
import { Config } from './config';
import { GhostClient, GhostPost } from './ghost-client';
import { EncypherClient } from './encypher-client';
import { MetadataStore } from './metadata-store';
import {
  extractText,
  embedSignedText,
  stripC2paEmbeddings,
  detectC2paEmbeddings,
} from './html-utils';
import { generateBadgeScript, mergeBadgeInjection } from './badge-injector';

const logger = pino({ name: 'signer' });

const PLUGIN_VERSION = '1.0.0';

export interface SignResult {
  success: boolean;
  documentId: string;
  instanceId: string;
  totalSegments: number;
  actionType: string;
  error?: string;
}

export class Signer {
  private config: Config;
  private ghostClient: GhostClient;
  private encypherClient: EncypherClient;
  private metadataStore: MetadataStore;

  constructor(
    config: Config,
    ghostClient: GhostClient,
    encypherClient: EncypherClient,
    metadataStore: MetadataStore,
  ) {
    this.config = config;
    this.ghostClient = ghostClient;
    this.encypherClient = encypherClient;
    this.metadataStore = metadataStore;
  }

  /**
   * Sign a Ghost post or page.
   *
   * Full flow:
   * 1. Read post from Ghost Admin API
   * 2. Strip any existing C2PA embeddings
   * 3. Extract plain text from HTML
   * 4. Determine action type (created vs edited)
   * 5. Call Encypher Enterprise API /sign
   * 6. Embed signed text back into HTML
   * 7. Update post in Ghost via Admin API
   * 8. Record signing metadata
   */
  async signPost(postId: string, postType: 'post' | 'page' = 'post'): Promise<SignResult> {
    // 1. Read post from Ghost
    let post: GhostPost;
    try {
      post = postType === 'page'
        ? await this.ghostClient.readPage(postId)
        : await this.ghostClient.readPost(postId);
    } catch (err) {
      logger.error({ postId, postType, err }, 'Failed to read post from Ghost');
      return { success: false, documentId: '', instanceId: '', totalSegments: 0, actionType: '', error: `Failed to read ${postType}: ${err}` };
    }

    if (!post.html || post.html.trim() === '') {
      logger.warn({ postId }, 'Post has no HTML content');
      return { success: false, documentId: '', instanceId: '', totalSegments: 0, actionType: '', error: 'Post has no content' };
    }

    // 2. Strip any existing C2PA embeddings
    let cleanHtml = post.html;
    const existingEmbeddings = detectC2paEmbeddings(cleanHtml);
    if (existingEmbeddings.count > 0) {
      logger.info({ postId, count: existingEmbeddings.count }, 'Stripping existing C2PA embeddings before re-signing');
      cleanHtml = stripC2paEmbeddings(cleanHtml);

      // Verify stripping was successful
      const verifyClean = detectC2paEmbeddings(cleanHtml);
      if (verifyClean.count > 0) {
        return { success: false, documentId: '', instanceId: '', totalSegments: 0, actionType: '', error: 'Failed to strip existing C2PA embeddings' };
      }
    }

    // 3. Extract plain text from HTML
    const extractedText = extractText(cleanHtml);
    if (extractedText.trim() === '') {
      logger.warn({ postId }, 'No text content found in post');
      return { success: false, documentId: '', instanceId: '', totalSegments: 0, actionType: '', error: 'No text content found' };
    }

    const contentHash = crypto.createHash('md5').update(extractedText).digest('hex');

    // Check if content has changed since last signing
    if (!this.metadataStore.hasContentChanged(postId, contentHash)) {
      logger.info({ postId }, 'Content unchanged since last signing, skipping');
      const latest = this.metadataStore.getLatestRecord(postId);
      return {
        success: true,
        documentId: latest?.document_id || '',
        instanceId: latest?.instance_id || '',
        totalSegments: latest?.total_segments || 0,
        actionType: 'skipped',
      };
    }

    // 4. Determine action type
    const previousRecord = this.metadataStore.getLatestRecord(postId);
    const actionType = previousRecord ? 'c2pa.edited' : 'c2pa.created';
    const previousInstanceId = previousRecord?.instance_id || null;

    // 5. Generate unique document_id
    const uniqueDocumentId = `ghost_${postType}_${postId}_v${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;

    logger.info({
      postId,
      postType,
      actionType,
      textLength: extractedText.length,
      htmlLength: cleanHtml.length,
    }, 'Signing post');

    // 6. Build and send signing request
    const authorName = post.primary_author?.name || post.authors?.[0]?.name || 'Unknown';

    // Preserve user's existing tags and add encypher-signed tag
    const existingTags = (post.tags || []).map(t => ({ id: t.id, name: t.name, slug: t.slug }));
    const hasEncypherTag = existingTags.some(t => t.slug === 'hash-encypher-signed');

    const signPayload = {
      text: extractedText,
      document_id: uniqueDocumentId,
      document_title: post.title,
      document_url: post.url,
      metadata: {
        author: authorName,
        published_at: post.published_at,
        ghost_post_id: postId,
        ghost_post_type: postType,
        tier: this.config.signing.tier,
        organization_name: this.config.signing.organizationName,
        signing_mode: this.config.signing.signingMode,
        // Pass through Ghost tags as metadata for the Enterprise API
        tags: (post.tags || []).map(t => t.name),
      },
      options: {
        document_type: 'article',
        claim_generator: `Ghost/Encypher Integration v${PLUGIN_VERSION}`,
        action: actionType,
        manifest_mode: this.config.signing.manifestMode,
        segmentation_level: this.config.signing.segmentationLevel,
        index_for_attribution: true,
        ...(previousInstanceId ? { previous_instance_id: previousInstanceId } : {}),
      },
    };

    let signResponse;
    try {
      signResponse = await this.encypherClient.sign(signPayload);
    } catch (err) {
      logger.error({ postId, err }, 'Encypher API signing failed');
      return { success: false, documentId: '', instanceId: '', totalSegments: 0, actionType, error: `Signing API error: ${err}` };
    }

    // 7. Extract signed text from response
    const signedText = EncypherClient.extractSignedText(signResponse);
    if (!signedText) {
      logger.error({ postId }, 'No signed text in API response');
      return { success: false, documentId: '', instanceId: '', totalSegments: 0, actionType, error: 'No signed text in API response' };
    }

    // Verify C2PA compliance
    const c2paCheck = detectC2paEmbeddings(signedText);
    if (c2paCheck.count < 1) {
      logger.error({ postId, count: c2paCheck.count }, 'C2PA compliance violation');
      return { success: false, documentId: '', instanceId: '', totalSegments: 0, actionType, error: `C2PA compliance check failed: found ${c2paCheck.count} wrappers` };
    }

    // 8. Embed signed text back into HTML
    const embeddedHtml = embedSignedText(cleanHtml, signedText);

    logger.info({
      postId,
      embeddedHtmlLength: embeddedHtml.length,
      signedTextLength: signedText.length,
    }, 'Embedded signed text into HTML');

    // 9. Prepare update options
    const { documentId, instanceId, totalSegments } = EncypherClient.extractMetadata(signResponse);

    const updateOptions: {
      codeinjectionFoot?: string;
      tags?: Array<{ id?: string; name: string; slug?: string }>;
    } = {};

    // Add verification badge if enabled
    if (this.config.badge.enabled) {
      const badgeScript = generateBadgeScript(this.config, documentId, instanceId);
      updateOptions.codeinjectionFoot = mergeBadgeInjection(post.codeinjection_foot, badgeScript);
    }

    // Add #encypher-signed internal tag if not already present
    if (!hasEncypherTag) {
      updateOptions.tags = [
        ...existingTags,
        { name: '#encypher-signed' },
      ];
    }

    // 10. Update post in Ghost
    try {
      // Re-read the post to get the latest updated_at (it may have changed)
      const freshPost = postType === 'page'
        ? await this.ghostClient.readPage(postId)
        : await this.ghostClient.readPost(postId);

      if (postType === 'page') {
        await this.ghostClient.updatePageHtml(postId, embeddedHtml, freshPost.updated_at, updateOptions);
      } else {
        await this.ghostClient.updatePostHtml(postId, embeddedHtml, freshPost.updated_at, updateOptions);
      }
    } catch (err) {
      logger.error({ postId, err }, 'Failed to update post in Ghost');
      return { success: false, documentId, instanceId, totalSegments, actionType, error: `Ghost update failed: ${err}` };
    }

    // 11. Record signing metadata
    this.metadataStore.recordSigning({
      ghost_post_id: postId,
      ghost_post_type: postType,
      document_id: documentId,
      instance_id: instanceId,
      content_hash: contentHash,
      action_type: actionType,
      total_segments: totalSegments,
      signed_at: new Date().toISOString(),
      previous_instance_id: previousInstanceId,
    });

    logger.info({
      postId,
      documentId,
      instanceId,
      totalSegments,
      actionType,
    }, 'Post signed successfully');

    return {
      success: true,
      documentId,
      instanceId,
      totalSegments,
      actionType,
    };
  }
}
