var ENCYPHER_CONFIG = {
  DEFAULT_API_BASE_URL: 'https://api.encypherai.com',
  SIGN_PATH: '/api/v1/sign',
  VERIFY_PATH: '/api/v1/verify',
  ALLOWED_API_HOST_SUFFIX: 'encypherai.com',
  PROPERTY_API_KEY: 'encypher_api_key',
  PROPERTY_API_BASE_URL: 'encypher_api_base_url',
  PROPERTY_DOC_PROVENANCE_PREFIX: 'encypher_doc_provenance_',
  MAX_PROVENANCE_ENTRIES_PER_HASH: 10,
  MAX_PROVENANCE_KEYS_PER_DOC: 50,
  MIN_SIGN_TEXT_LENGTH: 10,
};

function getUserProperties_() {
  return PropertiesService.getUserProperties();
}

function getDocumentProperties_() {
  return PropertiesService.getDocumentProperties();
}

function getApiBaseUrl_() {
  var userProps = getUserProperties_();
  var configured = userProps.getProperty(ENCYPHER_CONFIG.PROPERTY_API_BASE_URL);
  if (!configured) {
    return ENCYPHER_CONFIG.DEFAULT_API_BASE_URL;
  }

  if (!isAllowedApiBaseUrl_(configured)) {
    return ENCYPHER_CONFIG.DEFAULT_API_BASE_URL;
  }

  return configured;
}

function getApiKey_() {
  var userProps = getUserProperties_();
  return userProps.getProperty(ENCYPHER_CONFIG.PROPERTY_API_KEY) || '';
}

function requireApiKey_() {
  var apiKey = getApiKey_();
  if (!apiKey) {
    throw new Error('No API key configured. Open Encypher Sidebar > Settings and set your API key.');
  }
  return apiKey;
}

function isAllowedApiBaseUrl_(value) {
  if (!value) return false;

  var normalized = String(value).trim();
  if (!/^https:\/\//i.test(normalized)) {
    return false;
  }

  var host;
  try {
    host = normalized.replace(/^https:\/\//i, '').split('/')[0].toLowerCase();
  } catch (e) {
    return false;
  }

  return host === ENCYPHER_CONFIG.ALLOWED_API_HOST_SUFFIX || host.endsWith('.' + ENCYPHER_CONFIG.ALLOWED_API_HOST_SUFFIX);
}
