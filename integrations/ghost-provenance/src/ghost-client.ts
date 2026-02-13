import GhostAdminAPI from '@tryghost/admin-api';
import pino from 'pino';
import { Config } from './config';

const logger = pino({ name: 'ghost-client' });

export interface GhostPost {
  id: string;
  uuid: string;
  title: string;
  slug: string;
  html: string;
  status: string;
  visibility: string;
  created_at: string;
  updated_at: string;
  published_at: string;
  url: string;
  excerpt: string;
  codeinjection_head: string | null;
  codeinjection_foot: string | null;
  tags: Array<{ id: string; name: string; slug: string }>;
  authors: Array<{ id: string; name: string; slug: string; email: string }>;
  primary_author: { id: string; name: string; slug: string; email: string } | null;
  primary_tag: { id: string; name: string; slug: string } | null;
}

export class GhostClient {
  private api: InstanceType<typeof GhostAdminAPI> | null = null;
  private config: Config;

  constructor(config: Config) {
    this.config = config;
    // Defer API client creation — @tryghost/admin-api validates the key
    // format eagerly in the constructor, so we can't create it without a
    // valid key. The client is lazily initialized on first use.
    if (config.ghost.adminApiKey) {
      this.api = new GhostAdminAPI({
        url: config.ghost.url,
        key: config.ghost.adminApiKey,
        version: config.ghost.apiVersion,
      });
    }
  }

  private getApi(): InstanceType<typeof GhostAdminAPI> {
    if (!this.api) {
      if (!this.config.ghost.adminApiKey) {
        throw new Error('GHOST_ADMIN_API_KEY is not configured. Set it and restart the service.');
      }
      this.api = new GhostAdminAPI({
        url: this.config.ghost.url,
        key: this.config.ghost.adminApiKey,
        version: this.config.ghost.apiVersion,
      });
    }
    return this.api;
  }

  /**
   * Read a single post by ID, including HTML content and tags.
   */
  async readPost(postId: string): Promise<GhostPost> {
    logger.debug({ postId }, 'Reading post from Ghost');
    const post = await this.getApi().posts.read(
      { id: postId },
      { formats: 'html', include: 'tags,authors' }
    );
    return post as GhostPost;
  }

  /**
   * Read a single page by ID, including HTML content and tags.
   */
  async readPage(pageId: string): Promise<GhostPost> {
    logger.debug({ pageId }, 'Reading page from Ghost');
    const page = await this.getApi().pages.read(
      { id: pageId },
      { formats: 'html', include: 'tags,authors' }
    );
    return page as GhostPost;
  }

  /**
   * Update a post's HTML content. Requires the current updated_at timestamp
   * to prevent conflicts.
   */
  async updatePostHtml(
    postId: string,
    html: string,
    updatedAt: string,
    options?: {
      codeinjectionFoot?: string;
      tags?: Array<{ id?: string; name: string; slug?: string }>;
    }
  ): Promise<GhostPost> {
    logger.debug({ postId }, 'Updating post HTML in Ghost');

    const updatePayload: Record<string, unknown> = {
      id: postId,
      html,
      updated_at: updatedAt,
    };

    if (options?.codeinjectionFoot !== undefined) {
      updatePayload.codeinjection_foot = options.codeinjectionFoot;
    }

    if (options?.tags) {
      updatePayload.tags = options.tags;
    }

    const updated = await this.getApi().posts.edit(updatePayload, { source: 'html' });
    return updated as GhostPost;
  }

  /**
   * Update a page's HTML content.
   */
  async updatePageHtml(
    pageId: string,
    html: string,
    updatedAt: string,
    options?: {
      codeinjectionFoot?: string;
      tags?: Array<{ id?: string; name: string; slug?: string }>;
    }
  ): Promise<GhostPost> {
    logger.debug({ pageId }, 'Updating page HTML in Ghost');

    const updatePayload: Record<string, unknown> = {
      id: pageId,
      html,
      updated_at: updatedAt,
    };

    if (options?.codeinjectionFoot !== undefined) {
      updatePayload.codeinjection_foot = options.codeinjectionFoot;
    }

    if (options?.tags) {
      updatePayload.tags = options.tags;
    }

    const updated = await this.getApi().pages.edit(updatePayload, { source: 'html' });
    return updated as GhostPost;
  }

  /**
   * Browse all posts (paginated).
   */
  async browsePosts(options?: { limit?: number; page?: number; filter?: string }): Promise<GhostPost[]> {
    const posts = await this.getApi().posts.browse({
      formats: 'html',
      include: 'tags,authors',
      limit: options?.limit || 15,
      page: options?.page || 1,
      filter: options?.filter,
    });
    return posts as GhostPost[];
  }
}
