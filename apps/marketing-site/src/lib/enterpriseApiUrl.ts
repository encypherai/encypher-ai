const DEFAULT_PRODUCTION_API_URL = "https://api.encypherai.com";
const DEFAULT_DEVELOPMENT_API_URL = "http://localhost:9000";

type ResolveOptions = {
  env?: Partial<NodeJS.ProcessEnv>;
  nodeEnv?: string | undefined;
};

export function resolveEnterpriseApiUrl(options: ResolveOptions = {}): string {
  const env = options.env ?? process.env;
  const nodeEnv = options.nodeEnv ?? process.env.NODE_ENV;

  const configuredUrl = [env.ENTERPRISE_API_URL, env.NEXT_PUBLIC_ENTERPRISE_API_URL]
    .map((value) => (typeof value === "string" ? value.trim() : ""))
    .find((value) => value.length > 0);

  if (configuredUrl) {
    return configuredUrl;
  }

  return nodeEnv === "production" ? DEFAULT_PRODUCTION_API_URL : DEFAULT_DEVELOPMENT_API_URL;
}
