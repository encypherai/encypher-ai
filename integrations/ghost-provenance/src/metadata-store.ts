import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';
import pino from 'pino';

const logger = pino({ name: 'metadata-store' });

export interface SigningRecord {
  ghost_post_id: string;
  ghost_post_type: string;
  document_id: string;
  instance_id: string;
  content_hash: string;
  action_type: string;
  total_segments: number;
  signed_at: string;
  previous_instance_id: string | null;
}

interface ImageSigningRecord {
  ghost_post_id: string;
  image_record_id: string;
  manifest_url: string;
  signed_at: string;
}

export class MetadataStore {
  private db: Database.Database;
  private imageRecords: Map<string, ImageSigningRecord> = new Map();

  constructor(dbPath: string) {
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
    this.migrate();
  }

  private migrate(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS signing_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ghost_post_id TEXT NOT NULL,
        ghost_post_type TEXT NOT NULL DEFAULT 'post',
        document_id TEXT NOT NULL,
        instance_id TEXT NOT NULL DEFAULT '',
        content_hash TEXT NOT NULL,
        action_type TEXT NOT NULL DEFAULT 'c2pa.created',
        total_segments INTEGER NOT NULL DEFAULT 0,
        signed_at TEXT NOT NULL,
        previous_instance_id TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE INDEX IF NOT EXISTS idx_signing_ghost_post_id
        ON signing_records(ghost_post_id);

      CREATE INDEX IF NOT EXISTS idx_signing_document_id
        ON signing_records(document_id);

      CREATE INDEX IF NOT EXISTS idx_signing_instance_id
        ON signing_records(instance_id);
    `);

    logger.info('Database migrated successfully');
  }

  /**
   * Record a signing operation.
   */
  recordSigning(record: SigningRecord): void {
    const stmt = this.db.prepare(`
      INSERT INTO signing_records
        (ghost_post_id, ghost_post_type, document_id, instance_id, content_hash,
         action_type, total_segments, signed_at, previous_instance_id)
      VALUES
        (@ghost_post_id, @ghost_post_type, @document_id, @instance_id, @content_hash,
         @action_type, @total_segments, @signed_at, @previous_instance_id)
    `);

    stmt.run(record);
    logger.debug({ ghostPostId: record.ghost_post_id, documentId: record.document_id }, 'Recorded signing');
  }

  /**
   * Get the latest signing record for a Ghost post.
   */
  getLatestRecord(ghostPostId: string): SigningRecord | null {
    const stmt = this.db.prepare(`
      SELECT * FROM signing_records
      WHERE ghost_post_id = ?
      ORDER BY created_at DESC
      LIMIT 1
    `);

    return (stmt.get(ghostPostId) as SigningRecord) || null;
  }

  /**
   * Get all signing records for a Ghost post (provenance chain).
   */
  getProvenanceChain(ghostPostId: string): SigningRecord[] {
    const stmt = this.db.prepare(`
      SELECT * FROM signing_records
      WHERE ghost_post_id = ?
      ORDER BY created_at ASC
    `);

    return stmt.all(ghostPostId) as SigningRecord[];
  }

  /**
   * Check if a post's content has changed since last signing.
   */
  hasContentChanged(ghostPostId: string, currentHash: string): boolean {
    const latest = this.getLatestRecord(ghostPostId);
    if (!latest) return true;
    return latest.content_hash !== currentHash;
  }

  /**
   * Get the previous instance_id for provenance chain linking.
   */
  getPreviousInstanceId(ghostPostId: string): string | null {
    const latest = this.getLatestRecord(ghostPostId);
    return latest?.instance_id || null;
  }

  /**
   * Get all signed posts.
   */
  getAllSignedPosts(limit: number = 50, offset: number = 0): SigningRecord[] {
    const stmt = this.db.prepare(`
      SELECT sr.* FROM signing_records sr
      INNER JOIN (
        SELECT ghost_post_id, MAX(created_at) as max_created
        FROM signing_records
        GROUP BY ghost_post_id
      ) latest ON sr.ghost_post_id = latest.ghost_post_id
        AND sr.created_at = latest.max_created
      ORDER BY sr.created_at DESC
      LIMIT ? OFFSET ?
    `);

    return stmt.all(limit, offset) as SigningRecord[];
  }

  recordImageSigning(record: ImageSigningRecord): void {
    // Store alongside the text signing records
    const key = `image_${record.ghost_post_id}`;
    this.imageRecords.set(key, record);
  }

  getImageRecord(postId: string): ImageSigningRecord | undefined {
    return this.imageRecords.get(`image_${postId}`);
  }

  close(): void {
    this.db.close();
  }
}
