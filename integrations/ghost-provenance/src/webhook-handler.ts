import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import pino from 'pino';
import { Config } from './config';
import { Signer } from './signer';

const logger = pino({ name: 'webhook-handler' });

/**
 * Ghost webhook payload structure.
 * Ghost sends a JSON body with the resource nested under its type key.
 */
interface GhostWebhookPayload {
  post?: {
    current?: {
      id: string;
      title: string;
      status: string;
      updated_at: string;
      [key: string]: unknown;
    };
    previous?: {
      id: string;
      status: string;
      updated_at: string;
      [key: string]: unknown;
    };
  };
  page?: {
    current?: {
      id: string;
      title: string;
      status: string;
      updated_at: string;
      [key: string]: unknown;
    };
    previous?: {
      id: string;
      status: string;
      updated_at: string;
      [key: string]: unknown;
    };
  };
}

/**
 * In-flight set to prevent infinite webhook loops.
 *
 * When we update a post via the Ghost Admin API after signing, Ghost fires
 * another `post.published.edited` webhook. We track which posts are currently
 * being processed and skip re-processing.
 *
 * Entries auto-expire after LOCK_TTL_MS to prevent deadlocks if signing fails.
 */
const LOCK_TTL_MS = 60_000; // 1 minute

export class WebhookHandler {
  private config: Config;
  private signer: Signer;
  private inFlight: Map<string, number> = new Map();
  private router: Router;

  constructor(config: Config, signer: Signer) {
    this.config = config;
    this.signer = signer;
    this.router = Router();
    this.setupRoutes();

    // Periodically clean up expired locks
    setInterval(() => this.cleanupExpiredLocks(), 30_000);
  }

  getRouter(): Router {
    return this.router;
  }

  private setupRoutes(): void {
    // Ghost webhook endpoints — one per event type for clarity
    this.router.post('/ghost/post-published', (req, res) => this.handlePostPublished(req, res));
    this.router.post('/ghost/post-updated', (req, res) => this.handlePostUpdated(req, res));
    this.router.post('/ghost/page-published', (req, res) => this.handlePagePublished(req, res));
    this.router.post('/ghost/page-updated', (req, res) => this.handlePageUpdated(req, res));

    // Catch-all for any Ghost webhook (auto-detect event from payload)
    this.router.post('/ghost/webhook', (req, res) => this.handleGenericWebhook(req, res));

    // Manual signing endpoint
    this.router.post('/sign', (req, res) => this.handleManualSign(req, res));

    // Status endpoint
    this.router.get('/status/:postId', (req, res) => this.handleStatus(req, res));

    // Health check
    this.router.get('/health', (_req, res) => {
      res.json({ status: 'ok', inFlight: this.inFlight.size });
    });
  }

  /**
   * Verify webhook secret if configured.
   */
  private verifyWebhookSecret(req: Request): boolean {
    if (!this.config.webhookSecret) return true;

    const signature = req.headers['x-ghost-signature'] as string;
    if (!signature) {
      logger.warn('Webhook received without signature');
      return false;
    }

    // Ghost webhook signatures use HMAC-SHA256
    const body = JSON.stringify(req.body);
    const expected = crypto
      .createHmac('sha256', this.config.webhookSecret)
      .update(body)
      .digest('hex');

    const parts = signature.split(',');
    const sigPart = parts.find(p => p.startsWith('sha256='));
    if (!sigPart) return false;

    const actual = sigPart.replace('sha256=', '');
    return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(actual));
  }

  /**
   * Acquire a lock for a post ID. Returns true if lock acquired.
   */
  private acquireLock(postId: string): boolean {
    const existing = this.inFlight.get(postId);
    if (existing && Date.now() - existing < LOCK_TTL_MS) {
      return false; // Already being processed
    }
    this.inFlight.set(postId, Date.now());
    return true;
  }

  /**
   * Release a lock for a post ID.
   */
  private releaseLock(postId: string): void {
    this.inFlight.delete(postId);
  }

  /**
   * Clean up expired locks.
   */
  private cleanupExpiredLocks(): void {
    const now = Date.now();
    for (const [postId, timestamp] of this.inFlight.entries()) {
      if (now - timestamp >= LOCK_TTL_MS) {
        logger.warn({ postId }, 'Cleaning up expired lock');
        this.inFlight.delete(postId);
      }
    }
  }

  /**
   * Extract post ID from webhook payload.
   */
  private extractPostId(payload: GhostWebhookPayload, type: 'post' | 'page'): string | null {
    const resource = type === 'page' ? payload.page : payload.post;
    return resource?.current?.id || null;
  }

  /**
   * Process a signing request for a post/page.
   */
  private async processSign(postId: string, postType: 'post' | 'page', eventName: string): Promise<void> {
    if (!this.acquireLock(postId)) {
      logger.info({ postId, eventName }, 'Post already being processed, skipping (loop prevention)');
      return;
    }

    try {
      logger.info({ postId, postType, eventName }, 'Processing webhook event');
      const result = await this.signer.signPost(postId, postType);

      if (result.success) {
        logger.info({
          postId,
          documentId: result.documentId,
          actionType: result.actionType,
          totalSegments: result.totalSegments,
        }, 'Signing completed successfully');
      } else {
        logger.error({ postId, error: result.error }, 'Signing failed');
      }
    } catch (err) {
      logger.error({ postId, err }, 'Unexpected error during signing');
    } finally {
      this.releaseLock(postId);
    }
  }

  // =========================================================================
  // Route handlers
  // =========================================================================

  private async handlePostPublished(req: Request, res: Response): Promise<void> {
    if (!this.verifyWebhookSecret(req)) {
      res.status(401).json({ error: 'Invalid webhook signature' });
      return;
    }

    if (!this.config.signing.autoSignOnPublish) {
      res.json({ status: 'skipped', reason: 'auto_sign_on_publish disabled' });
      return;
    }

    const postId = this.extractPostId(req.body, 'post');
    if (!postId) {
      res.status(400).json({ error: 'No post ID in payload' });
      return;
    }

    // Respond immediately, process async
    res.json({ status: 'accepted', postId });

    // Fire and forget — don't block the webhook response
    this.processSign(postId, 'post', 'post.published').catch(err => {
      logger.error({ postId, err }, 'Background signing failed');
    });
  }

  private async handlePostUpdated(req: Request, res: Response): Promise<void> {
    if (!this.verifyWebhookSecret(req)) {
      res.status(401).json({ error: 'Invalid webhook signature' });
      return;
    }

    if (!this.config.signing.autoSignOnUpdate) {
      res.json({ status: 'skipped', reason: 'auto_sign_on_update disabled' });
      return;
    }

    const postId = this.extractPostId(req.body, 'post');
    if (!postId) {
      res.status(400).json({ error: 'No post ID in payload' });
      return;
    }

    res.json({ status: 'accepted', postId });

    this.processSign(postId, 'post', 'post.published.edited').catch(err => {
      logger.error({ postId, err }, 'Background signing failed');
    });
  }

  private async handlePagePublished(req: Request, res: Response): Promise<void> {
    if (!this.verifyWebhookSecret(req)) {
      res.status(401).json({ error: 'Invalid webhook signature' });
      return;
    }

    if (!this.config.signing.autoSignOnPublish) {
      res.json({ status: 'skipped', reason: 'auto_sign_on_publish disabled' });
      return;
    }

    const postId = this.extractPostId(req.body, 'page');
    if (!postId) {
      res.status(400).json({ error: 'No page ID in payload' });
      return;
    }

    res.json({ status: 'accepted', postId });

    this.processSign(postId, 'page', 'page.published').catch(err => {
      logger.error({ postId, err }, 'Background signing failed');
    });
  }

  private async handlePageUpdated(req: Request, res: Response): Promise<void> {
    if (!this.verifyWebhookSecret(req)) {
      res.status(401).json({ error: 'Invalid webhook signature' });
      return;
    }

    if (!this.config.signing.autoSignOnUpdate) {
      res.json({ status: 'skipped', reason: 'auto_sign_on_update disabled' });
      return;
    }

    const postId = this.extractPostId(req.body, 'page');
    if (!postId) {
      res.status(400).json({ error: 'No page ID in payload' });
      return;
    }

    res.json({ status: 'accepted', postId });

    this.processSign(postId, 'page', 'page.published.edited').catch(err => {
      logger.error({ postId, err }, 'Background signing failed');
    });
  }

  /**
   * Generic webhook handler that auto-detects the event type from the payload.
   * Useful when configuring a single webhook URL for all events.
   */
  private async handleGenericWebhook(req: Request, res: Response): Promise<void> {
    if (!this.verifyWebhookSecret(req)) {
      res.status(401).json({ error: 'Invalid webhook signature' });
      return;
    }

    const payload = req.body as GhostWebhookPayload;

    if (payload.post?.current) {
      const postId = payload.post.current.id;
      if (payload.post.current.status === 'published') {
        res.json({ status: 'accepted', postId, type: 'post' });
        this.processSign(postId, 'post', 'generic.post').catch(err => {
          logger.error({ postId, err }, 'Background signing failed');
        });
        return;
      }
    }

    if (payload.page?.current) {
      const pageId = payload.page.current.id;
      if (payload.page.current.status === 'published') {
        res.json({ status: 'accepted', postId: pageId, type: 'page' });
        this.processSign(pageId, 'page', 'generic.page').catch(err => {
          logger.error({ postId: pageId, err }, 'Background signing failed');
        });
        return;
      }
    }

    res.json({ status: 'ignored', reason: 'No published post/page in payload' });
  }

  /**
   * Manual signing endpoint — trigger signing for a specific post/page.
   */
  private async handleManualSign(req: Request, res: Response): Promise<void> {
    const { postId, postType } = req.body as { postId?: string; postType?: string };

    if (!postId) {
      res.status(400).json({ error: 'postId is required' });
      return;
    }

    const type = (postType === 'page' ? 'page' : 'post') as 'post' | 'page';

    if (!this.acquireLock(postId)) {
      res.status(409).json({ error: 'Post is already being signed' });
      return;
    }

    try {
      const result = await this.signer.signPost(postId, type);
      res.json(result);
    } catch (err) {
      logger.error({ postId, err }, 'Manual signing failed');
      res.status(500).json({ error: `Signing failed: ${err}` });
    } finally {
      this.releaseLock(postId);
    }
  }

  /**
   * Get signing status for a post.
   */
  private handleStatus(req: Request, res: Response): void {
    const postId = req.params.postId as string;
    res.json({
      postId,
      inFlight: this.inFlight.has(postId),
    });
  }
}
