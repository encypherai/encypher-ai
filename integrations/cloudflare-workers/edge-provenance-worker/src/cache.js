/**
 * KV cache layer for provisioning records and embedding plans.
 */

const PLAN_TTL = 3600;         // 1 hour
const PROVISION_TTL = 86400;   // 24 hours
const NEGATIVE_TTL = 300;      // 5 minutes

/**
 * Get cached embedding plan for a domain + content hash.
 *
 * @param {KVNamespace} kv
 * @param {string} domain
 * @param {string} hashPrefix - First 16 chars of content hash
 * @returns {Promise<Object|null>}
 */
export async function getCachedPlan(kv, domain, hashPrefix) {
  const key = `plan:${domain}:${hashPrefix}`;
  const cached = await kv.get(key, 'json');
  return cached;
}

/**
 * Cache an embedding plan.
 *
 * @param {KVNamespace} kv
 * @param {string} domain
 * @param {string} hashPrefix
 * @param {Object} data - {embeddingPlan, documentId, verificationUrl, boundarySelector}
 */
export async function cachePlan(kv, domain, hashPrefix, data) {
  const key = `plan:${domain}:${hashPrefix}`;
  await kv.put(key, JSON.stringify(data), { expirationTtl: PLAN_TTL });
}

/**
 * Get cached provisioning record for a domain.
 *
 * @param {KVNamespace} kv
 * @param {string} domain
 * @returns {Promise<Object|null>}
 */
export async function getCachedProvision(kv, domain) {
  const key = `provision:${domain}`;
  return await kv.get(key, 'json');
}

/**
 * Cache a provisioning record.
 *
 * @param {KVNamespace} kv
 * @param {string} domain
 * @param {Object} data - {orgId, domainToken, dashboardUrl, claimUrl}
 */
export async function cacheProvision(kv, domain, data) {
  const key = `provision:${domain}`;
  await kv.put(key, JSON.stringify(data), { expirationTtl: PROVISION_TTL });
}

/**
 * Get negative cache entry (page that had no article or alignment failure).
 *
 * @param {KVNamespace} kv
 * @param {string} domain
 * @param {string} hashPrefix
 * @returns {Promise<string|null>} "NO_ARTICLE" or "ALIGN_FAIL" or null
 */
export async function getNegativeCache(kv, domain, hashPrefix) {
  const key = `skip:${domain}:${hashPrefix}`;
  return await kv.get(key);
}

/**
 * Set negative cache entry.
 *
 * @param {KVNamespace} kv
 * @param {string} domain
 * @param {string} hashPrefix
 * @param {string} reason
 */
export async function setNegativeCache(kv, domain, hashPrefix, reason) {
  const key = `skip:${domain}:${hashPrefix}`;
  await kv.put(key, reason, { expirationTtl: NEGATIVE_TTL });
}
