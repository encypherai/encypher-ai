export interface Config {
  ghost: {
    url: string;
    adminApiKey: string;
    apiVersion: string;
  };
  encypher: {
    apiBaseUrl: string;
    apiKey: string;
  };
  server: {
    port: number;
    logLevel: string;
  };
  signing: {
    autoSignOnPublish: boolean;
    autoSignOnUpdate: boolean;
    tier: string;
    organizationName: string;
    signingMode: string;
    manifestMode: string;
    segmentationLevel: string;
  };
  webhookSecret: string;
  dbPath: string;
  badge: {
    enabled: boolean;
    verifyBaseUrl: string;
  };
}

function envBool(key: string, defaultVal: boolean): boolean {
  const val = process.env[key];
  if (val === undefined) return defaultVal;
  return val === 'true' || val === '1';
}

export function loadConfig(): Config {
  return {
    ghost: {
      url: process.env.GHOST_URL || 'http://localhost:2368',
      adminApiKey: process.env.GHOST_ADMIN_API_KEY || '',
      apiVersion: process.env.GHOST_API_VERSION || 'v5.0',
    },
    encypher: {
      apiBaseUrl: process.env.ENCYPHER_API_BASE_URL || 'http://localhost:8000/api/v1',
      apiKey: process.env.ENCYPHER_API_KEY || '',
    },
    server: {
      port: parseInt(process.env.PORT || '3000', 10),
      logLevel: process.env.LOG_LEVEL || 'info',
    },
    signing: {
      autoSignOnPublish: envBool('AUTO_SIGN_ON_PUBLISH', true),
      autoSignOnUpdate: envBool('AUTO_SIGN_ON_UPDATE', true),
      tier: process.env.SIGNING_TIER || 'free',
      organizationName: process.env.ORGANIZATION_NAME || '',
      signingMode: process.env.SIGNING_MODE || 'managed',
      manifestMode: process.env.MANIFEST_MODE || 'micro',
      segmentationLevel: process.env.SEGMENTATION_LEVEL || 'sentence',
    },
    webhookSecret: process.env.WEBHOOK_SECRET || '',
    dbPath: process.env.DB_PATH || './data/ghost-provenance.db',
    badge: {
      enabled: envBool('BADGE_ENABLED', true),
      verifyBaseUrl: process.env.VERIFY_BASE_URL || 'https://verify.encypherai.com',
    },
  };
}
