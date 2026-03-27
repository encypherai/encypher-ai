const DEFAULT_PRODUCTION_API_URL = "https://api.encypher.com";
const DEFAULT_DEVELOPMENT_API_URL = "http://localhost:9000";
const API_VERSION_PATH_REGEX = /\/api\/v1\/?$/i;

type ResolveOptions = {
  env?: Partial<NodeJS.ProcessEnv>;
  nodeEnv?: string | undefined;
};

export function resolveEnterpriseApiUrl(options: ResolveOptions = {}): string {
  const env = options.env ?? process.env;
  const nodeEnv = options.nodeEnv ?? process.env.NODE_ENV;

  const configuredUrl = [
    env.ENTERPRISE_API_URL,
    env.NEXT_PUBLIC_ENTERPRISE_API_URL,
    env.NEXT_PUBLIC_API_URL,
  ]
    .map((value) => normalizeEnterpriseApiUrl(value))
    .find((value) => value && (nodeEnv !== "production" || !isLocalhostUrl(value)));

  if (configuredUrl) {
    return configuredUrl;
  }

  return nodeEnv === "production" ? DEFAULT_PRODUCTION_API_URL : DEFAULT_DEVELOPMENT_API_URL;
}

export function resolvePublicEnterpriseApiUrl(options: ResolveOptions = {}): string {
  const env = options.env ?? process.env;
  const nodeEnv = options.nodeEnv ?? process.env.NODE_ENV;

  const configuredUrl = [env.NEXT_PUBLIC_ENTERPRISE_API_URL, env.NEXT_PUBLIC_API_URL]
    .map((value) => normalizeEnterpriseApiUrl(value))
    .find((value) => value && (nodeEnv !== "production" || !isLocalhostUrl(value)));

  if (configuredUrl) {
    return configuredUrl;
  }

  return nodeEnv === "production" ? DEFAULT_PRODUCTION_API_URL : DEFAULT_DEVELOPMENT_API_URL;
}

function normalizeEnterpriseApiUrl(value: string | undefined): string | null {
  if (typeof value !== "string") {
    return null;
  }

  const trimmed = value.trim().replace(/\/+$/, "");
  if (!trimmed) {
    return null;
  }

  try {
    const url = new URL(trimmed);
    const normalizedPath = url.pathname.replace(API_VERSION_PATH_REGEX, "").replace(/\/+$/, "");
    return `${url.origin}${normalizedPath}`;
  } catch {
    return trimmed.replace(API_VERSION_PATH_REGEX, "");
  }
}

function isLocalhostUrl(value: string): boolean {
  return /localhost|127\.0\.0\.1/i.test(value);
}
