import express from 'express';
import pino from 'pino';
import { loadConfig } from './config';
import { GhostClient } from './ghost-client';
import { EncypherClient } from './encypher-client';
import { MetadataStore } from './metadata-store';
import { Signer } from './signer';
import { WebhookHandler } from './webhook-handler';

const config = loadConfig();

const logger = pino({
  level: config.server.logLevel,
  name: 'ghost-provenance',
  transport: config.server.logLevel === 'debug'
    ? { target: 'pino-pretty', options: { colorize: true } }
    : undefined,
});

// Validate required configuration — warn but don't crash so the service
// can start while Ghost is being set up for the first time.
const missingKeys: string[] = [];
if (!config.ghost.adminApiKey) {
  missingKeys.push('GHOST_ADMIN_API_KEY');
  logger.warn('GHOST_ADMIN_API_KEY is not set. The service will start but signing is disabled. Set the key and restart.');
}
if (!config.encypher.apiKey) {
  missingKeys.push('ENCYPHER_API_KEY');
  logger.warn('ENCYPHER_API_KEY is not set. The service will start but signing is disabled. Set the key and restart.');
}

// Initialize clients
const ghostClient = new GhostClient(config);
const encypherClient = new EncypherClient(config);
const metadataStore = new MetadataStore(config.dbPath);

// Initialize signer and webhook handler
const signer = new Signer(config, ghostClient, encypherClient, metadataStore);
const webhookHandler = new WebhookHandler(config, signer);

// Create Express app
const app = express();
app.use(express.json({ limit: '10mb' }));

// Request logging
app.use((req, _res, next) => {
  logger.debug({ method: req.method, path: req.path }, 'Incoming request');
  next();
});

// Mount webhook routes under /api
app.use('/api', webhookHandler.getRouter());

// Root info endpoint
app.get('/', (_req, res) => {
  res.json({
    name: '@encypher/ghost-provenance',
    version: '1.0.0',
    description: 'Encypher C2PA provenance integration for Ghost CMS',
    endpoints: {
      health: '/api/health',
      webhooks: {
        postPublished: '/api/ghost/post-published',
        postUpdated: '/api/ghost/post-updated',
        pagePublished: '/api/ghost/page-published',
        pageUpdated: '/api/ghost/page-updated',
        generic: '/api/ghost/webhook',
      },
      manual: {
        sign: 'POST /api/sign { postId, postType }',
        status: 'GET /api/status/:postId',
      },
    },
    config: {
      ghostUrl: config.ghost.url,
      encypherApiUrl: config.encypher.apiBaseUrl,
      autoSignOnPublish: config.signing.autoSignOnPublish,
      autoSignOnUpdate: config.signing.autoSignOnUpdate,
      tier: config.signing.tier,
      badgeEnabled: config.badge.enabled,
    },
  });
});

// Start server
const server = app.listen(config.server.port, () => {
  logger.info({
    port: config.server.port,
    ghostUrl: config.ghost.url,
    encypherApiUrl: config.encypher.apiBaseUrl,
  }, `Encypher Ghost Provenance service listening on port ${config.server.port}`);

  logger.info('Configure Ghost webhooks to point to:');
  logger.info(`  post.published       → http://localhost:${config.server.port}/api/ghost/post-published`);
  logger.info(`  post.published.edited → http://localhost:${config.server.port}/api/ghost/post-updated`);
  logger.info(`  page.published       → http://localhost:${config.server.port}/api/ghost/page-published`);
  logger.info(`  page.published.edited → http://localhost:${config.server.port}/api/ghost/page-updated`);
});

// Graceful shutdown
function shutdown() {
  logger.info('Shutting down...');
  metadataStore.close();
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

export { app, server };
