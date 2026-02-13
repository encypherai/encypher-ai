declare module '@tryghost/admin-api' {
  interface GhostAdminAPIOptions {
    url: string;
    key: string;
    version: string;
  }

  interface BrowseOptions {
    formats?: string;
    include?: string;
    limit?: number;
    page?: number;
    filter?: string;
    [key: string]: unknown;
  }

  interface ReadOptions {
    id?: string;
    slug?: string;
    [key: string]: unknown;
  }

  interface Resource {
    browse(options?: BrowseOptions): Promise<unknown[]>;
    read(data: ReadOptions, options?: BrowseOptions): Promise<unknown>;
    add(data: Record<string, unknown>, options?: Record<string, unknown>): Promise<unknown>;
    edit(data: Record<string, unknown>, options?: Record<string, unknown>): Promise<unknown>;
    delete(data: ReadOptions): Promise<void>;
  }

  interface ImageResource {
    upload(data: { file: string; ref?: string }): Promise<{ url: string; ref: string }>;
  }

  class GhostAdminAPI {
    constructor(options: GhostAdminAPIOptions);
    posts: Resource;
    pages: Resource;
    tags: Resource;
    images: ImageResource;
    webhooks: Resource;
    users: Resource;
    site: { read(): Promise<unknown> };
  }

  export default GhostAdminAPI;
}
